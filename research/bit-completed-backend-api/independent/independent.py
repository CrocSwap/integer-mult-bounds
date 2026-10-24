"""Independent source/operator/typed controls for the bounded4945 API gate.
No A checker, receipt, matcher or price executable is imported as proof.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from hashlib import sha256
import gzip,json,sys
HERE=Path(__file__).resolve().parent

def need(v,m):
 if not v:raise ValueError(m)
def identity(n):return [[Q(i==j)for j in range(n)]for i in range(n)]
def transpose(a):return [list(x)for x in zip(*a)]
def product(a,b):return [[sum((x*y for x,y in zip(row,col)),Q(0))for col in zip(*b)]for row in a]
def invert(a):
 n=len(a);a=[list(map(Q,r))+e for r,e in zip(a,identity(n))]
 for k in range(n):
  p=next((j for j in range(k,n)if a[j][k]),None);need(p is not None,'Invertible actualbasis')
  a[k],a[p]=a[p],a[k];v=a[k][k];a[k]=[x/v for x in a[k]]
  for j in range(n):
   if j!=k:
    v=a[j][k];a[j]=[x-v*y for x,y in zip(a[j],a[k])]
 return [r[n:]for r in a]
def matrix_rank(a):
 a=[list(map(Q,r))for r in a];n=len(a);r=0
 for k in range(len(a[0])):
  p=next((j for j in range(r,n)if a[j][k]),None)
  if p is None:continue
  a[r],a[p]=a[p],a[r];v=a[r][k];a[r]=[x/v for x in a[r]]
  for j in range(r+1,n):
   v=a[j][k];a[j]=[x-v*y for x,y in zip(a[j],a[r])]
  r+=1
  if r==n:break
 return r

def matrix_mod(a,m):return [[int(x.numerator*pow(x.denominator,-1,m)%m)for x in map(Q,r)]for r in a]
def per_column(M,x,f,m):
 return [sum(M[i][j]*x[j*f+c]for j in range(8))%m for i in range(8)for c in range(f)]
def route(M,x,f,m):
 n=8*f;return per_column(M,x[:n],f,m)+list(reversed(per_column(M,list(reversed(x[n:])),f,m)))
def direct_projector(P,x,f,m,wrong_tail=False):
 n=8*f;h=x[:n];d=x[n:]
 def C(a):
  return [a[(7-i)*f+c]for i in range(8)for c in range(f)]if wrong_tail else list(reversed(a))
 ph=per_column(P,h,f,m);pcd=per_column(P,C(d),f,m)
 return [(a-b+c)%m for a,b,c in zip(h,ph,pcd)]+[(a+b-c)%m for a,b,c in zip(d,C(ph),C(pcd))]
def canonical(x,f,m,wrong_tail=False):
 return direct_projector([[int(i==j and i<4)for j in range(8)]for i in range(8)],x,f,m,wrong_tail)
def weighted(x,weights,inverse,m):
 n=len(weights);return [a*(pow(w,-1,m)if inverse else w)%m for a,w in zip(x[:n],weights)]+x[n:]
def source_flow(word,frames):
 N=658;need(len(word['start'])==len(word['final'])==N,'Distinct658originalfields')
 cur=list(word['start'])+[None];bits=[1<<i for i in range(N)]+[0];lease=None;paid=Counter();copies=0
 signed=[{i:1}for i in range(N)]+[{}]
 for e in word['records']:
  need(len(e)==6,'Source literalrecord shape');op,d,s,c,f,_=e
  need(0<=d<N,'Onlyoriginaldestination')
  if op==0:
   need(lease is None and cur[d]==s,'Move currentframe/lifetime')
   low,high=frames[str(s)],frames[str(c)]
   need(high['dim']-low['dim']==f and 0<f<8,'Proper paid MOVE rank')
   need(all(sum(x*y for x,y in zip(u,v))==0 for u in low['B']for v in high['A']),'ActualnestedQQmove')
   cur[d]=c;paid[f]+=1
  elif op==1:
   need(0<=s<=N and s!=d and c in(-1,1),'UnitADDtype')
   need(cur[d]==cur[s]==f,'Commonactualsourceframe')
   need(d!=lease and(s!=N or lease is not None),'Copiedsourceimmutable')
   bits[d]^=bits[s]
   for k,v in tuple(signed[s].items()):
    z=signed[d].get(k,0)+c*v
    if z:signed[d][k]=z
    else:signed[d].pop(k,None)
  elif op==2:
   need(s==N and lease is None and cur[N]is None and not signed[N]and bits[N]==0,'Private658ownedzero')
   need(cur[d]==c and f==0 and frames[str(c)]['dim']==7,'Actualchargedrank7COPY')
   lease=d;cur[N]=0;bits[N]=bits[d];signed[N]=signed[d].copy();copies+=1;paid[7]+=1
  else:
   need(op==3 and s==N and lease==d and cur[d]==c and cur[N]==f,'OwnedCOPYreturntype')
   need(bits[N]==bits[d]and signed[N]==signed[d],'Safeerasurealloriginalcolumns')
   lease=None;cur[N]=None;bits[N]=0;signed[N]={}
 need(cur==word['final']+[None]and lease is None,'Allsourceendpointframes/restoredprivate')
 wanted=[(1<<i)^((1<<(i-111))if 111<=i<222 else 0)for i in range(N)]+[0]
 need(bits==wanted,'All658Booleanoriginalcolumns')
 need(all(signed[i]=={i:1}for i in range(222,N)),'All436independentintegerhelperrows')
 need(copies==9,'AllnineCOPYepisodes')
 return {'original_columns':N,'independent_integer_helpers':436,'helper462_signedrow':signed[462],'owned_COPY_lifetimes':copies,'paid':dict(paid)}
def reject(name,fn,text):
 try:fn()
 except ValueError as e:need(text in str(e),name+' intendedtypegate');return True
 raise ValueError(name+' accepted')
def main():
 for name,h in json.loads((HERE/'CORRECTED-HASHES.json').read_text()).items():need(sha256((HERE/'corrected'/name).read_bytes()).hexdigest()==h,'Reviewedcorrectedfreezebytes')
 bindings=json.loads((HERE/'SOURCE-BINDING.json').read_text())
 for row in bindings['sources']:need(sha256((HERE/row['local']).read_bytes()).hexdigest()==row['sha256'],'Exactsourcebytes')
 word=json.loads(gzip.decompress((HERE/'inputs/WORD.json.gz').read_bytes()));frames=json.loads((HERE/'inputs/frames.json').read_text())['frames'];frame=frames['506']
 need(word['start'][462]==0 and word['final'][462]==506 and frame['dim']==4,'Actual462coldto506rank4')
 B=[[Q(v)for v in r]for r in frame['B']];A=[[Q(v)for v in r]for r in frame['A']]
 need(matrix_rank(B)==matrix_rank(A)==4 and product(B,transpose(A))==[[0]*4 for _ in range(4)],'Actualimage/kernelorthogonalranks')
 S=transpose(B+A);Si=invert(S);Proj=product(product(transpose(B),invert(product(B,transpose(B)))),B)
 Q4=[[Q(i==j and i<4)for j in range(8)]for i in range(8)]
 need(product(product(S,Q4),Si)==Proj and product(Proj,Proj)==Proj and matrix_rank(Proj)==4,'Actualrank4matcherprojector')
 flow=source_flow(word,frames)
 # Treat the author's elementary-factor list only as a proposed witness:
 # independently classify every matrix and multiply the entire right word.
 candidate=json.loads((HERE/'corrected/RESULT.json').read_text())
 factors=[[[Q(x)for x in row]for row in e]for e in candidate['right_route_factors']]
 counts=Counter();current=identity(8);unit_checks=[]
 for E in factors:
  changes=[(i,j)for i in range(8)for j in range(8)if E[i][j]!=int(i==j)]
  if len(changes)==1:
   i,j=changes[0];kind='scale'if i==j else'add'
   if kind=='scale':need(E[i][i]!=0,'Actualfactorunitscale');unit_checks.append(str(E[i][i]))
  else:
   need(len(changes)==4,'Elementaryswapfactor')
   rows=[i for i in range(8)if E[i]!=identity(8)[i]]
   need(len(rows)==2 and E[rows[0]]==identity(8)[rows[1]]and E[rows[1]]==identity(8)[rows[0]],'Actualswapmatrix')
   kind='swap'
  counts[kind]+=1;current=product(current,E)
 need(current==S and counts==Counter({'swap':5,'scale':5,'add':14}),'Independentfullrightfactorwitness')
 need(all(Q(x).numerator%q and Q(x).denominator%q for x in unit_checks for q in(5,7)),'Actualfixtureunitfactors')
 controls={};fixtures=[];columns=0;tail_witness=None
 for f in (1,2):
  n=8*f
  for prime in (5,7):
   m=prime**2
   for variant in (0,1):
    g=identity(8);g[0][1]=variant;h=product(g,S);hi=invert(h);Pg=product(product(g,Proj),invert(g))
    hp,hip,pg=matrix_mod(h,m),matrix_mod(hi,m),matrix_mod(Pg,m)
    for ancestor in (0,1):
     weights=[1+(i+ancestor)%2 for i in range(n)]
     for j in range(2*n):
      v=[int(i==j)for i in range(2*n)];unweighted=weighted(v,weights,True,m)
      actual=weighted(route(hp,canonical(route(hip,unweighted,f,m),f,m),f,m),weights,False,m)
      expected=weighted(direct_projector(pg,unweighted,f,m),weights,False,m)
      need(actual==expected,'Independentlyroutedweightedactualhelperbasiscolumn');columns+=1
      if f==2 and tail_witness is None:
       bad=weighted(route(hp,canonical(route(hip,unweighted,f,m),f,m,True),f,m),weights,False,m)
       if bad!=expected:tail_witness={'f':f,'prime':prime,'cover_variant':variant,'ancestor':ancestor,'basis_column':j,'first_different_coordinate':next(k for k,(x,y)in enumerate(zip(bad,expected))if x!=y)}
     fixtures.append({'f':f,'prime':prime,'cover_variant':variant,'ancestor':ancestor,'columns':2*n})
 need(columns==384 and len(fixtures)==16,'Full384columns16physicalfixtures')
 need(tail_witness is not None,'Wrongtailactualoperatorfailure');controls['wrong_column_tail_endpoint']=tail_witness
 # Independent actual nonzero q-adic carry and illegal fresh-row weight.
 carry_witnesses=[]
 for q in (5,7):
  modulus=q*q;low=identity(8);low[0][1]=1
  lifted=[[int(x)for x in row]for row in low];lifted[1][0]+=q
  Sm=matrix_mod(S,modulus);Sl=matrix_mod(S,q)
  mapped=product(lifted,Sm);lowproduct=product(low,Sm)
  h0=[[int(x)%q for x in row]for row in lowproduct]
  carry=[[(int(lowproduct[i][j])-h0[i][j])//q%q for j in range(8)]for i in range(8)]
  highlinear=[[Sl[0][j]if i==1 else 0 for j in range(8)]for i in range(8)]
  rebuilt=[[(h0[i][j]+q*(highlinear[i][j]+carry[i][j]))%modulus for j in range(8)]for i in range(8)]
  need(matrix_mod(mapped,modulus)==rebuilt,'Independentactualhighcarryformula')
  witness=next((i,j,int(carry[i][j]))for i in range(8)for j in range(8)if carry[i][j])
  carry_witnesses.append({'prime':q,'nonzero_carry':witness})
 controls['drop_actual_high_carry']=carry_witnesses
 g=identity(8);g[0][1]=1;h=product(g,S)
 fresh=lambda x:1+int(x[0][1]==0)
 need(fresh(g)!=fresh(h),'FreshROWweightactualcommutator')
 controls['fresh_ROW_weight']={'input_weight':fresh(g),'routed_weight':fresh(h),'nonzero_head_coordinate':1}

 # Sameactualprojector replacementwithout paidmatcher mustfail.
 m=25;Pm=matrix_mod(Proj,m)
 controls['omit_matcher']=next(j for j in range(16)if canonical([int(i==j)for i in range(16)],1,m)!=direct_projector(Pm,[int(i==j)for i in range(16)],1,m))
 # Independent 2x2 point-action weighted leaf, no matrix product copy.
 weighted_fixtures=[]
 for prime in (5,7):
  for a in (2,3):
   m=prime**2
   for x,y in ((1,0),(0,1)):
    h,d=x,y
    for typ,value in [('J',0),('L',a),('J',0),('L',-pow(a,-1,m)),('J',0),('L',a),('J',0),('sign',0)]:
     if typ=='J':h,d=d,h
     elif typ=='L':d=(d+value*h)%m
     else:d=-d%m
    need((h%m,d%m)==(a*y%m,pow(a,-1,m)*x%m),'Actual4swapweightedleafbasis')
   weighted_fixtures.append({'prime':prime,'unit':a,'ordinary_calls':4})
 # Source-typed negativepadding: different oddinternalradices, true atomC_n.
 padding=[]
 for genuine,inner,digits in ((25,7,2),(49,5,3)):
  pad=1<<(genuine-1).bit_length();need(pad<2*genuine,'Binarypositivepaddingvolume')
  def rev(x):
   out=0
   for k in range(digits):out=out*inner+(x//(inner**k))%inner
   return out
  x=next(i for i in range(genuine)if rev(i)>=genuine)
  need(rev(x)<inner**digits,'Typedrawradixreversalrange')
  padding.append({'genuine':genuine,'binary_pad':pad,'inner_prime':inner,'inner_digits':digits,'inner_complete_range':inner**digits,'raw_source_coordinate':x,'raw_reversed_coordinate':rev(x),'paired_binary_factor':str(Q(pad**2,genuine**2))})
 controls['premature_unpad_source_typed_radix']=padding
 # Actualsource/type/ownership mutations, not arithmetic receipt changes.
 bad=json.loads(json.dumps(word));i=next(i for i,e in enumerate(bad['records'])if e[0]==2);bad['records'][i][2]=657
 controls['borrowed_receiver_for_ownedCOPY']=reject('borrowedCOPY',lambda:source_flow(bad,frames),'Private658ownedzero')
 controls['fake_rank8_credit']=reject('rankpromotion',lambda:need(matrix_rank(Proj)==8,'Actualhelperrank4'), 'Actualhelperrank4')
 bad=json.loads(json.dumps(word));bad['final'][462]=1
 controls['wrong_actual_exitframe']=reject('wrongframe',lambda:source_flow(bad,frames),'Allsourceendpointframes')
 # Physicalowner namespace controls remain types, not nativeROWimplementation.
 def type_slots(H,D,outer,inner):need(len({H,D,outer,inner})==4,'Independentargument/ROWphysicalslots')
 type_slots('H','D','outerROW','innerROW')
 controls['conflated_two_ROW_slots']=reject('ROWalias',lambda:type_slots('H','D','outerROW','outerROW'),'Independentargument/ROWphysicalslots')
 # A source hash corruption is rejected before any projector execution.
 h=sha256((HERE/'inputs/frames.json').read_bytes()).hexdigest();b=bytearray((HERE/'inputs/frames.json').read_bytes());b[-1]^=1
 controls['sourcebyte_mutation']=reject('bytes',lambda:need(sha256(b).hexdigest()==h,'Exactsourcebytes'),'Exactsourcebytes')
 result={'status':'PASS_INDEPENDENT4945_SOURCE_OPERATOR_FIXTURE_REVIEW','source_heads':['ecdfcabd56dfa663ae020733f9f1a88c6644743c','f56ae4533a7d97d782a2c596a33fe844cd051747'],'source_binding':{'helper':462,'start':0,'finish':506,'rank':4,'five_common4760_4814_inputs_equal':True},'projector':[[str(x)for x in r]for r in Proj],'matcher':[[str(x)for x in r]for r in S],'matcher_inverse':[[str(x)for x in r]for r in Si],'source_flow':flow,'actual_right_factor_counts':dict(counts),'actual_scaling_units':unit_checks,'selected_pair_ledger_corollary':{'ordinary':8*2*counts['swap'],'scalings':8*2*counts['scale'],'linear_shifts':8*2*counts['add'],'carry_shifts_upper':128,'low_type_permutations':2},'source_operator_fixtures':fixtures,'weighted_leaf_fixtures':weighted_fixtures,'padding_fixtures':padding,'fixtures_total':len(fixtures)+len(weighted_fixtures)+len(padding),'actual_basis_columns':columns,'independent_controls':controls,'allwidth_scope':'Rationaloperatoridentity/sourcepremises; fixturescorroborate. NativeROW/tape/compilerremaininherited; nofullbackendAPIclaim.','A_checker_or_result_imported':False,'new_kappa':None}
 print(json.dumps(result,indent=2))
 if '--emit'in sys.argv:(HERE/'INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
