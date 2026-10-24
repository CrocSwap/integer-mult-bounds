#!/usr/bin/env python3
"""Portable read-only replay of unchanged one-port homogeneous construction.

Only the Git-byte loader assignment is rebound in an in-memory AST. The
unchanged local interval dependency is staged at its expected relative path
in private scratch. Apache-2.0; substantial OpenAI Codex assistance.
"""
import ast
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
FROZEN = HERE / 'homogeneous'
MANIFEST_SHA = 'dc0cd91a5d4ec4c3e1b19a9c6534cbb0cda7a6ec218b05bc116f08f6b5370e07'
OLD_LOADER = "raw = {k: subprocess.check_output(['git', '--no-replace-objects', 'show', PIN+':'+v]) for k,v in PATHS.items()}"


def need(test, why):
    if not test:
        raise ValueError(why)


def authenticate():
    manifest = (FROZEN / 'FILES.json').read_bytes()
    need(sha256(manifest).hexdigest() == MANIFEST_SHA, 'Exact G science manifest')
    rows = json.loads(manifest)['files']
    need({r['path'] for r in rows} | {'FILES.json'} == {p.name for p in FROZEN.iterdir() if p.is_file()}, 'Exact G nine-file archive')
    for row in rows:
        need(sha256((FROZEN / row['path']).read_bytes()).hexdigest() == row['sha256'], 'Frozen G file: ' + row['path'])
    result = json.loads((FROZEN / 'RESULT.json').read_text())
    sources = {}
    for path, digest in result['sources'].items():
        raw = (HERE / 'inputs' / path).read_bytes()
        need(sha256(raw).hexdigest() == digest, 'Exact G source: ' + path)
        sources[path] = raw
    dependency = json.loads((FROZEN / 'DEPENDENCIES.json').read_text())['local_interval_library']
    interval = (HERE / 'inputs/local/prefix-interval-library.py').read_bytes()
    need(sha256(interval).hexdigest() == dependency['sha256'], 'Exact retained local interval library')
    return sources, interval


def adapted_tree(body):
    tree = ast.parse(body)
    loads = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'load']
    need(len(loads) == 1, 'One G source loader')
    old = ast.parse(OLD_LOADER).body[0]
    need(ast.dump(loads[0].body[0]) == ast.dump(old), 'Exact Git-byte loader assignment')
    original = [ast.dump(n) for n in loads[0].body[1:]]
    loads[0].body[0] = ast.parse('raw = {k: FROZEN_SOURCES[v] for k,v in PATHS.items()}').body[0]
    need([ast.dump(n) for n in loads[0].body[1:]] == original, 'Scientific loader body unchanged')
    return ast.fix_missing_locations(tree)


if __name__ == '__main__':
    need(len(sys.argv) == 1, 'Read-only launcher accepts no generation arguments')
    sources, interval = authenticate()
    tree = adapted_tree((FROZEN / 'check.py').read_bytes())
    with TemporaryDirectory(prefix='one-h3-homogeneous-') as directory:
        root = Path(directory)
        (root / 'check.py').write_bytes(interval)
        local = root / 'actual'
        local.mkdir()
        (local / 'RESULT.json').write_bytes((FROZEN / 'RESULT.json').read_bytes())
        env = {'__file__': str(local / 'check.py'), '__name__': '__main__', 'FROZEN_SOURCES': sources}
        with redirect_stdout(io.StringIO()):
            exec(compile(tree, 'unchanged_G_science_with_vendored_byte_loader', 'exec'), env)
        need((local / 'RESULT.json').read_bytes() == (FROZEN / 'RESULT.json').read_bytes(), 'G replay is read-only')
    need(authenticate() == (sources, interval), 'Frozen inputs remain unchanged')
    print('PASS_PORTABLE_ONE_NATIVE_TALL_U three_original_owners dependent_prefix total36passes no_complete_caller no_new_kappa')
