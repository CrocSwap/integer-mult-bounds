#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact, source-bound T16 moment-order census; not a construction replay.

mightyOil, with substantial OpenAI Codex (GPT-6 Astra) assistance.
The stop-loss/majorization theorem is predecessor work; see README.md.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRS = (1050, 1053, 1055, 1056, 1061, 1063, 1065, 1068, 1074, 1082, 1087, 1094)
BASE = "dd6403f774a0891093a006ae9716c02e371b1fdb"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def profile(raw, m=73):
    result = {}
    for key, count in raw.items():
        rank = int(key)
        require(str(rank) == str(key) and 0 < rank < m, "rank domain")
        require(type(count) is int and count >= 0, "count domain")
        if count:
            result[rank] = count
    require(result, "empty profile")
    return result


def mass(h):
    return sum(r * n for r, n in h.items())


def delta(new, old):
    return {r: new.get(r, 0) - old.get(r, 0)
            for r in sorted(new.keys() | old.keys())
            if new.get(r, 0) != old.get(r, 0)}


def top_sum(h, k):
    total = 0
    for r in sorted(h, reverse=True):
        used = min(k, h[r])
        total += used * r
        k -= used
    return total  # The remaining entries are zero padding.


def sorted_prefix_majorizes(new, old):
    """Independent coordinate-count implementation of zero-padded majorization."""
    cuts = {0, sum(new.values()), sum(old.values())}
    for h in (new, old):
        count = 0
        for r in sorted(h, reverse=True):
            count += h[r]
            cuts.add(count)
    return all(top_sum(new, k) >= top_sum(old, k) for k in cuts)


def compare(new, old):
    require(mass(new) == mass(old), "unequal rank mass")
    d = delta(new, old)
    knots = sorted({0, *new, *old})
    gaps = {t: sum(n * min(r, t) for r, n in d.items()) for t in knots}
    forward = all(g <= 0 for g in gaps.values())
    reverse = all(g >= 0 for g in gaps.values())
    require(forward == sorted_prefix_majorizes(new, old), "dual certificate disagreement")
    require(reverse == sorted_prefix_majorizes(old, new), "reverse certificate disagreement")
    status = ("equal" if not d else "new_strictly_better_all_a" if forward
              else "old_strictly_better_all_a" if reverse else "majorization_inconclusive")
    return {"status": status, "delta": d, "truncated_rank_gaps": gaps}


