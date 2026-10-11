"""Negative controls for the relaxed checker (relax.py) and the interface audit (interface.py) on a mutable-source word.
usage: mutate_mut.py WORD.json.gz RELAXED_CHECKER PRICING_DIR INTERFACE_PY

Part 1: PR #370's six word-level mutants (same edits as PR #370's mutate.py), run against the relaxed checker.
Part 2: mutants aimed at the mutable-source interface; each must be rejected by the relaxed checker:
  - drop a source cleanup gate (a C gate whose destination is a source register);
  - corrupt a source's packet: cancel the last A gate into a Q-delivery source register and insert the matching inverse
    into C, so the cleanup still inverts the changed source transform exactly and every source is restored, but the
    packet that the targets read in B is wrong;
  - leave a source unrestored: delete every C gate whose destination is that source register;
  - move a source-destination A gate down to the source's own line frame (frame nesting);
  - drop a source-destination A gate.
Part 3: hypothesis controls for interface.py (PR #425's lemma): F2-neutral, frame-legal edits that the relaxed checker
  accepts (the linear map is unchanged) but that break the lemma's hypothesis "no target feeds a z register";
  interface.py must reject each:
  - a target feeds a source register (two identical gates x_a += y_t, which cancel over F2);
  - a target feeds a helper register (two identical gates h += y_t).
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import copy
import gzip
import json
import os
import subprocess
import sys
import tempfile

src, checker, pricing, iface = sys.argv[1:5]
c = json.load(gzip.open(src, "rt"))
v = c["v"]
FULLF = c["final"][0]


def run(cmd_word, script, extra):
    tmp = os.path.join(tempfile.mkdtemp(), "mut.json.gz")
    with gzip.open(tmp, "wt") as fh:
        json.dump(cmd_word, fh)
    r = subprocess.run([sys.executable, "-I", "-B", script, tmp] + extra, capture_output=True, text=True)
    last = (r.stderr.strip().splitlines() or r.stdout.strip().splitlines() or ["?"])[-1][:110]
    return r.returncode != 0, last


# ---------------- part 1: PR #370's six word-level mutants (verbatim edits)
def m1(c):
    c["B"].pop(len(c["B"]) // 2); return "drop a phase-B gate"
def m2(c):
    g = c["B"][-1]; g[0] = c["final"][0]; return "phase-B gate at the full frame (y beyond its cap)"
def m3(c):
    c["D"][0][2].pop(); return "drop a dirt compensation read"
def m4(c):
    c["C"].pop(10); return "drop a cleanup gate"
def m5(c):
    c["scatter"][5] = c["scatter"][5][1:]; return "wrong scatter row"
def m6(c):
    for g in c["A"]:
        if len(c["frames"][g[0]]) > 3:
            g[0] = c["start"][0]; break
    return "phase-A gate frame not nested"


# ---------------- part 2: mutable-source interface mutants
QSRC = sorted({s for g in c["B"] for s in g[2] if s < v})          # source registers read by targets (Q-deliveries)
assert QSRC, "no source register is read in phase B"
XA = QSRC[0]
ZGATES = [("A", i) for i, g in enumerate(c["A"]) if not (v <= g[1] < 2 * v)] + \
         [("B", i) for i, g in enumerate(c["B"]) if not (v <= g[1] < 2 * v)]


def last_write(c, r):
    return max(i for i, g in enumerate(c["A"]) if g[1] == r)


def n1(c):
    i = next(i for i, g in enumerate(c["C"]) if g[1] < v)
    c["C"].pop(i); return "drop a source cleanup gate (C gate with a source destination)"


def n2(c):
    i = last_write(c, XA); F, d, srcs = c["A"][i]
    assert len(srcs) == 1
    c["A"].insert(i + 1, [F, d, list(srcs)])                         # cancels the last write into the packet register
    p = len(ZGATES) - 1 - ZGATES.index(("A", i))                      # C position of that gate's literal inverse
    assert c["C"][p] == [FULLF, d, srcs]
    c["C"].insert(p, [FULLF, d, list(srcs)])                          # inverse of the inserted gate: cleanup stays exact
    return "corrupt a source packet read by targets (cleanup adjusted, so every source is still restored)"


def n3(c):
    c["C"] = [g for g in c["C"] if g[1] != XA]
    return "leave a source unrestored (delete every cleanup gate into source register %d)" % XA


def n4(c):
    for g in c["A"]:
        if g[1] < v:
            g[0] = c["start"][g[1]]; return "source-destination A gate moved down to the source's line frame"
    raise SystemExit("no source-destination A gate")


def n5(c):
    i = next(i for i, g in enumerate(c["A"]) if g[1] < v)
    c["A"].pop(i); return "drop a phase-A gate whose destination is a source"


# ---------------- part 3: hypothesis controls for interface.py (F2-neutral)
def h1(c):
    j = next(j for j, g in enumerate(c["B"]) if XA in g[2])
    F, t = c["B"][j][0], c["B"][j][1]
    c["B"][j:j] = [[F, XA, [t]], [F, XA, [t]]]                        # x_a += y_t twice: identity over F2
    return "a target feeds a source register (cancelled pair, F2-neutral)"


def h2(c):
    j = next(j for j, g in enumerate(c["B"]) if any(s >= 2 * v for s in g[2]))
    F, t = c["B"][j][0], c["B"][j][1]
    hreg = next(s for s in c["B"][j][2] if s >= 2 * v)
    c["B"][j:j] = [[F, hreg, [t]], [F, hreg, [t]]]                    # helper += y_t twice: identity over F2
    return "a target feeds a helper register (cancelled pair, F2-neutral)"


ok = True
for f in (m1, m2, m3, m4, m5, m6, n1, n2, n3, n4, n5):
    cc = copy.deepcopy(c); name = f(cc)
    rej, msg = run(cc, checker, [pricing])
    ok &= rej
    print(("   REJECTED  " if rej else "   ACCEPTED!! ") + name + " :: " + msg)
assert ok, "a mutant was accepted by the relaxed checker"
print("PASS relaxed checker: PR #370's 6 word-level mutants and 5 mutable-source mutants rejected")
for f in (h1, h2):
    cc = copy.deepcopy(c); name = f(cc)
    acc_rej, msg1 = run(cc, checker, [pricing])
    rej, msg2 = run(cc, iface, [])
    print("   %s by the relaxed checker (F2 map unchanged); %s by interface.py :: %s" %
          ("accepted" if not acc_rej else "REJECTED", "REJECTED" if rej else "ACCEPTED!!", msg2))
    ok &= rej
assert ok, "an interface hypothesis control was accepted by interface.py"
print("PASS interface.py: 2 hypothesis controls rejected")
