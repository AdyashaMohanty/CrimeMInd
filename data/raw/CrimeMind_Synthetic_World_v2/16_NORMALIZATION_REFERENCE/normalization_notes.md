NORMALIZATION REFERENCE

Person names may appear inconsistently across source systems (e.g. full
name in people.csv vs. abbreviated forms in some free-text documents).
Location names may appear with varying address formats/precision across
CSV, GeoJSON, and KML exports. Financial transactions in
04_FINANCIAL/bank/bank_export_subset.xml and .json are a duplicate,
differently-formatted export of a subset of 04_FINANCIAL/bank/../transactions
and should resolve to the same underlying events, not be double-counted.

Ingestion pipelines should preserve original_value alongside any
normalized_value produced during processing; raw source files are never
overwritten.


## v2 realism additions
- P009 has vehicle V017 with partial-plate sightings at L011 during the incident window.
- P009/P042 have a matched financial reference REF-LOAN-0228 documented as a personal loan repayment.
- P009 has warehouse access events near the incident window, including a denied server-room attempt.
- P006 works rotating shifts at the nearby 24-hour Green Park Fuel Station (L028); CAM017 contains routine incident-night activity.
- Coherent multi-message threads were added for important relationships.
