"""Close the role 902 gate against completed native, signed and independent receipts."""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path

ASSUMPTIONS = ["native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery"]
WORD = "bdecd5cc1cb9f164dc695ce07a07d5d44e9961996fcdfa4d77b4092fecbda745"
PACKED_WORD = "6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
PREDECESSOR = "d6be7d620c9c8337104daeb09fe01196eced5fe3"
COMPONENT = "71f5acb0409daf208a865482f3349049dbd3251c"
PREDECESSOR_CLAIM = Q(".003647969120276")
PREDECESSOR_APPLICATION = "d9b5d292abb87c87eb3fd3f53501e14d77629ca4adca77a527ff2cf5b58df514"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def unique(pairs):
    record = dict(pairs)
    assert len(record) == len(pairs), "duplicate JSON key"
    return record


def read(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def counts(profile):
    result = Counter({int(r): n for r, n in profile.items()})
    assert min(result) > 0 and all(n > 0 for n in result.values())
    return result


def difference(after, before):
    result = counts(after)
    result.subtract(counts(before))
    return {r: d for r, d in result.items() if d}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="isolated output with producer54 stages and wrapper receipts")
    parser.add_argument("recurrence", type=Path, help="fresh check_recurrence.py output")
    parser.add_argument("predecessor", type=Path, help="published exact #7544 final application")
    parser.add_argument("--pinned-native", type=Path,
                        help="native receipt compared by the mandatory separate native stage")
    args = parser.parse_args()
    root = args.root / "producer54"
    native_path = root / "validation_native/NATIVE-RESULT.json"
    signed_path = root / "validation_signed/RESULT.json"
    word_path = root / "reroute/WORD.json.gz"
    native, signed = read(native_path), read(signed_path)
    recurrence, old = read(args.recurrence), read(args.predecessor)
    assert digest(args.predecessor) == PREDECESSOR_APPLICATION
    assert old["caller_sha256"] == CALLER and Q(old["claim"]) == PREDECESSOR_CLAIM
    assert digest(word_path) == PACKED_WORD and sha256(decompress(word_path.read_bytes())).hexdigest() == WORD
    assert native["status"] == "PASS_ROLE902_COMPLETE_NATIVE"
    assert signed["status"] == "PASS_ROLE902_COMPLETE_SIGNED_APPLICATION"
    assert signed["source_head"] == PREDECESSOR and signed["component_head"] == COMPONENT
    assert signed["caller_sha256"] == CALLER and signed["assumptions"] == ASSUMPTIONS
    assert native["word_canonical_sha256"] == WORD and not native["native"]["bad_inputs"]
    assert native["native"]["lifetimes"] == 74 and native["native"]["owned_peak"] == 50
    assert native["derived_grid"]["fractional_bits"] == 25 and native["derived_grid"]["odd_scale"] == 1125
    assert native["physical_checks"] == ["verify_host3_odd.py", "physical.py"]
    for name in ("wrong_role902_move_source", "missing_role902_paid_move"):
        assert native["controls"][name]
    assert all(native["controls"].values()) and native["charts"]["wrong_phase_rejected"]
    assert native["charts"]["role902_exact_forward_and_adjoint_columns"] == 512
    pairs = {tuple(c["pair"]): c for c in native["charts"]["all_affected_pairs"]}
    for pair, rank in (((618, 789), 2), ((789, 913), 2), ((618, 913), 4)):
        assert pairs[pair]["rank"] == rank
        assert pairs[pair]["absolute_phase_verified"] and pairs[pair]["columns"] == 512
    receipt_stages = [("signed", signed["status"])]
    if args.pinned_native is None:
        receipt_stages.append(("native", native["status"]))
    else:
        assert native_path.read_bytes() == args.pinned_native.read_bytes()
        assert not (args.root / "receipts/native.json").exists()
    for stage, expected in receipt_stages:
        wrapper = read(args.root / "receipts" / f"{stage}.json")
        assert wrapper["exit"] == 0 and wrapper["expected_marker"] == expected
        assert expected in (args.root / "receipts" / f"{stage}.stdout").read_text()

    assert recurrence["status"] == "PASS_ROLE902_INDEPENDENT_DIRECTED_RECURRENCE"
    assert recurrence["inputs"]["new_word_canonical"] == WORD
    assert recurrence["inputs"]["caller"] == CALLER
    price = signed["price"]
    before, after, gate = (price[key] for key in ("before", "after", "gate"))
    for name, complete in (("before", before), ("after", after)):
        assert all(complete[key] == recurrence[name][key] for key in ("P", "T", "S", "empty_root_credits"))
    assert price["old_native"] == old["candidate_canonical_sha256"] and price["new_native"] == WORD
    assert price["signed_incumbent_rejects_new_claim"] and price["native_baseline_rejects_new_claim"]
    assert recurrence["old_raw_crossing_rejects_new_claim"]
    claim = Q(signed["claim"])
    assert claim == Q(price["price"]["claim_decimal"]) == Q(gate["claim"]) == Q(recurrence["claim"]) > PREDECESSOR_CLAIM
    old_lo, old_hi = map(Q, old["raw_crossing"])
    assert [old_lo, old_hi] == list(map(Q, recurrence["strict_old_raw_crossing"]))
    lo, hi = map(Q, gate["raw_bracket"])
    ilo, ihi = map(Q, recurrence["strict_new_raw_crossing"])
    assert old_lo < old_hi < claim < min(lo,ilo) <= max(lo,ilo) < min(hi,ihi)
    assert Q(gate["tested"]) == Q(recurrence["tested"]) < Q(gate["BIT_pin"]) == Q(".00376669")

    delta = difference(after["P"], before["P"])
    assert delta == {2: -34, 4: 17} and after["T"] == before["T"]
    assert before["S"] == after["S"] == 1424
    assert before["empty_root_credits"] == after["empty_root_credits"] == 0
    assert sum(counts(after["P"]).values()) == 110468 and sum(counts(after["T"]).values()) == 22461

    checks = signed["checks"]
    partial = checks["ODD-ADMISSION-PARTIAL.json"]
    assert partial["invoice"] == after and partial["compiler_outer"] == gate
    outer = gate["outer"]
    assert outer["strict_count"] == 54 and outer["functional_count"] == 4
    assert Q(outer["minimum_margin"]) > 0 and outer["BIT_just_below_effective_rejected"]
    for key in ("strict_count", "functional_count", "minimum_margin", "BIT_just_below_effective_rejected"):
        assert outer[key] == recurrence["gate"]["outer"][key]
    ordinary = partial["ordinary"]["conservative_total"]
    assert ordinary < 10**9
    joined = checks["ODD-8X9-APPLICATION-CHECKS.json"]
    assert joined["status"] == "PASS_8X9_EXACT_COMPONENT_APPLICATION_CHECKS"
    assert joined["native_canonical_sha256"] == WORD and joined["caller_sha256"] == CALLER
    catalogue = signed["catalogue"]
    assert catalogue and all(c["catalogue_size"] == sum(x["checked_maps"] for x in catalogue) for c in catalogue)
    assert sum(c["main_boundary_pairs"] for c in catalogue) == 104
    tape = checks["ODD-FIXED-TAPE-COUNTS.json"]
    precision = checks["ODD-PRECISION.json"]
    assert tape["context_c"] == precision["context_c"] and tape["native_invocations"] == 17
    tape_counts = {key: tape[key] for key in ("native_invocations", "monomial_map_slots",
                                             "elementary_records_upper", "scalar_services_upper")}
    headroom = recurrence["headroom"]
    assert headroom["ambient_cap"] == 145 and headroom["remainder_rank_mass"] == 109088
    floor, ceiling = map(Q, headroom["raw_ceiling"])
    assert claim < floor < ceiling < Q(1,32)
    gain = claim - PREDECESSOR_CLAIM
    assert Q(recurrence["gain"]) == gain
    ratio = 100 * gain / PREDECESSOR_CLAIM
    assert Q(recurrence["percentage_gain"]) == ratio
    print(json.dumps({
        "status": "PASS_ROLE902_FINAL_APPLICATION",
        "candidate_canonical_sha256": WORD,
        "caller_sha256": CALLER,
        "predecessor_head": PREDECESSOR,
        "predecessor_claim": str(PREDECESSOR_CLAIM),
        "claim": str(claim),
        "claim_decimal": f"0.{int(claim*10**15):015d}",
        "gain_over_7544": str(gain),
        "relative_gain_percent_over_7544": str(ratio),
        "raw_crossing": [str(max(lo,ilo)), str(min(hi,ihi))],
        "independent_raw_crossing": recurrence["strict_new_raw_crossing"],
        "signed_paid_delta": delta,
        "paid_calls": sum(counts(after["P"]).values()),
        "productive_calls": sum(counts(after["T"]).values()),
        "ordinary_bound": ordinary,
        "ordinary_change_over_7544": ordinary - old["ordinary_bound"],
        "precision_c": precision["context_c"],
        "tape": tape_counts,
        "tape_change_over_7544": {k: n - old["tape"][k] for k, n in tape_counts.items()},
        "outer": outer,
        "headroom": dict(headroom, claimed_fraction=[str(claim/ceiling),str(claim/floor)]),
        "signed_physical_map_count": sum(x["checked_maps"] for x in catalogue),
        "native_result_sha256": digest(native_path),
        "signed_result_sha256": digest(signed_path),
        "independent_recurrence_sha256": digest(args.recurrence),
        "assumptions": ASSUMPTIONS,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    assert __debug__
    main()
