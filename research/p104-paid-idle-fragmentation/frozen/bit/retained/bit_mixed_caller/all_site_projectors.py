#!/usr/bin/env python3
"""Export every binary rank2/3 projector admissible at each of seven sites."""
from pathlib import Path
import sys,json,time
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
from search_binary_root import *

def main():
    t=time.monotonic();R=[tuple((ALL^(1<<i))if j==i else 0 for j in range(N))for i in range(N)]+[(ALL,)*N];S=[];Q=(0,)*N
    for A in R:Q=add(Q,A);S.append(Q)
    sub={r:subspaces(r)for r in(2,3,4)};groups=[];counts={}
    for site in range(7):
        pp=[];counts[site]={}
        for r in(2,3):
            u=(1<<site)if site<6 else ALL;v=(ALL^(1<<site))if site<6 else ALL
            Us=[(B,sp)for B,sp in sub[r]if sp>>u&1 and any((v&w).bit_count()%2 for w in B)]
            Ws=[(B,sp)for B,sp in sub[N-r]if not any((v&w).bit_count()%2 for w in B)]
            ps=[]
            for U,su in Us:
                for W,sw in Ws:
                    if su&sw!=1:continue
                    P=projector(U,W)
                    if commute(P,S[site]):ps.append(P)
            ps=sorted(set(ps));pp.extend(ps);counts[site][r]=len(ps)
        if pp:groups.append(dict(site=site,projectors=pp))
    (H/'ALL-SITE-PROJECTORS.json').write_text(json.dumps(dict(groups=groups,counts=counts,seconds=time.monotonic()-t),separators=(',',':'))+'\n')
    lines=[str(len(groups))]
    for g in groups:
        lines.append(str(g['site'])+' '+str(len(g['projectors'])))
        lines.extend(' '.join(map(str,p))for p in g['projectors'])
    (H/'ALL-SITE-PROJECTORS.txt').write_text('\n'.join(lines)+'\n')
    print(counts,'seconds',time.monotonic()-t)

if __name__=='__main__':main()
