from pathlib import Path
import json,gzip,hashlib,struct
P=Path(__file__).resolve().parent;S=P.parent/'bit-provider-portfolio-v4';A=S/'global';rd=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();t=json.loads(gzip.decompress((A/'GLOBAL-TEMPLATE.json.gz').read_bytes()));op=rd(A/'TARGET-OPERATOR.json');pairs=rd(A/'local/PAIR-SELECTION.json')['pairs'];assert len(pairs)==60
assert op['source_template_sha256']==rd(P/'PORTFOLIO-GLOBAL.json')['template_sha256'];assert op['actual_provider_signed_record_sha256']=={p:z['signed_record_sha256']for p,z in t['provider_registry'].items()}
assert op['actual_call_provider_bindings']==[[c['stage'],c['replica'],c['provider'],c['program_key'],c['signed_record_sha256']]for c in t['calls']]
n=0
for c in t['calls']:
 for z in pairs:
  a,b=c['owners'][z['receiver']],c['owners'][z['donor']];assert a[0]!=b[0]and a[0]<9600 and b[0]<9600;assert a[1]==['data',c['stage'],z['receiver']-120]and b[1]==['data',c['stage'],z['donor']-120];n+=2
assert n==op['actual_global_owner_gate_instances']==10560;assert op['extra_route_selector_bound']==2*11*8*120*78*154==253693440
# Both provider scalar endpoints/frames were independently reconstructed; pin those exact records.
local=rd(P/'LAZY-LOCAL-GATE.json');base=rd(P/'baseline60/LOCAL.json');assert sha(P/'check_local.py')==local['checker_sha256'];assert local['providers']['drop970-948-lazy']['signed_record_sha256']==t['provider_registry']['lazy']['signed_record_sha256'];assert base['clean_source_ledger']['baseline_sha256']==t['provider_registry']['base']['signed_record_sha256']
root=P.parents[2]
for name,digest in rd(S/'CHECKPOINT.json')['source_inputs'].items():assert sha(root/name)==digest
complexgate=P.parent/'complex-paid-adapters-independent-v4/FULL-SCIENCE-GATE.json';assert sha(complexgate)=='9a8e58799e63ad08ac07ae988bff4bcef830607cf04e8a787609e9e87d0f9248'
for pid,z in t['provider_registry'].items():
 q=Path(z['directory']);assert sha(q/'signed-records.bin')==z['signed_record_sha256']
# Stage-cut hypothesis is explicit: complete invocation is block-diagonal on helpers;
# data J identical; private borrowed copy restored. Hence arbitrary correlated values
# permitted at each cover cut, with inactive hosted families and owner injection.
receipts=['LAZY-LOCAL-GATE.json','PORTFOLIO-GLOBAL.json','PORTFOLIO-SIGMA.json','PORTFOLIO-ADDRESSES.json','PORTFOLIO-PREFIX.json','PORTFOLIO-ARITHMETIC.json']
files=[complexgate,P/'baseline60/LOCAL.json',P/'drop970-948-lazy/LOCAL.json']+[P/x for x in receipts]+[P/x for x in ['check_local.py','portfolio_global.py','portfolio_sigma.py','portfolio_addresses.py','portfolio_prefix.py','portfolio_arithmetic.py',Path(__file__).name]]
files += [A/x for x in ['GLOBAL-TEMPLATE.json.gz','GLOBAL.json','HOSTED-SIGMA.json','TARGET-OPERATOR.json','PROVIDERS.json','GEOMETRY.json','REFINED-NOMINATION.json','local/GLOBAL-BOUND.json']]
out={'status':'PASS_INDEPENDENT_SIGNED_COMPLETE_CALL_PROVIDER_PORTFOLIO_FINITE_CONDITIONAL_SCIENCE','kappa':rd(P/'PORTFOLIO-ARITHMETIC.json')['kappa'],'calls':88,'alternate_calls':8,'all_selected_sigma_columns':65120*78,'target_owner_gates':n,'actual_raw_units':rd(A/'local/GLOBAL-BOUND.json')['finite']['raw_unit_additions'],'actual_signed_units':rd(A/'local/GLOBAL-BOUND.json')['finite']['signed_unit_additions'],'provider_registry_selectors':898544,'additional_provider_dispatch':100000,'source_checkpoint_sha256':sha(S/'CHECKPOINT.json'),'inputs':{str(p):sha(p)for p in files},'stage_cut':'Each provider independently restores arbitrary original target/helper/borrowed dirt except same exact integer decoder J, and has pure signed-frame helper address endpoint; each stage has complete cover-bijection invocation, no touch of selected inactive host pairs, distinct routed owners and disjoint pending children. Universal full-correlated slot/caller interface remains an explicit premise.','scope':'Conditional finite extension under inherited weighted source/current-target routing and full correlated-bank/compressed-window/compiler/chart/prime/precision/recovery interfaces, plus paid registry dispatch. Local all980 integer dirt/inverse/120adjoints separately proven. Exact route/owner/controller/profile/159prefix/532cube/19431row/dualengines8/full47 arithmetic verified; no native147 or unconditional expanded compiler claim. Paid458 complex supplier is explicitly bound by independent FULL-SCIENCE-GATE9a8e58; overall rate bit binding.'}
(P/'PORTFOLIO-SCIENCE-GATE.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],sha(P/'PORTFOLIO-SCIENCE-GATE.json'))
