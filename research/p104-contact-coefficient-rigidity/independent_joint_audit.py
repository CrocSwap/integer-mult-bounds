#!/usr/bin/env python3
"""Independent exact deletion10947 plus two-coefficient obstruction audit.

Jerry Chen / @CubeJerry, with substantial OpenAI assistance; Apache-2.0.
Native word and previous construction retain the credited P104 authorship.
No primary or gauge-lab code, frozen equations, or determinants are imported.
Native event semantics are independently adapted from this worker's earlier
prefix/adjoint and full-matrix audit. All proof-relevant arithmetic is rational.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import argparse,gzip,json,hashlib,time,math

DELETED=10947
PAYLOAD='d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821'

def need(ok,msg):
 if not ok:raise ValueError(msg)

def axpy(row,other,q=Q(1)):
 if not q:return
 for j,v in other.items():
  row[j]=row.get(j,Q(0))+q*v
  if not row[j]:del row[j]

def coef(e):return Q(e[2]if e[0]=='SCALE'else e[3])
def source(e):return e[1]if e[0]=='SCALE'else e[2]
def scalar(e):return e[0]in('ADD','COPY','SCALE')
def dot(a,b):return sum((x*b.get(j,Q(0))for j,x in a.items()),Q(0))
def normal(x):
 if not x:return None
 s=x[min(x)];return tuple((j,z/s)for j,z in sorted(x.items()))
def step(rows,e):
 op,r=e[:2]
 if op=='ADD':axpy(rows[r],rows[e[2]],coef(e))
 elif op=='COPY':rows[r]={j:coef(e)*z for j,z in rows[e[2]].items()if coef(e)*z}
 elif op=='SCALE':rows[r]={j:coef(e)*z for j,z in rows[r].items()if coef(e)*z}
 elif op in('INIT','CLEAR'):rows[r]={}

def inverse_full(matrix):
 n=len(matrix);a=[dict(row)for row in matrix];b=[{i:Q(1)}for i in range(n)];det=Q(1)
 for j in range(n):
  pivot=next((i for i in range(j,n)if a[i].get(j)),None)
  need(pivot is not None,'Deleted-word public matrix is invertible')
  if pivot!=j:a[j],a[pivot]=a[pivot],a[j];b[j],b[pivot]=b[pivot],b[j];det=-det
  s=a[j][j];det*=s;a[j]={k:z/s for k,z in a[j].items()};b[j]={k:z/s for k,z in b[j].items()}
  for i in range(n):
   if i==j:continue
   s=a[i].get(j,Q(0))
   if s:axpy(a[i],a[j],-s);axpy(b[i],b[j],-s)
 need(a==[{i:Q(1)}for i in range(n)],'Full inverse elimination completed')
 return b,det

def quotient(vector,target):
 # vector = coefficient*target + scale*canonical_quotient_direction.
 k=min(target);coefficient=vector.get(k,Q(0))/target[k];r=dict(vector);axpy(r,target,-coefficient)
 if not r:return None,Q(0),coefficient
 s=r[min(r)];return normal(r),s,coefficient

def spans_target(first,second):
 a,sa,ta=first;b,sb,tb=second
 if a is None and b is None:return bool(ta or tb)
 if a is None:return bool(ta)
 if b is None:return bool(tb)
 return a==b and sb*ta-sa*tb!=0

def reduce_equations(equations):
 # Rows are [x coefficient,y coefficient,Z coefficient,constant].
 piv={}
 for src in equations:
  row=list(src)
  for k,old in sorted(piv.items()):
   if row[k]:
    q=row[k];row=[a-q*b for a,b in zip(row,old)]
  k=next((j for j in range(3)if row[j]),None)
  if k is None:
   if row[3]:return None
   continue
  q=row[k];row=[x/q for x in row]
  for j,old in list(piv.items()):
   if old[k]:
    q=old[k];piv[j]=[a-q*b for a,b in zip(old,row)]
  piv[k]=row
 return sorted(piv.items())

def reduce_vector(row,pivots):
 row=list(row)
 for k,old in pivots:
  if row[k]:
   q=row[k];row=[a-q*b for a,b in zip(row,old)]
 return row

def polynomial_closure(equations,determinant):
 reduced=reduce_equations(equations)
 if reduced is None:return 'linear_inconsistent',None
 remainder=reduce_vector(determinant,reduced)
 if not any(remainder):return 'linear_determinant_span',reduced
 k=len(reduced)
 if k==1:
  row=reduced[0][1];f1,f2,f3,f0=row;d1,d2,d3,d0=determinant
  if f2 or f3:
   numerator=[d0*f2-d2*f0,d0*f3+d1*f2-d2*f1-d3*f0,d1*f3-d3*f1]
   need(not any(numerator),'Nonzero determinant on bilinear C1 component')
   if f3:
    root=-f2/f3
    if f0+f1*root==0:
     need(d0+d1*root==d2+d3*root==0,'Exceptional vertical C1 component')
   return ('coordinate_y_identity' if f1==f3==0 else 'bilinear_identity'),reduced
  need(f1!=0,'Unexpected constant-only C1 equation')
  root=-f0/f1
  need(d0+d1*root==d2+d3*root==0,'Linear-x C1 component')
  return 'coordinate_x_identity',reduced
 if k==2:
  free=next(j for j in range(3)if j not in{q for q,row in reduced})
  constant=[Q(0)]*3;slope=[Q(0)]*3;slope[free]=Q(1)
  for q,row in reduced:constant[q]=-row[3];slope[q]=-row[free]
  a,b,c=constant;u,v,z=slope
  g=[c-a*b,z-a*v-b*u,-u*v]
  ell0=determinant[3]+sum(determinant[j]*constant[j]for j in range(3));ell1=sum(determinant[j]*slope[j]for j in range(3))
  if not g[2]:
   if not g[1]:
    if g[0]:return 'no_nonlinear_solution',reduced
    need(ell0==ell1==0,'Affine line determinant identity');return 'affine_line_identity',reduced
   roots=[-g[0]/g[1]]
  else:
   disc=g[1]*g[1]-4*g[2]*g[0]
   if disc<0:return 'no_rational_quadratic_root',reduced
   aa,bb=math.isqrt(disc.numerator),math.isqrt(disc.denominator)
   if aa*aa!=disc.numerator or bb*bb!=disc.denominator:return 'no_rational_quadratic_root',reduced
   sq=Q(aa,bb);roots=[(-g[1]+sq)/(2*g[2]),(-g[1]-sq)/(2*g[2])]
  need(all(ell0+ell1*t==0 for t in roots),'Rational C1 root has nonzero determinant')
  return 'affine_parameter_roots',reduced
 if k==3:
  point=[Q(0)]*3
  for j,row in reduced:point[j]=-row[3]
  if point[2]!=point[0]*point[1]:return 'no_nonlinear_solution',reduced
  need(sum(determinant[j]*point[j]for j in range(3))+determinant[3]==0,'C1 point has nonzero determinant')
  return 'isolated_point',reduced
 raise ValueError('Unconstrained C1 system')

def direct_rank_and_null(matrix):
 piv={};order=[];product=Q(1);n=len(matrix)
 for original in matrix:
  row=dict(original)
  for j,old in sorted(piv.items()):
   if row.get(j):axpy(row,old,-row[j])
  if not row:continue
  j=min(row);scale=row[j];product*=scale;piv[j]={k:z/scale for k,z in row.items()};order.append(j)
 if len(piv)==n:
  inversions=sum(order[i]>order[j]for i in range(n)for j in range(i+1,n))
  return n,product*(-1 if inversions%2 else 1),{}
 free=min(set(range(n))-set(piv));vector={free:Q(1)}
 for j,row in sorted(piv.items(),reverse=True):
  z=-sum(a*vector.get(k,Q(0))for k,a in row.items()if k!=j)
  if z:vector[j]=z
 need(vector and all(dot(row,vector)==0 for row in matrix),'Direct full-matrix null vector')
 return len(piv),Q(0),vector

def literal_controls(program,n,nn,T0,A,prefix,suffix,transfers,pairs,residual,diag,qu,Kbar,Rbar):
 def replay(changes):
  rows=[{r:Q(1)}if r<n else{}for r in range(nn)]
  for i,original in enumerate(program):
   if i==DELETED:continue
   event=list(original)
   if i in changes:event[2 if event[0]=='SCALE'else 3]=str(coef(event)+changes[i])
   step(rows,event)
  return rows[:n]
 def predicted(a,b,x,y,tau):
  out=[dict(row)for row in T0]
  for u,v,q in ((suffix[a],prefix[a],x),(suffix[b],prefix[b],y),(suffix[b],prefix[a],x*y*tau)):
   for r,z in u.items():axpy(out[r],v,q*z)
  return out
 chosen=[]
 for typ in ('COPY','SCALE','ADD'):
  pair=next(((a,b)for a,b in pairs if typ in(program[a][0],program[b][0])and suffix[b]and prefix[a]),None)
  if pair is not None and pair not in chosen:chosen.append(pair)
 mixed=next(((a,b)for a,b in pairs if transfers[a,b]and suffix[b]and prefix[a]),None)
 if mixed is not None and mixed not in chosen:chosen.append(mixed)
 identities=[];corruption_checked=False
 for a,b in chosen:
  x,y=Q(2,3),Q(-5,7);actual=replay({a:x,b:y});expected=predicted(a,b,x,y,transfers[a,b]);need(actual==expected,'Literal complete two-update expansion')
  rank,det,_=direct_rank_and_null(actual);dab=dot(prefix[a],qu[b]);dba=dot(prefix[b],qu[a]);D=1+diag[a]*x+diag[b]*y+(diag[a]*diag[b]-dab*dba+transfers[a,b]*dab)*x*y
  need(det==D,'Direct determinant agrees with independently derived polynomial')
  if not corruption_checked:
   need(actual!=predicted(a,b,x,y,transfers[a,b]+1),'Corrupted transfer must change literal expansion');corruption_checked=True
  identities.append({'a':a,'b':b,'opcodes':[program[a][0],program[b][0]],'changes':[x,y],'mixed_transfer':transfers[a,b],'rank':rank,'direct_determinant':det})
 selected=[]
 for kind in ('coordinate_x_identity','coordinate_y_identity'):
  candidates=[case for case in residual if case['class']==kind]
  for category in ('ADD','SCALE'):
   case=next((case for case in candidates if category in(program[case['a']][0],program[case['b']][0])),None)
   if case is not None and(case['a'],case['b'])not in{(z['a'],z['b'])for z in selected}:selected.append(case)
 singular=[]
 for case in selected:
  a,b=case['a'],case['b'];row=list(map(Q,case['equations'][0]));x=y=Q(2,3)
  if row[0]:x=-row[3]/row[0]
  else:y=-row[3]/row[1]
  need(x and y,'Genuine two nonzero coefficient changes in literal control')
  actual=replay({a:x,b:y});need(actual==predicted(a,b,x,y,transfers[a,b]),'C1 sample literal two-update expansion')
  need(all({j:z for j,z in actual[i].items()if j in Kbar}=={j:z for j,z in A[i].items()if j in Kbar}for i in Rbar),'Literal sample C1 boundary block')
  rank,det,vector=direct_rank_and_null(actual);need(rank<n and det==0 and vector,'Literal C1 solution is singular')
  singular.append({'a':a,'b':b,'class':case['class'],'changes':[x,y],'rank':rank,'null_vector':vector})
 # Another scalar word genuinely admits a two-coefficient repair.
 original=[['ADD',1,0,'1'],['ADD',1,0,'1'],['ADD',1,0,'1'],['ADD',1,0,'-3']]
 rows=[{0:Q(1)},{1:Q(1)}]
 for e in original:step(rows,e)
 need(rows==[{0:Q(1)},{1:Q(1)}],'Positive toy baseline')
 rows=[{0:Q(1)},{1:Q(1)}]
 for e in [['ADD',1,0,'3/2'],['ADD',1,0,'3/2'],['ADD',1,0,'-3']]:step(rows,e)
 need(rows==[{0:Q(1)},{1:Q(1)}],'Positive toy genuine joint repair')
 rejected=False
 try:polynomial_closure([[Q(1),Q(1),Q(0),Q(-1)]],[Q(0),Q(0),Q(0),Q(1)])
 except ValueError as error:
  need('Nonzero determinant' in str(error),'Positive control rejected for the expected reason');rejected=True
 need(rejected,'A repairable toy must not receive a false obstruction')
 return {'literal_expansion_and_direct_determinant_cases':identities,'literal_joint_C1_null_vectors':singular,'corrupted_transfer_rejected':corruption_checked,'repairable_three_parallel_ADD_control':True}

def encode(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return{str(k):encode(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return[encode(y)for y in x]
 return x

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--word',type=Path,required=True);parser.add_argument('--output',type=Path);parser.add_argument('--details',type=Path,help='Optional full residual equation/determinant records');args=parser.parse_args();beg=time.monotonic()
 w=json.loads(gzip.decompress(args.word.read_bytes()));payload={k:v for k,v in w.items()if k!='verifier_profile'};digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest();need(digest==PAYLOAD,'Native payload pin')
 p=w['program'];n=w['public'];nn=n+w['owned_fields'];need(p[DELETED]==['ADD',796,438,'-1',245],'Fixed deleted event')
 dims=list(map(len,w['frames']));Kbar={r for r in range(n)if dims[w['initial'][r]]!=0};Rbar={r for r in range(n)if dims[w['final'][r]]!=9}
 gates=[i for i,e in enumerate(p)if scalar(e)and i!=DELETED]
 # Exact own forward replay and adjoint, on the already deleted word.
 rows=[{r:Q(1)}if r<n else{}for r in range(nn)];v={}
 for i,e in enumerate(p):
  if i==DELETED:continue
  if scalar(e):v[i]=dict(rows[source(e)])
  step(rows,e)
 T0=rows[:n];inverse,det0=inverse_full(T0);need(det0==1,'Independent deleted-word determinant')
 invcols=[{}for _ in range(n)]
 for r,row in enumerate(inverse):
  for j,z in row.items():invcols[j][r]=z
 def apply_inverse(column):
  out={}
  for j,z in column.items():axpy(out,invcols[j],z)
  return out
 u={};adj=[{r:Q(1)}if r<n else{}for r in range(nn)]
 for i in range(len(p)-1,-1,-1):
  if i==DELETED:continue
  e=p[i];op,r=e[:2]
  if scalar(e):u[i]=dict(adj[r])
  if op=='ADD':axpy(adj[e[2]],adj[r],coef(e))
  elif op=='COPY':tail=dict(adj[r]);adj[r]={};axpy(adj[e[2]],tail,coef(e))
  elif op=='SCALE':adj[r]={j:coef(e)*z for j,z in adj[r].items()if coef(e)*z}
  elif op in('INIT','CLEAR'):adj[r]={}
 A=[{r:Q(1)}for r in range(n)]
 for r in w['live']:A[r+112][r]=Q(1)
 defect={}
 for r in Rbar:
  row={j:T0[r].get(j,Q(0))-A[r].get(j,Q(0))for j in Kbar}
  row={j:z for j,z in row.items()if z}
  if row:defect[r]=row
 first=min(defect);z=dict(defect[first]);c0=min(z);ww={r:row.get(c0,Q(0))/z[c0]for r,row in defect.items()}
 need(all(row=={j:a*ww[r]for j,a in z.items()}for r,row in defect.items()),'Rank-one boundary defect')
 pp={i:{r:a for r,a in u[i].items()if r in Rbar}for i in gates};qq={i:{r:a for r,a in v[i].items()if r in Kbar}for i in gates}
 pd={i:normal(pp[i])for i in gates};qd={i:normal(qq[i])for i in gates};wd,zd=normal(ww),normal(z)
 col_nonzero=[i for i in gates if pd[i]==wd];col_zero=[i for i in gates if not pp[i]];row_nonzero=[i for i in gates if qd[i]==zd];row_zero=[i for i in gates if not qq[i]]
 pq={i:quotient(pp[i],ww)for i in gates};qqq={i:quotient(qq[i],z)for i in gates}
 colpairs=set()
 for a in col_nonzero:
  for b in col_nonzero+col_zero:
   if a!=b and spans_target(qqq[a],qqq[b]):colpairs.add(tuple(sorted((a,b))))
 rowpairs=set()
 for a in row_nonzero:
  for b in row_nonzero+row_zero:
   if a!=b and spans_target(pq[a],pq[b]):rowpairs.add(tuple(sorted((a,b))))
 pairs=sorted(colpairs|rowpairs)
 print('DOMAIN',len(pairs),'column',len(colpairs),'row_additional',len(rowpairs-colpairs),'classes',len(col_nonzero),len(col_zero),len(row_nonzero),len(row_zero),'seconds',time.monotonic()-beg,flush=True)
 small=set(col_nonzero)|set(row_nonzero);forward=defaultdict(set);backward=defaultdict(set)
 for a,b in pairs:
  if a in small:forward[a].add(b)
  else:need(b in small,'Small-endpoint transfer cover');backward[b].add(a)
 tau={}
 def propagate(column,e):
  op,r=e[:2]
  if op=='ADD':a=column.get(r,Q(0))+coef(e)*column.get(e[2],Q(0))
  elif op=='COPY':a=coef(e)*column.get(e[2],Q(0))
  elif op=='SCALE':a=coef(e)*column.get(r,Q(0))
  elif op in('INIT','CLEAR'):a=Q(0)
  else:return
  if a:column[r]=a
  else:column.pop(r,None)
 for a,later in forward.items():
  column={p[a][1]:Q(1)}
  for i in range(a+1,max(later)+1):
   e=p[i]
   if i in later:tau[a,i]=column.get(source(e),Q(0))
   if i!=DELETED:propagate(column,e)
 for b,earlier in backward.items():
  row={source(p[b]):Q(1)}
  for i in range(b-1,min(earlier)-1,-1):
   e=p[i];op,r=e[:2]
   if i in earlier:tau[i,b]=row.get(r,Q(0))
   if i==DELETED:continue
   if op=='ADD':
    a=row.get(e[2],Q(0))+coef(e)*row.get(r,Q(0))
    if a:row[e[2]]=a
    else:row.pop(e[2],None)
   elif op=='COPY':
    a=coef(e)*row.get(r,Q(0));row.pop(r,None)
    if a:row[e[2]]=row.get(e[2],Q(0))+a
    if row.get(e[2])==0:row.pop(e[2],None)
   elif op=='SCALE':
    a=coef(e)*row.get(r,Q(0))
    if a:row[r]=a
    else:row.pop(r,None)
   elif op in('INIT','CLEAR'):row.pop(r,None)
 need(len(tau)==len(pairs),'Every exact mixed transfer obtained')
 qu={i:apply_inverse(u[i])for i in gates};diag={i:dot(v[i],qu[i])for i in gates}
 one=[]
 for i in sorted(set(col_nonzero)&set(row_nonzero)):
  ps=pq[i][2];qs=qqq[i][2];delta=-1/(ps*qs)
  need(1+delta*diag[i]==0,'One-compensator boundary solution must be singular')
  one.append({'event':i,'delta':delta,'new_coefficient':coef(p[i])+delta})
 print('TRANSFERS_DONE',len(tau),'zero_variable_repairs',len(one),'seconds',time.monotonic()-beg,flush=True)
 counts=Counter();eq_hash=hashlib.sha256();det_hash=hashlib.sha256();residual=[]
 for number,(a,b)in enumerate(pairs):
  t=tau[a,b]
  if (a,b)in colpairs:
   pa=pq[a][2];pb=pq[b][2];coordinates=z.keys()|qq[a].keys()|qq[b].keys()
   equations=[[pa*qq[a].get(j,Q(0)),pb*qq[b].get(j,Q(0)),t*pb*qq[a].get(j,Q(0)),z.get(j,Q(0))]for j in sorted(coordinates)]
  else:
   qa=qqq[a][2];qb=qqq[b][2];coordinates=ww.keys()|pp[a].keys()|pp[b].keys()
   equations=[[qa*pp[a].get(j,Q(0)),qb*pp[b].get(j,Q(0)),t*qa*pp[b].get(j,Q(0)),ww.get(j,Q(0))]for j in sorted(coordinates)]
  daa,dbb=diag[a],diag[b];dab,dba=dot(v[a],qu[b]),dot(v[b],qu[a]);D=[daa,dbb,daa*dbb-dab*dba+t*dab,Q(1)]
  kind,reduced=polynomial_closure(equations,D);counts[kind]+=1
  eq_hash.update(json.dumps(encode([a,b,equations]),separators=(',',':')).encode());det_hash.update(json.dumps(encode([a,b,D]),separators=(',',':')).encode())
  if kind not in('linear_inconsistent','linear_determinant_span'):residual.append({'a':a,'b':b,'class':kind,'equations':encode([row for pivot,row in reduced]),'determinant':encode(D)})
  if number%10000==0:print('CLOSURES',number,dict(counts),'seconds',round(time.monotonic()-beg,2),flush=True)
 need(len(pairs)==46381,'Reconstructed joint domain census')
 need(counts['linear_inconsistent']==99 and counts['linear_determinant_span']==43334,'Independent linear closure partition')
 need(sum(v for k,v in counts.items()if k not in('linear_inconsistent','linear_determinant_span'))==2948,'Independent nonlinear residual census')
 controls=literal_controls(p,n,nn,T0,A,v,u,tau,pairs,residual,diag,qu,Kbar,Rbar)
 if args.details:args.details.write_text(json.dumps(residual,indent=2,sort_keys=True)+'\n')
 report={'claim':'Source-bound deletion10947 and any two other rational coefficient changes; necessary boundary equations imply singularity','payload_sha256':digest,'deleted_event':DELETED,'public':n,'det_T0':str(det0),'boundary_defect':{'column':encode(ww),'row':encode(z)},'scalar_compensators':len(gates),'direction_classes':{'column_nonzero':len(col_nonzero),'column_zero':len(col_zero),'row_nonzero':len(row_nonzero),'row_zero':len(row_zero)},'column_pairs':len(colpairs),'additional_row_pairs':len(rowpairs-colpairs),'pairs':len(pairs),'pair_domain_sha256':hashlib.sha256(json.dumps(pairs,separators=(',',':')).encode()).hexdigest(),'equation_stream_sha256':eq_hash.hexdigest(),'determinant_stream_sha256':det_hash.hexdigest(),'one_compensator_cases':encode(one),'closure_counts':dict(counts),'residual_case_sha256':hashlib.sha256(json.dumps(residual,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'literal_controls':encode(controls),'runtime_seconds':round(time.monotonic()-beg,6)}
 if args.output:args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('PASS_INDEPENDENT_TWO_COMPENSATOR_AUDIT',json.dumps({'pairs':len(pairs),'counts':dict(counts),'one_compensator':len(one),'seconds':report['runtime_seconds']},sort_keys=True),flush=True)

if __name__=='__main__':main()
