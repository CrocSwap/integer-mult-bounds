#!/usr/bin/env python3
"""Finite checks behind the width-independence theorem for the doubled centre Gram.

Nick Petalas. Apache-2.0. Standard library only; every acceptance test is an
explicit `require`, so `python -O` skips nothing.

PROOF.md proves, for the operators A_lambda of research/exact-one-slot-gram,
that one polynomial annihilates every width, that the minimal-polynomial degree
is nondecreasing, and that the minimal polynomial is constant from width 10 on.
The proof needs four finite facts, which this script checks:

  1. Source binding: the pinned 8-by-112 query has 112 distinct odd-weight labels.
  2. The Bell identity Gamma_q E_(a,b) = +-E_(a',b'), exactly, on every label.
  3. The F_2-dimension d_A of span{q q^T}, which bounds the label action of G.
  4. On exactly enumerated small groups of the same kind: |G| = |A||K|, the trace
     values lie in {0} U {2^(2n-r)}, and the sign function is additive on every
     fixed-point space (the lemma behind the trace values).

It does not compute the width-two or the stable minimal polynomial and says
nothing about physical cost.
"""
import hashlib
import json
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
INTERFACE = ROOT / ("research/centre-polynomial-cache-limits/frozen/work/"
                    "centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json")
INTERFACE_SHA256 = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
ONE_SLOT_PROOF = ROOT / "research/exact-one-slot-gram/PROOF.md"
OPERATOR_TEXT = "A_lambda = (1/4) sum_q r_q r_q^T tensor Gamma_q^tensor(lambda)"
N_BITS = 9
POINTS = 512
MARKER = "PASS_CENTRE_GRAM_WIDTH_STABILIZATION"


class CheckFailed(Exception):
    pass


def require(condition, message):
    if not condition:
        raise CheckFailed(message)


def parity(x):
    return bin(x).count("1") & 1


def f2_rank(rows):
    basis = {}
    for row in rows:
        while row:
            top = row.bit_length() - 1
            if top in basis:
                row ^= basis[top]
            else:
                basis[top] = row
                break
    return len(basis)


# ---------------------------------------------------------------- 1. source binding

def load_model():
    raw = INTERFACE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == INTERFACE_SHA256, "INTERFACE.json bytes differ from the pin")
    data = json.loads(raw)
    ports = data["ports"]
    require(len(ports) == 112 and len(set(ports)) == 112, "expected 112 distinct labels")
    require(all(isinstance(q, int) and 0 < q < POINTS and parity(q) == 1 for q in ports),
            "every label must be an odd-weight nonzero 9-bit integer")
    rows = data["R"]
    require(len(rows) == 8, "R must have 8 rows")
    columns = [dict() for _ in ports]
    for i, row in enumerate(rows):
        for key, value in row.items():
            j = int(key)
            require(0 <= j < 112 and value in ("1", "-1"), "R entries must be +-1 on columns 0..111")
            columns[j][i] = int(value)
    require(all(len(col) == 4 for col in columns), "every column of R must have four +-1 entries")
    for i in range(8):
        for k in range(8):
            gram = sum(columns[j].get(i, 0) * columns[j].get(k, 0) for j in range(112))
            require(gram == (56 if i == k else 0), "R R^T must equal 56 I")
    text = ONE_SLOT_PROOF.read_text(encoding="utf-8")
    require(OPERATOR_TEXT in text.replace("\n", " ").replace("  ", " ") or
            "A_lambda = (1/4) sum_q r_q r_q^T tensor Gamma_q^tensor(lambda)" in text,
            "operator definition not found in the pinned one-slot proof")
    quoted = {
        ROOT / "research/exact-one-slot-gram/TASK.json": "uniform upper-degree bound",
        ROOT / "research/equal-bell-two-slot-spectrum/README.md": "at least\n1093",
        ROOT / "research/clifford-tensor-gram/PROOF.md": "Burnside-Brauer",
    }
    for path, phrase in quoted.items():
        require(phrase in path.read_text(encoding="utf-8"), "pinned source no longer states: " + phrase)
    return ports


# ---------------------------------------------------------------- 2. Bell identity

