"""Portable wrappers around unchanged measured full-network code; Apache-2.0."""
from hashlib import sha256
import json
import os
from pathlib import Path
import runpy
import sys
import types

ROOT=Path(__file__).resolve().parent


def need(ok,why):
    if not ok:raise ValueError(why)


def digest(path):
    h=sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def authenticate():
    manifest=json.loads((ROOT/'CODE-SOURCES.json').read_text())
    need(manifest['schema_version']==1,'code/source manifest version')
    for name,expected in manifest['files'].items():
        path=ROOT/name
        need(not path.is_symlink() and path.is_file() and digest(path)==expected,'exact protected source: '+name)
    expected_code={p for p in manifest['files'] if Path(p).suffix in ('.py','.c')}
    actual_code={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and p.suffix in ('.py','.c')}
    need(actual_code==expected_code,'complete protected code census')
    need(not any(p.is_symlink() for p in ROOT.rglob('*')),'no package symlinks')
    return manifest


def source_module(name,path):
    authenticate();raw=path.read_bytes()
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module


def external(path):
    path=Path(path).resolve()
    need(not path.exists() and not path.is_relative_to(ROOT.parent.parent),'fresh external evidence path required')
    return path


def full_entry(arm):
    need(arm in ('B','C') and sys.flags.optimize==0,'full caller requires B/C and original assertions')
    authenticate()
    output=external(os.environ['CROC_GF2_FULL_OUTPUT'])
    driver=ROOT/'full_driver.py'
    sys.argv=[str(driver),'--frozen-root',str(ROOT/'frozen'),'--reference',str(ROOT/'reference/certificates/complex-network.json'),
              '--mode','baseline' if arm=='B' else 'candidate','--anchor',str(ROOT/'anchor.json'),'--output',str(output)]
    runpy.run_path(str(driver),run_name='__main__')
    authenticate()
