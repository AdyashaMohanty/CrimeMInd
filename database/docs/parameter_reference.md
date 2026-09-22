# Oracle CrimeMind SQL Module Parameter Reference

| Module | Questions | Main parameters |
|---|---|---|
| 01 | Q1,Q3,Q4 | entity_id, start_time, end_time, result_limit |
| 02 | Q2 | entity_a, entity_b, start_time, end_time, result_limit |
| 03 | Q5,Q8 | location_id, start_time, end_time, result_limit |
| 04 | Q9,Q10 | entity_ids, start_time, end_time, minimum_entities, result_limit |
| 05 | Q6,Q7 | entity_id, start_time, end_time, result_limit |
| 06 | Q11,Q12 | entity_id, start_time, end_time, result_limit |
| 07 | Q13 | entity_id, start_time, end_time, minimum_gap_seconds, result_limit |
| 08 | Q14,Q15,Q16 | case_id, incident_event_id, window_before, window_after, result_limit |
| 09 | Q17 | entity_id, result_limit |
| 10 | Q18 | entity_a, entity_b, result_limit |
| 11 | Q19,Q20 | start_entity_id, target_entity_id, max_hops, result_limit |
| 12 | Q21 | entity_id, minimum_strength, result_limit |
| 13 | Q22 | entity_id, start_time, end_time, result_limit |
| 14 | Q23,Q24,Q25 | location_id, start_time, end_time, result_limit |
| 15 | Q26-Q30 | entity_id, start_time, end_time, minimum_transaction_count, result_limit |
| 16 | Q31,Q32 | entity_id, event_id, minimum_reliability, result_limit |
| 17 | Q33,Q36,Q37 | entity_ids, minimum_entities, minimum_independent_sources, result_limit |
| 18 | Q34,Q35,Q38-Q40 | location_id, target_entity_id, minimum_independent_sources, result_limit |

Python expands list parameters into named Oracle binds. JSON-like attributes are CLOB in Oracle 11g.
