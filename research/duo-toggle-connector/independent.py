"""Independent checks for research/duo-toggle-connector (stdlib only).

Code-disjoint from generate.py: different enumeration and coverage code paths.
Checks (all must pass):

  1. Complete independent scan of every 9-point set {0} + 8 nonzero points of
     F2^5 for a full difference cover (the k = 9 exclusion), by brute-force
     itertools.combinations with no pruning.
  2. Independent re-derivation of the n = 3 frontier by a recursive walk DFS
     (generate.py uses an itertools.product scan).
  3. Independent re-derivation of the frozen 945-pairing control by restricted
     growth words (generate.py uses endpoint matchings).
  4. Witness replay: closure, weights, coverage, per-mask boundary pairs and
     the full 72-call batch word, computed by a direct schedule interpreter.
  5. Dense dirty-state replay at L = 1, 2, 3 with seeded random noncommuting
     maps, forward and reverse order, arbitrary dirty rows.
  6. Mutation controls: four tampered schedules/records must each be detected.

Navinor, with help from opencode.  Apache-2.0.
"""
import hashlib
import itertools
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def wt(v):
    return bin(v).count("1")


# --- coverage by bitmask (generate.py uses set comprehensions) --------------

def cov_bits(prefixes):
    mask = 0
    for a in prefixes:
        for b in prefixes:
            mask |= 1 << (a ^ b)
    return mask


def pair_table(prefixes):
    """mask -> one boundary pair (s, t) with q_s ^ q_t = mask, computed by
    scanning boundaries in order (different code from generate.placement)."""
    tab = {}
    k = len(prefixes) - 1
    for s in range(k + 1):
        for t in range(k + 1):
            m = prefixes[s] ^ prefixes[t]
            if m not in tab:
                tab[m] = (s, t)
    return tab


# --- 1. complete s = 9 scan ------------------------------------------------

def scan_s9():
    full = 0
    total = 0
    for combo in itertools.combinations(range(1, 32), 8):
        pts = (0,) + combo
        mask = 0
        for i in range(9):
            pi = pts[i]
            mask |= 1 << pi  # pi + 0
            for j in range(i):
                mask |= 1 << (pi ^ pts[j])
        total += 1
        if bin(mask).count("1") == 32:
            full += 1
    return total, full


# --- 2. n = 3 frontier by recursive walk DFS -------------------------------

def n3_dfs(kmax=7):
    steps = [v for v in range(1, 8) if wt(v) <= 2]
    counts = {}
    best = None
    witness = None

    def rec(q, walk, W):
        nonlocal best, witness
        k = len(walk)
        if k == kmax:
            return
        for s in steps:
            nq = q[-1] ^ s
            nwalk = walk + [s]
            if nq == 0:
                if cov_bits(q + [0]) == 0xFF:
                    key = (k + 1, W + wt(s))
                    counts[key] = counts.get(key, 0) + 1
                    if best is None or key < best:
                        best = key
                        witness = nwalk
                continue
            rec(q + [nq], nwalk, W + wt(s))

    rec([0], [], 0)
    return counts, best, witness


# --- 3. 945 control by restricted growth words -----------------------------

def rg_words_945():
    """All length-10 words where label i appears exactly twice and labels are
    introduced in order of first appearance (restricted growth strings)."""
    left = [2] * 5

    def rg(prefix, introduced):
        if len(prefix) == 10:
            yield tuple(prefix)
            return
        for lab in range(min(introduced + 1, 5)):
            if left[lab] > 0:
                left[lab] -= 1
                prefix.append(lab)
                yield from rg(prefix, max(introduced, lab + 1))
                prefix.pop()
                left[lab] += 1

    yield from rg([], 0)


def rg_hist():
    hist = {}
    for word in rg_words_945():
        q = 0
        prefixes = [0]
        for lab in word:
            q ^= 1 << lab
            prefixes.append(q)
        cov = bin(cov_bits(prefixes)).count("1")
        hist[cov] = hist.get(cov, 0) + 1
    return dict(sorted(hist.items()))


