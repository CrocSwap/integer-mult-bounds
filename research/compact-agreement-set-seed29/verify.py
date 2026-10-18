#!/usr/bin/env python3
"""Exact raw agreement-set census for the compact dirty-control selected-bit map.

Independent stdlib transcription of notes/compact-control-movement.tex
("Guards and deterministic repair"): the four-update scalar gadget packed as
whole-slot rotations, the earlier-source and later-source routines, and the
elementary highest-bit XOR. No predecessor interpreter is imported.

For each complete bounded geometry the checker enumerates every state of the
invariant fiber (selected source bits c, full target y modulo its untouched low
rho bits, compact temporaries t, compact controls u) and computes the exact
set AG of states where the complete routine equals the ideal selected-bit XOR
map and restores u, t exactly. It then tests, independently and on complete
domains, the sufficiency of the published guards

  G0  original temporary+target guard (plus u nonsaturation for later source)
  G1  compact-carry-repair-audit expanded predicate (last u digit free)
  H   compact-late-guard-audit-seed73 two-pass guard (source dependent)

and records smallest states each guard misses (AG without the guard) and
smallest counterexamples if any guard admits a state outside AG. It reproduces
both published failure fixtures as fidelity controls and runs a mutated-program
control that must be rejected.

No kappa change. This audits one named condition; it does not modify the
production predicate, the selected record, or any upstream file.
"""

import argparse
import hashlib
import json
from pathlib import Path
from fractions import Fraction as Q

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

STATUS = "PASS_COMPACT_AGREEMENT_SET"


def require(condition, message):
    if not condition:
        raise ValueError(message)


# ----------------------------------------------------------------------
# Independent transcription of the source note.

def step_E(z, y, t, n, K, G, rho):
    """One earlier-source block: four packed updates on (y, t).

    z is the n-bit control word (selected source bits, or u parities).
    All arithmetic is the literal packed arithmetic of the note: target
    updates are modular rotations of the whole f*K-bit slot; temporary
    updates are modular rotations of the whole n*G-bit compact field.
    """
    ymask = (1 << ((n + 1) * K)) - 1
    tmask = (1 << (n * G)) - 1
    D = (1 << G) - 1
    # R1: y += sum_i 2*z_i*t_i*2^{j_i}
    off = 0
    for i in range(n):
        if (z >> i) & 1:
            off += (2 * ((t >> (i * G)) & D)) << (rho + i * K)
    y = (y + off) & ymask
    # T1: t += pack of current selected target bits
    off = 0
    for i in range(n):
        off += ((y >> (rho + i * K)) & 1) << (i * G)
    t = (t + off) & tmask
    # R2: y += sum_i z_i*(1-2*t_i)*2^{j_i} with post-T1 digits
    off = 0
    for i in range(n):
        if (z >> i) & 1:
            off += (1 - 2 * ((t >> (i * G)) & D)) << (rho + i * K)
    y = (y + off) & ymask
    # T2: t -= pack of (current selected target bits xor z)
    off = 0
    for i in range(n):
        off += (((y >> (rho + i * K)) & 1) ^ ((z >> i) & 1)) << (i * G)
    t = (t - off) & tmask
    return y, t


def step_E_with_b(z, y, t, b, n, K, G, rho):
    """Faithful swap-sandwich realization; the back field must return."""
    ymask = (1 << ((n + 1) * K)) - 1
    tmask = (1 << (n * G)) - 1
    D = (1 << G) - 1
    off = 0
    for i in range(n):
        if (z >> i) & 1:
            off += (2 * ((t >> (i * G)) & D)) << (rho + i * K)
    y = (y + off) & ymask
    off = 0
    for i in range(n):
        off += ((y >> (rho + i * K)) & 1) << (i * G)
    b, t = t, b
    b = (b + off) & tmask
    t, b = b, t
    off = 0
    for i in range(n):
        if (z >> i) & 1:
            off += (1 - 2 * ((t >> (i * G)) & D)) << (rho + i * K)
    y = (y + off) & ymask
    off = 0
    for i in range(n):
        off += (((y >> (rho + i * K)) & 1) ^ ((z >> i) & 1)) << (i * G)
    b, t = t, b
    b = (b - off) & tmask
    t, b = b, t
    return y, t, b


def parity_word(u, n, G):
    z = 0
    for i in range(n):
        z |= ((u >> (i * G)) & 1) << i
    return z


def run_late(c, y, t, u, n, K, G, rho):
    """Later source: E(u parities), load c into u, E(new parities), unload."""
    fmask = (1 << (n * G)) - 1
    z = parity_word(u, n, G)
    y, t = step_E(z, y, t, n, K, G, rho)
    load = 0
    for i in range(n):
        load |= ((c >> i) & 1) << (i * G)
    u = (u + load) & fmask
    z = parity_word(u, n, G)
    y, t = step_E(z, y, t, n, K, G, rho)
    u = (u - load) & fmask
    return y, t, u


