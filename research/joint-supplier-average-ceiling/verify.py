#!/usr/bin/env python3
"""Joint bit+complex supplier on the p16 controller: side-by-side ledger of the #4470 complex invoice and the #4814 BIT
invoice, and the ceiling of any one-call-for-both-sides word under the paid-profile moment model.

usage: python3.12 -B verify.py [--json OUT]

Model (#4470 PROOF.md section 5, #4814 price.py): a side's saving C is the root of
    f(C) = sum_T n_r r^(1-C) - sum_P n_r r^(1-C) = 0
over its productive targets T and paid recursive jobs P.  The rank-mass identity sum_T r - sum_P r = S is fixed by the
p16 controller (credits per port window - centre - thin shears): 752 on complex, 753 on BIT.
Standard library only; roots are bisected with 40-digit Decimal arithmetic.
"""
from collections import Counter
from decimal import Decimal, getcontext
from pathlib import Path
import hashlib, json, re, sys

getcontext().prec = 40
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CX = "research/joint-helper-lattice/RESULT.json"                  # #4470 complex invoice, selected kappa 0.00302015
BT = "research/bit-finite-ordinary-bootstrap/RESULT.json"         # #4814 BIT invoice, admitted ordinary 0.003475458
OUTER = "research/kappa01-outer-repair/README.md"                  # conditional "one supplier for both" reduction, sec. 2
ENGINE = "research/coordinated-frames-and-entrance-banks/arithmetic/balanced_shared.py"


def need(ok, msg):
    if not ok:
        raise ValueError("FAIL: " + msg)


