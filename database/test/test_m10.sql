/* CrimeMind TEST_M10 */
SET PAGESIZE 100
SET LINESIZE 220
SET LONG 3000
SET DEFINE OFF

VARIABLE v_case_id NUMBER;
VARIABLE v_entity_id_1 NUMBER;
VARIABLE v_entity_id_2 NUMBER;

EXEC :v_case_id := 1;
EXEC :v_entity_id_1 := 36;
EXEC :v_entity_id_2 := 37;

@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\10_get_relationship_between_entities.sql

EXIT;
