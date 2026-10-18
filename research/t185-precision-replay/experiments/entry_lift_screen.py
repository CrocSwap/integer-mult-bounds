#!/usr/bin/env python3
"""Bounded changed-entry screening with least forward frame joins.

Not a native identity/admission verifier. Existing warps, centre paths, target
levels, endpoints and operation order are retained; only gate frames may grow.
Apache-2.0. OpenAI Codex assisted, 2026-10-16.
"""
import argparse,collections,copy,gzip,hashlib,json,math,time
from pathlib import Path
from screen_raw_basis import basis,read_word
from fractions import Fraction as F

def run(w,r,line):
    v=w['report']['v'];h=w['report']['h'];n=2*v+w['report']['R'];full=basis([1<<i for i in range(h)])
    end=[full]*v+[basis([x for x in range(1,1<<h) if (x&p).bit_count()%2==0]) for p in w['ports']]+[full]*w['report']['R']
    for q,U in w['helper_final'].items():end[int(q)]=basis(U)
    start=[(p,) for p in w['ports']]+[()]*(n-v)
    for q,U in w['start_extra'].items():start[int(q)]=basis(U)
    if r is not None:start[r]=basis([line])
    cur=start.copy();paid=collections.Counter();changes=[]
    def climb(q,U):
        if basis(cur[q]+U)!=U:raise ValueError(('end-frame',q))
        d=len(U)-len(cur[q])
        if d:paid[d]+=1
        cur[q]=U
    def step(g,where):
        if g[0]=='warp':
            if cur[g[1]]!=basis(g[3]):raise ValueError(('warp-input',where,g[1]))
            cur[g[1]]=basis(g[4]);return
        qs=g[1:3] if g[0]=='add' else g[1:2]
        U=basis(g[-1]);joined=basis(U+tuple(z for q in qs for z in cur[q]))
        if joined!=U:changes.append((where,list(U),list(joined)))
        for q in qs:climb(q,joined)
    for i,g in enumerate(w['A']):step(g,('A',i))
    lev={int(t):basis(U) for t,U in w['target_levels'].items()}
    for t in range(v):
        if cur[v+t]!=lev.get(t,()):raise ValueError(('target-level',t))
    for q,U in zip(w['centers'],w['center_frames']):
        U=basis(U)
        if cur[q]!=U:raise ValueError(('centre-frame',q))
        for T in sorted({lev.get(g[1]-v,()) for g in w['cut'] if g[2]==q},key=lambda x:-len(x)):
            if U!=T:paid[len(U)-len(T)]+=1
            U=T
    warps=collections.defaultdict(list)
    for op,rec in enumerate(w['warps'],1):warps[rec[0]].append((op,rec))
    for i in range(len(w['B'])+1):
        for op,rec in warps[i]:
            if cur[rec[1]]!=basis(rec[3]):raise ValueError(('B-warp-input',op,rec[1]))
            cur[rec[1]]=basis(rec[4])
        if i<len(w['B']):step(w['B'][i],('B',i))
    for i,g in enumerate(w['restore']):step(g,('restore',i))
    for q in set(range(n))-set(w['removed']):climb(q,end[q])
    return dict(sorted(paid.items())),changes

def main():
    p=argparse.ArgumentParser();p.add_argument('--words',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out={'scope':'13 compensation-zero helpers with at most four A reads and no A writes; entry lines taken from first nonzero recipient frames. Exact frame propagation only; word identity/hosting/all-size obligations not certified.','orientations':{}}
    for kind in ['base','extra']:
        path=a.words/f'WORD-{kind}.json.gz';raw,w=read_word(path);base,changes=run(w,None,None)
        if base!={int(k):v for k,v in w['report']['local_profile'].items()} or changes:raise ValueError('positive control does not reproduce baseline')
        bad=copy.deepcopy(w);bad['center_frames'][0]=[]
        try:run(bad,None,None)
        except ValueError:pass
        else:raise ValueError('changed centre-interface control was accepted')
        bad=copy.deepcopy(w);bad['helper_final']['500']=[]
        try:run(bad,None,None)
        except ValueError:pass
        else:raise ValueError('changed endpoint control was accepted')
        C=collections.defaultdict(lambda:collections.defaultdict(F))
        for g in w['compensation']:C[g[2]][g[1]]+=F(g[3],g[4])
        excl=set(w['removed'])|set(map(int,w['start_extra']))|{g['source'] for g in w['initial_corrections']}
        rows=[]
        for r in range(224,704):
            use=[g for g in w['A'] if r in(g[1:3] if g[0]=='add' else g[1:2])]
            if r in excl or any(C[r].values()) or not 1<=len(use)<=4 or not all(g[0]=='add' and g[2]==r for g in use):continue
            lines=set()
            for target in {g[1] for g in use}:
                U=next((basis(g[-1]) for g in w['A'] if target in(g[1:3] if g[0]=='add' else g[1:2]) and g[-1]),())
                S={0}
                for u in U:S|={s^u for s in list(S)}
                lines|=S-{0}
            for line in sorted(lines):
                try:
                    H,edits=run(w,r,line)
                    delta={k:H.get(k,0)-base.get(k,0) for k in H.keys()|base.keys() if H.get(k,0)!=base.get(k,0)}
                    rows.append({'helper':r,'line':line,'status':'frame-feasible','delta':delta,'changed_gates':len(edits),'screen_local_moment_delta':sum(c*k**(1-0.001720100805416886) for k,c in delta.items())})
                except ValueError as e:rows.append({'helper':r,'line':line,'status':'rejected-retained-interface','failure':e.args[0]})
        out['orientations'][kind]={'source_sha256':hashlib.sha256(raw).hexdigest(),'baseline_profile':base,
            'controls':{'baseline_profile_exact':True,'centre_corruption_rejected':True,'endpoint_corruption_rejected':True},'cases':rows}
        print(kind,len(rows),'cases',collections.Counter(r['status'] for r in rows),flush=True)
    a.out.write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
