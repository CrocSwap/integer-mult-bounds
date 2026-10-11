from pathlib import Path
import json,hashlib
from fractions import Fraction as Q
O=Path(__file__).resolve().parent;ROOT=O.parents[2];P=ROOT/'experiments/architecture/whole-owner-pooling-v4/bit60';rd=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();C=P/'CHECKPOINT.json';assert sha(C)=='4129ad82bca0a4a199dac8ecc0a04fd951e44da987f76190a96823d73a53c7a6'
ck=rd(C)
for path,h in ck['files'].items():assert sha(Path(path))==h
pins=rd(P/'SOURCE-PINS.json')
for path,h in pins['external'].items():assert sha(Path(path))==h
parent=ROOT/'experiments/architecture/target-prefix-multipair-complete/global/signed'
for path,e in pins['parent_local_byte_identity'].items():assert sha(Path(path))==sha(Path(e['parent']))==e['sha256']
attrib=rd(P/'ATTRIBUTION-SOURCE-PINS.json')
for e in attrib:
 p=ROOT/'experiments/verification/proposal-scout/pr455'/e['name'];b=p.read_bytes();assert hashlib.sha256(b).hexdigest()==e['sha256'];assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==e['sha']
receipts=['WHOLE-POOL60-BIT-ASSIGNMENT.json','WHOLE-POOL60-BIT-TEMPLATE.json','WHOLE-POOL60-PREFIX-CUT.json','WHOLE-POOL60-BIT-SIGMA.json','WHOLE-POOL60-BIT-ARITHMETIC.json','WHOLE-POOL60-WORD.json','WHOLE-POOL60-OPERATOR-REVIEW.json'];rbind={}
for name in receipts:
 p=O/name;r=rd(p);assert r['status'].startswith('PASS');rbind[name]=sha(p)
 for key in ['inputs','input_sha256','source_files']:
  for rel,h in r.get(key,{}).items():assert sha(ROOT/rel)==h
arith=rd(O/'WHOLE-POOL60-BIT-ARITHMETIC.json');assert arith['kappa']==ck['kappa'];assert arith['prefix_bits']==159 and arith['cube_bits']==532 and arith['row_coefficient']==19431
out={'status':'PASS_INDEPENDENT_SOURCE_BOUND_CONDITIONAL_SIGNED60_WHOLE_OWNER_POOL_FINITE_SCIENCE','checkpoint_sha256':sha(C),'checkpoint_files':len(ck['files']),'kappa':arith['kappa'],'gain_over_frozen56':str(100*(Q(arith['kappa'])/Q(78712924282401861620781,62500000000000000000000000)-1)),'live':9600,'physical':9609,'dimension':78,'rankmass':745536,'deficit':3264,'whole_helper_owners':65120,'foreign_replica_owners':52484,'selected_78_column_maps':65120,'unchanged_signed60_source_files':len(pins['parent_local_byte_identity']),'target_relative_charts':1320,'target_owner_gate_instances':10560,'target_negative_controls_source_bound':2520,'extra_target_selector_calls':253693440,'additional_helper_selector_factors':3,'dispatch_paid':100000,'prefix_bits':159,'three_level_coefficient_bits':532,'charged_cube_bits':1024,'row_reserve_used':19431,'row_reserve_allowed':20161,'receipts':rbind,'attribution':'Whole-family replica pooling adapted from Dugongue PR455 f76fc4e36030d4e00b4cbb83b1dbc661a0974c4e, pinned public proofs and allocator sources. Own60 signed target-prefix word retained; nativePR455rank147 provider and cross-family splithelper rules not imported. Complex direct8-eleven451 supplier retained under its separately sealed science gate.','scope':'Exact finite owner/window/axis/injective cover charts, literal1,713,800-eventtransport, fresh signed980/dirt/inverse/forwardcommonframe and exactall120integerdecoderadjoint equality tofrozen56, plus unchangedparent60reflected/compilerproof transfer, fullpaidinvoice, dualmoment adjacent signs,8bootstrap/full47outerformulas and controls. Stage-cutprefix requires explicit universalcompletephysicaldirtyslot endpoint/helperaddressisometry/workzero, FULLcover dataownerbijection and inactivehostpair conditions. Allsize compiler, correlatedbank/compressedwindow, precision/tape/commonprime/recovery/analytic/C_full remain conditional. No unconditional theorem, packing optimality, nativeF2-only signedprovider, newnorm2 or GLcompiler claim. Publication/sourceprojection/privacy/portableclosure are separate release gates.'}
(O/'SCIENCE-GATE-WHOLE-POOL60.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['checkpoint_files'])
