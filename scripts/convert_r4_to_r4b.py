"""
Convert Synthea R4 FHIR bundle to R4B-compatible bundle.

Only fixes the specific field renames/shape changes that fhir.resources R4B strict
validation rejects. Each transformation block is labelled with the error it fixes.
"""
from __future__ import annotations

import copy
import gzip
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _to_codeable_reference_list(concepts: list, refs: list) -> list:
    """Convert lists of CodeableConcepts and References to CodeableReference list."""
    result = []
    for c in concepts or []:
        result.append({"concept": c})
    for ref in refs or []:
        result.append({"reference": ref})
    return result


# ---------------------------------------------------------------------------
# Per-resource transformers
# ---------------------------------------------------------------------------


def fix_encounter(r: dict) -> dict:
    """
    R4 → R4B:
    - class: Coding → class: list[CodeableConcept]
    - period (forbidden) → actualPeriod
    - reasonCode (forbidden) → reason[].value (CodeableReference list)
    - participant[].individual (forbidden) → participant[].actor
    - hospitalization → admission
    """
    # class: Coding → list containing CodeableConcept wrapping that coding
    if "class" in r and isinstance(r["class"], dict):
        old_cls = r.pop("class")
        r["class"] = [{"coding": [old_cls]}]

    # period → actualPeriod
    if "period" in r:
        r["actualPeriod"] = r.pop("period")

    # reasonCode → reason[].value[].concept  (R4B EncounterReason.value is list[CodeableReference])
    if "reasonCode" in r:
        r["reason"] = [{"value": [{"concept": rc}]} for rc in r.pop("reasonCode")]

    # participant[].individual → participant[].actor
    for p in r.get("participant", []):
        if "individual" in p:
            p["actor"] = p.pop("individual")

    # hospitalization → admission
    if "hospitalization" in r:
        r["admission"] = r.pop("hospitalization")

    return r


def fix_medication_request(r: dict) -> dict:
    """
    R4 → R4B:
    - medicationCodeableConcept → medication.concept
    - medicationReference       → medication.reference
    - reasonCode / reasonReference → reason (list[CodeableReference])
    - dosageInstruction[].asNeededBoolean → dosageInstruction[].asNeeded
    """
    if "medicationCodeableConcept" in r:
        r["medication"] = {"concept": r.pop("medicationCodeableConcept")}
    if "medicationReference" in r:
        r["medication"] = {"reference": r.pop("medicationReference")}

    reason_codes = r.pop("reasonCode", None) or []
    reason_refs = r.pop("reasonReference", None) or []
    combined = _to_codeable_reference_list(reason_codes, reason_refs)
    if combined:
        r["reason"] = combined

    # asNeededBoolean → asNeeded (R4B uses asNeeded directly as a boolean)
    for d in r.get("dosageInstruction", []):
        if "asNeededBoolean" in d:
            d["asNeeded"] = d.pop("asNeededBoolean")

    return r


def fix_medication_administration(r: dict) -> dict:
    """
    R4 → R4B:
    - medicationCodeableConcept → medication.concept
    - medicationReference       → medication.reference
    - context                   → encounter
    - effectiveDateTime         → occurenceDateTime
    - effectivePeriod           → occurencePeriod
    - reasonReference / reasonCode → reason (list[CodeableReference])
    """
    if "medicationCodeableConcept" in r:
        r["medication"] = {"concept": r.pop("medicationCodeableConcept")}
    if "medicationReference" in r:
        r["medication"] = {"reference": r.pop("medicationReference")}
    if "context" in r:
        r["encounter"] = r.pop("context")
    if "effectiveDateTime" in r:
        r["occurenceDateTime"] = r.pop("effectiveDateTime")
    if "effectivePeriod" in r:
        r["occurencePeriod"] = r.pop("effectivePeriod")

    reason_codes = r.pop("reasonCode", None) or []
    reason_refs = r.pop("reasonReference", None) or []
    combined = _to_codeable_reference_list(reason_codes, reason_refs)
    if combined:
        r.setdefault("reason", [])
        r["reason"] = combined + r["reason"]

    return r


def fix_procedure(r: dict) -> dict:
    """
    R4 → R4B:
    - performedPeriod   → occurrencePeriod
    - performedDateTime → occurrenceDateTime
    - reasonReference / reasonCode → reason[].concept / reason[].reference
    """
    if "performedPeriod" in r:
        r["occurrencePeriod"] = r.pop("performedPeriod")
    if "performedDateTime" in r:
        r["occurrenceDateTime"] = r.pop("performedDateTime")

    reason_codes = r.pop("reasonCode", None) or []
    reason_refs = r.pop("reasonReference", None) or []
    combined = _to_codeable_reference_list(reason_codes, reason_refs)
    if combined:
        r["reason"] = combined

    return r


