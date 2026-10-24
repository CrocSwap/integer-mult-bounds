#!/usr/bin/env python3
"""Offline positive-result replay; standard library only. Apache-2.0."""
from pathlib import Path
import hashlib,json,subprocess,sys
P=Path(__file__).resolve().parent
def need(c,m):
    if not c: raise ValueError(m)
def main():
    manifest=json.loads((P/'MANIFEST.json').read_text(encoding='utf8'))
    actual={f.relative_to(P).as_posix() for f in P.rglob('*') if f.is_file() and '__pycache__' not in f.parts and f.name!='MANIFEST.json'}
    need(actual==set(manifest),'Exact manifest file set')
    for name,digest in manifest.items():need(hashlib.sha256((P/name).read_bytes()).hexdigest()==digest,'Hash mismatch: '+name)
    commands=[['retiming/retiming_verify.py'],['compiler/clifford_compile.py','--expected','compiler/CLIFFORD-EXPECTED.json'],['compiler/test.py','--expected','compiler/EXPECTED.json'],['decoder/testformula.py','--graph','inputs/round3-contact-graph.txt'],['decoder/paired_test.py','--expected','decoder/PAIRED-EXPECTED.json']]
    for command in commands:
        args=[sys.executable,'-I','-B']+(['-O'] if sys.flags.optimize else [])+[str(P/command[0])]+[str(P/x) if '/' in x and not x.startswith('--') else x for x in command[1:]]
        run=subprocess.run(args,cwd=P,capture_output=True,text=True,encoding='utf8',timeout=120)
        need(run.returncode==0,run.stdout+run.stderr)
        out=json.loads(run.stdout)
        if command[0]=='decoder/testformula.py':need(out==json.loads((P/'decoder/TRANSVECTION-EXPECTED.json').read_text(encoding='utf8')),'Tariff expected receipt')
        print(out['status'],flush=True)
    print('PASS_NATIVE_CLIFFORD_GAUGE_COMPILER new_kappa=false')
if __name__=='__main__':main()
