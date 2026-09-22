/* CrimeMind TEST_M12 */
SET PAGESIZE 100
SET LINESIZE 220
SET LONG 3000
SET DEFINE OFF

VARIABLE v_case_id NUMBER;
VARIABLE v_entity_id NUMBER;
VARIABLE v_minimum_strength NUMBER;
VARIABLE v_result_limit NUMBER;

EXEC :v_case_id := 1;
EXEC :v_entity_id := 36;
EXEC :v_minimum_strength := 0;
EXEC :v_result_limit := 20;

@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\12_get_strong_entity_relationships.sql

EXIT;