def fix_document_reference(r: dict) -> dict:
    """
    R4 → R4B:
    - content[].format (Coding) → removed (not in R4B)
    - context: object with encounter+period → context: list[Reference] (just the encounter refs)
      R4B DocumentReference.context is list[Reference] pointing to Encounter/EpisodeOfCare.
    """
    for c in r.get("content", []):
        c.pop("format", None)

    if "context" in r and isinstance(r["context"], dict):
        ctx = r.pop("context")
        # R4B context is list[Reference] — pull out the encounter references
        enc_refs = ctx.get("encounter", [])
        if enc_refs:
            r["context"] = enc_refs
        else:
            r.pop("context", None)

    return r


def fix_imaging_study(r: dict) -> dict:
    """
    R4 → R4B:
    - procedureCode (list[CodeableConcept]) → procedure[].concept
    - series[].modality: Coding → CodeableConcept
    - series[].bodySite: Coding → CodeableReference.concept
    - location (not a top-level field in R4B) → removed
    """
    if "procedureCode" in r:
        r["procedure"] = [{"concept": pc} for pc in r.pop("procedureCode")]

    r.pop("location", None)

    for s in r.get("series", []):
        # modality: Coding → CodeableConcept
        if "modality" in s and isinstance(s["modality"], dict):
            coding = s["modality"]
            if "coding" not in coding:
                s["modality"] = {"coding": [coding]}

        # bodySite: Coding → CodeableReference
        if "bodySite" in s and isinstance(s["bodySite"], dict):
            raw = s["bodySite"]
            if "coding" not in raw and "concept" not in raw:
                s["bodySite"] = {"concept": {"coding": [raw]}}

    return r


def fix_allergy_intolerance(r: dict) -> dict:
    """
    R4 → R4B:
    - type: string → type: CodeableConcept
    - reaction[].manifestation: list[CodeableConcept] → list[CodeableReference]
    """
    if "type" in r and isinstance(r["type"], str):
        r["type"] = {"coding": [{"code": r["type"]}]}

    for rxn in r.get("reaction", []):
        if "manifestation" in rxn:
            new_man = []
            for m in rxn["manifestation"]:
                if isinstance(m, dict) and "concept" not in m and "reference" not in m:
                    new_man.append({"concept": m})
                else:
                    new_man.append(m)
            rxn["manifestation"] = new_man

    return r


def fix_supply_delivery(r: dict) -> dict:
    """
    R4 → R4B:
    - suppliedItem: object → list[object]  (R4B SupplyDelivery.suppliedItem is a list)
    - suppliedItem.itemCodeableConcept stays as-is (R4B SupplyDeliverySuppliedItem
      still uses itemCodeableConcept, not item.concept)
    """
    if "suppliedItem" in r and isinstance(r["suppliedItem"], dict):
        r["suppliedItem"] = [r["suppliedItem"]]
    return r


def fix_care_team(r: dict) -> dict:
    """
    R4 → R4B:
    - participant[].role: list[CodeableConcept] → single CodeableConcept
    - encounter: not in R4B CareTeam → remove
    - reasonCode → reason (list[CodeableReference].concept)
    """
    for p in r.get("participant", []):
        if "role" in p and isinstance(p["role"], list):
            p["role"] = p["role"][0] if p["role"] else {}

    r.pop("encounter", None)

    reason_codes = r.pop("reasonCode", None) or []
    reason_refs = r.pop("reasonReference", None) or []
    combined = _to_codeable_reference_list(reason_codes, reason_refs)
    if combined:
        r["reason"] = combined

    return r


def fix_device(r: dict) -> dict:
    """
    R4 → R4B:
    - patient → removed (no patient field in R4B Device)
    - distinctIdentifier → removed
    - deviceName (R4) → name (R4B); items use 'value' not 'name'
    - udiCarrier[].issuer: must be URI string; if missing add default GS1 URI
    - type: CodeableConcept → list[CodeableConcept]
    """
    r.pop("patient", None)
    r.pop("distinctIdentifier", None)

    # deviceName → name  (R4B Device uses 'name' not 'deviceName')
    # R4B DeviceName uses 'value' (string) not 'name'
    if "deviceName" in r:
        converted = []
        for dn in r.pop("deviceName"):
            item = dict(dn)
            if "name" in item and "value" not in item:
                item["value"] = item.pop("name")
            converted.append(item)
        r["name"] = converted

    # udiCarrier[].issuer must be a URI string (element_required: True)
    for uc in r.get("udiCarrier", []):
        issuer = uc.get("issuer")
        if isinstance(issuer, dict):
            # Try to extract a URI from the Coding
            uc["issuer"] = issuer.get("system", "http://hl7.org/fhir/NamingSystem/gs1-di")
        elif issuer is None:
            # element_required but Synthea doesn't emit it — supply the GS1 default
            uc["issuer"] = "http://hl7.org/fhir/NamingSystem/gs1-di"

    # type: CodeableConcept → list[CodeableConcept]
    if "type" in r and isinstance(r["type"], dict):
        r["type"] = [r["type"]]

    return r


