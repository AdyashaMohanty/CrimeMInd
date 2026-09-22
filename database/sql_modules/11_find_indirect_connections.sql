/*
 M11 - Indirect connections
 Q19: Are two entities connected indirectly through other entities?
 Q20: What are the shortest known relationship paths between two entities?

 Binds:
 :v_case_id
 :v_entity_id_1
 :v_entity_id_2
 :v_result_limit

 Oracle 11g compatible.

 ENTITY_RELATIONSHIPS stores SOURCE_ENTITY_ID -> TARGET_ENTITY_ID.
 For investigation connectivity, traversal is treated as undirected.
 No inline UNION is used because SQL*Plus/Oracle XE 11g was rejecting the
 previous derived-edge formulation.
*/

SELECT *
FROM (
    SELECT
        :v_entity_id_1 AS start_entity_id,
        :v_entity_id_2 AS target_entity_id,
        LEVEL - 1 AS path_length,
        LTRIM(
            SYS_CONNECT_BY_PATH(
                TO_CHAR(er.relationship_id),
                ' -> '
            ),
            ' -> '
        ) AS relationship_path,
        CASE
            WHEN er.source_entity_id = :v_entity_id_2
              OR er.target_entity_id = :v_entity_id_2
            THEN 'TARGET_REACHED'
            ELSE 'INTERMEDIATE'
        END AS path_status
    FROM ENTITY_RELATIONSHIPS er
    JOIN CASE_ENTITIES cs
      ON cs.case_id = :v_case_id
     AND cs.entity_id = er.source_entity_id
    JOIN CASE_ENTITIES ct
      ON ct.case_id = :v_case_id
     AND ct.entity_id = er.target_entity_id
    START WITH er.source_entity_id = :v_entity_id_1
            OR er.target_entity_id = :v_entity_id_1
    CONNECT BY NOCYCLE
           (
               PRIOR er.target_entity_id = er.source_entity_id
               OR PRIOR er.source_entity_id = er.target_entity_id
           )
           AND LEVEL <= 7
)
WHERE path_status = 'TARGET_REACHED'
  AND path_length > 1
ORDER BY path_length, relationship_path;
