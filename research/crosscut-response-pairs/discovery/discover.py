#!/usr/bin/env python3
"""Reproduce the finite exploratory pair search; the independent verifier is authoritative."""
from pathlib import Path
import argparse,gzip,hashlib,json,shutil,subprocess,sys
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--baseline-package',required=True,type=Path);ap.add_argument('--export-dir',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);ap.add_argument('--cxx',default='clang++');ap.add_argument('--include',action='append',default=[]);a=ap.parse_args();pkg=a.baseline_package.resolve();out=a.output.resolve();X=a.export_dir.resolve()
if out.exists():raise SystemExit('Choose a new output directory')
out.mkdir(parents=True);(out/'input').mkdir();
for n in ['249-records.bin','249-states.json','frames.json']:shutil.copy2(X/n,out/'input'/n)
st=json.loads((out/'input/249-states.json').read_text());assert hashlib.sha256((out/'input/249-records.bin').read_bytes()).hexdigest()==st['record_sha256']
(out/'baseline-candidates.json').write_bytes(gzip.decompress((pkg/'inputs/candidates.json.gz').read_bytes()));shutil.copy2(pkg/'inputs/descent-selection.json',out/'baseline-descent-selection.json')
cmd=[a.cxx,'-std=c++17','-O2','-I',str(pkg/'vendor')]
for inc in a.include:cmd+=['-I',inc]
cmd += [str(HERE/'scan.cpp'),'-o',str(out/'scan')];subprocess.run(cmd,check=True)
subprocess.run([str(out/'scan'),str(out/'input'),str(out),'676559','680080','700582','727593'],check=True)
for script in ['pairs.py','geometry_pairs.py','rank_pairs.py','select_greedy.py']:subprocess.run([sys.executable,str(HERE/script),str(out)],check=True)
print('Frozen proposed witness:',out/'greedy/candidates.json');print('Run the literal transform and all independent checkers; search output is not a certificate.')
