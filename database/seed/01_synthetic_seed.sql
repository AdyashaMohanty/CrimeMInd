-- Minimal synthetic integration seed.
MERGE INTO locations l USING (
 SELECT 'L001' ref,'Meridian House' name,'MIXED_USE' typ,'Nandipur' addr,20.2900000 lat,85.8200000 lon FROM dual UNION ALL
 SELECT 'L002','East Corridor','CORRIDOR','Meridian House',20.2907000,85.8208000 FROM dual UNION ALL
 SELECT 'L003','Service Entrance','SERVICE','Meridian House',20.2910000,85.8210000 FROM dual
) s ON(l.external_reference=s.ref)
WHEN MATCHED THEN UPDATE SET l.location_name=s.name,l.location_type=s.typ,l.address=s.addr,l.latitude=s.lat,l.longitude=s.lon
WHEN NOT MATCHED THEN INSERT(location_id,external_reference,location_name,location_type,address,latitude,longitude)
VALUES(seq_locations.NEXTVAL,s.ref,s.name,s.typ,s.addr,s.lat,s.lon);

MERGE INTO entities e USING (
 SELECT 'P001' ref,'Arvind Malhotra' name FROM dual UNION ALL SELECT 'P002','Leena Malhotra' FROM dual UNION ALL
 SELECT 'P003','Synthetic Person 003' FROM dual UNION ALL SELECT 'P004','Synthetic Person 004' FROM dual
) s ON(e.external_reference=s.ref)
WHEN MATCHED THEN UPDATE SET e.display_name=s.name
WHEN NOT MATCHED THEN INSERT(entity_id,entity_type_id,display_name,external_reference)
VALUES(seq_entities.NEXTVAL,(SELECT entity_type_id FROM entity_types WHERE type_name='PERSON'),s.name,s.ref);

MERGE INTO vehicles v USING (
 SELECT 'V001' ref,'CAR' typ,'Compact Hatchback' model,'SYN-V001' reg FROM dual UNION ALL
 SELECT 'V002','VAN','Delivery Van','SYN-V002' FROM dual UNION ALL SELECT 'V003','CAR','Sedan','SYN-V003' FROM dual
) s ON(v.external_reference=s.ref)
WHEN MATCHED THEN UPDATE SET v.vehicle_type=s.typ,v.make_model=s.model,v.registration_reference=s.reg
WHEN NOT MATCHED THEN INSERT(vehicle_id,external_reference,vehicle_type,make_model,registration_reference)
VALUES(seq_vehicles.NEXTVAL,s.ref,s.typ,s.model,s.reg);
COMMIT;
