#!/usr/bin/env python3
"""The literal scalar word and its transparency replay.

The zeta DAG is a pure-addition circuit (every node = sum of two earlier
registers, coefficient +1). The word follows the retained schedule pattern:

  phase 1  pre-reads:   y[t] -= r[root_t]        (registers hold pure dirt)
  phase 2  V-gates:     r[in_i] += x_i           (the data enters)
  phase 3  compute:     r[n] += r[a]; r[n] += r[b]      (DAG order)
  phase 4  post-reads:  y[t] += r[root_t]
  phase 5  inverse:     undo compute, then undo the V-gates

Linearity makes the pre-read on pure dirt equal to the dirt flux that later
reaches each root (the root's value on dirt alone is the exact path-weighted
dirt sum), so the post-read minus that flux is exactly the family map
sum_{u: u&t=0} x_u.  Phase 5 restores every register to its initial value.
Tamper controls: skipping a pre-read, a post-read, an inverse gate, or flipping
one coefficient must all be rejected.
"""

# control vocabulary: 'skip_preread', 'skip_postread', 'skip_inverse', 'sign_flip'

def ops_of(g):
    ops = []
    for node, pair in enumerate(g['args']):
        if pair is None:
            continue
        ops.append((node, pair[0]))
        ops.append((node, pair[1]))
    reads = [(r['targets'][0], r['node']) for r in g['roots']]
    return ops, reads


def adjoint(g, root):
    """The transpose sweep: every node's path multiplicity into the root.
    Mirrors the retained adjoint construction."""
    n = len(g['args'])
    adj = [0] * n
    adj[root] = 1
    for dst, src in reversed(ops_of(g)[0]):
        adj[src] += adj[dst]
    return adj


def replay(g, ring, seed=1, tamper=None):
    import random
    rng = random.Random(seed)
    v, n = len(g['inputs']), len(g['args'])
    x = [ring(rng.randrange(1, 10**9)) for _ in range(v)]
    dirty = [ring(rng.randrange(1, 10**9)) for _ in range(n)]
    r = list(dirty)
    y = [ring(0)] * v
    ops, reads = ops_of(g)
    add = lambda a, b: ring(a + b)
    sub = lambda a, b: ring(a - b)
    # 1. adjoint pre-reads on the raw dirt: y[t] -= sum_n adj_t[n] * r[n]
    for t, root in reads:
        adj = adjoint(g, root)
        for node in range(n):
            if not adj[node]:
                continue
            if tamper == 'skip_preread' and (t, node) == (0, root):
                continue
            y[t] = sub(y[t], ring(adj[node] * r[node]))
    # 2. V-gates
    for i in range(v):
        r[i] = add(r[i], x[i])
    # 3. compute
    for dst, src in ops:
        r[dst] = add(r[dst], r[src])
    # 4. post-reads
    for k, (t, node) in enumerate(reads):
        if tamper == 'skip_postread' and k == 0:
            continue
        if tamper == 'sign_flip' and k == 0:
            y[t] = sub(y[t], r[node])
        else:
            y[t] = add(y[t], r[node])
    # 5. inverse
    for k, (dst, src) in enumerate(reversed(ops)):
        if tamper == 'skip_inverse' and k == 0:
            continue
        r[dst] = sub(r[dst], r[src])
    for i in reversed(range(v)):
        r[i] = sub(r[i], x[i])
    scratch_ok = r == dirty
    want = [sum(x[i] for i, u in enumerate(g['inputs']) if (u & g['inputs'][t]) == 0)
            for t in range(v)]
    map_ok = all(ring(y[t] - want[t]) == 0 for t in range(v))
    return scratch_ok, map_ok


def run_controls(g):
    P = (1 << 61) - 1
    rings = {'mod 2^61-1': lambda z: z % P, 'integers': lambda z: z}
    for name, ring in rings.items():
        for seed in (1, 7, 42):
            assert replay(g, ring, seed=seed) == (True, True), (name, 'clean', seed)
        for t in ('skip_preread', 'skip_postread', 'skip_inverse', 'sign_flip'):
            scratch_ok, map_ok = replay(g, ring, seed=3, tamper=t)
            assert not (scratch_ok and map_ok), (name, 'tamper accepted', t)
    return True


if __name__ == '__main__':
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from zeta import zeta_graph
    for h in (3, 4, 5, 6, 7, 8):
        assert run_controls(zeta_graph(h))
        print('h=%d: clean replay on three seeds + four tamper controls PASS (mod 2^61-1 and integers)' % h)
