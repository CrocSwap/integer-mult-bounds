#!/usr/bin/env python3
"""Read-only portable replay of the unchanged physical raw-dual emitter.

Only fetch(pin,path) is rebound in memory. An exact checker copy is executed
with --emit in private scratch, preserving its __file__ source-hash guard.
Apache-2.0; substantial OpenAI Codex assistance; credit in retained report.
"""
import ast
from contextlib import redirect_stdout
from hashlib import sha256, sha1
import gzip
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
ORIGINS_SHA = '96c10111ce6d0af4c99969b9e6789d47251a906c0ac5640fc1478886a70b6d60'
FETCH_SOURCE = "def fetch(pin,path):return subprocess.check_output(['git','--no-replace-objects','show',pin+':'+path])"


def need(test, why):
    if not test:
        raise ValueError(why)


def authenticate():
    original = (HERE / 'ORIGINS.json').read_bytes()
    need(sha256(original).hexdigest() == ORIGINS_SHA, 'Exact retained source origins')
    origins = json.loads(original)
    sources = {}
    for row in origins['files']:
        raw = (HERE / row['local_path']).read_bytes()
        need(sha256(raw).hexdigest() == row['sha256'], 'Source SHA256: ' + row['label'])
        need(sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == row['git_blob'], 'Source Git blob: ' + row['label'])
        sources[row['original_commit'], row['original_path']] = raw
    need(len(sources) == 10, 'Ten exact consumed sources')
    for row in origins['science']:
        need(sha256((HERE / row['path']).read_bytes()).hexdigest() == row['sha256'], 'Unchanged A science: ' + row['path'])
    need(len(origins['science']) == 7, 'Seven unchanged scientific files')
    return sources


def adapted_tree(body):
    tree = ast.parse(body)
    candidates = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'fetch']
    need(len(candidates) == 1, 'Single source loader')
    original = candidates[0]
    need(ast.dump(original) == ast.dump(ast.parse(FETCH_SOURCE).body[0]), 'Exact documented fetch function')
    position = tree.body.index(original)
    before = [ast.dump(n) for n in tree.body]
    tree.body[position] = ast.parse('def fetch(pin,path): return FROZEN_SOURCES[pin,path]').body[0]
    after = [ast.dump(n) for n in tree.body]
    need([i for i,(a,b) in enumerate(zip(before,after)) if a != b] == [position], 'Only source fetch AST differs')
    return ast.fix_missing_locations(tree)


def run():
    sources = authenticate()
    body = (HERE / 'science/check.py').read_bytes()
    tree = adapted_tree(body)
    with TemporaryDirectory(prefix='involutory-rawdual-private-') as temporary:
        folder = Path(temporary)
        checker = folder / 'check.py'
        checker.write_bytes(body)
        saved_arguments = sys.argv[:]
        try:
            sys.argv = [str(checker), '--emit']
            env = {'__file__': str(checker), '__name__': '__main__', 'FROZEN_SOURCES': sources}
            with redirect_stdout(io.StringIO()):
                exec(compile(tree, 'unchanged_rawdual_science_with_vendored_fetch', 'exec'), env)
        finally:
            sys.argv = saved_arguments
        actual_word = (folder / 'RAWDUAL-WORD.json.gz').read_bytes()
        expected_word = (HERE / 'science/RAWDUAL-WORD.json.gz').read_bytes()
        need(gzip.decompress(actual_word) == gzip.decompress(expected_word), 'Exact decompressed raw-dual payload')
        actual = json.loads((folder / 'RESULT.json').read_text())
        expected = json.loads((HERE / 'science/RESULT.json').read_text())
        need(actual.pop('word_sha256') == sha256(actual_word).hexdigest(), 'Regenerated container binds its receipt')
        need(expected.pop('word_sha256') == sha256(expected_word).hexdigest(), 'Frozen container binds its receipt')
        need(actual == expected, 'Every proof-relevant RESULT field')
        need(json.loads((folder / 'SOURCES.json').read_text()) == json.loads((HERE / 'science/SOURCES.json').read_text()), 'Original checker hash and consumed-source receipt')
        need(checker.read_bytes() == body, 'Exact original __file__ bytes')
    need(authenticate() == sources, 'Read-only replay preserved all retained bytes')
    return dict(status='PASS_PORTABLE_INVOLUTORY_SOURCE_RAWDUAL', all632_rows=True,
                independent_helpers=408, new_owned_arrays=0, added_H1=8,
                gzip_payload_equal=True, container_equal=actual_word == expected_word,
                source_loader_only_adapted=True, new_kappa=False, complete_caller=False)


if __name__ == '__main__':
    need(len(sys.argv) == 1, 'Read-only verifier accepts no generation arguments')
    print(json.dumps(run(), sort_keys=True))
