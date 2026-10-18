"""Exact small model of SUPPLIER-SUPPORT-AUDIT sec. 2-3/6 (PR1673 as vendored in PR2044):
support-local exposure + deferred reservation phases + whole-row padding/role split, for one
simultaneous H call on g selected bits taken one per axis from a d-axis binary tensor.

The supplier itself is modelled by its *contract* (completed invocation = H on active selected
bits, identity on reserved/spectator/row coordinates), but internally it is adversarial: inside each
role stream it applies an arbitrary role-dependent bijection to the dirty front/back control
chunks (which hold UNPROCESSED deferred selected bits) and undoes it.  We check:
  1. end result == H^{(x)g} applied directly in the native layout (exact integers);
  2. every exposure permutation has moved support <= 2hK;
  3. padded zero rows are zero at completion (so deletion is exact);
  4. mutation controls fail: skip deferred phase; supplier also hits row label; no restore of
     exposure before the next phase; preliminary C on reserved chunks (old exposition) applied twice.
Usage: python3 sim_deferred.py OUT.json
"""
import json, sys, itertools, random
import numpy as np

def bitperm(a, n, perm):
    """new address bit perm[i] = old address bit i."""
    t = a.reshape([2] * n)               # numpy axis k <-> address bit n-1-k
    # new array axis for bit perm[i] must come from old axis for bit i
    src_axes = [None] * n
    for i in range(n):
        src_axes[n - 1 - perm[i]] = n - 1 - i
    return np.ascontiguousarray(t.transpose(src_axes)).reshape(-1)

def hbit(a, j):
    v = a.reshape(-1, 2, 1 << j)
    x0, x1 = v[:, 0, :].copy(), v[:, 1, :].copy()
    out = np.empty_like(v); out[:, 0, :] = x0 + x1; out[:, 1, :] = x0 - x1
    return out.reshape(-1)

def support(perm):
    return sum(1 for i, p in enumerate(perm) if i != p)

