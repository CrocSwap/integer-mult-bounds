#!/usr/bin/env python3
"""Exact instance binding for the post-wrapper uniqueness lemma (HPE interface).

Reads the literal circuits of the pinned input
research/hyperplane-end-lean/HyperplaneEnd/Exact.lean and, with an independently
written exact gate semantics over Z[i] (integer semantics, the 1/2 of each C gate
carried as an explicit denominator 2^#C), checks on the three certified (E, U) pairs
of HyperplaneEnd.Exact:

  ports        : adj/inv/composition conventions reproduce the kernel literals
                 (lhsLit = adjC(fE) ++ fU, rhsLit = wR ++ fourierC 7 ++ wL,
                  Mono.gates(pair.L/R) = wL/wR with our own GF(2) inverse);
  positive     : L^-1 T_U T_E^-1 R^-1 = C7 (x) id  exactly, phase included;
  width guard  : the identity fails against C8 (x) id (wrong residual width);
  lemma        : for every declared one-field post-wrapper mutant L' and every
                 k in 0..3, L'^-1 T_U T_E^-1 R^-1 = i^k (C7 (x) id) holds only
                 when L' = i^t L with k = -t mod 4 (phase sharpness), and never
                 for a non-phase mutant;
  failure ctl  : a corrupted wrapper literal must be rejected (mutant suite).

usage: python3 -B research/hpe-post-wrapper-lemma/verify.py [--write-result PATH]
Python 3.10+, standard library only.  Apache-2.0.
"""
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEAN = ROOT / "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean"
N = 512  # 2^9 basis states

BRACKETS = {0x27E8: "[", 0x27E9: "]", 0x2329: "[", 0x232A: "]", 0x00AB: "[",
            0x00BB: "]", 0x2039: "[", 0x203A: "]", 0xFF08: "(", 0xFF09: ")"}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def translated(text):
    return "".join(BRACKETS.get(ord(ch), ch) for ch in text)


def bracket_block(text, start):
    """Return the [...] block starting at the first '[' at or after start."""
    i = text.index("[", start)
    depth = 0
    for j in range(i, len(text)):
        if text[j] == "[":
            depth += 1
        elif text[j] == "]":
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    raise ValueError("unterminated bracket block")


def parse_gate_block(block):
    """Parse `.dg Q Iv | .pm G Gi | .cg q s | .xg b | .ph p` into tuples."""
    gates = []
    for m in re.finditer(r"\.(dg|pm|cg|xg|ph)\b", block):
        kind = m.group(1)
        pos = m.end()
        args = []
        if kind in ("dg", "pm"):
            for _ in range(2):
                start = block.index("[", pos)
                arg = bracket_block(block, pos)
                args.append(ast.literal_eval(arg))
                pos = start + len(arg)
        elif kind == "cg":
            m2 = re.match(r"\s*(\d+)\s+(true|false)", block[pos:])
            need(m2 is not None, "bad cg gate")
            args = [int(m2.group(1)), m2.group(2) == "true"]
        elif kind == "xg":
            m2 = re.match(r"\s*(\d+)", block[pos:])
            need(m2 is not None, "bad xg gate")
            args = [int(m2.group(1))]
        else:
            m2 = re.match(r"\s*(\d+)", block[pos:])
            need(m2 is not None, "bad ph gate")
            args = [int(m2.group(1))]
        gates.append(tuple([kind] + args))
    return gates


def parse_defs(text):
    """Extract the literal gate lists and pair monomials from Exact.lean."""
    text = translated(text)
    out = {}
    for name in ("fE1", "fU1", "fE2", "fU2", "fE3", "fU3",
                 "wL1", "wR1", "wL2", "wR2", "wL3", "wR3",
                 "lhsLit1", "rhsLit1", "lhsLit2", "rhsLit2", "lhsLit3", "rhsLit3"):
        m = re.search(r"def " + name + r" : List Gate :=", text)
        need(m is not None, "missing literal " + name)
        out[name] = parse_gate_block(bracket_block(text, m.end()))
    for n in (1, 2, 3):
        m = re.search(r"def pair" + str(n) + r" : Pair :=", text)
        need(m is not None, "missing literal pair%d" % n)
        data = ast.literal_eval(bracket_block(text, m.end()))
        need(len(data) == 4, "pair%d shape" % n)
        out["pair%d" % n] = data  # [E, U, [Q,Iv,G,b,p], [Q,Iv,G,b,p]]
    return out


