"""Optional numerical nomination; every reported obstruction is checked exactly.

Requires NumPy/SciPy; the standalone verifier does not. LP infeasibility,
timeouts, failed rational reconstruction, and other solver outcomes mean
unclassified, never that an invertible circuit exists.
"""
if not __debug__:
    raise SystemExit('Run without -O: inherited Clifford checks require assertions.')

import argparse
from fractions import Fraction
from itertools import product
import gzip
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import model
from valuation import symbolic_records, targets, allowed, check


def nominate(records, blocks, frames=None):
    import numpy as np
    from scipy.optimize import linprog

    nw = 3*(blocks-1)
    nv = nw+6
    equal, lower = [], []
    for record in records:
        degrees = []
        for path in record['paths']:
            row = [0]*nv
            for k, role in enumerate(path):
                row[3*k+role] += 1
            degrees.append(row)
        if allowed(record, frames):
            for row in degrees:
                row[nw+record['output']] -= 1
                row[nw+3+record['column']] -= 1
                lower.append(row)
        else:
            equal.extend([[a-b for a, b in zip(row, degrees[0])] for row in degrees[1:]])
    lower.append([-1]*nw+[1]*6)
    bounds = [0]*(len(lower)-1)+[1]
    result = linprog(np.zeros(nv), A_ub=-np.asarray(lower), b_ub=-np.asarray(bounds),
                     A_eq=np.asarray(equal) if equal else None,
                     b_eq=np.zeros(len(equal)) if equal else None,
                     bounds=[(None, None)]*nv, method='highs',
                     options={'threads': 1})
    answer = {'status': 'unclassified', 'solver_status': int(result.status)}
    if result.x is None:
        return answer
    rational = [Fraction(float(x)).limit_denominator(1000000) for x in result.x]
    scale = math.lcm(*(x.denominator for x in rational))
    vector = [int(x*scale) for x in rational]
    divisor = math.gcd(*vector)
    if divisor:
        vector = [x//divisor for x in vector]
    try:
        gap = check(records, blocks, vector, frames)
    except ValueError:
        return answer
    return {'status': 'excluded_exact', 'vector': vector, 'gap': gap}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--case', default=None, help='ID in the pinned PR705 corpus')
    source.add_argument('--word', type=Path, help='JSON literal program, or object with a program field')
    parser.add_argument('--all-frames', action='store_true', help='Try every full-rank frame triple')
    parser.add_argument('--out', type=Path, required=True, help='Write nominations outside this package')
    args = parser.parse_args()
    if args.word:
        raw = json.loads(args.word.read_text())
        raw = raw['program'] if isinstance(raw, dict) else raw
    else:
        cases = json.loads(gzip.decompress((ROOT/'words.json.gz').read_bytes()))['cases']
        raw = next(c['program'] for c in cases if c['id'] == (args.case or 'evolved-27'))
    records, blocks = symbolic_records(model.decode(raw))
    choices = list(product(*targets(records))) if args.all_frames else [None]
    answer = [{'frames': frames, 'result': nominate(records, blocks, frames)} for frames in choices]
    args.out.write_text(json.dumps(answer, indent=2)+'\n')
    print(json.dumps({'choices': len(answer),
                      'excluded_exact': sum(a['result']['status'] == 'excluded_exact' for a in answer)}))


if __name__ == '__main__':
    main()
