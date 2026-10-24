#!/usr/bin/env python3
"""Independent exact nine-axis Pauli and integer-Gaussian phase audit.

No candidate or predecessor evaluator imports. Equality of conjugation on all
Pauli generators fixes an operator up to scalar; equality on |0> fixes that
scalar. Primitive formulas are derived directly from affine monomial entries
and C_q=((1+i)I+(1-i)X_q)/2. All arithmetic is binary/integer.
"""
from pathlib import Path
from functools import lru_cache
import gzip,hashlib,json,time
N=9;SIZE=1<<N;MASK=SIZE-1
HERE=Path(__file__).resolve().parent;WORKSPACE=HERE.parents[2]
PKG=HERE.parent/'source-capsule/research/native-transpose-owned'
OLD=WORKSPACE/'outputs/price-plane-swarm-20261024/09-capsule-cold/capsule-v1/snapshot/research/kappa-joint-relations-20261023/WORD.json.gz'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def parity(x):return x.bit_count()&1
def mv(a,x):return sum(parity(r&x)<<i for i,r in enumerate(a))
def transpose(a,n=N):return tuple(sum(((a[j]>>i)&1)<<j for j in range(n)) for i in range(n))
def inverse(a):
 out=[r|1<<(N+i) for i,r in enumerate(a)]
 for j in range(N):
  hit=next((i for i in range(j,N) if out[i]>>j&1),None);need(hit is not None,'invertible binary map')
  out[j],out[hit]=out[hit],out[j]
  for i in range(N):
   if i!=j and out[i]>>j&1:out[i]^=out[j]
 need([r&MASK for r in out]==[1<<i for i in range(N)],'inverse reduced identity')
 return tuple(r>>N for r in out)
def rank(a):
 piv={}
 for x in a:
  while x:
   k=x.bit_length()-1
   if k not in piv:piv[k]=x;break
   x^=piv[k]
 return len(piv)
ID=tuple((1<<i,0,0) for i in range(N))+tuple((0,1<<i,0) for i in range(N))
def pmul(a,b):return a[0]^b[0],a[1]^b[1],(a[2]+b[2]+2*parity(a[1]&b[0]))%4
def papply(tab,p):
 out=(0,0,p[2])
 for i in range(N):
  if p[0]>>i&1:out=pmul(out,tab[i])
 for i in range(N):
  if p[1]>>i&1:out=pmul(out,tab[N+i])
 return out
def compose(after,before):return tuple(papply(after,p) for p in before)
def mono(rows=None,offset=0,phase=0,alpha=None,q=None):
 rows=tuple(rows) if rows is not None else tuple(1<<i for i in range(N))
 return rows,offset,phase%4,tuple(alpha) if alpha is not None else (0,)*N,tuple(q) if q is not None else (0,)*N
def parse(r):
 m=mono(r['matrix_rows'],r['offset'],r['phase'],r['linear_Z4'],r['quadratic_rows'])
 rows,t,c,a,q=m;need(len(rows)==len(a)==len(q)==N and 0<=t<SIZE,'monomial dimensions')
 need(all(0<=v<4 for v in a) and all(0<=v<SIZE for v in rows+q),'monomial range')
 need(q==transpose(q) and all(a[i]%2==(q[i]>>i&1) for i in range(N)),'quadratic phase parity/symmetry')
 inverse(rows);return m
def exponent(m,x):
 rows,t,c,a,q=m;out=c
 for i in range(N):
  if x>>i&1:out+=a[i]+2*parity((q[i]>>(i+1))&(x>>(i+1)))
 return out%4
@lru_cache(None)
def mono_tables(m):
 rows,t,c,a,q=m;ir=inverse(rows);it=transpose(ir);cols=transpose(rows)
 # Phase derivative p(x+e_i)-p(x)=a_i+2(q_i dot x).
 xs=[];zs=[]
 for i in range(N):
  z=mv(it,q[i]);xs.append((cols[i],z,(a[i]+2*parity(z&t))%4))
  z=ir[i];zs.append((0,z,2*parity(z&t)))
 return tuple(xs+zs)
@lru_cache(None)
def mono_address(m):
 rows,t,c,a,q=m
 return tuple(mv(rows,x)^t for x in range(SIZE)),tuple(exponent(m,x) for x in range(SIZE))
def conjugate(m):
 rows,t,c,a,q=m;return mono(rows,t,-c,[-v%4 for v in a],q)
