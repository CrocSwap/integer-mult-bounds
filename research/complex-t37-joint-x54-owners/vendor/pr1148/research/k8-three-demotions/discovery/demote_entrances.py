"""Change local recursion interfaces: exhaustive codimension-one entrance choices."""
import argparse,json,gzip,copy,time,sys,os
from pathlib import Path
from collections import defaultdict
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
os.environ['K8_BASE_WORD']=str(ROOT/'research/k8-eight-ends/FULL-WORD.json.gz')
sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'))
import screen_end_groups as S
ap=argparse.ArgumentParser();ap.add_argument('--dimension',type=int,default=5);a=ap.parse_args()
groups=defaultdict(list)
for h,fr in S.w['start_extra'].items():
    if len(fr)==a.dimension:groups[tuple(fr)].append(int(h))
results=[]
for fr,hs in groups.items():
    k=len(fr);subspaces=set()
    for mask in range(1,1<<k):
        vectors=[]
        for c in range(1,1<<k):
            if (c&mask).bit_count()%2:continue
            v=0
            for i,x in enumerate(fr):
                if c>>i&1:v^=x
            vectors.append(v)
        subspaces.add(S.M.basis(vectors))
    for j,start in enumerate(sorted(subspaces)):
        t=time.monotonic();nw=copy.deepcopy(S.w)
        for h in hs:nw['start_extra'][str(h)]=list(start)
        try:
            nw=S.optimize(nw);r=dict(helpers=hs,subspace=j,start=list(start),status='FRAME_FEASIBLE_NOMINATION',profile=nw['report']['local_profile'],**S.screen(nw))
            path=P/f'demote{a.dimension}-{hs[0]}-{j}.json.gz';path.write_bytes(gzip.compress(json.dumps(nw,sort_keys=True,separators=(',',':')).encode(),mtime=0));r['word']=path.name
        except (AssertionError,RuntimeError,ValueError) as e:r=dict(helpers=hs,subspace=j,start=list(start),status='REJECTED',reason=str(e))
        r['seconds']=time.monotonic()-t;results.append(r);print(json.dumps(r),flush=True)
        (P/f'DEMOTION-{a.dimension}.json').write_text(json.dumps(results,indent=2)+'\n')
