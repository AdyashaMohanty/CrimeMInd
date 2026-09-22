-- Q1-Q40 routing catalog. Canonical wording remains in the approved SRS.
MERGE INTO sql_modules m USING (
 SELECT LEVEL id,'M'||LEVEL name,'1.0' ver,'Oracle deterministic investigation SQL module '||LEVEL descr
 FROM dual CONNECT BY LEVEL<=18
) s ON(m.module_id=s.id)
WHEN MATCHED THEN UPDATE SET m.module_name=s.name,m.version=s.ver,m.description=s.descr
WHEN NOT MATCHED THEN INSERT(module_id,module_name,version,description) VALUES(s.id,s.name,s.ver,s.descr);

MERGE INTO investigation_queries q USING (
 SELECT LEVEL id,'Q'||LEVEL code,'Investigation question Q'||LEVEL||' (canonical wording maintained by SRS)' question,
 'M'||CASE LEVEL WHEN 1 THEN 1 WHEN 2 THEN 2 WHEN 3 THEN 1 WHEN 4 THEN 1 WHEN 5 THEN 3 WHEN 6 THEN 5 WHEN 7 THEN 5 WHEN 8 THEN 3 WHEN 9 THEN 4 WHEN 10 THEN 4 WHEN 11 THEN 6 WHEN 12 THEN 6 WHEN 13 THEN 7 WHEN 14 THEN 8 WHEN 15 THEN 8 WHEN 16 THEN 8 WHEN 17 THEN 9 WHEN 18 THEN 10 WHEN 19 THEN 11 WHEN 20 THEN 11 WHEN 21 THEN 12 WHEN 22 THEN 13 WHEN 23 THEN 14 WHEN 24 THEN 14 WHEN 25 THEN 14 WHEN 26 THEN 15 WHEN 27 THEN 15 WHEN 28 THEN 15 WHEN 29 THEN 15 WHEN 30 THEN 15 WHEN 31 THEN 16 WHEN 32 THEN 16 WHEN 33 THEN 17 WHEN 34 THEN 18 WHEN 35 THEN 18 WHEN 36 THEN 17 WHEN 37 THEN 17 WHEN 38 THEN 18 WHEN 39 THEN 18 ELSE 18 END module_name
 FROM dual CONNECT BY LEVEL<=40
) s ON(q.query_id=s.id)
WHEN MATCHED THEN UPDATE SET q.query_code=s.code,q.question_text=s.question,q.module_name=s.module_name
WHEN NOT MATCHED THEN INSERT(query_id,query_code,question_text,module_name) VALUES(s.id,s.code,s.question,s.module_name);

INSERT INTO query_modules(query_module_id,query_id,module_id)
SELECT seq_query_modules.NEXTVAL,q.query_id,m.module_id FROM investigation_queries q JOIN sql_modules m ON m.module_name=q.module_name
WHERE NOT EXISTS(SELECT 1 FROM query_modules x WHERE x.query_id=q.query_id AND x.module_id=m.module_id);
COMMIT;
