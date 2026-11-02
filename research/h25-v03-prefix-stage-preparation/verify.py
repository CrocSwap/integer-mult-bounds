#!/usr/bin/env python3
"""Authenticate exact exported bytes and replay only the five frozen NEW fixtures.

Clear1nsight, with OpenAI Codex/GPT-6.1 Sol Max assistance. Apache-2.0.
No archived historical/original caller code is executed by this wrapper.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
SOURCE = 'unit07/implementation/prepare_prefix_stage_v2.py'
CORE_SHA = '25c0ee198bcb5a7b77a9d56fe8c551799e1add398bab992782da5eb6bfc677a5'
FIXTURES = (
    ('preparer_controls_v2.py', 12, '801887622cac72f321050fbdce5cef1381da11d155730fe2b2ead9b5ad754447'),
    ('preparer_review_counterexamples_v2.py', 4, '7fd0fa01bd17bda9054105421bcf556473f523d18d779ad5af3d0f08bc9a0bda'),
    ('preparer_data_dag_v2.py', 1, '0b0fb6b475ac8185dd1624efab88b0fa54c6d4767b40af5a8923d2a700a33d89'),
    ('preparer_repair_extra_v2.py', 4, 'bb562456230936609d367d4c0c105ce778e4dd9a99ef20079fab78f7e2e4b5ba'),
    ('preparer_path_contract_v2.py', 1, 'd858c5ed25f1528d1165c2cc65826b9942b6efa35836e37787fa90f726855273'),
)
ACTIVE = (SOURCE,) + tuple('unit07/fixtures/' + row[0] for row in FIXTURES)


def need(condition, message):
    if condition is not True:
        raise RuntimeError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local(name):
    need(type(name) is str and name and '\\' not in name, 'invalid package path type/spelling')
    parts = name.split('/')
    need(not name.startswith('/') and all(p not in ('', '.', '..') for p in parts), 'noncanonical/host package path')
    need(PurePosixPath(name).as_posix() == name, 'package path normalization differs')
    p = ROOT
    for part in parts:
        p = p / part
        need(not p.is_symlink(), 'package symlink refused: ' + name)
    need(p.is_file(), 'missing regular package file: ' + name)
    return p


def inventory():
    need(not ROOT.is_symlink(), 'package root symlink refused')
    names = []
    for directory, dirs, files in os.walk(ROOT, followlinks=False):
        for name in dirs + files:
            need(not (Path(directory) / name).is_symlink(), 'package alias refused')
        names.extend((Path(directory) / name).relative_to(ROOT).as_posix() for name in files)
    return sorted(names)


def authenticate():
    manifest = json.loads(local('MANIFEST.json').read_bytes())
    need(manifest['schema'] == 'h25-prefix-preparation-manifest-v1', 'manifest schema')
    rows = manifest['files']
    expected = ['MANIFEST.json'] + [row['path'] for row in rows]
    need(len(expected) == len(set(expected)), 'duplicate manifest part')
    need(inventory() == sorted(expected), 'missing or extra package parts')
    for row in rows:
        need(set(row) == {'path', 'bytes', 'sha256', 'ast_sha256'}, 'manifest row shape')
        raw = local(row['path']).read_bytes()
        need(type(row['bytes']) is int and len(raw) == row['bytes'], 'byte length drift: ' + row['path'])
        need(digest(raw) == row['sha256'], 'byte digest drift: ' + row['path'])
        if row['ast_sha256'] is not None:
            need(digest(ast.dump(ast.parse(raw), include_attributes=False).encode()) == row['ast_sha256'], 'AST drift: ' + row['path'])
    origin = json.loads(local('ORIGIN.json').read_bytes())
    need(['unit07/' + name for name in origin['active_allowlist']] == list(ACTIVE), 'unknown active source/fixture')
    for row in origin['rows']:
        raw = local(row['destination']).read_bytes()
        need(len(raw) == row['bytes'] and digest(raw) == row['sha256'] and row['byte_changed'] is False, 'origin/source export differs')
    raw = local(SOURCE).read_bytes()
    need(len(raw) == 47423 and digest(raw) == CORE_SHA, 'fixed frozen core source differs')
    prefix = raw.split(b'# UNIT06_T0_SUPPORT_END\n')[0] + b'# UNIT06_T0_SUPPORT_END\n'
    need(len(prefix) == 9878 and digest(prefix) == '48bc4009acb7569fb4a2ac529bec928a3aafdedc017a0ebaae97f72b7c97eabe', 'exact inherited NEW helper prefix differs')
    for name, count, pinned in FIXTURES:
        raw = local('unit07/fixtures/' + name).read_bytes()
        need(digest(raw) == pinned, 'fixed frozen fixture differs: ' + name)
        tree = ast.parse(raw)
        methods = [n for c in tree.body if isinstance(c, ast.ClassDef) for n in c.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test_')]
        need(len(methods) == count, 'fixture method count differs: ' + name)
    need(sum(row[1] for row in FIXTURES) == 22, 'final method denominator differs')
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('normal', 'optimized'), required=True)
    args = parser.parse_args()
    need(sys.version_info[:2] == (3, 12), 'Python 3.12 required')
    need(sys.flags.optimize == (1 if args.profile == 'optimized' else 0), 'requested/interpreter profile differs')
    parts = authenticate()
    env = dict(os.environ)
    env.pop('PYTHONOPTIMIZE', None)
    env.pop('PYTHONPYCACHEPREFIX', None)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    for name, count, pinned in FIXTURES:
        with tempfile.TemporaryDirectory(prefix='prefix-preparer-private-pycache-') as cache:
            argv = [sys.executable, '-I', '-B', '-X', 'pycache_prefix=' + cache]
            if args.profile == 'optimized':
                argv.append('-O')
            argv.append(str(local('unit07/fixtures/' + name)))
            # Launch only this exact hash-checked NEW test interpreter, never
            # original/archived source or any preparer output/caller/target.
            result = subprocess.run(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30, check=False)
            sys.stdout.buffer.write(result.stdout)
            sys.stdout.flush()
            need(result.returncode == 0, 'frozen fixture failed: ' + name)
            counts = re.findall(rb'^Ran ([0-9]+) tests? in ', result.stdout, re.MULTILINE)
            need(counts == [str(count).encode()] and b'\nOK\n' in result.stdout, 'fixture result/method count differs: ' + name)
    authenticate()
    print(json.dumps({'status': 'PASS', 'profile': args.profile, 'methods': 22, 'fixtures': 5, 'authenticated_payload_files': parts, 'source_sha256': CORE_SHA, 'source_or_test_edits': 0, 'original_or_target_execution': False, 'outside_costs': 'OPEN_NOT_ZERO'}, sort_keys=True))


if __name__ == '__main__':
    main()
