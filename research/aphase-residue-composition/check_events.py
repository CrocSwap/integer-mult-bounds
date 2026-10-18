#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the independent PR2853 event, source-word and exact-moment audit."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
CHECKER_SHA256 = 'f30de7e4a8ad7fb0566169d5a448a373f9de80afec943cd36475eeaaa492c301'
BASIS_SHA256 = '73c9a7243c6dec623ced189ed3a82b16835f5935153799b9c5a1824d46b0f7f9'


def need(value, message):
    if not value:
        raise ValueError(message)


def authenticate_derivation():
    bundle = HERE / 'event-checker'
    checker = bundle / 'independent_events.py'
    basis = (bundle / 'reference/previous_independent_events.py').read_bytes()
    actual = checker.read_bytes()
    need(hashlib.sha256(basis).hexdigest() == BASIS_SHA256, 'exact independent predecessor checker')
    need(hashlib.sha256(actual).hexdigest() == CHECKER_SHA256, 'exact reviewed independent checker')
    derivation = json.loads((bundle / 'DERIVATION.json').read_bytes())
    need(derivation['source_checker_sha256'] == BASIS_SHA256
         and derivation['target_sha256'] == CHECKER_SHA256, 'event derivation endpoints')
    text = basis.decode()
    for change in derivation['changes']:
        need(text.count(change['old']) == 1, 'unique event checker replacement')
        text = text.replace(change['old'], change['new'])
    need(text.encode() == actual, 'complete exact event checker derivation')
    return checker


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=HERE.parent / 'gmx-t74-borrow43-handoff')
    parser.add_argument('--candidate', type=Path, default=HERE / 'data')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    source, candidate = args.source.resolve(), args.candidate.resolve()
    checker = authenticate_derivation()
    with tempfile.TemporaryDirectory(prefix='p53-independent-events-') as temporary:
        output = args.out.resolve() if args.out else Path(temporary) / 'RESULT.json'
        need(not output.exists(), 'fresh receipt required')
        need(all(not output.is_relative_to(path) for path in (HERE, source, candidate)),
             'receipt must be outside package and inputs')
        result = subprocess.run([sys.executable, '-I', '-O', '-B', str(checker),
                                 '--predecessor', str(source), '--candidate', str(candidate),
                                 '--out', str(output)], stdin=subprocess.DEVNULL, check=False)
        need(result.returncode == 0, 'independent event audit failed')
        receipt = json.loads(output.read_bytes())
        need(receipt['status'] == 'PASS_INDEPENDENT_P53_EVENT_CLOCK_PROFILE_AND_MOMENT'
             and len(receipt['controls']) == 10, 'complete event audit and ten controls')


if __name__ == '__main__':
    main()
