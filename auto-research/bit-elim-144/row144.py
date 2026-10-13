"""Build #144's bit row after terminal elimination (stdlib only), mirroring scripts/paired_cube_bit.reconstruct():
auxiliary chain steps of the remaining slots (selected slots start at sigma, others at 0), unchanged source chains,
target chains [0, remaining selected sigmas (positive Z support, readout order), redirected write frames in time order,
h-1], gauge children 3*sigma of the remaining selected slots, copied centres, the 2v endpoint children.
Usage: python3 research/bit-elim-144/row144.py PLAN.json OUT_ROW.json"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(ROOT / 'scripts'))
from elim144 import schedule144  # noqa: E402
from paired_cube_bit import child_histogram  # noqa: E402


def build(elim):
    dr, W, D, S, selected, omitted, record = schedule144()
    chosen = set(selected); S.sel = chosen; elim = set(elim)
    h, v, R = S.h, S.v, S.R
    src = Counter()
    for op in S.ops:
        if op[0] == 'add': src[op[2]] += 1
        elif op[0] == 'fan': src[op[1]] += 1
    assert all(u in S.out and u in chosen | set(omitted) and src[u] == 0 for u in elim), 'eliminated: deferred never-source outputs'
    adj = S.adjoint()
    aux = Counter()
    for s in range(R):
        if s in elim: continue
        ds = [S.dim(k) for k in S.chain_keys(s)]
        assert all(b >= a for a, b in zip(ds, ds[1:])) and ds[-1] == h
        for a, b in zip(ds, ds[1:]):
            if b > a: aux[b - a] += 1
    source = Counter(r for path in S.xdata() for r in path if r)
    late_pos = {s: i for i, s in enumerate(S.late_v)}
    red = defaultdict(list)
    for i, op in enumerate(S.ops):
        if op[0] == 'add' and op[1] in elim: red[S.tid[S.out[op[1]][1]]].append(((2, i, 0), S.dim(('n', op[3]))))
        elif op[0] == 'fan':
            for j, f in enumerate(sorted(op[2], key=lambda s: S.dim(S.start_key(s)))):
                if f in elim: red[S.tid[S.out[f][1]]].append(((2, i, j), S.dim(S.start_key(f))))
    for u in elim:
        if u in S.srcop: red[S.tid[S.out[u][1]]].append(((1, late_pos[u], 0), S.dim(('v', u))))
    current = [0] * v; target = Counter()
    for slot in selected:
        if slot in elim: continue
        rank = S.f[slot]
        for t, c in adj[slot].items():
            assert c > 0
            inc = rank - current[t]; assert inc >= 0
            if inc: target[inc] += 1
            current[t] = rank
    for t, lst in red.items():
        for _, rank in sorted(lst):
            inc = rank - current[t]; assert inc >= 0, 'redirected frame below the last read level'
            if inc: target[inc] += 1
            current[t] = rank
    for rank in current:
        assert 0 <= rank <= h - 1
        if rank < h - 1: target[h - 1 - rank] += 1
    assert sum(r * n for r, n in target.items()) == v * (h - 1)
    gauges = Counter(S.f[s] for s in selected if s not in elim)
    children = child_histogram(h, v, aux, source, target, gauges)
    Rn = R - len(elim)
    row = dict(record)
    row.update(R=Rn, W_per_vertex=2 * v + Rn, selected_roles=sum(gauges.values()),
               selected_rank_histogram={str(r): n for r, n in sorted(gauges.items())},
               auxiliary_histogram={str(r): n for r, n in sorted(aux.items()) if n},
               target_data_histogram={str(r): n for r, n in sorted(target.items()) if n},
               child_histogram={str(r): n for r, n in sorted(children.items()) if n},
               rank_per_vertex=sum(r * n for r, n in children.items()), eliminated_roles=len(elim))
    assert row['W_per_vertex'] * row['m'] - row['rank_per_vertex'] == row['deficit_per_vertex'] == 2024
    return row


if __name__ == '__main__':
    plan = json.loads(Path(sys.argv[1]).read_text())
    row = build(plan['elim'])
    Path(sys.argv[2]).write_text(json.dumps(row, indent=1, sort_keys=True) + '\n')
    print('R', row['R'], 'W', row['W_per_vertex'], 'rank', row['rank_per_vertex'], 'selected', row['selected_roles'])