# ---- exact bit arithmetic (ports of the documented semantics) ----

def mv(rows, x):
    y = 0
    for i, r in enumerate(rows):
        if bin(r & x).count("1") & 1:
            y |= 1 << i
    return y


def qv(q_rows, alpha, x):
    s = 0
    for i in range(len(q_rows)):
        if (x >> i) & 1:
            s += alpha[i] + 2 * (bin((q_rows[i] >> (i + 1)) & (x >> (i + 1))).count("1") & 1)
    return s % 4


def inv_rows(rows, n):
    """GF(2) inverse of the matrix with the given rows (unique)."""
    aug = [[rows[i] if i < len(rows) else 0, 1 << i] for i in range(n)]
    for col in range(n):
        piv = None
        for i in range(col, n):
            if (aug[i][0] >> col) & 1:
                piv = i
                break
        need(piv is not None, "singular matrix")
        aug[col], aug[piv] = aug[piv], aug[col]
        for i in range(n):
            if i != col and (aug[i][0] >> col) & 1:
                aug[i][0] ^= aug[col][0]
                aug[i][1] ^= aug[col][1]
    return [aug[i][1] for i in range(n)]


def mono_gates(mono):
    q_rows, alpha, g, b, p = mono
    return [("dg", q_rows, alpha), ("pm", g, inv_rows(g, 9)), ("xg", b), ("ph", p)]


def adj(g):
    kind = g[0]
    if kind == "pm":
        return ("pm", g[2], g[1])
    if kind == "dg":
        return ("dg", g[1], [(4 - a % 4) % 4 for a in g[2]])
    if kind == "cg":
        return ("cg", g[1], not g[2])
    if kind == "xg":
        return g
    return ("ph", (4 - g[1] % 4) % 4)


def adj_c(circ):
    return [adj(g) for g in reversed(circ)]


def fourier_c(r):
    return [("cg", 1 << i, True) for i in range(r)]


# ---- integer semantics over Z[i] (C gates without their 1/2) ----

def ipow(k, a, b):
    k %= 4
    if k == 0:
        return a, b
    if k == 1:
        return -b, a
    if k == 2:
        return -a, -b
    return b, -a


def apply_circuit(circ, re, im):
    for g in circ:
        kind = g[0]
        if kind == "pm":
            nre, nim = [0] * N, [0] * N
            for y in range(N):
                s = mv(g[2], y)
                nre[y], nim[y] = re[s], im[s]
            re, im = nre, nim
        elif kind == "dg":
            for x in range(N):
                re[x], im[x] = ipow(qv(g[1], g[2], x), re[x], im[x])
        elif kind == "cg":
            q, s = g[1], g[2]
            nre, nim = [0] * N, [0] * N
            for x in range(N):
                a, b = re[x], im[x]
                c, d = re[x ^ q], im[x ^ q]
                if s:
                    nre[x] = (a - b) + (c + d)
                    nim[x] = (a + b) + (-c + d)
                else:
                    nre[x] = (a + b) + (c - d)
                    nim[x] = (-a + b) + (c + d)
            re, im = nre, nim
        elif kind == "xg":
            bit = g[1]
            nre, nim = [0] * N, [0] * N
            for x in range(N):
                nre[x], nim[x] = re[x ^ bit], im[x ^ bit]
            re, im = nre, nim
        else:
            for x in range(N):
                re[x], im[x] = ipow(g[1], re[x], im[x])
    return re, im


def packed(circ, base):
    re = [0] * N
    im = [0] * N
    power = 1
    for x in range(N):
        re[x] = power
        power *= base
    return apply_circuit(circ, re, im)


def ncg(circ):
    return sum(1 for g in circ if g[0] == "cg")


