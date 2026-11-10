#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Raw archive/frozen source checks only; no original imports or execution."""
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
    p = PurePosixPath(spelling)
    need(not p.is_absolute() and p.as_posix() == spelling and all(v not in ('', '.', '..') for v in p.parts), 'archive path')
    out = ROOT / spelling
    need(not any(q.is_symlink() for q in (out, *out.parents) if q.is_relative_to(ROOT)), 'archive alias')
    return out


def literal(tree, name):
    nodes = [n.value for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
    need(len(nodes) == 1, 'literal source field: ' + name)
    return ast.literal_eval(nodes[0])


def main():
    manifest = json.loads(local('ARTIFACTS.json').read_text())
    seen = set()
    for row in manifest['files']:
        need(row['path'] not in seen, 'duplicate artifact')
        seen.add(row['path'])
        raw = local(row['path']).read_bytes()
        need((len(raw), digest(raw)) == (row['bytes'], row['sha256']), 'raw artifact: ' + row['path'])
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    need(actual == seen | {'ARTIFACTS.json'}, 'archive file set')
    entry = local('implementation/predecessor_entry.py').read_bytes()
    fixture = local('fixtures/test_bootstrap_new_v1.py').read_bytes()
    need((len(entry), digest(entry)) == (21857, 'b783c6812a6295069456cfb4187d4e09bb7acbcb20fffd76e0c10267f90c1201'), 'frozen entry bytes')
    need((len(fixture), digest(fixture)) == (6532, '19c1b08d4daeaf0c2d40357b0e117fcb2ca2f632f627e290fe7442abf49b3504'), 'frozen fixture bytes')
    graph_raw = local('SOURCE-GRAPH-v1.json').read_bytes()
    need((len(graph_raw), digest(graph_raw)) == (132763, 'f999a6bfc9ac9048b248d9b029b7676ba04dea5c559228d5286e49d269ca3597'), 'fixed graph bytes')
    graph = json.loads(graph_raw)
    rows = graph['modules']
    expected = {r['module']: (r['sha256'], r['bytes']) for r in rows}
    tree = ast.parse(entry)
    need(literal(tree, 'PROJECT_PINS') == expected and literal(tree, 'PROJECT_ORDER') == tuple(graph['topological_initialization_order']), 'entry/graph selection')
    need(len(rows) == 15 and sum(r['bytes'] for r in rows) == 379241, 'inner source bill')
    for row in rows:
        raw = local('prerequisites/' + Path(row['copy_path']).name).read_bytes()
        need((digest(raw), len(raw)) == expected[row['module']], 'inert graph input identity')
    tests = ast.parse(fixture)
    classes = [n for n in tests.body if isinstance(n, ast.ClassDef) and n.name == 'Tests']
    need(len(classes) == 1, 'fixture class')
    methods = [n for n in classes[0].body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
    need(len(methods) == 12 and any(n.name == 'test_fixed_original_graph_is_parsed_only_and_ordered' for n in methods), 'exact twelve fixture scope')
    need(not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'm' and n.func.attr in ('main', 'entry_operation') for n in ast.walk(tests)), 'forbidden full entry fixture call')
    close_raw = local('evidence/SOURCE-CLOSE-v1.json').read_bytes()
    need(digest(close_raw) == '7cac80142264ca41f80be6fa7ea4a0b268cd2ce6c44ff2755f0cb3294c59fd9b', 'source close identity')
    close = json.loads(close_raw)
    need(close['accepted_checkpoints'] == ['U6.1', 'U6.2'] and close['accepted_count'] == 2 and close['fixed_local_denominator'] == 4, 'closed partial denominator')
    need(close['original_C05'] is False and close['original_V03'] is False and close['runtime_qualified'] is False and close['original_activity_credit_added'] == 0 and close['costs'] == 'OPEN_NOT_ZERO', 'original acceptance boundary')
    review = local('evidence/review-loader-source-v2.json').read_bytes()
    need(digest(review) == '7ed7ef8896abdaab443473038992f652a5054f43c4ea41a0f0aa0f028079b799', 'entry review identity')
    caller = local('evidence/review-caller-source-v2.json').read_bytes()
    need(digest(caller) == '37c9f79c9f836fa14ea88d1ae5790b2ce350361699e848f35e2faebe6549c8b6', 'caller partial review identity')
    reconstruction = json.loads(local('evidence/review-loader-initial-reconstruction-v1.json').read_text())
    initial = local('history/initial-draft-VERIFIED-RECONSTRUCTION-d751.py.txt').read_bytes()
    need(initial == reconstruction['reconstructed_source_text'].encode() and digest(initial) == reconstruction['reconstructed_sha256'], 'verified reconstruction identity')
    need(local('history/reviewed-entry-final-b783.py.txt').read_bytes() == entry and local('history/reviewed-tests-final-19c1.py.txt').read_bytes() == fixture, 'direct final snapshots')
    print('PASS_AUTHENTICATED_ENTRY_ARCHIVE_ONLY files=' + str(len(seen)) + ' inert_sources=15 bytes=379241 fixture_methods=12', flush=True)


if __name__ == '__main__':
    main()
