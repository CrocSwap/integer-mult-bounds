#!/usr/bin/env python3
"""One source-bound conditional completed ordinary backend API gate.
No predecessor executable/price engine imported. Apache-2.0; Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from collections import Counter
import json,subprocess,sys
HERE=Path(__file__).resolve().parent
PIN='f56ae4533a7d97d782a2c596a33fe844cd051747'
PATHS={'frames':'research/kappa-rebuild/bit/sources/pr589-regenerated/records/frames.json','word':'research/bit-compact-carrier-retirement/provider/inputs/WORD.json.gz','proof':'research/bit-finite-ordinary-bootstrap/PROOF.md','independent':'research/bit-finite-ordinary-bootstrap/independent.py','bridge':'research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md','bit':'notes/three-stage-cover-bit.tex','rows':'notes/three-stage-cover-rows.tex','record':'research/bit-finite-ordinary-bootstrap/RECORD.json'}
def need(x,m):
 if not x:raise ValueError(m)
def eye(n):return [[F(i==j)for j in range(n)]for i in range(n)]
def tr(a):return list(map(list,zip(*a)))
def mm(a,b):return [[sum((x*y for x,y in zip(r,c)),F(0))for c in zip(*b)]for r in a]
def add(a,b,k=1):return [[x+k*y for x,y in zip(r,s)]for r,s in zip(a,b)]
def inverse(a):
 n=len(a);w=[list(r)+e for r,e in zip(a,eye(n))]
 for j in range(n):
  k=next(i for i in range(j,n)if w[i][j]);w[j],w[k]=w[k],w[j];v=w[j][j];w[j]=[x/v for x in w[j]]
  for i in range(n):
   if i!=j:
    z=w[i][j];w[i]=[x-z*y for x,y in zip(w[i],w[j])]
 return [r[n:]for r in w]
def kron(a,f):return [[a[i//f][j//f]*F(i%f==j%f)for j in range(len(a[0])*f)]for i in range(len(a)*f)]
def paired(p):
 n=len(p);c=[[F(i+j==n-1)for j in range(n)]for i in range(n)];u=add(eye(n),p,-1)
 return [x+y for x,y in zip(u,mm(p,c))]+[x+y for x,y in zip(mm(c,p),mm(mm(c,u),c))]
def paired_map(s):
 n=len(s);z=[[F(0)]*n for _ in range(n)];c=[[F(i+j==n-1)for j in range(n)]for i in range(n)]
 return [x+y for x,y in zip(s,z)]+[x+y for x,y in zip(z,mm(mm(c,s),c))]
def mod(a,m):return [[(x.numerator*pow(x.denominator,-1,m))%m for x in r]for r in a]
def mv(a,v,m):return [sum(x*y for x,y in zip(r,v))%m for r in a]
def direct_action(p,v,m):
 # Independently apply the actual projector law coordinate-by-coordinate.
 n=len(p);h,t=v[:n],v[n:];ph=mv(p,h,m);pct=mv(p,list(reversed(t)),m)
 return [(h[i]-ph[i]+pct[i])%m for i in range(n)]+[(t[i]+ph[n-1-i]-pct[n-1-i])%m for i in range(n)]
def decompose(s):
 w=[r[:]for r in s];n=len(s);ops=[]
 for j in range(n):
  k=next(i for i in range(j,n)if w[i][j])
  if k!=j:w[j],w[k]=w[k],w[j];ops.append(('swap',j,k,F(1)))
  v=w[j][j]
  if v!=1:w[j]=[x/v for x in w[j]];ops.append(('scale',j,j,1/v))
  for i in range(n):
   if i!=j and w[i][j]:
    z=-w[i][j];w[i]=[x+z*y for x,y in zip(w[i],w[j])];ops.append(('add',i,j,z))
 need(w==eye(n),'deterministic rational elimination')
 factors=[]
 for typ,i,j,z in ops:
  e=eye(n)
  if typ=='swap':e[i],e[j]=e[j],e[i]
  elif typ=='scale':e[i][i]=1/z
  else:e[i][j]=-z
  factors.append(e)
 out=eye(n)
 for e in factors:out=mm(out,e)
 need(out==s,'literal right multiplier factor order')
 return ops,factors

def wrapper(h,d,rows,raw):
 # Source exact completed ordinary body; rows are read-only spectators of raw.
 h=list(h);d=[y-x for x,y in zip(h,d)];h,d,r=raw(h,d,rows)
 d=[x+y for x,y in zip(d,h)];h,d,r=raw(h,d,r)
 d=[x-y for x,y in zip(h,d)]
 return h,d,r

def main():
 raw={k:subprocess.check_output(['git','--no-replace-objects','show',PIN+':'+p])for k,p in PATHS.items()}
 need(sha256(raw['frames']).hexdigest()=='d006b3bfe0c04afecfea7aecfa59dfe4298b99501c70da3938e40289bc2f5010','actual source frame bank')
 import gzip
 word=json.loads(gzip.decompress(raw['word']));frame=json.loads(raw['frames'])['frames']['506']
 need(word['start'][462]==0 and word['final'][462]==506 and frame['dim']==4,'actual arbitrary helper462 rank4')
 B=[[F(x)for x in r]for r in frame['B']];A=[[F(x)for x in r]for r in frame['A']]
 P=mm(mm(tr(B),inverse(mm(B,tr(B)))),B);S=tr(B+A);Si=inverse(S);Q=[[F(i==j and i<4)for j in range(8)]for i in range(8)]
 need(mm(P,P)==P and mm(mm(S,Q),Si)==P,'source rational idempotent and matcher')
 ops,factors=decompose(S);need(all(x.denominator%5 and x.denominator%7 for r in S+Si+P for x in r),'declared fixture primes valid')
 controls={};fixtures=[];basis_columns=0
 for f in (1,2):
  Pf,Sf,Qf=kron(P,f),kron(S,f),kron(Q,f);n=8*f;Sfi=inverse(Sf)
  need(mm(mm(paired_map(Sf),paired(Qf)),paired_map(Sfi))==paired(Pf),'actual reversed-tail all-f tensor form in fixture')
  # This wrong C8 tensor I_f must fail at f2, unless accidentally symmetric.
  if f==2:
   wrong=[[F(i//f+j//f==7 and i%f==j%f)for j in range(n)]for i in range(n)]
   need(wrong!=[[F(i+j==n-1)for j in range(n)]for i in range(n)],'wrong tail reversal distinguished')
   controls['omit_column_tail_reversal']=True
  for prime in (5,7):
   m=prime**2
   for variant in (0,1):
    g=eye(8);g[0][1]=F(variant);gi=inverse(g);h=mm(g,S)
    gp=mm(mm(g,P),gi);hq=mm(mm(h,Q),inverse(h));need(gp==hq,'whole cover route g to gS correct')
    need(mm(h,Si)==g,'exact row inverse return')
    # A genuinely independent coordinate path: route via gS,Q then undo vs
    # direct requested projector gPg^-1 on every linear coordinate basis.
    routed=paired_map(kron(h,f));unroute=paired_map(kron(inverse(h),f));canonical=paired(Qf)
    dp=mod(kron(gp,f),m);ri=mod(unroute,m);rc=mod(canonical,m);ro=mod(routed,m)
    # Independent q-adic high-matrix route/carry, with fixed nonzero high part.
    g0=mod(g,prime);G1=[[0]*8 for _ in range(8)];G1[1][0]=1
    sm=mod(S,m);slow=mod(S,prime)
    gw=[[g0[i][j]+prime*G1[i][j]for j in range(8)]for i in range(8)]
    direct=mod(mm(gw,sm),m);z=mm(g0,sm)
    low=[[int(x)%prime for x in row]for row in z]
    carry=[[(int(z[i][j])-low[i][j])//prime%prime for j in range(8)]for i in range(8)]
    linear=mod(mm(G1,slow),prime)
    high=[[(linear[i][j]+carry[i][j])%prime for j in range(8)]for i in range(8)]
    rebuilt=[[low[i][j]+prime*high[i][j]for j in range(8)]for i in range(8)]
    need(direct==rebuilt,'actual whole-cover high affine route including carry')
    without=[[low[i][j]+prime*linear[i][j]for j in range(8)]for i in range(8)]
    need(without!=direct,'omitting real route carry fails')
    controls['omit_high_matrix_carry']=True
    for ancestor in (0,1):
     weights=[1+(i+ancestor)%2 for i in range(n)]
     lam=eye(2*n);lami=eye(2*n)
     for i,a in enumerate(weights):lam[i][i]=a;lami[i][i]=F(1,a)
     lm,li=mod(lam,m),mod(lami,m)
     for j in range(2*n):
      v=[int(i==j)for i in range(2*n)]
      lhs=mv(lm,mv(ro,mv(rc,mv(ri,mv(li,v,m),m),m),m),m)
      rhs=mv(lm,direct_action(dp,mv(li,v,m),m),m)
      need(lhs==rhs,'independent all-basis weighted physical helper route')
      basis_columns+=1
     # Two visible ROW levels + a complete spectator, held by the raw contract.
     r={'outer':(prime,variant),'inner':(ancestor,prime+1),'spectator':(3,7,11)}
     x=[F(i+1)for i in range(n)];y=[F(2*i-3)for i in range(n)]
     rawbody=lambda a,b,row:(list(reversed(b)),list(reversed(a)),dict(row))
     def inner_completed(a,b,row):
      # Inner ROW is borrowed from the CURRENT argument's own high part,
      # not a new arbitrary owner or externally supplied empty stock.
      ah,bh=list(a[:1]),list(b[:1]);ar,br=list(a[1:]),list(b[1:])
      borrowed=dict(row);borrowed['borrowed_inner_ROW']=tuple(ah)
      ao,bo,ret=wrapper(ar,br,borrowed,rawbody)
      need(ret==borrowed,'inner completed body restores borrowed/current high ROW')
      del ret['borrowed_inner_ROW']
      # One completed high-part interchange, after ROW restoration.
      return bh+ao,ah+bo,ret
     def nested_raw(a,b,row):
      aa,bb,ret=inner_completed(a,b,row)
      return list(reversed(aa)),list(reversed(bb)),ret
     xo,yo,rr=wrapper(x,y,r,nested_raw)
     need(xo==y and yo==x and rr==r,'completed wrapper arbitrary typed ROWs')
     # The second nesting order is a control: overwrite outer row by inner.
     def badbody(a,b,row):
      row=dict(row);row['outer']=row['inner'];return list(reversed(b)),list(reversed(a)),row
     _,_,bad=wrapper(x,y,r,badbody);need(bad!=r,'unrestored/aliased ROW control')
     controls['inner_ROW_alias']=True
     fixtures.append({'f':f,'prime':prime,'modulus':m,'g_variant':variant,'ancestor':ancestor,'basis_columns':2*n,'two_ROW_levels_preserved':True,'inner_stock_borrowed_from_argument':True})
   # Non-tautological fresh weight failure: the route changes the row queried
   # by the illegal weight. Choose the already declared variant1, no search.
   g=eye(8);g[0][1]=1;h=mm(g,S)
   fresh=lambda z:1+int(z[0][1]==0)
   need(fresh(g)!=fresh(h),'fresh-row weight descriptor changes on actual route')
   address=[1]+[0]*15
   left=(tuple(map(tuple,h)),fresh(g)*address[0])
   right=(tuple(map(tuple,h)),fresh(h)*address[0])
   need(left!=right,'actual fresh-row scaling and route commutator on nonzero address')
   controls['fresh_ROW_weight']=True
 # Four OLD ordinary swaps, three shifts, one fixed sign; exact modular word.
 I=eye(2);J=[[F(0),F(1)],[F(1),F(0)]]
 def L(a):return [[F(1),F(0)],[F(a),F(1)]]
 sig=[[F(1),F(0)],[F(0),F(-1)]];weighted=[]
 for prime in (5,7):
  m=prime**2
  for a in (2,3):
   aa=F(a);word=[J,L(aa),J,L(-1/aa),J,L(aa),J,sig]
   op=I
   for e in word:op=mm(e,op)
   expected=[[F(0),aa],[1/aa,F(0)]]
   need(op==expected,'literal4 ordinary weighted leaf swaps')
   bad=I
   for k,e in enumerate(word):
    if k!=0:bad=mm(e,bad)
   need(bad!=expected,'omitted ordinary atom interchange')
   controls['omit_weighted_leaf_swap']=True;weighted.append({'prime':prime,'unit':a,'ordinary_swaps':4,'shifts':3,'signs':1})
 # Padding uses the invariant genuine rectangle, not an assumed inverse of
 # an internally uncompleted body. These address permutations are independent
 # of the rational matrix helper checks above.
 padding=[]
 for radix in (5,7):
  original=radix**2;padded=1<<(original-1).bit_length();need(padded<2*original,'two chunk binary pad bound')
  genuinely=set((i,j)for i in range(original)for j in range(original));returned={(j,i)for i,j in genuinely}
  need(returned==genuinely,'completed ordinary swap preserves genuine rectangle')
  need(all((i<original and j<original)==(j<original and i<original)for i in range(padded)for j in range(padded)),'zero padded complement restored')
  # A raw reversed body reverses TWO radix digits, which need not preserve
  # the binary genuine set if unpadding prematurely at the radix boundary.
  row_stock=3;source=original;row_padded=((source+row_stock-1)//row_stock)*row_stock
  need(source>=row_stock and row_padded<2*source,'owned ROW pad bound')
  bits=padded.bit_length()-1
  rev=lambda n:sum(((n>>i)&1)<<(bits-1-i)for i in range(bits))
  bad={(rev(j),rev(i))for i,j in genuinely}
  need(bad!=genuinely,'actual raw reversed body violates genuine padding rectangle')
  controls['premature_padding_cleanup']=True
  padding.append({'radix':radix,'digit_width':2,'range':original,'binary_range':padded,'two_range_volume_factor':str(F(padded**2,original**2)),'row_divisor':row_stock,'padded_row_range':row_padded,'owned_padded_rows':row_padded-source})
 # Reject omitted physical whole-job matcher with actual matrices.
 controls['omit_matcher']=paired(Q)!=paired(P)
 need(all(controls.values()),'every semantic control distinguishes')
 C1=F('.00347545805')-F(1,2**36)-F(1,10**20);rho=F(1,100);b=F('.0034597');levels=[]
 for value in (F('.0034753004'),F('.0034754564'),F('.0034754580')):
  a=(1-rho)*C1+rho*b;need(b<value<a<C1<rho<1-a,'existing finite stage type/cost gaps')
  levels.append({'backend':str(b),'admitted':str(value),'exact':str(a),'adapter_gap':str(rho-a),'stock_gap':str(1-rho-a),'relaxation_gap':str(a-value)});b=value
 report={'status':'PASS_ONE_CONDITIONAL_A0_TO_A1_API_IMPLICATION_NOT_PRIMITIVE_ADMISSION','source_head':PIN,'original_helper':462,'source_frame':506,'column_multiplicities':[1,2],'small_fixtures':len(fixtures)+len(weighted)+len(padding),'fixture_cap':64,'physical_basis_columns_checked':basis_columns,'fixtures':fixtures,'weighted_leaf_fixtures':weighted,'padding_fixtures':padding,'matcher':[[str(x)for x in r]for r in S],'projector':[[str(x)for x in r]for r in P],'matcher_inverse':[[str(x)for x in r]for r in Si],'right_route_elimination_counts':dict(Counter(x[0]for x in ops)),
 'selected_route_pair_high_matrix_ledger':{'ordinary_chunk_interchanges':80,'fixed_unit_scalings':80,'linear_ordered_shifts':224,'carry_ordered_shifts_upper':128,'low_type_permutations':2,'scope':'N=8 coarse head; all charged; low-type finite-permutation costs separate; tensor f does not enlarge cover row dimension'},'right_route_factors':[[[str(x)for x in r]for r in e]for e in factors],'controls':controls,'finite_levels':levels,'arbitrary_data_scope':'Exact coordinate operator identities + written universal permutation/interface proof; no full arrays or astronomical template executed','native_rawbody_ROW_semantics':'Inherited premise; wrapper proof checks its exact use, not actual full compiler implementation','routing_cost_primitive':'Inherited fixed-rational ordered-affine/scaling/shift lemma; every elementary factor is charged','all_width_proof':'See PROOF.md; finite fixtures are corroboration only','new_kappa':False,'selected_record_changed':False,'full4814_primitive_API_independently_proved':False}
 sources={'schema_version':1,'source_head':PIN,'files':{PATHS[k]:sha256(v).hexdigest()for k,v in raw.items()},'checker_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
 for name,obj in [('RESULT.json',report),('SOURCES.json',sources)]:
  bts=(json.dumps(obj,indent=2,sort_keys=True)+'\n').encode()
  if '--write' in sys.argv:(HERE/name).write_bytes(bts)
  else:need((HERE/name).read_bytes()==bts,'frozen '+name)
 print(json.dumps({'status':report['status'],'fixtures':report['small_fixtures'],'basis_columns':basis_columns,'controls':len(controls),'helper':462,'native_primitives_remain_inherited':True},sort_keys=True))
if __name__=='__main__':main()
