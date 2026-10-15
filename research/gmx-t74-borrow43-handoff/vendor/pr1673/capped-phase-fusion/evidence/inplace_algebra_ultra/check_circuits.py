"""Numerical replay of n-wire, invertible 1x1/2x2 gate circuits.

The production theorem is algebraic. This independent small-size replay
checks the parity Toeplitz factor, low-displacement LU recursion, the
Stein sum-LU identity, and the actual no-ancilla FFT/shear gate schedule.
"""
import json
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).parent
STATS = {"triangle_nodes": 0, "full_nodes": 0, "generator_shears": 0,
         "max_displacement_rank": 0, "min_gate_determinant": 1.0,
         "max_generator_entry": 0.0, "max_triangle_coefficient": 0.0}


def toep(c, row=None):
    c = np.asarray(c, dtype=complex)
    row = c.copy() * 0 if row is None else np.asarray(row, dtype=complex)
    row[0] = c[0]
    n = len(c)
    return np.array([[c[i-j] if i >= j else row[j-i]
                      for j in range(n)] for i in range(n)])


def lower(c):
    return toep(c)


def invseries(f):
    n = len(f)
    ans = np.zeros(n, complex)
    ans[0] = 1 / f[0]
    for j in range(1, n):
        ans[j] = -sum(f[k] * ans[j-k] for k in range(1, j+1)) / f[0]
    return ans


def conv(a, b, n):
    return np.convolve(a, b)[:n]


def diag(indices, values):
    return [[((int(i),), np.array([[v]], complex)) for i, v in zip(indices, values)]]


def inverse(plan):
    return [[(ids, np.linalg.inv(g)) for ids, g in layer]
            for layer in reversed(plan)]


def parallel(a, b):
    return [(a[j] if j < len(a) else []) + (b[j] if j < len(b) else [])
            for j in range(max(len(a), len(b)))]


