"""Exact dyadic Clifford-to-one-rank-d-call compiler; Python stdlib only.
Cliffords are specified by literal sequential gates, retaining absolute phase.
Paulis use bare i**p X**x Z**z. Gate turn normalizes (I-i H)/(1-i).
"""
from fractions import Fraction as F
import json,random,argparse
from pathlib import Path


def need(x,msg):
 if not x:raise ValueError(msg)


def parity(x):return x.bit_count()&1


def mv(cols,x):
 y=0
 while x:
  t=x&-x;y^=cols[t.bit_length()-1];x-=t
 return y


def inverse(cols):
 n=len(cols);rows=[sum(((cols[j]>>i)&1)<<j for j in range(n))|(1<<(n+i)) for i in range(n)]
 for j in range(n):
  k=next((i for i in range(j,n) if rows[i]>>j&1),None);need(k is not None,'singular GL')
  rows[j],rows[k]=rows[k],rows[j]
  for i in range(n):
   if i!=j and rows[i]>>j&1:rows[i]^=rows[j]
 return [sum(((rows[i]>>(n+j))&1)<<i for i in range(n)) for j in range(n)]


def transpose(cols):return [sum(((cols[i]>>j)&1)<<i for i in range(len(cols))) for j in range(len(cols))]


def independent(vectors):
 bs={};out=[]
 for v in vectors:
  x=v
  while x and x.bit_length()-1 in bs:x^=bs[x.bit_length()-1]
  if x:bs[x.bit_length()-1]=x;out.append(v)
 return out


def pgate(t,g,n):
 x,z,p=t;typ=g[0]
 if typ=='turn':
  a,b,sgn=g[1:];need(sgn in (-1,1),'turn orientation')
  if parity((a&z)^(b&x)):p=(p+(a&b).bit_count()+2*parity(b&x)-sgn)%4;x^=a;z^=b
 elif typ=='s':
  mask,sgn=g[1:];p=(p+sgn*(x&mask).bit_count())%4;z^=(x&mask)if sgn%2 else 0
 elif typ=='cz':
  a,b=g[1:];p=(p+2*((x>>a)&1)*((x>>b)&1))%4;z^=(((x>>a)&1)<<b)^(((x>>b)&1)<<a)
 elif typ=='gl':
  cols=g[1];x=mv(cols,x);z=mv(transpose(inverse(cols)),z)
 elif typ=='x':p=(p+2*parity(z&g[1]))%4
 elif typ=='phase':pass
 else:raise ValueError('unknown gate '+str(g))
 return x,z,p


def tableau(n,gates):
 ts=[(1<<j,0,0)for j in range(n)]+[(0,1<<j,0)for j in range(n)]
 for g in gates:ts=[pgate(t,g,n)for t in ts]
 return ts


ZERO=(F(0),F(0));ONE=(F(1),F(0));IP=(ONE,(F(0),F(1)),(-F(1),F(0)),(F(0),-F(1)))

def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):return a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]
def sc(a,r):return a[0]*r,a[1]*r


def state_gate(v,g,n):
 out=[ZERO]*len(v);typ=g[0]
 if typ=='turn':
  x,z,sgn=g[1:];a=(F(1,2),F(sgn,2));b=(F(1,2),F(-sgn,2));ph=(x&z).bit_count()
  for j,c in enumerate(v):
   out[j]=add(out[j],mul(a,c));k=j^x;out[k]=add(out[k],mul(mul(b,IP[(ph+2*parity(z&j))%4]),c))
 elif typ=='s':
  mask,sgn=g[1:]
  for j,c in enumerate(v):out[j]=mul(c,IP[(sgn*(j&mask).bit_count())%4])
 elif typ=='cz':
  a,b=g[1:]
  for j,c in enumerate(v):out[j]=sc(c,-1 if (j>>a&1)and(j>>b&1)else 1)
 elif typ=='gl':
  for j,c in enumerate(v):out[mv(g[1],j)]=c
 elif typ=='x':
  for j,c in enumerate(v):out[j^g[1]]=c
 elif typ=='phase':out=[mul(c,IP[g[1]%4])for c in v]
 else:raise ValueError(typ)
 return out


def state(n,gates,x=0):
 v=[ZERO]*(1<<n);v[x]=ONE
 for g in gates:v=state_gate(v,g,n)
 return v


