/* CrimeMind M02 test */
SET PAGESIZE 100
SET LINESIZE 200
SET LONG 2000
SET DEFINE OFF

VARIABLE v_case_id NUMBER;
VARIABLE v_entity_id_1 NUMBER;
VARIABLE v_entity_id_2 NUMBER;
VARIABLE v_start_time VARCHAR2(50);
VARIABLE v_end_time VARCHAR2(50);
VARIABLE v_result_limit NUMBER;

EXEC :v_case_id := 1;
EXEC :v_entity_id_1 := 36;
EXEC :v_entity_id_2 := 37;
EXEC :v_start_time := '01-JAN-2025';
EXEC :v_end_time := '01-JAN-2027';
EXEC :v_result_limit := 20;

@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\02_get_communication_between_entities.sql
@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\02_get_communication_between_entities.sql
EXIT;
