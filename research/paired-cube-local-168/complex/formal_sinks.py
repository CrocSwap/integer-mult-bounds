"""Independent full execution of PR166 sink substitution on our fused168.

James Chang's PR166 compiler; fused168 source lineage in its SOURCE.json.
New full packed-column executor by Chafik Boukhalfa with OpenAI Codex.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict
from hashlib import sha256
import argparse,gzip,json,time,importlib.util,sys

BASE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--candidate',type=Path,default=BASE.parents[1]/'r13-search/fused168')
ap.add_argument('--selection',type=Path,default=BASE/'fused168-screen.json')
ap.add_argument('--formal-helper',type=Path)
ap.add_argument('--output',type=Path,default=BASE/'formal-sinks.json')
args=ap.parse_args();INPUT=args.candidate;HELPER=args.formal_helper or INPUT/'prove.py'
if sys.flags.optimize:raise SystemExit('Run without -O')
spec=importlib.util.spec_from_file_location('original_formal',HELPER)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def load(name):return json.loads(gzip.decompress((INPUT/(name+'.json.gz')).read_bytes()))
g,w,row=[load(n) for n in ['graph','word','profile-before']]
pairs=load('physical-pairs');selection=json.loads(args.selection.read_text())
for name,digest in selection['input_pins'].items():assert sha256((INPUT/name).read_bytes()).hexdigest()==digest,name
sinks=selection['sinks'];removed={s['role'] for s in sinks};sinkroots={s['root_index'] for s in sinks}
alias={b:a for a,b,t in pairs};R=row['R'];v=g['v']
live=[s for s in range(R) if s not in alias and s not in removed]
slot={s:i for i,s in enumerate(live)}
phys=lambda s:slot[alias.get(s,s)]
D,adj=old.adjoint(g,w,R)
ops=w['ops'];coef=w['opcoeff'];phase=w['phase1'];rest=[i for i in range(len(ops)) if i not in set(phase)]
deadlines=dict((b,t) for a,b,t in pairs);at=defaultdict(list)
for s,t in deadlines.items():
 if t is not None:at[t].append(s)
selected=[z['role'] for z in w['selected']];deferred=set(selected)
sources={int(x):s for x,s in w['sources'].items()}
bywrite={i:s for s in sinks for i in s['writes']};after={s['writes'][-1]:s for s in sinks}
cnum=[[int(6*Q(c)) for c in r['coefficients']] for r in g['roots']]
assert len(live)==selection['new_physical_R']

def execute(direction,bits=None,mutation=None):
 # With bits=None this is an absolute coefficient L1 majorant. With bits
 # supplied it is the actual signed word on an injectively packed basis.
 major=bits is None; top=6; count=2*v+len(live)
 def basis(i):return 6 if major else 6<<(bits*i)
 def add(x,c,y):return x+abs(c)*y if major else x+c*y
 def track(xs):
  nonlocal top
  if major:top=max(top,max(xs,default=0))
 X=[basis(i) for i in range(v)];Y=[basis(v+i) for i in range(v)];Z=[basis(2*v+i) for i in range(len(live))]
 initial=Y[:];z=Z[:]
 # Retain the ORIGINAL response of every retained dirty coordinate,
 # including responses propagated through the deleted sinks.
 virtual=[0 if s in deferred or s in alias or s in removed else Z[phys(s)] for s in range(R)]
 def gate(values,i):
  a,b,_=ops[i];ca,cb=coef[i]
  values[a]=abs(ca)*values[a]+abs(cb)*values[b] if major else ca*values[a]+cb*values[b]
 def decode(values,kind=None,skip=False):
  out=[0]*v
  for j,(root,s,cs) in enumerate(zip(g['roots'],w['rootroles'],cnum)):
   if kind is not None and root['kind']!=kind:continue
   if skip and j in sinkroots:continue
   for t,c in zip(root['targets'],cs):out[t]=add(out[t],c,values[s])
  assert all(x%6==0 for x in out)
  return [x//6 for x in out]
 for i in range(len(ops)):gate(virtual,i)
 response=decode(virtual,skip=mutation=='omit-ancestor-response')
 Y=[add(y,-direction,r) for y,r in zip(Y,response)];track(Y);del virtual,response
 for n,s in sources.items():z[phys(s)]=add(z[phys(s)],1,X[n-1])
 done=[]
 def actualgate(i):
  a,b,_=ops[i];ca,cb=coef[i];a,b=phys(a),phys(b)
  z[a]=abs(ca)*z[a]+abs(cb)*z[b] if major else ca*z[a]+cb*z[b]
  if major:
   nonlocal top
   top=max(top,z[a])
  done.append(i)
 def read(s):
  for t,c in D[s].items():
   assert z[phys(s)]%6==0
   Y[t]=add(Y[t],-direction*c,z[phys(s)]//6)
  track(Y)
 for i in phase:actualgate(i)
 virtual=[0 if s in removed else z[phys(s)] for s in range(R)]
 center=decode(virtual,'center');Y=[add(y,direction,c) for y,c in zip(Y,center)];track(Y);del virtual,center
 for sink in sinks:
  pivot=sink['pivot']
  for t in sink['targets']:
   if t!=pivot and mutation!='omit-pre-shear':Y[t]=add(Y[t],-1,Y[pivot])
 track(Y)
 for s in reversed(selected):
  if deadlines.get(s) is None:read(s)
 for i in rest:
  for s in at.get(i,[]):read(s)
  if i in bywrite:
   sink=bywrite[i];pivot=sink['pivot'];b=phys(ops[i][1]);assert z[b]%2==0
   if mutation!='omit-first-write' or i!=sinks[0]['writes'][0]:Y[pivot]=add(Y[pivot],direction*coef[i][1],z[b]//2)
   track(Y)
  else:actualgate(i)
  if i in after:
   sink=after[i];pivot=sink['pivot']
   for t in sink['targets']:
    if t!=pivot:Y[t]=add(Y[t],1,Y[pivot])
   track(Y)
 virtual=[0 if s in removed else z[phys(s)] for s in range(R)]
 side=decode(virtual,'side',True);Y=[add(y,direction,c) for y,c in zip(Y,side)];del virtual,side
 for a in range(0,v,8):
  for j,q in enumerate(g['inputs'][a:a+8]):
   value=0
   for r,x in zip(g['inputs'][a:a+8],X[a:a+8]):
    c=1 if (q^r).bit_count()==6 else -1 if (q^r).bit_count()==2 else 0
    value=add(value,c,x)
   assert value%2==0;Y[a+j]=add(Y[a+j],direction,value//2)
 track(Y)
 if not major:assert Y==[y+direction*x for y,x in zip(initial,X)],'all formal output columns'
 for i in reversed(done):
  a,b,_=ops[i];ca,cb=coef[i];a,b=phys(a),phys(b)
  z[a]=z[a]+abs(cb)*z[b] if major else ca*(z[a]-cb*z[b])
  if major:top=max(top,z[a])
 for n,s in sources.items():z[phys(s)]=add(z[phys(s)],-1,X[n-1])
 track(z)
 if not major:assert z==Z,'retained arbitrary dirty columns restored'
 # Include the expected map in a safe final residual bound.
 return top+12 if major else dict(direction=direction,columns=count,dirty=len(live),outputs=True,restored=True)

if __name__=='__main__':
 t=time.monotonic();bound=execute(1);bits=8*((bound.bit_length()+2+7)//8);assert 2**bits>2*bound
 print('majorant',bound,'digit bits',bits,flush=True)
 columns=[execute(d,bits) for d in [1,-1]]
 controls={}
 for mutation in ['omit-first-write','omit-ancestor-response','omit-pre-shear']:
  try:execute(1,bits,mutation)
  except AssertionError:controls[mutation]='REJECTED'
  else:raise AssertionError('accepted '+mutation)
 result=dict(status='PASS full modified finite word',absolute_residual_bound=bound,digit_bits=bits,columns=columns,controls=controls,source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),input_pins={p.name:sha256(p.read_bytes()).hexdigest() for p in list(INPUT.glob('*.json.gz'))+[args.selection,HELPER]},seconds=time.monotonic()-t)
 args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
