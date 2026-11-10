"""Concrete inventory-only consumer; parent guarded admission required.

No process launcher, scientific import, native bind, timer or cached PASS.
Outer guard begins before process/bootstrap and ends after cleanup and guard
receipt/source/log validation. Parent source pins authenticate this program.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import stat
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ORIGINAL_ORDER = ('valid', 'list-pins', 'wrong-digest', 'missing', 'extra',
                  'extra-nonexact', 'symlink', 'root-symlink', 'changed-mode',
                  'fresh-call-after-mutation', 'restored')
HEADER = b'"""Literal pinned v4 inventory extraction; no full-driver import."""\nimport hashlib\nimport stat\n\n\n'


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def read_checked(path, info):
    need(path.is_file() and not path.is_symlink(), 'Missing or symlinked source: ' + str(path))
    raw = path.read_bytes()
    actual = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
              'mode': stat.S_IMODE(path.stat().st_mode)}
    need(actual == info, 'Source custody changed: ' + str(path))
    return raw, actual


def authenticate(workspace):
    """Fresh reads every call, including pre-load and post-work custody."""
    bill_raw = (HERE / 'SOURCE-PINS.json').read_bytes()
    bill = json.loads(bill_raw)
    result = {'SOURCE-PINS.json': {'sha256': hashlib.sha256(bill_raw).hexdigest(),
                                  'bytes': len(bill_raw),
                                  'mode': stat.S_IMODE((HERE / 'SOURCE-PINS.json').stat().st_mode)}}
    actual_files = {str(path.relative_to(HERE)) for path in HERE.rglob('*') if path.is_file()}
    need(actual_files == set(bill['package']) | {'SOURCE-PINS.json'}, 'Package file census changed')
    need(not any(path.is_symlink() for path in HERE.rglob('*')), 'Package symlink')
    for name, info in sorted(bill['package'].items()):
        _, result['package/' + name] = read_checked(HERE / name, info)
    for name, info in sorted(bill['external'].items()):
        relative = Path(name)
        need(not relative.is_absolute() and '..' not in relative.parts, 'Unsafe external source path')
        current = workspace
        for part in relative.parts:
            current = current / part
            need(not current.is_symlink(), 'External source ancestry symlink')
        _, result['external/' + name] = read_checked(current, info)
    return result


def check_extraction(workspace):
    spec = json.loads((HERE / 'REFERENCE-EXTRACTION.json').read_bytes())
    raw = (workspace / spec['source']).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == spec['source_sha256'], 'Original driver identity changed')
    lines = raw.splitlines(keepends=True)
    nodes = ast.parse(raw).body
    parts = {node.name: b''.join(lines[node.lineno - 1:node.end_lineno])
             for node in nodes if isinstance(node, ast.FunctionDef) and node.name in ('need', 'sha', 'inventory')}
    need(set(parts) == {'need', 'sha', 'inventory'}, 'Literal extraction closure changed')
    for name, part in parts.items():
        need(part.decode() == spec['functions'][name]['source'] and
             hashlib.sha256(part).hexdigest() == spec['functions'][name]['sha256'],
             'Literal extraction differs: ' + name)
    body = b'\n\n\n'.join(parts[name] for name in ('need', 'sha', 'inventory')) + b'\n'
    need((HERE / 'reference.py').read_bytes() == HEADER + body, 'Reference is not literal extraction')
    old = b'            need(sha(raw) == expected, "Frozen input digest changed: " + relative)\n            files[relative] = {"sha256": sha(raw),'
    new = b'            raw_digest = sha(raw)\n            need(raw_digest == expected, "Frozen input digest changed: " + relative)\n            files[relative] = {"sha256": raw_digest,'
    need(body.count(old) == 1 and (HERE / 'candidate.py').read_bytes() == HEADER + body.replace(old, new),
         'Candidate differs beyond the single local digest change')


def load_local(name):
    path = HERE / (name + '.py')
    spec = importlib.util.spec_from_file_location('_inventory_component_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    need(Path(module.__file__).resolve() == path, 'Unpinned component import')
    return module


def prepare_fixture(workspace, scratch):
    spec = json.loads((HERE / 'FIXTURE-v1.json').read_bytes())
    manifest_raw = (workspace / spec['manifest_source']).read_bytes()
    need(hashlib.sha256(manifest_raw).hexdigest() == spec['manifest_sha256'], 'Original pins changed')
    pins = json.loads(manifest_raw)
    need(len(pins) == spec['file_count'] == 32, 'Representative file count changed')
    need([row['name'] for row in spec['files']] == sorted(pins), 'Representative names changed')
    need(spec['inventory_calls_per_arm'] == 128, 'Representative call count changed')
    expected = {}
    root = scratch / 'representative'
    root.mkdir(parents=True)
    for row in spec['files']:
        name = row['name']
        need(pins[name] == row['pin'] and type(pins[name]) is list,
             'Representative original list pin changed')
        source = workspace / row['source']
        raw = source.read_bytes()
        need(hashlib.sha256(raw).hexdigest() == pins[name][0] == row['sha256'] and
             len(raw) == row['bytes'] and stat.S_IMODE(source.stat().st_mode) == row['mode'],
             'Representative source changed: ' + name)
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        path.chmod(row['mode'])
        expected[name] = {'sha256': pins[name][0], 'mode': row['mode'], 'bytes': row['bytes']}
    need(sum(row['bytes'] for row in spec['files']) == spec['total_bytes'] == 453700,
         'Representative byte count changed')
    return root, pins, expected, spec


def run(mode, workspace, output):
    need(sys.implementation.name == 'cpython' and sys.version_info[:2] == (3, 12),
         'Declared supported runtime is CPython3.12')
    need(sys.flags.optimize in (0, 1), 'Only normal and -O modes declared')
    need(mode in ('controls', 'baseline', 'candidate'), 'Invalid mode')
    need(not output.exists(), 'Fresh output required')
    before = authenticate(workspace)
    check_extraction(workspace)
    reference = load_local('reference')
    candidate = load_local('candidate')
    original_controls = load_local('inventory_controls')
    extra_controls = load_local('digest_controls')
    need(reference.inventory.__globals__ is not candidate.inventory.__globals__,
         'Reference and candidate namespaces overlap')
    output.mkdir(parents=True)
    scratch = output / 'scratch'
    receipt = {'mode': mode, 'optimization': sys.flags.optimize,
               'scope': 'Inventory-only component; no full H25/native/scientific/publication qualification'}
    try:
        if mode == 'controls':
            old = original_controls.run_controls(reference.inventory, candidate.inventory, scratch / 'original')
            need([row[0] for row in old['cases']] == list(ORIGINAL_ORDER) and len(old['cases']) == 11,
                 'Original11 ordered controls changed')
            added = extra_controls.run_controls(reference, candidate, scratch / 'added')
            need(added['case_count'] == 16 and [row['case'] for row in added['cases']] == list(extra_controls.ORDER),
                 'Additional16 ordered controls changed')
            receipt.update(status='INVENTORY_COMPONENT_CONTROLS_RETURNED', original=old, additional=added,
                           case_count=27)
        else:
            root, pins, expected, spec = prepare_fixture(workspace, scratch)
            inventory = reference.inventory if mode == 'baseline' else candidate.inventory
            expected_typed = extra_controls.typed(expected)
            for index in range(spec['inventory_calls_per_arm']):
                actual = inventory(root, pins)
                need(extra_controls.typed(actual) == expected_typed,
                     'Exact representative output changed at call: ' + str(index))
            raw_output = canonical(actual) + b'\n'
            result_path = output / 'inventory.json'
            result_path.write_bytes(raw_output)
            need(result_path.read_bytes() == canonical(expected) + b'\n', 'Output readback differs')
            # Fresh independent file reader after all calls checks returned values
            # against source-pinned identities; no reference result is reused.
            for row in spec['files']:
                path = root / row['name']
                raw = path.read_bytes()
                need(hashlib.sha256(raw).hexdigest() == row['sha256'] and len(raw) == row['bytes'] and
                     stat.S_IMODE(path.stat().st_mode) == row['mode'], 'Fixture changed after inventory')
            receipt.update(status='INVENTORY_REPRESENTATIVE_COMPONENT_RETURNED',
                           fixture_files=32, fixture_bytes=453700, inventory_calls=128,
                           output_sha256=hashlib.sha256(raw_output).hexdigest(),
                           declared_inventory_file_reads=4096, declared_inventory_read_bytes=58073600,
                           declared_inventory_sha_calls=8192 if mode == 'baseline' else 4096,
                           declared_inventory_sha_bytes=116147200 if mode == 'baseline' else 58073600,
                           counts_status='Source-derived bill; measured instrumentation is in controls only')
    finally:
        if scratch.exists():
            shutil.rmtree(scratch)
        need(not scratch.exists(), 'Fixture cleanup incomplete')
    after = authenticate(workspace)
    need(before == after, 'Source custody changed across component work')
    receipt['source_custody'] = after
    receipt['cleanup_complete'] = True
    receipt_path = output / 'component-receipt.json'
    receipt_bytes = canonical(receipt) + b'\n'
    receipt_path.write_bytes(receipt_bytes)
    need(receipt_path.read_bytes() == receipt_bytes, 'Receipt readback differs')
    need({path.name for path in output.iterdir()} == ({'component-receipt.json'} if mode == 'controls'
         else {'component-receipt.json', 'inventory.json'}), 'Unexpected retained output')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('controls', 'baseline', 'candidate'), required=True)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    receipt = run(args.mode, args.workspace.resolve(), args.output.resolve())
    print(json.dumps({'status': receipt['status'], 'mode': args.mode,
                      'optimization': sys.flags.optimize}, sort_keys=True))


if __name__ == '__main__':
    main()