def signed_digits(value, base, count):
    digits = []
    for _ in range(count):
        t = value % base
        if t > base // 2:
            t -= base
        digits.append(t)
        value = (value - t) // base
    need(value == 0, "packed value exceeds digit budget")
    return digits


def map_equal(circ_a, circ_b):
    """Exact equality of the two circuits as C-linear maps (1/2 per C gate).

    Returns None when equal, else a witness (row, column, entry_a, entry_b).
    """
    ca, cb = ncg(circ_a), ncg(circ_b)
    da, db = 1 << ca, 1 << cb
    expo = max(cb + 2 * ca, ca + 2 * cb)
    base = 1 << (expo + 3)  # signed digits |d| <= 2^expo < base/2
    re_a, im_a = packed(circ_a, base)
    re_b, im_b = packed(circ_b, base)
    for x in range(N):
        if re_a[x] * db != re_b[x] * da or im_a[x] * db != im_b[x] * da:
            dre_a = signed_digits(re_a[x] * db, base, N)
            dim_a = signed_digits(im_a[x] * db, base, N)
            dre_b = signed_digits(re_b[x] * db, base, N)
            dim_b = signed_digits(im_b[x] * db, base, N)
            for y in range(N):
                if (dre_a[y], dim_a[y]) != (dre_b[y], dim_b[y]):
                    return (x, y, [dre_a[y], dim_a[y]], [dre_b[y], dim_b[y]])
            need(False, "row differs but no column witness decodes")
    return None


def phase_mul(circ, k):
    """circ followed by a global phase i^k (kept as an extra gate)."""
    return list(circ) + [("ph", k % 4)]


def post_id(pair, post_mono):
    """Circuit of L'^-1 T_U T_E^-1 R'^-1 for the pair's literals."""
    _, _, left, right = pair
    return (adj_c(mono_gates(right)) + adj_c(pair_fE) + pair_fU
            + adj_c(mono_gates(post_mono)))


def main():
    args = sys.argv[1:]
    write = None
    if "--write-result" in args:
        write = Path(args[args.index("--write-result") + 1])
    text = LEAN.read_text(encoding="utf-8")
    d = parse_defs(text)
    if "--self-test" in args:
        # failure control: a corrupted wrapper literal must fail the pipeline
        bad = list(d["wL1"])
        bad[3] = ("ph", (bad[3][1] + 1) % 4)
        d["wL1"] = bad
        d["pair1"][2][4] = (d["pair1"][2][4] + 1) % 4
        try:
            run(d)
        except ValueError as exc:
            print("PASS_SELF_TEST corrupted literal rejected: " + str(exc))
            return
        need(False, "self-test: corrupted wrapper literal was accepted")
    run(d, write)


