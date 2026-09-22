-- ============================================================
-- CRIMEMIND
-- 08_investigation_catalog.sql
-- Investigation Questions + SQL Module Catalog
-- Oracle 11g compatible
-- ============================================================

SET DEFINE OFF;

PROMPT ============================================
PROMPT Creating 18 SQL Modules
PROMPT ============================================

-- ------------------------------------------------------------
-- 18 APPROVED SQL MODULES
-- ------------------------------------------------------------

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (1,
     '01_get_recent_contacts',
     '1.0',
     'Retrieves recent contacts and repeated communication relationships for an entity.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (2,
     '02_get_communication_between_entities',
     '1.0',
     'Retrieves communication records between two specified entities.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (3,
     '03_find_entities_near_location',
     '1.0',
     'Finds entities recorded near a specified location during a relevant time period.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (4,
     '04_find_common_locations',
     '1.0',
     'Finds locations commonly visited by multiple entities and summarizes visit frequency.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (5,
     '05_get_entity_location_history',
     '1.0',
     'Retrieves the location history of an entity for a specified period.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (6,
     '06_get_entity_timeline',
     '1.0',
     'Builds a chronological timeline of events associated with an entity.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (7,
     '07_find_timeline_gaps',
     '1.0',
     'Identifies significant gaps in an entity observed timeline.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (8,
     '08_get_events_around_incident',
     '1.0',
     'Retrieves events immediately before, after and around a specified incident.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (9,
     '09_get_direct_relationships',
     '1.0',
     'Retrieves direct relationships associated with a specified entity.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (10,
     '10_get_relationship_between_entities',
     '1.0',
     'Determines the recorded relationship between two specified entities.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (11,
     '11_find_indirect_connections',
     '1.0',
     'Finds indirect connections and shortest known relationship paths between entities.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (12,
     '12_get_strong_entity_relationships',
     '1.0',
     'Identifies entities with strong direct relationships to a specified entity.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (13,
     '13_get_entity_vehicles',
     '1.0',
     'Retrieves vehicles associated with a specified entity.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (14,
     '14_find_vehicles_near_location',
     '1.0',
     'Finds vehicles and associated entities observed near locations during specified periods.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (15,
     '15_get_entity_transactions',
     '1.0',
     'Retrieves and analyzes financial transactions associated with entities.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (16,
     '16_get_entity_evidence',
     '1.0',
     'Retrieves evidence associated with specified entities, events or incidents.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (17,
     '17_find_cross_entity_evidence',
     '1.0',
     'Identifies evidence connecting multiple entities and independently corroborating records.');

INSERT INTO SQL_MODULES
    (MODULE_ID, MODULE_NAME, VERSION, DESCRIPTION)
VALUES
    (18,
     '18_get_case_evidence_ranking',
     '1.0',
     'Ranks case evidence and identifies entities with strong overall evidence associations.');

PROMPT 18 SQL modules inserted.


PROMPT ============================================
PROMPT Creating 40 Investigation Questions
PROMPT ============================================

