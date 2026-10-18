"""Optimized isolated replay and fail-closed packaging controls."""
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(b,s):
 if not b:raise RuntimeError(s)
def main():
 with tempfile.TemporaryDirectory(prefix='.semantic-d-test-',dir=ROOT) as d:
  root=Path(d);p=root/'research'/HERE.name;shutil.copytree(HERE,p)
  manifest=json.loads((p/'SOURCES.json').read_text())
  for rel in manifest['files']:
   dst=root/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/rel,dst)
  def run(label,error=None):
   r=subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py')],cwd=root,capture_output=True,text=True)
   need((r.returncode==0) if error is None else (r.returncode!=0 and error in r.stderr),label+' '+r.stdout+r.stderr)
  run('minimal relocation')
  source=(p/'SOURCES.json').read_bytes();receipt=(p/'RESULT.json').read_bytes()
  del manifest['files'][next(iter(manifest['files']))];(p/'SOURCES.json').write_text(json.dumps(manifest));run('missing source entry','exact source inventory');(p/'SOURCES.json').write_bytes(source)
  (p/'SOURCES.json').write_text('{"base":1,"base":2}');run('duplicate key','duplicate JSON key');(p/'SOURCES.json').write_bytes(source)
  (p/'SOURCES.json').write_text('{"base":NaN}');run('nonfinite','nonfinite JSON');(p/'SOURCES.json').write_bytes(source)
  rel='research/e8-bit-p111-tuned/code/xcheck_p.py';b=(root/rel).read_bytes();(root/rel).write_bytes(b+b' ');run('source corruption','source pin');(root/rel).write_bytes(b)
  bad=json.loads(receipt);bad['columns']=True;(p/'RESULT.json').write_text(json.dumps(bad));run('Boolean receipt count','typed canonical result mismatch');(p/'RESULT.json').write_bytes(receipt)
 print('PASS_SEMANTIC_D_PACKAGE relocation=1 corruptions=5')
if __name__=='__main__':main()