def pull_phase(m,rows,t,sign=1):
 # Exact unique degree-two phase reconstruction after inverse-affine input.
 cols=transpose(rows);c=sign*exponent(m,t)%4
 a=[(sign*exponent(m,t^v)-c)%4 for v in cols];q=[(a[i]%2)<<i for i in range(N)]
 for i in range(N):
  for j in range(i+1,N):
   v=(sign*exponent(m,t^cols[i]^cols[j])-c-a[i]-a[j])%4;need(v%2==0,'quadratic phase reconstruction')
   if v:q[i]|=1<<j;q[j]|=1<<i
 return c,a,q
def monoinv(m):
 rows,t,c,a,q=m;ir=inverse(rows);nt=mv(ir,t);c,a,q=pull_phase(m,ir,nt,-1);return mono(ir,nt,c,a,q)
def monotrans(m):
 rows,t,c,a,q=m;ir=inverse(rows);nt=mv(ir,t);c,a,q=pull_phase(m,ir,nt,1);return mono(ir,nt,c,a,q)
@lru_cache(None)
def ctable(q,sgn=1):
 need(0<q<SIZE and sgn in (-1,1),'Gaussian primitive domain')
 return ID[:N]+tuple((q if q>>i&1 else 0,1<<i,(3*sgn)%4 if q>>i&1 else 0) for i in range(N))
def adjoint(circuit):return tuple(('C',e[1],-e[2]) if e[0]=='C' else ('M',monoinv(e[1])) for e in reversed(circuit))
def ctr(circuit):
 # (conjugate U)^T=U^dagger, derived primitive-wise.
 return adjoint(circuit)
@lru_cache(None)
def circuit_table(circuit):
 t=ID
 for e in circuit:t=compose(ctable(e[1],e[2]) if e[0]=='C' else mono_tables(e[1]),t)
 return t
@lru_cache(None)
def standard(r):return tuple(('C',1<<i,1) for i in range(r))
FRAMES=None
@lru_cache(None)
def frame(index):
 U=tuple(FRAMES[index]);r=len(U);need(rank(U)==r,'frame independent ordered basis')
 if r==0:return ()
 if r==N:return standard(N)
 basis=[]
 for x in U+tuple(1<<i for i in range(N)):
  if rank(basis+[x])>len(basis):basis.append(x)
 need(len(basis)==N,'deterministic binary frame extension')
 G=transpose(basis);gi=inverse(G);cols=transpose(gi)
 q=tuple((1<<i)^sum(parity(a&b)<<j for j,b in enumerate(cols)) for i,a in enumerate(cols))
 K=(('M',mono(G)),('M',mono(q=q,alpha=[(q[i]>>i)&1 for i in range(N)])))
 return adjoint(K)+standard(r)+K

