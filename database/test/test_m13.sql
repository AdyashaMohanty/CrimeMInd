/* CrimeMind M13 test */
SET PAGESIZE 100
SET LINESIZE 220
SET LONG 3000
SET DEFINE OFF

VARIABLE v_case_id NUMBER
VARIABLE v_entity_id NUMBER
VARIABLE v_result_limit NUMBER

EXEC :v_case_id := 1
EXEC :v_entity_id := 34
EXEC :v_result_limit := 20

@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\13_get_entity_vehicles.sql

EXIT;
