#!/usr/bin/env python3
"""Verify the eight-transfer threshold package (standard library only).

Default mode:
  * reproduces the predecessor's 945-path one-connector histogram;
  * expands two eight-transfer skeletons into complete paired-readout words
    and replays them in the free noncommutative F2 algebra and on dense
    random F2 matrices with arbitrary dirty rows;
  * rejects mutation controls (each dropped call, wrong port, wrong phase).

--native additionally compiles both C censuses with the system C compiler
and replays the four- and six-transfer censuses, which must agree exactly
with each other and with EXPECTED.json.  Without a compiler it fails.
--native-eight replays the recorded eight-transfer census (seven processes,
roughly ten CPU-minutes per method); it is not part of the registered hook.

Apache-2.0.  Prepared with substantial Claude Code (Anthropic) assistance.
"""
from __future__ import annotations

import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = json.loads((HERE / "EXPECTED.json").read_text())
PREDECESSOR = HERE.parent / "universal-connector-boundary" / "CERTIFICATE.json"
SOURCES = 5
MASKS = list(range(1, 1 << SOURCES))


class Fail(Exception):
    pass


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise Fail(msg)


# ---------------------------------------------------------------- old census
def canonical_words(n_labels: int):
    out = []

    def rec(word, counts, used):
        if len(word) == 2 * n_labels:
            out.append(tuple(word))
            return
        for lab in range(min(used + 1, n_labels)):
            if counts[lab] < 2:
                counts[lab] += 1
                word.append(lab)
                rec(word, counts, max(used, lab + 1))
                word.pop()
                counts[lab] -= 1

    rec([], [0] * n_labels, 0)
    return out


def old_census():
    hist = {}
    for w in canonical_words(SOURCES):
        q, prefixes = 0, {0}
        for lab in w:
            q ^= 1 << lab
            prefixes.add(q)
        size = len({a ^ b for a in prefixes for b in prefixes})
        hist[size] = hist.get(size, 0) + 1
    return hist


# ----------------------------------------------------- skeleton -> full word
def parse(skeleton):
    events = []
    for tok in skeleton:
        if tok == "C":
            events.append(("C",))
        else:
            src, port = tok[1:].split("@z")
            events.append(("B", int(src), int(port)))
    return events


def cut_values(events):
    """Formal (dirt, source) values of z0 and z1 at every cut 0..len."""
    z = [(1, 0), (2, 0)]  # dirt bits e0=1, e1=2; source bits b_j=1<<j
    cuts = [tuple(z)]
    for ev in events:
        if ev[0] == "C":
            z[0] = (z[0][0] ^ z[1][0], z[0][1] ^ z[1][1])
        else:
            _, j, p = ev
            z[p] = (z[p][0], z[p][1] ^ (1 << j))
        cuts.append(tuple(z))
    return cuts


def plan_readouts(events):
    """Pick, for each nonzero mask, two dirt-equal readout cuts on one row."""
    cuts = cut_values(events)
    slots = [(t, row) for t in range(len(cuts)) for row in (0, 1)]
    plan = {}
    for (t1, r1), (t2, r2) in combinations(slots, 2):
        d1, s1 = cuts[t1][r1]
        d2, s2 = cuts[t2][r2]
        m = s1 ^ s2
        if d1 == d2 and m and m not in plan:
            plan[m] = ((t1, r1), (t2, r2))
    return plan


def full_word(events, plan):
    """Interleave A_m(row) readouts at their cuts with the B/C skeleton."""
    at = {}
    for m, pair in sorted(plan.items()):
        for t, row in pair:
            at.setdefault(t, []).append(("A", m, row))
    word = []
    for t in range(len(events) + 1):
        word.extend(at.get(t, []))
        if t < len(events):
            word.append(events[t])
    return word


# --------------------------------------------------- free algebra replay
def free_replay(word):
    """Rows are F2 sums of monomials (operator strings applied to symbols)."""
    rows = {("x", j): {(f"x{j}",)} for j in range(SOURCES)}
    rows.update({("y", m): {(f"y{m}",)} for m in MASKS})
    rows[("z", 0)] = {("z0",)}
    rows[("z", 1)] = {("z1",)}
    for ev in word:
        if ev[0] == "B":
            _, j, p = ev
            rows[("z", p)] ^= {(f"B{j}", f"x{j}")}
        elif ev[0] == "C":
            rows[("z", 0)] ^= set(rows[("z", 1)])
        else:
            _, m, p = ev
            rows[("y", m)] ^= {(f"A{m}",) + mono for mono in rows[("z", p)]}
    ok = rows[("z", 0)] == {("z0",)} and rows[("z", 1)] == {("z1",)}
    ok &= all(rows[("x", j)] == {(f"x{j}",)} for j in range(SOURCES))
    for m in MASKS:
        want = {(f"y{m}",)} | {(f"A{m}", f"B{j}", f"x{j}") for j in range(SOURCES) if m >> j & 1}
        ok &= rows[("y", m)] == want
    return ok


