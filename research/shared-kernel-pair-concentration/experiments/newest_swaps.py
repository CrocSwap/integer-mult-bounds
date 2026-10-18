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
    package=a.package
    def read(name):
        p=package/name;b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
    prov=read('PROVIDERS.json');order=read('ORDER.json');fill=read('FILL.json.gz');dispatch={(s,r):p for s,r,p in read('DISPATCH.json')}
    widths={p:d['widths'] for p,d in prov.items()}
    rows=[list(x) for x in fill['rows']]
    w=[widths[dispatch[tuple(order[x[0]])]][x[1]] for x in rows]
    bins=lambda i:tuple(rows[i][2:5])
    template=read('sources/PR2833-T37-TEMPLATE.json.gz')
    rank={e['child']:e['rank'] for e in template['idle_children']}
    caps={(rep,ch):cap for rep in range(37) for ch,cap in rank.items()}
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
    out={'baseline_head':'0b2e2537b368a0cade07ce3f71452ea018ebe394','seed':a.seed,'passes':step+1,'pairs_screened':tested,'moves':moves,'scope':'Exhaustive same-call distinct-width pair census at each visited allocation. No infeasibility claim for multi-role paths, cycles, inter-call moves or new words.'}
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n')
    print('SWAPS',len(moves),flush=True)

if __name__=='__main__':main()
