#!/usr/bin/env python3
"""Independent check of PR #4541 (Dugongue), packed Word RAM transfer: Section 1 parameters and Sections 2-3 macro steps.

Written from #4541's PROOF.md text only (vendored as PR4541-PROOF.md); nothing is imported from its code. Checks:
  A. Section 1 parameter arithmetic, exactly, over k<=8, c in {2,4,8}, s<=10, lambda<=3000:
     16b <= lambda above the cutoff lambda >= max(64Kc, 64s); 128Kc*r >= lambda; L <= B; codec exponent cr < b;
     plus the Section 2 origin bound T+n+m+16 <= 2^(a-4)(n+2)^d  =>  every coordinate H+z with |z| <= T+r lies in
     (0, 2H), for a=8, d<=3 and all n < 2^12.
  B. Sections 2-3 by an independent packed simulator: B=4r fields of c bits per word with dirty high bits above the
     fields, tapes interleaved at dataBase+J*u+i, signed positions at origin H, windows of L=2r+1 cells read across at
     most two words, all reads before writes, a generated (lazily memoised) local table of up to r literal steps with
     invalid patterns treated as halt, and newHead = oldHead + localHead - r. Random k-tape machines are compared with
     direct execution: halting runs on state, transition count, heads and every tape cell; nonhalting runs on every
     macro-boundary prefix. Halts at an exact epoch boundary, block-crossing windows and negative coordinates are
     counted. A rejection control (writing the window back one cell off) must be detected.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
PROOF = HERE / "PR4541-PROOF.md"  # #4541 head 46ca24a8, research/packed-ram-speedup/PROOF.md, blob 43a6afbe
PROOF_SHA256 = "788535dea58df897055de81175acdea9abb149604ad9bdf7ee36b6100982d541"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def pow2_at_least(x):
    p = 1
    while p < x:
        p *= 2
    return p


def pow2_at_most(x):
    p = 1
    while 2 * p <= x:
        p *= 2
    return p


def params(k, c, s, lam):
    K = pow2_at_least(k)
    q = lam // (64 * K * c)
    r = pow2_at_most(max(1, q))
    return K, r, 4 * r, 2 * r + 1, s + k * c * (2 * r + 1)


def check_parameters():
    rows = 0
    for k in range(1, 9):
        for c in (2, 4, 8):
            for s in range(1, 11):
                for lam in range(0, 3001):
                    K, r, B, L, b = params(k, c, s, lam)
                    need(L <= B and c * r < b, "window fits two words; codec exponent below b")
                    if lam >= 1:
                        need(128 * K * c * r >= lam, "r >= lambda/(128Kc)")
                    if lam >= max(64 * K * c, 64 * s):
                        need(r >= 1 and 64 * k * c * r <= lam and 16 * b <= lam, "16b <= lambda")
                    rows += 1
    origins = 0
    for d in (1, 2, 3):
        a = 8
        for n in range(0, 1 << 12):
            ell = (n + 2).bit_length()  # floor(log2(n+2)) + 1
            H = 1 << (a + d * ell)
            envelope = (1 << (a - 4)) * (n + 2) ** d  # T+n+m+16 <= envelope, so T and r are below it
            need(H >= (1 << a) * (n + 2) ** d and 2 * envelope < H, "origin margin")
            origins += 1
    return rows, origins


class Packed:
    def __init__(self, k, c, r, H, rng):
        self.k, self.c, self.r, self.H = k, c, r, H
        self.B, self.L = 4 * r, 2 * r + 1
        self.lb = self.B.bit_length() - 1
        self.J = pow2_at_least(k)
        self.base = 1 << 20
        self.fieldbits = c * self.B
        self.mem = {}
        self.junk = {}
        self.rng = rng
        self.crossings = 0

    def word(self, addr):
        if addr not in self.mem:
            # Fields start blank (zero memory); high bits above the fields carry arbitrary dirty values.
            self.junk[addr] = self.rng.getrandbits(13) << self.fieldbits
            self.mem[addr] = self.junk[addr]
        return self.mem[addr]

    def addr(self, tape, u):
        return self.base + self.J * u + tape

    def read(self, tape, p0):
        u, a0 = p0 >> self.lb, p0 & (self.B - 1)
        avail = self.B - a0
        first = min(self.L, avail)
        win = (self.word(self.addr(tape, u)) >> (self.c * a0)) & ((1 << (self.c * first)) - 1)
        if self.L > avail:
            self.crossings += 1
            rest = self.L - avail
            win |= (self.word(self.addr(tape, u + 1)) & ((1 << (self.c * rest)) - 1)) << (self.c * avail)
        return win

    def write(self, tape, p0, win):
        u, a0 = p0 >> self.lb, p0 & (self.B - 1)
        avail = self.B - a0
        first = min(self.L, avail)
        m1 = ((1 << (self.c * first)) - 1) << (self.c * a0)
        a = self.addr(tape, u)
        self.mem[a] = (self.word(a) & ~m1) | ((win << (self.c * a0)) & m1)
        if self.L > avail:
            rest = self.L - avail
            m2 = (1 << (self.c * rest)) - 1
            a2 = self.addr(tape, u + 1)
            self.mem[a2] = (self.word(a2) & ~m2) | ((win >> (self.c * avail)) & m2)

    def cell(self, tape, p):
        u, f = p >> self.lb, p & (self.B - 1)
        return (self.word(self.addr(tape, u)) >> (self.c * f)) & ((1 << self.c) - 1)


def random_machine(rng, k, Q, sigma, p_missing):
    delta = {}

    def all_syms(i):
        if i == k:
            yield ()
            return
        for x in range(sigma):
            for rest in all_syms(i + 1):
                yield (x,) + rest

    for q in range(Q):
        for syms in all_syms(0):
            if rng.random() < p_missing:
                continue
            delta[(q, syms)] = (rng.randrange(Q), tuple(rng.randrange(sigma) for _ in range(k)),
                                tuple(rng.choice((-1, 0, 1)) for _ in range(k)))
    return delta


def direct(delta, k, inputs, max_steps):
    tapes = [dict(enumerate(inp)) for inp in inputs]
    heads, state, steps = [0] * k, 0, 0
    while steps < max_steps:
        key = (state, tuple(tapes[i].get(heads[i], 0) for i in range(k)))
        if key not in delta:
            return state, steps, heads, tapes, True
        state, writes, moves = delta[key]
        for i in range(k):
            tapes[i][heads[i]] = writes[i]
            heads[i] += moves[i]
        steps += 1
    return state, steps, heads, tapes, False


def make_table(delta, k, c, r, s, Q, sigma):
    L = 2 * r + 1
    table = {}

    def row(key):
        if key in table:
            return table[key]
        state = key & ((1 << s) - 1)
        wins = [[(key >> (s + i * c * L + c * j)) & ((1 << c) - 1) for j in range(L)] for i in range(k)]
        local = [r] * k
        elapsed, halted = 0, False
        while elapsed < r:
            syms = tuple(wins[i][local[i]] for i in range(k))
            if state >= Q or any(x >= sigma for x in syms) or (state, syms) not in delta:
                halted = True
                break
            state, writes, moves = delta[(state, syms)]
            for i in range(k):
                wins[i][local[i]] = writes[i]
                local[i] += moves[i]
                need(0 <= local[i] < L, "head stays inside its window")
            elapsed += 1
        packed = [sum(w[j] << (c * j) for j in range(L)) for w in wins]
        table[key] = (state, halted, elapsed, packed, local)
        return table[key]

    return row, table


def packed_run(delta, k, c, r, Q, sigma, inputs, max_macros, rng, skew=0):
    s = max(1, (Q - 1).bit_length())
    H = 1 << 16
    pk = Packed(k, c, r, H, rng)
    for i, inp in enumerate(inputs):
        for z, x in enumerate(inp):
            p = H + z
            u, f = p >> pk.lb, p & (pk.B - 1)
            a = pk.addr(i, u)
            pk.mem[a] = pk.word(a) | (x << (c * f))
    row, table = make_table(delta, k, c, r, s, Q, sigma)
    heads, state, steps = [H] * k, 0, 0
    prefixes = []
    for _ in range(max_macros):
        wins = [pk.read(i, heads[i] - r) for i in range(k)]  # every read before any write
        key = state | sum(wins[i] << (s + i * c * pk.L) for i in range(k))
        state, halted, elapsed, out, local = row(key)
        for i in range(k):
            pk.write(i, heads[i] - r + skew, out[i])
            heads[i] = heads[i] + local[i] - r
        steps += elapsed
        prefixes.append((state, steps, [h - H for h in heads]))
        if halted:
            return pk, state, steps, heads, True, prefixes, len(table)
    return pk, state, steps, heads, False, prefixes, len(table)


def compare(delta, k, c, r, Q, sigma, inputs, rng, skew=0):
    max_macros = 40
    pk, state, steps, heads, halted, prefixes, rows = packed_run(delta, k, c, r, Q, sigma, inputs, max_macros, rng, skew)
    ref = direct(delta, k, inputs, max_macros * r + 1)
    if halted:
        need(ref[4] and ref[0] == state and ref[1] == steps, "halting state and transition count")
        need([h - pk.H for h in heads] == ref[2], "halting heads")
    else:
        need(not ref[4] or ref[1] > (max_macros - 1) * r, "nonhalting prefix")
        # Prefix fidelity at every macro boundary: rerun directly to each boundary.
        for j, (st, sp, hd) in enumerate(prefixes):
            d = direct(delta, k, inputs, sp)
            need(d[0] == st and d[1] == sp and d[2] == hd, "macro-boundary prefix")
    cells = set()
    for i in range(k):
        cells |= {(i, z) for z in ref[3][i]}
    visited_lo = min([z for _, z in cells] + [h - pk.H for h in heads] + [0])
    lo = visited_lo - 2 * r
    hi = max([z for _, z in cells] + [h - pk.H for h in heads] + [0]) + 2 * r
    if halted:
        for i in range(k):
            for z in range(lo, hi + 1):
                need(pk.cell(i, pk.H + z) == ref[3][i].get(z, 0), "every tape cell")
    for a, v in pk.mem.items():
        need(v >> pk.fieldbits == pk.junk[a] >> pk.fieldbits, "dirty high bits preserved")
    boundary_halt = halted and steps > 0 and len(prefixes) >= 2 and prefixes[-1][1] == prefixes[-2][1]
    return halted, boundary_halt, visited_lo < 0, pk.crossings, rows


def check_simulator():
    rng = random.Random(4541)
    stats = {"runs": 0, "halting": 0, "nonhalting": 0, "epoch_boundary_halts": 0, "negative_coordinates": 0,
             "block_crossing_windows": 0, "table_rows_generated": 0}
    configs = [(k, Q, sigma, r) for k in (1, 2, 3) for Q in (2, 3, 5) for sigma in (2, 3, 4) for r in (1, 2, 4)]
    for k, Q, sigma, r in configs:
        for trial in range(6):
            delta = random_machine(rng, k, Q, sigma, rng.choice((0.02, 0.08, 0.25)))
            inputs = [[rng.randrange(1, sigma) for _ in range(rng.randrange(0, 9))] for _ in range(k)]
            halted, boundary_halt, neg, crossings, rows = compare(delta, k, 2, r, Q, sigma, inputs, rng)
            stats["runs"] += 1
            stats["halting" if halted else "nonhalting"] += 1
            stats["epoch_boundary_halts"] += int(boundary_halt and r > 1)
            stats["negative_coordinates"] += int(neg)
            stats["block_crossing_windows"] += crossings
            stats["table_rows_generated"] += rows
    need(min(stats["halting"], stats["nonhalting"], stats["epoch_boundary_halts"], stats["negative_coordinates"],
             stats["block_crossing_windows"]) > 0, "every edge case occurs")
    # Rejection control: writing each returned window one cell to the right must be caught.
    caught = 0
    for trial in range(20):
        delta = random_machine(rng, 2, 3, 3, 0.05)
        inputs = [[rng.randrange(1, 3) for _ in range(6)] for _ in range(2)]
        try:
            compare(delta, 2, 2, 2, 3, 3, inputs, rng, skew=1)
        except AssertionError:
            caught += 1
    need(caught >= 15, "rejection control detected")
    stats["rejection_control_caught"] = caught
    return stats


def check_binding():
    raw = PROOF.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PROOF_SHA256, "vendored #4541 PROOF.md bytes")
    text = raw.decode("utf-8")
    for line in ("q = floor(lambda/(64 K c));", "B = 4r;  L = 2r+1.", "b = s + kc(2r+1).", "16b <= 16s + 48kcr <= lambda.",
                 "H = 2^(a+d*ell).", "dataBase + J*u + i.", "newHead_i = oldHead_i + savedLocalHead_i - r.",
                 "T+n+m+16 <= 2^(a-4) (n+2)^d.", "r >= lambda/(128Kc) when lambda>=1"):
        need(line in text, f"#4541 states: {line}")
    return 9


def main():
    rows, origins = check_parameters()
    report = {"status": "PASS_PR4541_PACKED_TRANSFER_CHECK", "parameter_cases": rows, "origin_cases": origins,
              "proof_statements_bound": check_binding(),
              "simulator": check_simulator(), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
