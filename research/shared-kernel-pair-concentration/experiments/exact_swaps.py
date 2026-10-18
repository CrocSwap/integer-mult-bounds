#!/usr/bin/env python3
"""All-width same-call swaps using exact concavity dominance, seed fixed.

Reuses the source-bound window/inventory reader and literal fill checker from
Philippe Van Velzen/Jeremy Kothe's credited package. Unlike swapfill.py this
screens every pair of distinct widths and uses no floating-point comparison.
OpenAI Codex assistance. Apache-2.0.
"""
import argparse, collections, gzip, json, os, random, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser();ap.add_argument('package',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--passes',type=int,default=4);ap.add_argument('--seed',type=int,default=20261016);a=ap.parse_args()
    os.environ['FILLPKG']=str(a.package.resolve())
    sys.path.insert(0,str(a.package.resolve()/'new/borrow-fill/search'))
    import fillbase as f
    widths={p:d['widths'] for p,d in f.prov.items()}
    paid={p:{int(k):v for k,v in d['actual_paid_profile'].items()} for p,d in f.prov.items()}
    rows=[list(x) for x in f.fill['rows']]
    original_idle,original_profile=f.check(rows,widths,paid)
    w=[widths[f.dispatch[tuple(f.order[x[0]])]][x[1]] for x in rows]
    bins=lambda i:tuple(rows[i][2:5])
    caps={(int(k.split(',')[0]),int(k.split(',')[1])):v[0] for k,v in f.windows.items()}
    used=collections.Counter();calls=collections.defaultdict(list)
    for i,row in enumerate(rows):used[bins(i)]+=w[i];calls[row[0]].append(i)
    rng=random.Random(a.seed);moves=[];tested=0
    for step in range(a.passes):
        count=0;times=list(calls);rng.shuffle(times)
        for t in times:
            ids=sorted(calls[t],key=lambda i:(w[i],i))
            for ix,i in enumerate(ids):
                for j in ids[ix+1:]:
                    d=w[j]-w[i]
                    if not d:continue
                    bi,bj=bins(i),bins(j)
                    if bi==bj:continue
                    x,y=caps[bi[:2]]-used[bi],caps[bj[:2]]-used[bj]
                    tested+=1
                    if x<d:continue
                    # For 0<a<1, concavity gives strict saving iff the
                    # nonnegative residual pair with equal sum is more spread.
                    if max(x-d,y+d)<=max(x,y):continue
                    rows[i][2:5],rows[j][2:5]=list(bj),list(bi)
                    used[bi]+=d;used[bj]-=d
                    moves.append({'call':t,'roles':[rows[i][1],rows[j][1]],'widths':[w[i],w[j]],'before':[x,y],'after':[x-d,y+d]})
                    count+=1
        print('pass',step,'exactly_dominating_swaps',count,'tested',tested,flush=True)
        if not count:break
    rows=f.compact(rows,lambda row:widths[f.dispatch[tuple(f.order[row[0]])]][row[1]])
    idle,profile=f.check(rows,widths,paid)
    out={'seed':a.seed,'passes':step+1,'pairs_screened':tested,'moves':moves,'idle_before':dict(sorted(original_idle.items())),'idle_after':dict(sorted(idle.items())),'profile_before':dict(sorted(original_profile.items())),'profile_after':dict(sorted(profile.items())),'claim':'strict moment improvement for all 0<a<1 if and only if at least one recorded move; no final kappa certification'}
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
    (a.out/'FILL.json.gz').write_bytes(gzip.compress(json.dumps(dict(columns=f.fill['columns'],dispatch_overrides=f.fill['dispatch_overrides'],rows=rows),separators=(',',':')).encode(),mtime=0))
    print('SWAPS',len(moves),flush=True)

if __name__=='__main__':main()
