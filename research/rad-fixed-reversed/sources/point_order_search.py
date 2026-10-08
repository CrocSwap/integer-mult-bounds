#!/usr/bin/env python3
"""Distinct common-dependent global pair ordering and tree co-design."""
import argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
from producer_search import digest,initialize,worker


def evaluate(c):
    import partial_swap.graph as graph
    def points(h,common):
        pairs=[(a,a+1) for a in range(0,h-1,2) if common not in (a,a+1)]
        policy=c['point_policy']
        if policy=='common-rotate':
            k=common%len(pairs);pairs=pairs[k:]+pairs[:k]
        elif policy=='paired-rotate':
            k=(common//2)%len(pairs);pairs=pairs[k:]+pairs[:k]
        elif policy=='alternating-reverse':
            if common%2:pairs.reverse()
        elif policy=='xor-pairs':
            pairs.sort(key=lambda pair:(pair[0]//2)^(common//2))
        head=[x for pair in pairs for x in pair]
        tail=[x for x in range(h) if x!=common and x not in head]
        if policy=='tail-first':return tail+head
        return head+tail
    graph.aligned_points=points
    return worker(c)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=8)
    a=p.parse_args();assert not a.output.exists()
    (a.work/'builds').mkdir(parents=True,exist_ok=True)
    native=Path(__file__).with_name('moment_match_positive.cpp')
    subprocess.run(['c++','-O3','-std=c++17',str(native),'-o',str(a.work/'builds'/'moment_match_positive')],check=True)
    subprocess.run(['c++','-O3','-std=c++17',str(a.source/'scripts/partial_swap/match_exported_dag.cpp'),
                    '-o',str(a.work/'builds'/'match_exported_dag')],check=True)
    configurations=[]
    for h in (21,23,25,27):
        for tree in ('left','support-right','seeded-left'):
            for j,policy in enumerate(('common-rotate','paired-rotate','alternating-reverse','xor-pairs','tail-first')):
                configurations.append(dict(h=h,threshold=2,grouping='pairs',tree=tree,mode=2,
                                           seed=2750159+104729*j,point_policy=policy))
    result=dict(status='running',command=sys.argv,started_utc=datetime.now(timezone.utc).isoformat(),
                source_revision='11817ccacb564bb7f98789c20dc11d3fece207e3',workers=a.workers,
                source_sha256={p.name:digest(p) for p in (Path(__file__),native,Path(__file__).with_name('producer_search.py'))},
                configurations=configurations,rows=[])
    with ProcessPoolExecutor(max_workers=a.workers,initializer=initialize,
                             initargs=(a.source,a.work,a.work/'builds'/'moment_match_positive')) as pool:
        futures=[pool.submit(evaluate,c)for c in configurations]
        for f in as_completed(futures):
            row=f.result();result['rows'].append(row)
            a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
            print(json.dumps({k:row.get(k)for k in ('case_id','status','R','matched','seconds','pid')}),flush=True)
    result.update(status='complete',completed_utc=datetime.now(timezone.utc).isoformat())
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