def invert_gate(g):
 if g[0]in('turn','s','phase'):return [*g[:-1],-g[-1]]
 if g[0]=='gl':return ['gl',inverse(g[1])]
 return g[:]


def free_reduction(n,lag):
 xs=independent([x for x,z,p in lag]);d=len(xs)
 full=independent(xs+[1<<j for j in range(n)]);need(len(full)==n,'GL completion')
 R=inverse(full);linear=['gl',R]
 lt=[pgate(v,linear,n)for v in lag]
 bs={}
 for x,z,p in lt:
  while x and x.bit_length()-1 in bs:
   k=x.bit_length()-1;xx,zz=bs[k];x^=xx;z^=zz
  if x:bs[x.bit_length()-1]=(x,z)
 K=[]
 for j in range(d):
  x=1<<j;z=0
  while x:
   k=x.bit_length()-1;need(k in bs,'missing active projection');xx,zz=bs[k];x^=xx;z^=zz
  K.append(z&((1<<d)-1))
 need(all(((K[i]>>j)&1)==((K[j]>>i)&1)for i in range(d)for j in range(d)),'nonisotropic Z image')
 free=[linear]+[['s',1<<i,1]for i in range(d)if K[i]>>i&1]+[['cz',i,j]for i in range(d)for j in range(i+1,d)if K[i]>>j&1]
 mask=(1<<d)-1
 J=[['s',mask,1]]+[['turn',1<<i,0,1]for i in range(d)]+[['s',mask,1]]
 return d,free,J


def chart_from_lagrangian(n,columns):
 lag=[(v&((1<<n)-1),v>>n,0)if isinstance(v,int)else (*v,0)for v in columns]
 need(len(lag)==n and len(independent([x|(z<<n)for x,z,p in lag]))==n,'Lagrangian dimension')
 need(all(not parity((x&zz)^(z&xx))for x,z,p in lag for xx,zz,pp in lag),'Lagrangian isotropy')
 d,free,J=free_reduction(n,lag)
 gates=[invert_gate(g)for g in reversed(J)]+[invert_gate(g)for g in reversed(free)]
 got=[x|(z<<n)for x,z,p in tableau(n,gates)[n:]]
 need(len(independent(got+[x|(z<<n)for x,z,p in lag]))==n,'explicit chart factory')
 return {'n':n,'gates':gates,'projection_rank':d,'scope':'Explicit chosen chart; no assertion of equality to an older chart with the same Lagrangian.'}


def factor_gl(cols):
 n=len(cols);rows=transpose(cols);ops=[]
 for j in range(n):
  k=next((i for i in range(j,n)if rows[i]>>j&1),None);need(k is not None,'singular GL factor')
  if k!=j:
   rows[j],rows[k]=rows[k],rows[j];cc=[1<<i for i in range(n)];cc[j],cc[k]=cc[k],cc[j];ops.append(['gl',cc])
  for i in range(n):
   if i!=j and rows[i]>>j&1:
    rows[i]^=rows[j];cc=[1<<k for k in range(n)];cc[j]^=1<<i;ops.append(['gl',cc])
 need(rows==[1<<j for j in range(n)],'GL reduction failed')
 return list(reversed(ops))


