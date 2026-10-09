"""Bounded Fano completions with a freely chosen all-role output permutation.

All matrices here are binary scalar maps, not rational frame certificates.
"""
from hashlib import sha256

from certify import require
from finite_bit_contract import scalar_permutation, xor_gate
from experiments.fano_completion import clean_prefix


LAYOUTS = (('compact', True, False), ('decoded', False, False), ('edge', True, True))


def rows_after(W, gates):
    rows = [1 << i for i in range(W)]
    for gate in gates:
        for t, s in gate['xors']:
            rows[t] ^= rows[s]
    return rows


def refinement(rows):
    """Bipartite support-graph color refinement; unique colors prove rigidity.

    Row and column vertices have different initial colors. Each subsequent
    color consists of the old color and the multiset of neighbor colors.
    Every color-preserving graph automorphism preserves every round.
    """
    W = len(rows)
    require(all(0 <= r < 1 << W for r in rows), 'Malformed binary matrix')
    adj = [set() for _ in range(2*W)]
    for i, row in enumerate(rows):
        for j in range(W):
            if row >> j & 1:
                adj[i].add(W+j)
                adj[W+j].add(i)
    colors = [0]*W+[1]*W
    rounds = [colors]
    while True:
        signatures = [(colors[i], tuple(sorted(colors[j] for j in adj[i])))
                      for i in range(2*W)]
        palette = {v: k for k, v in enumerate(sorted(set(signatures)))}
        new = [palette[s] for s in signatures]
        rounds.append(new)
        if len(set(new)) == len(set(colors)):
            break
        colors = new
    return dict(rounds=rounds, singleton_colors=len(set(new)) == 2*W,
                stable_classes=[[i for i, color in enumerate(new) if color == c]
                                for c in sorted(set(new))])


def tie(seed, kind, *indices):
    return sha256((':'.join(map(str, (seed, kind)+indices))).encode()).digest()


def complete(prefix, seed, policy, keep_terminals=False):
    """Gauss-Jordan with free pivot locations: final rows are a permutation.

    No physical row swap is inserted. A pivot location is selected among all
    remaining rows, so output roles can contain different input-role values.
    """
    require(policy in ('sparse', 'dense', 'shuffled'), 'Unknown pivot policy')
    W = prefix['W']
    rows = rows_after(W, prefix['gates'])
    available = set(range(W))
    suffix = []
    pivots = []
    columns = sorted(range(W), key=lambda c: tie(seed, 'column', c))
    if keep_terminals:
        columns = list(range(3))+[c for c in columns if c >= 3]
    for c in columns:
        options = [r for r in available if rows[r] >> c & 1]
        require(options, 'Scalar map is singular')
        sign = 1 if policy == 'sparse' else -1 if policy == 'dense' else 0
        pivot = (3+c if keep_terminals and c < 3 else
                 min(options, key=lambda r: (sign*rows[r].bit_count(), tie(seed, 'row', c, r))))
        require(pivot in options, 'Required terminal cannot be used as a pivot')
        targets = sorted((r for r in range(W) if r != pivot and rows[r] >> c & 1),
                         key=lambda r: tie(seed, 'target', c, r))
        for r in targets:
            suffix.append(xor_gate(r, pivot))
            rows[r] ^= rows[pivot]
        available.remove(pivot)
        pivots.append(dict(column=c, row=pivot, targets=targets))
    require(sorted(rows) == [1 << i for i in range(W)], 'Completion is not a permutation')
    program = dict(W=W, gates=prefix['gates']+suffix)
    scalar_permutation(W, program['gates'])
    return dict(program=program, prefix_xors=len(prefix['gates']), suffix_xors=len(suffix),
                pivots=pivots, seed=seed, policy=policy, keep_terminals=keep_terminals)


def cases():
    for name, compact, edge in LAYOUTS:
        prefix = clean_prefix(compact, edge)
        for keep in (False, True):
            for policy in ('sparse', 'dense', 'shuffled'):
                for seed in range(8):
                    mode = 'terminals' if keep else 'free'
                    yield f'{name}-{mode}-{policy}-{seed}', complete(prefix, seed, policy, keep)
