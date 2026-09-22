SET PAGESIZE 100
SET LINESIZE 220
SET LONG 3000
SET DEFINE OFF
VARIABLE v_case_id NUMBER
VARIABLE v_location_id NUMBER
VARIABLE v_vehicle_id NUMBER
VARIABLE v_start_time VARCHAR2(100)
VARIABLE v_end_time VARCHAR2(100)
VARIABLE v_result_limit NUMBER
EXEC :v_case_id := 1
EXEC :v_location_id := 25
EXEC :v_vehicle_id := NULL
EXEC :v_start_time := TO_TIMESTAMP_TZ('01-APR-2026 00:00:00 +05:30', 'DD-MON-YYYY HH24:MI:SS TZH:TZM');
EXEC :v_end_time   := TO_TIMESTAMP_TZ('30-APR-2026 23:59:59 +05:30', 'DD-MON-YYYY HH24:MI:SS TZH:TZM');
EXEC :v_result_limit := 20
@C:\Users\KIIT0001\Downloads\CrimeMind_Folder\CrimeMind\database\sql_modules\14_find_vehicles_near_location.sql
EXIT;
