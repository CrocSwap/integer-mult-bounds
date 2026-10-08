#!/usr/bin/env python3
"""Export exact local templates for the direct intersection-two producer.

The default C++ consumer merges supports by 256-bit fingerprints; its output
is only a discovery screen. ternary_target_exact.cpp consumes the same plan
using canonical ZDD equality and independent expected-output-family checks.
"""
from itertools import combinations
from math import comb
from pathlib import Path
import argparse
import json
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from intersection_circuit import build, feasible


def export(h, path):
    nl, nr = h//2, h-h//2
    inputs = list(combinations(range(h), 5))
    input_index = {t: i for i, t in enumerate(inputs)}
    templates, template_index, stages = [], {}, []

    def template(key):
        if key not in template_index:
            c = build(*key)
            mapping = {i: i for i in range(len(c.inputs)+1)}
            gates = []
            for node in c.active:
                if c.args[node]:
                    a, b = c.args[node]
                    gates.append((mapping[a], mapping[b]))
                    mapping[node] = len(c.inputs)+len(gates)
            outputs = [mapping[n] for n in c.outputs]
            template_index[key] = len(templates)
            templates.append((key, len(c.inputs), gates, outputs))
        return template_index[key]

    for degree in (5, 2):
        targets = list(combinations(range(h), degree))
        target_index = {t: i for i, t in enumerate(targets)}
        cases = []
        for b in range(max(0, degree-nr), min(degree, nl)+1):
            TL = list(combinations(range(nl), b))
            TR = list(combinations(range(nr), degree-b))
            outmap = [target_index[s+tuple(nl+x for x in t)] for s in TL for t in TR]
            for a in range(max(0, 5-nr), min(5, nl)+1):
                IL = list(combinations(range(nl), a))
                IR = list(combinations(range(nr), 5-a))
                source_map = [input_index[s+tuple(nl+x for x in t)]+1 for s in IL for t in IR]
                for u in range(3):
                    if not feasible(nl, a, b, u) or not feasible(nr, 5-a, degree-b, 2-u):
                        continue
                    left = template((nl, a, b, u))
                    right = template((nr, 5-a, degree-b, 2-u))
                    lc, rc = len(templates[left][2]), len(templates[right][2])
                    left_first = len(IR)*lc+len(TL)*rc <= len(TR)*lc+len(IL)*rc
                    cases.append((left, right, len(IL), len(IR), len(TL), len(TR),
                                  int(left_first), source_map, outmap))
        stages.append((len(targets), cases))

    with path.open('wb') as f:
        def words(values):
            f.write(struct.pack('<'+'I'*len(values), *values))
        words([h, len(inputs), len(templates), len(stages)])
        for key, ni, gates, outs in templates:
            words([*key, ni, len(gates), len(outs)])
            words([x for pair in gates for x in pair])
            words(outs)
        for target_count, cases in stages:
            words([target_count, len(cases)])
            for left, right, il, ir, tl, tr, first, sources, targets in cases:
                words([left, right, il, ir, tl, tr, first])
                words(sources)
                words(targets)
    return dict(h=h, inputs=len(inputs), local_templates=len(templates),
                local_additions=sum(len(t[2]) for t in templates),
                top_cases=[len(cases) for _, cases in stages], bytes=path.stat().st_size)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, default=14)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--binary', type=Path, default=Path('/private/tmp/ternary-target-fingerprint'))
    args = parser.parse_args()
    start = time.monotonic()
    print(json.dumps(export(args.h, args.plan)), flush=True)
    if args.run:
        subprocess.run(['c++', '-std=c++17', '-O3', str(Path(__file__).with_suffix('.cpp')),
                        '-o', str(args.binary)], check=True)
        subprocess.run([str(args.binary), str(args.plan)], check=True)
    print(json.dumps(dict(export_and_run_seconds=time.monotonic()-start)), flush=True)
