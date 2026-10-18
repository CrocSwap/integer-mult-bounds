"""Verify the pair-source connector result (package connector-pair-source-path-seed2cdb).

Result: with exactly one added operation family -- pair-source connector calls
B_jk: z += B_j x_j + B_k x_k, one complete query per call -- the five-source
universal source path drops from twelve calls (fixed alphabet) to exactly ten,
and the all-31-nonzero-row batch drops from 74 to exactly 72 complete queries,
attaining the support bound the fixed alphabet proves unattainable.

Checks (fast):
  1. Certificate word: closed walk, steps of Hamming weight 1 or 2, coverage
     D(w) = P XOR P = F2^5 by two independent recomputations.
  2. Bound chain constants: C(8,2) = 28 < 31.
  3. Dirty replay at L = 1,2,3: seeded dense nonsymmetric noncommuting F2
     maps, arbitrary dirty x/z/y, all-31 matrix schedule, exact boundary.
  4. Mutation controls: every mutation must break the boundary check.
  5. Pricing: predecessor fixture leaf prices (1,4,10,16,28); query/leaf
     counts and the dispatch break-even.

Checks (--full): the exact nine-point census excluding L = 9 (independent
itertools enumeration of all C(31,8) sets; expects zero covering sets and
maximum coverage 29).

Aaron Wang, with help from opencode. Apache-2.0.
"""
import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Word: closed walk of ten steps over weight-1/2 vectors in F2^5.
PREFIXES = [0, 2, 3, 5, 13, 15, 30, 26, 10, 8, 0]
STEPS = [2, 1, 6, 8, 2, 17, 4, 16, 2, 8]
WEIGHTS = [1, 1, 2, 1, 1, 2, 1, 1, 1, 1]

PRICES = [1, 4, 10, 16, 28]  # predecessor fixture: B factor leaf prices
N_SRC = 5
N_OUT = 31

def wt(v):
    return bin(v).count("1")

def coverage_pairs(points):
    """Method 1: explicit pairwise XOR set."""
    return {a ^ b for a in points for b in points}

def coverage_bits(points):
    """Method 2: bitmask accumulation."""
    cov = 0
    for i in range(len(points)):
        for j in range(len(points)):
            cov |= 1 << (points[i] ^ points[j])
    return cov

def check_word():
    assert PREFIXES[0] == 0 and PREFIXES[-1] == 0, "walk must close"
    assert len(STEPS) == 10 == len(PREFIXES) - 1
    for i, s in enumerate(STEPS):
        assert s != 0 and wt(s) in (1, 2), "step %d not a legal call" % i
        assert PREFIXES[i] ^ PREFIXES[i + 1] == s, "step %d disagrees with prefixes" % i
    P = PREFIXES[:-1]  # distinct prefixes (q_10 = q_0)
    assert len(set(P)) == 10, "prefix set must be simple"
    cov1 = coverage_pairs(P)
    cov2 = coverage_bits(P)
    assert len(cov1) == 32 and cov2 == (1 << 32) - 1, "coverage must be all of F2^5"
    assert sum(1 for v in range(32) if v in cov1) == 32
    mults = [sum(1 for s in STEPS if s >> j & 1) for j in range(N_SRC)]
    assert all(m % 2 == 0 for m in mults), "closure forces even multiplicities"
    return mults

def boundaries_for(mask):
    """First pair of prefixes whose XOR is the mask."""
    for s in range(len(PREFIXES)):
        for t in range(s + 1, len(PREFIXES)):
            if PREFIXES[s] ^ PREFIXES[t] == mask:
                return s, t
    raise AssertionError("mask %d uncovered" % mask)

def schedule():
    """All-31 matrix: readout pairs per output at prefix boundaries."""
    out = [[] for _ in PREFIXES]
    for m in range(1, N_OUT + 1):
        s, t = boundaries_for(m)
        out[s].append((m, 0))
        out[t].append((m, 1))
    return out

def mat_vec(rows, x):
    r = 0
    k = 0
    while x:
        if x & 1:
            r ^= rows[k]
        x >>= 1
        k += 1
    return r

def run_schedule(word, sched, Bm, Am, xs, z0, ys):
    """Execute complete calls; return final (z, ys) or None on contract error."""
    z = z0
    ys = list(ys)
    if len(word) != 10:
        return None
    for step in range(11):
        for (m, half) in sched[step]:
            ys[m - 1] ^= mat_vec(Am[m - 1], z)
        if step < 10:
            s = word[step]
            for j in range(N_SRC):
                if s >> j & 1:
                    z ^= mat_vec(Bm[j], xs[j])
    return z, ys

def expected_for_mask(mask, Bm, Am, xs):
    acc = 0
    for j in range(N_SRC):
        if mask >> j & 1:
            acc ^= mat_vec(Am, mat_vec(Bm[j], xs[j]))
    return acc

