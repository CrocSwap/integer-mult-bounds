#!/usr/bin/env python3
"""ROOT ONLY. One exact q^-1 W fanout quotient/program, no search or native replay.
Classification: pullback computational-Z Lagrangians (LEFT monomial cosets).
Alias oracle: pinned signed tableau + absolute anchor AND all512 sparse columns.
Integer row-lattice certificates avoid all runtime odd divisions.
"""
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
from functools import lru_cache
import argparse,hashlib,importlib.util,json,math,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[3]
PH=BASE/'swarm-provider-audit-sol-high-20261024/agents/algebra/phase_exact.py'
N=9;D=512

def need(x,msg):
 if not x:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(path,value):
 need(not path.exists(),'immutable output exists: '+str(path));path.write_text(json.dumps(value,indent=2)+'\n')
def zmat(m,n):return [[0]*n for _ in range(m)]
def eye(m):return [[int(i==j)for j in range(m)]for i in range(m)]
def mul(A,B):
 if not A:return []
 return [[sum(a*b for a,b in zip(row,col))for col in zip(*B)]for row in A]
def rational_rank(M):
 a=[[Fraction(x)for x in row]for row in M];r=0
 for c in range(8):
  k=next((k for k in range(r,len(a))if a[k][c]),None)
  if k is None:continue
  a[r],a[k]=a[k],a[r];v=a[r][c];a[r]=[x/v for x in a[r]]
  for k in range(len(a)):
   if k!=r and a[k][c]:
    v=a[k][c];a[k]=[x-v*y for x,y in zip(a[k],a[r])]
  r+=1
 return r

def rref2(rows):
 a=list(rows);r=0
 for c in range(17,-1,-1):
  k=next((k for k in range(r,len(a))if a[k]>>c&1),None)
  if k is None:continue
  a[r],a[k]=a[k],a[r]
  for k in range(len(a)):
   if k!=r and a[k]>>c&1:a[k]^=a[r]
  r+=1
 return tuple(a[:r])
def egcd(a,b):
 oldr,r=a,b;olds,s=1,0;oldt,t=0,1
 while r:
  q=oldr//r;oldr,r=r,oldr-q*r;olds,s=s,olds-q*s;oldt,t=t,oldt-q*t
 if oldr<0:return -oldr,-olds,-oldt
 return oldr,olds,oldt

