#!/usr/bin/env python3
"""Compare every Gram entry and time complete audits in fresh interpreters."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
BASE = '66849e1475c930fd7732b1a0067ffee7e1e95f60'
PINS = {
    'research/single-intersection-packing/baseline.py':
        '08ddae46e5621a5b4c525b504e67ae655abe9b49461d894feaa7abc89a51847d',
    'scripts/experiments/single_intersection_witnesses.json':
        'c2308a3d21991f5828b0519b191b470f48b2fbbcaa5af0f7aed3986cc7534185',
    'scripts/audit_single_intersection.py':
        '1de7f9a62edc93c624ff2693ae9bb725cf6dc9735ff1caad56f6913aae9448ee',
}
SOURCE = 'scripts/experiments/single_intersection.py'
CERTIFICATE_SHA256 = '59bca430c5cda9050b346f0f89ff980c9e610a30786cd19677911a1eb433d5b8'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_baseline():
    for name, expected in PINS.items():
        require(digest((ROOT / name).read_bytes()) == expected,
                'Pinned source changed: ' + name)
    spec = importlib.util.spec_from_file_location('orbit_baseline', HERE / 'baseline.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample(engine):
    # Import before timing, identically in both fresh worker processes.
    baseline = load_baseline()
    import audit_single_intersection as audit
    from prepare_layers import serializable
    if engine == 'baseline':
        audit.verify_feature_orbit = baseline.verify_feature_orbit
    started = time.perf_counter()
    result = serializable(audit.certificate())
    elapsed = time.perf_counter() - started
    # Permit exactly the implementation-source binding to differ. Everything
    # else, including all other source bindings and all 5,257 rows, is hashed.
    require(result['source_sha256'][SOURCE] == digest((ROOT / SOURCE).read_bytes()),
            'Current implementation is not bound to the certificate')
    result['source_sha256'][SOURCE] = PINS['research/single-intersection-packing/baseline.py']
    normalized = (json.dumps(result, indent=2, sort_keys=True) + '\n').encode()
    require(digest(normalized) == CERTIFICATE_SHA256,
            'Full predecessor certificate changed beyond the implementation binding')
    return {
        'engine': engine,
        'audit_seconds': elapsed,
        'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                          * (1 if sys.platform == 'darwin' else 1024),
        'certificate_sha256_with_original_source_binding': digest(normalized),
    }


def compare_rows():
    baseline = load_baseline()
    from experiments.single_intersection import minor_rows
    fixtures = json.loads((ROOT / 'scripts/experiments/single_intersection_witnesses.json').read_text())
    comparisons = []
    for fixture in fixtures['feature_orbits']:
        labels, j = fixture['labels'], fixture['j']
        expected = baseline.minor_rows(labels, j)
        actual = minor_rows(labels, j)
        require(actual == expected, 'Complete packed Gram matrix differs')
        width = (len(labels) + 7) // 8
        sha = hashlib.sha256()
        for row in actual:
            sha.update(row.to_bytes(width, 'little'))
        comparisons.append({
            'h': fixture['h'], 'k': fixture['k'], 'j': j,
            'rows': len(labels), 'entries_compared': len(labels) ** 2,
            'packed_rows_sha256': sha.hexdigest(),
        })
    return comparisons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--worker', choices=('baseline', 'packed'), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.rounds < 1:
        parser.error('--rounds must be positive')
    if args.worker:
        print(json.dumps(sample(args.worker)))
        return
    if args.output and args.output.exists():
        parser.error('--output must be a fresh path')
    rows = compare_rows()
    samples = []
    for turn in range(args.rounds):
        order = ('baseline', 'packed') if turn % 2 == 0 else ('packed', 'baseline')
        for engine in order:
            command = [sys.executable, '-B']
            if sys.flags.optimize:
                command.append('-O')
            command += [str(Path(__file__).resolve()), '--worker', engine]
            run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
            result = json.loads(run.stdout)
            samples.append(result)
            print(engine, f"{result['audit_seconds']:.3f}s", flush=True)
    medians = {
        engine: statistics.median(s['audit_seconds'] for s in samples if s['engine'] == engine)
        for engine in ('baseline', 'packed')
    }
    report = {
        'status': 'PASS_IDENTICAL_GRAM_ROWS_AND_COMPLETE_CERTIFICATES',
        'base_commit': BASE, 'assignment_seed': 86,
        'python': sys.version, 'platform': platform.platform(), 'machine': platform.machine(),
        'source_pins': PINS, 'packed_source_sha256': digest((ROOT / SOURCE).read_bytes()),
        'row_comparisons': rows, 'samples': samples, 'median_audit_seconds': medians,
        'speedup': medians['baseline'] / medians['packed'],
        'scope': 'Four committed orbit witnesses and 5,257 historical cases; no new kappa.',
    }
    if args.output:
        with args.output.open('x') as stream:
            stream.write(json.dumps(report, indent=2) + '\n')
    print(report['status'], f"speedup={report['speedup']:.3f}x")


if __name__ == '__main__':
    main()
