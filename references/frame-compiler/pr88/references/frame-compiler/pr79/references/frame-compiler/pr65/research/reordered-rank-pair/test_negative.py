#!/usr/bin/env python3
"""Adversarial controls for the reordered serialized words and scheduling."""
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

def main():
    optimized=subprocess.run([sys.executable,'-B','-O',str(verify.HERE/'verify.py')],capture_output=True,text=True)
    assert optimized.returncode!=0 and 'Assertions must remain enabled' in optimized.stderr
    print('PASS rejected optimized Python invocation',flush=True)
    work=verify.ROOT/'build/reordered-rank-pair';work.mkdir(parents=True,exist_ok=True)
    original=json.loads(gzip.decompress((verify.HERE/'frame-word-23.json.gz').read_bytes()))
    with tempfile.TemporaryDirectory(prefix='negative-',dir=work) as temporary:
        path=Path(temporary)/'mutated.json'
        bad=dict(original);bad['ops']=original['ops'][1:]
        path.write_text(json.dumps(bad,separators=(',',':')))
        rejected('omitted physical XOR',lambda:verify.replay(path))
        bad=dict(original);bad['R']=original['R']-1
        path.write_text(json.dumps(bad,separators=(',',':')))
        rejected('understated physical role count',lambda:verify.replay(path))
        records=json.loads((verify.HERE/'frame-compiler.json').read_text())
        for name in ('frame-word-23.json.gz','frame-profiles-23.json'):
            path.write_bytes((verify.HERE/name).read_bytes()+b' ')
            rejected('changed digest '+name,lambda name=name:require_digest(path,records['artifact_sha256'][name]))
    # Two equal-rank regions with an actual dependency must not be reversed.
    blocks=[{'rank':1,'nodes':[1],'inputs':[],'candidates':[]},
            {'rank':1,'nodes':[2],'inputs':[1],'candidates':[]}]
    invalid=lambda h:(None,blocks,[],{}, {1:0,2:1},{},[0,1],None)
    rejected('backward region dependency',lambda:verify.reordered_build(invalid,'reverse-node')(23))
    print('PASS all six reordered-word negative controls',flush=True)

def require_digest(path,expected):assert verify.sha(path)==expected

if __name__=='__main__':main()
