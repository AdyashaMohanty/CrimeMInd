/* CrimeMind M11 test */
SET PAGESIZE 100
SET LINESIZE 220
SET LONG 3000
SET DEFINE OFF

VARIABLE v_case_id NUMBER
VARIABLE v_entity_id_1 NUMBER
VARIABLE v_entity_id_2 NUMBER
VARIABLE v_result_limit NUMBER

EXEC :v_case_id := 1
EXEC :v_entity_id_1 := 36
EXEC :v_entity_id_2 := 37
EXEC :v_result_limit := 20

@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\11_find_indirect_connections.sql

EXIT;
