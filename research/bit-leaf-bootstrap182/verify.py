#!/usr/bin/env python3
"""Source-pinned exact finite bootstrap check; inherited physical words stay explicit."""
import hashlib,json,sys,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def verify():
    if sys.flags.optimize:raise ValueError('Assertions must remain enabled')
    manifest=json.loads((HERE/'SOURCE.json').read_text())
    for path,digest in manifest['repository_files'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,('Repository source drift',path)
    for path,digest in manifest['package_files'].items():
        assert hashlib.sha256((HERE/path).read_bytes()).hexdigest()==digest,('Package source drift',path)
    import certificate
    actual=certificate.generate();expected=json.loads((HERE/'certificate.json').read_text())
    assert actual==expected,'Canonical certificate differs'
    subprocess.run([sys.executable,'-B',str(HERE/'independent_audit.py')],check=True,stdout=subprocess.PIPE,text=True)
    selected=actual['selected']
    print('PASS pinned source chain, paid supplier moments, three finite bootstrap levels, 47 strict constraints, 7 margins, 11 controls per depth, adjacent grids')
    print('kappa='+actual['kappa'])
    print('Physical words are inherited unchanged; this command does not replay them.')
if __name__=='__main__':verify()
