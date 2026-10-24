#!/usr/bin/env python3
"""Independent check of PR #4626 (hexapode, head e4413c43): helper621 entrance/contact chart change.

Part A (native census, own code). From the frozen PR4610 checkpoint word (vendored, blob 79dad65b,
identical bytes to #4626's predecessor/ACTUAL-WORD.json.gz and to #4610 at 4b4c75bc), this script
  1. re-derives every paid climb with its own frame walker and requires the result to equal the shipped
     climb list (multiset) and the checkpoint census {1:2201,2:412,3:506,4:135,5:36,8:8} in both orientations;
  2. checks legality of #4626's patch: helper621 starts at ZERO and ends at FULL9, nothing (scalar, warp,
     climb, adapter, centre) touches L621 before event 12704 in either orientation, L514 sits at ZERO there,
     and A = span{30,429} is nested in, indeed equal to the intersection of, the frames of both roles'
     next contacts (797 and 4329);
  3. applies the patch (start[621] := A, frame of event 12704 := A), re-walks, and requires the new census
     {1:2202,2:414,3:505,4:134,5:36,8:8}, the exact climb difference
     -(514:0->797,r3) -(621:0->4329,r4) +(514:0->A,r2) +(514:A->797,r1) +(621:A->4329,r2), i.e.
     dP = H1 + 2H2 - H3 - H4, and an unchanged scalar opcode/coefficient sequence;
  4. computes all 408 relative helper ranks twice: by the nested-dimension count dim(final)-dim(start), and
     as the exact Clifford rank of C_final C_start^{-1} using main's shipped clifford_exact.py (evaluator
     only; nothing from #4626 is imported). Checkpoint census {4:28,7:7,8:47,9:326}; patched
     {4:28,7:8,8:47,9:325}, helper621 rank 9 -> 7. The five changed paid edges are also checked to have
     exact Clifford rank equal to their climb rank.
Part B (arithmetic, own code, 80-digit Decimal; correctly rounded exp/ln).
  5. whole histograms from main's pinned joint-helper-lattice/CONTROLLER.json (read as JSON, no import);
     equality with #4626's ARITHMETIC.json paid/targets, 64,422 paid calls, 10,928 fields, surplus 752;
  6. the whole-cost change 18(H1+2H2-H3-H4-H7+H9) at a=.00302156 versus #4626's PROOF interval, and
     the exponent at which the PR body's quoted value -0.00401665923 is attained;
  7. raw crossing by Newton iteration (not bisection) with endpoint sign checks at 0.0030215713 / ...714;
  8. kappa selection: tested=.00302157 < root, kappa = tested - 1e-9, alpha/gamma/delta strictification
     quotients against #4626's displayed digits, and the least compiler exponent 48,264 by exact integers.
Rejection controls: a non-nested chart, the entrance moved without its contact, a 1-dim chart, the old helper
credit, the PR4610 rule kappa, and a dropped idle charge must all fail the corresponding checks.

Prepared by lm1909 with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from collections import Counter
from decimal import Decimal as D, getcontext
from fractions import Fraction as Q
from hashlib import sha1, sha256
from pathlib import Path
import gzip
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = HERE / "PR4610-CHECKPOINT-ACTUAL-WORD.json.gz"
WORD_SHA256 = "d578875344095047c383ef513e69b9deb9d99d2b75abe14f7359d06365a924ac"
WORD_BLOB = "79dad65b9c9bd05956183492090d5439a269fc08"
CONTROLLER = ROOT / "research/joint-helper-lattice/CONTROLLER.json"
CLIFFORD = ROOT / "research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py"

# Claims under test, transcribed from PR #4626 head e4413c43 (PATCH.json, PROOF.md, ARITHMETIC.json).
HELPER, EVENT, BASIS = 621, 12704, [30, 429]
P_OLD = {1: 2201, 2: 412, 3: 506, 4: 135, 5: 36, 8: 8}
P_NEW = {1: 2202, 2: 414, 3: 505, 4: 134, 5: 36, 8: 8}
T_OLD = {4: 28, 7: 7, 8: 47, 9: 326}
T_NEW = {4: 28, 7: 8, 8: 47, 9: 325}
WHOLE_PAID = {1: 41316, 2: 7452, 3: 9090, 4: 2412, 5: 648, 8: 144, 16: 448, 24: 448, 32: 448,
              40: 448, 48: 448, 56: 448, 64: 448, 72: 224}
WHOLE_TARGETS = {4: 504, 7: 144, 8: 846, 9: 5850, 17: 448, 25: 448, 33: 448, 41: 448, 49: 448,
                 57: 448, 65: 448, 73: 224, 145: 224}
PROOF_DC = (D("-0.004016704251714084"), D("-0.004016704251714083"))  # PROOF.md section 4, a=.00302156
BODY_DC = D("-0.00401665923")  # PR body: "approximately -0.00401665923 at the tested exponent"
ROOT_BRACKET = (D("0.0030215713"), D("0.0030215714"))
KAPPA, TESTED = Q("0.003021569"), Q("0.00302157")
DISPLAY = {  # ARITHMETIC.json strictification, lower displayed endpoints (30 digits)
    "alpha": D("0.999999998585401279767941804505"),
    "gamma": D("0.956206638044871931847709338655"),
    "delta": D("0.958429239685014938905792889089")}
EXPONENT, H_CLAIM = 48264, 337848000000000

getcontext().prec = 80


def need(ok, why):
    if not ok:
        raise AssertionError(why)


def rejects(check, *args):
    try:
        check(*args)
    except AssertionError:
        return True
    return False


def load_word():
    raw = WORD.read_bytes()
    need(sha256(raw).hexdigest() == WORD_SHA256, "vendored checkpoint word SHA256")
    need(sha1(b"blob %d\0" % len(raw) + raw).hexdigest() == WORD_BLOB, "vendored checkpoint word git blob")
    return json.loads(gzip.decompress(raw))


def span(basis):
    s = {0}
    for x in basis:
        s |= {y ^ x for y in s}
    return frozenset(s)


def walk(word, start, final, spaces):
    """Own frame walker: returns (climbs as (role, from, to, rank), centre ranks)."""
    cur, climbs, centres = list(start), [], []

    def move(r, f):
        o = cur[r]
        if o == f:
            return
        need(spaces[o] < spaces[f], "paid edge %d:%d->%d is not a strict nesting" % (r, o, f))
        climbs.append((r, o, f, len(spaces[f]).bit_length() - len(spaces[o]).bit_length()))
        cur[r] = f

    for e in word:
        if e[0] == "scalar":
            g = e[1]
            for kind, r in (g[1:3] if g[0] in ("add", "copy") else g[1:2]):
                if kind == "L":
                    move(r, e[2])
        elif e[0] == "warp":
            need(e[1][0] == "L", "warp on an L role")
            move(e[1][1], e[3])
            cur[e[1][1]] = e[4]
        elif e[0] == "center":
            centres.append(e[4])
    for r, f in enumerate(final):
        move(r, f)
    return climbs, centres


def census(climbs, centres):
    return dict(sorted((Counter(c[3] for c in climbs) + Counter(centres)).items()))


def touches(e, role):
    if e[0] == "scalar":
        return ["L", role] in e[1][1:3]
    if e[0] == "warp":
        return e[1] == ["L", role]
    if e[0] == "climb":
        return e[2] == role
    return False


def patched(payload, basis=BASIS, event=EVENT):
    c = json.loads(json.dumps(payload["canonical"]))
    words = json.loads(json.dumps(payload["programs"]))
    label = len(c["frames"])
    c["frames"].append(list(basis))
    c["start"][HELPER] = label
    for w in words.values():
        if event is not None:
            w[event][2] = label
    return c, words, label


def native(payload):
    c0, programs = payload["canonical"], payload["programs"]
    need(len(c0["start"]) == len(c0["final"]) == 632 and c0["h"] == 9, "632 roles over F_2^9")
    sp0 = [span(f) for f in c0["frames"]]
    need(all(len(s) == 1 << len(f) for s, f in zip(sp0, c0["frames"])), "frame bases independent")
    old = {}
    for dr, w in programs.items():
        shipped = Counter((e[2], e[3], e[4], e[5]) for e in w if e[0] == "climb")
        cl, ce = walk(w, c0["start"], c0["final"], sp0)
        need(Counter(cl) == shipped, dr + ": own walker reproduces every shipped checkpoint climb")
        need(census(cl, ce) == P_OLD, dr + ": checkpoint census")
        old[dr] = Counter(cl)
    # Legality of the chart move.
    A = span(BASIS)
    need(len(A) == 4, "A has dimension 2")
    need(c0["start"][HELPER] == 0 and c0["frames"][0] == [] and len(c0["frames"][c0["final"][HELPER]]) == 9,
         "helper621 ZERO -> FULL9 in the checkpoint")
    nxt = {}
    for dr, w in programs.items():
        first = next(i for i, e in enumerate(w) if touches(e, HELPER))
        need(first == EVENT, dr + ": first touch of L621 is event 12704")
        need(w[EVENT][0] == "scalar" and w[EVENT][2] == 0, dr + ": event 12704 is a ZERO-frame scalar")
        need(["L", 514] in w[EVENT][1][1:3], dr + ": partner L514")
        prev514 = [i for i in range(EVENT) if touches(w[i], 514) and w[i][0] == "scalar"][-1]
        need(w[prev514][2] == 0, dr + ": L514 previous contact at ZERO")
        for role in (514, HELPER):
            k = next(i for i in range(EVENT + 1, len(w)) if w[i][0] == "scalar" and ["L", role] in w[i][1][1:3])
            need(A < sp0[w[k][2]], dr + ": A nested in next contact frame of L%d" % role)
            nxt[dr, role] = (k, w[k][2])
        need(A == sp0[nxt[dr, 514][1]] & sp0[nxt[dr, HELPER][1]], dr + ": A is exactly the intersection of both next-contact frames")
    # Apply the patch and re-walk.
    c1, words1, label = patched(payload)
    sp1 = sp0 + [A]
    diffs, new = {}, {}
    for dr, w in words1.items():
        stripped = [e for e in w if e[0] != "climb"]
        cl, ce = walk(stripped, c1["start"], c1["final"], sp1)
        need(census(cl, ce) == P_NEW, dr + ": patched census equals #4626's claim")
        need([e[1] for e in w if e[0] == "scalar"] == [e[1] for e in programs[dr] if e[0] == "scalar"],
             dr + ": scalar opcodes/coefficients unchanged")
        cnt = Counter(cl)
        diffs[dr] = (sorted((old[dr] - cnt).elements()), sorted((cnt - old[dr]).elements()))
        new[dr] = cnt
    f797, f4329 = nxt["forward", 514][1], nxt["forward", HELPER][1]
    expect = (sorted([(514, 0, f797, 3), (HELPER, 0, f4329, 4)]),
              sorted([(514, 0, label, 2), (514, label, f797, 1), (HELPER, label, f4329, 2)]))
    for dr in diffs:
        need(diffs[dr] == expect, dr + ": exact climb difference dP = H1 + 2H2 - H3 - H4")
    return c0, c1, sp0, sp1, label, (f797, f4329), diffs["forward"]


def helper_ranks(c, spaces, ce):
    dimcount, exact, fc = Counter(), {}, {}

    def frame(i):
        if i not in fc:
            fc[i] = ce.canonical_frame(9, c["frames"][i])
        return fc[i]

    for r in range(224, 632):
        a, b = c["start"][r], c["final"][r]
        need(spaces[a] <= spaces[b], "helper start nested in final")
        dimcount[len(c["frames"][b]) - len(c["frames"][a])] += 1
        op = frame(a).adjoint().then(frame(b))
        exact[r] = ce.rank([x for x, z, p in op.tab[9:]])
    return dict(sorted(dimcount.items())), exact, frame


def load_clifford():
    spec = importlib.util.spec_from_file_location("main_clifford_exact", CLIFFORD)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def histograms(local, helpers, idle=True):
    row = json.loads(CONTROLLER.read_text(encoding="utf-8"))
    need((row["kind"], row["pairs"]) == ("complex", 16), "p16 complex controller")
    T, P, kinds = Counter(), Counter(), Counter(e[0] for e in row["physical_events"])
    need((kinds["LOCAL"], kinds["QUERY_SHEAR"], kinds["IDLE"]) == (18, 15, 15), "18 calls, 15 shears, 15 idles")
    for e in row["physical_events"]:
        if e[0] == "LOCAL":
            T.update(helpers)
            P.update(local)
        elif e[0] == "QUERY_SHEAR":
            P[1] += 112
        elif e[0] == "IDLE" and idle:
            P[8 * len(e[2])] += 224
    for term in row["diagonal"]:
        T[1 + 8 * sum(term[1:])] += 112
    return dict(sorted(T.items())), dict(sorted(P.items()))


LN = {}


def mom(h, s):
    total = D(0)
    for r, n in h.items():
        if r not in LN:
            LN[r] = D(r).ln()
        total += n * (LN[r] * s).exp()
    return total


def dmom(h, s):  # d/ds of the moment
    return sum(n * LN[r] * (LN[r] * s).exp() for r, n in h.items())


def margin(T, P, a):
    return mom(T, 1 - a) - mom(P, 1 - a)


def newton_root(T, P, a=D("0.003")):
    for _ in range(40):
        step = margin(T, P, a) / -(dmom(T, 1 - a) - dmom(P, 1 - a))
        a -= step
        if abs(step) < D("1e-70"):
            return a
    raise AssertionError("Newton did not converge")


def Hr(r, a):
    return (D(r).ln() * (1 - a)).exp()


def dC(a):
    return 18 * (Hr(1, a) + 2 * Hr(2, a) - Hr(3, a) - Hr(4, a) - Hr(7, a) + Hr(9, a))


def kappa_checks(root, kappa, tested):
    need(Q(0) < kappa < tested < Q(str(root)), "kappa < tested < raw root")
    need(Q(int(Q(str(root)) * 10**8), 10**8) == tested, "tested = raw root floored to 1e-8")
    need(tested - kappa == Q(1, 10**9), "compiler gap 1e-9")


def wins(step, j):
    return (step * j + 1) ** 1000 < 2 ** j


def main():
    out = {}
    for path, digest in ((CONTROLLER, "1f5d6aa267e4e66048818714b5d3b5eae17a58abe91d15deeaa34574f7391a5f"),
                         (CLIFFORD, "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962")):
        need(sha256(path.read_bytes()).hexdigest() == digest, "main input pin " + path.name)
    payload = load_word()
    c0, c1, sp0, sp1, label, (f797, f4329), diff = native(payload)
    out["next_contact_frames"] = {"L514": [f797, payload["canonical"]["frames"][f797]],
                                  "L621": [f4329, payload["canonical"]["frames"][f4329]]}
    out["climb_diff_forward"] = {"removed": diff[0], "added": diff[1]}
    # Controls on the native side.
    need(rejects(lambda: _census_with(payload, [30, 1])), "control: non-nested chart span{30,1} rejected")
    need(rejects(lambda: _census_with(payload, BASIS, None)), "control: entrance moved without its contact rejected")
    need(rejects(lambda: _census_with(payload, [30])), "control: one-dimensional chart span{30} gives another census")

    ce = load_clifford()
    dc0, ex0, _ = helper_ranks(c0, sp0, ce)
    dc1, ex1, frame1 = helper_ranks(c1, sp1, ce)
    need(dc0 == T_OLD and dict(sorted(Counter(ex0.values()).items())) == T_OLD, "checkpoint helper census")
    need(dc1 == T_NEW and dict(sorted(Counter(ex1.values()).items())) == T_NEW, "patched helper census")
    need(ex0[HELPER] == 9 and ex1[HELPER] == 7 and all(ex0[r] == ex1[r] for r in ex0 if r != HELPER),
         "only helper621 changes, 9 -> 7")
    need(rejects(lambda: need(dict(Counter(ex1.values())) == T_OLD, "old credit")), "control: old helper credit")
    for r, a, b, k in diff[1]:
        op = frame1(a).adjoint().then(frame1(b))
        need(ce.rank([x for x, z, p in op.tab[9:]]) == k, "changed paid edge exact Clifford rank")
    out["helper_census"] = {"checkpoint": dc0, "patched": dc1, "helper621": [ex0[HELPER], ex1[HELPER]]}

    # Part B.
    T, P = histograms(P_NEW, T_NEW)
    need(T == WHOLE_TARGETS and P == WHOLE_PAID, "whole histograms equal #4626 ARITHMETIC.json")
    mass = lambda h: sum(r * n for r, n in h.items())
    need((sum(P.values()), sum(T.values()), mass(T) - mass(P)) == (64422, 10928, 752), "whole inventory")
    a0 = D("0.00302156")
    v = dC(a0)
    need(PROOF_DC[0] <= v <= PROOF_DC[1], "PROOF.md whole cost-change interval at a=.00302156")
    T0, P0 = histograms(P_OLD, T_OLD)
    whole_delta = (mom(T0, 1 - a0) - mom(P0, 1 - a0)) - (mom(T, 1 - a0) - mom(P, 1 - a0))
    need(abs(whole_delta - v) < D("1e-60"), "whole-histogram difference equals 18(H1+2H2-H3-H4-H7+H9)")
    # The PR body's -0.00401665923 is attained near a=.00302152, not at the tested exponent.
    lo, hi = D("0.0030"), D("0.0031")
    for _ in range(120):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if dC(mid) > BODY_DC else (lo, mid)
    out["dC"] = {"a=.00302156": str(v)[:24], "a=.00302157(tested)": str(dC(D("0.00302157")))[:24],
                 "a=.00302152": str(dC(D("0.00302152")))[:24], "body_value_attained_at_a": str(lo)[:16]}
    need(abs(lo - D("0.00302152")) < D("1e-11"), "body value corresponds to a=.00302152")
    need(abs(dC(D("0.00302157")) - BODY_DC) > D("5e-8"), "body value is not the tested-exponent value")

    root = newton_root(T, P)
    need(margin(T, P, ROOT_BRACKET[0]) > D("1e-60") and margin(T, P, ROOT_BRACKET[1]) < D("-1e-60"),
         "raw crossing inside #4626's bracket (signs exceed 80-digit error by >1e-60)")
    need(ROOT_BRACKET[0] < root < ROOT_BRACKET[1], "Newton root in bracket")
    root_old = newton_root(T0, P0)
    need(D("0.0030215551") < root_old < D("0.0030215552"), "control: checkpoint root reproduces #4610/#4615")
    Ti, Pi = histograms(P_NEW, T_NEW, idle=False)
    need(newton_root(Ti, Pi, D("0.01")) > ROOT_BRACKET[1], "control: dropping idle charges moves the root")
    out["raw_root"] = str(root)[:22]
    out["checkpoint_root"] = str(root_old)[:22]

    kappa_checks(root, KAPPA, TESTED)
    need(rejects(kappa_checks, root, Q("0.00302154"), Q("0.00302155")), "control: PR4610-rule kappa is a different selection")
    out["kappa_rule_comparison"] = {
        "pr4610_rule_floor_root_e8_minus_3": str(Q(int(Q(str(root)) * 10**8) - 3, 10**8)),
        "pr4626_rule_tested_minus_1e-9": str(KAPPA),
        "pr4626_rule_on_checkpoint_root": str(Q(int(Q(str(root_old)) * 10**8), 10**8) - Q(1, 10**9)),
        "tested_headroom_below_root": f"{root - D('0.00302157'):.6E}"}
    t = 1 - D("0.00302157")
    tgt, paid = mom(T, t), mom(P, t)
    alpha = paid / tgt
    gamma = mom(P, t + D("0.2")) / ((D(20).ln() * D("0.2")).exp() * tgt)
    delta = D(sum(T.values()) * 21) / ((D(20).ln() * D("0.00302157")).exp() * tgt)
    for name, val in (("alpha", alpha), ("gamma", gamma), ("delta", delta)):
        need(DISPLAY[name] <= val < DISPLAY[name] + D("1e-30"), name + " reproduces #4626's 30 displayed digits")
    need(alpha < 1 - D("1e-9") and gamma < D("0.97") and delta < D("0.97"), "strictification thresholds")
    out["alpha_gap_to_1e-9_threshold"] = f"{1 - D('1e-9') - alpha:.6E}"
    step = 7 * 10**9
    need((TESTED - KAPPA) / 7 == Q(1, step), "gap/7 = 1/7e9")
    need(wins(step, EXPONENT) and not wins(step, EXPONENT - 1), "48,264 is the least winning exponent")
    need(step * EXPONENT == H_CLAIM, "H = 7e9 * 48264")
    need(rejects(lambda: need(wins(step, EXPONENT - 1), "x")), "control: 48,263 loses")
    out["compiler"] = {"step": step, "least_exponent": EXPONENT, "H": step * EXPONENT}
    out["status"] = "PASS_PR4626_HELPER621_CENSUS_AND_ARITHMETIC_INDEPENDENTLY_REPRODUCED"
    out["new_kappa_claimed"] = False
    print(json.dumps(out, indent=1, default=str))


def _census_with(payload, basis, event=EVENT):
    c1, words1, label = patched(payload, basis, event)
    sp = [span(f) for f in c1["frames"]]
    for dr, w in words1.items():
        cl, ce = walk([e for e in w if e[0] != "climb"], c1["start"], c1["final"], sp)
        need(census(cl, ce) == P_NEW, "patched census")


if __name__ == "__main__":
    main()