def run(d, write=None):
    controls = []
    result_pairs = []
    global pair_fE, pair_fU

    for n in (1, 2, 3):
        pair = d["pair%d" % n]
        e_rows, u_rows, left, right = pair
        fE, fU = d["fE%d" % n], d["fU%d" % n]
        wL, wR = d["wL%d" % n], d["wR%d" % n]
        pair_fE, pair_fU = fE, fU

        # port controls: the kernel literals must match our conventions
        need(adj_c(fE) + fU == d["lhsLit%d" % n], "pair%d: adj convention differs from lhsLit" % n)
        need(wR + fourier_c(7) + wL == d["rhsLit%d" % n], "pair%d: composition differs from rhsLit" % n)
        need(mono_gates(left) == wL, "pair%d: our GF(2) inverse/Mono port differs from wL" % n)
        need(mono_gates(right) == wR, "pair%d: our GF(2) inverse/Mono port differs from wR" % n)
        for rows, gi in ((wL[1][1], wL[1][2]), (wR[1][1], wR[1][2])):
            for x in range(N):
                need(mv(rows, mv(gi, x)) == x and mv(gi, mv(rows, x)) == x,
                     "pair%d: pm matrices are not mutual inverses" % n)
        controls.append("pair%d: adj/inverse/composition ports reproduce the kernel literals" % n)

        # positive fixture: the shipped post wrapper satisfies the identity exactly
        lhs = post_id(pair, left)
        c7 = fourier_c(7)
        witness = map_equal(lhs, c7)
        need(witness is None, "pair%d: shipped post wrapper fails the identity" % n)
        # width guard: C8 must not satisfy the identity
        need(map_equal(lhs, fourier_c(8)) is not None,
             "pair%d: identity wrongly holds against C8" % n)

        # smallest falsifying instance first, then the declared mutant family.
        # mode: "phase" = i^t L (lambda sharpness), "reject" = must break every
        # lambda form, "equal" = record-only change that must NOT change the map
        # (qv reads Q_i only through bits above i, so bit 0 of Q_0 is dead data).
        q_rows, alpha, g, b, p = left
        mutants = [
            ("phase+1", [q_rows, alpha, g, b, p + 1], "phase", 3),
            ("phase-1", [q_rows, alpha, g, b, p - 1], "phase", 1),
            ("phase+2", [q_rows, alpha, g, b, p + 2], "phase", 2),
            ("offset-xor-1", [q_rows, alpha, g, b ^ 1, p], "reject", None),
            ("linear-Z4-flip", [q_rows, [alpha[0] ^ 1] + alpha[1:], g, b, p], "reject", None),
            ("quadratic-live-bit", [[q_rows[0] ^ 2] + q_rows[1:], alpha, g, b, p], "reject", None),
            ("matrix-row-swap", [q_rows, alpha, [g[1], g[0]] + g[2:], b, p], "reject", None),
            ("swapped-L-R", right, "reject", None),
            ("quadratic-dead-bit", [[q_rows[0] ^ 1] + q_rows[1:], alpha, g, b, p], "equal", 0),
        ]
        mutant_rows = []
        for name, mono, mode, sharp_k in mutants:
            ks_ok = [k for k in range(4)
                     if map_equal(post_id(pair, mono), phase_mul(c7, k)) is None]
            if mode == "phase":
                need(ks_ok == [sharp_k],
                     "pair%d: phase mutant %s must hold only at k=%d, got %s" % (n, name, sharp_k, ks_ok))
            elif mode == "equal":
                need(ks_ok == [0],
                     "pair%d: inert mutant %s must keep the identity at k=0 only, got %s" % (n, name, ks_ok))
            else:
                need(ks_ok == [],
                     "pair%d: mutant %s must break every lambda form, got %s" % (n, name, ks_ok))
            w = map_equal(post_id(pair, mono), c7)
            if mode == "equal":
                need(w is None, "pair%d: mutant %s unexpectedly breaks lambda=1" % (n, name))
            else:
                need(w is not None, "pair%d: mutant %s not rejected at lambda=1" % (n, name))
            mutant_rows.append({"mutant": name, "mode": mode,
                                "lambda1_witness": w, "k_satisfying": ks_ok})
        result_pairs.append({"pair": n, "E": e_rows, "U": u_rows,
                             "positive": "exact", "width_guard_C8": "rejected",
                             "mutants": mutant_rows})
        print("pair%d: positive exact; C8 rejected; %d mutants classified with witnesses"
              % (n, len(mutant_rows)))
        sys.stdout.flush()

    status = "PASS_HPE_POST_WRAPPER_UNIQUENESS"
    print(status + " pairs=3 mutants_per_pair=9 controls=" + str(len(controls)))
    for line in controls:
        print("  control: " + line)
    if write is not None:
        payload = {
            "status": status,
            "lean_source": "research/hyperplane-end-lean/HyperplaneEnd/Exact.lean",
            "lean_source_sha256": hashlib.sha256(LEAN.read_bytes()).hexdigest(),
            "semantics": "documented five-gate semantics of HyperplaneEnd/Clifford.lean over Z[i]; C gates without their 1/2, denominators 2^#C compared exactly",
            "controls": controls,
            "pairs": result_pairs,
        }
        write.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n",
                         encoding="utf-8", newline="\n")
        print("wrote " + str(write))


if __name__ == "__main__":
    main()
