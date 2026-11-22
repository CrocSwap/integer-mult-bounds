#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Diagnostic handoff correction for the eleven retired non-pristine lenders.

No existing replay assertion is changed. diagnose=True returns explicit failed
lender obligations and residuals, which this script tests as a separate changed
mechanism. No native or global admission is implied.
"""
from collections import Counter
from fractions import Fraction as Q
import json,sys
from pathlib import Path
import census as C
from replay_core import replay,frame_basis,span,warp
from build_ext import Builder,prefix_plan
from target_transport import verify_transport,controls

HERE=Path(__file__).resolve().parent

def factor(residual,row):
    key=next(iter(row));coeff={}
    for t,delta in residual.items():
        c=delta.get(key,Q(0))/row[key]
        if {k:c*a for k,a in row.items() if c*a} != delta:
            return None
        if c:coeff[t]=-c
    return coeff


def run():
    if not __debug__:raise RuntimeError('assertions must remain enabled')
    C.check_sources();controls()
    census=json.loads((HERE/'CENSUS.json').read_text())
    records=[]
    for name,tag in [('gauge44','base'),('extra','extra')]:
      B=Builder(name,tag);w=B.w;full=C.read(C.VENDOR/'witness'/f'witness_80_{tag}.json');v=w['v'];L=644;i=B.block_of[L]['first_input']
      plan,why=prefix_plan(w,B.block_of[L],L,B.skip);assert why is None
      for baseline in ('high48','full80'):
        inv=C.subset_witness(full,set() if baseline=='high48' else {p['register'] for p in full['pairs'] if p['low']})
        case=next(c for c in census['cases'] if c['provider']==name and c['baseline']==baseline)
        for cand in case['unused_nonzero_lenders']:
          if not(cand['retired'] and cand['first_use_dim_allows_rankzero']):continue
          r=cand['register'];p=B.make_pair(L,r,True,plan)
          assert span(p['retirement_basis'])==span(cand['current_basis'])
          trial=dict(inv,pairs=inv['pairs']+[p]);trace=[];probe={i:None}
          diag=replay(w,B.blocks,trial,diagnose=True,trace_handoff=trace,probe=probe)
          op=len(trial['pairs']);tr=next(t for t in trace if t[0]==op)
          transformed=warp(tr[4],op)
          coeff=factor(diag['residual'],transformed)
          rec=dict(provider=name,baseline=baseline,lender=r,operator=op,handoff=i,source_row=C.encode_row(tr[4]),
             source_frame=tr[5],handoff_frame=p['handoff_basis'],pristine_obligation_passes=next(ok for k,old,ok in diag['lender_check'] if k==op),
             residual_factors=coeff is not None,final_residual={str(t):C.encode_row(row) for t,row in diag['residual'].items()})
          if coeff is not None:
            suffix=[e for j,phase,e in C.actual_events(w,B.blocks,trial) if j>i or (j==i and phase!='early_tail')]
            vectors=verify_transport(suffix,coeff,set(range(v,2*v)))
            correction=vectors[0];E=span(p['handoff_basis']);frames=probe[i]['cur']
            # At immediate post-warp slot, correction targets have not changed.
            # Promoting them is only free if no new positive rank is introduced;
            # this conservative nomination records containment separately.
            target=[dict(target=t,coefficient=str(a),basis=frames[t],dimension=len(frames[t]),
                         exact_same_frame=span(frames[t])==E,can_climb_to_handoff=span(frames[t])<=E)
                    for t,a in sorted(correction.items())]
            rec.update(final_coefficients={str(t):str(a) for t,a in sorted(coeff.items())},
                       handoff_coefficients={str(t):str(a) for t,a in sorted(correction.items())},
                       target_checks=target,all_target_frames_equal=all(t['exact_same_frame'] for t in target),
                       all_target_frames_contained=all(t['can_climb_to_handoff'] for t in target))
          records.append(rec)
          print(name,baseline,r,'factor',rec['residual_factors'],'same',rec.get('all_target_frames_equal'),'nested',rec.get('all_target_frames_contained'),flush=True)
    result=dict(status='DIAGNOSTIC_EXACT_DYNAMIC_HANDOFF_SCREEN',object='low644; eleven retired rank4 non-pristine lenders; both providers and two baselines',cases=records,
      scope='Exact free-operator residual factorization and full target-suffix transport. Original pristine assertion remains unsatisfied. This is no native admission or exponent claim.')
    (HERE/'DYNAMIC-SCREEN.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':run()