def run(seed, d, ell, K, k, g_axes, Q, mutate=None):
    rng = random.Random(seed)
    n = d * ell
    data = np.array([rng.randrange(-50, 51) for _ in range(1 << n)], dtype=np.int64)
    # axis a occupies address bits [a*ell, (a+1)*ell); axis 0 holds the untouched suffix
    sel = {a: a * ell + k for a in g_axes}                  # selected bit per axis
    nbhd = {a: [a * ell + k + i for i in range(K)] for a in g_axes}
    assert all(k + K <= ell for _ in g_axes)
    suffix = list(range(0, ell))                             # reserved untouched suffix (record grouping)
    assert 0 not in g_axes
    # reference
    ref = data.copy()
    for a in g_axes: ref = hbit(ref, sel[a])
    cur = data.copy()
    pending = list(g_axes)
    log = []
    phase = 0
    while pending:
        h = len(pending)
        if h <= 3:                                         # tail: process individually (O(V) each)
            for a in pending: cur = hbit(cur, sel[a])
            log.append({'phase': phase, 'h': h, 'mode': 'individual'}); pending = []
            break
        # reservation: 1 row chunk, 1 front chunk (two toy H-fields), 1 back chunk
        rng.shuffle(pending)
        fc = max(1, -(-h // 4))                             # front chunks grow with h (toy 2hG/K)
        row, fronts, back = pending[0], pending[1:1 + fc], pending[1 + fc]
        active = pending[2 + fc:]
        assert active
        order = [back] + active + fronts + [row]
        front = fronts[0]
        # exposure: S -> T (top hK bits), T\S -> S\T, identity elsewhere
        T = list(range(n - h * K, n))
        S = [b for a in order for b in nbhd[a]]
        assert len(set(S)) == len(S) and not set(S) & set(suffix)
        perm = list(range(n))
        for s, t in zip(S, T): perm[s] = t
        rest_dom = [t for t in T if t not in S]; rest_img = [s for s in S if s not in T]
        for x, y in zip(rest_dom, rest_img): perm[x] = y
        assert sorted(perm) == list(range(n))
        sup = support(perm)
        assert sup <= 2 * h * K, (sup, h, K)
        assert all(perm[b] == b for b in suffix)
        x = bitperm(cur, n, perm)
        pos = {a: n - h * K + K * i for i, a in enumerate(order)}   # selected offset rho=0 in chunk
        # rows: top K bits = row chunk; pad row count 2^K up to multiple of Q
        R = 1 << K; Rp = -(-R // Q) * Q
        body = 1 << (n - K)
        M = np.zeros((Rp, body), dtype=np.int64); M[:R] = x.reshape(R, body)
        roles = [M[w::Q].copy() for w in range(Q)]                # u = Q*g' + w -> role w
        fb_bits = [pos[f] + i for f in fronts for i in range(K)] + [pos[back] + i for i in range(K)]
        for w in range(Q):
            st = roles[w].reshape(-1)
            nb = n - K
            # adversarial dirty use: role-dependent bijection on front/back chunk values
            vals = 1 << len(fb_bits)
            sig = list(range(vals)); random.Random(seed * 1000 + w + phase).shuffle(sig)
            idx = np.arange(st.size, dtype=np.int64)
            addr_body = idx % body
            def field(addr):
                f = 0
                for i, b in enumerate(fb_bits): f |= ((addr >> b) & 1) << i
                return f
            def setfield(addr, f):
                for i, b in enumerate(fb_bits):
                    addr = (addr & ~(1 << b)) | (((f >> i) & 1) << b)
                return addr
            F = field(addr_body)
            sigarr = np.array(sig, dtype=np.int64)
            newaddr = (idx - addr_body) + setfield(addr_body, sigarr[F])
            scr = np.empty_like(st); scr[newaddr] = st
            # active H on selected bits (contract); mutation: also touch row label
            for a in active: scr = hbit(scr, pos[a])
            if mutate == 'row_label_touched' and phase == 0:
                scr = hbit(scr.reshape(-1), (scr.size // body - 1).bit_length() + n - K - 1) if False else scr
                scr = scr.reshape(-1, body); scr[[0, 1]] = scr[[1, 0]]; scr = scr.reshape(-1)  # swap two rows of role stream
            # undo dirty bijection
            back_st = scr[newaddr]
            roles[w] = back_st.reshape(-1, body)
        M2 = np.zeros_like(M)
        for w in range(Q): M2[w::Q] = roles[w]
        pad_zero = bool(np.all(M2[R:] == 0))
        x = M2[:R].reshape(-1)
        if mutate == 'preliminary_on_reserved' and phase == 0:
            for a in [row, back] + fronts: x = hbit(x, pos[a])
        inv = [0] * n
        for i, p in enumerate(perm): inv[p] = i
        if mutate == 'no_restore' and phase == 0:
            cur = x                                         # forget inverse exposure
        else:
            cur = bitperm(x, n, inv)
        log.append({'phase': phase, 'h': h, 'active': len(active), 'deferred': h - len(active), 'exposure_support': sup,
                    'bound_2hK': 2 * h * K, 'rows': R, 'padded_rows': Rp, 'padding_zero_at_completion': pad_zero})
        pending = [a for a in pending if a not in active]
        if mutate == 'drop_deferred': pending = []
        phase += 1
    return bool(np.array_equal(cur, ref)), log, all(e.get('padding_zero_at_completion', True) for e in log)

def main():
    out = {'positive': [], 'controls': {}}
    configs = [dict(d=9, ell=2, K=2, k=0, g_axes=list(range(1, 9)), Q=3),
               dict(d=7, ell=3, K=2, k=1, g_axes=list(range(1, 7)), Q=3),
               dict(d=5, ell=4, K=3, k=1, g_axes=[1, 2, 3, 4], Q=5),
               dict(d=10, ell=2, K=1, k=1, g_axes=list(range(1, 10)), Q=3)]
    for ci, c in enumerate(configs):
        for seed in range(3):
            ok, log, padok = run(seed + 10 * ci, **c)
            assert ok and padok, (c, seed, log)
            out['positive'].append({'config': c, 'seed': seed, 'exact_equal': ok, 'phases': log})
    for m in ['drop_deferred', 'no_restore', 'preliminary_on_reserved', 'row_label_touched']:
        ok, log, padok = run(1, **configs[0], mutate=m)
        out['controls'][m] = {'exact_equal': ok, 'padding_zero': padok}
        assert not (ok and padok), m
    json.dump(out, open(sys.argv[1], 'w'), indent=1)
    print('positive cases', len(out['positive']), 'all exact; controls', {k: v for k, v in out['controls'].items()})

main()
