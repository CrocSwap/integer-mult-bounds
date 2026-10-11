"""Exact matrix realization of pinned PR473's whole-owner routes.
Checker by OpenAI Codex. Source construction: Rohan Arun, chafreaky,
Dugongue, DaysSky, and upstream attribution retained in pinned source slice.
No public sources are modified. No all-size or cover enumeration claim.
"""
import gzip, hashlib, json, sys
from collections import Counter,defaultdict
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve()
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
M=78

def actual_routes():
 t=read(OUT/'hosted/GLOBAL-TEMPLATE.json.gz');geo=read(OUT/'hosted/GEOMETRY.json');w=read(ROOT/'data/word.json')
 isos={x['frame']:x for x in t['residual_isometries']};idle={e['idx']:e for e in t['schedule'] if e['kind']=='idle'}
 # Each basis column is an ACTUAL rational ambient vector, stored with denominator2.
 bases=[]
 for p in geo['ports']:
  head=[[F(q,2) for q in p['q']]]+[[F(row[j]) for row in p['complement_columns']] for j in range(7)]
  assert all(sum(x*y for x,y in zip(a,b))==int(i==j) for i,a in enumerate(head) for j,b in enumerate(head))
  cols=[tuple((i,int(2*x)) for i,x in enumerate(col) if x) for col in head]
  assert all(F(n,2)==x for col,cc in zip(head,cols) for i,n in cc for x in [col[i]])
  cols += [((j,2),) for j in range(8,M)]
  assert len(cols)==M and len(set(cols))==M;bases.append(tuple(cols))
 residuals={}
 for f,z in isos.items():
  rows=z['orthogonal_rows_numerator'];e=z['entrance_rank']
  assert z['denominator']==2 and len(rows)==8
  order=[]
  for row in rows:
   assert len(row)==8 and sum(v!=0 for v in row)==1 and 2 in row
   order.append(row.index(2))
  assert set(order)==set(range(8))
  assert order[:e]==z['entrance_basis'] and order[e:]==z['residual_basis']
  assert set(w['frames'][f])==set(z['entrance_basis'])
  for a in z['entrance_basis']:
   assert w['lines'][a]==[2*int(a==j) for j in range(8)]
  residuals[f]=order[e:]
 digest=hashlib.sha256();maps=0;mult=Counter();distinct=set();widths=Counter();used=defaultdict(set);pending=defaultdict(set);orientation=Counter()
 for call in t['calls']:
  seen=set();families=Counter();active={f for f,r in call['owners'][:240]};assert len(active)==240
  for h,(family,route) in enumerate(call['owners'][240:]):
   typ,idx,off,width=route;assert typ=='hosted'
   assert family not in active
   owner_rep,sub=divmod(family,1200);pair,sp=divmod(sub,240);side,port=divmod(sp,120)
   child=idle[idx];assert child['pair']==pair
   lo,hi=child['source_level'],child['target_level']
   axes=(list(range(1,8))+list(range(8,8+7*hi))) if lo==-1 else list(range(8+7*lo,8+7*hi))
   assert len(axes)==child['rank'];foot=axes[off:off+width];assert len(foot)==width
   f=w['start'][240+h];res=residuals[f];assert width==len(res) and width in (6,7,8)
   # sigma sends each residual coordinate to one assigned pending coordinate.
   # Complete the remaining columns with unused actual basis vectors in fixed order.
   order=[None]*M
   for src,dst in zip(res,foot):order[src]=dst
   rest=iter(j for j in range(M) if j not in foot)
   for j in range(M):
    if order[j] is None:order[j]=next(rest)
   assert set(order)==set(range(M))
   sigma=tuple(bases[port][j] for j in order)
   # Orthogonality is exact: actual full orthonormal basis with all78columns permuted.
   assert len(set(sigma))==M
   assert tuple(sigma[j] for j in res)==tuple(bases[port][j] for j in foot)
   # Therefore sigma(I-P_f)sigma^T is exactly the pending slot projector.
   actual=(family,sigma);assert actual not in seen,'actual cover owner collision';seen.add(actual)
   key=(idx,family);assert not used[key].intersection(foot);used[key].update(foot);pending[key]=set(axes)
   families[family]+=1;maps+=1;widths[width]+=1;orientation[call['orientation']]+=1
   sh=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest();distinct.add(sh)
   digest.update(json.dumps([call['stage'],call['replica'],h,family,sh],separators=(',',':')).encode()+b'\n')
  assert len(seen)==715
  for n in families.values():mult[n]+=1
 # Hosted projectors and remaining idle projector are orthogonal and sum to the entire child.
 completion=0
 for (idx,family),u in used.items():
  assert u<=pending[idx,family]
  remainder=pending[idx,family]-u
  assert not u&remainder and u|remainder==pending[idx,family]
  completion+=1
 assert maps==62920
 return dict(status='PASS_ACTUAL_ORTHOGONAL_OWNER_INJECTION_AND_IDLE_COMPLETION',ambient_dimension=M,helper_routes=maps,
  residual_width_counts=dict(sorted(widths.items())),orientations=dict(orientation),actual_distinct_sigma_matrices=len(distinct),
  sigma_stream_sha256=digest.hexdigest(),family_multiplicity_histogram=dict(sorted(mult.items())),
  same_family_additional_roles=sum((n-1)*c for n,c in mult.items()),max_helpers_per_family_per_call=max(mult),
  idle_family_completion_checks=completion,matrix_denominator=2,
  proof='Every sigma is a complete actual rational orthogonal matrix. Its residual projector maps exactly to its assigned pending slot. At fixed d, equal (family,d*sigma^-1) forces equal family and sigma. Disjoint pending factors plus their complement give the original idle D-projector. This applies to both reflected orientations since D_E D_I=D_(I-E).')

def main():
 r=actual_routes();r['scope']='Candidate exact route construction, owner injection and physical residual completion; full all-size compiler and analytic contracts are not established by this check.'
 (OUT/'COVER-OWNER-INJECTION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