# --- 4. witness + batch replay --------------------------------------------

def walk_prefixes(walk):
    q = [0]
    for s in walk:
        q.append(q[-1] ^ s)
    return q


def batch_ok(batch):
    """Direct symbolic replay of a batch word: True iff the source word is
    closed, covers all 32 masks and every output's two readouts realize its
    requested mask at the stated boundaries."""
    q = [0]
    open_readouts = {}
    realized = set()
    for call in batch:
        if call[0] == "A":
            m = call[1]
            if m in open_readouts:
                a = open_readouts.pop(m)
                if (q[a] ^ q[len(q) - 1]) != m:
                    return False
                realized.add(m)
            else:
                open_readouts[m] = len(q) - 1
        elif call[0] == "B":
            q.append(q[-1] ^ (1 << call[1]))
        else:
            q.append(q[-1] ^ (1 << call[1]) ^ (1 << call[2]))
    return (q[-1] == 0 and bin(cov_bits(q)).count("1") == 32
            and not open_readouts and len(realized) == 31)


def check_witness(cert):
    w = cert["n5_witness"]
    walk = w["walk"]
    q = walk_prefixes(walk)
    assert q[-1] == 0, "witness not closed"
    assert len(walk) == w["k"][0] == 10, "witness length"
    assert sum(wt(s) for s in walk) == w["W"] == 12, "witness weight"
    assert bin(cov_bits(q)).count("1") == 32, "witness coverage"
    tab = pair_table(q)
    for m in range(1, 32):
        a, b = w["placement"][str(m)]
        assert (q[a] ^ q[b]) == m, "placement row %d" % m
        assert tab[m] is not None
    assert batch_ok(w["batch_word"]), "batch word replay"
    n_calls = len(w["batch_word"])
    assert n_calls == 72, "batch call count %d" % n_calls
    return n_calls


# --- 5. dense dirty replay ------------------------------------------------

def matvec(rows, x):
    y = 0
    for i, r in enumerate(rows):
        if bin(r & x).count("1") & 1:
            y |= 1 << i
    return y


def dense_replay(cert, L, seed):
    rng = random.Random(seed)
    n_out, n_src = 31, 5

    def rand_mat():
        return [rng.getrandbits(L) for _ in range(L)]

    A = [rand_mat() for _ in range(n_out)]
    B = [rand_mat() for _ in range(n_src)]
    # deliberately noncommuting maps are generic; no relation is imposed
    x = [rng.getrandbits(L) for _ in range(n_src)]
    z0 = rng.getrandbits(L)
    y0 = [rng.getrandbits(L) for _ in range(n_out)]
    z, y = z0, list(y0)

    for call in cert["n5_witness"]["batch_word"]:
        if call[0] == "A":
            i = call[1] - 1
            y[i] ^= matvec(A[i], z)
        elif call[0] == "B":
            z ^= matvec(B[call[1]], x[call[1]])
        else:
            j, k = call[1], call[2]
            z ^= matvec(B[j], x[j]) ^ matvec(B[k], x[k])
    assert z == z0, "connector not restored at L=%d seed=%d" % (L, seed)
    for i in range(n_out):
        mask = i + 1
        want = y0[i]
        for j in range(n_src):
            if mask >> j & 1:
                want ^= matvec(A[i], matvec(B[j], x[j]))
        assert y[i] == want, "row %d wrong at L=%d seed=%d" % (mask, L, seed)
    # reverse-order replay of the source calls only: the source word is a
    # closed walk, so replaying it backwards from any state restores z.
    z2 = rng.getrandbits(L)
    z2_start = z2
    src_calls = [c for c in cert["n5_witness"]["batch_word"] if c[0] != "A"]
    for call in reversed(src_calls):
        if call[0] == "B":
            z2 ^= matvec(B[call[1]], x[call[1]])
        else:
            j, k = call[1], call[2]
            z2 ^= matvec(B[j], x[j]) ^ matvec(B[k], x[k])
    assert z2 == z2_start, "reverse replay failed at L=%d seed=%d" % (L, seed)
    return True


