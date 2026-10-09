"""Exact comparison of complete own composition profiles; no producer replay."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
from datetime import datetime,timezone
from math import factorial
from copy import deepcopy
import ast,gzip,importlib.util,json,sys
if sys.flags.optimize: raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent.parent/'r12-audit';BASE=HERE/'balanced-composition';OUT=Path(__file__).resolve().parent/'composition-arithmetic';OUT.mkdir(exist_ok=True);sys.path.insert(0,str(HERE))
ROOT=Path('/Users/chafreaky/Documents/personal/integer-mult-research-20261008/r12-composition/research/composed-shrunk-birth')
import balanced_stopped as balanced
import interval_moment as intervals
read=lambda p:json.loads(p.read_text());sha=lambda p:sha256(p.read_bytes()).hexdigest()
def check(ok,msg):
 if not ok: raise ValueError(msg)
def js(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [js(v) for v in x]
 return x
def exact(x):
 if isinstance(x,dict):return {k:exact(v) for k,v in x.items()}
 if isinstance(x,list):return [exact(v) for v in x]
 if isinstance(x,str) and '/' in x and all(s.lstrip('-').isdigit() for s in x.split('/')):return Q(x)
 return x
SRC=HERE/'pr100/source/research/deferred-balanced/arithmetic-sources'
spec=importlib.util.spec_from_file_location('pinned_math',SRC/'binary_frame_math.py');math=importlib.util.module_from_spec(spec);spec.loader.exec_module(math)
tree=ast.parse((SRC/'refine.py').read_text());wanted={'floor_scaled','ceiling_scaled','exact_moment'};nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in wanted];check({n.name for n in nodes}==wanted,'Missing frozen enclosure function')
env=dict(Q=Q,factorial=factorial,arithmetic=math);exec(compile(ast.Module(body=nodes,type_ignores=[]),str(SRC/'refine.py'),'exec'),env)
base=exact(read(BASE/'certificate.json'));A=Q(base['actual_bit_saving']);oldleaf=base['ordinary_leaf_bridge'];results={};pins={str(p):sha(p) for p in (Path(__file__),BASE/'certificate.json',BASE/'second-audit.json',HERE/'balanced_stopped.py',HERE/'interval_moment.py',SRC/'refine.py',SRC/'binary_frame_math.py')}
profiles={'base':ROOT,'weighted':ROOT/'variants/weighted','cost-filtered':ROOT/'variants/cost-filtered'}
if len(sys.argv)>1:profiles={Path(p).name:Path(p).resolve() for p in sys.argv[1:]}
for name,folder in profiles.items():
 saved=OUT/name;saved.mkdir(exist_ok=True)
 for filename in ('BIRTH_MATCHES.json.gz','READOUT_COST.json','BIRTH_AUDIT.json','SCALAR_REUSE_AUDIT.json','TRANSPORT.json'):
  p=folder/filename
  if p.exists():
   data=p.read_bytes();(saved/filename).write_bytes(data);pins[str(p)]=sha256(data).hexdigest()
 raw=json.loads(gzip.decompress((saved/'BIRTH_MATCHES.json.gz').read_bytes()));cost=read(saved/'READOUT_COST.json');p=deepcopy(base['profile']);p.update(R=raw['R'],W=raw['W'],total_rank=raw['rank'],deficit=raw['deficit'],maxchild=max(map(int,raw['child_histogram'])),child_multiplicities=raw['child_histogram'])
 check(p['W']==2*p['N']+2*p['v']*p['R'],'Role width');intervals.prepare(p)
 bridge=deepcopy(base['finite_bridge']);axis=bridge['complex'];m,W,s=(p[k] for k in ('m','W','total_rank'));G=cost['global_scalar_group_upper'];axis.update(m=m,W=W,maxchild=p['maxchild'],s=s,scalar_group_upper=G,halving_degree=balanced.halving_degree(m,p['maxchild']),wire_bits=W.bit_length())
 E=64*(W+m+G+1)**3;B=s+E;literal=2*G*W**2+8*s+4*W+4+32*m;bridge['semantic'].update(E=E,B=B,C0=32*m*B**2,C1=1,literal_charge=literal,strict_literal_gap=E-literal,induction_gap=2*B*(m-p['maxchild'])-s-E)
 coefficient=sum(x['halving_degree']*x['wire_bits'] for x in (bridge['bit_coarse'],axis,oldleaf));degree=1000*((51*coefficient)//25000+1);bridge['rows'].update(coefficient=coefficient,degree=degree,degree_gap=Q(degree)-Q(51,25)*coefficient,suffix_slope=4*degree);balanced.validate_bridge(bridge,oldleaf)
 moment=intervals.saving_grid(p);b=moment['accepted']['saving'];bn=moment['rejected']['saving'];beta=eta=Q(1,10**24);backoff=Q(1,10**30);a=min(A,(1-beta)*b-backoff);q=a*(1-2*eta);limit=(1-eta)*q/(1+q);scaled=limit*10**18;k=Q(-((-scaled.numerator)//scaled.denominator)-1,10**18);assembly=balanced.assembly(bridge,oldleaf,a,k,beta=beta,h=eta,a_complex=b)
 def reject(fn):
  try:fn()
  except balanced.InvalidAssembly as error:return str(error)
  raise ValueError('Adverse parameter accepted')
 next_rejection=reject(lambda:balanced.assembly(bridge,oldleaf,a,k+Q(1,10**18),beta=beta,h=eta,a_complex=b));old_rejection=reject(lambda:balanced.assembly(bridge,oldleaf,a,k,beta=beta,h=eta,a_complex=b,original_prefix=True));cap=min(A,bn)/(1+min(A,bn));check(cap<k+Q(1,10**18),'Fixed-family grid ceiling')
 hist={int(t):n for t,n in p['child_multiplicities'].items()};second={label:env['exact_moment'](m,W,hist,saving) for label,saving in [('accepted',b),('rejected',bn)]};check(second['accepted']['upper']<1<second['rejected']['lower'],'Independent enclosure contradicted first')
 for label in second:
  record=second[label];narrow=moment[label];check(record['lower']<=narrow['lower']<=narrow['upper']<=record['upper'],'Moment nesting')
  first_terms={r['child']:r for r in narrow['terms']}
  for t,r in record['terms'].items():
   f=first_terms[t];check(r['log_lower']<=f['log_lower']<=f['log_upper']<=r['log_upper'],'Log nesting');check(r['exp_lower']<=f['exp_lower']<=f['exp_upper']<=r['exp_upper'],'Exp nesting')
 check(len(assembly['constraints'])==47 and len(assembly['margins'])==7,'Constraint coverage')
 result=dict(name=name,profile=p,finite_bridge=bridge,complex_saving=b,next_complex_rejected=bn,first_moment=moment,independent_moment=second,actual_bit_saving=A,assembly_bit=a,kappa=k,beta=beta,eta=eta,backoff=backoff,assembly=assembly,cutoffs=balanced.cutoffs(bridge,oldleaf,assembly),next_kappa=k+Q(1,10**18),next_kappa_rejection=next_rejection,old_prefix_rejection=old_rejection,fixed_profile_family_ceiling=cap,grid_optimality=True,baseline_kappa=base['selected']['kappa'],kappa_gain=k-base['selected']['kappa'])
 output=saved/'arithmetic.json';output.write_text(json.dumps(js(result),indent=2,sort_keys=True)+'\n');results[name]=dict(kappa=k,complex_saving=b,kappa_gain=result['kappa_gain'],arithmetic_sha256=sha(output),profile_sha256=sha(saved/'BIRTH_MATCHES.json.gz'),physical_receipts={name:sha(saved/name) for name in ('BIRTH_AUDIT.json','SCALAR_REUSE_AUDIT.json') if (saved/name).exists()});print(name,'complex',b,'kappa',k,'gain',result['kappa_gain'],flush=True)
for p,h in pins.items():check(sha(Path(p))==h,'Source changed during comparison '+p)
report=dict(status='PASS two independent exact arithmetic enclosures and full three-stock balanced transfer',verified_utc=datetime.now(timezone.utc).isoformat(),profiles=results,input_and_source_pins=pins,scope='Own supplied physical profiles compared read-only. Correct physical/reflection/dirty identities remain external evidence; receipt presence alone is not an independent replay. Inherited paid balanced-layout and stopped product-ring contracts retained. Adjacent-grid ceiling is scoped to each fixed profile and this transfer family.')
(OUT/'comparison.json').write_text(json.dumps(js(report),indent=2,sort_keys=True)+'\n');print('comparison sha256',sha(OUT/'comparison.json'))
