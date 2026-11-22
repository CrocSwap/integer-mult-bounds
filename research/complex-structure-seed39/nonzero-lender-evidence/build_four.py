#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Four low aliases with shared lifted-target compensation, formal full replay."""
from collections import defaultdict
from fractions import Fraction as Q
import copy,json
from pathlib import Path
import census as C
from replay_lifted import replay
from target_transport import step
HERE=Path(__file__).resolve().parent

def build(case):
    name=case['provider'];tag='base' if name=='gauge44' else 'extra';baseline=case['baseline']
    w=C.read(C.VENDOR/'inputs'/f'{name}.canonical.json.gz');blocks=C.read(C.VENDOR/'inputs/blocks.json')['sources'][0]['blocks']
    full=C.read(C.VENDOR/'witness'/f'witness_80_{tag}.json')
    inv=C.subset_witness(full,set() if baseline=='high48' else {p['register'] for p in full['pairs'] if p['low']})
    inv['pairs']+=copy.deepcopy(case['pairs'])
    for g in case['restoration_gates']:inv['early_tail_events'].append({'before_B':1109,'gate':g})
    groups=defaultdict(dict);targets=set(range(w['v'],2*w['v']))
    for term in case['abstract_initial_corrections']:
        op,=term['operator_word'];key=(term['source'],op);groups[key][term['target']]=Q(term['coefficient'])
    corr=[]
    for (source,op),coeff in groups.items():
        for g in w['precondition']+w['compensation']:coeff=step(coeff,g,targets)
        corr += [dict(target=t,source=source,operator=op,coefficient=str(c)) for t,c in sorted(coeff.items())]
    targetset={t['target'] for t in corr};assert targetset=={135,146,162,220}
    line=next(i for i,F in enumerate(w['frames']) if C.span(F)==C.span([30]))
    inv['lifted_target_frames']={str(t):line for t in sorted(targetset)};inv['post_wrapper_corrections']=corr
    r=replay(w,blocks,inv,expect_pairs=len(inv['pairs']));widths=C.inventory(w,inv,r)
    oldcase=next(c for c in C.read(HERE/'CENSUS.json')['cases'] if c['provider']==name and c['baseline']==baseline)
    old=oldcase['baseline_profile'];pd={k:r['local_profile'].get(k,0)-old.get(str(k),0) for k in sorted(set(r['local_profile'])|set(map(int,old)))}
    wd={k:widths.get(k,0)-oldcase['baseline_widths'].get(str(k),0) for k in sorted(set(widths)|set(map(int,oldcase['baseline_widths'])))}
    return dict(provider=name,baseline=baseline,witness=inv,replay=r,width_inventory=widths,local_profile=r['local_profile'],
       profile_delta={k:v for k,v in pd.items() if v},width_delta={k:v for k,v in wd.items() if v},
       status='PASS_FORMAL_FOUR_LIFTED_TARGET_ALIASES_NO_NATIVE_OR_GLOBAL_ADMISSION')

def main():
    if not __debug__:raise RuntimeError('assertions must remain enabled')
    C.check_sources();out=[]
    for case in C.read(HERE/'FLAG-FOUR.json')['cases']:
        r=build(case);out.append(r);print(r['provider'],r['baseline'],r['profile_delta'],r['width_delta'],r['replay']['local_mass'],flush=True)
    (HERE/'FOUR-CANDIDATE.json').write_text(json.dumps(dict(cases=out,scope='Complete finite free-operator forward replay and full inverse cleanup. Native both-orientation physical emission and global admission remain open.'),indent=2)+'\n')
if __name__=='__main__':main()