def ideal_y(y, c, n, K, rho):
    off = 0
    for i in range(n):
        off |= ((c >> i) & 1) << (rho + i * K)
    return y ^ off


# ----------------------------------------------------------------------
# Published guard predicates, transcribed from the cited packages.

def guard_temp_target(y, t, n, K, G, rho):
    """G0's temporary and target conditions (all i < n)."""
    D = (1 << G) - 1
    B = 1 << G
    A = 1 << (K - 1)
    for i in range(n):
        if ((t >> (i * G)) & D) > B - 2:
            return False
        g = (y >> (rho + i * K + 1)) & ((1 << (K - 1)) - 1)
        if not (2 * B <= g < A - 2 * B):
            return False
    return True


def guard_G0_late(y, t, u, n, K, G, rho):
    """Original later source: G0 plus every u digit nonsaturated."""
    if not guard_temp_target(y, t, n, K, G, rho):
        return False
    D = (1 << G) - 1
    B = 1 << G
    for i in range(n):
        if ((u >> (i * G)) & D) == B - 1:
            return False
    return True


def guard_G1_late(y, t, u, n, K, G, rho):
    """Expanded predicate: last source-control digit keeps its complete range."""
    if not guard_temp_target(y, t, n, K, G, rho):
        return False
    D = (1 << G) - 1
    B = 1 << G
    for i in range(n - 1):
        if ((u >> (i * G)) & D) == B - 1:
            return False
    return True


def guard_H(y, t, u, c, n, K, G, rho):
    """compact-late-guard-audit-seed73 two-pass guard (1)."""
    D = (1 << G) - 1
    B = 1 << G
    A = 1 << (K - 1)
    for i in range(n):
        if ((t >> (i * G)) & D) > B - 2:
            return False
    for i in range(n - 1):
        ui = (u >> (i * G)) & D
        ci = (c >> i) & 1
        if ui + ci >= B:
            return False
        g = (y >> (rho + i * K + 1)) & ((1 << (K - 1)) - 1)
        if g + ((ui & 1) | ci) * ((t >> (i * G)) & D) >= A:
            return False
    return True


def H_fraction(n, K, G):
    """Closed form (2) of compact-late-guard-audit-seed73."""
    B = 1 << G
    A = 1 << (K - 1)
    return ((B - 1) / Q(B)) ** n * (
        Q(1) - Q(1, 2 * B) - Q((3 * B - 2) * (B - 2), 8 * A * B)
    ) ** (n - 1)


# ----------------------------------------------------------------------
# Domain: (n, K, G, early rhos, late rhos). f = n+1 wide slot.

DOMAIN = [
    (2, 3, 1, (0, 1, 2), (0, 1, 2)),
    (2, 3, 2, (0, 1, 2), (0, 1, 2)),
    (2, 4, 1, (0, 1, 2, 3), (0, 1, 2, 3)),
    (2, 4, 2, (0, 1, 2, 3), (0, 1, 2, 3)),
    (2, 5, 1, (0, 1, 2, 3, 4), (0, 2, 4)),
    (2, 6, 1, (4, 5), (4, 5)),
    (3, 3, 1, (0, 1, 2), (0, 1, 2)),
    (3, 5, 1, (4,), ()),
]


def census_early(n, K, G, rho):
    ycount = 1 << ((n + 1) * K - rho)
    tcount = (1 << G) ** n
    total = ag = g0_adm = 0
    viol = None          # smallest state admitted by G0 but outside AG
    waste = None         # smallest AG state rejected by G0
    waste_active = None  # smallest such state with c != 0
    for t in range(tcount):
        for c in range(1 << n):
            for yr in range(ycount):
                y = yr << rho
                y2, t2 = step_E(c, y, t, n, K, G, rho)
                ok = (y2 == ideal_y(y, c, n, K, rho)) and (t2 == t)
                gd = guard_temp_target(y, t, n, K, G, rho)
                total += 1
                if ok:
                    ag += 1
                    if not gd:
                        key = [y, t, c]
                        if waste is None or key < waste:
                            waste = key
                        if c and (waste_active is None or key < waste_active):
                            waste_active = key
                if gd:
                    g0_adm += 1
                    if not ok:
                        key = [y, t, c]
                        if viol is None or key < viol:
                            viol = key
    return {
        "total": total, "ag": ag,
        "G0_admitted": g0_adm, "G0_violation": viol,
        "ag_outside_G0": waste, "ag_outside_G0_active": waste_active,
    }


