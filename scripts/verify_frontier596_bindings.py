#!/usr/bin/env python3
"""Bind the rebuilt PR543 supplier to the PR596 hyperplane-ended construction."""
import argparse
import json
from pathlib import Path
from fractions import Fraction
from verify_frontier588_bindings import check, require


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('bit', 'complex', 'out'):
        ap.add_argument('--' + name, type=Path, required=True)
    a = ap.parse_args()
    result = check(a.bit, a.complex)
    require(Fraction(result['kappa']) == Fraction(16127213726553, 10**16), 'PR596 exact result')
    result['status'] = 'PASS_REBUILT_PR543_PR596_COMPOSITION'
    a.out.write_text(json.dumps(result, indent=2) + '\n')
    print(result['status'], result['decimal'])


if __name__ == '__main__':
    main()
