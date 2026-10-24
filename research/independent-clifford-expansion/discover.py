#!/usr/bin/env python3
"""Optional compiled floating discovery; no supplier admission follows.

Apache-2.0. Cinna Davis, with substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
import algebra as A


def encoded(model):
    keys = sorted(model['operators'])
    index = {op: i for i, op in enumerate(keys)}
    frozen = set(model['frozen'])
    lines = [f"{len(model['charts'])} {len(model['contacts'])} {len(keys)}"]
    lines += [f"{int(i in frozen)} " + ' '.join(map(str, c)) for i, c in enumerate(model['charts'])]
    lines += [' '.join(map(str, model['operators'][op])) for op in keys]
    lines += [f'{a} {b} {index[op] if op else -1} {sign}' for a,b,op,sign in model['contacts']]
    return '\n'.join(lines) + '\n'


def replay(model, moves):
    charts = list(model['charts'])
    frozen = set(model['frozen'])
    for round_, node, axis, delta in moves:
        A.need(node not in frozen and 0 <= node < len(charts), 'valid unfrozen group')
        A.need(0 < axis < (1 << (2*model['width'])), 'valid nonzero Pauli axis')
        old = charts[node]
        charts[node] = A.turn(old, axis, model['width'])
        A.need(A.distance(old, charts[node], model['width']) == 1, 'actual distance-one chart change')
    return charts


def run(seed, rounds, plateau, collapse=True):
    model = A.build(collapse)
    data = encoded(model)
    started = time.monotonic()
    compiler_path = shutil.which('g++') or shutil.which('clang++')
    A.need(compiler_path is not None, 'C++17 compiler required')
    compiler = subprocess.run([compiler_path, '--version'], check=True, capture_output=True, text=True).stdout.splitlines()[0]
    with tempfile.TemporaryDirectory(prefix='independent-chart-') as td:
        binary = str(Path(td) / 'search')
        subprocess.run([compiler_path, '-std=c++17', '-O3', '-Wall', '-Wextra', str(A.HERE / 'search.cpp'), '-o', binary], check=True)
        process = subprocess.run([binary, str(seed), str(rounds), str(int(plateau))], input=data,
                                 text=True, capture_output=True, check=True, timeout=240)
    moves, summaries = [], []
    for line in process.stdout.splitlines():
        row = line.split()
        if row[0] == 'MOVE':
            moves.append([int(row[1]), int(row[2]), int(row[3]), float(row[4])])
        elif row[0] == 'ROUND':
            summaries.append(dict(round=int(row[1]), moves=int(row[2]), strict=int(row[3]), floating_delta=float(row[4])))
        else:
            raise ValueError('unexpected search record')
    charts = replay(model, moves)
    paid, helpers = A.invoice(model, charts)
    paid0, helpers0 = A.invoice(model, model['charts'])
    def moment(p):
        return sum(count * rank ** (1-.00302177585) for rank, count in p.items())
    delta = moment(paid)-moment(helpers)-moment(paid0)+moment(helpers0)
    A.need(abs(delta-sum(m[3] for m in moves)) < 1e-7, 'independent complete invoice delta equals compiled move sum')
    return dict(scope='FLOATING_DISCOVERY_WITH_EXACT_FINAL_RANK_INVOICE_NO_NEW_KAPPA',
                seed=seed, seed_origin='OS randomness' if SEED_FROM_OS else 'explicit reproducible seed',
                rounds_requested=rounds, plateau=plateau, collapse_zero=collapse,
                source_base='81e9bd69e4a5b00ba9c713a1620e36d576d5522e',
                source_sha256=sha256((A.ROOT/'research/general-gaussian-contact-search/inputs/round3-word.json.gz').read_bytes()).hexdigest(),
                graph_sha256=sha256(data.encode()).hexdigest(), search_sha256=sha256((A.HERE/'search.cpp').read_bytes()).hexdigest(),
                compiler=compiler, python=platform.python_version(), platform=platform.platform(),
                elapsed_seconds=time.monotonic()-started, groups=len(charts),
                free_groups=len(charts)-len(model['frozen']), original_nodes=model['original_nodes'],
                incidences=len(model['contacts']), neighbor_count_per_group=1022,
                rounds=summaries, moves=moves, paid=dict(sorted(paid.items())),
                helpers=dict(sorted(helpers.items())), baseline_paid=dict(sorted(paid0.items())),
                baseline_helpers=dict(sorted(helpers0.items())), floating_local_energy=delta,
                final_chart_sha256=sha256(json.dumps(charts,separators=(',',':')).encode()).hexdigest())


SEED_FROM_OS = False


def main():
    global SEED_FROM_OS
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int)
    ap.add_argument('--rounds', type=int, default=8)
    ap.add_argument('--plateau', action='store_true')
    ap.add_argument('--uncontracted', action='store_true')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    A.need(0 < args.rounds <= 100, 'bounded discovery rounds')
    seed = args.seed
    if seed is None:
        seed = int.from_bytes(os.urandom(8), 'big')
        SEED_FROM_OS = True
    A.need(0 <= seed < 1 << 64, 'unsigned 64-bit seed')
    print(json.dumps(dict(seed=seed, rounds=args.rounds, plateau=args.plateau)), flush=True)
    result = run(seed, args.rounds, args.plateau, not args.uncontracted)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('moves',)}, sort_keys=True))


if __name__ == '__main__':
    main()
