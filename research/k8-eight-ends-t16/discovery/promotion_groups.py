import os,json,gzip,copy,importlib.util,sys
from pathlib import Path
from collections import defaultdict
P=Path(__file__).resolve().parent;ROOT=P.parents[2];os.environ['K8_BASE_WORD']=str(ROOT/'research/k8-eight-ends/FULL-WORD.json.gz');sys.path.insert(0,str(ROOT/'research/k8-eight-ends/discovery'));import screen_end_groups as S
m=S.M.Model(S.w);groups=defaultdict(list)
for q,start in S.w['start_extra'].items():
 q=int(q);first=m.chains[q][1];hi=m.hi[first]
 if len(hi)>len(start):groups[(tuple(start),hi)].append(q)
G=[dict(helpers=hs,old=list(old),new=list(new)) for (old,new),hs in groups.items()];(P/'PROMOTION-GROUPS.json').write_text(json.dumps(G,indent=2)+'\n');print('groups',len(G),[dict(helpers=g['helpers'],dim=(len(g['old']),len(g['new']))) for g in G],flush=True)
results=[]
for i,g in enumerate(G):
 nw=copy.deepcopy(S.w)
 for q in g['helpers']:nw['start_extra'][str(q)]=g['new']
 try:
  nw=S.optimize(nw);r=dict(group=i,helpers=g['helpers'],profile=nw['report']['local_profile'],**S.screen(nw));(P/f'promotion-{i}.json.gz').write_bytes(gzip.compress(json.dumps(nw,sort_keys=True,separators=(',',':')).encode(),mtime=0))
 except AssertionError as e:r=dict(group=i,helpers=g['helpers'],status='INFEASIBLE',reason=str(e))
 results.append(r);print(json.dumps(r),flush=True);(P/'PROMOTION-SCREEN.json').write_text(json.dumps(results,indent=2)+'\n')
