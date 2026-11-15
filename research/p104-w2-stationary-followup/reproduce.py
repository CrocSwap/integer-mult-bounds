"""Reproduce the explicitly adapted W2 application using authenticated #7605 sources."""
from pathlib import Path
import argparse,hashlib,json,importlib.util,subprocess,sys,os
P=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
def apply(path,records):
 s=path.read_text()
 for r in records:
  n=r.get('occurrences',r.get('count'));assert s.count(r['before'])==n,(path.name,r['before'])
  s=s.replace(r['before'],r['after'])
 path.write_text(s)
def main():
 a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True,help='immutable #7605 research/p104-timed-helper757 directory');a.add_argument('--work',type=Path,required=True);a.add_argument('--stage',choices=['prepare','native','signed','all'],default='all');x=a.parse_args()
 for f,h in read(P/'PINS.json').items():assert hashlib.sha256((P/f).read_bytes()).hexdigest()==h,f
 source=x.source.resolve();work=x.work.resolve();spec=read(P/'SOURCE.json')
 assert hashlib.sha256((source/'application.py').read_bytes()).hexdigest()==spec['base_application_sha256']
 m=importlib.util.spec_from_file_location('base_application',source/'application.py');b=importlib.util.module_from_spec(m);m.loader.exec_module(b)
 b.authenticate()
 if x.stage in ('prepare','all'):
  assert not work.exists(),'Use a new empty output directory; do not overwrite prior evidence'
  b.prepare(work,b.authenticate())
  for rel in ['producer54/reroute/WORD.json.gz','frozen-composition/CANDIDATE-WORD.json.gz']:(work/rel).write_bytes((P/'data/word.json.gz').read_bytes())
  (work/'frozen-composition/W2-EDITS.json').write_bytes((P/'data/edits7605.json').read_bytes())
  (work/'frozen-composition/CANDIDATE-INVOICE.json').write_bytes((P/'evidence/invoice-w2.json').read_bytes())
  apply(work/'producer54/validation_native/run.py',read(P/'adapters/native.json'))
  apply(work/'producer54/validation_signed/run.py',read(P/'adapters/signed.json'))
  s=(work/'inputs/pr7480/adapt.py').read_text();assert s.count('(74, 50, 68)')==1
  (work/'producer54/validation_signed/w2_adapt.py').write_text(s.replace('(74, 50, 68)','(113, 50, 68)'))
 if x.stage=='prepare':return
 temp=work.parent/'w2tmp';temp.mkdir(exist_ok=True);env=dict(os.environ,TEMP=str(temp),TMP=str(temp))
 for stage in (['native','signed'] if x.stage=='all' else [x.stage]):
  if stage=='signed':assert read(work/'producer54/validation_native/NATIVE-RESULT.json')['status']=='PASS_W2_ADAPTED_COMPLETE_NATIVE'
  subprocess.run([sys.executable,'-I','-B',str(P/'windows_path_shim.py'),str(work/f'producer54/validation_{stage}/run.py')],env=env,check=True,timeout=1200)
 print('PASS W2 candidate-adapted application; five inherited assumptions remain')
if __name__=='__main__':main()
