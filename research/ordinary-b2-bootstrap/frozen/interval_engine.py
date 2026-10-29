#!/usr/bin/env python3
"""Exact joint arithmetic, with an optional binding to completed finite release.

Prepared for Ross Richardson with OpenAI Codex assistance. Apache-2.0.
The interval implementation is separate from the inherited moment engines.
Finite arithmetic and receipt binding do not prove the all-size interfaces.
"""
import argparse
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {
    "frozen/pr4181/RESULT.json": "d823509ea38e545db6c287a85c00bc4257825fb2710728dfc776c8801d2becd9",
    "frozen/pr4181/owner/MIXED-DISPATCH.json": "ab8c774b614730701435c0f5dc1bfba4a46d980690a1b6bc09225555ff9be6f4",
    "frozen/selected/ASSEMBLY.json": "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
    "frozen/selected/BIT-EXPECTED.json": "b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4",
}
THREE = {1: 2487, 2: 713, 3: 224, 4: 102, 5: 20, 8: 8}
FOUR = {1: 2489, 2: 713, 3: 227, 4: 99, 5: 20, 8: 8}
PREVIOUS = {1: 8060060, 2: 2310120, 3: 751813, 4: 327210,
            5: 66425, 8: 25920, 48: 138492}
PREVIOUS_LOWER = Q("0.001730979115670792472760")
PREVIOUS_UPPER = PREVIOUS_LOWER + Q(1, 10**24)
SCALE = 1 << 384
LOG_TERMS = 140
EXP_TERMS = 80


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hist(x):
    return {int(k): int(v) for k, v in x.items() if v}


