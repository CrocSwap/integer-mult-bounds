#!/usr/bin/env python3
"""Offline complete reproduction; package check alone never certifies the bound."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent
if not __debug__:raise SystemExit('Assertions required')
def integrity():
 expected=json.loads((P/'MANIFEST.json').read_text())['files']
 for rel,want in expected.items():
  p=P/rel;assert p.is_file() and not p.is_symlink(),rel
  assert hashlib.sha256(p.read_bytes()).hexdigest()==want,'Changed package file: '+rel
 actual={x.relative_to(P).as_posix()for x in P.rglob('*')if x.is_file()and x.name!='MANIFEST.json'}
 actual.update(x.relative_to(P).as_posix()for x in P.rglob('MANIFEST.json')if x!=P/'MANIFEST.json')
 assert actual==set(expected),'Missing or unpinned package member'
 return hashlib.sha256((P/'MANIFEST.json').read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);ap.add_argument('--check-package',action='store_true');a=ap.parse_args()
 digest=integrity()
 if a.check_package:
  for p in P.rglob('*.py'):compile(p.read_bytes(),str(p),'exec')
  print('PASS package hashes and Python syntax only; no new mathematical validation');return
 assert a.output is not None,'--output is required';out=a.output.resolve();assert not out.exists()and not out.is_relative_to(P);out.mkdir(parents=True);start=time.monotonic()
 prime=json.loads((P/'prime-proof.json').read_text())['prime'];q=prime['q'];assert q==2**127-1 and prime['p']==127 and prime['iterations']==125
 assert all(127%d for d in range(2,12));r=[4]
 for _ in range(125):r.append((r[-1]*r[-1]-2)%q)
 assert r==prime['residues'] and r[-1]==0 and q>2**80
 # Lucas-Lehmer sufficiency is the stated mathematical criterion, not a new Lean build.
 subprocess.run([sys.executable,'-B',str(P/'source/verify.py'),'--output',str(out/'supplier')],check=True)
 verification=json.loads((out/'supplier/verification.json').read_text());assert verification['inputs_unchanged'] and verification['status'].startswith('PASS')
 admission=out/'admission.json';admission.write_text(json.dumps(dict(status='PASS fresh complete gen5b-full (PR300) original supplier',inputs_unchanged=True,supplier_manifest=verification['manifest_sha256'],prime_checked=True)))
 subprocess.run([sys.executable,'-B',str(P/'prime_eight_port.py'),'--run',str(out/'supplier'),'--admission',str(admission),'--output',str(out/'certificate.json')],check=True)
 got=json.loads((out/'certificate.json').read_text());expected=json.loads((P/'certificate.json').read_text())
 for key in ['kappa','coarse','excluded_coarse','public_accepted','public_excluded','independent_accepted','independent_excluded','bit_profile','complex_profile','complex_saving','rare_density','prime','ordinary_chain','steps','delta_linear','assembly','eta','beta','selector','normalizer','coefficient']:
  assert got[key]==expected[key],key
 assert integrity()==digest
 report=dict(status='PASS complete gen5b-full fixed-prime eight-level reproduction',kappa=got['kappa'],seconds=time.monotonic()-start,package_unchanged=True,manifest_sha256=digest,prime_checked=True,full_parent_stages=verification['fresh_stages'],new_Lean_build=False,unconditional=False)
 (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
