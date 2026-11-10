import json,gzip,collections,pathlib,sys,time,copy
from fractions import Fraction as Q
ROOT=pathlib.Path(__file__).resolve().parent/'build';P=1000000007

def add(a,b,q):
 for k,v in b.items():
  x=a.get(k,0)+q*v
  if x:a[k]=x
  else:a.pop(k,None)
def pure(rows,roles,group):
 piv={};out=[]
 for role in roles:
  outside={k:v for k,v in rows[role].items()if k not in group};inside={k:v for k,v in rows[role].items()if k in group};co={role:Q(1)}
  while outside:
   pivot=min(outside)
   if pivot not in piv:
    s=1/outside[pivot];piv[pivot]=[{k:v*s for k,v in z.items()}for z in(outside,inside,co)];break
   s=-outside[pivot]
   for a,b in zip((outside,inside,co),piv[pivot]):add(a,b,s)
  if not outside and inside:out.append((inside,co))
 return out

def exact_hit(w,cut,frame,pivot):
 n=w['public'];N=n+w['owned_fields'];group={r for r in range(n)if w['initial'][r]==3 and w['final'][r]==127};rows=[{r:Q(1)}if r<n else{}for r in range(N)];cur=w['initial']+[None]*w['owned_fields']
 for i,e in enumerate(w['program'][:cut+1]):
  op,r=e[:2]
  if op=='MOVE':cur[r]=e[3]
  elif op=='INIT':cur[r]=e[2];rows[r]={}
  elif op=='CLEAR':cur[r]=None;rows[r]={}
  elif op=='SCALE':rows[r]={k:v*Q(e[-2])for k,v in rows[r].items()}
  else:
   if op=='COPY':rows[r]={}
   add(rows[r],rows[e[2]],Q(e[-2]))
 roles=[r for r,f in enumerate(cur)if f==frame];pr=pure(rows,roles,group);rows=[{r:Q(1)}if r<n else{}for r in range(N)]
 for e in reversed(w['program'][cut+1:]):
  op,r=e[:2]
  if op in('INIT','CLEAR'):rows[r]={}
  elif op=='SCALE':rows[r]={k:v*Q(e[-2])for k,v in rows[r].items()}
  elif op in('ADD','COPY'):
   add(rows[e[2]],rows[r],Q(e[-2]))
   if op=='COPY':rows[r]={}
 su=pure(rows,roles,group)
 for c,a in pr:
  for d,b in su:
   cd=sum(v*d.get(k,0)for k,v in c.items())
   if not cd:continue
   b={k:v/cd for k,v in b.items()};d={k:v/cd for k,v in d.items()};ab=sum(v*b.get(k,0)for k,v in a.items())
   if ab==1 and pivot in roles:return a,b,c,d
 raise ValueError('no exact split')

def swap(p,j,f):return [['ADD',p,j,'1',f],['ADD',j,p,'-1',f],['ADD',p,j,'1',f],['SCALE',j,'-1',f]]
def basis(c,d,p,f):
 assert sum(v*d.get(k,0)for k,v in c.items())==1
 c=c.copy();d=d.copy();out=[]
 if not c.get(p):
  j=next(k for k,v in c.items()if abs(v)==1);out+=swap(p,j,f)
  c[p],c[j]=c.get(j,0),c.get(p,0);d[p],d[j]=d.get(j,0),d.get(p,0)
 q=c[p]
 if q!=1:out.append(['SCALE',p,str(q),f])
 for j,v in sorted(c.items()):
  if j!=p and v:out.append(['ADD',p,j,str(v),f])
 for j,v in sorted(d.items()):
  if j!=p and v:out.append(['ADD',j,p,str(-v),f])
 return out

def inverse(es):
 out=[]
 for e in reversed(es):
  z=e.copy();z[-2]=str(1/Q(z[-2])if z[0]=='SCALE'else-Q(z[-2]));out.append(z)
 return out

def build(w,cut,frame,pivot):
 a,b,c,d=exact_hit(w,cut,frame,pivot);print('EXACT_HIT',a,b,c,d,flush=True)
 assert all(r<w['public'] for r in set(a)|set(b)), 'Owned cut support requires index shift'
 B0=basis(c,d,pivot,w['initial'][pivot]);BF=basis(c,d,pivot,w['final'][pivot]);BC=basis(a,b,pivot,frame)
 n=w['public'];tail=n
 def transform(e,after=False):
  z=e.copy()
  def rr(r):return tail if after and r==pivot else r+(r>=n)
  z[1]=rr(z[1])
  if z[0]in('ADD','COPY'):z[2]=rr(z[2])
  return z
 prog=inverse(B0)+[transform(e)for e in w['program'][:cut+1]]+BC+[transform(e,True)for e in inverse(BC)]+[transform(e,True)for e in w['program'][cut+1:]]+[transform(e,True)for e in BF]
 z=copy.deepcopy(w);z['initial'].append(frame);z['final'].append(w['final'][pivot]);z['final'][pivot]=frame;z['public']+=1;z['program']=prog
 proof={'cut':cut,'frame':frame,'pivot':pivot,'a':a,'b':b,'c':c,'d':d,'B0':B0,'BF':BF,'BC':BC}
 return z,proof
if __name__=='__main__':
 path,cut,frame,piv,name=sys.argv[1:];w=json.load(gzip.open(path));z,p=build(w,int(cut),int(frame),int(piv))
 with gzip.open(ROOT/f'{name}.json.gz','wt')as f:json.dump(z,f,separators=(',',':'))
 (ROOT/f'{name}.proof.json').write_text(json.dumps(p,default=str,indent=2))
