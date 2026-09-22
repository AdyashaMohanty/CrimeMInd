SET PAGESIZE 100
SET LINESIZE 220
SET LONG 3000
SET DEFINE OFF
VARIABLE v_case_id NUMBER
VARIABLE v_entity_id NUMBER
VARIABLE v_location_id NUMBER
VARIABLE v_result_limit NUMBER
EXEC :v_case_id := 1
EXEC :v_entity_id := NULL
EXEC :v_location_id := NULL
EXEC :v_result_limit := 20
@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\18_get_case_evidence_ranking.sql
EXIT;
