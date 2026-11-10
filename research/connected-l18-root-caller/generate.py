import json,sys
from pathlib import Path
from fractions import Fraction as Q
sys.path.insert(0,str(Path(__file__).resolve().parent))
import matrix as v
if not __debug__:raise RuntimeError('Exact generator requires assertions')
def construct(g):
 assert g in (3,9,18)
 n=2*g+2;N=2*g+3;X=[];Y=[]
 for i in range(g):
  x=[Q(0)]*n;y=x[:];x[0]=1;x[1+i]=1;y[0]=1;y[1+i]=-1
  for j in range(i):x[1+j]=2
  X.append(x);Y.append(y)
 for a,ss,p,q in [(0,1,0,1),(-1,0,1,0),(-1,-1,1,-1)]:
  u=2-ss if g%2 else ss;x=[Q(0)]*n;y=x[:];x[0]=a;y[0]=u;x[-1]=q;y[-1]=p
  for i in range(g):x[1+i]=a+1;y[1+i]=(1-u)*(-1)**i
  for m in range(g):x[g+1+m]=1-a;y[g+1+m]=(u-1)*(-1)**(g-1-m)
  X.append(x);Y.append(y)
 for m in range(g):
  x=[Q(0)]*n;y=x[:];x[0]=-1;x[g+1+m]=1;y[0]=1;y[g+1+m]=1
  for j in range(m+1,g):x[g+1+j]=2
  X.append(x);Y.append(y)
 B=v.eye(n)
 for start in list(range(1,g+1,3))+list(range(g+1,2*g+1,3)):
  block=[[1,1,0],[1,1,1],[1,0,1]]
  for i in range(3):
   for j in range(3):B[start+i][start+j]=Q(block[i][j])
 Bi=v.inverse(B);X=[list(r) for r in zip(*v.mul(Bi,list(zip(*X))))];Y=v.mul(Y,B);stages=[]
 for u in range(1,g-1,2):
  e=u+1;end=3*((e+3)//3);stages.append(dict(units=[u,e],mask=[0]+list(range(1,1+end))))
 stages.append(dict(units=[g,g+1],mask=[0,n-1]+list(range(1,g+1,3))+list(range(g+1,2*g+1,3))))
 for m in range(0,g-1,2):
  start=3*(m//3);stages.append(dict(units=[g+3+m,g+4+m],mask=[0]+list(range(g+1+start,2*g+1))))
 pref=v.prefixes(X,Y,Q(-2));assert pref[-1]==v.scale(v.eye(n),Q(-1))
 assert all(v.dot(Y[i],X[j])==((i>j)-(i<j)) for i in range(N) for j in range(N))
 for st in stages:
  mask=set(st['mask']);assert all(not X[u][c] and not Y[u][c] for u in st['units'] for c in range(n) if c not in mask)
  for k in [min(st['units']),max(st['units'])+1]:assert all(not pref[k][i][j] for i in range(n) for j in range(n) if (i in mask)!=(j in mask))
 return dict(n=n,N=N,X=[[str(x) for x in r] for r in X],Y=[[str(x) for x in r] for r in Y],stages=stages)

def basis(candidates,n):
 cols=[]
 for c in candidates:
  if v.rank(list(map(list,zip(*(cols+[c])))))>len(cols):cols.append(c)
  if len(cols)==n:return list(map(list,zip(*cols)))
 raise ValueError('not a basis')
def synth(M):
 A=[r[:] for r in M];n=len(M);ops=[]
 for c in range(n):
  p=next(i for i in range(c,n) if A[i][c])
  if p!=c:A[p],A[c]=A[c],A[p];ops.append(['SWAP',p,c])
  q=A[c][c]
  if q!=1:A[c]=[x/q for x in A[c]];ops.append(['SCALE',c,str(1/q)])
  for i in range(n):
   if i!=c and A[i][c]:
    q=-A[i][c];A[i]=[x+q*y for x,y in zip(A[i],A[c])];ops.append(['ADD',i,c,str(q)])
 out=[]
 for op in reversed(ops):
  op=op[:]
  if op[0]=='SCALE':op[2]=str(1/Q(op[2]))
  if op[0]=='ADD':op[3]=str(-Q(op[3]))
  out.append(op)
 return out

def compile_root(R):
 n=R['n'];X=[[Q(x)for x in r]for r in R['X']];Y=[[Q(x)for x in r]for r in R['Y']];ST=R['stages'];events=[];skip=set();at={s['units'][0]:k for k,s in enumerate(ST)}
 for u in range(R['N']):
  if u in skip:continue
  if u in at:
   k=at[u];w=u+1;skip.add(w);mask=ST[k]['mask'];H=v.add(v.outer(X[u],Y[w]),v.outer(X[w],Y[u]),Q(-1));E=v.zero(n)
   for c in mask:E[c][c]=Q(1)
   residual=v.add(E,H,Q(-1));outside=[v.eye(n)[c]for c in range(n)if c not in mask]
   B=basis([X[u],X[w]]+list(map(list,zip(*residual)))+outside,n);Bi=v.inverse(B)
   assert v.mul(v.mul(Bi,E),B)==[[Q(i==j and i<len(mask))for j in range(n)]for i in range(n)]
   assert v.mul([Y[u],Y[w]],B)==[[Q(-1 if j==1 else 0)for j in range(n)],[Q(1 if j==0 else 0)for j in range(n)]]
   events+=synth(Bi)+[['ADD',0,1,'1'],['SCALE',1,'-1'],['LAMBDA',0,-1],['HOST',0,1,k,'1','-1'],['LAMBDA',0,1],['ADD',1,0,'1'],['SCALE',1,'-1']]
   events += [['IDLE_ONE',j,[k]]for j in range(2,len(mask))]
   events+=synth(B)
  else:
   a,b=X[u],Y[u];j=next(i for i,z in enumerate(b)if z);q=[Q(0)]*n;q[j]=1/b[j];K=v.add(v.eye(n),v.outer(q,b),Q(-1));B=basis([a,q]+list(map(list,zip(*K))),n)
   events+=synth(v.inverse(B))+[['ADD',0,1,'-1'],['LAMBDA',1,1],['QUERY',0,1,1],['LAMBDA',1,-1]]+synth(B)
 events += [['LAMBDA',r,-1]for r in range(n)]
 return dict(roles=n,stages=len(ST),masks=[sum(1<<k for k,s in enumerate(ST)if c in s['mask'])for c in range(n)],events=events,central_relation='Q^4=1; R=Lambda Q; R^2=1')

if __name__=='__main__':
 import argparse,hashlib
 parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args();here=Path(__file__).resolve().parent
 for pin in json.loads((here/'INPUT-PINS.json').read_text())['inputs']:
  assert hashlib.sha256((here/pin['local_path']).read_bytes()).hexdigest()==pin['sha256']
 from collections import Counter
 for name in ['tHHtHt','tHtHHt']:
  data=json.loads((here/f'inputs/root_L3_{name}.json').read_text())
  a,b,plus,parts,es=v.reconstruct(data,Q(1));_,_,minus,_,ems=v.reconstruct(data,Q(-1))
  assert minus[-1]==v.scale(plus[-1],Q(-1)) and es==ems
  dims={}
  for mask in range(8):
   J=v.eye(8)
   for k,E in enumerate(es):J=v.mul(J,E if mask>>k&1 else v.add(v.eye(8),E,Q(-1)))
   if v.rank(J):dims[mask]=v.rank(J)
  assert dims=={1:2,2:1,3:1,4:2,6:1,7:1}
 for g in [3,9,18]:
  root=construct(g);caller=compile_root(root)
  assert v.rank([[Q(x)for x in r]for r in root['X']])==root['n']
  assert v.rank([[Q(x)for x in r]for r in root['Y']])==root['n']
  for name,data in [(f'root_L{g}.json',root),(f'caller_L{g}.json',caller)]:
   if args.write:(here/name).write_text(json.dumps(data)+'\n')
   else:assert data==json.loads((here/name).read_text()),name
  if g==9:
   B=v.eye(20);block=[[1,1,0],[1,1,1],[1,0,1]]
   for start in list(range(1,10,3))+list(range(10,19,3)):
    for i in range(3):
     for j in range(3):B[start+i][start+j]=Q(block[i][j])
   XX=[[Q(x)for x in r]for r in root['X']]
   rawX=list(map(list,zip(*v.mul(B,list(zip(*XX))))))
   rawY=v.mul([[Q(x)for x in r]for r in root['Y']],v.inverse(B))
   retained=json.loads((here/'inputs/root_A.json').read_text())
   assert rawX==[[Q(x)for x in retained['X'][2*i][:20]]for i in range(21)]
   assert rawY==[[Q(x)for x in retained['Y'][2*i][:20]]for i in range(21)]
  print('PASS_ROOT_CALLER',g,len(caller['events']))
