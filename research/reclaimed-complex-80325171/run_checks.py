#!/usr/bin/env python3
"""Verify frozen bytes and optionally rerun original independent checkers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

if not __debug__ or os.environ.get('PYTHONOPTIMIZE'):
    raise RuntimeError('Assertions must be enabled; -O/-OO/PYTHONOPTIMIZE are unsupported')

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--replay', action='store_true', help='replay the accepted complex witness and exact assembly')
parser.add_argument('--bit-controls', action='store_true', help='also run the independent bounded stopped-bit controls')
args = parser.parse_args()
manifest = json.loads((ROOT / 'RELEASE_MANIFEST.json').read_text())
files = manifest['files']
if not (0 < len(files) < 100):
    raise ValueError('Unexpected release size')
seen = set()
for entry in files:
    rel = Path(entry['path'])
    if rel.is_absolute() or '..' in rel.parts or str(rel) in seen:
        raise ValueError(('Unsafe or repeated manifest path', str(rel)))
    seen.add(str(rel))
    path = ROOT / rel
    raw = path.read_bytes()
    if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
        raise ValueError(('Changed or corrupt release file', str(rel)))

# Check the same path layout as the accepted checkers, without importing them.
cx = ROOT / 'research/explore_complex_ceiling_breakthrough/pr97_port'
for entry in json.loads((cx / 'H24_WITNESS_MANIFEST.json').read_text())['files']:
    raw = (ROOT / entry['path']).read_bytes()
    if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
        raise ValueError(('Component manifest mismatch', entry['path']))
author = ROOT / 'research/explore_complex_ceiling_breakthrough/compose_pr104'
for entry in json.loads((author / 'INPUT_PINS.json').read_text()).values():
    if hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError(('Composition input mismatch', entry['path']))
administrative = json.loads((ROOT / 'ADMINISTRATIVE_PIN_AMENDMENT.json').read_text())
if administrative['path'] != 'pool/frontier/PR97_f5f9c56/ADOPTION.json':
    raise ValueError('Administrative exception may not name any other path')
administrative_seen = 0
for entry in json.loads((cx / 'SOURCE_BINDING.json').read_text())['sources']:
    raw = (ROOT / entry['local']).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if entry['local'] == administrative['path']:
        if (entry['sha256'] != administrative['historical_sha256']
                or digest != administrative['packaged_sha256']
                or json.loads(raw)['scientific_predecessor_head'] != administrative['scientific_predecessor_head']):
            raise ValueError('Administrative provenance amendment mismatch')
        administrative_seen += 1
    elif digest != entry['sha256']:
        raise ValueError(('Scientific source binding mismatch', entry['local']))
if administrative_seen != 1:
    raise ValueError('Expected exactly one explicitly amended administrative record')
acceptance = ROOT / 'research/verify_complex_reclamation_ledger/ASSEMBLY_REVIEW/ACCEPTANCE.json'
for entry in json.loads(acceptance.read_text())['files']:
    raw = (ROOT / entry['path']).read_bytes()
    if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
        raise ValueError(('Frozen acceptance mismatch', entry['path']))
print(f'PASS: {len(files)} immutable files; component, composition and source pins closed.', flush=True)

checks = []
if args.replay:
    checks.extend([
        'research/verify_complex_reclamation_ledger/replay_h24.py',
        'research/verify_complex_reclamation_ledger/ASSEMBLY_REVIEW/check_assembly.py',
    ])
if args.bit_controls:
    checks.append('research/verify_stopped_product_interchange/check.py')

def limits():
    # These original checks previously used under 100 MiB. No upstream code runs.
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (384 * 1024**2, 384 * 1024**2))
        resource.setrlimit(resource.RLIMIT_CPU, (120, 120))
    except (ImportError, AttributeError):
        pass

if checks:
    # Keep accepted receipts immutable even though the original checkers emit
    # runtime-dependent result files at their own reviewed locations.
    with tempfile.TemporaryDirectory(prefix='reclaimed-complex-check-') as tmp:
        dest = Path(tmp)
        for entry in files:
            target = dest / entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / entry['path'], target)
        for relative in checks:
            started = time.monotonic()
            result = subprocess.run(
                [sys.executable, str(dest / relative)], cwd=dest,
                text=True, capture_output=True, timeout=120,
                preexec_fn=limits if os.name == 'posix' else None,
            )
            if result.returncode:
                print(result.stdout)
                print(result.stderr, file=sys.stderr)
                raise SystemExit(f'FAIL: {relative} (exit {result.returncode})')
            print(f'PASS: {relative} ({time.monotonic()-started:.2f} seconds)', flush=True)
print('No upstream producer or verifier was executed.')
