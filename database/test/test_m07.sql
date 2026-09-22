/* CrimeMind M07 test */
SET PAGESIZE 100
SET LINESIZE 200
SET LONG 2000
SET DEFINE OFF

VARIABLE v_case_id NUMBER;
VARIABLE v_entity_id NUMBER;
VARIABLE v_start_time VARCHAR2(50);
VARIABLE v_end_time VARCHAR2(50);
VARIABLE v_minimum_gap_minutes NUMBER;
VARIABLE v_result_limit NUMBER;

EXEC :v_case_id := 1;
EXEC :v_entity_id := 36;
EXEC :v_start_time := '01-JAN-2025';
EXEC :v_end_time := '01-JAN-2027';
EXEC :v_minimum_gap_minutes := 60;
EXEC :v_result_limit := 20;

@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\07_find_timeline_gaps.sql
@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\07_find_timeline_gaps.sql
EXIT;
