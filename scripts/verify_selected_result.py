#!/usr/bin/env python3
"""Bind the published selection to its frozen finite certificate and proof files.

This fast check does not replay the construction. Run make gen4-bank-verify
for the complete selected finite replay. Douglas Colkitt, with OpenAI Codex
assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def path(root, relative):
    p = (root / relative).resolve()
    require(p.is_relative_to(root.resolve()) and p.is_file(), 'Invalid selected file: ' + relative)
    return p


def check(record, root=ROOT):
    certificate_path = path(root, record['certificate'])
    certificate = json.loads(certificate_path.read_text())
    kappa = Fraction(record['kappa'])
    require(kappa > 0 and kappa == Fraction(certificate['kappa']), 'Selected kappa differs from finite certificate')
    require(kappa == Fraction(record['decimal']), 'Selected decimal differs from exact kappa')
    require(sha256(certificate_path.read_bytes()).hexdigest() == record['certificate_sha256'],
            'Selected certificate bytes changed')
    manifest_path = path(root, record['source_manifest'])
    manifest = json.loads(manifest_path.read_text())
    require(manifest.get('files'), 'Empty selected source inventory')
    package = manifest_path.parent
    actual = {p.relative_to(package).as_posix(): sha256(p.read_bytes()).hexdigest()
              for p in package.rglob('*') if p.is_file() and p != manifest_path}
    require(actual == manifest['files'], 'Selected package inventory or bytes changed')
    require(record['proof_supplements'], 'Missing bank scheduling supplement')
    for relative, digest in record['proof_supplements'].items():
        require(sha256(path(root, relative).read_bytes()).hexdigest() == digest,
                'Selected proof supplement changed: ' + relative)
    for key in ('proof', 'review', 'validation'):
        path(root, record[key])
    return kappa


def main():
    require(not sys.flags.optimize, 'Assertions must remain enabled for the verification pipeline')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, default=ROOT / 'certificates/selected-result.json',
                        help='Selected or historical checkpoint record to verify')
    args = parser.parse_args()
    record = json.loads(args.record.read_text())
    kappa = check(record)
    print('PASS selected record, exact kappa, original source inventory and proof supplement: ' + str(kappa))


if __name__ == '__main__':
    main()
