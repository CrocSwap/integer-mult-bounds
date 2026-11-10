from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
import contextlib,io,hashlib
with contextlib.redirect_stdout(io.StringIO()):exec(open(HERE/'groups.py').read())
oldpairs=pairs;scalar=lambda x:Q(x).numerator*pow(Q(x).denominator,-1,MOD)%MOD
iv=[];exports_at=defaultdict(list);byframe=defaultdict(list)
for a,b in oldpairs:
 if a['second']>=b['first']:continue
 r=a['role'];i=a['first'];j=b['second'];lo=a['lo'];hi=b['hi'];middle=[z for z in reads[r]if a['second']<z<b['first']]
 if not middle:raise ValueError('Missing retained middle reads')
 c=dict(role=r,first=i,second=j,A=a['E'],C=a['G'],E=b['G'],lo=lo,hi=hi,l1=max([lo]+[z+1 for z in reads[r]if lo<=z<i]),h1=min(middle),l2=max(middle)+1,h2=min([hi]+[z for z in reads[r]if j<z<hi]),exports=a['exports']+b['exports'],target={},nodes=[],ranks_before=a['paid_ranks_before']+b['paid_ranks_before'],ranks_after=[sum(a['paid_ranks_before']),sum(b['paid_ranks_before'])])
 idx=len(iv);iv.append(c)
 for kind,fr,left,right in [('A',c['A'],lo,c['h1']),('C',c['C'],c['l1'],c['h2']),('E',c['E'],c['l2'],hi)]:byframe[fr].append((idx,kind,left,right))
 for z in c['exports']:
  q=scalar(p[z][3])
  for si,se in writes[r]:
   if i<si<z and se[0]=='SCALE':q=q*scalar(se[2])%MOD
  exports_at[z].append((idx,q))
def axpy(a,b,q):
 for k,v in b.items():
  z=(a.get(k,0)+q*v)%MOD
  if z:a[k]=z
  else:a.pop(k,None)
full={r for r,f in enumerate(w['final'])if f==127};cols=[{r:1}if r<n and r not in full else{}for r in range(N)];frames=w['final']+[None]*w['owned_fields'];ends=[len(p)]*N

def save(r,left,right):
 if left>right or frames[r]is None or not cols[r]:return
 for idx,kind,a,b in byframe[frames[r]]:
  c=iv[idx];lo,hi=max(left,a),min(right,b)
  if lo<=hi and r!=c['role']:c['nodes'].append((lo,hi,r,cols[r].copy(),kind))
monitor=n
for i in range(len(p)-1,-1,-1):
 e=p[i];op,r=e[:2];affected={r}
 if op in ('ADD','COPY'):affected.add(e[2])
 for z in affected:save(z,i+1,ends[z]);ends[z]=i
 for idx,q in exports_at[i]:axpy(iv[idx]['target'],cols[r],q)
 if op=='MOVE':frames[r]=e[2]
 elif op=='SCALE':cols[r]={k:v*scalar(e[2])%MOD for k,v in cols[r].items()}
 elif op in ('ADD','COPY'):
  axpy(cols[e[2]],cols[r],scalar(e[3]))
  if op=='COPY':cols[r][monitor]=1;monitor+=1
 elif op in ('INIT','CLEAR'):cols[r]={};frames[r]=None if op=='INIT' else e[2]
for r in range(N):save(r,0,ends[r])
exec(s[s.index('def solve('):s.index('hits=[];stats=Counter()')])
st=Counter();hits=[]
for c in iv:
 ts1={c['l1'],c['h1']};ts2={c['l2'],c['h2']}
 for lo,hi,r,v,kind in c['nodes']:
  if kind=='A':ts1.add(lo)
  elif kind=='E':ts2.add(hi)
  else:ts1.add(hi);ts2.add(lo)
 ts1=sorted(t for t in ts1 if c['l1']<=t<=c['h1']);ts2=sorted(t for t in ts2 if c['l2']<=t<=c['h2'])
 for t1 in ts1:
  for t2 in ts2:
   use=[];seen=set()
   for lo,hi,r,v,kind in c['nodes']:
    cut=lo if kind=='A' else hi if kind=='E' else max(lo,t1)
    valid=lo<=t1 if kind=='A' else hi>=t2 if kind=='E' else lo<=t2 and hi>=t1
    key=tuple(sorted(v.items()))
    if valid and key not in seen:seen.add(key);use.append((cut,r,v,kind))
   sol,rank=solve(use,c['target']);st['systems']+=1;st['maxrank']=max(st['maxrank'],rank)
   if sol is not None:
    hit={k:v for k,v in c.items()if k not in ('nodes','target')};hit.update(t1=t1,t2=t2,injections=[(use[k][0],use[k][1],use[k][3],q)for k,q in sol.items()]);hits.append(hit);print('HIT',hit,flush=True)
print('DONE',len(iv),dict(st),'hits',len(hits),flush=True)
Path(sys.argv[1]).write_text(json.dumps(dict(interval_pairs=len(iv),stats=st,hits=hits),indent=2)+'\n')