def census_late(n, K, G, rho):
    ycount = 1 << ((n + 1) * K - rho)
    tcount = (1 << G) ** n
    total = ag = 0
    adm = {"G0": 0, "G1": 0, "H": 0}
    viol = {"G0": None, "G1": None, "H": None}
    waste = {"G0": None, "G1": None, "H": None, "all": None, "all_active": None}
    inc01 = inc1H = None  # inclusion witnesses
    for t in range(tcount):
        for u in range(tcount):
            for c in range(1 << n):
                for yr in range(ycount):
                    y = yr << rho
                    y2, t2, u2 = run_late(c, y, t, u, n, K, G, rho)
                    ok = (y2 == ideal_y(y, c, n, K, rho)) and (t2 == t) and (u2 == u)
                    g0 = guard_G0_late(y, t, u, n, K, G, rho)
                    g1 = guard_G1_late(y, t, u, n, K, G, rho)
                    gh = guard_H(y, t, u, c, n, K, G, rho)
                    total += 1
                    if ok:
                        ag += 1
                        if not (gh or g0 or g1):
                            key = [y, t, u, c]
                            if waste["all"] is None or key < waste["all"]:
                                waste["all"] = key
                            if c and (waste["all_active"] is None
                                      or key < waste["all_active"]):
                                waste["all_active"] = key
                    for name, gd in (("G0", g0), ("G1", g1), ("H", gh)):
                        if gd:
                            adm[name] += 1
                            if not ok:
                                key = [y, t, u, c]
                                if viol[name] is None or key < viol[name]:
                                    viol[name] = key
                        elif ok:
                            key = [y, t, u, c]
                            if waste[name] is None or key < waste[name]:
                                waste[name] = key
                    if g0 and not g1 and inc01 is None:
                        inc01 = [y, t, u, c]
                    if g1 and not gh and inc1H is None:
                        inc1H = [y, t, u, c]
    return {
        "total": total, "ag": ag,
        "G0_admitted": adm["G0"], "G1_admitted": adm["G1"], "H_admitted": adm["H"],
        "G0_violation": viol["G0"], "G1_violation": viol["G1"], "H_violation": viol["H"],
        "ag_outside_G0": waste["G0"], "ag_outside_G1": waste["G1"],
        "ag_outside_H": waste["H"],
        "ag_outside_all": waste["all"], "ag_outside_all_active": waste["all_active"],
        "G0_not_G1": inc01, "G1_not_H": inc1H,
    }


# ----------------------------------------------------------------------
# Fidelity and failure controls.

def published_fixtures():
    """Both published counterexamples must reproduce exactly."""
    out = {}
    # research/compact-carry-repair-audit: n=2,K=5,rho=4,G=1, later source.
    n, K, G, rho = 2, 5, 1, 4
    x, y, t, u, b = 16, 4224, 0, 1, 2
    c = ((x >> rho) & 1) | (((x >> (rho + K)) & 1) << 1)
    y2, t2, u2 = run_late(c, y, t, u, n, K, G, rho)
    out["carry_repair_fixture"] = {
        "input": [x, y, t, u, b], "c": c,
        "y_out": y2, "t_out": t2, "u_out": u2,
        "ideal": ideal_y(y, c, n, K, rho),
    }
    require(y2 == 4752, "published fixture 16,4224,0,1,2 must give y=4752")
    require(ideal_y(y, c, n, K, rho) == 4240, "published fixture ideal must be 4240")
    require(t2 == 0 and u2 == 1, "published fixture restores temporaries")
    # research/compact-late-guard-audit-seed73: n=2,K=6,rho=1,G=2.
    n, K, G, rho = 2, 6, 2, 1
    x, y, t, u, b = 2, 124, 1, 0, 7
    c = ((x >> rho) & 1) | (((x >> (rho + K)) & 1) << 1)
    y2, t2, u2 = run_late(c, y, t, u, n, K, G, rho)
    out["late_guard_fixture"] = {
        "input": [x, y, t, u, b], "c": c,
        "y_out": y2, "t_out": t2, "u_out": u2,
        "ideal": ideal_y(y, c, n, K, rho),
    }
    require(y2 == 126, "published fixture 2,124,1,0,7 must give y=126")
    require(t2 == 5, "published fixture must corrupt temporary 1 -> 5")
    require(u2 == 0, "published fixture restores the compact control")
    return out


