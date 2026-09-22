/* CrimeMind M04 test */
SET PAGESIZE 100
SET LINESIZE 200
SET LONG 2000
SET DEFINE OFF

VARIABLE v_case_id NUMBER;
VARIABLE v_entity_id NUMBER;
VARIABLE v_start_time VARCHAR2(50);
VARIABLE v_end_time VARCHAR2(50);
VARIABLE v_minimum_strength NUMBER;
VARIABLE v_result_limit NUMBER;

EXEC :v_case_id := 1;
EXEC :v_entity_id := NULL;
EXEC :v_start_time := '01-JAN-2025';
EXEC :v_end_time := '01-JAN-2027';
EXEC :v_minimum_strength := 2;
EXEC :v_result_limit := 20;

@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\04_find_common_locations.sql
@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\04_find_common_locations.sql
EXIT;
