# fhir-mcp Demo Script

This script guides a live demo or asciinema recording of Claude Desktop using all six fhir-mcp tools. Run through the steps in order. Each step shows the query to type and what to verify in Claude's response.

---

## Setup (before recording)

1. Install the package:
   ```bash
   pip install fhir-mcp
   ```

2. Merge the Claude Desktop config block from `examples/claude_desktop_config.json` into your local config file.
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`

   Update the `--bundle` path to the absolute path of `examples/synthea_patients.json.gz` on your machine.

3. Restart Claude Desktop.

4. Open a new conversation. Confirm the fhir-mcp tools appear in the tool panel (hammer icon).

Note: "p1" below is a placeholder. Synthea patient resources use UUIDs, so the agent will pick a real UUID at runtime after the Step 1 search (or you can substitute one from the bundle).

---

## Step 1 - Search for patients (fhir_search_patients)

**Type:** "Find all patients in the bundle and tell me how many there are."

**Verify:**
- Claude calls `fhir_search_patients` with `criteria: {}`.
- Response lists Patient resources and reports the total count.
- No PHI is present; all names and dates are synthetic.

---

## Step 2 - Query observations (fhir_get_observations)

**Type:** "Show me the glucose lab results for patient p1."

**Verify:**
- Claude calls `fhir_get_observations` with `patient_id: "p1"` and `code: "2339-0"`.
- Response lists Observation resources with glucose values.
- If p1 has no glucose result, Claude says so rather than hallucinating a value.

---

## Step 3 - Review medications (fhir_get_medications)

**Type:** "What medications is patient p1 prescribed? Is metformin on the list?"

**Verify:**
- Claude calls `fhir_get_medications` with `patient_id: "p1"`.
- Response identifies MedicationRequest resources and confirms or denies metformin.

---

## Step 4 - Look up conditions (fhir_get_conditions)

**Type:** "Does patient p1 have a diagnosis of type-2 diabetes?"

**Verify:**
- Claude calls `fhir_get_conditions` with `patient_id: "p1"`.
- Response checks SNOMED code 44054006 in the returned Condition resources and reports the clinical status.

---

## Step 5 - Review encounter history (fhir_get_encounters)

**Type:** "How many outpatient visits has patient p1 had? When was the most recent one?"

**Verify:**
- Claude calls `fhir_get_encounters` with `patient_id: "p1"`.
- Response counts encounters with class AMB and reports the most recent period.start date.

---

## Step 6 - Structured adherence query (compute_adherence, structured branch)

**Type:** "Did patient p1 take metformin in Q1 2026? What is their adherence ratio?"

**Verify:**
- Claude calls `compute_adherence` with `patient_id: "p1"`, `medication: "metformin"`, and the question text.
- The routing result shows `"branch": "structured"`.
- Response includes an `adherence_ratio` between 0.0 and 1.0, computed from MedicationRequest dispense data.

---

## Step 7 - Narrative adherence query (compute_adherence, narrative branch)

**Type:** "Describe patient p1's overall medication adherence pattern."

**Verify:**
- Claude calls `compute_adherence` with the same patient and medication.
- The routing result shows `"branch": "narrative"`.
- Response is based on DocumentReference and Composition resources returned by the narrative pipeline, not a computed ratio.
- Claude summarizes the documents rather than fabricating clinical detail.

---

## Step 8 - Ambiguous query (compute_adherence, both branches)

**Type:** "Tell me about patient p1's health in general."

**Verify:**
- Claude calls `compute_adherence`.
- The routing result shows `"branch": "ambiguous"`.
- Response integrates both the structured adherence ratio and the narrative document summary.

---

## End of demo

All six tools have been exercised:
- `fhir_search_patients` (Step 1)
- `fhir_get_observations` (Step 2)
- `fhir_get_medications` (Step 3)
- `fhir_get_conditions` (Step 4)
- `fhir_get_encounters` (Step 5)
- `compute_adherence` - structured, narrative, and ambiguous branches (Steps 6-8)

The routing rule in `compute_adherence` is justified by Jani et al., May 2026 preprint (arXiv ID TBD): AUC 0.997 for structured-FHIR-wins classification, AUC 0.843 for narrative-wins free-form QA.
