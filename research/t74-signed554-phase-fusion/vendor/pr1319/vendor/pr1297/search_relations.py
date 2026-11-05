"""Exact rational two-shock relations, retaining suffix effects on every register."""
import argparse,gzip,json,collections,sys,time
from fractions import Fraction as Q
from pathlib import Path
P=Path(__file__).resolve().parent;F=P.parent
ap=argparse.ArgumentParser();ap.add_argument('--word',type=Path,default=P/'inputs/base.json.gz');ap.add_argument('--pivots',nargs='+',type=int,default=[555,567]);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
w=json.loads(gzip.decompress(args.word.read_bytes()));B=w['B'];R=max(max(g[1:3]) if g[0]=='add' else g[1] for g in B)+1
coef=lambda g:Q(g[3],g[4]) if g[0]=='add' else Q(g[2],g[3])
def add(a,b,c):
 d=dict(a)
 for k,v in b.items():
  d[k]=d.get(k,Q(0))+c*v
  if not d[k]:del d[k]
 return d
def col(seq,q):
 r={q:Q(1)}
 for g in seq:
  t=g[1]
  if g[0]=='add':r[t]=r.get(t,Q(0))+coef(g)*r.get(g[2],Q(0))
  else:r[t]=r.get(t,Q(0))*coef(g)
  if not r[t]:r.pop(t,None)
 return r
def solve(u,v,d):
 keys=set(u)|set(v)|set(d)
 if not keys:return None
 i=next(iter(keys));ui,vi,di=u.get(i,0),v.get(i,0),d.get(i,0)
 for j in keys:
  uj,vj,dj=u.get(j,0),v.get(j,0),d.get(j,0);det=ui*vj-uj*vi
  if det:
   a=(di*vj-dj*vi)/det;b=(ui*dj-uj*di)/det
   if not a or not b:return None
   a,b=Q(a),Q(b)
   if any(c.denominator&(c.denominator-1) for c in [a,b]):return None
   if all(a*u.get(k,0)+b*v.get(k,0)==d.get(k,0) for k in keys):return a,b
   return None
 return None
out=[]
for q in args.pivots:
 first=next(i for i,g in enumerate(B) if g[1]==q);dele=[i for i,g in enumerate(B[:first]) if g[0]=='add' and g[2]==q];tail=[w['cleanup'][i] for i,U in w['early_cleanup']];seq=B+tail;new=[g for i,g in enumerate(B) if i not in dele]+tail;d=add(col(seq,q),col(new,q),-1)
 cols={j:{j:Q(1)} for j in range(R)};hs=[];ts=[]
 for i in range(len(seq)-1,-1,-1):
  g=seq[i]
  if i<first and g[0]=='add' and 112<=g[1]<224 and g[2]>=224 and g[2]!=q and i not in dele:
   h=g[2];effect=add(cols[h],{h:Q(1)},-1)
   if effect:hs.append((i+1,h,effect))
   ts.append((i,g,dict(cols[g[1]])))
  if i in dele:continue
  if g[0]=='add':t,s=g[1:3];cols[s]=add(cols[s],cols[t],coef(g))
  else:cols[g[1]]={k:v*coef(g) for k,v in cols[g[1]].items()}
 start=time.monotonic();matches=[]
 for cut,h,u in hs:
  for i,g,v in ts:
   if h==g[2]:continue
   sol=solve(u,v,d)
   if sol:
    a,b=sol;c=b/coef(g)
    if c.denominator&(c.denominator-1):continue
    ed=dict(delete=dele,insert=[[i,['add',g[2],q,c.numerator,c.denominator,[]]],[i+1,['add',g[2],q,-c.numerator,c.denominator,[]]],[cut,['add',h,q,a.numerator,a.denominator,[]]]],tail=[[len(w['early_cleanup']),['add',h,q,-a.numerator,a.denominator,[]]]],prepend=[])
    matches.append(dict(pivot=q,helper=h,cut=cut,output=g[1],hook=i,donor=g[2],amount=str(a),correction=str(b),ed=ed))
 print('PIVOT',q,'pairs',len(hs)*len(ts),'matches',len(matches),'seconds',time.monotonic()-start,flush=True);print(matches[:3],flush=True);out+=matches
args.out.write_text(json.dumps(out,indent=2)+'\n')