def sha256(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def authenticate():
    pins = {f["path"]: f["sha256"] for f in json.loads((HERE / "SOURCES.json").read_text())["files"]}
    for p in (CX, BT, OUTER, ENGINE):
        need(sha256(p) == pins[p], "source bytes changed: " + p)


# ------------------------------------------------------------------ moment arithmetic
def D(x):
    return Decimal(x)


def mom(prof, t):
    return sum((D(n) * D(r) ** t for r, n in prof.items() if n), D(0))


def f_of(T, P):
    return lambda c: mom(T, 1 - c) - mom(P, 1 - c)


def root(T, P, lo=D("1e-12"), hi=D(1), iters=140):
    """Root of f in (0,1): 0 if f(lo) <= 0 (no saving), 1 if f(1) > 0 (beyond the model)."""
    f = f_of(T, P)
    if f(lo) <= 0:
        return D(0)
    if f(hi) > 0:
        return D(1)
    for _ in range(iters):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    return lo


def mass(prof):
    return sum(r * n for r, n in prof.items())


def logmoment(prof):
    return sum(D(n) * D(r) * D(r).ln() for r, n in prof.items() if n)


def SG(T, P):
    """Linearisation f(C) ~= S - C*G: S = mass surplus, G = log-moment difference."""
    return mass(T) - mass(P), logmoment(T) - logmoment(P)


def cnt(d):
    return Counter({int(k): int(v) for k, v in d.items()})


def expand(prof, reverse=True):
    out = []
    for r, n in sorted(prof.items()):
        out += [r] * n
    return sorted(out, reverse=reverse)


def pair(a, b, combine, rev_b=True):
    """Pair two rank multisets element-wise after sorting; leftovers stay single."""
    la, lb = expand(a), expand(b, rev_b)
    out = Counter()
    k = min(len(la), len(lb))
    for i in range(k):
        out[combine(la[i], lb[i])] += 1
    for r in la[k:] + lb[k:]:
        out[r] += 1
    return out


# ------------------------------------------------------------------ invoices and roles
def load():
    cx = json.loads((ROOT / CX).read_text())
    bt = json.loads((ROOT / BT).read_text())["raw_invoice"]
    need(cx["full_calls"] == bt["thick_calls"] == 18, "both sides are the 18-call p16 controller")
    need(cx["query_shears"] == 15 and bt["thin_queries"] == 1665, "15 thin query stages per port")
    Tc, Pc, Tb, Pb = cnt(cx["targets"]), cnt(cx["paid"]), cnt(bt["targets"]), cnt(bt["paid"])
    return cx, bt, Tc, Pc, Tb, Pb


def roles(cx, bt, Tc, Pc, Tb, Pb):
    """Split paid jobs into idle / local / shear / centre and targets into main / idle / helper on both sides."""
    calls, pc, pb = 18, 112, 111
    LPc = cnt(cx["local_paid"])
    paid_c = {"centre": Counter({8: calls * LPc[8]}),
              "local": Counter({r: calls * n for r, n in LPc.items() if r != 8}),
              "shear": Counter({1: cx["query_shears"] * pc})}
    idle = Pc.copy()
    for p in paid_c.values():
        idle.subtract(p)
    paid_c["idle"] = +idle
    need(all(r % 8 == 0 and r >= 16 for r in paid_c["idle"]), "complex idle ranks 8(j+1)")
    idle_b = Counter({r: n for r, n in Pb.items() if r >= 14})
    need(all(r % 7 == 0 for r in idle_b), "BIT idle ranks 7(j+1)")
    shear_b = Counter({1: bt["thin_queries"]})
    local_b = Pb.copy(); local_b.subtract(idle_b); local_b.subtract(shear_b); local_b = +local_b
    need(all(1 <= r <= 7 for r in local_b), "BIT local ranks 1..7")
    paid_b = {"centre": Counter(), "local": local_b, "shear": shear_b, "idle": idle_b}
    for name, parts, P in (("complex", paid_c, Pc), ("bit", paid_b, Pb)):
        tot = Counter()
        for p in parts.values():
            tot.update(p)
        need(+tot == +P, name + " paid roles partition the invoice")

    def targets(T, big, step):
        main = Counter({big: T[big]})
        idle = Counter({r: n for r, n in T.items() if r != big and r > 9 and (r - 1) % step == 0})
        helper = T.copy(); helper.subtract(main); helper.subtract(idle)
        return {"main": main, "idle": idle, "helper": +helper}

    tg_c, tg_b = targets(Tc, 145, 8), targets(Tb, 127, 7)
    need(sum(tg_c["idle"].values()) == sum(paid_c["idle"].values()) == 3360, "3360 complex idle pairs")
    need(sum(tg_b["idle"].values()) == sum(paid_b["idle"].values()) == 3330, "3330 BIT idle pairs")
    need(tg_c["main"][145] == 2 * pc and tg_b["main"][127] == 2 * pb, "two main fields per port")
    return paid_c, paid_b, tg_c, tg_b


def identities(cx, bt, Tc, Pc, Tb, Pb):
    Sc, Sb = mass(Tc) - mass(Pc), mass(Tb) - mass(Pb)
    need(Sc == 752 == 112 * 32 - 18 * 64 - 1680, "complex surplus 752 = ports*32 - centre - shears")
    need(Sb == 753 == bt["rank_surplus"], "BIT surplus 753 as recorded in #4814")
    need(sum(Tc.values()) == cx["productive_fields"] == 10928 and sum(Pc.values()) == cx["paid_calls"] == 64620, "#4470 counts")
    need(sum(Tb.values()) == bt["original_fields"] == 11400, "#4814 original fields")
    return Sc, Sb


# ------------------------------------------------------------------ the six joint models
def models(paid_c, paid_b, tg_c, tg_b):
    both = lambda a, b: Counter(a) + Counter(b)
    once = lambda a, b: Counter({r: max(a[r], b[r]) for r in set(a) | set(b)})
    amax = lambda a, b: pair(a, b, max)
    asum = lambda a, b: pair(a, b, lambda x, y: x + y)
    asum_rev = lambda a, b: pair(a, b, lambda x, y: x + y, rev_b=False)

    def build(rule_t, rule_p):
        T, P = Counter(), Counter()
        for role in ("main", "idle", "helper"):
            T.update(rule_t(tg_c[role], tg_b[role]))
        for role in ("idle", "local", "shear", "centre"):
            P.update(rule_p(paid_c[role], paid_b[role]))
        return T, P

    return {
        "A_side_by_side": build(both, both),
        "B_literal_paid_once": build(both, once),
        "C_aligned_max": build(amax, amax),
        "D_stacked_sum": build(asum, asum),
        "E_paid_merged_targets_separate": build(both, asum),
        "F_paid_merged_reverse_pairing": build(both, asum_rev),
    }


def decreasing(T, P, upto=D("0.05"), steps=50):
    """f is strictly decreasing on [0, upto] iff its log-moment G(t) stays positive there (checked on a grid)."""
    for i in range(steps + 1):
        c = upto * i / steps
        t = 1 - c
        g = sum(D(n) * D(r) ** t * D(r).ln() for r, n in T.items()) - sum(D(n) * D(r) ** t * D(r).ln() for r, n in P.items())
        if g <= 0:
            return False
    return True


def run(out):
    authenticate()
    cx, bt, Tc, Pc, Tb, Pb = load()
    Sc, Sb = identities(cx, bt, Tc, Pc, Tb, Pb)
    paid_c, paid_b, tg_c, tg_b = roles(cx, bt, Tc, Pc, Tb, Pb)
    Cc, Cb = root(Tc, Pc), root(Tb, Pb)
    need(abs(Cc - D("0.00302016597702")) < D("1e-13"), "complex raw root 0.00302016597702 (#4470)")
    need(abs(Cb - D("0.00347545806408")) < D("1e-13"), "BIT raw root 0.00347545806408 (#4814)")
    Gc, Gb = SG(Tc, Pc)[1], SG(Tb, Pb)[1]
    need(decreasing(Tc, Pc) and decreasing(Tb, Pb), "both side equations are decreasing on [0, 0.05]")
    out["baseline"] = {"complex_root": str(Cc), "bit_root": str(Cb), "S_complex": Sc, "S_bit": Sb,
                       "G_complex": str(Gc.quantize(D(1))), "G_bit": str(Gb.quantize(D(1))),
                       "S_over_G_complex": str((D(Sc) / Gc).quantize(D("1e-6"))), "S_over_G_bit": str((D(Sb) / Gb).quantize(D("1e-6")))}

    # ledger of identical (rank, role) paid jobs
    common = {role: Counter({r: min(paid_c[role][r], paid_b[role][r]) for r in set(paid_c[role]) | set(paid_b[role])})
              for role in paid_c}
    common_mass = sum(mass(+c) for c in common.values())
    need(set(+common["idle"]) == {56}, "idle ranks 8(j+1) and 7(j+1) coincide only at 56")
    need(common_mass == 74499, "identical (rank, role) paid mass 74499")
    out["ledger"] = {"identical_rank_role_paid_jobs": sum(sum((+c).values()) for c in common.values()),
                     "identical_rank_role_paid_mass": common_mass,
                     "paid_mass": {"complex": mass(Pc), "bit": mass(Pb)},
                     "paid_by_role": {s: {role: dict(sorted(p.items())) for role, p in parts.items()}
                                      for s, parts in (("complex", paid_c), ("bit", paid_b))},
                     "targets_by_role": {s: {role: dict(sorted(p.items())) for role, p in parts.items()}
                                         for s, parts in (("complex", tg_c), ("bit", tg_b))}}

    res = {}
    for name, (T, P) in models(paid_c, paid_b, tg_c, tg_b).items():
        C = root(T, P)
        S, G = SG(T, P)
        res[name] = {"C_joint": str(C.quantize(D("1e-12"))), "S": S, "G": str(G.quantize(D(1))),
                     "ratio_to_complex": str((C / Cc).quantize(D("1e-4"))), "ratio_to_bit": str((C / Cb).quantize(D("1e-4"))),
                     "mass_identity": S <= Sc + Sb, "target_mass": mass(T), "paid_mass": mass(P)}
    out["models"] = res
    A, B, Cm, Dm, E, F = (res[k] for k in ("A_side_by_side", "B_literal_paid_once", "C_aligned_max", "D_stacked_sum",
                                            "E_paid_merged_targets_separate", "F_paid_merged_reverse_pairing"))
    # averaging: any mass-consistent joint model with both target sets stays between the two side roots
    for name in ("A_side_by_side", "D_stacked_sum"):
        C = D(res[name]["C_joint"])
        need(Cc < C < Cb, name + " lies strictly between the two side roots")
        need(res[name]["S"] == Sc + Sb, name + " keeps the surplus 1505")
    need(not B["mass_identity"] and B["S"] == Sc + Sb + 74499 and D(B["C_joint"]) > D("0.1"),
         "literal paid-once rule drops 74499 paid mass with unchanged targets: identity violated, root not a ceiling")
    need(Cm["S"] < 0 and D(Cm["C_joint"]) == 0, "aligned-max twins have negative surplus: no saving")
    need(E["S"] == F["S"] == Sc + Sb and D(E["C_joint"]) > Cb and D(F["C_joint"]) > Cb, "E/F keep the surplus and gain only from merging")

    # E/F are the within-side small-job merge lever, not a two-sided effect: the same pairing inside the complex side alone
    loc = paid_c["local"]
    half = expand(loc)
    merged = Counter()
    for i in range(0, len(half) - 1, 2):
        merged[half[i] + half[i + 1]] += 1
    if len(half) % 2:
        merged[half[-1]] += 1
    P1 = Counter(paid_c["idle"]) + paid_c["shear"] + paid_c["centre"] + merged
    C1 = root(Tc, P1)
    need(mass(P1) == mass(Pc) and C1 > Cb, "pairwise merge of complex local jobs alone already exceeds the BIT root")
    out["within_side_merge_control"] = {"complex_local_jobs_paired": str(C1.quantize(D("1e-9"))),
                                        "ratio_to_complex": str((C1 / Cc).quantize(D("1e-4")))}

    # the best mass-consistent two-sided model (A or D) stays below the BIT gate that an ordinary complex improvement reaches
    best = max(D(A["C_joint"]), D(Dm["C_joint"]))
    need(best < Cb, "joint word ceiling below the BIT gate 0.003475458")
    out["conclusion"] = {"best_mass_consistent_joint": str(best.quantize(D("1e-9"))),
                         "gain_over_selected": str(((best / Cc) - 1).quantize(D("1e-4"))),
                         "bit_gate_gain": str(((Cb / Cc) - 1).quantize(D("1e-4")))}

    # source binding of the outer statements used in the README (provenance only; no engine replay here)
    outer = (ROOT / OUTER).read_text(encoding="utf-8")
    need(re.search(r"no separate numerical bit endpoint: one can choose both `a<s` and\s+`b<s`", outer),
         "kappa01-outer-repair sec. 2 conditional one-supplier reduction present")
    eng = (ROOT / ENGINE).read_text(encoding="utf-8")
    need(re.search(r"margins = dict\(g1=1-eps, g2=a, g3=G, g4=a", eng) and "scoped_limit=a/(1+a)" in eng,
         "balanced engine: standalone swap margins g2=g4=a, controlling margin G, scoped limit a/(1+a)")
    out["status"] = "PASS_JOINT_SUPPLIER_AVERAGE_CEILING_NEGATIVE"
    return out


def controls():
    """Rejecting controls: each corruption must fail a check."""
    cx, bt, Tc, Pc, Tb, Pb = load()
    done = []

    def rejects(name, fn):
        try:
            fn()
        except ValueError:
            done.append(name)
            return
        raise SystemExit("UNREJECTED control: " + name)

    # 1. one extra rank-1 paid job breaks the complex surplus identity 752
    Pc1 = Counter(Pc); Pc1[1] += 1
    rejects("surplus identity", lambda: identities(cx, bt, Tc, Pc1, Tb, Pb))
    # 2. a BIT invoice whose recorded surplus disagrees with its profile
    bt2 = dict(bt); bt2["rank_surplus"] = 754
    rejects("recorded BIT surplus", lambda: identities(cx, bt2, Tc, Pc, Tb, Pb))
    # 3. a paid profile with a foreign idle rank is not the p16 role split
    Pc3 = Counter(Pc); Pc3[20] += 1; Pc3[16] -= 1
    rejects("idle rank grid", lambda: roles(cx, bt, Tc, Pc3, Tb, Pb))
    # 4. swapping targets and paid on one side destroys monotonicity, which the averaging argument needs
    rejects("decreasing equation", lambda: need(decreasing(Pc, Tc), "x"))
    # 5. the literal paid-once model is rejected as a ceiling by the mass identity check
    rejects("literal model as ceiling", lambda: need(mass(Tc) + mass(Tb) - (mass(Pc) + mass(Pb) - 74499) <= 752 + 753, "x"))
    # 6. a tampered source byte is caught by the pin
    pins = json.loads((HERE / "SOURCES.json").read_text())["files"]
    rejects("source pin", lambda: need(sha256(CX) == next(f["sha256"] for f in pins if f["path"] == CX)[::-1], "x"))
    return done


def main():
    out = {"schema_version": 1}
    run(out)
    out["rejected_controls"] = controls()
    need(len(out["rejected_controls"]) == 6, "six controls")
    exp = json.loads((HERE / "RESULT.json").read_text()).get("receipt") if (HERE / "RESULT.json").exists() else None
    if exp:
        for k in ("baseline", "models", "conclusion"):
            need(exp[k] == out[k], "receipt matches RESULT.json: " + k)
    if "--json" in sys.argv:
        Path(sys.argv[sys.argv.index("--json") + 1]).write_text(json.dumps(out, indent=1))
    print(json.dumps(out["conclusion"]))
    print(out["status"])


if __name__ == "__main__":
    main()
