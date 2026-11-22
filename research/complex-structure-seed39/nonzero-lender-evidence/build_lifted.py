#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""One explicit lifted-target compensation candidate; formal replay only."""
from collections import Counter
from fractions import Fraction as Q
import copy,json
from pathlib import Path
import census as C
from replay_lifted import replay
from target_transport import step
HERE=Path(__file__).resolve().parent

def build(name,tag,baseline):
    w=C.read(C.VENDOR/'inputs'/f'{name}.canonical.json.gz')
    blocks=C.read(C.VENDOR/'inputs/blocks.json')['sources'][0]['blocks']
    full=C.read(C.VENDOR/'witness'/f'witness_80_{tag}.json')
    inv=C.subset_witness(full,set() if baseline=='high48' else {p['register'] for p in full['pairs'] if p['low']})
    cases=C.read(HERE/'CENSUS.json')['cases'];case=next(c for c in cases if c['provider']==name and c['baseline']==baseline)
    rec=case['repaired_candidates'][0];pair=copy.deepcopy(rec['pair'])
    pair['handoff_basis']=[504,30,95,20]
    inv['pairs'].append(pair);op=len(inv['pairs'])
    for g in rec['restoration_gates']:
        inv['early_tail_events'].append({'before_B':pair['handoff_B'],'gate':g})
    # Initial cancellation must be transported through target precondition.
    coeff={162:Q(-1),220:Q(1)};targets=set(range(w['v'],2*w['v']))
    for g in w['precondition']+w['compensation']:coeff=step(coeff,g,targets)
    assert coeff=={135:Q(1,2),146:Q(-1,2),162:Q(1,2),220:Q(1,2)}
    line=next(i for i,F in enumerate(w['frames']) if C.span(F)==C.span([30]))
    inv['lifted_target_frames']={str(t):line for t in coeff}
    inv['post_wrapper_corrections']=[dict(target=t,source=33,operator=op,coefficient=str(c)) for t,c in sorted(coeff.items())]
    r=replay(w,blocks,inv,expect_pairs=len(inv['pairs']))
    widths=C.inventory(w,inv,r)
    old=case['baseline_profile'];pd={k:r['local_profile'].get(k,0)-old.get(str(k),0) for k in sorted(set(r['local_profile'])|set(map(int,old)))}
    wd={k:widths.get(k,0)-case['baseline_widths'].get(str(k),0) for k in sorted(set(widths)|set(map(int,case['baseline_widths'])))}
    return dict(provider=name,baseline=baseline,witness=inv,replay=r,width_inventory=widths,
        local_profile=r['local_profile'],profile_delta={k:v for k,v in pd.items() if v},width_delta={k:v for k,v in wd.items() if v},
        status='PASS_FORMAL_LIFTED_TARGET_COMPENSATION_NO_NATIVE_OR_GLOBAL_ADMISSION')

def main():
    if not __debug__:raise RuntimeError('assertions must remain enabled')
    C.check_sources();out=[]
    for name,tag in [('gauge44','base'),('extra','extra')]:
      for baseline in ('high48','full80'):
        r=build(name,tag,baseline);out.append(r)
        print(name,baseline,r['profile_delta'],r['width_delta'],r['replay']['local_mass'],flush=True)
    (HERE/'LIFTED-CANDIDATE.json').write_text(json.dumps({'cases':out,'scope':'Finite free-operator replay of changed compensation placement and COPY profile. Physical G flag products checked separately. Native/global admission remains open.'},indent=2)+'\n')
if __name__=='__main__':main()
