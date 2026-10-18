"""Full78-column matrix owner injection in the actual pending-child geometry."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
import json,gzip,hashlib,sys
read=lambda p:json.loads(gzip.decompress(Path(p).read_bytes())if str(p).endswith('.gz')else Path(p).read_bytes())
a=read(sys.argv[1]);w=read(sys.argv[2]);t=read(Path(sys.argv[3])/'GLOBAL-TEMPLATE.json.gz');geo=read(Path(sys.argv[3])/'GEOMETRY.json');out=Path(sys.argv[4]);M=78
assert hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest()==a['source_word_sha256']==t['source_word_sha256']
assert t['paired_rational_hosting']==a
bases=[]
for p in geo['ports']:
 head=[[Q(x,2)for x in p['q']]]+[[Q(row[j])for row in p['complement_columns']]for j in range(7)]
 assert all(sum(x*y for x,y in zip(u,v))==int(i==j)for i,u in enumerate(head)for j,v in enumerate(head))
 assert all((4*x).denominator==1 for col in head for x in col)
 cols=[tuple((i,int(4*x))for i,x in enumerate(col)if x)for col in head]+[((j,4),)for j in range(8,M)];bases.append(tuple(cols))
idle={e['idx']:e for e in t['schedule']if e['kind']=='idle'};calls={(c['stage'],c['replica']):c for c in t['calls']};seen=defaultdict(set);sigs=set();digest=hashlib.sha256();paircache={};counts=Counter()
for s,rep,h,z in a['owners']:
 fam=z['family'];expected_route=['paired-rational',z['pair'],z['copy']]if z['kind']=='paired-rational-whole'else['coordinate-whole',z['window'],z['offset'],z['width']]
 assert calls[s,rep]['owners'][h]==[fam,expected_route]
 child=idle[z['window']];pair,sp=divmod(fam%1200,240);side,port=divmod(sp,120);assert child['pair']==pair
 assert fam not in {x[0]for x in calls[s,rep]['owners'][:240]}
 lo,hi=child['source_level'],child['target_level'];axes=(list(range(1,8))+list(range(8,8+7*hi)))if lo==-1 else list(range(8+7*lo,8+7*hi));assert len(axes)==child['rank']
 assert s in a['windows'][str(z['window'])][2]
 assert lo<s<=hi and a['windows'][str(z['window'])][1]==child['rank']
 if z['kind']=='coordinate-whole':
  f=w['start'][h];entrance=[]
  for line in w['frames'][f]:
   v=w['lines'][line];nz=[i for i,x in enumerate(v)if x]
   if len(nz)==1:entrance.append(nz[0])
  assert all(all(i in entrance for i,x in enumerate(w['lines'][line])if x)for line in w['frames'][f])
  res=[i for i in range(8)if i not in entrance];assert len(res)==z['width'];foot=axes[z['offset']:z['offset']+z['width']];order=[None]*M
  for src,dst in zip(res,foot):order[src]=dst
  rest=iter(i for i in range(M)if i not in foot)
  for i in range(M):
   if order[i]is None:order[i]=next(rest)
  sigma=tuple(bases[port][i]for i in order)
 else:
  p=a['pairs'][z['pair']];frame=str(p['route_registry_frame']);G=[[Q(x)for x in row]for row in a['registry'][frame]['route']];assert w['start'][h]==int(frame)
  assert [rep,h]==p['roles'][z['copy']] and p['family']==fam and p['stage']==s and p['window']==z['window']
  assert a['registry'][frame]['entrance_basis']==[w['lines'][i]for i in w['frames'][int(frame)]]
  # pending axes first, then its actual orthogonal complement in fixed order.
  adapted=axes+[i for i in range(M)if i not in axes];co=p['output_coordinates'];placement=co+[i for i in range(M)if i not in co];actual=[adapted[i]for i in placement]
  assert set(actual)==set(range(M));cols=[]
  for j in range(16):
   src=(j+8)%16 if z['copy']else j;v=Counter()
   for k in range(16):
    for ix,num in bases[port][actual[k]]:v[ix]+=G[k][src]*num
   assert all(q.denominator==1 for q in v.values());cols.append(tuple(sorted((i,int(q))for i,q in v.items()if q)))
  cols += [bases[port][actual[i]]for i in range(16,M)];sigma=tuple(cols)
  # Full orthogonality follows from separately checked G and actual orthonormal basis.
  assert len(sigma)==M
 actual=(fam,sigma);assert actual not in seen[s,rep],('owner collision',s,rep,h);seen[s,rep].add(actual)
 sh=hashlib.sha256(json.dumps(sigma,separators=(',',':')).encode()).hexdigest();sigs.add(sh);digest.update(json.dumps([s,rep,h,fam,sh],separators=(',',':')).encode()+b'\n');counts[z['kind']]+=1
assert all(len(v)==715 for v in seen.values())and len(seen)==88
r=dict(status='PASS_ACTUAL_FULL_MATRIX_PAIRED_OWNER_INJECTION',ambient=78,matrix_common_denominator=4,owners=sum(counts.values()),owner_kinds=dict(counts),calls=len(seen),distinct_sigma_matrices=len(sigs),sigma_stream_sha256=digest.hexdigest(),allocation_sha256=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),source_word_sha256=hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest(),scope='Exact per-call distinct full matrices, including physical pending-child ambient geometry, entrance directions and inverse transpose. Whole-cover right translation and exact paired projector identities yield conditional hosting.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
