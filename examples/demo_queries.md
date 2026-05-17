# fhir-mcp Demo Queries

Example queries for testing each tool with a Claude Desktop MCP session backed by the Synthea bundle at `examples/synthea_patients.json.gz`.

---

## 1. fhir_search_patients

**Query:** "Find all patients in the bundle."

Expected agent behaviour: calls `fhir_search_patients` with `criteria: {}` and lists returned Patient resources.

**Query:** "Are there any female patients over the age of 60?"

Expected agent behaviour: calls `fhir_search_patients` with `criteria: {}`, then filters in the answer by birthDate and gender fields from the FHIR Patient resources.

---

## 2. fhir_get_observations

**Query:** "Show me the lab results for patient p1."

Expected agent behaviour: calls `fhir_get_observations` with `patient_id: "p1"` and presents the returned Observation resources.

**Query:** "Has patient p2 had a glucose test (code 2339-0)?"

Expected agent behaviour: calls `fhir_get_observations` with `patient_id: "p2"` and `code: "2339-0"`. Reports whether any results were returned and what values they contain.

---

## 3. fhir_get_medications

**Query:** "What medications is patient p1 currently prescribed?"

Expected agent behaviour: calls `fhir_get_medications` with `patient_id: "p1"` and lists the MedicationRequest resources, highlighting medication names and status.

**Query:** "Does patient p3 have a metformin prescription?"

Expected agent behaviour: calls `fhir_get_medications` with `patient_id: "p3"` and searches the returned MedicationRequest resources for metformin.

---

## 4. fhir_get_conditions

**Query:** "What chronic conditions does patient p2 have?"

Expected agent behaviour: calls `fhir_get_conditions` with `patient_id: "p2"` and presents the Condition resources, noting any SNOMED codes and clinical statuses.

**Query:** "Does patient p1 have a diagnosis of type-2 diabetes (SNOMED 44054006)?"

Expected agent behaviour: calls `fhir_get_conditions` with `patient_id: "p1"` and checks for SNOMED code 44054006 in the returned conditions.

---

## 5. fhir_get_encounters

**Query:** "How many clinic visits has patient p3 had?"

Expected agent behaviour: calls `fhir_get_encounters` with `patient_id: "p3"` and counts the returned Encounter resources, noting the encounter classes and dates.

**Query:** "When was patient p1's most recent outpatient encounter?"

Expected agent behaviour: calls `fhir_get_encounters` with `patient_id: "p1"`, sorts encounters by period.start, and reports the most recent one with class AMB or equivalent.

---

## 6. compute_adherence

**Structured routing — date-bounded adherence:**

Query: "Did patient p1 take metformin between January and June 2026?"

Expected agent behaviour: calls `compute_adherence` with `patient_id: "p1"`, `medication: "metformin"`, and the question text. The heuristic router classifies this as `structured` (date range detected), so the response includes an `adherence_ratio` computed from MedicationRequest dispense data.

**Narrative routing — open-ended summary:**

Query: "Describe patient p1's overall medication adherence pattern."

Expected agent behaviour: calls `compute_adherence` with the question. The heuristic router classifies this as `narrative` (words "describe", "overall", "pattern" detected), so the response includes DocumentReference and Composition resources for the agent to summarize — no ratio is computed.

**Ambiguous routing — both pipelines:**

Query: "Tell me about patient p2's health."

Expected agent behaviour: calls `compute_adherence`. The router returns `ambiguous`, so both the structured adherence ratio and the narrative document resources are returned. The agent synthesizes both into an answer.

---

## Notes

- Replace `p1`, `p2`, `p3` with actual patient IDs when using the full Synthea 100-patient bundle.
- The `compute_adherence` routing rule is justified by Jani et al., May 2026 preprint (arXiv ID TBD): AUC 0.997 for structured-FHIR-wins classification, AUC 0.843 for narrative-wins QA.
- No PHI is present in the Synthea bundles. All data is synthetically generated.