def sandwich_column(q, a, b, x):
    """Column x of (X_q + Z_q) E_(a,b) (X_q + Z_q), with E_(a,b) = X_b Z_a, as {row: integer}."""
    out = {}
    for y, s1 in ((x ^ q, 1), (x, -1 if parity(q & x) else 1)):
        z, s2 = y ^ b, s1 * (-1 if parity(a & y) else 1)
        for w, s3 in ((z ^ q, s2), (z, s2 * (-1 if parity(q & z) else 1))):
            out[w] = out.get(w, 0) + s3
    return {row: value for row, value in out.items() if value}


def predicted_column(q, a, b, x, flip=False):
    """Column x of 2 * Gamma_q(E_(a,b)) by the claimed signed permutation; `flip` is a mutant."""
    if parity(q & (a ^ b)) == 0:
        a2, b2, sign = a, b, (-1 if parity(q & a) else 1)
        if flip:
            sign = -sign
    else:
        a2, b2, sign = a ^ q, b ^ q, 1
    return {x ^ b2: 2 * sign * (-1 if parity(a2 & x) else 1)}


def bell_identity_holds(q, a, b, flip=False):
    return all(sandwich_column(q, a, b, x) == predicted_column(q, a, b, x, flip) for x in range(POINTS))


def sample_pairs(q, count):
    state = (q * 2654435761 + 12345) & 0xFFFFFFFF
    pairs = [(0, 0), (POINTS - 1, 0), (0, POINTS - 1), (q, 0), (0, q), (q, q), (1, q ^ 1), (q ^ 0x155, 0x0AA)]
    while len(pairs) < count:
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        a = state % POINTS
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        pairs.append((a, state % POINTS))
    return pairs


def check_bell_identity(ports):
    zero_cases = one_cases = 0
    for q in ports:
        for a, b in sample_pairs(q, 16):
            require(bell_identity_holds(q, a, b), "Bell identity fails at q=%d a=%d b=%d" % (q, a, b))
            if parity(q & (a ^ b)):
                one_cases += 1
            else:
                zero_cases += 1
    require(zero_cases > 0 and one_cases > 0, "both Bell cases must be exercised")
    return zero_cases, one_cases


# ---------------------------------------------------------------- 3. label-group dimension

def outer_product_bits(q, n=N_BITS):
    bits = k = 0
    for i in range(n):
        for j in range(i, n):
            if (q >> i) & 1 and (q >> j) & 1:
                bits |= 1 << k
            k += 1
    return bits


def label_dimension(labels, n=N_BITS):
    return f2_rank([outer_product_bits(q, n) for q in labels])


def symmetric_rank(labels, n):
    """F_2 rank of M_S = sum of q q^T over the given labels."""
    rows = [0] * n
    for q in labels:
        for i in range(n):
            if (q >> i) & 1:
                rows[i] ^= q
    return f2_rank(rows)


# ---------------------------------------------------------------- 4. exactly enumerated groups

def generator(n, q):
    """Gamma_q as a signed permutation of the 4^n Pauli labels v = (a << n) | b.

    Entry v is (image << 1) | s, where s = 1 means the sign -1."""
    mask = (1 << n) - 1
    image = []
    for v in range(1 << (2 * n)):
        a, b = v >> n, v & mask
        if parity(q & (a ^ b)) == 0:
            image.append((v << 1) | parity(q & a))
        else:
            image.append((((a ^ q) << n) | (b ^ q)) << 1)
    return tuple(image)


def compose(g, h):
    """g after h."""
    return tuple(g[hv >> 1] ^ (hv & 1) for hv in h)


def check_element(g, n, labels, parity_set):
    """Lemma behind the trace values; returns the trace and |Fix|."""
    fixed = [v for v in range(1 << (2 * n)) if (g[v] >> 1) == v]
    basis = {}
    for v in fixed:
        vec, sign = v, g[v] & 1
        while vec:
            top = vec.bit_length() - 1
            if top in basis:
                bvec, bsign = basis[top]
                vec ^= bvec
                sign ^= bsign
            else:
                basis[top] = (vec, sign)
                break
        else:
            require(sign == 0, "sign function is not additive on the fixed labels")
    require(len(fixed) == 1 << len(basis), "fixed labels do not form a subspace")
    trace = sum(-1 if g[v] & 1 else 1 for v in fixed)
    trivial = all(sign == 0 for _, sign in basis.values())
    require(trace == (len(fixed) if trivial else 0), "trace is neither |Fix| nor 0")
    chosen = [labels[i] for i in range(len(labels)) if (parity_set >> i) & 1]
    require(len(fixed) == 1 << (2 * n - symmetric_rank(chosen, n)), "|Fix| differs from 2^(2n - rank M_S)")
    return trace, len(fixed)