def compile_word(n,gates):
 need(1<=n<=12,'finite compiler supports up to 12 bits')
 t=tableau(n,gates);d,free,J=free_reduction(n,t[n:])
 mon=tableau(n,gates+free+J)
 need(all(x==0 and p%2==0 for x,z,p in mon[n:]),'monomial reduction failed')
 A=[x for x,z,p in mon[:n]];need(len(independent(A))==n,'monomial address singular')
 sign=sum((p//2)<<j for j,(x,z,p)in enumerate(mon[n:]));b=mv(A,sign)
 v=state(n,gates+free+J)
 need(all(c==ZERO for j,c in enumerate(v)if j!=b),'absolute-phase extraction not monomial')
 need(v[b]in IP,'non-Z4 dyadic unit phase')
 phase=IP.index(v[b]);lin=[(p+2*parity(z&b))%4 for x,z,p in mon[:n]]
 cross=[[i,j]for j in range(n)for i in range(j)if parity(mon[j][1]&A[i])]
 # G=P_(A,b) D_phi. Its literal gate list retains the extracted absolute phase separately.
 G=[['s',1<<j,a]for j,a in enumerate(lin)if a]+[['cz',i,j]for i,j in cross]+[['gl',A],['x',b]]
 need(tableau(n,G)==mon,'free monomial phase polynomial mismatch')
 return {'n':n,'paid_rank':d,'F':free,'J':J,'G':G,'G_global_i':phase,'address_columns':A,'address_offset':b,'phase_linear':lin,'phase_cross':cross,'equation':'U = F^-1 J^-1 G; G includes its explicit global i phase','all_width_scope':'Tensorize each literal gate separately; scalar phases become i^(phase*f). One paid rank-d call for C on d selected blocks.'}


def replay(n,gates,certificate,full_columns=True):
 need(certificate==compile_word(n,gates),'certificate recomputation mismatch')
 c=certificate;inverse_J=[invert_gate(g)for g in reversed(c['J'])];inverse_F=[invert_gate(g)for g in reversed(c['F'])]
 for x in range(1<<n)if full_columns else [0]:
  expected=state(n,gates,x);actual=state(n,c['G']+inverse_J+inverse_F,x)
  actual=[mul(IP[c['G_global_i']],v)for v in actual]
  need(actual==expected,'absolute-phase column mismatch')
 return (1<<n)if full_columns else 1


def lift_word(n,gates,f):
 out=[]
 for g in gates:
  typ=g[0]
  if typ=='phase':out.append(['phase',g[1]*f]);continue
  if typ=='gl':
   out.append(['gl',[v<<(n*t)for t in range(f)for v in g[1]]]);continue
  for t in range(f):
   off=n*t
   if typ=='turn':out.append(['turn',g[1]<<off,g[2]<<off,g[3]])
   elif typ=='s':out.append(['s',g[1]<<off,g[2]])
   elif typ=='cz':out.append(['cz',g[1]+off,g[2]+off])
   elif typ=='x':out.append(['x',g[1]<<off])
   else:raise ValueError('unknown lift')
 return out


def run():
 rng=random.Random(62210);cases=columns=0;ranks={}
 for n in (1,2,3):
  for length in (0,1,2,5,12):
   for repeat in range(5):
    gates=[]
    for k in range(length):
     axis=rng.randrange(1,1<<(2*n));gates.append(['turn',axis&((1<<n)-1),axis>>n,rng.choice([-1,1])])
    c=compile_word(n,gates);columns+=replay(n,gates,c);cases+=1;ranks[str(c['paid_rank'])]=ranks.get(str(c['paid_rank']),0)+1
 # Actual 9-bit scale: tableaux plus one exact column determine the Clifford including phase.
 nine_cases=0
 for length in (0,20,48):
  gates=[['turn',(axis:=rng.randrange(1,1<<18))&511,axis>>9,rng.choice([-1,1])]for k in range(length)]
  c=compile_word(9,gates);replay(9,gates,c,full_columns=False);nine_cases+=1
 # An explicit -I word has identity tableau and rank zero, but phase two.
 neg=[['turn',1,0,1],['turn',1,0,1],['turn',0,1,1],['turn',0,1,1]]*2
 nc=compile_word(1,neg);need(nc['paid_rank']==0 and nc['G_global_i']==2,'negative identity scalar')
 replay(1,neg,nc)
 tensor_columns=0
 for n,gates,f in [(1,neg,2),(1,neg,3),(2,[['turn',1,2,1],['turn',3,1,-1],['phase',1]],2)]:
  c=compile_word(n,gates)
  compiled=c['G']+[invert_gate(g)for g in reversed(c['J'])]+[invert_gate(g)for g in reversed(c['F'])]+[['phase',c['G_global_i']]]
  for x in range(1<<(n*f)):
   need(state(n*f,lift_word(n,gates,f),x)==state(n*f,lift_word(n,compiled,f),x),'all-width literal tensor phase')
   tensor_columns+=1
 grouped=compile_word(2,[['turn',1,0,1],['turn',2,0,1]])
 need(grouped['paid_rank']==2 and sum(g[0]=='turn'for g in grouped['J'])==2,'rank-two grouping control')
 chart_cases=gl_cases=0;max_gl_passes=0
 for n in (1,2,3,9):
  for repeat in range(5):
   gates=[['turn',(axis:=rng.randrange(1,1<<(2*n)))&((1<<n)-1),axis>>n,rng.choice([-1,1])]for k in range(16)]
   lag=[x|(z<<n)for x,z,p in tableau(n,gates)[n:]]
   ch=chart_from_lagrangian(n,lag);chart_cases+=1
   cols=[1<<j for j in range(n)]
   for k in range(20):
    i,j=rng.randrange(n),rng.randrange(n)
    if i!=j:cols=[v^((v>>i&1)<<j)for v in cols]
   fact=factor_gl(cols);need(tableau(n,fact)==tableau(n,[['gl',cols]]),'GL elementary replay')
   need(len(fact)<=n*n,'GL pass bound');max_gl_passes=max(max_gl_passes,len(fact));gl_cases+=1
 edge_cases=edge_columns=orientation_differences=0
 for n in (2,3):
  for rep in range(5):
   words=[]
   for side in range(2):
    word=[['turn',(axis:=rng.randrange(1,1<<(2*n)))&((1<<n)-1),axis>>n,rng.choice([-1,1])]for k in range(8)]
    lag=[x|(z<<n)for x,z,p in tableau(n,word)[n:]];words.append((lag,chart_from_lagrangian(n,lag)['gates']))
   (la,Ba),(lb,Bb)=words
   gl=[1<<i for i in range(n)];gl[0]^=1<<(n-1)
   # Actual phase-complete representative of the native free map S^-1 P_g S.
   mask=(1<<n)-1;M=[['s',mask,1],['gl',gl],['s',mask,-1]]
   mt=tableau(n,M)
   def tmap(v):
    x,z=v&mask,v>>n;out=0
    for j,t in enumerate(mt):
     if ((x|(z<<n))>>j)&1:out^=t[0]|(t[1]<<n)
    return out
   expected=len(independent([tmap(v)for v in la]+lb))-n
   # A_v=B_v^-1, so A_b M A_a^-1 has sequential word Ba, M, inverse(Bb).
   transition=Ba+M+[invert_gate(g)for g in reversed(Bb)]
   c=compile_word(n,transition);need(c['paid_rank']==expected,'contact edge grade versus physical operator')
   edge_columns+=replay(n,transition,c);edge_cases+=1
   wrong=[invert_gate(g)for g in reversed(Ba)]+M+Bb
   if compile_word(n,wrong)['paid_rank']!=expected:orientation_differences+=1
 need(orientation_differences>0,'orientation rejecting fixture not discriminating')
 # Absolute phase cannot be dropped even though every Pauli tableau is unchanged.
 gates=[['turn',1,0,1],['turn',0,1,1]];c=compile_word(1,gates)
 bad=dict(c);bad['G_global_i']=(c['G_global_i']+1)%4
 rejection=0
 try:replay(1,gates,bad)
 except ValueError:rejection+=1
 need(rejection==1,'global phase rejecting control')
 return {'status':'PASS_DYADIC_CLIFFORD_COMPILER','cases':cases,'exact_columns':columns,'nine_bit_tableau_and_phase_cases':nine_cases,'negative_identity_phase_control':True,'lifted_exact_columns':tensor_columns,'rank_two_grouping_control':True,'explicit_lagrangian_chart_cases':chart_cases,'GL_involution_factorization_cases':gl_cases,'maximum_observed_GL_passes':max_gl_passes,'physical_contact_edge_cases':edge_cases,'physical_contact_exact_columns':edge_columns,'wrong_orientation_distinguished':orientation_differences,'rank_census':ranks,'absolute_phase_rejecting_controls':rejection,'actual_new_source_profile':False,'new_kappa':None}


def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path);p.add_argument('--chart',type=Path);p.add_argument('--expected',type=Path);a=p.parse_args()
 if a.chart:
  x=json.loads(a.chart.read_text(encoding='utf8'));out=chart_from_lagrangian(x['n'],x['lagrangian'])
 elif a.input:
  x=json.loads(a.input.read_text(encoding='utf8'));c=compile_word(x['n'],x['gates']);replay(x['n'],x['gates'],c,full_columns=x['n']<=4);out=c
 else:
  out=run()
  if a.expected:need(out==json.loads(a.expected.read_text(encoding='utf8')),'expected mismatch')
 print(json.dumps(out,sort_keys=True))

if __name__=='__main__':main()
