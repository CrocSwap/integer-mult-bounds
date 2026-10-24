#!/usr/bin/env python3
"""Narrow actual-source/census/reserve mutation controls; no numeric replay."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json
from exact_engine import need
from bind_and_check import checked_bytes
H=Path(__file__).resolve().parent;W=H.parent;CAP=W/'09-capsule-cold/capsule-5387-v1'
r=json.loads((H/'5387-receipt-v2.json').read_bytes());controls={}
inv=json.loads(Path(r['invoice']['path']).read_bytes());inv['histograms']['productive']['9']+=128
try:need(sha256(json.dumps(inv).encode()).hexdigest()==r['invoice']['sha256'],'independent invoice SHA256 mismatch')
except ValueError as e:controls['unearned_128_rank9_productive_credit']={'rejected':True,'reason':str(e),'scope':'Immutable independent literal census binding; fraud cannot borrow otherwise favorable moment.'}
else:raise ValueError('unearned credit accepted')
m=json.loads((CAP/'IMMUTABLE-MANIFEST.json').read_bytes());row=next(x for x in m['rows'] if x['path']=='research/eight-owned-relations/WORD.json.gz' and x['binding']=='exact candidate head')
try:checked_bytes(row,(CAP/row['capsule_path']).read_bytes()+b'\0')
except ValueError as e:controls['changed_literal_word']={'rejected':True,'reason':str(e)}
else:raise ValueError('changed source accepted')
alpha=tuple(map(Q,r['ratios']['alpha']));need(alpha[0]>1-Q(1,10**9),'old reserve accepted');controls['predecessor_reserve_1e_9']={'rejected':True,'reason':'alpha lower > 1-1e-9'}
need(1/(1+1024*Q(1,10**13))+Q(4,2**32)>1,'insufficient reserve accepted');controls['insufficient_reserve_1e_13']={'rejected':True,'reason':'normalized completion/rounding envelope >1'}
need(all(x['rejected'] for x in controls.values()),'control missing')
a={'status':'PASS_NEW_CANDIDATE_BINDING_AND_RESERVE_CONTROLS','candidate_head':r['candidate']['head'],'funding_receipt_sha256':sha256((H/'5387-receipt-v2.json').read_bytes()).hexdigest(),'controls':controls,'source_mutated_on_disk':False}
out=H/'5387-binding-controls-v1.json';need(not out.exists(),'immutable control receipt exists');out.write_text(json.dumps(a,indent=2,sort_keys=True)+'\n');out.chmod(0o444);print(sha256(out.read_bytes()).hexdigest())