def fix_explanation_of_benefit(r: dict) -> dict:
    """
    R4 → R4B:
    - contained Coverage.payor: no payor field in R4B Coverage → remove
    - contained Coverage.kind: required in R4B → add 'insurance' default
    """
    for contained in r.get("contained", []):
        if contained.get("resourceType") == "Coverage":
            contained.pop("payor", None)
            # Coverage.kind is element_required in R4B
            if "kind" not in contained:
                contained["kind"] = "insurance"
    return r


def fix_care_plan(r: dict) -> dict:
    """
    R4 → R4B:
    - activity[].detail → removed (activities are separate resources in R4B)
    - addresses: list[Reference] → list[CodeableReference]
    """
    for act in r.get("activity", []):
        act.pop("detail", None)

    if "addresses" in r:
        new_addr = []
        for a in r["addresses"]:
            if isinstance(a, dict) and "reference" in a and "concept" not in a:
                new_addr.append({"reference": a})
            else:
                new_addr.append(a)
        r["addresses"] = new_addr

    return r


def fix_organization(r: dict) -> dict:
    """
    R4 → R4B:
    - telecom + address → contact[0] (ExtendedContactDetail)
    """
    telecom = r.pop("telecom", None)
    address = r.pop("address", None)
    if telecom or address:
        contact_item: dict = {}
        if telecom:
            contact_item["telecom"] = telecom
        if address:
            # ExtendedContactDetail.address is a single Address (not list)
            contact_item["address"] = address[0] if isinstance(address, list) else address
        existing = r.get("contact", [])
        r["contact"] = [contact_item] + (existing if isinstance(existing, list) else [])
    return r


def fix_practitioner_role(r: dict) -> dict:
    """
    R4 → R4B:
    - telecom → contact[].telecom  (ExtendedContactDetail)
    """
    telecom = r.pop("telecom", None)
    if telecom:
        contact_item = {"telecom": telecom}
        existing = r.get("contact", [])
        r["contact"] = [contact_item] + (existing if isinstance(existing, list) else [])
    return r


def fix_location(r: dict) -> dict:
    """
    R4 → R4B:
    - physicalType → form (R4B renamed physicalType to form)
    - telecom → contact[].telecom  (R4B Location uses ExtendedContactDetail)
    """
    if "physicalType" in r:
        r["form"] = r.pop("physicalType")

    telecom = r.pop("telecom", None)
    if telecom:
        contact_item = {"telecom": telecom}
        existing = r.get("contact", [])
        r["contact"] = [contact_item] + (existing if isinstance(existing, list) else [])

    return r


FIXERS = {
    "Encounter": fix_encounter,
    "MedicationRequest": fix_medication_request,
    "MedicationAdministration": fix_medication_administration,
    "Procedure": fix_procedure,
    "DocumentReference": fix_document_reference,
    "ImagingStudy": fix_imaging_study,
    "AllergyIntolerance": fix_allergy_intolerance,
    "SupplyDelivery": fix_supply_delivery,
    "CareTeam": fix_care_team,
    "Device": fix_device,
    "ExplanationOfBenefit": fix_explanation_of_benefit,
    "CarePlan": fix_care_plan,
    "Location": fix_location,
    "Organization": fix_organization,
    "PractitionerRole": fix_practitioner_role,
}


def convert_entry(entry: dict) -> dict:
    r = copy.deepcopy(entry.get("resource", {}))
    rt = r.get("resourceType", "")
    fixer = FIXERS.get(rt)
    if fixer:
        r = fixer(r)
    return {**entry, "resource": r}


def convert_bundle(path: Path, out_path: Path) -> int:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as f:
        bundle = json.load(f)

    converted = [convert_entry(e) for e in bundle.get("entry", [])]
    bundle["entry"] = converted

    out_opener = gzip.open if out_path.suffix == ".gz" else open
    with out_opener(out_path, "wt") as f:
        json.dump(bundle, f)

    print(f"converted {len(converted)} entries → {out_path}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print(
            "usage: convert_r4_to_r4b.py <input.json[.gz]> [output.json[.gz]]",
            file=sys.stderr,
        )
        raise SystemExit(2)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2]) if len(sys.argv) == 3 else src
    raise SystemExit(convert_bundle(src, dst))
