from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fhir_mcp.backend.base import FhirBackend


def _get_medication_text(med_resource: dict[str, Any]) -> str:
    """Extract medication text from either R4B (medication.concept.text) format."""
    # R4B: medication is a CodeableReference with concept.text
    med = med_resource.get("medication", {})
    if isinstance(med, dict):
        concept = med.get("concept", {})
        text: str = concept.get("text", "") if isinstance(concept, dict) else ""
        if text:
            return text
        # Fall back to coding display
        codings = concept.get("coding", []) if isinstance(concept, dict) else []
        if codings and isinstance(codings, list):
            display: str = codings[0].get("display", "") if isinstance(codings[0], dict) else ""
            return display
    # Legacy R4 fallback
    legacy = med_resource.get("medicationCodeableConcept", {})
    if isinstance(legacy, dict):
        legacy_text: str = legacy.get("text", "")
        return legacy_text
    return ""


def compute_structured_adherence(
    backend: FhirBackend,
    patient_id: str,
    medication: str,
) -> dict[str, Any]:
    meds = backend.search("MedicationRequest", {"patient": patient_id})
    matching = [m for m in meds if medication.lower() in _get_medication_text(m).lower()]

    observed_doses = 0
    first_date: date | None = None
    last_date: date | None = None
    for m in matching:
        dispense = m.get("dispenseRequest", {})
        quantity = dispense.get("quantity", {}).get("value") or 0
        observed_doses += int(quantity)
        authored = m.get("authoredOn")
        if authored:
            d = datetime.fromisoformat(authored.replace("Z", "+00:00")).date()
            first_date = d if first_date is None or d < first_date else first_date
            last_date = d if last_date is None or d > last_date else last_date

    span_days = (last_date - first_date).days if first_date and last_date else 0
    expected_doses = max(span_days, observed_doses)

    ratio = observed_doses / expected_doses if expected_doses else 0.0

    return {
        "source": "structured",
        "patient_id": patient_id,
        "medication": medication,
        "period": {
            "start": first_date.isoformat() if first_date else None,
            "end": last_date.isoformat() if last_date else None,
        },
        "expected_doses": expected_doses,
        "observed_doses": observed_doses,
        "adherence_ratio": ratio,
    }
