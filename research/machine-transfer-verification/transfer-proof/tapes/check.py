#!/usr/bin/env python3
"""Rebuild the literal tape transducers and audit every declared theorem."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
SOURCES = ('TapeStack.lean', 'TapeStackPush.lean')
ALLOWED = {'propext', 'Quot.sound', 'Classical.choice'}
AUDIT = re.compile(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)")
DECL = re.compile(r'^\s*(?:@\[[^\]]*\]\s*)?theorem\s+(\w+)\b', re.M)

def need(condition, message):
    if not condition:
        raise SystemExit(message)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mathlib-project', type=Path, required=True)
    parser.add_argument('--lean-bin', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=HERE / 'verification')
    args = parser.parse_args()
    project, lean_bin, output = (p.resolve() for p in (args.mathlib_project, args.lean_bin, args.output))
    need((project/'lean-toolchain').read_text().strip() == 'leanprover/lean4:v4.21.0', 'Wrong Lean pin')
    packages = json.loads((project/'lake-manifest.json').read_text())['packages']
    mathlib = [p for p in packages if p['name']=='mathlib']
    need(len(mathlib)==1 and mathlib[0]['rev']=='308445d7985027f538e281e18df29ca16ede2ba3', 'Wrong Mathlib pin')
    env = os.environ.copy()
    env['PATH'] = str(lean_bin)+os.pathsep+env.get('PATH','')
    version = subprocess.check_output([str(lean_bin/'lean'),'--version'],text=True).strip()
    need(re.search(r'version 4\.21\.0(?:,|\s)',version), 'Wrong actual compiler: '+version)
    output.mkdir(parents=True,exist_ok=True)
    receipt = {'status':'PASS','compiler':version,'mathlib_revision':mathlib[0]['rev'],'modules':{}}
    with tempfile.TemporaryDirectory(prefix='tape-proof-') as temp:
        directory = Path(temp)
        env['LEAN_PATH'] = str(directory)
        for name in SOURCES:
            source = HERE/name
            text = source.read_text()
            names = {source.stem+'.'+n for n in DECL.findall(text)}
            expected_prints = {n if '.' in n else source.stem+'.'+n for n in
                               re.findall(r'^#print axioms (\S+)\s*$',text,re.M)}
            need(names==expected_prints, 'Incomplete source axiom coverage: '+name)
            need(not re.search(r'^\s*(?:axiom|constant)\s',text,re.M), 'Custom axiom declaration')
            need(not re.search(r'\b(?:sorry|admit|native_decide)\b',text), 'Proof escape in '+name)
            local = directory/name
            shutil.copy2(source,local)
            result = subprocess.run([str(lean_bin/'lake'),'env','lean','--root='+str(directory),
                                     '-o',str(local.with_suffix('.olean')),str(local)],
                                    cwd=project,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            (output/(source.stem+'.log')).write_text(result.stdout)
            need(result.returncode==0, 'Compilation failed: '+name+'; see verification log')
            reports = AUDIT.findall(result.stdout)
            need({n for n,_ in reports}==names and len(reports)==len(names), 'Incomplete compiler audit: '+name)
            axioms = {n:sorted(filter(None,(x.strip() for x in a.split(',')))) for n,a in reports}
            need(all(set(a)<=ALLOWED for a in axioms.values()), 'Nonstandard axiom in '+name)
            receipt['modules'][name] = {
                'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                'theorem_count':len(names),'axioms':axioms,
            }
            print(f'PASS {name}: {len(names)} theorem audits',flush=True)
    receipt['new_theorem_count'] = sum(x['theorem_count'] for x in receipt['modules'].values())
    receipt['scope'] = 'Literal head-local push/pop transducers and marked-tape round trip. Entire recursive scheduler, arbitrary child cleanup and global machine remain external.'
    (output/'axiom-audit.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('PASS all tape-transducer sources, finite tables and axiom audits')

if __name__=='__main__':
    main()
