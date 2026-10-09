#!/usr/bin/env python3
# Copyright 2026 icekylinx. Apache-2.0.
"""Verify the selected GPT-6 Astra source-assisted construction increment.

Immutable public sources retain their original authorship. Generated graphs,
transcripts and logs stay in a temporary or explicitly requested work directory.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'research/source-assisted'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, log, cwd):
    with log.open('w') as stream:
        result = subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Increment failed: {log}\n{log.read_text()[-6000:]}')


def verify(work, arithmetic_only):
    source = json.loads((PACKAGE / 'SOURCE.json').read_text())
    for name, expected in source['sha256'].items():
        require(digest(PACKAGE / name) == expected, 'Source hash differs: ' + name)
    package = work / 'package'
    shutil.copytree(PACKAGE, package)
    with tarfile.open(package / 'public/pr168_fd25adb7.tar.gz', 'r:gz') as archive:
        for member in archive:
            relative = Path(member.name)
            require(member.isfile() and not relative.is_absolute() and
                    '..' not in relative.parts and relative.parts[0] == 'pr168_fd25adb7',
                    'Unsafe frozen source archive member')
            target = package / 'public' / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as inp, target.open('wb') as out:
                shutil.copyfileobj(inp, out)
    public = json.loads((package / 'public/SOURCE_MANIFEST.json').read_text())
    for item in public['files']:
        raw = (package / 'public/pr168_fd25adb7' / item['path']).read_bytes()
        require(len(raw) == item['expected_bytes'] and
                hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
                == item['git_blob_sha'], 'Public git blob differs: ' + item['path'])
    flow = package / 'decision/aligned_parity_purified_flow.result.witness.json'
    with gzip.open(flow.with_suffix('.json.gz'), 'rb') as inp, flow.open('wb') as out:
        shutil.copyfileobj(inp, out)
    require(digest(flow) == source['flow_uncompressed_sha256'], 'Compressed flow differs')
    output = work / 'output'
    command = [sys.executable, str(package / 'reproduce.py'), '--output', str(output)]
    if arithmetic_only:
        command.append('--arithmetic-only')
    run(command, work / 'reproduction.log', package)
    if not arithmetic_only:
        run([sys.executable, str(ROOT / 'scripts/source_assisted/complex_allocated_replay.py'),
             '--package', str(package), '--cache', str(output / 'complex/aligned_parity/cache'),
             '--transcript', str(work / 'complex-transcript.json'),
             '--out', str(work / 'complex-allocated-replay.json')],
            work / 'complex-allocated-replay.log', ROOT)
    # Regeneration receipts contain cache paths, elapsed times and gzip headers.
    # Bind the published certificate to the frozen selected inputs after those
    # inputs' constructive fields have been independently regenerated above.
    canonical = work / 'canonical-certificate.json'
    run([sys.executable, str(package / 'global/assemble_profiles.py'),
         '--complex', str(package / 'decision/complex_source_aligned_profile.json'),
         '--bit', str(package / 'bit/source_aligned_profile.json'),
         '--bit-lifts', str(package / 'bit/source_aligned_lifts.json'),
         '--output', str(canonical)], work / 'canonical-arithmetic.log', package)
    result = json.loads(canonical.read_text())
    expected = json.loads((PACKAGE / 'global/global_certificate.json').read_text())
    for key in ('kappa', 'assembly'):
        require(result[key] == expected[key], 'Exact certificate differs: ' + key)
    validation_path = ROOT / 'certificates/source-assisted-validation.json'
    validation = json.loads(validation_path.read_text())
    if not arithmetic_only:
        actual_replay = json.loads((work / 'complex-allocated-replay.json').read_text())
        require(actual_replay == validation['complex_scalar_replay'],
                'Independent scalar replay differs from its receipt')
    for key in ('fixed_doubling_target', 'ratio_to_reviewed_baseline',
                'ratio_to_reviewed_baseline_decimal', 'doubling_achieved'):
        result.pop(key, None)
    for branch in ('complex', 'bit'):
        result[branch].pop('numerical_root_for_discovery_only', None)
    result['integration'] = {
        'source_manifest_sha256': digest(PACKAGE / 'SOURCE.json'),
        'verifier_sha256': digest(Path(__file__)),
        'complex_allocated_replay_sha256': digest(ROOT / 'scripts/source_assisted/complex_allocated_replay.py'),
        'proof_sha256': digest(ROOT / 'notes/source-assisted-note.tex'),
        'validation_receipt_sha256': digest(validation_path),
        'scope': 'Exact local maps, complete flow/boundary ledgers and conditional assembly. '
                 'Additional complex scalar transcript probes; no new flattened bit transcript '
                 'or full Clifford/router replay.',
    }
    return result


def main():
    require(not sys.flags.optimize, 'Assertions required; do not use -O')
    sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arithmetic-only', action='store_true')
    parser.add_argument('--work', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT / 'certificates/source-assisted-network.json')
    args = parser.parse_args()
    if args.work:
        args.work.mkdir(parents=True, exist_ok=False)
        result = verify(args.work.resolve(), args.arithmetic_only)
    else:
        with tempfile.TemporaryDirectory(prefix='source-assisted-') as temporary:
            result = verify(Path(temporary), args.arithmetic_only)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print('PASS conditional kappa = 6.566436e-4; ' +
          ('recorded-profile arithmetic only' if args.arithmetic_only else
           'new construction regeneration and complex scalar dirty replay'))


if __name__ == '__main__':
    main()
