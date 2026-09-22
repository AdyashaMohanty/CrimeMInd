SET PAGESIZE 100
SET LINESIZE 220
SET LONG 3000
SET DEFINE OFF

VARIABLE v_case_id NUMBER
VARIABLE v_analysis_type VARCHAR2(30)
VARIABLE v_minimum_entity_count NUMBER
VARIABLE v_minimum_evidence_types NUMBER
VARIABLE v_result_limit NUMBER

EXEC :v_case_id := 1
EXEC :v_analysis_type := 'MULTI_TYPE_ENTITY'
EXEC :v_minimum_entity_count := 2
EXEC :v_minimum_evidence_types := 2
EXEC :v_result_limit := 20

@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\17_find_cross_entity_evidence.sql

EXIT;