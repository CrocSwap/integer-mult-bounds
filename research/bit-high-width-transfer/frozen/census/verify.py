"""Replay the five-call, nullity-two census and its controls.

Apache-2.0. Prepared for Josie Elliston with Claude (Anthropic) assistance.

Default (a few minutes on CPython 3.12): register counts W = 2, 3, 4 for every
relation lattice of rank 2 and every lattice of rank at most 1, the unpruned
cross-checks at (W, k) = (2, 4) and (3, 3), the orbit-weighting check at W = 2,
controls, and exact comparison with CERTIFICATE.json.  ``--long`` adds W = 5
(about ten minutes) and the unpruned cross-check at (W, k) = (2, 5) (about
seven minutes).  ``--write`` rewrites CERTIFICATE.json from the rows it ran.
"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census as C  # noqa: E402

CERT = os.path.join(HERE, "CERTIFICATE.json")


def fail(msg):
    raise SystemExit("FAIL " + msg)


def evaluate(W, Ns, D, B):
    """Exact product of one word in F2[Z^k/L]; return (diagonal?, high register count)."""
    k = len(Ns)
    I = tuple(1 << a for a in range(W))
    prods = [(0, I)]
    for j, N in enumerate(Ns):
        m0 = tuple(r ^ i for r, i in zip(N, I))
        prods = [q for S, X in prods for q in ((S, C.mul(X, m0)), (S | 1 << j, C.mul(X, N)))]
    reps, cid = [], []
    for S in range(1 << k):
        v = tuple((S >> j) & 1 for j in range(k))
        f = next((c for c, T in enumerate(reps) if tuple(x - y for x, y in zip(v, T)) in D), None)
        if f is None:
            f = len(reps)
            reps.append(v)
        cid.append(f)
    acc = [[0] * W for _ in reps]
    for S, X in prods:
        for a in range(W):
            acc[cid[S]][a] ^= X[a]
    dcls = [None] * W
    for c, X in enumerate(acc):
        for a in range(W):
            if X[a] & ~(1 << a):
                return False, None
            if X[a]:
                if dcls[a] is not None:
                    return False, None
                dcls[a] = c

    def inspan(v):
        if not B:
            return not any(v)
        return C.rank_q(list(B) + [list(v)]) == len(B)

    if None in dcls:
        return False, None
    high = 0
    for c in set(dcls):
        T = reps[c]
        lw = (not any(T)) or inspan(T)
        for j in range(k):
            for sg in (1, -1):
                if not lw:
                    u = list(T)
                    u[j] -= sg
                    lw = (not any(u)) or inspan(u)
        if not lw:
            high += dcls.count(c)
    return True, high


def E(W, a):
    return tuple((1 << a) if i == a else 0 for i in range(W))


def controls():
    n = 0
    # 1. detector can fire: six coordinate calls, two per data register, no relation (k = 6).
    W = 4
    word = (E(W, 0), E(W, 0), E(W, 1), E(W, 1), E(W, 2), E(W, 2))
    ok, high = evaluate(W, word, frozenset(), ())
    if not (ok and high == 3):
        fail("control 1: six coordinate calls should give three high registers")
    n += 1
    # 2. under the relation A_1 + A_2 = 0 (a cancelling pair) register 0 ends at 0: low.
    r = (1, 1, 0, 0, 0, 0)
    ok, high = evaluate(W, word, frozenset({r, tuple(-x for x in r)}), (r,))
    if not (ok and high == 2):
        fail("control 2: cancelling pair should make register 0 low")
    n += 1
    # 3. a non-coordinate projector under no relation is not diagonal.
    N = (0b011, 0, 0)  # x = e0, y = e0 + e1 on three registers
    ok, _ = evaluate(3, (N,) + (E(3, 0),) * 4, frozenset(), ())
    if ok:
        fail("control 3: non-coordinate projector without relation accepted")
    n += 1
    # 4. the same projector twice under the cancelling relation is diagonal (D_N(B) D_N(-B) = I).
    r = (1, 1, 0, 0, 0)
    ok, _ = evaluate(3, (N, N, E(3, 0), E(3, 1), E(3, 2)), frozenset({r, tuple(-x for x in r)}), (r,))
    if not ok:
        fail("control 4: cancelling pair rejected")
    n += 1
    # 5. lattice enumeration at k = 5: every listed basis is saturated (2x2 minors coprime) and
    #    spans its D; 4,250 rank-2 planes, of which 190 contain a unit vector (a zero frame).
    lats = C.lattices(5)
    for D, B in lats:
        if C.minors_gcd(*B) != 1 or not all(C.in_span(B, v) for v in D):
            fail("control 5: unsaturated or wrong basis")
    unit = sum(1 for D, B in lats if any(sum(1 for x in v if x) == 1 for v in D))
    if (len(lats), unit) != (4250, 190):
        fail(f"control 5: lattice counts {len(lats)}, {unit}")
    n += 1
    return n


def main():
    long_ = "--long" in sys.argv
    write = "--write" in sys.argv
    rows = {}
    for W in (2, 3, 4) + ((5,) if long_ else ()):
        for mode, low in (("rank2", False), ("rank_le_1", True)):
            st, cands = C.run(W, 5, log=None, lowrank=low)
            if cands or st["candidates"]:
                fail(f"candidate word at W={W} {mode}: {cands[:1]}")
            if max(st["high_hist"]) >= 3:
                fail("high histogram reaches 3")
            rows[f"W{W}_{mode}"] = st
            print(f"row W={W} {mode}: diagonal={st['diagonal_words_weighted']} hist={st['high_hist']}", flush=True)
    # orbit weighting equals the unreduced enumeration at W = 2
    a, _ = C.run(2, 5, log=None, sym=False)
    b = rows["W2_rank2"]
    for key in ("weighted_words", "diagonal_words_weighted", "high_hist"):
        if a[key] != b[key]:
            fail(f"orbit weighting mismatch on {key}")
    # unpruned cross-checks: same diagonal counts, no derivative violation
    for W, k in ((2, 4), (3, 3)) + (((2, 5),) if long_ else ()):
        u = C.run_unpruned(W, k)
        p, _ = C.run(W, k, log=None, sym=False)
        if u["derivative_violations"] or u["diagonal"] != p["diagonal_words_weighted"] or u["hist"] != p["high_hist"]:
            fail(f"unpruned cross-check W={W} k={k}: {u} vs {p}")
        rows[f"unpruned_W{W}_k{k}"] = u
        print(f"unpruned W={W} k={k}: diagonal={u['diagonal']} violations=0", flush=True)
    nctl = controls()
    norm = json.loads(json.dumps(rows))
    if write:
        old = {}
        if os.path.exists(CERT):
            with open(CERT) as fh:
                old = json.load(fh).get("rows", {})
        old.update(norm)
        with open(CERT, "w") as fh:
            json.dump({"schema_version": 1, "rows": dict(sorted(old.items()))}, fh, indent=1, sort_keys=True)
            fh.write("\n")
    with open(CERT) as fh:
        cert = json.load(fh)["rows"]
    for key, val in norm.items():
        if cert.get(key) != val:
            fail(f"certificate mismatch on {key}")
    missing = sorted(set(cert) - set(norm))
    total = sum(r["diagonal_words_weighted"] for k_, r in norm.items() if not k_.startswith("unpruned"))
    print(f"PASS_FIVE_CALL_TWO_RELATION_CENSUS rows={len(norm)} diagonal_words={total} "
          f"max_high_registers=2 candidates=0 controls={nctl} not_replayed={len(missing)} no_new_kappa")


if __name__ == "__main__":
    main()
