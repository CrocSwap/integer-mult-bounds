"""New nomination only: correct per-width bank padding and exact-exponent objective.
Uses PR484 frozen word. No scalar or all-size admission is implied.
Prepared by OpenAI Codex; reuses PR484 pattern enumerator with attribution.
"""
from pathlib import Path
import sys,json,gzip,math,importlib.util
from collections import Counter
import numpy as np
from scipy.optimize import milp,LinearConstraint,Bounds
from scipy.sparse import lil_matrix
ROOT=Path(__file__).resolve().parents[1]/'vendor/complex/e8-complex-gauge-kernel'
sys.path.insert(0,str(ROOT/'code'))
import onehost_gk as OH
OUT=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=False)
PROOF=Path(sys.argv[1]).resolve()
t=json.load(gzip.open(PROOF/'hosted/GLOBAL-TEMPLATE.json.gz'))
c=json.load(gzip.open(PROOF/'split-centres/CANONICAL-WORD.json.gz'))
widths=[9-len(c['frames'][c['start'][240+i]]) for i in range(c['R'])]
WID=Counter(widths); avail={(s,w):n for s in range(9) for w,n in WID.items()}
win={int(i):(p,r,st) for i,(p,r,st) in t['hosting']['windows'].items()}
var=[(i,pat) for i,(p,r,st) in sorted(win.items()) for pat in OH.patterns(r,sorted(st),sorted(WID))]
ids=sorted(win); aws=sorted(avail); n=len(var)
A=lil_matrix((len(ids)+len(aws),n)); idx={i:j for j,i in enumerate(ids)}; ai={sw:len(ids)+j for j,sw in enumerate(aws)}
for j,(i,pat) in enumerate(var):
 A[idx[i],j]=1
 for sw in pat:A[ai[sw],j]=1
A=A.tocsr(); lo=np.r_[np.full(len(ids),120),np.zeros(len(aws))]; hi=np.r_[np.full(len(ids),120),np.array([avail[x] for x in aws])]
print('variables',n,'windows',len(win),'widths',WID,flush=True)
oldsel=json.load(open(ROOT/'data/SELECTION.json'))['complex-gauge80-kernel42']['patterns']
local=json.load(open(PROOF/'split-centres/LOCAL-CHECKS.json'))

def profile(sel):
 H=Counter(); used=Counter();rem=[]
 for call in t['calls']:
  H.update({int(r):z for r,z in local[call['orientation']]['paid_profile'].items()})
 for i,pat,n in sel:
  left=win[i][1]-sum(w for s,w in pat)
  if left:H[left]+=8*n
  used.update({(s,w):n for s,w in pat})
 banks=0; rest={}
 for sw,a in avail.items():
  z=a-used[sw]; assert z>=0
  if z:rest[str(sw)]=z; banks+=z;H[73-8*sw[1]]+=z
 # original excluded windows are untouched, from parent template
 parent=json.load(gzip.open(PROOF/'split-centres/GLOBAL-TEMPLATE.json.gz'))
 for it in parent['idle_children']:
  if it['child'] not in win:H[it['rank']]+=it['replicas']
 live=7680+banks;assert 73*live-sum(r*n for r,n in H.items())==2496
 return dict(histogram=dict(sorted(H.items())),live=live,banks=banks,unhosted_per_replica=rest,deficit=2496)
assert profile(oldsel)['histogram']=={int(r):n for r,n in json.load(open(PROOF/'hosted/HOSTED.json'))['global_profile'].items()}
for label,b in [('entropy',0),('at484',.001326789535340266)]:
 def cost(r):return r*math.expm1(b*math.log(73/r))/b if r and b else r*math.log(73/r) if r else 0
 def objective(i,pat):return cost(win[i][1])-cost(win[i][1]-sum(w for s,w in pat))+sum(cost(73-8*w)/8 for s,w in pat)
 obj=np.array([-objective(i,pat) for i,pat in var])
 res=milp(obj,integrality=np.ones(n),bounds=Bounds(0,np.inf),constraints=LinearConstraint(A,lo,hi),options={'time_limit':90,'mip_rel_gap':1e-10})
 assert res.x is not None,res
 x=np.rint(res.x).astype(int);assert abs(A@x-hi)[:len(ids)].max()==0 and np.all(A@x<=hi) and np.all(x>=0)
 sel=[[i,[list(z) for z in pat],int(x[j])] for j,(i,pat) in enumerate(var) if x[j]]
 result=profile(sel)|dict(status='NOMINATION_ONLY',scipy_status=int(res.status),message=res.message,mip_gap=float(res.mip_gap),objective=-float(res.fun),old_objective=sum(n*objective(i,pat) for i,pat,n in oldsel),b=b,patterns=sel)
 (OUT/f'{label}.json').write_text(json.dumps(result,indent=2)+'\n')
 (OUT/f'SELECTION-{label}.json').write_text(json.dumps({'complex-gauge80-kernel42':dict(rule='one-helper-per-family',patterns=sorted(sel),proxy_saving=-float(res.fun))},indent=1,sort_keys=True)+'\n')
 print(label,{k:v for k,v in result.items() if k not in ['patterns','histogram']},flush=True)
