#!/usr/bin/env python3
"""One-command reproduction: census -> greedy loan + snapshot passes -> re-census, on any P104 native word.

    python3 engine/run_on.py WORD.json.gz [OUT_PREFIX] [MAX_PASSES]

Runs run7621.py (exact two-shape census of the loan + stationary-snapshot move, greedy gain-ordered
try_instance over it, each hit accepted only if check.full passes, owned peak <= 50 and the PRICEKIT kappa rises,
then a re-census) and writes OUT_PREFIX_<n>.json.gz (n = instances landed) and OUT_PREFIX_log.json.
Standard library only; one process; under 1 GB. On #7621's word it lands the 14 instances of hit_loan_14.
"""
import os
import runpy
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    word = os.path.abspath(argv[1])
    out = os.path.abspath(argv[2]) if len(argv) > 2 else os.path.join(tempfile.mkdtemp(prefix='loan-'), 'out')
    maxpass = argv[3] if len(argv) > 3 else '6'
    sys.argv = [os.path.join(HERE, 'run7621.py'), word, out, maxpass]
    print('output prefix', out, flush=True)
    runpy.run_path(sys.argv[0], run_name='__main__')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
