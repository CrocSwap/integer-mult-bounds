"""Actual helper240 first/last mixed-character deficit for aligned two carriers."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
O=Path(__file__).resolve().parent;ROOT=O.parents[2];source=ROOT/'experiments/architecture/collective-common-frame-bit/composed/records/frames.json';frames=json.load(open(source))['frames'];E=frames['2'];H=frames['1'];assert E['dim']==1 and H['dim']==8;assert len(E['B'])==1 and E['B'][0]==[2,0,0,0,0,0,0,0];bound=json.load(open(O/'BOUND-SPLITS.json'));witnesses=[w for c in bound['cases']for w in c['helper240_splits']if sorted(p[2]for p in w['parts'])==[1,7]];assert witnesses
out=[]
for m in(8,64,78):
 for q in(3,5,7):
  N=q**(2*m);old=F(N,4)*(1-F(1,q)+F(1,q**8)-F(1,q**7));assert old.denominator==1
  for a in(1,7):
   physical=F(N,4)*(1-F(1,q)+F(1,q**a)-F(1,q**(a-1)));gap=old-physical
   assert physical.denominator==gap.denominator==1 and gap>0
   assert gap==F(N,4)*(q-1)*(F(1,q**a)-F(1,q**8))
   out.append({'m':m,'address_field':q,'piece_containing_first_line_rank':a,'logical_minus_plus_joint_rank':str(old),'physical_minus_plus_joint_rank':str(physical),'strict_rank_gap':str(gap)})
r={'status':'EXACT_ACTUAL_HELPER_FIRST_LAST_ALIGNED_FIXED_ENCODING_OBSTRUCTION','helper':240,'first_frame':2,'last_frame':1,'first_rank':1,'total_rank':8,'split_widths':[7,1],'selected_actual_splits':witnesses,'cases':out,'frames_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'bound_splits_sha256':hashlib.sha256((O/'BOUND-SPLITS.json').read_bytes()).hexdigest(),'general_formula':'N/4*(q-1)*(q^(-a)-q^(-8))>0, a=1 or7, any odd q and m>=8. Here N=q^(2m).','scope':'Assumes one time-independent injective value encoding intertwines both actual first MOVE and final residual, and that each split frame acts independently on its own carrier via aligned address blocks. Rank-one first projector commuting with carrier block projector lies wholly in one piece. No such embedding can fit all original logical columns. Nonaligned cross-family intermediate MOVE, time-dependent encoding, explicit spectator correction or a changed local endpoint are outside this contract; must be paid and checked separately. Logical and physical streams are assumed to have the same full N=q^(2m) arbitrary value-address dimension; restricted local windows need a separate domain audit.'};(O/'FIRST-LAST-GATE.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status']);print('actual witnesses',len(witnesses),'small gaps',[(x['piece_containing_first_line_rank'],x['strict_rank_gap'])for x in out[:2]])