def integer_basis(M):
 """Row-Hermite via unimodular operations, maintaining exact inverse V."""
 m=len(M);A=[row[:]for row in M];U=eye(m);V=eye(m);rank=0;pivots=[]
 def swap(i,j):
  A[i],A[j]=A[j],A[i];U[i],U[j]=U[j],U[i]
  for row in V:row[i],row[j]=row[j],row[i]
 def plus(i,j,q):
  A[i]=[x+q*y for x,y in zip(A[i],A[j])];U[i]=[x+q*y for x,y in zip(U[i],U[j])]
  for row in V:row[j]-=q*row[i]
 for col in range(8):
  k=next((k for k in range(rank,m)if A[k][col]),None)
  if k is None:continue
  swap(rank,k)
  for i in range(rank+1,m):
   if not A[i][col]:continue
   aa,bb=A[rank][col],A[i][col];g,x,y=egcd(aa,bb)
   a0,a1=A[rank][:],A[i][:];u0,u1=U[rank][:],U[i][:]
   A[rank]=[x*z+y*w for z,w in zip(a0,a1)];A[i]=[-(bb//g)*z+(aa//g)*w for z,w in zip(a0,a1)]
   U[rank]=[x*z+y*w for z,w in zip(u0,u1)];U[i]=[-(bb//g)*z+(aa//g)*w for z,w in zip(u0,u1)]
   for row in V:
    v0,v1=row[rank],row[i];row[rank]=(aa//g)*v0+(bb//g)*v1;row[i]=-y*v0+x*v1
  if A[rank][col]<0:
   A[rank]=[-x for x in A[rank]];U[rank]=[-x for x in U[rank]]
   for row in V:row[rank]=-row[rank]
  pivot=A[rank][col]
  for i in range(rank):
   q=A[i][col]//pivot
   if q:plus(i,rank,-q)
  pivots.append(col);rank+=1
  if rank==m:break
 H=A[:rank];S=U[:rank];T=[row[:rank]for row in V]
 need(rank==rational_rank(M),'independent exact rational rank agrees')
 need(mul(U,V)==eye(m)and mul(V,U)==eye(m),'integer unimodular inverse certificate')
 need(mul(U,M)==A and all(not any(row)for row in A[rank:]),'Hermite transformed matrix certificate')
 need(mul(S,M)==H and (mul(T,H)if rank else zmat(m,8))==M,'M=TH and H=SM exact')
 need(all(H[j][pivots[j]]>0 and all(not H[j][c]for c in range(pivots[j]))for j in range(rank)),'independent echelon basis')
 return {'rank':rank,'H':H,'S':S,'T':T,'U':U,'V':V,'pivots':pivots}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--program',type=Path,required=True);ap.add_argument('--result',type=Path,required=True);args=ap.parse_args()
 for p in [args.program,args.result]:need(not p.exists(),'immutable output exists')
 inp=json.loads(args.input.read_text())
 for rel,h in inp['source_sha256'].items():need(sha(BASE/rel)==h,'source hash '+rel)
 need(sha(PH)=='15e90b63c5659090f02902cb38951ec4ab252352fb0b967b411ed547c501e2ba','pinned independent phase oracle')
 spec=importlib.util.spec_from_file_location('fanout_phase',PH);ph=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ph;spec.loader.exec_module(ph)
 Kp=[ph.freeze(w)for w in inp['Kp_words']];Km=[ph.freeze(w)for w in inp['Km_words']];M=inp['M_rows'];axes=inp['local_axes_25'];need(len(Kp)==112 and len(Km)==8 and len(M)==112 and all(len(row)==8 for row in M),'actual112x8 source')
 norm=json.loads((BASE/inp['normalizers_path']).read_text());hc=json.loads((BASE/inp['hcode_path']).read_text());provider=json.loads((BASE/inp['provider_path']).read_text())
 need([ph.freeze(z['K_word'])for z in norm['ports']]==Kp,'all112 actualKp words')
 need([[norm['mode_columns'][k][i]for k in range(8)]for i in range(112)]==M,'actual M rows orientation')
 need([ph.freeze(hc['operations'][112+k]['word'])for k in range(8)]==Km,'actual8 commonKm from acceptedHcode')
 need([ph.freeze(next(z['input_K']['literal_word']for z in provider['mode_boundaries']if z['mode']==k))for k in range(8)]==Km,'actualproviderKm without boundaryfactor2')
 A=[ph.adjoint(w)+(('C',1,-1),)for w in Kp]
 keys=[];bykey={}
 for i,word in enumerate(A):
  inv=ph.adjoint(word);rows=[]
  for j in range(9):
   x,z,p=ph.pauli(inv,0,1<<j);rows.append(x|(z<<9))
  key=rref2(rows);need(len(key)==9,'nine-dimensional pullbackZ Lagrangian');keys.append(key);bykey.setdefault(key,[]).append(i)
 # Exact monomial compiler from the full signed tableau and absolute anchor.
 def monomial_alias(word):
  sig=ph.signature(word);tab,anchor,den=sig
  need(all(tab[9+j][0]==0 and tab[9+j][2]%2==0 for j in range(9)),'left quotient preserves computationalZ')
  support=[j for j,v in enumerate(anchor)if v!=(0,0)];need(len(support)==1 and den==0,'unit-modulus absolute monomial anchor')
  b=support[0];gamma={(1,0):0,(0,1):1,(-1,0):2,(0,-1):3}[anchor[b]]
  cols=tuple(tab[j][0]for j in range(9));need(ph.rank(cols)==9,'invertible monomial affine map');F=ph.transpose(cols)
  alpha=tuple((tab[j][2]+2*ph.parity(tab[j][1]&b))%4 for j in range(9))
  Q=tuple(sum(ph.parity(tab[j][1]&cols[k])<<k for k in range(9))for j in range(9))
  need(all(((Q[j]>>k)&1)==((Q[k]>>j)&1)for j in range(9)for k in range(9))and all(alpha[j]%2==((Q[j]>>j)&1)for j in range(9)),'source-compatible symmetricQ/linear parity')
  alias=(('D',Q,alpha),('P',F),('X',b),('phase',gamma))
  need(ph.signature(alias)==sig,'full signed tableau and phase alias equality')
  return alias,sig
 def rot(z,p):
  a,b=z;return ((a,b),(-b,a),(-a,-b),(b,-a))[p%4]
 def column(word,index):
  values={index:(1,0)};den=0
  for e in word:
   op=e[0]
   if op=='P':values={ph.mv(e[1],x):v for x,v in values.items()}
   elif op=='X':values={x^e[1]:v for x,v in values.items()}
   elif op=='D':values={x:rot(v,ph.polynomial(e,x))for x,v in values.items()}
   elif op=='phase':values={x:rot(v,e[1])for x,v in values.items()}
   elif op=='C':
    out=defaultdict(lambda:(0,0));s=e[2];need(s in(-1,1),'sparseGaussian signed primitive')
    for x,(a,b)in values.items():
     for y,v in [(x,(a-s*b,b+s*a)),(x^e[1],(a+s*b,b-s*a))]:
      z=out[y];out[y]=(z[0]+v[0],z[1]+v[1])
    values={x:v for x,v in out.items()if v!=(0,0)};den+=1
   else:raise ValueError('alias primitive')
   while den and all(a%2==0 and b%2==0 for a,b in values.values()):values={x:(a//2,b//2)for x,(a,b)in values.items()};den-=1
  return tuple(sorted(values.items())),den
 groups=[];allalias={};controls=[]
 for gid,(key,rows)in enumerate(bykey.items()):
  rep=rows[0];basis=integer_basis([M[i]for i in rows]);members=[]
  for i in rows:
   # L_i=A_i A_rep^-1; chronological inverse representative THEN A_i.
   left=ph.adjoint(A[rep])+A[i];alias,sig=monomial_alias(left);digest=hashlib.sha256()
   for x in range(512):
    actual=column(left,x);need(actual==column(alias,x),'all512 alias columns');digest.update(json.dumps(actual,separators=(',',':')).encode())
   members.append({'row':i,'L_native_word9':left,'left_monomial_alias_word9':alias,'signed_tableau':sig[0],'anchor_index':next(j for j,z in enumerate(sig[1])if z!=(0,0)),'anchor_gamma':alias[-1][1],'all512_columns_sha256':digest.hexdigest()});allalias[i]=(alias,left,gid)
  groups.append({'group':gid,'representative_row':rep,'rows':rows,'pullbackZ_rref':key,'integer_row_lattice':basis,'members':members})
 need(len(allalias)==112,'every actualrow once')
 # Meaningful controls: right cosets all coincide but do not give left aliases.
 pair=next(((i,j)for i in range(112)for j in range(i)if keys[i]!=keys[j]),None)
 need(pair is not None,'source needs a nontrivial coset control');i,j=pair
 # Name by chronological circuit, to prevent a verbal left/right reversal.
 bad_left=ph.adjoint(A[j])+A[i]
 need(any(ph.pauli(bad_left,0,1<<k)[0]for k in range(9)),'cross-left-class quotient is nonmonomial')
 opposite=A[j]+ph.adjoint(A[i]) # A_i^-1 A_j, always ordinary here
 need(all(not ph.pauli(opposite,0,1<<k)[0]for k in range(9)),'wrong RIGHT-coset grouping would merge these source rows')
 controls.append({'name':'wrong RIGHT cosets collapse allrows and are rejected by actualLEFT alias test','rows':[i,j],'rejected':True})
 need(ph.signature(A[i]+opposite)!=ph.signature(A[j]),'RIGHTalias incorrectlyusedonLEFT cannot reproduce sourceoperator');controls.append({'name':'reversedalias multiplicationorder','rows':[i,j],'rejected':True})
 need(column(A[i],0)==column(A[j],0)and keys[i]!=keys[j],'actualsource impulse-only falsemerge witness');controls.append({'name':'oneimpulse-only grouping merges differentcompleteLEFTclasses','rows':[i,j],'rejected':True})
 first=groups[0]['members'][0];alias=ph.freeze(first['left_monomial_alias_word9']);left=ph.freeze(first['L_native_word9'])
 need(column(alias+(('phase',2),),0)!=column(left,0),'absolute phase alias mutant');controls.append({'name':'alias absolute phase flipped','rejected':True})
 need(ph.signature(A[0])!=ph.signature(ph.adjoint(Kp[0])+(('C',1,1),)),'query orientation mutant');controls.append({'name':'positiveQ substituted for inverseQ or omittedcentralX','rejected':True})
 badM=[row[:]for row in M];mi,mk=next((ii,kk)for ii,row in enumerate(M)for kk,x in enumerate(row)if x);badM[mi][mk]=0
 need(badM!=[[norm['mode_columns'][kk][ii]for kk in range(8)]for ii in range(112)],'dropped M coefficient sourcebindingcontrol');controls.append({'name':'droppedactualnonzero M coefficient','row':mi,'mode':mk,'rejected':True})
 need(Fraction(1,2)!=Fraction(1,2)**2,'exteriorhalf isnot tensoredownercoefficient');controls.append({'name':'tensor exterioronehalf into twocolumns','legal':'1/2','illegal':'1/4','rejected':True})
 need(rot((1,0),4)!=rot((1,0),2),'percolumnphase cannotbe exteriorphase');controls.append({'name':'phase2columnlift replacedby exteriornegativeone','fiberwidth':2,'legal':[1,0],'illegal':[-1,0],'rejected':True})
 one,den=column((('C',1,-1),),0);one=dict(one);aa,bb=one[0],one[1];cross=(aa[0]*bb[0]-aa[1]*bb[1],aa[0]*bb[1]+aa[1]*bb[0])
 need(cross!=(0,0)and cross==(2,0)and den==1,'actualtwo-column inverseQtensor hasmixedoutput');controls.append({'name':'illegal two-termwhole-fieldQshortcut','fiberwidth':2,'mixed_output':[0,1],'actual_numerator':list(cross),'actual_denominator_power2':2,'shortcut_numerator':[0,0],'rejected':True})
 # Each source row basis has exact integer certificates; a changed reconstruction cannot pass.
 g=next(g for g in groups if g['integer_row_lattice']['rank']);bb=g['integer_row_lattice'];bad=[z[:]for z in bb['T']];bad[0][0]+=1
 need(mul(bad,bb['H'])!=[M[i]for i in g['rows']],'reconstruction coefficient mutation');controls.append({'name':'integer reconstruction coefficient changed','rejected':True})
 # Emit one concrete copy-preserving17-owned program.
 ops=[];role={'h':list(range(8)),'y':list(range(8,120)),'b':list(range(120,128)),'query':list(range(128,136)),'rowwork':136};private=list(range(120,137));counts=Counter();addcoeff=Counter();primitive=Counter();unit=half=0
 def lift(word):
  out=[]
  for e in word:
   if e[0]=='P':
    rows=[1<<j for j in range(25)]
    for a0,aa in enumerate(axes):rows[aa]=sum(((e[1][a0]>>b0)&1)<<bb for b0,bb in enumerate(axes))
    out.append(['P',rows])
   elif e[0]=='D':
    qr=[0]*25;lin=[0]*25
    for a0,aa in enumerate(axes):qr[aa]=sum(((e[1][a0]>>b0)&1)<<bb for b0,bb in enumerate(axes));lin[aa]=e[2][a0]
    out.append(['D',qr,lin])
   elif e[0]=='X':out.append(['X',sum(((e[1]>>a0)&1)<<aa for a0,aa in enumerate(axes))])
   elif e[0]=='phase':out.append(list(e))
   else:raise ValueError('noGaussian inmonomiallift')
  return out
 def put(e):
  need(len(ops)<inp['instruction_cap'],'literal instruction cap exceeded; no truncation');ops.append(e);counts[e['op']]+=1
 def clear(dst):put({'op':'CLEAR','dst':dst});put({'op':'ZERO_RETAG','dst':dst,'new_chart':'ambient25_common','premise':'immediately preceding CLEAR'})
 def mono(dst,word,why):
  need(all(e[0]in('P','D','X','phase')for e in word),'monomial alphabet');put({'op':'MONOMIAL','dst':dst,'word9':word,'word25':lift(word),'purpose':why})
  for e in word:primitive[e[0]]+=1
 def add(dst,src,coefficient):
  nonlocal unit,half
  q=Fraction(coefficient);need(q in(Fraction(1),Fraction(-1),Fraction(1,2),Fraction(-1,2)),'literal unit/halfADD only');need(dst!=src,'no selfADD');put({'op':'ADD','dst':dst,'src':src,'coefficient':str(q)});addcoeff[str(q)]+=1
  if abs(q)==1:unit+=1
  else:half+=1
 def scaledadd(dst,src,n,den=1):
  need(den in(1,2),'no odd runtime division');need(abs(n)<=inp['coefficient_cap'],'coefficient cap failure, no alternatebasis/search');sign=1 if n>=0 else-1
  if den==1:
   for _ in range(abs(n)):add(dst,src,sign)
  else:
   for _ in range(abs(n)):add(dst,src,Fraction(sign,2))
 for slot in private:clear(slot)
 for k in range(8):put({'op':'COPY','dst':role['b'][k],'src':role['h'][k],'owned_zero_destination':True});mono(role['b'][k],Km[k],'sourcecommonKm input copy')
 checkpoints=[];C=0
 for g in groups:
  gid,rep=g['group'],g['representative_row'];bb=g['integer_row_lattice'];rank=bb['rank'];H,T=bb['H'],bb['T']
  for l,row in enumerate(H):
   slot=role['query'][l];start=len(ops)
   for k,n in enumerate(row):scaledadd(slot,role['b'][k],n)
   checkpoints.append({'kind':'basis_form','group':gid,'basis':l,'slot':slot,'range':[start,len(ops)],'expected_H_row':row})
   mono(slot,ph.adjoint(Kp[rep]),'representativeKp inverse');put({'op':'GAUSSIAN','dst':slot,'rank':1,'positive_operator':'C1','active_axis25':axes[0],'paid':True});mono(slot,(('X',1),),'positiveQ followedbycentralX givesinverseQ');C+=1
  for rowindex,i in enumerate(g['rows']):
   if not any(M[i]):continue
   work=role['rowwork'];start=len(ops)
   for l,n in enumerate(T[rowindex]):scaledadd(work,role['query'][l],n,2)
   checkpoints.append({'kind':'reconstruction','group':gid,'source_row':i,'slot':work,'range':[start,len(ops)],'expected_T_over2':[str(Fraction(n,2))for n in T[rowindex]]})
   mono(work,allalias[i][0],'phaseboundLEFTalias row'+str(i));add(role['y'][i],work,1);clear(work)
  for l in range(rank):clear(role['query'][l])
 for slot in role['b']:clear(slot)
 need(C==sum(g['integer_row_lattice']['rank']for g in groups)and C<=112,'Gaussian charge is sum ofactual rationalranks')
 # Static typed/lifetime and exact scalar-census replay of the emitted code.
 def audit(program):
  initialized={f:False for f in private};zero={f:False for f in private};seenq=0
  for at,e in enumerate(program):
   op=e['op'];dst=e['dst'];need(dst not in role['h'],'original modeinputs strictly read-only')
   if op=='CLEAR':need(dst in private,'CLEAR only owned');initialized[dst]=True;zero[dst]=True
   elif op=='ZERO_RETAG':need(dst in private and initialized[dst]and zero[dst]and at and program[at-1]['op']=='CLEAR'and program[at-1]['dst']==dst,'retag exactownedzero immediatelyafterCLEAR')
   elif op=='COPY':need(dst in private and initialized[dst]and zero[dst],'COPY only initializedownedzero');need(e['src']in role['h'],'copyactualsource');zero[dst]=False
   elif op=='ADD':
    src=e['src'];need(src!=dst,'distinctADD fields');need(src not in private or initialized[src],'no dirtyownedsource');need(src not in role['query']or not zero[src],'no premature read ofcleared queriedbasis');need(dst not in private or initialized[dst],'no dirtyownedreceiver');need(dst in private or dst in role['y'],'onlydesty orprivatewrite')
    if dst in private:zero[dst]=False
   elif op=='MONOMIAL':need(dst in private and initialized[dst],'monomialonlyinitializedprivate');need(e['word25']==lift(ph.freeze(e['word9'])),'actual25axislift')
   elif op=='GAUSSIAN':need(dst in role['query']and initialized[dst]and e['rank']==1 and e['active_axis25']==axes[0],'actual paidpositivecenterQ');seenq+=1
   else:raise ValueError('literal program alphabet')
  need(all(initialized[f]and zero[f]for f in private),'all17 arbitraryowned returnzero');return seenq
 need(audit(ops)==C,'typedpaid charge')
 target_updates=Counter(e['dst']for e in ops if e['op']=='ADD'and e['dst']in role['y']);need(all(target_updates[role['y'][i]]==int(any(M[i]))for i in range(112)),'all originaly targets updatedonce iff source rownonzero')
 badops=ops[2:] # remove initialCLEAR/retag of b0; its actualCOPY must reject.
 try:audit(badops)
 except ValueError:controls.append({'name':'uncleared arbitraryb0 owned entry','rejected':True})
 else:raise ValueError('dirty ownedcontrolaccepted')
 badops=[dict(e)for e in ops];where=next(j for j,e in enumerate(badops)if e['op']=='MONOMIAL');badops[where]['dst']=role['h'][0]
 try:audit(badops)
 except ValueError:controls.append({'name':'write originalh instead ofownedcopy','rejected':True})
 else:raise ValueError('originalhwritecontrolaccepted')
 where=next(j for j,e in enumerate(ops)if e['op']=='ADD'and e['src']in role['query']);slot=ops[where]['src'];badops=ops[:where]+[{'op':'CLEAR','dst':slot},{'op':'ZERO_RETAG','dst':slot,'premise':'CLEAR'}]+ops[where:]
 try:audit(badops)
 except ValueError:controls.append({'name':'premature queriedbasis CLEAR beforelastread','rejected':True})
 else:raise ValueError('prematureCLEARcontrolaccepted')
 # Check each actual lowered ADD range against its emitted coefficient vector.
 for z in checkpoints:
  size=8 if z['kind']=='basis_form'else groups[z['group']]['integer_row_lattice']['rank'];got=[Fraction(0)]*size;sources=role['b']if z['kind']=='basis_form'else role['query'][:size]
  for e in ops[z['range'][0]:z['range'][1]]:
   need(e['op']=='ADD'and e['dst']==z['slot']and e['src']in sources,'loweredlinearcomb source/slot');got[sources.index(e['src'])]+=Fraction(e['coefficient'])
  expected=[Fraction(x)for x in(z['expected_H_row']if z['kind']=='basis_form'else z['expected_T_over2'])];need(got==expected,'actual unit/half lowerings match certifiedbasis/reconstruction')
 Nrows=sum(any(row)for row in M);Habs=sum(abs(x)for g in groups for row in g['integer_row_lattice']['H']for x in row);Tabs=sum(abs(x)for g in groups for row in g['integer_row_lattice']['T']for x in row)
 need(counts['ADD']==Habs+Tabs+Nrows and unit==Habs+Nrows and half==Tabs,'exactcontractADD census')
 need(counts['CLEAR']==25+C+Nrows and counts['ZERO_RETAG']==25+C+Nrows and counts['COPY']==8 and counts['MONOMIAL']==8+2*C+Nrows,'exactcontractowned/mapcensus')
 scalar=8*unit+10*half+2*counts['COPY']+2*counts['CLEAR']
 program={'schema':'exact-leftcoset-fanout-program/v1','status':'EXACT_COMPONENT_UPPER_PROGRAM','interface':'y112 += q^-1 W h8; h read-only; all137 directions include17arbitraryownedclearedtozero','roles':role,'private_ids':private,'local_axes_25':axes,'source_input_sha256':sha(args.input),'groups':groups,'queries':C,'nonzero_rows':Nrows,'H_abs':Habs,'T_abs':Tabs,'max_H_coefficient':max((abs(x)for g in groups for row in g['integer_row_lattice']['H']for x in row),default=0),'max_T_coefficient':max((abs(x)for g in groups for row in g['integer_row_lattice']['T']for x in row),default=0),'operations':ops,'linear_checkpoints':checkpoints,'runtime_odd_divisions':0,'phase_policy':'Each phase token lifts i^gamma to i^(f*gamma). IntegerH and dyadicT/2 remain exterior scalar coefficients once. No f1Q linear decomposition is used as the field implementation.','proof_factorization':'H=S M, M=T H; A_i=L_i A_rep by allcolumnoperatoridentity. Therefore L_i sum_l(T_il/2)*A_rep(H_l b)=A_i(M_i b/2). b_k=Km_k h_k. All originaly coefficients stayI and owned dirt is CLEARed.','all_width':'Operatorwords equal onall512sourcecolumns, so their prescribed columnwise lifts agree for everyf; tensorwith spectatoridentityonother16axes. Ownerlinearcoefficients are exterior.','ordinary_counts':dict(counts),'ADD_coefficient_census':dict(addcoeff),'monomial_primitive_census':dict(primitive),'scalar_tariff':scalar,'positiveQpaid_profile':{'1':C},'max_norm_SUFFIX_log2_bound':counts['ADD'],'joint_norm_SUFFIX_log2_bound':counts['ADD']+counts['COPY'],'not_admitted':['wholecaller target/price/funding','tape routing/storage/precision/compiler','any optimality outside this fixedcoset-latticegrammar'],'controls':controls}
 dump(args.program,program)
 result={'schema':'exact-fanout-component-result/v1','status':'PASS_EXACT_COMPONENT_QUERY_REDUCTION'if C<112 else'PASS_EXACT_COMPONENT_NO_QUERY_REDUCTION','source_rows':112,'common_modes':8,'leftcoset_count':len(groups),'rationalrank_sum_Qqueries':C,'query_savings_vs112':112-C,'owned_arbitrary':17,'owned_zero_return':17,'all512_alias_columns_checked':112*512,'group_sizes':[len(g['rows'])for g in groups],'group_ranks':[g['integer_row_lattice']['rank']for g in groups],'nonzero_rows':Nrows,'H_abs':Habs,'T_abs':Tabs,'maximum_integer_coefficient_bitlength':max((abs(x).bit_length()for g in groups for key in('H','T')for row in g['integer_row_lattice'][key]for x in row),default=0),'maximum_certificate_integer_bitlength':max((abs(x).bit_length()for g in groups for key in('H','T','S','U','V')for row in g['integer_row_lattice'][key]for x in row),default=0),'runtime_coefficients':'integersandhalvesonly','runtime_odd_divisions':0,'program_counts':dict(counts),'ADD_census':dict(addcoeff),'monomial_primitive_census':dict(primitive),'scalar_tariff':scalar,'controls':controls,'input_sha256':sha(args.input),'program_sha256':sha(args.program),'checker_sha256':sha(Path(__file__)),'oracle_sha256':sha(PH),'scope':'ONE actual112-row sourcefanout LEFTcosetclassification and upperprogram/cost; no native/provider/helper-class census/global/price replay. No newkappa or universalminimum claim.'}
 dump(args.result,result);print(json.dumps({k:result[k]for k in['status','leftcoset_count','rationalrank_sum_Qqueries','query_savings_vs112','program_counts','scalar_tariff','program_sha256']},sort_keys=True))
if __name__=='__main__':main()
