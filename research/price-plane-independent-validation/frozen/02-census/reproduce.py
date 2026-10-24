#!/usr/bin/env python3
"""Reproduce frozen census into an isolated temp directory and compare hashes."""
from pathlib import Path
from hashlib import sha256
import argparse,json,shutil,subprocess,sys,tempfile
p=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--revision',choices=('v1','v2'),default='v1');ap.add_argument('--capsule',type=Path,required=True);a=ap.parse_args()
script=p/('census.py' if a.revision=='v1' else 'census-v2.py')
with tempfile.TemporaryDirectory(prefix='independent-census-') as td:
 t=Path(td);shutil.copyfile(script,t/script.name)
 r=subprocess.run([sys.executable,'-B',str(t/script.name),str(a.capsule.resolve())],capture_output=True,text=True)
 if r.returncode:print(r.stderr);raise SystemExit(r.returncode)
 for name in ('INVOICE-'+a.revision+'.json','CHRONOLOGY-'+a.revision+'.json'):
  expected=sha256((p/name).read_bytes()).hexdigest();actual=sha256((t/name).read_bytes()).hexdigest()
  if actual!=expected:raise RuntimeError((name,expected,actual))
 print('PASS_ISOLATED_INDEPENDENT_CENSUS_'+a.revision.upper())
