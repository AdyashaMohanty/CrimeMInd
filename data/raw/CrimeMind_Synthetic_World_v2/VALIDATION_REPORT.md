# VALIDATION REPORT — CrimeMind Synthetic World v2

**Status: PASS.** Intentional uncertainty and source disagreement are preserved.

## Key checks
- **P009_vehicle_registered:** True
- **P009_incident_vehicle_sightings:** 2
- **P009_incident_access_records:** 4
- **loan_transfer_records:** 2
- **P037_P042_calls_7_to_13_March:** 7
- **P009_P042_incident_messages:** 6
- **forbidden_assignment_patterns:** 0
- **evaluation_folder_present:** True

## Repairs
- P009 vehicle V017 and incident-window partial-plate sightings added.
- P009 warehouse access records added near incident time.
- P009/P042 matched loan-repayment transaction added.
- P006 assigned to nearby 24-hour Green Park Fuel Station (L028); routine CAM017 incident-night activity added.
- Coherent message threads added for important relationships.
- Synthetic CCTV frames and short ambient WAV artifacts added.
- Ground-truth claims were aligned with operational records.

## Isolation
`14_EVALUATION_ONLY/ground_truth.json` is validation-only and must never enter the operational ingestion pipeline.

## Intentional imperfections
CCTV offsets, partial plates, approximate witness times, missing records, duplicates, irrelevant background activity, and qualified forensic findings are deliberate.