# ------------------------------------------------------ dense F2 replay
def mat(rng, r, c):
    return [[rng.randrange(2) for _ in range(c)] for _ in range(r)]


def mul(a, v):
    return [sum(x & y for x, y in zip(row, v)) & 1 for row in a]


def xor(u, v):
    return [a ^ b for a, b in zip(u, v)]


def dense_replay(word, rng, zl=3, trials=4):
    """Random noncommuting maps of mixed widths; arbitrary dirty rows."""
    xl = [1 + (j % 3) for j in range(SOURCES)]
    yl = [1 + (m % 2) for m in range(1 << SOURCES)]
    B = [mat(rng, zl, xl[j]) for j in range(SOURCES)]
    A = {m: mat(rng, yl[m], zl) for m in MASKS}
    for _ in range(trials):
        x = [[rng.randrange(2) for _ in range(xl[j])] for j in range(SOURCES)]
        y = {m: [rng.randrange(2) for _ in range(yl[m])] for m in MASKS}
        z = [[rng.randrange(2) for _ in range(zl)] for _ in range(2)]
        x0, y0, zz = [r[:] for r in x], {m: r[:] for m, r in y.items()}, [r[:] for r in z]
        for ev in word:
            if ev[0] == "B":
                z[ev[2]] = xor(z[ev[2]], mul(B[ev[1]], x[ev[1]]))
            elif ev[0] == "C":
                z[0] = xor(z[0], z[1])
            else:
                y[ev[1]] = xor(y[ev[1]], mul(A[ev[1]], z[ev[2]]))
        if z != zz or x != x0:
            return False
        for m in MASKS:
            want = y0[m]
            for j in range(SOURCES):
                if m >> j & 1:
                    want = xor(want, mul(A[m], mul(B[j], x0[j])))
            if y[m] != want:
                return False
    return True


def check_witness(name, spec):
    events = parse(spec["skeleton"])
    need(sum(e[0] == "C" for e in events) == spec["transfers"], f"{name}: transfer count")
    counts = {}
    for e in events:
        if e[0] == "B":
            counts[e[1]] = counts.get(e[1], 0) + 1
    need(counts == {j: 2 for j in range(SOURCES)}, f"{name}: each B exactly twice")
    plan = plan_readouts(events)
    need(sorted(plan) == MASKS, f"{name}: paired readouts cover {len(plan)} masks")
    word = full_word(events, plan)
    need(len(word) == 10 + spec["transfers"] + 62, f"{name}: word length {len(word)}")
    need(free_replay(word), f"{name}: free-algebra replay")
    need(dense_replay(word, random.Random(spec["transfers"] * 1009 + len(name))), f"{name}: dense replay")
    rendered = [
        "C" if e[0] == "C" else (f"B{e[1]}@z{e[2]}" if e[0] == "B" else f"A{e[1]}@z{e[2]}")
        for e in word
    ]
    need(rendered == spec["complete_word"], f"{name}: complete word differs from EXPECTED")

    # Mutation controls: every single deletion must fail.
    rejected = 0
    for i in range(len(word)):
        mutant = word[:i] + word[i + 1:]
        need(not free_replay(mutant), f"{name}: deletion {i} accepted")
        rejected += 1
    # Wrong port for every B, C-free relabelling is illegal; wrong row for A.
    for i, e in enumerate(word):
        if e[0] in ("A", "B"):
            mutant = list(word)
            mutant[i] = (e[0], e[1], 1 - e[2])
            need(not free_replay(mutant), f"{name}: port flip {i} accepted")
            rejected += 1
    # Moving any readout across one transfer changes its dirt phase.
    for i, e in enumerate(word):
        if e[0] == "A" and e[2] == 0:
            j = i + 1
            while j < len(word) and word[j][0] != "C":
                j += 1
            if j < len(word):
                mutant = word[:i] + word[i + 1:j + 1] + [e] + word[j + 1:]
                need(not free_replay(mutant), f"{name}: phase move {i} accepted")
                rejected += 1
    return len(word), rejected


