#!/usr/bin/env python3
"""Reproduce a two-pass structural bitword from its pinned source producers.

External provenance check only: all word acceptance is performed by the complete
source verifier, and this script never writes inside the candidate package.
"""
import argparse,gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('package',type=Path);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--rounds',type=int,default=2);a=ap.parse_args()
 source=a.package.resolve();bit=source/'bitword';prod=bit/'producer';work=a.work.resolve();assert not work.exists() and not work.is_relative_to(source);work.mkdir()
 before={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()}
 run=lambda args:subprocess.run([sys.executable,'-B']+list(map(str,args)),check=True)
 raw=work/'raw';run([prod/'paired_cube_bit_word.py','--p','10','--out',raw])
 pkg=work/'pkg';shutil.copytree(bit/'bit',pkg/'bit');shutil.copytree(bit/'references',pkg/'references');(pkg/'selected').mkdir()
 current=raw
 for cycle in range(a.rounds):
  phys=work/f'phys{cycle}';final=work/f'final{cycle}'
  run([prod/'make_physical.py','--src',current,'--out',phys,'--bank-parity'])
  selected=pkg/'selected/bit'
  if selected.exists():shutil.rmtree(selected)
  shutil.copytree(phys,selected)
  run([prod/'descent.py',pkg,final]);current=final
 names=['graph_p10.json','kchron_p10.json','profile_p10.json','word_p10.json.gz','frames_p10.json.gz']
 result={}
 for name in names:
  expected=(bit/'selected/bit'/name).read_bytes();actual=(current/name).read_bytes()
  assert (gzip.decompress(expected)==gzip.decompress(actual)) if name.endswith('.gz') else expected==actual,name
  result[name]=dict(pinned=sha(bit/'selected/bit'/name),rebuilt=sha(current/name),expanded=hashlib.sha256(gzip.decompress(actual)).hexdigest() if name.endswith('.gz') else sha(current/name))
 after={str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()};assert before==after
 report=dict(status='PASS_STRUCTURAL_PRODUCER_REGENERATION_ALL_FIVE_FILES',source=str(source),rounds=a.rounds,source_unchanged=True,source_manifest_sha256=sha(source/'MANIFEST.json'),checker_sha256=sha(Path(__file__)),files=result)
 (work/'REGENERATION.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print('PASS',report['status'],flush=True)
if __name__=='__main__':main()
