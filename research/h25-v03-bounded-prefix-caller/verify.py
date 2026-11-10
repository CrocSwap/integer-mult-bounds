#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded export integrity and passive source checks; no archived code execution."""
from pathlib import Path, PurePosixPath
import ast
import hashlib
import json
import stat

PACKAGE = Path(__file__).resolve().parent
FROZEN = {
    'archive/unit07/implementation/run_queue4_prefix_v2.py': (34716, '25138c2c998762649c6a61cb8a6ae8aacd81bd533591b082ab6f58def712fca2'),
    'archive/unit07/fixtures/caller_new_controls_v1.py': (14236, '310fe5a31db4c4ac2bab0794a1633ec2061e8f97de654f9701b019185b138765'),
    'archive/unit06/implementation/run_queue4_prefix_v1.py': (34412, '90a7ed4a45b94e16fa313623e56f6f3efcd85f3ea40355a43b289d8c49a75825'),
    'archive/unit06/implementation/predecessor_entry.py': (21857, 'b783c6812a6295069456cfb4187d4e09bb7acbcb20fffd76e0c10267f90c1201'),
    'archive/unit06/prerequisites/h25_parent_supervisor.py.txt': (23047, 'cfb09a18dd10b597cc6d5a8139ee769bef679bc44ae029329755e3d97b055075'),
    'archive/unit06/fixtures/caller_original_wrapper.py.txt': (None, 'ea4c07337ccc1865accfd1b1fe485d51057a04a49e4bfb5f10cc36dc92b5f9a8'),
    'archive/unit07/review-caller-P3-v1.json': (5719, 'f61464ed7496af2ae47414bcdfad2f63e773563411c4e70a2fc8955442e7b089'),
    'archive/unit07/fixtures/caller_resource_bill_v1.json': (None, 'b22dc7fa984657ced87fe37052f38a10dc1fa0d61b2509715603514fe52fbdff'),
}
NEW_FUNCTIONS = {'_caller_simple', '_caller_pin', '_caller_inventory', '_caller_stage', '_caller_case', '_caller_source_packet'}
CONSTANTS = {'CALLER_QUEUE_SHA', 'CALLER_RUNNER_SHA', 'CALLER_SUPERVISOR_SHA', 'CALLER_STAGE_KEYS', 'CALLER_FALSE_FIELDS'}
METHODS = {
    'test_exact_prefix_only_delta_and_old_unit_unchanged',
    'test_read_at_8192_short_returns_can_complete',
    'test_8193rd_short_read_is_prevented_and_close_secondary_retained',
    'test_record_4097th_short_write_is_prevented',
    'test_large_file_8193rd_short_write_is_prevented',
    'test_prior_digest_refuses_changed_bytes_and_retains_actual_raw',
    'test_real_owned_inventory_and_negative_file_changes',
    'test_nested_excluded_manifest_requires_exact_prior_blob',
    'test_case_requires_actual_job_stage_and_all_five_false_fields',
    'test_new_packet_basename_and_original_supervisor_data_only',
    'test_new_dispatch_recheck_precedes_fake_base_and_failure_suppresses_it',
}


def need(ok, message):
    if ok is not True:
        raise RuntimeError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_segment(raw, name):
    text = raw.decode('utf-8')
    nodes = [n for n in ast.parse(text).body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name]
    need(len(nodes) == 1, 'source segment count: ' + name)
    return ast.get_source_segment(text, nodes[0]).encode('utf-8')


