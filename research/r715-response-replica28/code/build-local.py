"""Build the changed E510 program using source-bound upstream scalar/emission code.
No network access. All paths are explicit CLI arguments. No global chdir.
"""
import argparse,gzip,json,hashlib,sys
from pathlib import Path
sys.dont_write_bytecode=True
p=argparse.ArgumentParser();p.add_argument('--word',type=Path,required=True);p.add_argument('--vendor',type=Path,required=True);p.add_argument('--routes',type=Path,required=True);p.add_argument('--clifford',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--skip-phase',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
word_bytes=a.word.read_bytes();word_bytes=gzip.decompress(word_bytes) if a.word.suffix=='.gz' else word_bytes;w=json.loads(word_bytes);raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode();(a.out/'FULL-WORD.json.gz').write_bytes(gzip.compress(raw,mtime=0));sources={}
def run(name,changes,extra=None):
 q=a.vendor/name;s=q.read_text();sources[name]=hashlib.sha256(q.read_bytes()).hexdigest()
 for old,new in changes:
  assert old in s,(name,old);s=s.replace(old,new,1)
 ns={'__name__':'__main__','OUT':a.out,'ROUTES':a.routes};ns.update(extra or {});exec(compile(s,str(q),'exec'),ns)
 # Runtime measurements are operational logs, never part of source identity.
 report={'audit_cxg.py':'SCALAR-FRAME-AUDIT.json','phases_cxg.py':'CLIFFORD-REVIEW.json'}.get(name)
 if report:
  rp=a.out/report;rr=json.loads(rp.read_text());rr.pop('seconds',None);rp.write_text(json.dumps(rr,indent=2)+'\n')
run('audit_cxg.py',[("OUT=Path(os.environ.get('CXOUT','split-centres'));p=OUT/'FULL-WORD.json.gz'","p=OUT/'FULL-WORD.json.gz'"),("old=json.load(gzip.open('work/higher-stage-e8/verified/gcert1-e8-retimed.json.gz'))","old=json.load(gzip.open(ROUTES))")])
run('emit_cxg.py',[("OUT=Path('split-centres');cp=OUT/'CANONICAL-WORD.json.gz'","cp=OUT/'CANONICAL-WORD.json.gz'")])
sys.path.insert(0,str(a.clifford.parent));sources['clifford_exact.py']=hashlib.sha256(a.clifford.read_bytes()).hexdigest()
if not a.skip_phase:run('phases_cxg.py',[("sys.path.insert(0,str(Path('work/odd-stages').resolve()))","# exact module supplied by CLI"),("OUT=Path('split-centres');P=OUT/'CANONICAL-WORD.json.gz'","P=OUT/'CANONICAL-WORD.json.gz'")])
manifest={'input_word_sha256':hashlib.sha256(word_bytes).hexdigest(),'sources':sources,'files':{q.name:hashlib.sha256(q.read_bytes()).hexdigest()for q in sorted(a.out.iterdir())if q.is_file() and q.name in ['FULL-WORD.json.gz','CANONICAL-WORD.json.gz','SCALAR-FRAME-AUDIT.json','LOCAL-PROGRAMS.json.gz','LOCAL-CHECKS.json','CLIFFORD-RECIPES.json','CLIFFORD-REVIEW.json']}};(a.out/'BUILD-RECEIPT.json').write_text(json.dumps(manifest,indent=2));print('BUILD COMPLETE',flush=True)


