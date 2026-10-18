#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Deterministic bounded witness discovery; only verify.py certifies the result.

Try two fixed shuffled greedy orders per stratum. A missed witness is an error,
not an infeasibility claim. Never overwrite an existing output.
"""
import argparse
import importlib.util
from itertools import combinations
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('checker', HERE / 'verify.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    v.require(not args.output.exists(), 'refuse to overwrite certificate')
    v.source_pins()
    data = v.geometry()
    cases = []
    for pair in combinations(range(8), 2):
        for strata in v.STRATA:
            readers, sources, spaces = v.model(data, pair, strata)
            ground = []
            for i in range(112):
                for old in range(2):
                    for new in range(2):
                        if readers[old][i] and sources[new][i]:
                            ground.append((i, old, new,
                                v.projected(spaces[old], data['labels'][i]) << (9*old),
                                v.projected(spaces[new+2], data['labels'][i]) << (9*new)))
            for seed in (0, 1):
                order = ground.copy(); random.Random(seed).shuffle(order)
                picked, left, right = [], [], []
                for unit in order:
                    if (sum(t[2] == unit[2] for t in picked) < 8
                            and len(v.basis(left + [unit[3]])) > len(left)
                            and len(v.basis(right + [unit[4]])) > len(right)):
                        picked.append(unit); left.append(unit[3]); right.append(unit[4])
                if len(picked) == 16:
                    break
            case = {'pair': list(pair), 'strata': list(strata), 'units': [list(t[:3]) for t in picked]}
            v.check_case(case, data)
            cases.append(case)
    text = '{"schema_version":1,"cases":[\n' + ',\n'.join(
        json.dumps(row, separators=(',', ':')) for row in cases) + '\n]}\n'
    with args.output.open('x') as out:
        out.write(text)
    print('GENERATED_P112_MASK_CERTIFICATES cases=308; run verify.py for acceptance')


if __name__ == '__main__':
    main()