def check_group(n, labels, generators=None):
    require(n in (3, 4) and 1 <= len(labels) <= 4, "enumeration is restricted to the two small dimensions")
    d_a = label_dimension(labels, n)
    cap = 1 << (d_a + 2 * n)
    gens = generators or [generator(n, q) for q in labels]
    identity = tuple(v << 1 for v in range(1 << (2 * n)))
    seen = {identity: 0}
    frontier = [identity]
    for _ in range(cap):
        if not frontier:
            break
        nxt = []
        for g in frontier:
            for index, gen in enumerate(gens):
                h = compose(gen, g)
                if h not in seen:
                    require(len(seen) < cap, "group exceeds the proved order bound 2^(d_A + 2n)")
                    seen[h] = seen[g] ^ (1 << index)
                    nxt.append(h)
        frontier = nxt
    require(not frontier, "group enumeration exhausted its finite bound")
    traces = set()
    labelings = {}
    for g, parity_set in seen.items():
        trace, _ = check_element(g, n, labels, parity_set)  # Fixed-space size is checked inside the callee.
        traces.add(trace)
        labelings.setdefault(tuple(v >> 1 for v in g), []).append(g)
    kernel = labelings.get(tuple(range(1 << (2 * n))), [])
    require(len(seen) == len(labelings) * len(kernel), "|G| differs from |A||K|")
    require(len(kernel) <= 1 << (2 * n), "kernel exceeds 2^(2n)")
    require(len(labelings) == 1 << d_a, "label image does not have order 2^d_A")
    for gen_a in gens:
        for gen_b in gens:
            require(tuple(x >> 1 for x in compose(gen_a, gen_b)) == tuple(x >> 1 for x in compose(gen_b, gen_a)),
                    "label actions of the generators do not commute")
    allowed = {0} | {1 << (2 * n - r) for r in range(n + 1)}
    require(traces <= allowed, "trace value outside {0} U {2^(2n-r)}")
    if generators is None:
        require(1 << kernel_dimension(n, labels) == len(kernel), "kernel module differs from the enumerated kernel")
    return {"order": len(seen), "label_image": len(labelings), "kernel": len(kernel), "d_A": d_a,
            "trace_values": sorted(traces), "width_bound": len(traces) - 1}


# ---------------------------------------------------------------- exact kernel dimension

def apply_word(n, word, v):
    """Apply Gamma_{q_1} ... Gamma_{q_k} (rightmost letter first) to the label v; return (image, sign bit)."""
    mask = (1 << n) - 1
    sign = 0
    for q in reversed(word):
        a, b = v >> n, v & mask
        if parity(q & (a ^ b)) == 0:
            sign ^= parity(q & a)
        else:
            v = ((a ^ q) << n) | (b ^ q)
    return v, sign


def omega(n, s, v):
    mask = (1 << n) - 1
    return parity((s >> n) & (v & mask)) ^ parity((s & mask) & (v >> n))


def sign_vector(n, word):
    """The vector s with word = diagonal sign matrix (-1)^omega(s, v); the word must act trivially on labels."""
    s = 0
    for i in range(n):
        v = (1 << i) << n
        image, sign = apply_word(n, word, v)
        require(image == v, "word does not act trivially on labels")
        s |= sign << i
        v = 1 << i
        image, sign = apply_word(n, word, v)
        require(image == v, "word does not act trivially on labels")
        s |= sign << (n + i)
    state = (len(word) * 40503 + 7) & 0xFFFFFFFF
    for _ in range(32):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        v = state % (1 << (2 * n))
        image, sign = apply_word(n, word, v)
        require(image == v and sign == omega(n, s, v), "sign function of a trivial-label word is not linear")
    return s


