#!/usr/bin/env python3
"""Integrity, scope and receipt controls; no fixture/source is overwritten."""
from pathlib import Path
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from types import ModuleType

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("primary_control",ROOT/"verify.py")
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
passed=[]


def reject(label, fn):
    try:fn()
    except ValueError:passed.append(label);return
    raise ValueError("accepted corrupt control: "+label)


def main():
    v.runtime.authenticate()
    receipt=json.loads((ROOT/"RESULT.json").read_text())
    v.runtime.check_receipt(receipt,receipt)
    bad=json.loads(json.dumps(receipt));bad['no_new_kappa']=1
    reject('typed-receipt',lambda:v.runtime.check_receipt(receipt,bad))
    for name,args in [('bool-N',(True,3,7,20,5,0,0,True)),
                      ('empty-packet',(0,3,7,20,5,0,0,True)),
                      ('short-source',(2,3,6,20,5,0,0,True)),
                      ('past-last-prefix',(2,3,7,20,5,0,2,True)),
                      ('negative-pass',(2,3,7,20,5,-1,0,True))]:
        reject(name,lambda a=args:v.budget(*a))
    module='packet_engine'
    v.need(module not in sys.modules,'preload control isolated')
    sys.modules[module]=ModuleType(module)
    try:reject('preloaded-runtime',v.runtime.load_runtime)
    finally:del sys.modules[module]
    # The one owned temporary directory is removed on both success and failure.
    with tempfile.TemporaryDirectory(prefix='packet-backing-control-') as tmp:
        dst=Path(tmp)/'package';shutil.copytree(ROOT,dst)
        for p in dst.rglob('*'):
            if p.is_dir():p.chmod(0o700)
            elif p.is_file():p.chmod(0o600)
        source=dst/'sources/pr2697/packet_engine.py';original=source.read_bytes()
        source.write_bytes(original+b'\n# defect control\n')
        reject('source-byte-corruption',lambda:v.runtime.authenticate(dst))
        source.write_bytes(original)
        manifest=dst/'SNAPSHOTS.json';manifest.write_bytes(manifest.read_bytes()+b'\n')
        reject('manifest-corruption',lambda:v.runtime.authenticate(dst))
    print(json.dumps({'status':'PASS_PACKET_BACKING_CONTROLS','controls':passed},sort_keys=True))


if __name__=='__main__':main()
