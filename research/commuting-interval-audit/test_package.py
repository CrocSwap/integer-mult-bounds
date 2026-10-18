#!/usr/bin/env python3
"""Run the complete audit in a read-only relocated package and reject faults."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent

def run(path,good):
 p=subprocess.run([sys.executable,'-I','-O','-B',str(path/'verify.py')],capture_output=True,text=True,timeout=240)
 if good:
  if p.returncode:raise RuntimeError(p.stderr)
  r=json.loads(p.stdout)
  if r['status']!='PASS_COMMUTING_INTERVAL_AUDIT':raise ValueError('missing mathematical receipt')
  return r
 if not p.returncode:raise ValueError('package fault accepted')
 return p.stderr

def main():
 with tempfile.TemporaryDirectory(prefix='commuting interval ') as td:
  target=Path(td)/'read only';shutil.copytree(HERE,target)
  for p in target.rglob('*'):
   if p.is_file():p.chmod(0o444)
   elif p.is_dir():p.chmod(0o555)
  target.chmod(0o555)
  phase=subprocess.run([sys.executable,'-I','-O','-B',str(target/'check_phase_algebra.py')],capture_output=True,text=True,timeout=30)
  if phase.returncode or 'PASS_PHASE_ALGEBRA identities=108' not in phase.stdout:raise RuntimeError(phase.stderr or phase.stdout)
  r=run(target,True)
  target.chmod(0o755)
  for p in target.rglob('*'):
   if p.is_file():p.chmod(0o644)
   elif p.is_dir():p.chmod(0o755)
  faults=[]
  src=target/'vendor/dirty.py';old=src.read_bytes();src.write_bytes(old+b'\n# altered\n')
  if 'source drift' not in run(target,False):raise ValueError('wrong source-fault reason')
  faults.append('altered_source');src.write_bytes(old)
  src.unlink();run(target,False);faults.append('missing_source');src.write_bytes(old)
  pins=target/'SOURCES.json';old=pins.read_text();d=json.loads(old);d['sha256']['vendor/dirty.py']='0'*64;pins.write_text(json.dumps(d))
  if 'source drift' not in run(target,False):raise ValueError('wrong pin-fault reason')
  faults.append('wrong_source_pin');pins.write_text(old)
  cert=target/'CERTIFICATE.json';d=json.loads(cert.read_text());d['intervals']+=1;cert.write_text(json.dumps(d))
  if 'certificate mismatch' not in run(target,False):raise ValueError('wrong certificate-fault reason')
  faults.append('altered_receipt')
 print('PASS_COMMUTING_INTERVAL_PACKAGE',json.dumps({'intervals':r['intervals'],'phase_identities':108,'package_faults':faults,'read_only_relocation':True}))
if __name__=='__main__':main()