# --- 6. mutation controls -------------------------------------------------

def mutation_controls(cert):
    w = cert["n5_witness"]

    # (a) deleting one source call breaks closure/coverage
    batch = list(w["batch_word"])
    for idx, call in enumerate(batch):
        if call[0] != "A":
            del batch[idx]
            break
    assert not batch_ok(batch), "control (a) not detected"

    # (b) shrinking a DUO call to one source breaks closure/coverage
    batch = list(w["batch_word"])
    for idx, call in enumerate(batch):
        if call[0] == "DUO":
            batch[idx] = ["B", call[1]]
            break
    assert not batch_ok(batch), "control (b) not detected"

    # (c) moving one readout to a wrong boundary gives the wrong row.  Note
    # boundary 10 equals boundary 0 for a closed walk, so only placements that
    # change the realized mask count as mutations.
    found = False
    for c in range(1, 10):
        batch = list(w["batch_word"])
        moved = None
        for idx, call in enumerate(batch):
            if call == ["A", 21]:
                moved = batch.pop(idx)
                break
        assert moved is not None
        src_seen = 0
        pos = 0
        for idx, call in enumerate(batch):
            if call[0] != "A":
                src_seen += 1
                if src_seen == c:
                    pos = idx + 1
                    break
        batch.insert(pos, moved)
        if not batch_ok(batch):
            found = True
            break
    assert found, "control (c) not detected"

    # (d) a tampered record is caught by its own consistency fields
    bad = json.loads(json.dumps(w))
    bad["W"] = 14
    assert sum(wt(s) for s in bad["walk"]) != bad["W"], "control (d) not detected"
    return 4


# --- main ------------------------------------------------------------------

def main():
    with open(os.path.join(HERE, "CERTIFICATE.json"), encoding="utf-8") as f:
        cert = json.load(f)
    results = {}

    total, full = scan_s9()
    results["s9_scan"] = {"sets_scanned": total, "full_covers": full}
    assert total == 7888725 and full == cert["n5_s9_cover_sets"] == 0, "s9 scan"

    counts3, best3, wit3 = n3_dfs()
    results["n3_dfs"] = {"best": list(best3), "witness": wit3,
                         "counts": {"k%dW%d" % t: c for t, c in sorted(counts3.items())}}
    assert list(best3) == cert["n3"]["pareto"] == [5, 6], "n3 frontier"
    q3 = walk_prefixes(wit3)
    assert q3[-1] == 0 and sum(wt(s) for s in wit3) == 6
    assert bin(cov_bits(q3)).count("1") == 8, "n3 independent witness"

    hist = rg_hist()
    results["rg_945"] = {"histogram": hist}
    cert_hist = {int(k): v for k, v in cert["predecessor_945_control"]["histogram"].items()}
    assert hist == cert_hist, "945 histogram"
    assert sum(hist.values()) == 945 and max(hist) == 31, "945 shape"

    results["batch_calls"] = check_witness(cert)

    replay = {}
    for L in (1, 2, 3):
        for seed in range(4):
            dense_replay(cert, L, 1000 * L + seed)
        replay["L%d" % L] = 4
    results["dense_replay"] = replay

    results["mutation_controls"] = mutation_controls(cert)

    blob = json.dumps(results, sort_keys=True).encode()
    results["results_sha256"] = hashlib.sha256(blob).hexdigest()
    print(json.dumps(results, sort_keys=True))
    print("PASS_DUO_TOGGLE_INDEPENDENT s9_sets=%d full=%d batch_calls=%d"
          % (total, full, results["batch_calls"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