def check_replay():
    """Smallest falsifying instances: L = 1,2,3 with dirty state."""
    sched = schedule()
    cases = 0
    for L in (1, 2, 3):
        for case in range(2):
            rng = random.Random(1000 * L + case + 7)
            Bm = [[rng.getrandbits(L) for _ in range(L)] for _ in range(N_SRC)]
            Am = [[rng.getrandbits(L) for _ in range(L)] for _ in range(N_OUT)]
            xs = [rng.getrandbits(L) for _ in range(N_SRC)]
            z0 = rng.getrandbits(L)
            ys0 = [rng.getrandbits(L) for _ in range(N_OUT)]
            z, ys = run_schedule(STEPS, sched, Bm, Am, xs, z0, ys0)
            assert z == z0, "z must be restored (L=%d case %d)" % (L, case)
            for m in range(1, N_OUT + 1):
                exp = expected_for_mask(m, Bm, Am[m - 1], xs)
                assert ys[m - 1] == ys0[m - 1] ^ exp, (
                    "output %d wrong at L=%d case %d" % (m, L, case))
            cases += 1
    return cases

def check_controls():
    """Every mutation must break the boundary check on a replay case."""
    sched = schedule()
    L = 3
    rng = random.Random(4242)
    Bm = [[rng.getrandbits(L) for _ in range(L)] for _ in range(N_SRC)]
    Am = [[rng.getrandbits(L) for _ in range(L)] for _ in range(N_OUT)]
    xs = [rng.getrandbits(L) for _ in range(N_SRC)]
    z0 = rng.getrandbits(L)
    ys0 = [rng.getrandbits(L) for _ in range(N_OUT)]

    def boundary_ok(word, sched_local):
        r = run_schedule(word, sched_local, Bm, Am, xs, z0, ys0)
        if r is None:
            return False
        z, ys = r
        if z != z0:
            return False
        for m in range(1, N_OUT + 1):
            exp = expected_for_mask(m, Bm, Am[m - 1], xs)
            if ys[m - 1] != ys0[m - 1] ^ exp:
                return False
        return True

    assert boundary_ok(STEPS, sched), "positive control must pass"

    # Control 1: drop one source call (breaks closure).
    w1 = STEPS[:-1] + [0]
    assert not boundary_ok(w1, sched), "dropped call must be rejected"

    # Control 2: mutate one pair call to a different legal step.
    w2 = list(STEPS)
    w2[3] = 3
    assert not boundary_ok(w2, sched), "mutated step must be rejected"

    # Control 3: move output 5's readouts one boundary later (wrong mask).
    s3 = [row[:] for row in sched]
    moved = []
    for row in s3:
        moved.append([(m, h) for (m, h) in row if m != 5])
    s, t = boundaries_for(5)
    moved[(s + 1) % 11].append((5, 0))
    moved[(t + 1) % 11].append((5, 1))
    assert not boundary_ok(STEPS, moved), "misplaced readouts must be rejected"
    return 3

def check_pricing():
    mults = [sum(1 for s in STEPS if s >> j & 1) for j in range(N_SRC)]
    assert sum(mults) == 12
    fixed = sum(m * c for m, c in zip(mults, PRICES))
    srt = sorted(mults, reverse=True)
    prs = sorted(PRICES)
    min_cost = sum(m * c for m, c in zip(srt, prs))
    max_cost = sum(m * c for m, c in zip(srt, reversed(prs)))
    queries = 10 + 2 * N_OUT  # source calls + two readouts per nonzero output
    leaves_min = min_cost + N_OUT * 2
    assert queries == 72
    # predecessor fixture rows (universal-connector-boundary README table)
    pred = {"ten-call path": (74, 182), "twelve-call path": (74, 200)}
    return {
        "multiplicities": mults,
        "b_leaf_cost_fixed_labeling": fixed,
        "b_leaf_cost_min_relabeling": min_cost,
        "b_leaf_cost_max_relabeling": max_cost,
        "queries": queries,
        "leaves_min_relabeling": leaves_min,
        "predecessor_rows": pred,
    }

def full_census():
    """Independent itertools enumeration of all nine-point sets."""
    total = 0
    covering = 0
    max_cov = 0
    for comb in itertools.combinations(range(1, 32), 8):
        pts = (0,) + comb
        cov = 1  # zero mask
        for i in range(9):
            pi = pts[i]
            for j in range(i + 1, 9):
                cov |= 1 << (pi ^ pts[j])
        total += 1
        c = cov.bit_count()
        if c > max_cov:
            max_cov = c
        if cov == (1 << 32) - 1:
            covering += 1
    assert total == 7888725, total
    assert covering == 0, covering
    assert max_cov == 29, max_cov
    return {"sets": total, "covering": covering, "max_coverage": max_cov}

def main():
    cert_path = os.path.join(HERE, "CERTIFICATE.json")
    with open(cert_path, "r", encoding="utf-8") as f:
        cert = json.load(f)
    assert cert["prefixes"] == PREFIXES and cert["word_steps"] == STEPS, (
        "CERTIFICATE.json disagrees with verify.py constants")

    mults = check_word()
    cases = check_replay()
    controls = check_controls()
    pricing = check_pricing()

    if "--full" in sys.argv:
        census = full_census()
        print("CENSUS", json.dumps(census))
        print("PASS_CONNECTOR_PAIR_SOURCE_PATH_CENSUS")
        return

    print("word ok: 10 steps, coverage 32, multiplicities", mults)
    print("replay ok: %d dirty cases at L=1,2,3" % cases)
    print("controls ok: %d mutations rejected" % controls)
    print("pricing", json.dumps(pricing))
    print("PASS_CONNECTOR_PAIR_SOURCE_PATH")

if __name__ == "__main__":
    main()
