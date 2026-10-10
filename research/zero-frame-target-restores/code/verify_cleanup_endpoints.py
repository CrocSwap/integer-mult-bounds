"""Recompute the pinned cleanup endpoint charts and inventory on the final word."""
import importlib.util,json,sys
from pathlib import Path
PRE,D,OUT,CLEAN=map(lambda x:Path(x).resolve(),sys.argv[1:])
spec=importlib.util.spec_from_file_location('pinned_endpoints',CLEAN/'endpoints272.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def load(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
receipt=load(D/'CERTIFICATE.json')['receipts']['rewrite']
assert load(OUT/'lead/COHORT249-INITIAL.json')==load(D/'lead/COHORT249-INITIAL.json')
frames=load(OUT/'lead/COHORT249-FRAMES.json');assert frames==load(D/'lead/COHORT249-FRAMES.json')
new={str(e['frame']):frames[str(e['frame'])] for e in receipt['edits']}
generic=load(OUT/'compiler/BANK-REVIEW.json');prior=load(D/'compiler/BANK-REVIEW.json')
assert {k:v for k,v in generic.items() if k!='label'}=={k:v for k,v in prior.items() if k!='label'}
original=PRE/'temporal/CURRENT249-EXPORT';lead=PRE/'targeted'
bank,br=m.banks(original,lead,new,receipt,generic)
expected=load(D/'compiler/COHORT-BANK-REVIEW.json')
assert {k:v for k,v in bank.items() if k!='label'}=={k:v for k,v in expected.items() if k!='label'}
norm=m.normalizers(original,lead,new,(OUT/'lead/COHORT249-RECORDS.bin').read_bytes(),receipt)
assert br['banks_saved_per_stage']==1980 and norm['max_factors']<=548
save(OUT/'compiler/GENERIC-BANK-REVIEW.json',generic);save(OUT/'compiler/BANK-REVIEW.json',bank)
save(OUT/'endpoint-composition-audit.json',{'banks':br,'normalizers':norm,'unchanged_helper_endpoints':True})
print(json.dumps({'banks':br,'normalizers':norm}))
