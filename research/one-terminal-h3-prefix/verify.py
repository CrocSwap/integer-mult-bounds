#!/usr/bin/env python3
"""Read-only vendored-source replay of unchanged one-H3 prefix science.

Only the Git source-loader function is rebound in an in-memory AST. Emitted
receipts are regenerated in private scratch and compared byte-for-byte.
Apache-2.0; substantial OpenAI Codex assistance; source credit in README.
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
SCIENCE = HERE / 'science'
MANIFEST_SHA256 = '3e0eaff1f992b59f9cce72523311bcc2b70897ed5765fc40dacaccb70f3c8aa3'
ORIGINAL_READ = "def read(p):return subprocess.check_output(['git','show',PIN+':'+p],env={**os.environ,'GIT_NO_REPLACE_OBJECTS':'1'})"


def need(test, why):
    if not test:
        raise ValueError(why)


def authenticate():
    raw = (SCIENCE / 'SOURCES.json').read_bytes()
    need(sha256(raw).hexdigest() == MANIFEST_SHA256, 'Exact science source manifest')
    manifest = json.loads(raw)
    expected = {r['path'] for r in manifest['own_files']} | {'SOURCES.json'}
    need(expected == {p.name for p in SCIENCE.iterdir() if p.is_file()}, 'Exact seven-file science archive')
    for row in manifest['own_files']:
        need(sha256((SCIENCE / row['path']).read_bytes()).hexdigest() == row['sha256'],
             'Frozen science: ' + row['path'])
    sources = {}
    for path, digest in manifest['source_sha256'].items():
        data = (HERE / 'inputs' / path).read_bytes()
        need(sha256(data).hexdigest() == digest, 'Pinned vendored source: ' + path)
        sources[path] = data
    need(len(sources) == 5, 'Five exact source inputs')
    return sources


def adapted_tree(body):
    tree = ast.parse(body)
    loaders = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'read']
    need(len(loaders) == 1, 'One source loader')
    old = loaders[0]
    need(ast.dump(old) == ast.dump(ast.parse(ORIGINAL_READ).body[0]), 'Exact documented Git loader')
    replacement = ast.parse('def read(p): return FROZEN_SOURCES[p]').body[0]
    index = tree.body.index(old)
    before = [ast.dump(n) for n in tree.body]
    tree.body[index] = replacement
    after = [ast.dump(n) for n in tree.body]
    need([i for i, pair in enumerate(zip(before, after)) if pair[0] != pair[1]] == [index],
         'Only source-loader AST is changed')
    return ast.fix_missing_locations(tree)


if __name__ == '__main__':
    need(len(sys.argv) == 1, 'Read-only verifier accepts no generation arguments')
    sources = authenticate()
    tree = adapted_tree((SCIENCE / 'check.py').read_bytes())
    with TemporaryDirectory(prefix='one-terminal-h3-prefix-') as directory:
        temporary = Path(directory)
        environment = {'__file__': str(temporary / 'check.py'), '__name__': 'one_h3_private_replay',
                       'FROZEN_SOURCES': sources}
        with redirect_stdout(io.StringIO()):
            exec(compile(tree, 'unchanged_one_h3_science_with_vendored_source_loader', 'exec'), environment)
        for name in ['PATCH.json', 'RESULT.json']:
            need((temporary / name).read_bytes() == (SCIENCE / name).read_bytes(),
                 'Exact regenerated scientific receipt: ' + name)
    need(authenticate() == sources, 'Read-only replay left all frozen inputs unchanged')
    print('PASS_PORTABLE_ONE_TERMINAL_H3_PREFIX exact_phase_and_prefix receipts_equal no_consumer no_new_kappa')
