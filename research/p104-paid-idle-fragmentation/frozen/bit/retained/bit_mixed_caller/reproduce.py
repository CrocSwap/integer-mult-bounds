#!/usr/bin/env python3
"""Rebuild this source-local caller package; optional sibling admission."""
from pathlib import Path
import subprocess,sys,json,hashlib,argparse
H=Path(__file__).resolve().parent

def run(*args):
    subprocess.run([str(x)for x in args],cwd=H,check=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--admission',action='store_true');a=ap.parse_args()
    for script in ('search_binary_root.py','binary_mixed_caller.py','all_site_projectors.py'):
        run(sys.executable,H/script)
    run(sys.executable,H/'binary_mixed_caller.py','--children','4,4,4,4','--name','GOAL-BALANCED-16-CALLER')
    for name in ('search_all_sites','price_all_patterns'):
        run('g++','-O3','-std=c++17',H/(name+'.cpp'),'-o',H/name)
    run(H/'search_all_sites',H/'ALL-SITE-PROJECTORS.txt',H/'ALL-SITE-PATTERNS.json')
    run(sys.executable,H/'prepare_pattern_bounds.py')
    run(H/'price_all_patterns',H/'PATTERN-BOUND-TABLES.txt',H/'PATTERN-FINITE-BOUND.json')
    run(sys.executable,H/'formal_root_relaxation.py')
    run(H/'price_all_patterns',H/'FORMAL-RANK2-BOUND-TABLES.txt',H/'FORMAL-RANK2-BOUND.json')
    run(sys.executable,H/'prepare_pattern_bounds.py','--kappa','.0042','--prefix','GOAL4200')
    run(sys.executable,H/'formal_root_relaxation.py','--prefix','GOAL4200')
    run(H/'price_all_patterns',H/'FORMAL-GOAL4200-BOUND-TABLES.txt',H/'FORMAL-GOAL4200-BOUND.json')
    run(sys.executable,H/'goal_economics.py')
    for name,sha in [('BINARY-MIXED-CALLER','86c4574d47e406e560b3ae2602e52501d4da4bc4c082b4f31b21f6cfef362cc3'),('GOAL-BALANCED-16-CALLER','8824b4cc22ba67b576b9d648e88483bb47d0f54678b94c7e9e3d90b42e804df9')]:
        assert hashlib.sha256((H/(name+'.json.gz')).read_bytes()).hexdigest()==sha
    for name in ('PATTERN-FINITE-BOUND','FORMAL-RANK2-BOUND','FORMAL-GOAL4200-BOUND'):
        assert json.loads((H/(name+'.json')).read_text())['global_margin_upper_integer']<0
    if a.admission:run(sys.executable,H.parent/'root/admit_binary_mixed.py')
    print('PASS_REPRODUCED_BINARY_MIXED_CALLERS_AND_TARGET_CEILINGS')

if __name__=='__main__':main()
