"""Explicit W3 overlay of authenticated #7616 preparation; five premises remain."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent

def main():
 if not __debug__:raise RuntimeError('Assertions required')
 a=argparse.ArgumentParser();a.add_argument('--w2',type=Path,required=True);a.add_argument('--source',type=Path,required=True);a.add_argument('--work',type=Path,required=True);a.add_argument('--stage',choices=['prepare','native','signed','all'],default='all');x=a.parse_args()
 for f,h in json.loads((P/'PINS.json').read_text()).items():assert hashlib.sha256((P/f).read_bytes()).hexdigest()==h,f
 assert hashlib.sha256((x.w2/'reproduce.py').read_bytes()).hexdigest()=='fc8ff4f56e25cc9579035900efa2b2e3614937a63717e18ee22afd1d83a5b8e2'
 work=x.work.resolve();env=dict(os.environ);tmp=work.parent/'w3tmp';tmp.mkdir(exist_ok=True);env.update(TEMP=str(tmp),TMP=str(tmp))
 if x.stage in ('prepare','all'):
  assert not work.exists(),'Use a new empty work directory'
  subprocess.run([sys.executable,'-B',str(x.w2/'reproduce.py'),'--source',str(x.source),'--work',str(work),'--stage','prepare'],check=True,timeout=1200,env=env)
  for src,dst in [('data/word.json.gz','producer54/reroute/WORD.json.gz'),('data/word.json.gz','frozen-composition/CANDIDATE-WORD.json.gz'),('data/edits.json','frozen-composition/W2-EDITS.json'),('data/invoice.json','frozen-composition/CANDIDATE-INVOICE.json'),('runners/native.py','producer54/validation_native/run.py'),('runners/signed.py','producer54/validation_signed/run.py'),('runners/precision_adapter.py','producer54/validation_signed/w2_adapt.py')]:
   q=work/dst;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((P/src).read_bytes())
 if x.stage=='prepare':return
 for stage in (['native','signed'] if x.stage=='all' else [x.stage]):
  if stage=='signed':assert json.loads((work/'producer54/validation_native/NATIVE-RESULT.json').read_text())['status']=='PASS_W3_ADAPTED_COMPLETE_NATIVE'
  subprocess.run([sys.executable,'-B',str(P/'windows_path_shim.py'),str(work/f'producer54/validation_{stage}/run.py')],check=True,timeout=1200,env=env)
if __name__=='__main__':main()
