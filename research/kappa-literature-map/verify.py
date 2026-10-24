#!/usr/bin/env python3
"""Exact, bounded, network-free reproduction of a scoped literature dossier."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def require(ok,msg):
 if not ok:raise ValueError(msg)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=argparse.ArgumentParser(description=__doc__)
 a.add_argument('--quick',action='store_true',help='Skip the expensive hook replay.')
 args=a.parse_args()
 manifest=json.loads((P/'MANIFEST.json').read_text(encoding='utf-8'))
 actual={p.relative_to(P).as_posix() for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='MANIFEST.json'}
 require(actual==set(manifest['files']),'manifest file inventory mismatch')
 for name,pin in manifest['files'].items():require(digest(P/name)==pin,'source hash drift: '+name)
 python=[sys.executable,'-I','-B']+(['-O'] if sys.flags.optimize else [])
 receipts={}
 for lane in ('root','quantum','algebra','ram'):
  r=subprocess.run(python+[str(P/lane/'test.py')],capture_output=True,text=True,encoding='utf-8',timeout=120,cwd=P)
  require(r.returncode==0,lane+' failed: '+r.stderr)
  rows=[json.loads(line) for line in r.stdout.splitlines() if line.startswith('{')]
  require(len(rows)==1,lane+' missing unique receipt')
  require(rows[0]==json.loads((P/lane/'EXPECTED.json').read_text(encoding='utf-8')),lane+' expected receipt mismatch')
  receipts[lane]=rows[0].get('status','PASS')
 r=subprocess.run(python+[str(P/'algebra/anchor_check.py'),'--check',str(P/'algebra/ANCHOR-EXPECTED.json')],capture_output=True,text=True,encoding='utf-8',timeout=120,cwd=P)
 require(r.returncode==0,'anchor compiler failed: '+r.stderr)
 receipts['anchor']=json.loads(r.stdout)['status']
 if not args.quick:
  r=subprocess.run(python+[str(P/'algebra/hook_check.py'),'--check',str(P/'algebra/HOOK-EXPECTED.json')],capture_output=True,text=True,encoding='utf-8',timeout=570,cwd=P)
  require(r.returncode==0,'hook failed: '+r.stderr)
  report=json.loads(r.stdout.splitlines()[-1])
  require(report['cases']==6,'hook case count')
  receipts['hook']=report['status']
 bibliography=json.loads((P/'BIBLIOGRAPHY.json').read_text(encoding='utf-8'))
 require(bibliography['record_count']==74,'bibliography record count')
 print(json.dumps({'status':'PASS_KAPPA_LITERATURE_MAP','receipts':receipts,'source_records':74,'hook_replayed':not args.quick,'new_kappa':False},sort_keys=True))
if __name__=='__main__':main()
