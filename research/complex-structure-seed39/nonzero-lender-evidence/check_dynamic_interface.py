#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Independent check of recorded dynamic factorization, target suffix and frames.

No census, replay, builder, or target_transport implementation is imported.
Reported source rows/residuals are evidence inputs, not independently regenerated
here. Target frames and scalar suffix are rederived from immutable canonical
words and witness schedules.
"""
import argparse
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
VENDOR=HERE.parent/'anticipatory-stage-evidence/vendor/pr2339'
SOURCE_PINS={'inputs/blocks.json': 'ddfac1dae1fe7cc0a91e7c7205c6d9d0c07c682880aa34eed83bf4ad7384da9f', 'inputs/extra.canonical.json.gz': 'd7e48dcbafa236a2e1e41f7958244211506f7c7630fe6a2d43d2bdf17b7ae015', 'inputs/gauge44.canonical.json.gz': '65c6d17ffee2eacf27bff438f37fc549c9ed0c909cbc7a52976cc75cf2d15b91', 'witness/witness_80_base.json': '9380f74c032b0616d5b13e8ef94b6d9f80cac36239e329357e7d5fcab5283ad0', 'witness/witness_80_extra.json': '6737072dcca47c6e6526bd62a41585dd09026549550c9e62eb53e64b265a6709', 'words/BORROW-WORD-80base.json.gz': '61290abffd8c8225e0abb3958c1506674e256de688fc4cdf358bbe7c981df493', 'words/BORROW-WORD-80extra.json.gz': '1dd2d6f2ae5b5a27b5f89fb830203f0cca7a78d0323a7845e85e1e80f8f6d1a5'}

def need(x,msg):
    if not x:raise ValueError(msg)

def read(p):
    b=p.read_bytes()
    return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def span(xs):
    out={0}
    for x in xs:out|={x^y for y in tuple(out)}
    return frozenset(out)

def touches(g):return g[1:3] if g[0]=='add' else g[1:2]

def row(xs):
    out={}
    for x in xs:
        key=x['source'],tuple(x['operator_word']);q=F(x['coefficient'])
        need(key not in out and q,'sparse row duplicates/zero')
        out[key]=q
    return out

def warprow(r,op):
    return {(v,word[1:] if word and word[0]==-op else (op,)+word):q
            for (v,word),q in r.items()}

def target_step(values,g,v):
    if g[0]=='scale' and v<=g[1]<2*v:
        values[g[1]-v]*=F(g[2],g[3])
    elif g[0]=='add' and v<=g[2]<2*v:
        need(v<=g[1]<2*v,'target read by non-target')
        values[g[1]-v]+=F(g[3],g[4])*values[g[2]-v]

def new_low_prefix(w,blocks,L):
    block=next(b for b in blocks if L in b['helpers']);deadline=block['first_input']
    skipped=set()
    for b in blocks:
        allowed=set(b['helpers'])
        for i in range(b['first_correction'],b['first_input']):
            if set(touches(w['B'][i]))<=allowed:skipped.add(i)
    delta={};deleted=set();rewrites={};v=w['v']
    for i,g in enumerate(w['B'][:deadline]):
        if i in skipped or L not in touches(g):continue
        need(g[0]=='add','low prefix is not an add')
        if g[2]==L and v<=g[1]<2*v:
            a=F(g[3],g[4]);rewrites[i]=[]
            for src,b in delta.items():
                if b:
                    q=a*b;rewrites[i].append(['add',g[1],src,q.numerator,q.denominator,g[-1]])
        else:
            need(g[1]==L and not v<=g[2]<2*v,'unsupported low prefix')
            delta[g[2]]=delta.get(g[2],F(0))+F(g[3],g[4])
        deleted.add(i)
    need(not any(delta.values()),'nonzero low-prefix temporary sum')
    return deadline,skipped,deleted,rewrites

def prepare(provider,baseline):
    w=read(VENDOR/'inputs'/(provider+'.canonical.json.gz'))
    witness=read(VENDOR/'witness'/('witness_80_'+('base' if provider=='gauge44' else 'extra')+'.json'))
    blocks=read(VENDOR/'inputs/blocks.json')['sources'][0]['blocks']
    deadline,skip,deleted,rewrites=new_low_prefix(w,blocks,644)
    pairs=[p for p in witness['pairs'] if baseline=='full80' or not p['low']]
    for p in pairs:
        if not p['low']:continue
        deleted.update(p.get('deleted_prefix_indices',p['deleted_echo_indices']))
        for i,gs in p.get('early_prefix_rewrites',{}).items():
            need(int(i) not in rewrites,'overlapping prefix rewrites');rewrites[int(i)]=gs
    early={}
    for x in witness['early_tail_events']:
        early.setdefault(x['before_B'],[]).append(x['gate'])
    events=[]
    for i in range(len(w['B'])+1):
        for g in early.get(i,[]):events.append((i,'early',g))
        if i==len(w['B']):break
        for g in rewrites.get(i,[]):events.append((i,'rewrite',g))
        if i not in skip and i not in deleted:events.append((i,'original',w['B'][i]))
    v=w['v'];frames={r:span(w['frames'][w['start'][r]]) for r in range(v,2*v)}
    def update(g):
        if g[-1] is None:return
        for r in touches(g):
            if r in frames:
                f=span(w['frames'][g[-1]])
                need(frames[r]<=f,'nonnested original target timeline')
                frames[r]=f
    for section in ('precondition','compensation','A'):
        for g in w[section]:update(g)
    suffix=[]
    for i,phase,g in events:
        if i<deadline or i==deadline and phase=='early':update(g)
        else:suffix.append(g)
    return w,deadline,frames,suffix

def verify_case(c,cache):
    key=c['provider'],c['baseline']
    if key not in cache:cache[key]=prepare(*key)
    w,deadline,frames,suffix=cache[key];v=w['v']
    need(c['handoff']==deadline==1109,'handoff index')
    need(c['operator']==(81 if key[1]=='full80' else 49),'operator metadata')
    R=row(c['source_row']);KR=warprow(R,c['operator'])
    residual={int(t):row(xs) for t,xs in c['final_residual'].items()}
    final={int(t):F(q) for t,q in c['final_coefficients'].items()}
    for t in set(residual)|set(final):
        expected={k:-final.get(t,F(0))*q for k,q in KR.items() if final.get(t,F(0))*q}
        need(residual.get(t,{})==expected,'reported residual does not factor through full source row')
    correction={int(t):F(q) for t,q in c['handoff_coefficients'].items()}
    values=[correction.get(v+t,F(0)) for t in range(v)]
    for g in suffix:target_step(values,g,v)
    need({v+t:q for t,q in enumerate(values) if q}==final,'handoff vector does not transport to final correction')
    E=span(c['handoff_frame']);claimed={x['target']:x for x in c['target_checks']}
    need(set(claimed)==set(correction),'target coverage')
    measured=[]
    for t,q in sorted(correction.items()):
        need(span(claimed[t]['basis'])==frames[t],'reported target frame differs from independent schedule')
        need(F(claimed[t]['coefficient'])==q,'reported target coefficient')
        dimension=(len(frames[t]).bit_length()-1)
        contained=frames[t]<=E;equal=frames[t]==E
        need(claimed[t]['dimension']==dimension and claimed[t]['can_climb_to_handoff']==contained
             and claimed[t]['exact_same_frame']==equal,'reported frame predicate')
        rank=(len(E).bit_length()-1)+dimension-2*((len(E&frames[t])).bit_length()-1)
        measured.append(dict(target=t,dimension=dimension,recursive_rank=rank,contained=contained))
    need(c['all_target_frames_equal']==all(x['recursive_rank']==0 for x in measured),'same-frame aggregate')
    need(c['all_target_frames_contained']==all(x['contained'] for x in measured),'containment aggregate')
    return dict(provider=key[0],baseline=key[1],lender=c['lender'],factorization=True,
                target_transport=True,independent_frames=True,target_checks=measured)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--input',type=Path,default=HERE/'DYNAMIC-SCREEN.json');ap.add_argument('--out',type=Path,default=HERE/'DYNAMIC-INDEPENDENT-CHECK.json');a=ap.parse_args()
    for name,digest in SOURCE_PINS.items():need(sha(VENDOR/name)==digest,'immutable source pin: '+name)
    before=sha(a.input);data=read(a.input);need(len(data['cases'])==44,'expected complete44-case screen')
    cache={};records=[verify_case(c,cache) for c in data['cases']]
    need(before==sha(a.input),'input changed during independent check')
    # Actual mutation controls; each must fail an independently rederived obligation.
    controls=[]
    for name,mutate in [
      ('missing_residual_column',lambda c:c['final_residual'][next(iter(c['final_residual']))].pop()),
      ('wrong_handoff_coefficient',lambda c:c['handoff_coefficients'].__setitem__('135','-1/2')),
      ('forged_target_frame',lambda c:c['target_checks'][0].__setitem__('basis',c['handoff_frame']))]:
        c=json.loads(json.dumps(data['cases'][0]));mutate(c)
        try:verify_case(c,cache)
        except ValueError as e:controls.append(dict(name=name,rejected=True,reason=str(e)))
        else:raise ValueError('negative control accepted: '+name)
    paths=[VENDOR/'inputs/blocks.json']+[VENDOR/'inputs'/(p+'.canonical.json.gz') for p in ('gauge44','extra')]+[VENDOR/'witness'/('witness_80_'+p+'.json') for p in ('base','extra')]
    result=dict(status='PASS_INDEPENDENT_DYNAMIC_FACTOR_SUFFIX_FRAMES_NO_FREE_HANDOFF',
                input_sha256=before,source_sha256={str(p.relative_to(VENDOR)):sha(p) for p in paths},
                records=records,negative_controls=controls,
                scope='44 reported row/residual factorizations checked, not independently regenerated; target suffix and frames independently reconstructed from pinned source words/witnesses. No emitted native program, recursive labels, global admission or new kappa.')
    a.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'])

if __name__=='__main__':main()
