"""Exact dyadic cold-end realization of the source-branch/factory-completion word.
Prepared for icekylinx with OpenAI Codex assistance; Apache-2.0.
This is a constructor: independent endpoint/frame audits remain required.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import copy,gzip,json,hashlib,time,sys,argparse,importlib.util
D=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
for name in ('input','out','hamming','upstream-package'):ap.add_argument('--'+name,type=Path,required=True)
args=ap.parse_args();WPATH=args.input;OUT=args.out
assert __debug__, 'Assertions are required'
OUT.mkdir(exist_ok=False,parents=True)
def rd(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
w=rd(WPATH);v=w['report']['v'];n=2*v+w['report']['R'];N=list(range(v))+list(range(2*v,n));ix={x:i for i,x in enumerate(N)}
F9=[256,128,64,32,16,8,4,2,1];t0=time.monotonic()
def basis(vs):
 d={}
 for a in vs:
  for k in sorted(d,reverse=True):
   if a>>k&1:a^=d[k]
  if a:
   k=a.bit_length()-1
   for j in d:
    if d[j]>>k&1:d[j]^=a
   d[k]=a
 return tuple(d[k] for k in sorted(d,reverse=True))
def inside(a,b):return basis(a+b)==b
def regs(e):return e[1:3] if e[0]=='add' else e[1:2]
def inverse(e):
 e=copy.deepcopy(e)
 if e[0]=='add':e[3]=-e[3]
 else:e[2],e[3]=e[3],e[2]
 return e
def apply(e,M,mapping=None):
 t=mapping[e[1]] if mapping is not None else e[1]
 if e[0]=='add':
  s=mapping[e[2]] if mapping is not None else e[2];q=Q(e[3],e[4])
  for j,a in M[s].items():
   x=M[t].get(j,Q(0))+q*a
   if x:M[t][j]=x
   else:M[t].pop(j,None)
 else:
  q=Q(e[2],e[3]);M[t]={j:q*a for j,a in M[t].items()}
def rref(A):
 a=[list(map(Q,row)) for row in A];nr=len(a);nc=len(a[0]) if nr else 0;row=0;piv=[]
 for c in range(nc):
  k=next((i for i in range(row,nr) if a[i][c]),None)
  if k is None:continue
  a[row],a[k]=a[k],a[row];q=a[row][c];a[row]=[x/q for x in a[row]]
  for i in range(nr):
   if i!=row and a[i][c]:q=a[i][c];a[i]=[x-q*y for x,y in zip(a[i],a[row])]
  piv.append(c);row+=1
  if row==nr:break
 return a,piv
def rank(A):return len(rref(A)[1])
def null(A,nc=None):
 if A:a,piv=rref(A);nc=len(a[0])
 else:a=[];piv=[];assert nc is not None
 free=[j for j in range(nc) if j not in piv];out=[[Q(0) for j in free] for i in range(nc)]
 for k,c in enumerate(free):out[c][k]=Q(1)
 for i,c in enumerate(piv):
  for k,j in enumerate(free):out[c][k]=-a[i][j]
 return out
def mm(A,B):
 if not A:return []
 if not B:return [[] for row in A]
 bt=list(zip(*B));return [[sum((a*b for a,b in zip(row,col)),Q(0)) for col in bt] for row in A]
def tr(A):return list(map(list,zip(*A)))
def inv(A):
 n0=len(A);a,p=rref([row+[Q(i==j) for j in range(n0)] for i,row in enumerate(A)])
 assert p[:n0]==list(range(n0))
 return [row[n0:] for row in a]
def unit(q):
 if not q:return False
 a=abs(q.numerator);b=q.denominator
 return not a&(a-1) and not b&(b-1)
def dyadic(q):return not q.denominator&(q.denominator-1)
def opadd(t,s,q,F):return ['add',t,s,q.numerator,q.denominator,list(F)]
def opscale(t,q,F):return ['scale',t,q.numerator,q.denominator,list(F)]
def eliminate(M,ids,F,skip=()):
 """Return legal dyadic row operations taking an invertible sparse matrix to I."""
 skip=set(skip);ops=[];dim=len(M)
 def add(i,j,q):
  if q:
   assert dyadic(q);e=opadd(ids[i],ids[j],q,F);ops.append(e)
   for c,x in M[j].items():
    z=M[i].get(c,Q(0))+q*x
    if z:M[i][c]=z
    else:M[i].pop(c,None)
 def scale(i,q):
  if q!=1:
   assert unit(q);ops.append(opscale(ids[i],q,F));M[i]={c:q*x for c,x in M[i].items()}
 def swap(i,j):
  if i!=j:
   add(i,j,Q(1));add(j,i,Q(-1));add(i,j,Q(1));scale(j,Q(-1))
 for c in range(dim):
  if c in skip:
   assert M[c]=={c:Q(1)} and all(not M[i].get(c) for i in range(dim) if i!=c)
   continue
  cand=[i for i in range(c,dim) if i not in skip and M[i].get(c)]
  k=next((i for i in cand if unit(M[i][c])),None)
  if k is None:
   # Elementary Euclidean row additions reduce the pivot-column numerator gcd.
   assert cand,('singular',c)
   while k is None:
    cand.sort(key=lambda i:abs(M[i][c]));a=cand[0]
    b=next((i for i in cand[1:] if M[i][c]),None)
    if b is None:raise ValueError(('non-dyadic determinant pivot',c,M[a][c]))
    rat=M[b][c]/M[a][c];q=rat.numerator//rat.denominator
    if q==0:q=1 if rat>0 else -1
    add(b,a,Q(-q));cand=[i for i in cand if M[i].get(c)]
    k=next((i for i in cand if unit(M[i][c])),None)
  swap(c,k);scale(c,1/M[c][c])
  for i in range(dim):
   if i!=c and M[i].get(c):
    assert i not in skip
    add(i,c,-M[i][c])
 assert all(row=={i:Q(1)} for i,row in enumerate(M))
 return ops
def realize(A,ids,F):
 M=[{j:Q(x) for j,x in enumerate(row) if x} for row in A]
 return [inverse(e) for e in reversed(eliminate(M,ids,F))]
# Reconstruct the actual non-target map after the inherited HPE tail.
inherited_tail=[w['cleanup'][i][:-1]+[list(f)] for i,f in w.get('early_cleanup',[])]
mainN=[e for e in w['A']+w['B'] if not v<=e[1]<2*v]
M=[{i:Q(1)} for i in range(len(N))]
for e in mainN+inherited_tail:apply(e,M,ix)
MI=[{i:Q(1)} for i in range(len(N))]
for e in reversed(mainN+inherited_tail):apply(inverse(e),MI,ix)
cur={x:(w['ports'][x],) if x<v else basis(w.get('start_extra',{}).get(str(x),[])) for x in N}
for e in w['A']+w['B']+inherited_tail:
 for x in regs(e):
  if x in cur:cur[x]=basis(e[-1])
enter=set(map(int,w.get('start_extra',{})));protected=[ix[x] for x in N if x<v or x in enter]
mods=rd(args.hamming/'PACKET-PROGRAMS.json.gz');proto=rd(args.hamming/'PROTOTYPE.json')
plans=[];premix=[];tail=[];ends={};Mafter=copy.deepcopy(M)
for b,mod in enumerate(mods):
 ss=mod['receipt']['source_lines'];F=basis([proto['binary_ports'][s] for s in ss]);I=[ix[x] for x in N if inside(cur[x],F)]
 hs=list(range(224+16*b,224+16*(b+1)));H=[ix[x] for x in hs]
 C=[[M[i].get(j,Q(0)) for j in protected] for i in I]
 L=tr(null(tr(C),len(I)))
 A=[[MI[j].get(i,Q(0)) for i in I] for j in protected];A=[row for row in A if any(row)]
 K=null(A,len(I));BK=mm(L,K);_,piv=rref(BK);r=len(piv);assert r==len(L)==(2 if b in [0,1,2,11,12,13] else 4),(b,r,len(L))
 Ksel=[[row[j] for j in piv] for row in K];Bsel=[[row[j] for j in piv] for row in BK];U=mm(Ksel,inv(Bsel));assert mm(L,U)==[[Q(i==j) for j in range(r)] for i in range(r)]
 q=mm([[MI[i].get(j,Q(0)) for j in I] for i in range(len(N))],U)
 assert all(not any(q[i]) for i in range(len(N)) if i not in H),('nonlocal premix',b)
 RR=mm(L,[[M[i].get(j,Q(0)) for j in H] for i in I]);qH=[q[i] for i in H]
 assert mm(RR,qH)==[[Q(i==j) for j in range(r)] for i in range(r)]
 # Pick low physical helper destinations with independent U coordinate rows.
 ih=[]
 for j in sorted((j for j,i in enumerate(I) if N[i] in hs),key=lambda j:(cur[N[I[j]]]!=F,N[I[j]])):
  if rank([U[k] for k in ih]+[U[j]])>len(ih):ih.append(j)
  if len(ih)==r:break
 assert len(ih)==r
 endhs=[N[I[j]] for j in ih];endhidx=[hs.index(h) for h in endhs]
 kerR=null(RR,16);Qmat=[[Q(0) for j in range(16)] for i in range(16)]
 for j,hj in enumerate(endhidx):
  for i in range(16):Qmat[i][hj]=qH[i][j]
 other=[j for j in range(16) if j not in endhidx]
 for k,j in enumerate(other):
  for i in range(16):Qmat[i][j]=kerR[i][k]
 assert rank(Qmat)==16
 pops=realize(Qmat,hs,());premix+=pops
 T=[[Q(i==j)-sum((U[i][k]*L[k][j] for k in range(r)),Q(0)) for j in range(len(I))] for i in range(len(I))]
 for k,i in enumerate(ih):T[i]=L[k]
 tops=realize(T,[N[i] for i in I],F);tail+=tops
 # Right-compose this initial helper premix; other blocks have disjoint H sets.
 for row in Mafter:
  vals=[row.get(h,Q(0)) for h in H]
  if any(vals):
   for hj in H:row.pop(hj,None)
   for j,hj in enumerate(H):
    z=sum((vals[i]*Qmat[i][j] for i in range(16)),Q(0))
    if z:row[hj]=z
 for e in tops:apply(e,Mafter,ix)
 ends.update({h:list(F) for h in endhs})
 plans.append(dict(block=b,frame=list(F),registers=[N[i] for i in I],ends=endhs,pairing_rank=r,premix_gates=len(pops),tail_gates=len(tops),Q=[[str(x) for x in row] for row in Qmat],T=[[str(x) for x in row] for row in T]))
 print('BLOCK',b,'ends',endhs,'Qops',len(pops),'Tops',len(tops),flush=True)
# Check actual post-tail isolation before constructing the high-frame inverse.
allends=set(ends)|set(map(int,w.get('helper_final',{})))
for h in allends:
 j=ix[h];assert Mafter[j]=={j:Q(1)},('row not isolated',h,Mafter[j]);assert all(not row.get(j) for i,row in enumerate(Mafter) if i!=j),('column not isolated',h)
print('EXACT_ISOLATED',len(ends),'new;',len(allends),'total',round(time.monotonic()-t0,3),flush=True)
fullops=eliminate(copy.deepcopy(Mafter),N,F9,[ix[x] for x in allends])
print('FULL_INVERSE',len(fullops),round(time.monotonic()-t0,3),flush=True)
# Cancel new cold-axis target responses inside A, after their wrappers.
Dirt=[({h:Q(1)} if h in ends else {}) for h in range(n)]
for e in premix+w['A']+w['cut']+w['B']:apply(e,Dirt)
for e in w['precondition']:apply(e,Dirt)
postcomp=[opadd(y,h,-a,()) for y in range(v,2*v) for h,a in sorted(Dirt[y].items()) if a]
assert all(h in ends for e in postcomp for h in [e[2]])
new=copy.deepcopy(w);new['A']=postcomp+premix+w['A'];new['cleanup']=inherited_tail+tail+fullops
new['early_cleanup']=[[i,e[-1]] for i,e in enumerate(inherited_tail+tail)]
new['helper_final'].update({str(h):f for h,f in ends.items()})
new['refactored_cleanup']={'kind':'source_branch_gauge_and_retired_completion_cold44','new_cold_ends':len(ends),'exact_non_target_isolation_checked':True,'high_inverse':'dyadic_sparse_Gauss_Jordan'}
# Derive paid profile by subtracting and adding literal frame-chain counts.
spec=importlib.util.spec_from_file_location('upstream_cold_end',args.upstream_package/'code/build_cold_end.py')
profile_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(profile_module)
oldprof,_=profile_module.chain_profile(w);newprof,_=profile_module.chain_profile(new)
prof=Counter({int(k):z for k,z in w['report']['local_profile'].items()});prof.subtract(oldprof);prof.update(newprof)
widths=Counter(len(basis(new['helper_final'].get(str(h),F9)))-len(basis(new.get('start_extra',{}).get(str(h),[]))) for h in range(224,n))
new['report'].update(local_profile={str(k):z for k,z in sorted(prof.items()) if z},local_rank_mass=sum(k*z for k,z in prof.items()),width_inventory={str(k):z for k,z in sorted(widths.items()) if z},status='EXACT_COLD44_CONSTRUCTED_PENDING_INDEPENDENT_AUDIT')
raw=json.dumps(new,sort_keys=True,separators=(',',':')).encode();sha=hashlib.sha256(raw).hexdigest();(OUT/'FULL-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0))
recipe={'premix':postcomp+premix,'cleanup':new['cleanup'],'early_cleanup':new['early_cleanup'],'cold_ends':{str(h):f for h,f in ends.items()},'refactored_cleanup':new['refactored_cleanup'],'output_content_sha256':sha}
(OUT/'RECIPE.json.gz').write_bytes(gzip.compress(json.dumps(recipe,sort_keys=True,separators=(',',':')).encode(),mtime=0))
receipt=dict(input_content_sha256=hashlib.sha256(gzip.decompress(WPATH.read_bytes())).hexdigest(),output_content_sha256=sha,blocks=plans,new_cold_ends=len(ends),all_low_ended_helpers=len(allends),premix_gates=len(premix),postwrapper_compensation_gates=len(postcomp),tail_gates=len(tail),inherited_tail_gates=len(inherited_tail),full_inverse_gates=len(fullops),profile=new['report']['local_profile'],width_inventory=new['report']['width_inventory'],rank_mass=new['report']['local_rank_mass'],seconds=time.monotonic()-t0)
(OUT/'CONSTRUCTION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:z for k,z in receipt.items() if k!='blocks'},indent=2),flush=True)
