"""Assemble composite qualification from completed native and signed checks."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from runpy import run_path
import gzip
import json

ASSUMPTIONS = ["native_all_columns", "owned_erasure", "compiler",
               "precision_tape", "analytic_recovery"]
WORD_SHA = "2acc6bfd2807239fafdb3f9e09ff8ad34703df958496590ab657ef0b9ac93aef"
CALLER_SHA = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
TARIFF_SHA = "60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5"


def read(path):
    return json.loads(path.read_text())


def packing_ceiling(tariff, paid, targets, native, claim):
    cap = 145
    fixed = Counter({rank: 17 * count for rank, count in native.items()})
    remainder = Counter(paid)
    remainder.subtract(fixed)
    assert all(1 <= rank <= cap and count >= 0 for rank, count in remainder.items())
    mass = sum(rank * count for rank, count in remainder.items())
    assert mass == 109088
    relaxed = Counter(targets)
    relaxed.subtract(fixed)
    relaxed[cap] -= Q(mass, cap)

    end = Q(1, 32)
    derivative = (0, 0)
    for rank, count in relaxed.items():
        value = tariff["mul"](tariff["power"](rank, end if count >= 0 else 0),
                              tariff["log"](rank))
        derivative = tariff["add"](derivative, tariff["smul"](value, -count))
    assert derivative[1] < 0
    lo, hi = claim, end
    assert tariff["moment"](relaxed, lo)[0] > 0 > tariff["moment"](relaxed, hi)[1]
    while hi - lo > Q(1, 10**12):
        mid = (lo + hi) / 2
        low, high = tariff["moment"](relaxed, mid)
        if low > 0:
            lo = mid
        elif high < 0:
            hi = mid
        else:
            raise AssertionError("Unresolved rigorous ceiling midpoint")
    return {"ambient_cap": cap, "remainder_rank_mass": mass,
            "raw_ceiling": [str(lo), str(hi)],
            "claimed_fraction": [str(claim / hi), str(claim / lo)]}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("tariff", type=Path)
    args = parser.parse_args()
    assert sha256(args.tariff.read_bytes()).hexdigest() == TARIFF_SHA
    tariff = run_path(str(args.tariff))

    root = args.root / "producer54"
    native_path = root / "validation_native/NATIVE-RESULT.json"
    signed_path = root / "validation_signed/RESULT.json"
    native, signed = read(native_path), read(signed_path)
    word_bytes = gzip.decompress((root / "reroute/WORD.json.gz").read_bytes())
    assert sha256(word_bytes).hexdigest() == native["word_canonical_sha256"] == WORD_SHA
    assert native["status"] == "PASS_COMPOSED_7481_7542_COMPLETE_NATIVE"
    assert signed["status"] == "PASS_COMPOSED_7481_7542_COMPLETE_SIGNED_APPLICATION"
    assert signed["source_head"] == "89eaa9d8cae37c1540de98f2d29a3abaabb96a2b"
    assert signed["component_head"] == "71f5acb0409daf208a865482f3349049dbd3251c"
    assert signed["caller_sha256"] == CALLER_SHA
    assert signed["assumptions"] == ASSUMPTIONS
    price = signed["price"]
    assert price["new_native"] == WORD_SHA
    assert price["signed_incumbent_rejects_new_claim"]
    claim = Q(signed["claim"])
    assert claim == Q(price["gate"]["claim"])
    old = Q("0.003647081039689")
    peer = Q("0.0036475398277")
    assert old < peer < Q("0.0036475398278") < claim
    before, after = price["before"], price["after"]
    assert before["T"] == after["T"]
    assert before["S"] == after["S"] == 1424
    assert before["empty_root_credits"] == after["empty_root_credits"] == 0
    totals = lambda values: {int(rank): count for rank, count in values.items()}
    paid = totals(after["P"])
    change = Counter(paid)
    change.subtract(totals(before["P"]))
    delta = {k: v for k, v in change.items() if v}
    assert delta == {1: -34, 5: -17, 7: 17}
    targets = totals(after["T"])
    assert sum(paid.values()) == 110485 and sum(targets.values()) == 22461
    partial = signed["checks"]["ODD-ADMISSION-PARTIAL.json"]
    assert partial["invoice"] == after and partial["compiler_outer"] == price["gate"]
    outer = price["gate"]["outer"]
    assert outer["strict_count"] == 54 and outer["functional_count"] == 4
    assert Q(outer["minimum_margin"]) > 0 and outer["BIT_just_below_effective_rejected"]
    ordinary = partial["ordinary"]["conservative_total"]
    assert ordinary < 10**9
    joined = signed["checks"]["ODD-8X9-APPLICATION-CHECKS.json"]
    assert joined["status"] == "PASS_8X9_EXACT_COMPONENT_APPLICATION_CHECKS"
    assert joined["native_canonical_sha256"] == WORD_SHA and joined["caller_sha256"] == CALLER_SHA
    assert all(c["catalogue_size"] == sum(x["checked_maps"] for x in signed["catalogue"])
               for c in signed["catalogue"])
    assert sum(c["main_boundary_pairs"] for c in signed["catalogue"]) == 104
    tape = signed["checks"]["ODD-FIXED-TAPE-COUNTS.json"]
    precision = signed["checks"]["ODD-PRECISION.json"]
    assert tape["context_c"] == precision["context_c"]
    assert native["derived_grid"]["fractional_bits"] == 25
    assert native["derived_grid"]["odd_scale"] == 1125
    assert native["native"]["lifetimes"] == 74 and native["native"]["owned_peak"] == 50
    assert not native["native"]["bad_inputs"]

    print(json.dumps({
        "status": "PASS_COMPOSED_7481_7542_FINAL_APPLICATION",
        "candidate_canonical_sha256": WORD_SHA,
        "caller_sha256": CALLER_SHA,
        "claim": str(claim),
        "claim_decimal": price["price"]["claim_decimal"],
        "predecessor_claim": str(old),
        "gain_over_7481": str(claim - old),
        "relative_gain_percent_over_7481": str(100 * (claim - old) / old),
        "pending_peer_claim": str(peer),
        "gain_over_peer_claim": str(claim - peer),
        "raw_crossing": price["gate"]["raw_bracket"],
        "signed_paid_delta": delta,
        "paid_calls": sum(paid.values()),
        "productive_calls": sum(targets.values()),
        "ordinary_bound": ordinary,
        "ordinary_increase_over_7481": ordinary - 782785912,
        "precision_c": precision["context_c"],
        "tape": {key: tape[key] for key in ("native_invocations", "monomial_map_slots",
                                             "elementary_records_upper", "scalar_services_upper")},
        "outer": outer,
        "headroom": packing_ceiling(tariff, paid, targets, totals(native["native"]["paid"]), claim),
        "native_result_sha256": sha256(native_path.read_bytes()).hexdigest(),
        "signed_result_sha256": sha256(signed_path.read_bytes()).hexdigest(),
        "assumptions": ASSUMPTIONS,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    assert __debug__
    main()
