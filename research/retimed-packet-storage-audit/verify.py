#!/usr/bin/env python3
"""Restore the pinned runtime offline and reproduce the storage/control audit."""
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ArithmeticError(message)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, default=HERE / 'run-results')
    cli.add_argument('--quick', action='store_true', help='omit only the full 27-high record oracle')
    args = cli.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    source = HERE / 'sources/pr8042'
    manifest = json.loads((HERE / 'SOURCE-BINDINGS.json').read_text())
    require(manifest['commit'] == 'dfd25d553a843a946ca0b94130a5ff8943e98fdd',
            'unexpected source commit')
    for name, record in manifest['files'].items():
        path = Path(name)
        require(not path.is_absolute() and '..' not in path.parts, 'invalid source path')
        data = (source / path).read_bytes()
        require(len(data) == record['size'] and sha256(data).hexdigest() == record['sha256'],
                'retained source differs: ' + name)
    print('PASS_PINNED_SOURCE_BYTES', len(manifest['files']), flush=True)
    spec = spec_from_file_location('pinned_bootstrap', source / 'bootstrap.py')
    bootstrap = module_from_spec(spec)
    spec.loader.exec_module(bootstrap)
    with TemporaryDirectory(prefix='retimed-storage-audit-') as temporary:
        runtime = Path(temporary)
        bootstrap.install(runtime)
        base = [sys.executable, '-B']
        command = base + [str(HERE / 'audit_packets.py'), '--runtime', str(runtime),
                          '--output', str(output / 'exact-trace.json')]
        if not args.quick:
            command.append('--full-high')
        subprocess.run(command, check=True)
        controls = ('missing-inverse', 'lost-highs', 'lost-marker', 'dirty-tail', 'live-scratch')
        for name in controls:
            subprocess.run(base + [str(HERE / 'audit_packets.py'), '--runtime', str(runtime),
                           '--output', str(output / ('exact-control-' + name + '.json')),
                           '--mutation', name], check=True)
        subprocess.run(base + [str(HERE / 'audit_owner_windows.py'), '--runtime', str(runtime),
                       '--output', str(output / 'exact-owner-windows.json')], check=True)
        stop = subprocess.run(base + [str(HERE / 'verify_stopping.py'), '--runtime', str(runtime)],
                              check=True, capture_output=True, text=True)
        stopping = json.loads(stop.stdout)
        require(stopping['status'] == 'PASS_STOPPING_CONTROL_AUDIT', 'stopping audit failed')
        (output / 'stopping.json').write_text(json.dumps(stopping, indent=2) + '\n')
        print(stopping['status'], flush=True)
    trace = json.loads((output / 'exact-trace.json').read_text())
    receipt = {
        'status': 'PASS_RETIMED_STORAGE_AND_STOPPING_AUDIT',
        'source_commit': manifest['commit'],
        'source_files_validated': len(manifest['files']),
        'python': platform.python_version(),
        'full_high_fixture': not args.quick,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'packet_cases': [{key: case[key] for key in ('case', 'records', 'same_stage_calls',
                           'max_nested_weighted_depth', 'itineraries', 'earlier_stage_calls')}
                         for case in trace['cases']],
        'source_mutations_rejected': list(controls) + ['live-count-owner-base'],
        'stopping_status': stopping['status'],
        'scope': 'source-bound packet and allocator invariants plus supplemental serial stop control; '
                 'no production-rank execution or new global resource constant',
    }
    (output / 'RESULT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], flush=True)


if __name__ == '__main__':
    main()
