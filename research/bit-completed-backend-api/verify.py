#!/usr/bin/env python3
"""Portable frozen conditional BIT API replay; Apache-2.0; Codex assistance.
Only the author's single Git byte-reader is rebound in memory. Original code,
__file__ and all assertions remain. No Git/network/predecessor imports needed.
"""
import ast
import contextlib
import io
import json
from hashlib import sha256
from pathlib import Path
import runpy
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def authenticate(root=HERE):
    packet = json.loads((root / 'PACKET.json').read_text())
    for name, digest in packet['files'].items():
        need(sha256((root / name).read_bytes()).hexdigest() == digest,
             'Frozen evidence changed: ' + name)
    origins = json.loads((root / 'ORIGINS.json').read_text())
    for row in origins['sources']:
        need(sha256((root / row['retained_path']).read_bytes()).hexdigest() == row['sha256'],
             'Retained source changed: ' + row['original_path'])
    return origins


def author(root=HERE, write=False):
    origins = authenticate(root)
    source_map = {(r['original_commit'], r['original_path']): root / r['retained_path']
                  for r in origins['sources']}

    def retained(argv):
        need(argv[:3] == ['git', '--no-replace-objects', 'show'] and len(argv) == 4,
             'Unexpected source command')
        pin, path = argv[3].split(':', 1)
        need((pin, path) in source_map, 'Undeclared source request')
        return source_map[pin, path].read_bytes()

    class Reader(ast.NodeTransformer):
        count = 0

        def visit_Call(self, node):
            node = self.generic_visit(node)
            if (isinstance(node.func, ast.Attribute) and
                    isinstance(node.func.value, ast.Name) and
                    node.func.value.id == 'subprocess' and node.func.attr == 'check_output'):
                need(len(node.args) == 1 and not node.keywords, 'Unexpected byte reader shape')
                self.count += 1
                return ast.copy_location(ast.Call(func=ast.Name(id='_retained', ctx=ast.Load()),
                                                  args=node.args, keywords=[]), node)
            return node

    path = root / 'science/check.py'
    tree = ast.parse(path.read_bytes(), filename=str(path))
    reader = Reader()
    tree = ast.fix_missing_locations(reader.visit(tree))
    need(reader.count == 1, 'Exactly one source byte-reader adaptation required')
    previous = sys.argv
    try:
        sys.argv = [str(path)] + (['--write'] if write else [])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            exec(compile(tree, str(path), 'exec'),
                 {'__name__': '__main__', '__file__': str(path), '_retained': retained})
        return output.getvalue()
    finally:
        sys.argv = previous


def replay_author():
    authenticate()
    stdout = author()
    need(stdout.encode() == (HERE / 'science/normal.log').read_bytes(),
         'Author stdout differs from frozen receipt')
    # Regenerate only a private copy, retaining original checker bytes/__file__.
    with tempfile.TemporaryDirectory(prefix='bit-api-regenerate-') as tmp:
        root = Path(tmp) / 'package'
        shutil.copytree(HERE, root)
        author(root, write=True)
        for name in ('RESULT.json', 'SOURCES.json'):
            need((root / 'science' / name).read_bytes() == (HERE / 'science' / name).read_bytes(),
                 'Scratch regeneration differs: ' + name)
    authenticate()
    return {'status': 'PASS_PORTABLE_CONDITIONAL_BIT_API_AUTHOR', 'fixtures': 22,
            'basis_columns': 384, 'controls': 7, 'primitive_API_admitted': False,
            'new_kappa': False}


def replay_independent():
    authenticate()
    previous = sys.argv
    path = HERE / 'independent/independent.py'
    try:
        sys.argv = [str(path)]
        with contextlib.redirect_stdout(io.StringIO()) as output:
            runpy.run_path(str(path), run_name='__main__')
    finally:
        sys.argv = previous
    need(json.loads(output.getvalue()) == json.loads((HERE / 'independent/INDEPENDENT.json').read_text()),
         'Independent derivation differs from frozen JSON')
    authenticate()
    return {'status': 'PASS_PORTABLE_INDEPENDENT_BIT_API_SOURCE_OPERATOR_REVIEW',
            'source_originals': 658, 'independent_helpers': 436, 'COPY_episodes': 9,
            'basis_columns': 384, 'primitive_API_admitted': False, 'new_kappa': False}


def controls():
    authenticate()
    rejected = []
    with tempfile.TemporaryDirectory(prefix='bit-api-source-controls-') as tmp:
        root = Path(tmp) / 'package'
        shutil.copytree(HERE, root)
        for name in ('independent/inputs/frames.json', 'science/RESULT.json', 'science/check.py'):
            path = root / name
            original = path.read_bytes()
            path.write_bytes(original + b' ')
            try:
                authenticate(root)
            except ValueError as exc:
                need('Frozen evidence changed' in str(exc), 'Wrong integrity rejection')
                rejected.append(name)
            else:
                raise ValueError('Source mutation accepted: ' + name)
            path.write_bytes(original)
    return {'status': 'PASS_PORTABLE_EVIDENCE_MUTATION_CONTROLS', 'rejected': rejected,
            'scope': 'Integrity only; semantic controls run in author and independent modes'}


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) == 2 else 'author' if len(sys.argv) == 1 else None
    need(mode in ('author', 'independent', 'controls'), 'Use author, independent or controls')
    result = {'author': replay_author, 'independent': replay_independent, 'controls': controls}[mode]()
    print(json.dumps(result, sort_keys=True))
