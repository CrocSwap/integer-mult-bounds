"""Check sealed evidence bindings and the exact signed-invoice price comparison."""
import argparse
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
RECEIPTS = ROOT / "receipts"
BASE = "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd"
CANDIDATE = "aa83ede3e5833d43606d711068619db0dc28cbcd858dd11e8e89da6d09883916"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"


def read(name):
    return json.loads((RECEIPTS / name).read_bytes())


def check_manifest():
    seen = set()
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        relative = Path(name)
        assert not relative.is_absolute() and ".." not in relative.parts and relative not in seen
        seen.add(relative)
        source = ROOT / relative
        assert source.resolve() == source and sha256(source.read_bytes()).hexdigest() == digest, name
    actual = {p.relative_to(ROOT) for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    assert actual == seen | {Path("SHA256SUMS")}, "Complete path-keyed package inventory"


def check_paid(before, after):
    ranks = set(before) | set(after)
    delta = {rank: after.get(rank, 0) - before.get(rank, 0) for rank in ranks
             if after.get(rank, 0) != before.get(rank, 0)}
    assert delta == {"1": -34, "2": 17}
    assert sum(before.values()) == 110366 and sum(after.values()) == 110349


def signed_moment(invoice):
    ranks = set(invoice["T"]) | set(invoice["P"])
    return {int(rank): invoice["T"].get(rank, 0) - invoice["P"].get(rank, 0) for rank in ranks}


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    check_manifest()
    native, signed, final, baseline = (read(name) for name in (
        "NATIVE.json", "SIGNED.json", "FINAL.json", "7605-replay.json"))
    assert native["status"] == "PASS_MAIN46_COMPLETE_NATIVE"
    assert signed["status"] == "PASS_MAIN46_COMPLETE_SIGNED_APPLICATION"
    assert final["status"] == "PASS_MAIN46_FINAL_APPLICATION"
    assert signed["source_head"] == baseline["head"] == "e1d2756eecf03e146338239fee81772a99ba8d4c"
    assert signed["component_head"] == "93fded4340bb08bc1f99d6f18e47a198456a41df"
    assert baseline["registered_final"]["candidate_canonical_sha256"] == BASE
    assert signed["caller_sha256"] == final["caller_sha256"] == baseline["caller"]["sha256"] == CALLER
    assert native["word_canonical_sha256"] == final["candidate_canonical_sha256"] == CANDIDATE
    exact = read("EXACT.json")
    assert exact["candidate_canonical_sha256"] == CANDIDATE and exact["owned_clear_rows"] == 74
    assert exact["owned_interface_row_checks"] == 1599 and exact["public_endpoint_rows"] == 1501
    assert native["charts"]["main46_composed_columns"] == native["charts"]["main46_composed_adjoint_columns"] == 512
    assert all(native["controls"][name] for name in ("missing_main46_paid_move", "wrong_main46_move_source",
                                                    "missing_main46_coframe_correction"))
    price = signed["price"]
    old, new = (price[key] for key in ("before", "after"))
    audited = read("INVOICE.json")
    assert old["P"] == audited["old_full_paid"] and new["P"] == audited["new_full_paid"]
    assert old["T"] == new["T"] == audited["productive_targets"] and sum(new["T"].values()) == 22461
    assert old["S"] == new["S"] == 1424 and not new["empty_root_credits"]
    check_paid(old["P"], new["P"])
    mutated = deepcopy(new["P"])
    mutated["2"] -= 1
    try:
        check_paid(old["P"], mutated)
    except AssertionError:
        pass
    else:
        raise AssertionError("Missing rank-two paid position control was accepted")

    cost = run_path(str(ROOT / "checks/pricing.py"))["cost"]
    claim = Fraction(final["framework_claim"])
    old_claim = Fraction(final["comparator_claim"])
    assert claim == Fraction(signed["claim"]) == Fraction("0.003650666180757")
    assert old_claim == Fraction(baseline["registered_final"]["framework_claim"])
    assert final["comparator_crossing"] == baseline["registered_final"]["raw_crossing"]
    assert claim > Fraction(final["comparator_crossing"][1]) > old_claim
    assert cost(signed_moment(old), claim)[1] < 0 < cost(signed_moment(new), claim)[0]
    assert claim - old_claim == Fraction("0.000000221936041")
    assert final["ordinary_bound"] == audited["ordinary_projected_after"] == 782685204
    assert final["precision_c"] == 2430 and final["tape"]["elementary_records_upper"] == 25448575552
    assert final["signed_physical_map_count"] == 3040
    print("PASS signed invoice price, receipt bindings and missing-paid control")


if __name__ == "__main__":
    main()