def fft(indices):
    n = len(indices)
    if n <= 1:
        return []
    assert n & (n - 1) == 0
    bits = n.bit_length() - 1
    rev = [int(f"{j:0{bits}b}"[::-1], 2) for j in range(n)]
    plan = [[((indices[i], indices[j]), np.array([[0, 1], [1, 0]], complex))
             for i, j in enumerate(rev) if i < j]]
    size = 2
    while size <= n:
        layer = []
        for start in range(0, n, size):
            for j in range(size // 2):
                w = np.exp(-2j * np.pi * j / size)
                layer.append(((indices[start+j], indices[start+j+size//2]),
                              np.array([[1, w], [1, -w]], complex) / math.sqrt(2)))
        plan.append(layer)
        size *= 2
    return plan


def circ_shear(target, source, kernel):
    """target += circulant(kernel) source, using these wires only."""
    p = parallel(fft(target), fft(source))
    lams = np.fft.fft(kernel)
    mid = [[((source[j], target[j]), np.array([[1, 0], [lams[j], 1]], complex))
            for j in range(len(source))]]
    return p + mid + inverse(p)


def toeplitz_shear(target, source, T):
    """Cyclic + negacyclic decomposition; source and target are disjoint."""
    n = len(source)
    assert T.shape == (n, n) and len(target) == n
    c, r = T[:, 0], T[0, :]
    g = np.zeros(n, complex)
    h = np.zeros(n, complex)
    g[0] = h[0] = c[0] / 2
    for j in range(1, n):
        g[j] = (c[j] + r[n-j]) / 2
        h[j] = (c[j] - r[n-j]) / 2
    gamma = np.exp(1j * np.pi / n)
    d = gamma ** np.arange(n)
    twists = parallel(diag(target, d), diag(source, d))
    return (circ_shear(target, source, g) + twists
            + circ_shear(target, source, d * h) + inverse(twists))


def triangle_plan(indices, f):
    n = len(indices)
    STATS["triangle_nodes"] += 1
    STATS["max_triangle_coefficient"] = max(
        STATS["max_triangle_coefficient"], float(np.max(np.abs(f))))
    if n == 1:
        return diag(indices, f)
    assert n % 2 == 0
    m = n // 2
    ev, od = indices[::2], indices[1::2]
    e, o = np.asarray(f[::2]), np.asarray(f[1::2])
    k = conv(o, invseries(e), m)
    zk = np.r_[0, k[:-1]]
    s = e - np.r_[0, conv(o, k, m)[:-1]]
    right = toeplitz_shear(ev, od, lower(zk))
    middle = parallel(triangle_plan(ev, e), triangle_plan(od, s))
    left = toeplitz_shear(od, ev, lower(k))
    return right + middle + left


def lowdisp_shear(target, source, T):
    n = len(source)
    Z = np.eye(n, k=-1)
    Delta = T - Z @ T @ Z.T
    U, vals, Vh = np.linalg.svd(Delta)
    cutoff = 1e-11 * max(1.0, vals[0])
    rank = int(np.sum(vals > cutoff))
    STATS["max_displacement_rank"] = max(STATS["max_displacement_rank"], rank)
    STATS["generator_shears"] += 1
    result = []
    reconstructed = np.zeros_like(T)
    for j in range(rank):
        g = U[:, j]
        h = vals[j] * Vh[j, :]
        STATS["max_generator_entry"] = max(
            STATS["max_generator_entry"], float(np.max(np.abs(g))),
            float(np.max(np.abs(h))))
        reconstructed += lower(g) @ lower(h).T
        gamma = max(1.0, 2 * float(np.sum(np.abs(h))))
        p = h / gamma
        p[0] += 1
        # U(h)=J L(h) J. This is a genuinely invertible source transform.
        transform = triangle_plan(source[::-1], p)
        result += transform
        result += toeplitz_shear(target, source, gamma * lower(g))
        result += inverse(transform)
        result += toeplitz_shear(target, source, -gamma * lower(g))
    assert np.max(np.abs(T - reconstructed)) < 1e-9
    return result


def full_plan(indices, M):
    n = len(indices)
    STATS["full_nodes"] += 1
    if n == 1:
        return diag(indices, [M[0, 0]])
    m = n // 2
    A, B, C, D = M[:m, :m], M[:m, m:], M[m:, :m], M[m:, m:]
    K = np.linalg.solve(A, B)
    L = np.linalg.solve(A.T, C.T).T
    S = D - C @ K
    right = lowdisp_shear(indices[:m], indices[m:], K)
    mid = parallel(full_plan(indices[:m], A), full_plan(indices[m:], S))
    left = lowdisp_shear(indices[m:], indices[:m], L)
    return right + mid + left


def replay(plan, n, track=True):
    out = np.eye(n, dtype=complex)
    peak = 1.0
    min_det = 1.0
    for layer in plan:
        used = set()
        for ids, g in layer:
            assert not used.intersection(ids), "non-disjoint layer"
            used.update(ids)
            min_det = min(min_det, float(abs(np.linalg.det(g))))
            out[list(ids), :] = g @ out[list(ids), :]
        if track:
            peak = max(peak, float(np.linalg.norm(out, 2)))
    STATS["min_gate_determinant"] = min(STATS["min_gate_determinant"], min_det)
    return out, peak


def main():
    rng = np.random.default_rng(20261013)
    rows = []
    for n in [2, 4, 8, 16]:
        f = rng.normal(size=n) / (12 * n)
        f[0] += 1
        p = triangle_plan(list(range(n)), f)
        actual, peak = replay(p, n)
        rows.append({"kind": "triangular", "n": n, "rounds": len(p),
                     "gates": sum(map(len, p)),
                     "max_error": float(np.max(np.abs(actual-lower(f)))),
                     "peak_prefix_norm_2": peak})

        c = rng.normal(size=n) / (20 * n)
        r = rng.normal(size=n) / (20 * n)
        c[0] += 1
        H = toep(c, r)
        p = full_plan(list(range(n)), H)
        actual, peak = replay(p, n, track=n <= 8)
        rows.append({"kind": "full_toeplitz", "n": n, "rounds": len(p),
                     "gates": sum(map(len, p)),
                     "max_error": float(np.max(np.abs(actual-H))),
                     "peak_prefix_norm_2": peak if n <= 8 else None,
                     "input_distance_from_I_2": float(np.linalg.norm(H-np.eye(n), 2))})
    # Destructive control: dropping the second subtraction computes the wrong map.
    # Independent direct parity block algebra across a range of sizes.
    identities = []
    for n in [2, 4, 8, 16, 32]:
        f = rng.normal(size=n) / n
        f[0] += 2
        m = n // 2
        e, o = f[::2], f[1::2]
        k = conv(o, invseries(e), m)
        s = e - np.r_[0, conv(o, k, m)[:-1]]
        E, O, K = lower(e), lower(o), lower(k)
        Z = np.eye(m, k=-1)
        left = np.block([[np.eye(m), np.zeros((m,m))], [K, np.eye(m)]])
        diagblock = np.block([[E, np.zeros((m,m))], [np.zeros((m,m)), lower(s)]])
        right = np.block([[np.eye(m), Z@K], [np.zeros((m,m)), np.eye(m)]])
        order = list(range(0,n,2)) + list(range(1,n,2))
        exact = lower(f)[np.ix_(order,order)]
        identities.append({"n": n, "error": float(np.max(np.abs(left@diagblock@right-exact)))})
    sylvester = []
    for b in [1, 2, 4, 8]:
        f = np.array([1.0])
        g = np.array([1.0])
        for j in range(b):
            f = np.convolve(f, [1.0, 256.0 ** (j-b+0.5)])
            g = np.convolve(g, [1.0, 256.0 ** (-j-0.5)])
        fp = np.r_[f, np.zeros(3*b+2-len(f))]
        fi = invseries(fp)
        def hc(k):
            return sum(g[v]*fi[k+v] for v in range(b+1) if 0 <= k+v < len(fi))
        K = np.array([[hc(i-b-j) for j in range(b)] for i in range(b)])
        H = np.array([[hc(i-j) for j in range(b)] for i in range(b)])
        S = np.zeros((2*b, 2*b), complex)
        for j in range(b):
            for k in range(b+1):
                if j+k < 2*b:
                    S[j+k, j] += f[k]
                if 0 <= b+j-k < 2*b:
                    S[b+j-k, b+j] += g[k]
        inds = list(range(2*b))
        p = toeplitz_shear(inds[:b], inds[b:], K)
        p += full_plan(inds[b:], H)
        p += triangle_plan(inds, np.r_[f, np.zeros(2*b-len(f))])
        actual, peak = replay(p, 2*b, track=b <= 4)
        sylvester.append({"b": b, "total_wires": 2*b, "rounds": len(p),
                          "gates": sum(map(len, p)),
                          "max_error": float(np.max(np.abs(actual-S))),
                          "H_minus_I_norm_1": float(np.linalg.norm(H-np.eye(b), 1)),
                          "H_minus_I_norm_infinity": float(np.linalg.norm(H-np.eye(b), np.inf)),
                          "peak_prefix_norm_2": peak if b <= 4 else None})
    # Removing the compensating dirty subtraction must fail.
    b = 4
    gi, hi = np.array([1, .02, .01, .005]), np.array([.1, .04, .02, .01])
    pi = hi.copy()
    pi[0] += 1
    target = np.block([[np.eye(b), np.zeros((b,b))], [lower(gi)@lower(hi).T, np.eye(b)]])
    pp = triangle_plan(list(range(b))[::-1], pi)
    correct = pp + toeplitz_shear(list(range(b, 2*b)), list(range(b)), lower(gi)) + inverse(pp)
    broken_actual, _ = replay(correct, 2*b, track=False)
    correct += toeplitz_shear(list(range(b, 2*b)), list(range(b)), -lower(gi))
    correct_actual, _ = replay(correct, 2*b, track=False)
    omission = {"correct_error": float(np.max(np.abs(correct_actual-target))),
                "omit_second_subtraction_error": float(np.max(np.abs(broken_actual-target)))}
    result = {"seed": 20261013, "note": "Floating replay supports, does not replace, algebraic proof.",
              "controls": rows, "polyphase_identity": identities,
              "normalized_sylvester": sylvester, "omission_control": omission, "stats": STATS}
    (ROOT / "CIRCUIT-REPLAY.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