def state(circuit,basis=0):
 re=[0]*SIZE;im=[0]*SIZE;re[basis]=1;den=0
 for e in circuit:
  if e[0]=='M':
   images,phases=mono_address(e[1]);nr=[0]*SIZE;ni=[0]*SIZE
   for x,y in enumerate(images):
    a,b=re[x],im[x];p=phases[x]
    if p==0:nr[y],ni[y]=a,b
    elif p==1:nr[y],ni[y]=-b,a
    elif p==2:nr[y],ni[y]=-a,-b
    else:nr[y],ni[y]=b,-a
   re,im=nr,ni
  else:
   _,q,sgn=e;nr=[0]*SIZE;ni=[0]*SIZE
   for x,(a,b) in enumerate(zip(re,im)):
    c,d=re[x^q],im[x^q]
    nr[x]=a-sgn*b+c+sgn*d;ni[x]=b+sgn*a+d-sgn*c
   re,im=nr,ni;den+=1
 while den and all(v%2==0 for v in re+im):
  re=[v//2 for v in re];im=[v//2 for v in im];den-=1
 return tuple(re),tuple(im),den

def same(a,b,msg):
 need(circuit_table(a)==circuit_table(b),msg+' Pauli conjugation')
 need(state(a)==state(b),msg+' absolute scalar anchor')

def extract_mono(circuit):
 tab=circuit_table(circuit);need(all(x==0 and p%2==0 for x,z,p in tab[N:]),'native operator monomial')
 G=transpose(tuple(x for x,z,p in tab[:N]));b=mv(G,sum((p//2)<<i for i,(x,z,p) in enumerate(tab[N:])))
 gt=transpose(G);cols=[mv(gt,z) for x,z,p in tab[:N]];q=transpose(cols);a=[(p-2*parity(b&z))%4 for x,z,p in tab[:N]]
 re,im,den=state(circuit);need(den==0 and all(re[x]==im[x]==0 for x in range(SIZE) if x!=b),'monomial state anchor')
 phase={(1,0):0,(0,1):1,(-1,0):2,(0,-1):3}.get((re[b],im[b]));need(phase is not None,'unit Gaussian monomial phase')
 m=mono(G,b,phase,a,q);need(mono_tables(m)==tab,'extracted exact monomial tableau');return m

def main():
 global FRAMES
 start=time.monotonic();source=read(OLD);c=source['canonical'];FRAMES=c['frames'];program=source['programs']['backward'];rows=read(PKG/'PHASES.json.gz')
 expected=sorted({(e[3],e[4],e[5]) for e in program if e[0]=='climb'}|{(e[2],e[3],e[4]) for e in program if e[0]=='center'})
 need([(r['old'],r['new'],r['rank']) for r in rows]==expected,'all actual transposed paid classes exactly once')
 for i,r in enumerate(rows):
  # Source backward physical child is conjugate(F_b F_a^dagger),
  # hence its bilinear transpose is F_a F_b^dagger exactly.
  want=adjoint(frame(r['new']))+frame(r['old'])
  got=(('M',parse(r['right'])),)+standard(r['rank'])+(('M',parse(r['left'])),)
  same(got,want,'paid class '+str((r['old'],r['new'],r['rank'])))
  if i%250==0:print('PAID',i+1,len(rows),flush=True)
 warpmap={}
 for w in c['warps']:
  G=transpose(w['G_columns']);gi=inverse(G);cols=transpose(gi)
  q=tuple((1<<i)^sum(parity(a&b)<<j for j,b in enumerate(cols)) for i,a in enumerate(cols))
  warpmap[w['op']]=(('M',mono(G)),('M',mono(q=q,alpha=[(q[i]>>i)&1 for i in range(N)])))
 warps=sorted({(e[2],e[3],e[4]) for e in program if e[0]=='warp'});columns=0
 for op,a,b in warps:
  K=warpmap[abs(op)];K=K if op>0 else adjoint(K)
  # Full source normalized backward native is conjugate(F_b K F_a†).
  # Its transpose is F_a K† F_b†, exactly the signed-inverse raw warp
  # and swapped frame pair emitted by the independent literal checker.
  raw=adjoint(frame(a))+K+frame(b)
  old=tuple(('C',e[1],-e[2]) if e[0]=='C' else ('M',conjugate(e[1])) for e in raw)
  want=adjoint(frame(b))+adjoint(K)+frame(a)
  om=extract_mono(old);nm=extract_mono(want);tm=monotrans(om)
  need(nm==tm,'actual native transpose recipe exact')
  oi,ophas=mono_address(om);ni,nphas=mono_address(nm)
  for x,y in enumerate(oi):need(ni[y]==x and nphas[y]==ophas[x],'literal native transpose matrix entry');columns+=1
 for q in c['ports']:
  same((('C',q,1),('C',q,1)),(('M',mono(offset=q)),),'actual Q squared translation')
  need(ctable(q,1)==circuit_table((('C',q,1),)),'symmetric Gaussian primitive')
 for r in (4,7,8,9):
  C=standard(r);fixed=adjoint(C)+(('M',mono(offset=(1<<r)-1)),)
  same(C,fixed,'helper conjugate Gaussian orientation correction')
 bad=dict(rows[0]);bad['left']=dict(bad['left']);bad['left']['phase']=(bad['left']['phase']+2)%4
 want=adjoint(frame(bad['new']))+frame(bad['old']);got=(('M',parse(bad['right'])),)+standard(bad['rank'])+(('M',parse(bad['left'])),)
 try:same(got,want,'wrong phase control')
 except ValueError as e:control=str(e)
 else:raise ValueError('wrong absolute phase accepted')
 result={'status':'PASS_INDEPENDENT_EXACT_TRANSPOSE_PHASES','head':'329b2ff35d2994b11abbb59f770d12da75c494ac','paid_classes':len(rows),'native_warp_classes':len(warps),'literal_native_columns':columns,'Q_squared_ports':len(c['ports']),'helper_ranks':[4,7,8,9],'absolute_phase_control_rejected':control,'independent_method':'Pauli conjugation plus exact integer-Gaussian |0> scalar anchor; no candidate/source evaluator imports','seconds':round(time.monotonic()-start,3),'phase_artifact_sha256':hashlib.sha256((PKG/'PHASES.json.gz').read_bytes()).hexdigest(),'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 (HERE/'PHASE-RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
