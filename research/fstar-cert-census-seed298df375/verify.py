#!/usr/bin/env python3
"""F-star falsifier census for exact 3-total rational decoders (stdlib only).

Object: open problem F* of research/root-unit-decoder-lemmas section 7. For a
rational 3-total decoder M = sum_j p_j q_j^T on v lines with M_tt != 0, an L8
labelling chooses a(t) supported in Omega(t) = {j : p_j(t) != 0} and b(s)
supported in Psi(s) = {j : q_j(s) != 0}, K_ts = a(t).b(s) mod 2. cert(M) is the
largest |S| admitting an order with K_tt = 1 on S and K_ts = 0 at every
incidence M_ts = 0 with t before s. F* states cert(M) >= floor(2v/3).

Two exact sides:
  Side B (lower bound on cert): exhibit a labelling, subset and order witness.
  Side A (upper bound on cert, falsifier hunt): the proven chain of the source
  package gives cert(M) <= sum_j rank_F2 B[R_j, A_j] for every 0/1 unit-diagonal
  pairing B with ones only where M vanishes. Any instance whose minimum such
  cost falls below floor(2v/3) is a falsifier of F* (universal reading).

Everything is deterministic: the only randomness comes from fixed seeds.
Aaron Wang, with help from opencode. Apache-2.0.
"""
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = 3


# ---------------------------------------------------------------- F2 linear algebra

def f2_rank(rows, ncols):
    """Rank over F2 of a matrix given as a list of bitmasks (bit c = column c)."""
    basis = {}
    for r in rows:
        x = r
        while x:
            c = x.bit_length() - 1
            if c in basis:
                x ^= basis[c]
            else:
                basis[c] = x
                break
    return len(basis)


# ---------------------------------------------------------------- instance model

class Decoder:
    """M = sum_{j<T} p_j q_j^T on lines 0..v-1, integer factors."""

    def __init__(self, v, P, Q):
        self.v = v
        self.P = P  # P[j][t] = p_j(t)
        self.Q = Q  # Q[j][t] = q_j(t)
        self.M = [[sum(P[j][t] * Q[j][s] for j in range(T)) for s in range(v)] for t in range(v)]
        self.diag_ok = all(self.M[t][t] != 0 for t in range(v))
        self.zero = [[self.M[t][s] == 0 for s in range(v)] for t in range(v)]
        self.omega = [{j for j in range(T) if P[j][t] != 0} for t in range(v)]
        self.psi = [{j for j in range(T) if Q[j][t] != 0} for t in range(v)]
        self.R = [{t for t in range(v) if P[j][t] != 0} for j in range(T)]
        self.A = [{t for t in range(v) if Q[j][t] != 0} for j in range(T)]

    def label_options(self, t):
        """All (a, b) in F2^3 x F2^3 with supp(a) subset Omega(t), supp(b) subset Psi(t)."""
        opts = []
        for amask in range(1 << T):
            if any((amask >> j) & 1 and j not in self.omega[t] for j in range(T)):
                continue
            for bmask in range(1 << T):
                if any((bmask >> j) & 1 and j not in self.psi[t] for j in range(T)):
                    continue
                opts.append((amask, bmask))
        return opts


def threshold(v):
    return (2 * v) // 3


def kval(a, b):
    return bin(a & b).count("1") & 1


# ---------------------------------------------------------------- Side B: witnesses

