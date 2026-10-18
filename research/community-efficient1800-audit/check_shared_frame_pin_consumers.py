"""Execute actual unchanged source gates with frozen positives and candidate negatives.

This is an integration diagnostic, not a replay of the consumers' mathematics.
"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
P=Path('/tmp/pr-efficient1800');R=Path('/tmp/integer-mult-efficient1100-20261015');D=P/'combined-1861-1922-v3'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=R)
head=git('rev-parse','HEAD').decode().strip();results=[];start=time.monotonic()
def require(ok,message):
 if not ok:raise ValueError(message)
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
for pkg,script,target in [('binary-residual-exhaustive','verify.py','scripts/binary_phase_frames.py'),('cube-xor-replay','replay.py','scripts/audit_joint_frames.py')]:
 with tempfile.TemporaryDirectory(prefix='shared-frame-pin-gate-') as tmp:
  root=Path(tmp);folder=root/'research'/pkg
  paths=git('ls-tree','-r','--name-only',head,'research/'+pkg).decode().splitlines()
  for path in paths:
   f=root/path;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(git('show',head+':'+path))
  pins=json.loads((folder/'SOURCES.json').read_text());effective=dict(pins['files'])
  if pkg=='cube-xor-replay':
   compat=json.loads((folder/'COMPATIBILITY.json').read_text())
   for name,row in compat['files'].items():effective[name]=row['current']
  inputs={}
  for name,row in effective.items():
   data=git('show',head+':'+name)
   if sha(data)!=row['sha256']:data=git('cat-file','blob',row['git_blob'])
   require(sha(data)==row['sha256'],'Wrong authenticated input '+name)
   f=root/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data);inputs[name]=sha(data)
  m=load(folder/script,'consumer_'+pkg.replace('-','_'))
  m.check_sources()
  f=root/target;old=f.read_bytes();new=(D/target).read_bytes();f.write_bytes(new)
  try:m.check_sources()
  except ValueError as error:
   message=str(error);require(target in message,'Wrong failure: '+message)
  else:raise ValueError('Candidate unexpectedly passed old source gate')
  f.write_bytes(old);m.check_sources()
  results.append(dict(package=pkg,code_sha256=sha((folder/script).read_bytes()),manifest_sha256=sha((folder/'SOURCES.json').read_bytes()),positive_control=True,restoration_control=True,candidate_rejection=message,changed_path=target,candidate_sha256=sha(new),effective_input_sha256=inputs))
# The new PR1076 historical replay already authenticates its old audit_joint_frames input.
# An unrecognized successor must fail before any historical mathematical checker runs.
config=json.loads(git('show',head+':research/quadratic-affine-performance/HISTORICAL-PACKED.json'))
manifest=json.loads(git('show',head+':research/quadratic-affine-packed/SOURCES.json'))
target='scripts/audit_joint_frames.py';candidate=sha((D/target).read_bytes())
require(candidate!=manifest['files'][target] and candidate not in config['accepted_live'].get(target,[]),'Unexpected accepted joint successor')
results.append(dict(package='quadratic-affine-performance/historical_packed.py',scope='Static exact accepted-live predicate: new joint helper requires explicit reviewed successor entry.',candidate_sha256=candidate,accepted_live=config['accepted_live'].get(target,[]),predecessor_sha256=manifest['files'][target]))
out=dict(status='PASS',baseline=head,seconds=time.monotonic()-start,results=results,scope='Actual unchanged binary-residual and cube source gates pass exact frozen/effective inputs, reject only the candidate helper replacement, and pass restoration. Not full scientific consumer replays. Third historical-adapter predicate is a static inventory check.')
(P/'finding-1861-1922-source-gates.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='results'}));print([(r['package'],r.get('candidate_rejection','needs explicit successor entry')) for r in results])
