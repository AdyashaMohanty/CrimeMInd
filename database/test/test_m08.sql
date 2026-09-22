/* CrimeMind M08 test */
SET PAGESIZE 100
SET LINESIZE 200
SET LONG 2000
SET DEFINE OFF

VARIABLE v_case_id NUMBER;
VARIABLE v_incident_event_id NUMBER;
VARIABLE v_before_minutes NUMBER;
VARIABLE v_after_minutes NUMBER;
VARIABLE v_result_limit NUMBER;

EXEC :v_case_id := 1;
EXEC :v_incident_event_id := 1;
EXEC :v_before_minutes := 60;
EXEC :v_after_minutes := 60;
EXEC :v_result_limit := 20;

@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\08_get_events_around_incident.sql
@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\08_get_events_around_incident.sql
EXIT;