def decimal(x):
    with localcontext() as ctx:
        ctx.prec = 90
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def ceildiv(a, b):
    return -((-a) // b)


def down(x):
    return (x.numerator * SCALE) // x.denominator


def up(x):
    return ceildiv(x.numerator * SCALE, x.denominator)


def unit_log(x):
    """Enclose ln(x), 1<=x<=2, in integer units of 2^-384.

    ln(x)=2 sum z^(2j+1)/(2j+1), z=(x-1)/(x+1)<=1/3.
    Every recurrence rounds out; the remaining positive tail is at most
    2*z^(2N+1)/((2N+1)*(1-z*z)).
    """
    need(1 <= x <= 2, "unit logarithm domain")
    z = (x - 1) / (x + 1)
    p, q = z.numerator, z.denominator
    lo, hi = down(z), up(z)
    sl = sh = 0
    for j in range(LOG_TERMS):
        sl += lo // (2*j + 1)
        sh += ceildiv(hi, 2*j + 1)
        lo = lo * p*p // (q*q)
        hi = ceildiv(hi * p*p, q*q)
    tail = ceildiv(2 * hi * q*q, (2*LOG_TERMS + 1) * (q*q-p*p))
    return 2*sl, 2*sh + tail


@lru_cache(None)
def log_interval(x):
    need(x >= 1, "positive logarithm domain")
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    lo, hi = unit_log(x)
    l2, h2 = unit_log(Q(2))
    return lo + k*l2, hi + k*h2


def exp_interval(lo, hi):
    """Enclose exp(x), x in [lo,hi]/SCALE, with positive Taylor terms."""
    need(0 <= lo <= hi < SCALE//100, "exponential domain x<0.01")
    tl = th = sl = sh = SCALE
    for j in range(1, EXP_TERMS):
        tl = tl * lo // (SCALE*j)
        th = ceildiv(th * hi, SCALE*j)
        sl += tl
        sh += th
    next_upper = ceildiv(th * hi, SCALE*EXP_TERMS)
    # Subsequent term ratios are < 1/2, so this geometric tail is valid.
    return Q(sl, SCALE), Q(sh + 2*next_upper, SCALE)


def moment(profile, m, live, a, fallback=Q(0)):
    """Normalized complete moment minus one; fallback is a rank-one count."""
    need(0 <= a < Q(1, 500), "certified arithmetic exponent domain")
    terms = {r: Q(n) for r, n in profile.items()}
    terms[1] = terms.get(1, Q(0)) + fallback
    lo = hi = Q(0)
    for rank, count in sorted(terms.items()):
        need(0 < rank < m and count >= 0, "positive proper child")
        ll, lh = log_interval(Q(m, rank))
        el, eh = exp_interval(down(a * Q(ll, SCALE)), up(a * Q(lh, SCALE)))
        weight = Q(count * rank, m*live)
        lo += weight * el
        hi += weight * eh
    return lo-1, hi-1


def bracket(profile, m, live, lower, upper, fallback=Q(0)):
    need(upper-lower == Q(1, 10**24), "adjacent root bracket")
    at = moment(profile, m, live, lower, fallback)
    nxt = moment(profile, m, live, upper, fallback)
    need(at[1] < 0 < nxt[0], "strict lower/upper moment signs")
    return {"lower_interval": list(map(str, at)), "upper_interval": list(map(str, nxt))}


def profile_check(profile, idle):
    full = Counter(idle)
    full.update({r: 2160*n for r, n in THREE.items()})
    full.update({r: 1080*n for r, n in FOUR.items()})
    need(dict(full) == profile, "all local, restoration and idle children included")
    need(sum(r*n for r, n in profile.items()) == 65088*360, "complete rank mass")
    need(73*(896*360)-sum(r*n for r, n in profile.items()) == 320*360, "rank deficit")
    need(max(profile) == 48 and 73**2 > 2*48**2, "proper contraction and halving guard")


def legacy(complex_rate, bit_rate):
    """Selected PR1094 convention, independently written in exact rationals."""
    eta = beta = Q(1, 10**24)
    s = min(bit_rate, (1-beta)*complex_rate) - Q(1, 10**27)
    a = Q(384599, 10**10)
    chain = [a]
    for _ in range(7):
        nxt = s*(1-s) + s*a
        need(0 < a < nxt < s < 1-nxt, "strict finite bootstrap")
        a = nxt
        chain.append(a)
    q = (1-2*eta)*a
    ceiling = (1-eta)*q/(1+q)
    scale = 10**18
    ticks = ceiling*scale
    kappa = Q(ceildiv(ticks.numerator, ticks.denominator)-1, scale)
    need(kappa < ceiling <= kappa+Q(1, scale), "strict legacy grid")
    return {"kappa": kappa, "ceiling": ceiling, "s": s,
            "chain": chain, "binding": "bit" if bit_rate <= (1-beta)*complex_rate else "complex"}


def modern(complex_rate, bit_rate):
    """Exact endpoint-DIG24 parameter algebra; analytic hypotheses are external."""
    r = Q(1, 10**104)
    delta = Q(1025, 1024)*r
    eps, beta = 1-delta, 1-3*delta
    b, q = complex_rate-r, complex_rate-2*r
    a = (q+b)/2
    saving = eps*q
    need(0 < q < a < b < complex_rate < bit_rate, "joint modern rates")
    need(0 < complex_rate-saving < Q(1, 10**70), "modern floor gap")
    need((complex_rate*10**70).denominator == 1, "modern endpoint on floor grid")
    kappa = Q((saving*10**70).__floor__(), 10**70)-Q(1, 10**46)
    need(kappa == complex_rate-Q(1, 10**70)-Q(1, 10**46), "derived modern kappa")
    need(1-eps-r > 0 and 1-beta-2*(1-eps) > 0, "gamma and membership costs")
    need(1-eps+q*beta-saving == delta*(1-2*q) > 0, "Gaussian cost exceeds main saving")
    # An explicit finite ordinary-bootstrap witness can reach the effective a.
    # It requires the inherited arbitrary-strict-rate bootstrap lemma, with
    # carried constants; the historical twelve-stage receipt alone is not it.
    s = complex_rate-r/2
    a0 = Q(384599, 10**10)
    aj = s-(s-a0)*s**38
    need(a < aj < s < bit_rate, "38-stage ordinary-rate existence witness")
    return {"kappa": kappa, "b": b, "q": q, "a": a, "epsilon": eps,
            "beta": beta, "r0": r, "ordinary_bootstrap_steps_sufficient": 38,
            "ordinary_bootstrap_s": s, "ordinary_bootstrap_final_above_effective": aj-a}


def reject(name, fn):
    try:
        fn()
    except ValueError:
        return name
    raise ValueError("accepted mutation: " + name)


def release_binding(work, profile, idle, complex_rate, bit_rate, modern_kappa, legacy_kappa):
    """Cross-bind actual emitted ledgers, without claiming to re-execute them."""
    work = work.resolve()
    admission = work / "admission"
    paths = {
        "result": admission / "RESULT.json",
        "release": admission / "release/RELEASE-RECEIPT.json",
        "strict_result": admission / "release/verify/RESULT.json",
        "assembly": admission / "release/verify/strict/ASSEMBLY.json",
        "invoice": admission / "release/verify/strict/global/audit/PREFIX-AND-INVOICE.json",
        "outer": admission / "release/outer-tmp/outer/LEDGER.json",
        "spec": admission / "package/new/SPEC.json",
        "contract": work / "source/new/MIXED-CONTRACT.json",
    }
    x = {k: read(p) for k, p in paths.items()}
    need(x["result"]["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE", "completed inherited release")
    need(x["release"]["status"] == "PASS_RELEASE", "completed release verifier")
    need(hist(x["result"]["profile"]) == profile and Q(x["result"]["kappa"]) == modern_kappa, "actual new result")
    need(Q(x["release"]["kappa_decimal"]) == modern_kappa, "actual modern release endpoint")
    selected = read(HERE / "frozen/pr4181/owner/MIXED-DISPATCH.json")
    need(sorted(x["contract"]["dispatch"]) == sorted(selected), "actual pooled selector")
    a = x["assembly"]
    need(hist(a["complex_profile"]) == profile and Q(a["complex_lower"]) == complex_rate, "actual complete complex profile")
    need(Q(a["bit_lower"]) == bit_rate and a["surcharge_model"] == {"complex": False, "bit": True}, "actual surcharge models")
    need(Q(a["kappa"]) == legacy_kappa, "actual legacy grid comparison")
    need(len(a["outer"]) == 47 and all(Q(v) > 0 for v in a["outer"].values()), "all 47 inherited outer rows")
    outer = x["outer"]["rows"]["struct_boundary_radix_union"]
    need(Q(outer["kappa"]["rational"]) == modern_kappa, "actual modern outer ledger")
    need(len(outer["strict_checks"]) == 63 and all(Q(v["rational"]) > 0 for v in outer["strict_checks"].values()), "all 63 modern outer rows")
    s = x["strict_result"]
    need(s["status"] == "PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION", "ordinary strict admission")
    expected = x["spec"]["expected"]
    need(s["controls"] == {"admission": expected["assembly_controls_rejected"], "bit": 12,
                            "controller": expected["mutations_rejected"], "independent_owner": 8,
                            "geometry": 6}, "actual generated mutation coverage")
    need(s["controls"]["admission"] > 119 and s["controls"]["controller"] > 25,
         "active third provider retains expanded control families")
    i = x["invoice"]
    need(i["physical"] == 323069 == 896*360+408+8+91+2 and i["live"] == 896*360, "all physical families")
    need(i["helpers"] == 408 and i["centres"] == 8 and i["private_zero_buffers"] == 91, "private and helper inventory")
    calls = i["selected_calls"]
    need(len(calls) == 3240 and len({(c["stage"], c["replica"]) for c in calls}) == 3240, "all literal calls")
    dispatch = {(s, r): p for s, r, p in selected}
    counts = Counter()
    local = Counter()
    for c in calls:
        pid, orientation = c["provider_id"], c["orientation"]
        need(dispatch[c["stage"], c["replica"]] == pid, "invoice follows pooled dispatch")
        p = i["providers"][pid]
        need(c["program_sha256"] == p["program_hashes"][orientation], "actual program binding")
        need(hist(p["paid_profile"]) == (FOUR if pid.endswith("-four") else THREE), "complete local rank bill")
        local.update(hist(p["paid_profile"]))
        counts[pid] += 1
        z = p["local"][orientation]
        need(z["all_exact_columns"] == 632 and z["dirty_helper_columns"] == 408 and z["all_dirty_helper_columns_restored"] and z["private_centres_and_coefficient_work_cleared"], "dirty and private restoration")
        for key in ("real_component_primitives", "coefficient_work_primitive_count", "macros", "pre_wrappers", "post_wrappers"):
            need(c[key] == z[key], "actual local cost: " + key)
    need(dict(counts) == i["provider_counts"] == {"gauge44": 1568, "extra": 592, "extra-four": 1080}, "actual three active provider counts")
    need(dict(local) == hist(i["selected_local_paid_profile"]), "local invoice sum")
    local.update(idle)
    need(dict(local) == profile, "actual local plus idle invoice")
    for field, key in (("selected_real_component_primitives", "real_component_primitives"), ("selected_coefficient_work_primitive_count", "coefficient_work_primitive_count"), ("selected_scalar_macros", "macros")):
        need(i[field] == sum(c[key] for c in calls), "full invoice sum: " + field)
    need(i["wrapper_elementary_factors_charged"] == 144*sum(c["pre_wrappers"]+c["post_wrappers"] for c in calls), "paid wrapper factors")
    b = i["blocknorm"]
    need(b["local_actual_prefix_bits"] == 95 and b["stock_l2_bits"] == 1323 and b["max_active_depth"] == 18, "actual prefix components")
    need(i["global_prefix_bits"] == 95+37+18+1323+1+4 == 1478 and i["charged_prefix_bits"] == 2048, "complete prefix reserve")
    f = i["finite"]
    need(f["physical_stock_bits"] == 2646 and f["physical_row_coefficient"] == 19549 < f["retained_row_coefficient"] == 20161, "complete stock and row reserve")
    need(f["required_C0_bits"] < f["C0_exponent"] == 210000 and all(i["strict_checks"].values()), "precision, tape, router and finite guards")
    return {"status": "COMPLETED_FINITE_RELEASE_RECEIPTS_BOUND",
            "files": {k: {"path": str(p.relative_to(work)), "sha256": sha(p)} for k, p in paths.items()},
            "provider_counts": dict(counts), "physical": i["physical"], "global_prefix_bits": i["global_prefix_bits"],
            "charged_prefix_bits": i["charged_prefix_bits"], "finite": f,
            "selected_real_component_primitives": i["selected_real_component_primitives"],
            "selected_coefficient_work_primitive_count": i["selected_coefficient_work_primitive_count"],
            "selected_scalar_macros": i["selected_scalar_macros"],
            "conservative_pervertex_used": i["conservative_pervertex_used"],
            "scope": "Cross-binding of the parent driver's actual complete finite release; this check neither reruns the engine nor proves its all-size premises."}


def certificate(release_work=None):
    for name, digest in PINS.items():
        need(sha(HERE/name) == digest, "frozen source pin: " + name)
    source = read(HERE / "frozen/pr4181/RESULT.json")
    selected = read(HERE / "frozen/selected/ASSEMBLY.json")
    bit = read(HERE / "frozen/selected/BIT-EXPECTED.json")["nine"]
    profile, idle = hist(source["profile"]), hist(source["idle"])
    provider_counts = Counter(p for _, _, p in read(HERE / "frozen/pr4181/owner/MIXED-DISPATCH.json"))
    need(dict(provider_counts) == {"gauge44": 1568, "extra": 592, "extra-four": 1080},
         "actual pooled dispatch has three active providers")
    profile_check(profile, idle)
    c, upper = Q(source["root_lower"]), Q(source["root_upper"])
    b = Q(bit["bit_lower"])
    need(b == Q(selected["bit_lower"]) and selected["surcharge_model"] == {"complex": False, "bit": True}, "selected BIT and native-complex models")
    candidate_signs = bracket(profile, 73, 896*360, c, upper)
    previous_signs = bracket(PREVIOUS, 73, 896*360, PREVIOUS_LOWER, PREVIOUS_UPPER)
    bh = hist(bit["profile"])
    fallback = Q(32*64**2*sum(bh.values()), 10**16)
    bit_signs = bracket(bh, 64, bit["bit"]["live"], b, b+Q(1, 10**24), fallback)
    need(b > upper, "retained BIT strictly above candidate complex root")
    old_legacy = legacy(Q(selected["complex_lower"]), b)
    need(old_legacy["kappa"] == Q(selected["kappa"]), "reproduce selected normalization")
    new_legacy, pred_legacy = legacy(c, b), legacy(PREVIOUS_LOWER, b)
    new_modern = modern(c, b)
    need(new_modern["kappa"] == Q(source["conditional_kappa"]), "pooled modern claim")
    gain = {r: PREVIOUS.get(r, 0)-profile.get(r, 0) for r in set(PREVIOUS)|set(profile)}
    gain = {r: n for r, n in gain.items() if n}
    need(gain == {1: 20, 3: 25, 4: -30, 5: 5}, "complete signed profile difference")
    need(3**15*5**5 < 4**24, "uniform power-gain derivative witness")
    controls = [
        reject("missing_idle_children", lambda: profile_check(profile, {})),
        reject("root_used_as_legacy_kappa", lambda: need(c < new_legacy["ceiling"], "legacy outer loss omitted")),
        reject("unpadded_root_used_as_modern_kappa", lambda: need(c == new_modern["kappa"], "strict modern padding omitted")),
        reject("bit_improvement_only_claims_joint_gain", lambda: need(legacy(Q(selected["complex_lower"]), Q("0.001737631818486007553483"))["kappa"] > Q(selected["kappa"]), "unchanged complex side still binds")),
        reject("bit_fallback_omitted", lambda: bracket(bh, 64, bit["bit"]["live"], b, b+Q(1, 10**24))),
        reject("old_profile_claims_new_root", lambda: bracket(PREVIOUS, 73, 896*360, c, upper)),
    ]
    out = {"status": "PASS_JOINT_CONDITIONAL_ARITHMETIC_NOT_SUPPLIER_ADMISSION", "source_sha256": PINS,
           "profile": profile, "idle": idle, "rank_mass": sum(r*n for r, n in profile.items()),
           "active_provider_counts": dict(provider_counts),
           "rank_deficit": 320*360, "child_count": sum(profile.values()),
           "complex_root_bracket": [str(c), str(upper)], "complex_signs": candidate_signs,
           "previous_complex_signs": previous_signs, "bit_endpoint": str(b), "bit_signs": bit_signs,
           "bit_fallback_rank_one_count": str(fallback), "bit_slack_above_candidate_upper": str(b-upper),
           "legacy": {**new_legacy, "kappa_decimal": decimal(new_legacy["kappa"]),
                      "gain_over_selected": new_legacy["kappa"]-Q(selected["kappa"]),
                      "gain_over_previous": new_legacy["kappa"]-pred_legacy["kappa"]},
           "modern": {**new_modern, "kappa_decimal": decimal(new_modern["kappa"]),
                      "gain_over_previous_upper": new_modern["kappa"]-PREVIOUS_UPPER},
           "uniform_profile_gain": {"previous_minus_new": gain, "covered_domain": "0 < a < 1",
                                    "exact_integer_witness": [3**15*5**5, 4**24],
                                    "argument": "F(p)=4*4^(-p)+5*(3/4)^p+(5/4)^p-6 is strictly convex; F(1)=0 and F'(1)<0. Therefore F(p)>0 for p=1-a<1. See RECURSION.md."},
           "controls": controls,
           "release_binding": {"status": "NOT_REQUESTED_ARITHMETIC_ONLY"},
           "all_size_admission": False, "selected_frontier_changed": False,
           "scope": "Exact complete-profile and joint-transfer arithmetic. A finite conditional improvement requires the new literal owner/operator and full ordinary/outer release. Uniform source/native generation, whole-call hosting, rounded cleanup, precision, fixed tapes, and the stated analytic transfer remain hypotheses."}
    if release_work is not None:
        out["release_binding"] = release_binding(release_work, profile, idle, c, b, new_modern["kappa"], new_legacy["kappa"])
        out["status"] = "PASS_JOINT_CONDITIONAL_ARITHMETIC_WITH_FINITE_RELEASE_BINDING"
    return out


def encode(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encode(v) for v in x]
    return x


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-work", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = encode(certificate(args.release_work))
    if args.output:
        with args.output.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        print(json.dumps(result, sort_keys=True))
    print(result["status"], "legacy_kappa=" + result["legacy"]["kappa_decimal"],
          "controls=" + str(len(result["controls"])), "all_size_admission=false")


if __name__ == "__main__":
    main()
