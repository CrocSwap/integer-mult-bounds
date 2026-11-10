# SPDX-License-Identifier: Apache-2.0
"""Archive and production-body preservation checks; no archived code execution."""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json
ROOT = Path(__file__).resolve().parent

def need(ok, message):
    if ok is not True:
        raise RuntimeError(message)

def check():
    manifest = json.loads((ROOT / 'ARTIFACTS.json').read_text())
    expected = set()
    for row in manifest['files']:
        name = row['path']; path = PurePosixPath(name)
        need(path.as_posix() == name and not path.is_absolute() and all(x not in ('', '.', '..') for x in path.parts) and name not in expected, 'invalid archive path')
        expected.add(name); target = ROOT / name
        need(not any(p.is_symlink() for p in (target, *target.parents) if p.is_relative_to(ROOT)), 'archive link')
        raw = target.read_bytes()
        need(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'archive identity: ' + name)
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(actual == expected | {'ARTIFACTS.json'}, 'archive inventory')
    impl = ROOT / 'unit05/implementation'
    old_domain = (ROOT / 'basis/parent_domain_v1.py.txt').read_bytes()
    domain = (impl / 'parent_domain_v1.py').read_bytes()
    fragment = (ROOT / 'unit05/proposal/domain-prefix-accessor.py.fragment').read_bytes()
    need(domain == old_domain + b'\n\n' + fragment, 'domain append changed')
    old_closure = (ROOT / 'basis/parent_closure_v1.py.txt').read_bytes()
    closure = (impl / 'parent_closure_v1.py').read_bytes()
    allowance = (ROOT / 'unit05/proposal/closure-allowance.py.fragment').read_bytes()
    need(len(allowance) == 63 and closure.count(allowance) == 1 and closure.replace(allowance, b'', 1) == old_closure, 'closure delta changed')
    parent = (impl / 'parent_completion_v1.py').read_bytes()
    need(parent == (ROOT / 'basis/parent_completion_v1.py.txt').read_bytes(), 'production parent changed')
    for before, after in ((old_domain, domain), (old_closure, closure), (parent, parent)):
        old = {n.name:n for n in ast.parse(before).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        new = {n.name:n for n in ast.parse(after).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        for name, node in old.items():
            need(ast.get_source_segment(before.decode(), node) == ast.get_source_segment(after.decode(), new[name]), 'original production source changed')
    print('PASS_PREFIX_SUPERVISION_ARCHIVE_ONLY files=' + str(len(expected)), flush=True)

if __name__ == '__main__':
    check()