def cert_witness(dec, labels):
    """MAS of the incidence digraph on valid lines, with order. labels[t] = (a, b)."""
    v = dec.v
    valid = [t for t in range(v) if kval(labels[t][0], labels[t][1]) == 1]
    if not valid:
        return 0, [], []
    index = {t: i for i, t in enumerate(valid)}
    n = len(valid)
    outmask = [0] * n
    for ti in valid:
        for s in valid:
            if s != ti and dec.zero[ti][s] and kval(labels[ti][0], labels[s][1]) == 1:
                outmask[index[ti]] |= 1 << index[s]
    full = (1 << n) - 1
    dp = bytearray(1 << n)
    dp[0] = 1
    best = 0
    bestmask = 0
    for mask in range(1, 1 << n):
        m = mask
        while m:
            bit = m & -m
            u = bit.bit_length() - 1
            if dp[mask ^ bit] and (outmask[u] & (mask ^ bit)) == 0:
                dp[mask] = 1
                if mask.bit_count() > best:
                    best = mask.bit_count()
                    bestmask = mask
                break
            m ^= bit
    subset = [valid[i] for i in range(n) if (bestmask >> i) & 1]
    # Sink-peeling order: sinks first. Edge u->w requires w before u.
    order = []
    remaining = set(subset)
    while remaining:
        sinks = sorted(t for t in remaining
                       if not any(s in remaining and s != t and dec.zero[t][s]
                                  and kval(labels[t][0], labels[s][1]) == 1 for s in remaining))
        assert sinks, "MAS subset must be acyclic"
        order.extend(sinks)
        remaining -= set(sinks)
    return best, subset, order


def witness_ok(dec, labels, subset, order):
    """Independent replay of the witness conditions."""
    pos = {t: i for i, t in enumerate(order)}
    if sorted(order) != sorted(subset) or len(set(order)) != len(order):
        return False
    for t in subset:
        if kval(labels[t][0], labels[t][1]) != 1:
            return False
    for t in subset:
        for s in subset:
            # t before s at an incidence M_ts = 0 requires K_ts == 0.
            if s != t and dec.zero[t][s] and pos[t] < pos[s]:
                if kval(labels[t][0], labels[s][1]) != 0:
                    return False
    return True


