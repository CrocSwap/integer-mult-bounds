#!/usr/bin/env python3
"""Replay all twelve pinned quadratic-affine witnesses without overwriting them.

Copyright 2026 Curtis Dransfield, substantial OpenAI Codex assistance.
Apache-2.0. Uses Douglas Colkitt's original finite audit and source checks.
"""
import argparse
from functools import partial
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check_sources(root=ROOT):
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    for relative, digest in manifest['files'].items():
        path = root / relative
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Pinned input changed: ' + relative)
    return manifest


def run(engine, compare_rows=False):
    if sys.flags.optimize:
        raise ValueError('Assertions must remain enabled for the inherited audit')
    check_sources()
    sys.path.insert(0, str(ROOT / 'scripts'))
    import audit_quadratic_affine as audit
    import experiments.quadratic_affine as original
    from prepare_layers import serializable
    # The adapter is process-local; the original audit entry point stays intact.
    original_rank = audit.rank_witness
    try:
        if engine == 'packed':
            sys.path.insert(0, str(HERE))
            from packed import rank_witness
            audit.rank_witness = partial(rank_witness, original, compare_rows=compare_rows)
        elif engine != 'original' or compare_rows:
            raise ValueError('Row comparison requires the packed engine')
        certificate = json.dumps(serializable(audit.certificate()), indent=2, sort_keys=True) + '\n'
    finally:
        audit.rank_witness = original_rank
    expected = (ROOT / 'certificates/quadratic-affine-vectors.json').read_text()
    if certificate != expected:
        raise ValueError('Complete certificate differs from the pinned finite witness')
    return certificate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=('original', 'packed'), default='packed')
    parser.add_argument('--compare-rows', action='store_true',
                        help='compare every full packed row to the original pairwise calculation')
    parser.add_argument('--out', type=Path, help='optional fresh certificate output file')
    args = parser.parse_args()
    if args.out is not None and args.out.exists():
        parser.error('Output must not already exist')
    certificate = run(args.engine, args.compare_rows)
    if args.out is not None:
        with args.out.open('x') as out:
            out.write(certificate)
    print('PASS_QUADRATIC_AFFINE_PACKED cases=12 certificate_sha256=' +
          sha256(certificate.encode()).hexdigest() + ' engine=' + args.engine +
          ' compare_rows=' + str(args.compare_rows).lower())


if __name__ == '__main__':
    main()