def integer_root_floor(n, degree):
    require(n >= 0 and degree > 0, "root domain")
    lo, hi = 0, 1 << ((n.bit_length() + degree - 1) // degree)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if pow(mid, degree) <= n:
            lo = mid
        else:
            hi = mid
    require(pow(lo, degree) <= n < pow(lo + 1, degree), "integer root enclosure")
    return lo


@lru_cache(maxsize=None)
def rank_power_interval(rank, a, bits=40):
    """Enclose rank**(1-a) by integer powers only; no log/root solver reuse."""
    exponent = 1 - a
    require(0 < exponent < 1, "exponent domain")
    p, q, scale = exponent.numerator, exponent.denominator, 1 << bits
    radicand = pow(rank, p) * pow(scale, q)
    lower = integer_root_floor(radicand, q)
    upper = lower if pow(lower, q) == radicand else lower + 1
    return Q(lower, scale), Q(upper, scale)


def sign_witness(d, a):
    lo = hi = Q(0)
    terms = []
    for rank, count in sorted(d.items()):
        lower, upper = rank_power_interval(rank, a)
        lo += count * (lower if count > 0 else upper)
        hi += count * (upper if count > 0 else lower)
        terms.append({"rank": rank, "count": count, "lower": str(lower), "upper": str(upper)})
    sign = "negative" if hi < 0 else "positive" if lo > 0 else "zero" if lo == hi == 0 else "undecided"
    return {"a": str(a), "quantity": "sum delta_n[r] * r**(1-a)",
            "lower": str(lo), "upper": str(hi), "sign": sign, "terms": terms}


def single_positive_tangent(d):
    """Certify a non-majorization order by a strictly concave exponential sum.

    If F(p) = c*r**p - sum a_s*s**p has F(1)=0, then
    G(p)=F(p)/r**p is strictly concave. G'(1)>0 is exactly the
    integer-product comparison below, so G(p)<0 whenever p<1.
    """
    positive = [(r, n) for r, n in d.items() if n > 0]
    if len(positive) != 1 or sum(r * n for r, n in d.items()) != 0:
        return None
    rank, count = positive[0]
    left = pow(rank, rank * count)
    right = 1
    for r, n in d.items():
        if n < 0:
            right *= pow(r, -r * n)
    if left <= right:
        return None
    return {"positive_rank": rank, "positive_count": count,
            "derivative_log_numerator_product": str(left),
            "derivative_log_denominator_product": str(right),
            "strict_integer_gap": str(left - right),
            "consequence": "F(p)<0 for every real p<1; in particular 0<a=1-p<1"}


def check_pair_contract(new, old):
    for key in ("m", "live", "native_surcharge", "local_profile", "calls",
                "charged_prefix_bits", "physical_row_coefficient", "bit_supplier"):
        require(new[key] == old[key], "changed contract: " + key)
    require(new["native_surcharge"] is False, "native-only comparison")
    require(mass(new["profile"]) == mass(old["profile"]), "unequal rank mass")


def read_sources():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    require(pins["base_commit"] == BASE, "base pin")
    for entry in pins["files"]:
        if entry["usage"] == "input":
            require(sha((ROOT / entry["path"]).read_bytes()) == entry["sha256"], "source hash: " + entry["path"])
    heads = json.loads((ROOT / "research/community-batch1099-audit/PLAN.json").read_text())["heads"]
    records = {}
    for pr in PRS:
        path = ROOT / f"research/community-batch1099-audit/replay-{pr}.tar.gz"
        prefix = "strict/" if pr in (1056, 1063, 1082, 1094) else ""
        names = ("ASSEMBLY.json", "INDEPENDENT-T16.json", "global/PLAN.json")
        with tarfile.open(path) as archive:
            blobs = {n: archive.extractfile(prefix + n).read() for n in names}
        assembly, owner, plan = [json.loads(blobs[n]) for n in names]
        h = profile(assembly["complex_profile"])
        require(h == profile(owner["profile"]) == profile(plan["profile"]), "profile receipt binding")
        local = profile(owner["local_profile"])
        expected = Counter({r: owner["calls"] * n for r, n in local.items()})
        expected.update(profile(owner["idle"]))
        require(h == expected, "local plus idle decomposition")
        require((plan["M"], plan["live"], owner["live"], owner["calls"], owner["rank_mass"], owner["deficit"])
                == (73, 14336, 14336, 144, 1041408, 5120), "T16 scalar contract")
        require(mass(h) == 73 * owner["live"] - owner["deficit"], "rank mass invoice")
        require(assembly["surcharge_model"] == {"complex": False, "bit": True}, "surcharge contract")
        records[pr] = {"head": heads[str(pr)], "archive": str(path.relative_to(ROOT)),
            "member_sha256": {prefix + n: sha(b) for n, b in blobs.items()},
            "profile": h, "idle": owner["idle"], "local_profile": local,
            "m": plan["M"], "live": owner["live"], "calls": owner["calls"],
            "native_surcharge": False, "charged_prefix_bits": owner["charged_prefix_bits"],
            "physical_row_coefficient": owner["physical_row_coefficient"],
            "bit_supplier": assembly["bit_supplier"], "complex_lower": assembly["complex_lower"],
            "kappa": assembly["kappa"], "count": sum(h.values()), "mass": mass(h)}
    return records


def controls(records):
    rejected = []
    def reject(name, fn):
        try:
            fn()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("control incorrectly accepted: " + name)
    reject("rank_zero", lambda: profile({0: 1}))
    reject("rank_at_ambient_dimension", lambda: profile({73: 1}))
    reject("negative_count", lambda: profile({1: -1}))
    reject("boolean_count", lambda: profile({1: True}))
    reject("unequal_mass", lambda: compare({1: 1}, {1: 2}))
    for key, value in (("m", 74), ("live", 14337), ("native_surcharge", True),
                       ("charged_prefix_bits", 1024), ("physical_row_coefficient", 16470),
                       ("calls", 145), ("bit_supplier", {}), ("local_profile", {1: 1})):
        mutant = dict(records[1094], **{key: value})
        reject("changed_" + key, lambda mutant=mutant: check_pair_contract(mutant, records[1094]))
    require(compare({1: 1, 4: 1}, {2: 1, 3: 1})["status"] == "new_strictly_better_all_a", "spread positive control")
    require(compare({2: 1, 3: 1}, {1: 1, 4: 1})["status"] == "old_strictly_better_all_a", "reversed dominance")
    require(compare({1: 2}, {1: 2})["status"] == "equal", "strictness control")
    require(compare({4: 1}, {1: 4})["status"] == "new_strictly_better_all_a", "zero-padding control")
    for a in (Q(0), Q(1), Q(-1, 2), Q(3, 2)):
        reject("exponent_" + str(a), lambda a=a: rank_power_interval(3, a))
    witness = sign_witness({4: -3, 9: 2}, Q(1, 2))
    require(witness["lower"] == witness["upper"] == "0", "signed interval control")
    require(single_positive_tangent({1: -7, 3: -4, 7: 5, 16: -1}) is not None,
            "single-positive tangent positive control")
    # The maintainer's PR1048 counterexample has the opposite derivative sign.
    wrong_direction = {1: -14, 2: 15, 4: -4}
    require(single_positive_tangent(wrong_direction) is None, "wrong derivative admitted")
    require(sign_witness(wrong_direction, Q(1, 650))["sign"] == "positive"
            and sign_witness(wrong_direction, Q(1, 2))["sign"] == "negative",
            "tangent false-positive negative control")
    require(single_positive_tangent({1: -6, 3: -4, 7: 5, 16: -1}) is None,
            "tangent unequal mass admitted")
    require(single_positive_tangent({1: 7, 3: -3, 7: -2, 16: 1}) is None,
            "tangent multiple-positive ranks admitted")
    return rejected


def build_report():
    records = read_sources()
    order = sorted(PRS, key=lambda pr: Q(records[pr]["complex_lower"]))
    pairs = []
    for old, new in itertools.combinations(order, 2):
        check_pair_contract(records[new], records[old])
        comparison = compare(records[new]["profile"], records[old]["profile"])
        comparison.update(old=old, new=new)
        comparison["final_order"] = comparison["status"]
        if comparison["status"] == "majorization_inconclusive":
            comparison["sign_witnesses"] = [sign_witness(comparison["delta"], a)
                for a in (Q(1, 650), Q(1, 2), Q(64, 65))]
            require(all(w["sign"] != "undecided" for w in comparison["sign_witnesses"]), "unresolved witness")
            tangent = single_positive_tangent(comparison["delta"])
            if tangent is not None:
                comparison["tangent_certificate"] = tangent
                comparison["final_order"] = "new_strictly_better_all_a"
            elif {w["sign"] for w in comparison["sign_witnesses"]} == {"negative", "positive"}:
                comparison["final_order"] = "certified_crossing"
        pairs.append(comparison)
    require(len(pairs) == 66, "complete pair coverage")
    crossed = [p for p in pairs if p["status"] == "majorization_inconclusive"
               and {w["sign"] for w in p["sign_witnesses"]} == {"negative", "positive"}]
    require(any((p["old"], p["new"]) == (1050, 1053) for p in crossed), "named crossing")
    require(any((p["old"], p["new"]) == (1082, 1087) for p in crossed), "second named crossing")
    require(all(p["final_order"] in ("new_strictly_better_all_a", "certified_crossing") for p in pairs),
            "complete classification")
    return {"status": "PASS_T16_MOMENT_ORDER_AUDIT", "base": BASE, "seed": 65,
            "domain": list(PRS), "increasing_recorded_endpoint_order": order,
            "records": records, "pairs": pairs,
            "majorization_summary": dict(Counter(p["status"] for p in pairs)),
            "summary": dict(Counter(p["final_order"] for p in pairs)),
            "certified_crossings": [[p["old"], p["new"]] for p in crossed],
            "rejected_controls": controls(records),
            "scope": "Exact moment-order census on authenticated historical receipts; inherited construction, physical hosting, exact root and all-size evidence is reused, not replayed. No new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a fresh receipt instead of checking EVIDENCE.json")
    args = parser.parse_args()
    report = build_report()
    raw = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.write:
        args.write.write_text(raw)
    else:
        require(json.loads((HERE / "EVIDENCE.json").read_text()) == json.loads(raw), "recorded evidence mismatch")
    print(report["status"], json.dumps(report["summary"], sort_keys=True),
          "crossings=" + str(len(report["certified_crossings"])), "rejected_controls=" + str(len(report["rejected_controls"])))


if __name__ == "__main__":
    main()
