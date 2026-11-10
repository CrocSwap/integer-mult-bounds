#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Archive and static source preservation only; never execute originals."""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def need(value, message):
    if value is not True:
        raise RuntimeError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local(spelling):
    need(type(spelling) is str, 'archive path type')
    parts = PurePosixPath(spelling)
    need(parts.as_posix() == spelling and not parts.is_absolute()
         and all(p not in ('', '.', '..') for p in parts.parts), 'archive path spelling')
    path = ROOT / spelling
    need(not any(p.is_symlink() for p in (path, *path.parents) if p.is_relative_to(ROOT)), 'archive alias')
    return path


def assignment(tree, name):
    nodes = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
             and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
    need(len(nodes) == 1, 'missing/ambiguous assignment: ' + name)
    return nodes[0]


def normalized_environment_source(raw, tree):
    value = assignment(tree, 'NATIVE_ENV').value
    lines = raw.splitlines(keepends=True)
    start = sum(len(line) for line in lines[:value.lineno-1]) + value.col_offset
    end = sum(len(line) for line in lines[:value.end_lineno-1]) + value.end_col_offset
    return raw[:start] + b'<ENVIRONMENT_LITERAL>' + raw[end:]


def main():
    manifest = json.loads(local('ARTIFACTS.json').read_text())
    expected = set()
    for row in manifest['files']:
        need(row['path'] not in expected, 'duplicate artifact')
        expected.add(row['path'])
        raw = local(row['path']).read_bytes()
        need(len(raw) == row['bytes'] and digest(raw) == row['sha256'], 'archive bytes: ' + row['path'])
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(actual == expected | {'ARTIFACTS.json'}, 'archive inventory changed')
    preserved = json.loads(local('PRESERVATION.json').read_text())
    old = local('comparison/v03_integrated_constructor_v1.py.txt').read_bytes()
    new = local('implementation/v03_integrated_constructor_v2.py').read_bytes()
    old_tree, new_tree = ast.parse(old), ast.parse(new)
    need(normalized_environment_source(old, old_tree) == normalized_environment_source(new, new_tree), 'change outside environment value')
    old_funcs = {n.name: ast.get_source_segment(old.decode(), n) for n in old_tree.body if isinstance(n, ast.FunctionDef)}
    new_funcs = {n.name: ast.get_source_segment(new.decode(), n) for n in new_tree.body if isinstance(n, ast.FunctionDef)}
    need(len(old_funcs) == 4 and old_funcs == new_funcs, 'four function source bodies changed')
    old_env = ast.literal_eval(assignment(old_tree, 'NATIVE_ENV').value)
    new_env = ast.literal_eval(assignment(new_tree, 'NATIVE_ENV').value)
    need(type(old_env) is dict and len(old_env) == 6 and all(type(k) is bytes and type(v) is bytes for k, v in old_env.items()), 'historical bytes-key environment changed')
    need(type(new_env) is tuple and len(new_env) == 6
         and all(type(row) is tuple and len(row) == 2 and all(type(v) is bytes for v in row) for row in new_env), 'immutable six-pair environment changed')
    need(len(dict(new_env)) == 6 and dict(new_env) == old_env, 'six native pairs differ')
    gates = ast.literal_eval(assignment(new_tree, 'GATES').value)
    need(type(gates) is tuple and len(gates) == 8 and len(set(gates)) == 8, 'eight gate names changed')
    need(gates == ast.literal_eval(assignment(old_tree, 'GATES').value), 'historical gate set changed')
    original = ast.parse(local('snapshot/variant_driver_v1.py.txt').read_bytes())
    for gate in gates:
        need(ast.literal_eval(assignment(original, gate).value) is None, 'original gate is configured')
    old_checker = local('comparison/v03_prefix_derivation_pre_repair.py.txt').read_bytes()
    new_checker = local('implementation/v03_prefix_derivation_v1.py').read_bytes()
    need(old_checker.count(b'v03_integrated_constructor_v1') == 1
         and old_checker.replace(b'v03_integrated_constructor_v1', b'v03_integrated_constructor_v2') == new_checker, 'verifier change beyond constructor import')
    for row in preserved['source_anchors']:
        text = local(row['path']).read_text()
        nodes = [n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == row['function']]
        need(len(nodes) == 1 and (nodes[0].lineno, nodes[0].end_lineno) == (row['first_line'], row['last_line']), 'original source anchor location')
        need(digest(ast.get_source_segment(text, nodes[0]).encode()) == row['source_segment_sha256'], 'original source anchor changed')
    receipt = local('evidence/AUTHOR-RECEIPT-v2.json').read_bytes()
    need(digest(receipt) == preserved['frozen_author_receipt_sha256'], 'frozen author receipt changed')
    close = json.loads(local('evidence/SOURCE-CLOSE-v1.json').read_text())
    need(close['author_receipt_sha256'] == digest(receipt) and close['full_C05'] is False
         and close['full_V03'] is False and close['original_execution'] is False
         and close['original_activity_credit_added'] == 0, 'closed source scope changed')
    need(preserved['full_C05'] is False and preserved['full_V03'] is False
         and preserved['source_clock_reopened'] is False and preserved['outside_costs'] == 'OPEN_NOT_ZERO', 'archive scope changed')
    print('PASS_PREFIX_DERIVATION_ARCHIVE_AND_STATIC_PRESERVATION files=' + str(len(expected)), flush=True)


if __name__ == '__main__':
    main()
