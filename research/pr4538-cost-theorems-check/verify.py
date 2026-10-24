#!/usr/bin/env python3
"""Independent check of PR #4538 (Dugongue) native-layout cost theorems 1-4, from the vendored COST-THEOREMS.md text.

Nothing is imported from #4538's streaming_affine.py, quadratic_phase.py or monomial_metadata.py.
  T1. Flip count T = sum_j (N/2^j - 1) = 2N - r - 2 by literal increments, and the identity
      8NL + 9N + 11T + 3 = 8NL + 31N - 11r - 19 <= 8NL + 40N + 8. Then my own fixed program on a small
      additive/Boolean RAM (no multiplication, division or right shift; costs XOR 4, MOV 2, JNZ 2, others 1, as
      stated) performs destination[(Ax^b)K + j] = source[xK + j], preserves source, table and padding cells, and its
      expanded count stays within 8NL + 40N + 8.
  T2. The streaming update d = (a_j + 2 g_j) mod 4, q += d on a 0->1 flip and q -= d on 1->0, g ^= column j,
      reproduces q(x) = sum a_j x_j + 2 sum_{j<k} B_jk x_j x_k (mod 4) at every x, with fewer than 2N flips.
  T3. Limb negation by digit complement plus carry equals negation modulo 2^(kL); the four Gaussian-unit cases equal
      multiplication by i^q.
  T4. My own metadata compiler from the stated update rules for X, S, Z, CNOT, SWAP, CZ satisfies
      word|x> = i^(c+q(x)) |Ax ^ b> against a literal Gaussian-integer state-vector interpreter on random words, global
      phase included; dropping c is caught (X then S).
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SPEC = HERE / "PR4538-COST-THEOREMS.md"  # #4538 head dffc7939, research/word-ram-transfer/cost/COST-THEOREMS.md, blob a5d940b2
SPEC_SHA256 = "79eef859eb2ae32a66879f294d626c3947bcfe55434b4a38a296d271b3aa9675"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


# ---------------------------------------------------------------- T1: a small RAM and my own fixed program
COST = {"LI": 1, "MOV": 2, "ADD": 1, "SUB": 1, "AND": 1, "XOR": 4, "SHL": 1, "LOAD": 1, "STORE": 1,
        "JZ": 1, "JNZ": 2, "JMP": 1, "HALT": 0}


def run(prog, regs, mem, w, limit):
    labels = {ins[1]: i for i, ins in enumerate(prog) if ins[0] == "LABEL"}
    mask = (1 << w) - 1
    pc = cost = 0
    while True:
        ins = prog[pc]
        op = ins[0]
        pc += 1
        if op == "LABEL":
            continue
        cost += COST[op]
        need(cost <= limit, "instruction limit")
        R = regs
        if op == "LI":
            R[ins[1]] = ins[2] & mask
        elif op == "MOV":
            R[ins[1]] = R[ins[2]]
        elif op == "ADD":
            R[ins[1]] = (R[ins[2]] + R[ins[3]]) & mask
        elif op == "SUB":
            R[ins[1]] = max(0, R[ins[2]] - R[ins[3]])  # truncated subtraction
        elif op == "AND":
            R[ins[1]] = R[ins[2]] & R[ins[3]]
        elif op == "XOR":
            R[ins[1]] = R[ins[2]] ^ R[ins[3]]
        elif op == "SHL":
            R[ins[1]] = (R[ins[2]] << R[ins[3]]) & mask
        elif op == "LOAD":
            R[ins[1]] = mem.get(R[ins[2]], 0)
        elif op == "STORE":
            need(R[ins[1]] < (1 << w), "address fits")
            mem[R[ins[1]]] = R[ins[2]]
        elif op == "JZ":
            if R[ins[1]] == 0:
                pc = labels[ins[2]]
        elif op == "JNZ":
            if R[ins[1]] != 0:
                pc = labels[ins[2]]
        elif op == "JMP":
            pc = labels[ins[1]]
        elif op == "HALT":
            return cost


# Inputs: SRC, DST, COL (r column words), NM1 = N-1, L, S = log2 K, Y = b. Constants: ONE.
AFFINE = [
    ("LI", "ONE", 1), ("LI", "X", 0),
    ("LABEL", "record"),
    ("SHL", "SA", "X", "S"), ("ADD", "SA", "SA", "SRC"),
    ("SHL", "DA", "Y", "S"), ("ADD", "DA", "DA", "DST"),
    ("MOV", "J", "L"),
    ("LABEL", "copy"),
    ("LOAD", "V", "SA"), ("STORE", "DA", "V"),
    ("ADD", "SA", "SA", "ONE"), ("ADD", "DA", "DA", "ONE"), ("SUB", "J", "J", "ONE"),
    ("JNZ", "J", "copy"),
    ("SUB", "T", "NM1", "X"), ("JZ", "T", "done"),
    ("LI", "M", 1), ("MOV", "CA", "COL"),
    ("LABEL", "carry"),
    ("AND", "T", "X", "M"), ("JZ", "T", "set"),
    ("SUB", "X", "X", "M"), ("LOAD", "C", "CA"), ("XOR", "Y", "Y", "C"),
    ("ADD", "M", "M", "M"), ("ADD", "CA", "CA", "ONE"), ("JMP", "carry"),
    ("LABEL", "set"),
    ("ADD", "X", "X", "M"), ("LOAD", "C", "CA"), ("XOR", "Y", "Y", "C"), ("JMP", "record"),
    ("LABEL", "done"), ("HALT",),
]


def flips(r):
    N = 1 << r
    return sum(bin(x ^ (x + 1)).count("1") for x in range(N - 1))


def check_t1(rng, program=AFFINE):
    cases = worst = 0
    for r in range(0, 9):
        N = 1 << r
        T = flips(r)
        need(T == sum(N // (1 << j) - 1 for j in range(r)) == 2 * N - r - 2, "flip count")
        for L in (1, 2, 3, 5):
            need(8 * N * L + 9 * N + 11 * T + 3 == 8 * N * L + 31 * N - 11 * r - 19 <= 8 * N * L + 40 * N + 8,
                 "count identity and bound")
            s = max(0, (L - 1).bit_length())
            K = 1 << s
            need(L <= K < 2 * L, "stride")
            while True:  # random invertible A over F_2
                cols = [rng.getrandbits(r) if r else 0 for _ in range(r)]
                basis = []
                for v in cols:
                    for bv in basis:
                        v = min(v, v ^ bv)
                    if v:
                        basis.append(v)
                if len(basis) == r:
                    break
            b = rng.getrandbits(r) if r else 0
            w = 32
            SRC, COL, DST = 1 << 12, 1 << 11, 1 << 20
            mem = {}
            for x in range(N):
                for j in range(K):
                    mem[SRC + x * K + j] = rng.getrandbits(16) if j < L else 7777
                    mem[DST + x * K + j] = 5555
            for j, c in enumerate(cols):
                mem[COL + j] = c
            before = dict(mem)
            regs = {"SRC": SRC, "DST": DST, "COL": COL, "NM1": N - 1, "L": L, "S": s, "Y": b}
            limit = 8 * N * L + 40 * N + 8
            cost = run(program, regs, mem, w, limit)

            def image(x):
                y = b
                for j in range(r):
                    if x >> j & 1:
                        y ^= cols[j]
                return y

            for x in range(N):
                y = image(x)
                for j in range(K):
                    if j < L:
                        need(mem[DST + y * K + j] == before[SRC + x * K + j], "payload moved")
                    else:
                        need(mem[DST + y * K + j] == 5555, "destination padding preserved")
            need(all(mem[a] == v for a, v in before.items() if a < DST), "source and table preserved")
            worst = max(worst, cost / limit)
            cases += 1
    return cases, round(worst, 4)


# ---------------------------------------------------------------- T2
def check_t2(rng):
    cases = 0
    for r in range(1, 9):
        N = 1 << r
        for _ in range(6):
            a = [rng.randrange(4) for _ in range(r)]
            B = [[0] * r for _ in range(r)]
            for j in range(r):
                for k in range(j + 1, r):
                    B[j][k] = B[k][j] = rng.randrange(2)
            colB = [sum(B[k][j] << k for k in range(r)) for j in range(r)]

            def q(x):
                v = sum(a[j] * (x >> j & 1) for j in range(r))
                v += 2 * sum(B[j][k] * (x >> j & 1) * (x >> k & 1) for j in range(r) for k in range(j + 1, r))
                return v % 4

            x = qq = g = nflips = 0
            need(q(0) == 0, "q(0)")
            for _ in range(N - 1):
                j = 0
                while True:  # binary increment, flip by flip
                    gj = g >> j & 1
                    d = (a[j] + 2 * gj) & 3
                    if x >> j & 1:
                        qq = (qq + 4 - d) & 3
                        x ^= 1 << j
                        g ^= colB[j]
                        nflips += 1
                        j += 1
                    else:
                        qq = (qq + d) & 3
                        x ^= 1 << j
                        g ^= colB[j]
                        nflips += 1
                        break
                need(qq == q(x), "streamed phase")
                cases += 1
            need(nflips < 2 * N, "fewer than 2N flips")
    return cases


# ---------------------------------------------------------------- T3
def check_t3(rng):
    cases = 0
    for k in (1, 2, 3, 8, 16):
        for L in (1, 2, 3, 5):
            beta = 1 << k
            for _ in range(40):
                v = rng.getrandbits(k * L)
                digits = [(v >> (k * i)) & (beta - 1) for i in range(L)]
                carry, out = 1, []
                for a in digits:
                    t = beta - 1 - a + carry
                    need(t <= beta, "temporary at most beta")
                    out.append(t & (beta - 1))
                    carry = 1 if t == beta else 0
                need(sum(d << (k * i) for i, d in enumerate(out)) == (-v) % (beta ** L), "limb negation")
                cases += 1
    units = {0: lambda u, v: (u, v), 1: lambda u, v: (-v, u), 2: lambda u, v: (-u, -v), 3: lambda u, v: (v, -u)}
    for qv in range(4):
        for u, v in ((3, 5), (-2, 7), (0, 1)):
            z = complex(u, v) * (1j ** qv)
            need(units[qv](u, v) == (round(z.real), round(z.imag)), "Gaussian unit")
            cases += 1
    return cases


# ---------------------------------------------------------------- T4
def gmul_i(z, e):
    u, v = z
    for _ in range(e % 4):
        u, v = -v, u
    return (u, v)


def literal(word, r, x):
    """Apply the gate word to basis state |x>; returns (index, Gaussian-integer amplitude)."""
    amp, y = (1, 0), x
    for g in word:
        op = g[0]
        if op == "X":
            y ^= 1 << g[1]
        elif op == "S":
            if y >> g[1] & 1:
                amp = gmul_i(amp, 1)
        elif op == "Z":
            if y >> g[1] & 1:
                amp = gmul_i(amp, 2)
        elif op == "CNOT":
            if y >> g[1] & 1:
                y ^= 1 << g[2]
        elif op == "SWAP":
            bj, bk = y >> g[1] & 1, y >> g[2] & 1
            if bj != bk:
                y ^= (1 << g[1]) | (1 << g[2])
        elif op == "CZ":
            if (y >> g[1] & 1) and (y >> g[2] & 1):
                amp = gmul_i(amp, 2)
    return y, amp


def compile_metadata(word, r):
    """Metadata from the stated update rules. A is stored by rows: row j is the output coordinate j."""
    rows = [1 << j for j in range(r)]
    b = [0] * r
    c = 0
    a = [0] * r
    B = [[0] * r for _ in range(r)]
    bit = lambda u, l: u >> l & 1
    for g in word:
        op = g[0]
        if op == "X":
            b[g[1]] ^= 1
        elif op == "CNOT":
            j, k = g[1], g[2]
            rows[k] ^= rows[j]
            b[k] ^= b[j]
        elif op == "SWAP":
            j, k = g[1], g[2]
            rows[j], rows[k] = rows[k], rows[j]
            b[j], b[k] = b[k], b[j]
        elif op in ("S", "Z"):
            j = g[1]
            u = rows[j]
            if op == "S":
                c = (c + b[j]) % 4
                for l in range(r):
                    a[l] = (a[l] + (1 - 2 * b[j]) * bit(u, l)) % 4
                for l in range(r):
                    for t in range(l + 1, r):
                        if bit(u, l) and bit(u, t):
                            B[l][t] ^= 1
                            B[t][l] ^= 1
            else:
                c = (c + 2 * b[j]) % 4
                for l in range(r):
                    a[l] = (a[l] + 2 * bit(u, l)) % 4
        elif op == "CZ":
            j, k = g[1], g[2]
            u, v = rows[j], rows[k]
            c = (c + 2 * (b[j] & b[k])) % 4
            for l in range(r):
                lin = (b[j] & bit(v, l)) ^ (b[k] & bit(u, l)) ^ (bit(u, l) & bit(v, l))
                a[l] = (a[l] + 2 * lin) % 4
            for l in range(r):
                for t in range(l + 1, r):
                    if (bit(u, l) & bit(v, t)) ^ (bit(u, t) & bit(v, l)):
                        B[l][t] ^= 1
                        B[t][l] ^= 1
    for j in range(r):
        need(B[j][j] == 0 and all(B[j][t] == B[t][j] for t in range(r)), "B symmetric, zero diagonal")
    return rows, b, c, a, B


def apply_metadata(meta, r, x, keep_c=True):
    rows, b, c, a, B = meta
    y = 0
    for j in range(r):
        y |= ((bin(rows[j] & x).count("1") + b[j]) & 1) << j
    qv = sum(a[j] * (x >> j & 1) for j in range(r))
    qv += 2 * sum(B[j][t] * (x >> j & 1) * (x >> t & 1) for j in range(r) for t in range(j + 1, r))
    return y, gmul_i((1, 0), (c if keep_c else 0) + qv)


def check_t4(rng):
    words = 0
    for r in range(1, 7):
        for _ in range(60):
            m = rng.randrange(0, 41)
            word = []
            for _ in range(m):
                op = rng.choice(("X", "S", "Z", "CNOT", "SWAP", "CZ"))
                if op in ("X", "S", "Z") or r == 1:
                    word.append((op if r > 1 or op in ("X", "S", "Z") else "S", rng.randrange(r)))
                else:
                    j, k = rng.sample(range(r), 2)
                    word.append((op, j, k))
            meta = compile_metadata(word, r)
            for x in range(1 << r):
                need(literal(word, r, x) == apply_metadata(meta, r, x), "word|x> = i^(c+q(x))|Ax^b>")
            words += 1
    # Control: X then S has global phase i on |0>; dropping c is caught.
    meta = compile_metadata([("X", 0), ("S", 0)], 1)
    need(meta[2] == 1 and literal([("X", 0), ("S", 0)], 1, 0) == apply_metadata(meta, 1, 0), "global phase kept")
    need(literal([("X", 0), ("S", 0)], 1, 0) != apply_metadata(meta, 1, 0, keep_c=False), "dropping c caught")
    return words


def check_binding():
    raw = SPEC.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SPEC_SHA256, "vendored COST-THEOREMS.md bytes")
    text = raw.decode("utf-8")
    for s in ("8 N L + 40 N + 8", "T = sum_(j=0)^(r-1) (N/2^j - 1) = 2N - r - 2,", "8 N L + 9 N + 11 T + 3",
              "d = (a_j + 2 g_j) mod 4.", "q=0: (u,v); q=1: (-v,u); q=2: (-u,-v); q=3: (v,-u).",
              "literal_word |x> = i^(c+q(x)) |A x XOR b>.", "b_j*v_l XOR b_k*u_l XOR u_l*v_l;",
              "u_l*v_t XOR u_t*v_l.", "2*b_j to c and 2*u_l to a_l"):
        need(s in text, f"COST-THEOREMS.md states: {s!r}")
    return 9


def t1_rejection_control(rng):
    """Replacing the carry-chain XOR by ADD breaks the affine invariant and must be caught."""
    bad = [("ADD", "Y", "Y", "C") if ins == ("XOR", "Y", "Y", "C") else ins for ins in AFFINE]
    need(bad != AFFINE, "mutation applied")
    try:
        check_t1(rng, bad)
    except AssertionError:
        return True
    raise AssertionError("mutated program accepted")


def main():
    rng = random.Random(4538)
    t1_cases, t1_worst = check_t1(rng)
    t1_control = t1_rejection_control(random.Random(1))
    report = {"status": "PASS_PR4538_COST_THEOREMS_CHECK",
              "t1_affine_programs_run": t1_cases, "t1_worst_cost_over_bound": t1_worst,
              "t1_rejection_control_caught": t1_control,
              "t2_streamed_phases": check_t2(rng), "t3_negation_and_unit_cases": check_t3(rng),
              "t4_random_words_all_basis_states": check_t4(rng), "spec_statements_bound": check_binding(),
              "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