def search_labels(dec, budget=150, seed=0):
    """Deterministic local search over labellings maximising the witness size."""
    v = dec.v
    rng = random.Random(seed)
    options = [dec.label_options(t) for t in range(v)]
    base = []
    for t in range(v):
        common = sorted(dec.omega[t] & dec.psi[t])
        j = common[0]
        base.append((1 << j, 1 << j))
    best_labels = list(base)
    best_size, best_subset, best_order = cert_witness(dec, best_labels)
    evals = 1
    improved = True
    while improved and evals < budget and best_size < v:
        improved = False
        for t in range(v):
            for opt in options[t]:
                if opt == best_labels[t]:
                    continue
                trial = list(best_labels)
                trial[t] = opt
                size, subset, order = cert_witness(dec, trial)
                evals += 1
                if size > best_size:
                    best_size, best_subset, best_order = size, subset, order
                    best_labels = trial
                    improved = True
                if evals >= budget or best_size == v:
                    break
            if evals >= budget or best_size == v:
                break
    if best_size < v and evals < budget:
        for _restart in range(3):
            if evals >= budget or best_size == v:
                break
            trial = list(best_labels)
            for t in rng.sample(range(v), k=max(1, v // 3)):
                trial[t] = rng.choice(options[t])
            for t in range(v):
                for opt in options[t]:
                    if opt == trial[t]:
                        continue
                    cand = list(trial)
                    cand[t] = opt
                    size, subset, order = cert_witness(dec, cand)
                    evals += 1
                    if size > best_size:
                        best_size, best_subset, best_order = size, subset, order
                        best_labels = cand
                    if evals >= budget or best_size == v:
                        break
                if evals >= budget or best_size == v:
                    break
    return best_size, best_labels, best_subset, best_order, evals


def brute_cert(dec):
    """Exact cert by enumerating every labelling (tiny v only)."""
    v = dec.v
    options = [dec.label_options(t) for t in range(v)]
    best = 0
    labels = [None] * v

    def rec(t):
        nonlocal best
        if t == v:
            size, _, _ = cert_witness(dec, labels)
            if size > best:
                best = size
            return
        for opt in options[t]:
            labels[t] = opt
            rec(t + 1)

    rec(0)
    return best


# ---------------------------------------------------------------- Side A: pairing cost

def cost_B(dec, B):
    """sum_j rank_F2 B[R_j, A_j]. B is a list of row bitmasks over columns."""
    total = 0
    for j in range(T):
        rows = []
        A_list = sorted(dec.A[j])
        colbit = {s: 1 << i for i, s in enumerate(A_list)}
        for t in sorted(dec.R[j]):
            row = 0
            for s in A_list:
                if (B[t] >> s) & 1:
                    row |= colbit[s]
            rows.append(row)
        total += f2_rank(rows, len(A_list))
    return total


def pairing_ok(dec, B):
    for t in range(dec.v):
        if ((B[t] >> t) & 1) != 1:
            return False
        for s in range(dec.v):
            if s != t and ((B[t] >> s) & 1) and not dec.zero[t][s]:
                return False
    return True


def min_cost_pairing(dec, exhaustive_limit=10, budget=300, seed=0):
    """Minimum cost over admissible B: 0/1, unit diagonal, ones only at incidences.

    Exhaustive over all such B when the admissible pair count is small;
    deterministic single-bit local search otherwise. Returns
    (min_cost, B, exact) where exact says the exhaustive minimum was proved.
    """
    v = dec.v
    # Admissible B: 0/1, unit diagonal, B_ts = 1 only where M_ts = 0 (s != t).
    # The source lemma's chain cert(M) <= sum_j rank_F2 B[R_j, A_j] uses only
    # these two properties, so asymmetric B are included (stronger upper bound).
    pairs = [(t, s) for t in range(v) for s in range(v)
             if s != t and dec.zero[t][s]]
    base = [1 << t for t in range(v)]  # B = identity

    def apply(mask):
        B = list(base)
        for i, (t, s) in enumerate(pairs):
            if (mask >> i) & 1:
                B[t] |= 1 << s
        return B

    if len(pairs) <= exhaustive_limit:
        best = None
        bestB = None
        for mask in range(1 << len(pairs)):
            B = apply(mask)
            c = cost_B(dec, B)
            if best is None or c < best:
                best, bestB = c, B
        return best, bestB, True

    rng = random.Random(seed)
    best = cost_B(dec, base)
    bestB = list(base)
    bestmask = 0
    evals = 1
    improved = True
    while improved and evals < budget:
        improved = False
        for i in range(len(pairs)):
            cand = bestmask ^ (1 << i)
            B = apply(cand)
            c = cost_B(dec, B)
            evals += 1
            if c < best:
                best, bestB, bestmask = c, B, cand
                improved = True
        for _ in range(2):
            if evals >= budget:
                break
            cand = bestmask ^ (1 << rng.randrange(len(pairs)))
            B = apply(cand)
            c = cost_B(dec, B)
            evals += 1
            if c < best:
                best, bestB, bestmask = c, B, cand
    return best, bestB, False


# ---------------------------------------------------------------- families

def draw_entries(rng, v, alphabet):
    P = [[rng.choice(alphabet) for _ in range(v)] for _ in range(T)]
    Q = [[rng.choice(alphabet) for _ in range(v)] for _ in range(T)]
    return P, Q


def make_instance(family, v, seed):
    """Build a decoder with M_tt != 0 on every line; deterministic in seed."""
    rng = random.Random(seed)
    for _attempt in range(2000):
        if family == "dense":
            P, Q = draw_entries(rng, v, [-2, -1, 0, 1, 2])
        elif family == "config":
            P, Q = draw_entries(rng, v, [-1, 0, 1])
        elif family == "tied":
            # Products p_j(t) q_j(t) from a 2-adic-weighted alphabet; retained
            # only when tied minimal valuations cover at least half the lines,
            # the obstruction named in the source package's section 7.
            P, Q = draw_entries(rng, v, [-2, -1, 1, 2, 4])
        else:
            raise ValueError(family)
        dec = Decoder(v, P, Q)
        if dec.diag_ok and (family != "tied" or tied_score(dec) >= (v + 1) // 2):
            return dec
    raise RuntimeError("no instance with nonzero diagonal")


def tied_score(dec):
    """Number of lines whose minimal 2-adic valuation among products is attained twice or more."""
    def v2(x):
        if x == 0:
            return 99
        k = 0
        while x % 2 == 0:
            x //= 2
            k += 1
        return k

    count = 0
    for t in range(dec.v):
        vals = [v2(dec.P[j][t] * dec.Q[j][t]) for j in range(T)]
        m = min(vals)
        if vals.count(m) >= 2:
            count += 1
    return count


# ---------------------------------------------------------------- census

FAMILIES = ("dense", "config", "tied")


def run_census():
    records = []
    for family in FAMILIES:
        for v in range(4, 13):
            n = 10 if v <= 8 else 5
            if family == "tied":
                n = 8 if v <= 8 else 4
            for i in range(n):
                seed = 20261015 + 1000 * FAMILIES.index(family) + 17 * v + i
                dec = make_instance(family, v, seed)
                thr = threshold(v)
                size, labels, subset, order, evals = search_labels(
                    dec, budget=150, seed=seed + 1)
                assert witness_ok(dec, labels, subset, order), "search produced an invalid witness"
                minc, B, exact = min_cost_pairing(
                    dec, exhaustive_limit=10, budget=300, seed=seed + 2)
                assert pairing_ok(dec, B)
                # Proven chain: witness size <= cost(B) for every admissible B.
                assert size <= cost_B(dec, B), "proven chain violated"
                if exact:
                    assert size <= minc, "proven chain violated"
                records.append({
                    "family": family, "v": v, "seed": seed, "threshold": thr,
                    "witness": size, "min_cost_upper": minc, "min_cost_exact": exact,
                    "tied_lines": tied_score(dec),
                    "zero_pairs": sum(dec.zero[t][s] for t in range(v) for s in range(v) if s != t),
                    "evals": evals,
                    "falsifier": minc < thr, "resolved": size >= thr,
                })
    return records


def run_controls():
    out = {}
    # C1: tiny-domain brute force cross-checks the search engine exactly.
    brute_cases = []
    for k, (family, v) in enumerate((("dense", 3), ("config", 3), ("tied", 3))):
        dec = make_instance(family, v, 777 + k)
        exact = brute_cert(dec)
        size, labels, subset, order, _ = search_labels(dec, budget=200, seed=900 + k)
        assert witness_ok(dec, labels, subset, order)
        brute_cases.append({"family": family, "v": v, "brute": exact, "search": size})
        assert size == exact, "search engine missed the exact cert on a tiny instance"
    out["bruteforce_crosscheck"] = brute_cases

    # C2: a corrupted witness must be rejected.
    dec = make_instance("config", 5, 4242)
    size, labels, subset, order, _ = search_labels(dec, budget=150, seed=1)
    assert witness_ok(dec, labels, subset, order)
    bad = list(labels)
    t0 = order[0]
    bad[t0] = (0, 0)  # breaks K_tt = 1
    assert not witness_ok(dec, bad, subset, order), "corrupted witness was accepted"
    # A binding pair (K_ts = 1 at an incidence) must reject any order with t before s.
    binding = None
    for t in subset:
        for s in subset:
            if s != t and dec.zero[t][s] and kval(labels[t][0], labels[s][1]) == 1:
                binding = (t, s)
                break
        if binding:
            break
    order_rejected = False
    if binding:
        t, s = binding
        flipped = [t] + [x for x in order if x not in (t, s)] + [s]  # forces t before s at a binding pair
        if not witness_ok(dec, labels, subset, flipped):
            order_rejected = True
    out["corrupted_witness_rejected"] = True
    out["binding_pair_order_rejected"] = order_rejected

    # C3: threshold table by hand for v = 4..12 (floor(2v/3)).
    table = {v: (2 * v) // 3 for v in range(4, 13)}
    assert table == {4: 2, 5: 3, 6: 4, 7: 4, 8: 5, 9: 6, 10: 6, 11: 7, 12: 8}
    out["threshold_table"] = table

    # C4: hand-checkable diagonal decoder: p_j = q_j = e_j on three lines.
    P = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    dec = Decoder(3, P, [list(r) for r in P])
    assert dec.diag_ok and all(dec.M[t][s] == (1 if t == s else 0) for t in range(3) for s in range(3))
    exact = brute_cert(dec)
    assert exact == 3
    out["diagonal_control_cert"] = exact

    # C5: the proven chain cert <= cost(B) on a known instance, both sides exact.
    dec = make_instance("dense", 4, 31337)
    exact = brute_cert(dec)
    minc, B, is_exact = min_cost_pairing(dec, exhaustive_limit=6)
    assert pairing_ok(dec, B)
    assert exact <= minc
    out["chain_control"] = {"brute_cert": exact, "min_cost": minc, "min_cost_exact": is_exact}
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    controls = run_controls()
    records = run_census()
    total = len(records)
    falsifiers = [r for r in records if r["falsifier"]]
    unresolved = [r for r in records if not r["resolved"] and not r["falsifier"]]
    resolved = [r for r in records if r["resolved"]]
    min_ratio = min(r["witness"] / r["v"] for r in records)
    worst = min(records, key=lambda r: (r["witness"] / r["v"], r["v"]))
    by_family = {}
    for fam in FAMILIES:
        rows = [r for r in records if r["family"] == fam]
        by_family[fam] = {
            "instances": len(rows),
            "resolved": sum(1 for r in rows if r["resolved"]),
            "min_witness_ratio": min(r["witness"] / r["v"] for r in rows),
            "max_tied_lines": max(r["tied_lines"] for r in rows),
        }
    cert = {
        "schema_version": 1,
        "claim": "F-star: cert(M) >= floor(2v/3) for exact 3-total rational decoders",
        "source": "research/root-unit-decoder-lemmas/README.md section 7 (OPEN)",
        "domain": {"v": "4..12", "totals": 3, "factor_entries": "-2..2",
                   "families": list(FAMILIES), "seeds": "20261015 + 1000*family_index + 17*v + i"},
        "instances": total,
        "resolved_witness": len(resolved),
        "falsifiers": len(falsifiers),
        "unresolved": len(unresolved),
        "min_witness_ratio": min_ratio,
        "worst_instance": worst,
        "by_family": by_family,
        "controls": controls,
        "outcome": "SCOPED_NEGATIVE_NO_FALSIFIER" if not falsifiers and not unresolved
                   else ("FALSIFIER_FOUND" if falsifiers else "UNRESOLVED_INSTANCES"),
        "no_new_kappa": True,
    }
    digest = hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()
    cert["census_digest"] = digest
    (HERE / "CERTIFICATE.json").write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n",
                                           encoding="utf-8")
    (HERE / "CENSUS-RECORDS.json").write_text(json.dumps(records, indent=2, sort_keys=True) + "\n",
                                              encoding="utf-8")
    print("PASS_FSTAR_CERT_CENSUS instances=%d resolved=%d falsifiers=%d unresolved=%d "
          "min_ratio=%.4f digest=%s" % (total, len(resolved), len(falsifiers), len(unresolved),
                                        min_ratio, digest[:16]))
    print("PASS_FSTAR_CERT_CONTROLS bruteforce=%d diagonal_cert=%d chain_cert=%d"
          % (len(controls["bruteforce_crosscheck"]), controls["diagonal_control_cert"],
             controls["chain_control"]["brute_cert"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