def mutant_controls():
    """A sign-flipped unloading must break restoration inside the guarded domain."""
    n, K, G, rho = 2, 5, 1, 4  # G0's target guard is nonempty for K > G+3
    D = (1 << G) - 1
    tmask = (1 << (n * G)) - 1
    ycount = 1 << ((n + 1) * K - rho)
    exact = 0
    sign_err = None
    for t in range((1 << G) ** n):
        for c in range(1 << n):
            for yr in range(ycount):
                y = yr << rho
                if not guard_temp_target(y, t, n, K, G, rho):
                    continue
                y1, t1 = step_E(c, y, t, n, K, G, rho)
                exact += 1
                require(y1 == ideal_y(y, c, n, K, rho) and t1 == t,
                        "guarded early domain must be exact")
                off = 0
                for i in range(n):
                    off += (((y1 >> (rho + i * K)) & 1) ^ ((c >> i) & 1)) << (i * G)
                t_bad = (t1 + off) & tmask  # add instead of subtract at T2
                if t_bad != t and sign_err is None:
                    sign_err = [y, t, c, t_bad]
    require(sign_err is not None, "sign-flipped unload must be caught by restoration")
    return {"guarded_exact_states": exact, "sign_flip_witness": sign_err}


def spectator_controls():
    """Low rho target bits and the dirty back field must not affect results."""
    n, K, G, rho = 2, 4, 1, 2
    lowmask = (1 << rho) - 1
    checked = 0
    for t in range((1 << G) ** n):
        for u in range((1 << G) ** n):
            for c in range(1 << n):
                y = 0b101010101010
                y2, t2, u2 = run_late(c, y, t, u, n, K, G, rho)
                for low in (0, 1, 3, 7):
                    yb = (y & ~lowmask) | (low & lowmask)
                    y3, t3, u3 = run_late(c, yb, t, u, n, K, G, rho)
                    require(y3 >> rho == y2 >> rho and t3 == t2 and u3 == u2,
                            "low target bits must be spectators")
                    require(y3 & lowmask == yb & lowmask,
                            "low target bits must be preserved")
                    for dirty in (0, 5, 15, (1 << (n * G)) - 1):
                        _, _, be = step_E_with_b(
                            parity_word(u, n, G), yb, t, dirty, n, K, G, rho)
                        require(be == dirty, "back field must return untouched")
                    checked += 1
    return {"spectator_states": checked}


# ----------------------------------------------------------------------

def verify_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = ROOT / entry["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(digest == entry["sha256"],
                "source pin mismatch: " + entry["path"])


def compute():
    verify_sources()
    receipts = {"fixtures": published_fixtures(),
                "controls": mutant_controls(),
                "spectators": spectator_controls()}
    cells = []
    for (n, K, G, early_rhos, late_rhos) in DOMAIN:
        for rho in early_rhos:
            r = census_early(n, K, G, rho)
            r.update({"n": n, "K": K, "G": G, "rho": rho, "order": "early"})
            require(r["G0_violation"] is None,
                    "G0 sufficiency violated (early) at %s" % ((n, K, G, rho),))
            cells.append(r)
        for rho in late_rhos:
            r = census_late(n, K, G, rho)
            r.update({"n": n, "K": K, "G": G, "rho": rho, "order": "late"})
            for name in ("G0", "G1", "H"):
                require(r[name + "_violation"] is None,
                        "%s sufficiency violated (late) at %s" % (name, (n, K, G, rho)))
            require(r["G0_not_G1"] is None, "original guard must imply G1")
            expected = H_fraction(n, K, G) * r["total"]
            require(expected.denominator == 1 and r["H_admitted"] == expected.numerator,
                    "H count must match closed form (2) at %s" % ((n, K, G, rho),))
            r["H_fraction"] = [H_fraction(n, K, G).numerator,
                               H_fraction(n, K, G).denominator]
            r["H_count_formula"] = expected.numerator
            cells.append(r)
    receipt = {
        "status": STATUS,
        "domain": [[n, K, G, list(e), list(l)] for (n, K, G, e, l) in DOMAIN],
        "cells": cells,
        **receipts,
    }
    return json.loads(json.dumps(receipt))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", metavar="PATH")
    ap.add_argument("--check", metavar="PATH")
    args = ap.parse_args()
    receipt = compute()
    if args.write:
        target = Path(args.write)
        require(not target.exists(), "refusing to overwrite " + str(target))
        target.write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n",
                          encoding="utf-8")
    else:
        target = Path(args.check) if args.check else HERE / "RESULT.json"
        expected = json.loads(target.read_text(encoding="utf-8"))
        require(receipt == expected, "receipt mismatch against " + str(target))
    totals = sum(c["total"] for c in receipt["cells"])
    ags = sum(c["ag"] for c in receipt["cells"])
    print("%s: %d states; %d raw agreements; %d cells; 2 fixtures; 2 controls"
          % (STATUS, totals, ags, len(receipt["cells"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