def kernel_dimension(n, labels):
    """dim_F2 of K = ker(G -> label action), as the A-module generated by commutators and relation words.

    G/K is generated by the images of an F_2-independent subfamily of the generators (their label
    actions I + N_q add), so K is the normal closure of the commutators of generators together with the
    words that express each dependent generator through the independent ones."""
    require(1 <= n <= N_BITS and 1 <= len(labels) <= 112, "kernel model exceeds the fixed dimensions")
    require(len(set(labels)) == len(labels), "kernel labels must be distinct")
    require(all(0 < q < 1 << n and parity(q) for q in labels), "kernel labels must be odd n-bit integers")
    basis, relations = {}, []
    for j, q in enumerate(labels):
        vec, combo = outer_product_bits(q, n), 1 << j
        while vec:
            top = vec.bit_length() - 1
            if top in basis:
                vec ^= basis[top][0]
                combo ^= basis[top][1]
            else:
                basis[top] = (vec, combo)
                break
        else:
            relations.append([labels[i] for i in range(len(labels)) if (combo >> i) & 1])
    words = [[x, y, x, y] for x in labels for y in labels if x < y] + relations
    queue = [sign_vector(n, word) for word in words]
    span = {}
    pair_masks = [(q << n) | q for q in labels]
    for _ in range(len(words) + 2 * n * len(labels)):
        if not queue:
            break
        u = queue.pop()
        while u:
            top = u.bit_length() - 1
            if top in span:
                u ^= span[top]
            else:
                span[top] = u
                require(len(span) <= 2 * n, "kernel span exceeds its ambient dimension")
                for q, t in zip(labels, pair_masks):
                    queue.append(u ^ (t if parity(q & ((u >> n) ^ (u & ((1 << n) - 1)))) else 0))
                break
    require(not queue, "kernel closure exhausted its finite bound")
    return len(span)


def expect_failure(label, function):
    try:
        function()
    except CheckFailed:
        return
    raise CheckFailed("control did not reject: " + label)


def run_controls(ports):
    q_even = 3
    require(not all(bell_identity_holds(q_even, a, b) for a, b in sample_pairs(q_even, 8)),
            "an even-weight label must break the Bell identity")
    odd = ports[0]
    require(not all(bell_identity_holds(odd, a, b, flip=True) for a, b in sample_pairs(odd, 8)),
            "a sign-flipped prediction must be rejected")
    n, labels = 3, [1, 2, 4, 7]
    mutated = [generator(n, q) for q in labels]
    broken = list(mutated[3])
    broken[5] ^= 1
    mutated[3] = tuple(broken)
    expect_failure("one extra sign flip in a generator", lambda: check_group(n, labels, mutated))
    expect_failure("a translation that does not fix the zero Pauli label",
                   lambda: check_element(tuple(((v ^ 1) << 1) | (v & 1) for v in range(64)), 3, [1], 1))
    return 4


def main():
    ports = load_model()
    zero_cases, one_cases = check_bell_identity(ports)
    d_a = label_dimension(ports)
    require(1 <= d_a <= N_BITS * (N_BITS + 1) // 2, "d_A out of range")
    d_k = kernel_dimension(N_BITS, ports)
    require(0 <= d_k <= 2 * N_BITS, "kernel dimension out of range")
    require((d_a, d_k) == (36, 8), "actual group dimensions differ from the theorem")
    log_g = d_a + d_k
    toys = [(3, [1, 2, 4, 7]), (4, [1, 7, 14])]
    toy_rows = []
    for n, labels in toys:
        toy_rows.append((n, labels, check_group(n, labels)))
    controls = run_controls(ports)
    trace_values = 1 + (N_BITS + 1)
    print(json.dumps({
        "interface_sha256": INTERFACE_SHA256,
        "labels": len(ports),
        "bell_cases_checked": {"q.(a+b)=0": zero_cases, "q.(a+b)=1": one_cases},
        "d_A": d_a,
        "d_K": d_k,
        "log2_group_order": log_g,
        "annihilator_degree_bound": "8 * 2^%d = 2^%d" % (log_g, log_g + 3),
        "possible_trace_values": trace_values,
        "stabilization_width": trace_values - 1,
        "toy_groups": [{"n": n, "labels": labels, **row} for n, labels, row in toy_rows],
        "controls_rejected": controls,
    }, indent=1, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    try:
        main()
    except CheckFailed as error:
        sys.exit("FAIL: " + str(error))
