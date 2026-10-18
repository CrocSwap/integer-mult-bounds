"""Bounded 42-order capacity screen; no owner witness or endpoint claim.

Apache-2.0. OpenAI Codex assistance; PR2530 supplies exact actual_windows.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import maximum_flow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--prepared', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    sp = importlib.util.spec_from_file_location('window_source', a.prepared/'vendor/build_parent.py')
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    parent = mod.read(a.prepared/'inputs/GLOBAL-TEMPLATE.json.gz')
    calls = [(s, r) for s in range(9) for r in range(74)]
    cases = []
    for k in range(1, 13):
        for rev in [False, True]:
            cases.append((f'diagonal-{k}-reverse-{rev}',
                sorted(calls, key=lambda sr: (k*sr[0]+sr[1], -sr[0] if rev else sr[0], sr[1]))))
    for stage in range(9):
        for sign in [-1, 1]:
            cases.append((f'stage-{stage}-half-{sign}', sorted(calls,
                key=lambda sr: (8*sr[0]+2*sr[1]+sign*(sr[0] == stage), sr[0], sr[1]))))
    results = []
    for label, order in cases:
        windows, _ = mod.actual_windows(parent, order)
        gs = [v for v in windows.values() if v[0] == 8]
        sink = 667+len(gs)
        edges = [(0, 1+t, 78) for t in range(666)]
        for g, (_, times) in enumerate(gs):
            edges.append((667+g, sink, 112))
            edges.extend((1+t, 667+g, 112) for t in times)
        rows, cols, vals = zip(*edges)
        mat = coo_matrix((np.array(vals, dtype=np.int64), (rows, cols)), shape=(sink+1, sink+1)).tocsr()
        value = maximum_flow(mat, 0, sink).flow_value
        record = dict(order=label, rank8_capacity_loss=int(112*len(gs)-value))
        results.append(record)
        print(record, flush=True)
    a.out.write_text(json.dumps(dict(scope='One-width capacity nomination only; not a complete packing', results=results), indent=2))


if __name__ == '__main__':
    main()