def main():
    manifest_path = PACKAGE / 'MANIFEST.json'
    need(not manifest_path.is_symlink(), 'manifest symlink')
    need(stat.S_IMODE(manifest_path.stat().st_mode) == 0o644, 'manifest mode')
    manifest = json.loads(manifest_path.read_bytes())
    rows = manifest['files']
    expected = set(rows) | {'MANIFEST.json'}
    actual = set()
    for p in PACKAGE.rglob('*'):
        need(not p.is_symlink(), 'package symlink: ' + str(p))
        if p.is_dir():
            continue
        need(p.is_file(), 'nonregular package entry')
        name = p.relative_to(PACKAGE).as_posix()
        actual.add(name)
    need(actual == expected, 'package file inventory mismatch: ' + repr(sorted(actual ^ expected)))
    for name, row in rows.items():
        parts = PurePosixPath(name).parts
        need(type(name) is str and parts and not name.startswith('/') and all(v not in ('', '.', '..') for v in name.split('/')), 'manifest path')
        p = PACKAGE / name
        raw = p.read_bytes()
        need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'package bytes differ: ' + name)
        need(stat.S_IMODE(p.stat().st_mode) == row['posix_mode'] == 0o644, 'package mode differs: ' + name)
        need(row['intended_git_mode'] == '100644', 'intended Git mode')
    for name, (size, digest) in FROZEN.items():
        raw = (PACKAGE / name).read_bytes()
        need((size is None or len(raw) == size) and sha(raw) == digest, 'frozen source pin differs: ' + name)
    for row in json.loads((PACKAGE / 'SOURCE-ORIGINS-v1.json').read_bytes())['sources']:
        raw = (PACKAGE / row['package_path']).read_bytes()
        need(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'source origin copy differs')
    new = (PACKAGE / 'archive/unit07/implementation/run_queue4_prefix_v2.py').read_bytes()
    old = (PACKAGE / 'archive/unit06/implementation/run_queue4_prefix_v1.py').read_bytes()
    entry = (PACKAGE / 'archive/unit06/implementation/predecessor_entry.py').read_bytes()
    wrapper = (PACKAGE / 'archive/unit06/fixtures/caller_original_wrapper.py.txt').read_bytes()
    need(new[:9878] == entry[:9878] and sha(new[:9878]) == '48bc4009acb7569fb4a2ac529bec928a3aafdedc017a0ebaae97f72b7c97eabe', 'accepted prefix differs')
    need(new[9878:] == old[9574:], 'old caller tail differs')
    need(new.index(b'# UNIT06_T0_SUPPORT_END\n') + len(b'# UNIT06_T0_SUPPORT_END\n') == 9878, 'prefix marker')
    for name in ('source_packet', 'RootProxy'):
        need(source_segment(new, name) == source_segment(wrapper, name), 'preserved original source differs: ' + name)
    need((PACKAGE / 'archive/unit07/fixtures/caller_initial_candidate_v2.py.txt').read_bytes() == new, 'frozen initial caller differs')
    need((PACKAGE / 'archive/unit07/fixtures/caller_basis_unit06_90a.py.txt').read_bytes() == old, 'basis snapshot differs')
    need((PACKAGE / 'archive/unit07/fixtures/caller_bounded_T0_prefix_48bc.py.txt').read_bytes() == new[:9878], 'support snapshot differs')
    fixture_raw = (PACKAGE / 'archive/unit07/fixtures/caller_new_controls_v1.py').read_bytes()
    need((PACKAGE / 'archive/unit07/fixtures/caller_initial_controls_v1.py.txt').read_bytes() == fixture_raw, 'frozen controls snapshot differs')
    tree = ast.parse(fixture_raw)
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    need(len(classes) == 1 and classes[0].name == 'CallerNewControls', 'fixture class inventory')
    methods = {n.name for n in classes[0].body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
    need(methods == METHODS and len(methods) == 11, 'frozen method inventory')
    assignments = {n.targets[0].id: n.value for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}
    need(ast.literal_eval(assignments['NEW_FUNCTIONS']) == NEW_FUNCTIONS, 'helper extraction whitelist')
    need(ast.literal_eval(assignments['CONSTANTS']) == CONSTANTS, 'constant extraction whitelist')
    close = json.loads((PACKAGE / 'archive/unit07/SOURCE-CLOSE-v1.json').read_bytes())
    need(close['accepted_checkpoints'] == ['P1', 'P2', 'P3', 'P4'] and close['runtime_qualified'] is False and close['original_activity_credit_added'] == 0, 'closed source boundary')
    print('PASS_BOUNDED_CALLER_EXPORT_INTEGRITY files=' + str(len(actual)) + ' frozen_methods=11 original_source_execution=NONE', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
