"""Run original checks in a temporary directory, preserving all frozen inputs."""
import sys,os,json,gzip,hashlib,tempfile,shutil,subprocess
from pathlib import Path
if sys.flags.optimize or os.environ.get('PYTHONOPTIMIZE'):raise RuntimeError('Assertions required')
ROOT=Path(__file__).resolve().parent;REPO=Path(os.environ.get('BIRTH_REPO',ROOT.parents[1])).resolve()
for name,digest in json.loads((ROOT/'BASE_INPUTS.json').read_text())['files'].items():
 if hashlib.sha256((REPO/name).read_bytes()).hexdigest()!=digest:raise ValueError('Changed base input: '+name)
keys={'BIRTH_MATCHES.json.gz':['R','W','rank','matched','child_histogram','pairs'], 'READOUT_COST.json':['readout_nonzero_terms','readout_numerator_L1','max_abs_numerator','global_scalar_group_upper','exact_response_sha256'], 'BIRTH_AUDIT.json':['matches','physical_original_roles','word_blocks','forward_frame_transitions','reverse_frame_transitions','all_histogram_bins_match','forward_word_sha256','reverse_word_sha256']}
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_text())
with tempfile.TemporaryDirectory(prefix='birth-read-reuse-')as temp:
 work=Path(temp)
 for p in ROOT.iterdir():
  if p.is_file():shutil.copyfile(p,work/p.name)
 env=dict(os.environ,BIRTH_REPO=str(REPO))
 for program in ['check_birth_lemma.py','load_graph.py','build_roles.py','build_frames.py','match_births.py','readout_cost.py','audit_birth_frames.py']:
  subprocess.run([sys.executable,str(work/program)],env=env,check=True,timeout=180)
 for name,fields in keys.items():
  got,want=read(work/name),read(ROOT/name)
  for field in fields:
   if got[field]!=want[field]:raise ValueError(('Changed scientific result',name,field))
 # Assembly binds the exact frozen receipts, not run-dependent timing fields.
 for name in ['BIRTH_MATCHES.json.gz','READOUT_COST.json']:shutil.copyfile(ROOT/name,work/name)
 subprocess.run([sys.executable,str(work/'check_assembly.py')],env=env,check=True,timeout=10)
 if read(work/'CANDIDATE.json')!=read(ROOT/'CANDIDATE.json'):raise ValueError('Changed exact candidate')
print('PASS all author checks; frozen package unchanged; no upstream code executed')
