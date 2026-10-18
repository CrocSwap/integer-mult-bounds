#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exercise read-only replay and source/receipt rejection in separate processes."""
import importlib.util
import json
from pathlib import Path
import py_compile
import shutil
import struct
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent


def require(ok,message):
    if not ok:
        raise ValueError(message)


def replay(package,expected):
    proc=subprocess.run([sys.executable,'-I','-B','-O',str(package/'verify.py')],
                        capture_output=True,text=True,timeout=30)
    require((proc.returncode==0)==expected,proc.stdout+proc.stderr)
    if expected:
        require(json.loads(proc.stdout)['status']=='PASS_FIXED_TAPE_UNIT_CARRY','successful exact replay')
    return proc


def main():
    checked=[]
    with tempfile.TemporaryDirectory(prefix='unit-carry-controls-') as tmp:
        root=Path(tmp)
        def copy(name):
            dest=root/name
            shutil.copytree(HERE,dest,ignore=shutil.ignore_patterns('__pycache__'))
            return dest
        for name,relative,edit in (
            ('changed source','predecessor/shear.py',lambda raw:raw+b'\n'),
            ('changed table','TABLE.json',lambda raw:raw.replace(b'"entry": 0',b'"entry": 1',1)),
            ('wrong receipt type','RESULT.json',lambda raw:raw.replace(b'"physical_tapes": 14',b'"physical_tapes": true',1))):
            p=copy(name);f=p/relative;f.write_bytes(edit(f.read_bytes()));replay(p,False);checked.append(name)
        p=copy('missing receipt');(p/'RESULT.json').unlink();replay(p,False);checked.append('missing receipt')
        p=copy('preloaded module')
        script='import sys,types; sys.path.insert(0,sys.argv[1]); import bootstrap; sys.modules["machine"]=types.ModuleType("machine"); bootstrap.load()'
        proc=subprocess.run([sys.executable,'-I','-B','-c',script,str(p)],capture_output=True,text=True,timeout=10)
        require(proc.returncode!=0 and 'refuse preloaded source module' in proc.stderr,'preloaded module control')
        checked.append('preloaded module')
        p=copy('stale bytecode')
        source=p/'predecessor/machine.py'
        poison=root/'poison.py';poison.write_text('raise RuntimeError("STALE_BYTECODE_EXECUTED")\n')
        cache=Path(importlib.util.cache_from_source(str(source)))
        cache.parent.mkdir(exist_ok=True)
        py_compile.compile(str(poison),cfile=str(cache),doraise=True)
        raw=cache.read_bytes();stat=source.stat()
        cache.write_bytes(raw[:8]+struct.pack('<II',int(stat.st_mtime)&0xffffffff,stat.st_size&0xffffffff)+raw[16:])
        replay(p,True);checked.append('stale bytecode ignored')
        p=copy('read-only export')
        files=[f for f in p.rglob('*') if f.is_file()]
        before={str(f.relative_to(p)):f.read_bytes() for f in files}
        for f in files:f.chmod(0o444)
        dirs=[f for f in p.rglob('*') if f.is_dir()]
        for d in dirs:d.chmod(0o555)
        p.chmod(0o555)
        try:
            replay(p,True)
            require(before=={str(f.relative_to(p)):f.read_bytes() for f in p.rglob('*') if f.is_file()},'read-only unchanged files')
        finally:
            p.chmod(0o755)
            for d in dirs:d.chmod(0o755)
            for f in files:f.chmod(0o644)
        checked.append('read-only Git-free optimized replay')
        p=copy('emission refuses overwrite')
        proc=subprocess.run([sys.executable,'-I','-B',str(p/'verify.py'),'--emit'],capture_output=True,text=True,timeout=10)
        require(proc.returncode!=0 and 'refuses existing artifacts' in proc.stderr,'emission boundary')
        checked.append('emission refuses overwrite')
    print(json.dumps({'status':'PASS_UNIT_CARRY_INTEGRITY','checks':checked},indent=2))


if __name__=='__main__':
    main()
