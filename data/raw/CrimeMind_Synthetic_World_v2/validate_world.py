import os, json, pandas as pd
BASE=os.path.dirname(__file__)
def p(x): return os.path.join(BASE,x)
vr=pd.read_csv(p('05_VEHICLES/registry/vehicles.csv'))
vs=pd.read_csv(p('05_VEHICLES/sightings/vehicle_sightings.csv'))
ac=pd.read_csv(p('07_ACCESS_SECURITY/access_logs/access_logs.csv'))
tx=pd.read_csv(p('04_FINANCIAL/transactions/transactions.csv'))
msgs=pd.read_csv(p('03_COMMUNICATIONS/messages/messages.csv'))
calls=pd.read_csv(p('03_COMMUNICATIONS/calls/calls.csv'))
assert ((vr.owner_person_id=='P009')&(vr.vehicle_id=='V017')).any()
assert ((vs.vehicle_id=='V017')&(vs.location_id=='L011')&(vs.timestamp.str.startswith('2026-03-14'))).sum() >= 2
assert ((ac.person_id=='P009')&(ac.location_id=='L011')&(ac.timestamp.str.startswith('2026-03-14'))).sum() >= 2
assert (tx.reference_number=='REF-LOAN-0228').sum() == 2
assert ((calls.caller_person_id.isin(['P037','P042']))&(calls.receiver_person_id.isin(['P037','P042']))&(pd.to_datetime(calls.timestamp)>='2026-03-07')&(pd.to_datetime(calls.timestamp)<='2026-03-13 23:59:59')).sum() >= 5
assert ((msgs.sender_person_id.isin(['P009','P042']))&(msgs.receiver_person_id.isin(['P009','P042']))&(msgs.timestamp.str.startswith('2026-03-14'))).sum() >= 4
assert os.path.exists(p('14_EVALUATION_ONLY/ground_truth.json'))
for root,_,files in os.walk(BASE):
    for fn in files:
        rel=os.path.relpath(os.path.join(root,fn),BASE).replace('\\','/')
        if rel.startswith('14_EVALUATION_ONLY/') or rel == 'validate_world.py': continue
        try: txt=open(os.path.join(root,fn),encoding='utf-8',errors='ignore').read().lower()
        except: continue
        for bad in ('culprit=','suspect=','guilty=','innocent=','actual_offender','offender_id','is_suspect','is_guilty'):
            assert bad not in txt, (rel,bad)
print('CrimeMind Synthetic World v2 validation: PASS')