-- ------------------------------------------------------------
-- 40 CANONICAL INVESTIGATION QUESTIONS
-- ------------------------------------------------------------

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (1,
     'Q01',
     'What recent contacts did a specified entity have?',
     '01_get_recent_contacts');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (2,
     'Q02',
     'What communication occurred between two specified entities?',
     '02_get_communication_between_entities');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (3,
     'Q03',
     'Which entities recently communicated with a specified entity?',
     '01_get_recent_contacts');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (4,
     'Q04',
     'Which communication relationships are repeated or frequent for a specified entity?',
     '01_get_recent_contacts');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (5,
     'Q05',
     'Which entities were recorded near a specified location?',
     '03_find_entities_near_location');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (6,
     'Q06',
     'What is the location history of a specified entity?',
     '05_get_entity_location_history');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (7,
     'Q07',
     'Where was a specified entity observed during a specified period?',
     '05_get_entity_location_history');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (8,
     'Q08',
     'Which entities were near a specified location during a relevant time period?',
     '03_find_entities_near_location');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (9,
     'Q09',
     'Which locations were commonly visited by multiple specified entities?',
     '04_find_common_locations');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (10,
     'Q10',
     'How frequently did each entity visit the locations associated with an investigation?',
     '04_find_common_locations');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (11,
     'Q11',
     'What is the chronological timeline of events associated with a specified entity?',
     '06_get_entity_timeline');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (12,
     'Q12',
     'What events occurred around a specified entity during a specified time period?',
     '06_get_entity_timeline');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (13,
     'Q13',
     'Are there significant gaps in an entity''s observed timeline?',
     '07_find_timeline_gaps');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (14,
     'Q14',
     'What events occurred immediately before a specified incident?',
     '08_get_events_around_incident');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (15,
     'Q15',
     'What events occurred immediately after a specified incident?',
     '08_get_events_around_incident');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (16,
     'Q16',
     'Which entities were active or present around the time of a specified incident?',
     '08_get_events_around_incident');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (17,
     'Q17',
     'What direct relationships does a specified entity have with other entities?',
     '09_get_direct_relationships');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (18,
     'Q18',
     'What relationship exists between two specified entities?',
     '10_get_relationship_between_entities');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (19,
     'Q19',
     'Are two entities connected indirectly through other entities?',
     '11_find_indirect_connections');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (20,
     'Q20',
     'What are the shortest known relationship paths between two specified entities?',
     '11_find_indirect_connections');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (21,
     'Q21',
     'Which entities have the strongest direct relationships with a specified entity?',
     '12_get_strong_entity_relationships');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (22,
     'Q22',
     'Which vehicles are associated with a specified entity?',
     '13_get_entity_vehicles');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (23,
     'Q23',
     'Which vehicles were observed near a specified location during a specified time period?',
     '14_find_vehicles_near_location');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (24,
     'Q24',
     'Which entities were associated with a specified vehicle during a specified period?',
     '14_find_vehicles_near_location');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (25,
     'Q25',
     'Which vehicles or associated entities appear repeatedly across relevant locations or time periods?',
     '14_find_vehicles_near_location');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (26,
     'Q26',
     'What financial transactions are associated with a specified entity?',
     '15_get_entity_transactions');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (27,
     'Q27',
     'What transactions occurred between two specified entities?',
     '15_get_entity_transactions');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (28,
     'Q28',
     'Which entities received or sent the highest transaction amounts within a specified period?',
     '15_get_entity_transactions');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (29,
     'Q29',
     'Which entities share financial links through direct or repeated transactions?',
     '15_get_entity_transactions');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (30,
     'Q30',
     'Are there unusual or repeated financial relationships among entities connected to an investigation?',
     '15_get_entity_transactions');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (31,
     'Q31',
     'What evidence is associated with a specified entity?',
     '16_get_entity_evidence');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (32,
     'Q32',
     'What evidence is associated with a specified event or incident?',
     '16_get_entity_evidence');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (33,
     'Q33',
     'Which evidence items connect multiple entities?',
     '17_find_cross_entity_evidence');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (34,
     'Q34',
     'Which evidence items have the highest reliability scores?',
     '18_get_case_evidence_ranking');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (35,
     'Q35',
     'Which entities have the strongest overall evidence associations?',
     '18_get_case_evidence_ranking');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (36,
     'Q36',
     'Which entities are supported by multiple independent evidence types?',
     '17_find_cross_entity_evidence');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (37,
     'Q37',
     'Which evidence items independently corroborate the same entity or event?',
     '17_find_cross_entity_evidence');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (38,
     'Q38',
     'Which entities are connected to both a specified entity and a specified location?',
     '18_get_case_evidence_ranking');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (39,
     'Q39',
     'Which entities have multiple independent links across communications, locations, relationships, vehicles, transactions, or evidence?',
     '18_get_case_evidence_ranking');

INSERT INTO INVESTIGATION_QUERIES
    (QUERY_ID, QUERY_CODE, QUESTION_TEXT, MODULE_NAME)
VALUES
    (40,
     'Q40',
     'Which entities have the strongest overall association with a specified investigation based on combined temporal, spatial, relational, financial, communication, and evidence signals?',
     '18_get_case_evidence_ranking');

PROMPT 40 investigation questions inserted.


PROMPT ============================================
PROMPT Creating Question → Module Mappings
PROMPT ============================================

-- ------------------------------------------------------------
-- QUERY → MODULE MAPPINGS
-- ------------------------------------------------------------

INSERT INTO QUERY_MODULES
    (QUERY_MODULE_ID, QUERY_ID, MODULE_ID)
SELECT
    q.QUERY_ID,
    q.QUERY_ID,
    m.MODULE_ID
FROM INVESTIGATION_QUERIES q
JOIN SQL_MODULES m
    ON m.MODULE_NAME = q.MODULE_NAME;

PROMPT Query-module mappings inserted.


COMMIT;

PROMPT ============================================
PROMPT INVESTIGATION CATALOG COMPLETE
PROMPT ============================================