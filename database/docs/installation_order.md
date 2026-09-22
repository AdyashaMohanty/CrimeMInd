# Oracle XE 11g Installation Order

1. ddl/00_extensions.sql
2. ddl/01_schema.sql
3. ddl/02_sequences.sql
4. ddl/03_indexes.sql
5. ddl/05_seed_reference.sql
6. ddl/06_backend_application.sql
7. functions/01_evidence_reliability.sql
8. functions/02_relationship_strength.sql
9. functions/03_audit_trigger.sql
10. functions/04_timeline_gaps.sql
11. seed/01_synthetic_seed.sql
12. seed/02_query_catalog.sql
13. Load normalized evidence with ingestion/loaders/oracle_loader.py.

Do not execute the old legacy PostgreSQL SQL files.
Do not import evaluation-only ground truth as operational evidence.