# ---------------------------------------------------------------- native
def compile_censuses(tmp):
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    need(cc is not None, "native replay needs a C compiler (cc/gcc/clang)")
    bins = {}
    for name in ("census_prefix", "census_literal"):
        out = os.path.join(tmp, name)
        subprocess.run([cc, "-O2", "-std=c99", "-o", out, str(HERE / "native" / f"{name}.c")], check=True)
        bins[name] = out
    return bins


def native_eight():
    """Optional long replay of the recorded eight-transfer census."""
    exp = EXPECTED["recorded_T8"]
    with tempfile.TemporaryDirectory() as tmp:
        bins = compile_censuses(tmp)
        procs = [subprocess.Popen([bins["census_prefix"], "8"], stdout=subprocess.PIPE, text=True)]
        procs += [subprocess.Popen([bins["census_literal"], "8", str(r)], stdout=subprocess.PIPE, text=True)
                  for r in range(6)]
        outs = []
        for proc in procs:
            out, _ = proc.communicate()
            need(proc.returncode == 0, "native eight-transfer census failed")
            outs.append(json.loads(out))
    a, parts = outs[0], outs[1:]
    b_hist = {k: v for part in parts for k, v in part["histograms"].items()}
    b_univ = {k: v for part in parts for k, v in part["universal"].items()}
    need(sum(part["orbits"] for part in parts) == a["orbits"] == exp["orbits"], "T=8 orbit count")
    need(sum(part["restored"] for part in parts) == a["restored"] == exp["restored"], "T=8 restored count")
    need(a["histograms"] == b_hist == exp["histograms"], "T=8 histograms")
    need(a["universal"] == b_univ == exp["universal"], "T=8 universal counts")
    return sum(a["universal"].values())


def native():
    results = {}
    with tempfile.TemporaryDirectory() as tmp:
        bins = compile_censuses(tmp)
        for t in ("4", "6"):
            a = json.loads(subprocess.run([bins["census_prefix"], t], check=True, capture_output=True, text=True).stdout)
            b = json.loads(subprocess.run([bins["census_literal"], t], check=True, capture_output=True, text=True).stdout)
            exp = EXPECTED["census"][t]
            for res in (a, b):
                need(res["orbits"] == exp["orbits"], f"T={t} {res['method']} orbit count")
                need(res["restored"] == exp["restored"], f"T={t} {res['method']} restored count")
                need(res["histograms"] == exp["histograms"], f"T={t} {res['method']} histogram")
                need(res["universal"] == exp["universal"], f"T={t} {res['method']} universal count")
            results[t] = max(int(c) for h in a["histograms"].values() for c in h)
    return results


def main(argv):
    need(set(argv) <= {"--native", "--native-eight"}, "usage: verify.py [--native] [--native-eight]")
    hist = old_census()
    pinned = [c for c in json.loads(PREDECESSOR.read_text())["censuses"] if c["sources"] == SOURCES]
    need(len(pinned) == 1 and pinned[0]["pairings"] == 945, "predecessor five-source census missing")
    need(hist == {int(k): v for k, v in pinned[0]["histogram"].items()}, f"old census {hist}")
    need(max(hist) == 31 and pinned[0]["max_coverage"] == 31, "old census maximum")
    words = rejected = 0
    for name, spec in EXPECTED["witnesses"].items():
        n, r = check_witness(name, spec)
        words += n
        rejected += r
    # Arithmetic of the orbit counts used by the native censuses.
    from math import comb, factorial
    pairings = factorial(10) // (2 ** 5 * factorial(5))
    need(pairings == 945, "945 pairings")
    for t, exp in EXPECTED["census"].items():
        need(exp["orbits"] == pairings * 32 * comb(10 + int(t), int(t)), f"T={t} orbit arithmetic")
        need(all(v == 0 for v in exp["universal"].values()), f"T={t} expected no universal schedule")
    t8 = EXPECTED["recorded_T8"]
    need(t8["orbits"] == pairings * 32 * comb(18, 8), "T=8 orbit arithmetic")
    need(sum(t8["universal"].values()) > 0, "T=8 records universal schedules")
    msg = (f"PASS_TWO_CONNECTOR_EIGHT_TRANSFER witnesses={len(EXPECTED['witnesses'])} "
           f"calls={words} controls={rejected} old945=max31")
    if "--native" in argv:
        mx = native()
        msg += f" native_T4_max={mx['4']} native_T6_max={mx['6']} censuses=agree"
    if "--native-eight" in argv:
        msg += f" native_T8_universal={native_eight()}"
    print(msg)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Fail as exc:
        print(f"FAIL_TWO_CONNECTOR_EIGHT_TRANSFER: {exc}")
        sys.exit(1)
