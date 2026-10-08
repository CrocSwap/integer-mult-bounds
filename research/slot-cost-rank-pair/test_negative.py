#!/usr/bin/env python3
"""Adversarial controls for all-rank physical compilation; inherited notices apply."""
import sys
sys.dont_write_bytecode=True
import gzip,json,tempfile,subprocess
from pathlib import Path
import verify

def rejected(label,call):
    try:call()
    except (AssertionError,IndexError,ValueError):
        print('PASS rejected '+label,flush=True)
    else:raise AssertionError('Invalid control accepted: '+label)

def require_digest(path,expected):assert verify.sha(path)==expected

def main():
    for name in ('verify.py','compiler.py'):
        optimized=subprocess.run([sys.executable,'-B','-O',str(verify.HERE/name)],capture_output=True,text=True)
        assert optimized.returncode!=0 and 'Assertions must remain enabled' in optimized.stderr
        print('PASS rejected optimized Python '+name,flush=True)
    work=verify.ROOT/'build/slot-cost-rank-pair';work.mkdir(parents=True,exist_ok=True)
    original=json.loads(gzip.decompress((verify.HERE/'frame-word-23.json.gz').read_bytes()))
    with tempfile.TemporaryDirectory(prefix='negative-',dir=work) as temporary:
        path=Path(temporary)/'mutated.json'
        bad=dict(original);bad['ops']=original['ops'][1:]
        path.write_text(json.dumps(bad,separators=(',',':')))
        rejected('omitted physical XOR',lambda:verify.replay(path))
        bad=dict(original);bad['R']=original['R']-1
        path.write_text(json.dumps(bad,separators=(',',':')))
        rejected('understated physical role count',lambda:verify.replay(path))
        bad=dict(original);bad['events']=original['events'][1:]
        path.write_text(json.dumps(bad,separators=(',',':')))
        rejected('omitted paid physical transition',lambda:verify.prepare(path,Path(temporary)/'mutated.bin'))
        records=json.loads((verify.HERE/'frame-compiler.json').read_text())
        for name in ('frame-word-23.json.gz','frame-profiles-23.json'):
            path.write_bytes((verify.HERE/name).read_bytes()+b' ')
            rejected('changed digest '+name,lambda name=name:require_digest(path,records['artifact_sha256'][name]))
    print('PASS all seven all-rank physical negative controls',flush=True)

if __name__=='__main__':main()
