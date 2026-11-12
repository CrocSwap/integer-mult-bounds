"""Price a fixed-paid 4+5 split before decoding the exact #7334 word."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
WORD = "4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a"
PINS = {
    "inputs/ADMITTED.json": "c95300e9bca27e44a25c82d794f88cbf70757c142806b0e4c590ea29feb81a13",
    "inputs/RANK-STOCK.json": "4a7841699dd17688f6aada5c902a2a91e94558b2b1b4460c46b0e55aa95b3f9f",
    "inputs/R72-OCCUPANCY.json": "4c349e06b22bfebb431fab1c9ae04f0e798f398acc6fdd99591b49b1c95ef6ca",
    "inputs/READBACK.json": "337668788fb39ec9575887f9c5faf438a880471f78d936357dabf7deeac5de82",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
MOONSHOT = Fraction("0.0040075385047236")


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def main():
    documents = {}
    for rel, pin in PINS.items():
        raw = (ROOT / rel).read_bytes()
        if sha256(raw).hexdigest() != pin:
            raise ValueError(f"Changed input {rel}")
        if rel.endswith(".json"):
            documents[Path(rel).name] = loads(raw, object_pairs_hook=unique)
    admitted, stock, occupancy, readback = (documents[name] for name in (
        "ADMITTED.json", "RANK-STOCK.json", "R72-OCCUPANCY.json", "READBACK.json"))
    assert admitted["head"] == stock["head"] == occupancy["head"] == readback["head"] == HEAD
    assert admitted["exit"] == 0 and admitted["status"] == "independently_reproduced_comparable"
    assert len(admitted["stages"]) == 4 and admitted["inputs"]["WORD.json.gz"] == WORD
    assert occupancy["pins"]["inputs/7334-WORD.json.gz"] == WORD
    assert readback["word_git_blob"] == stock["word_git_blob"] if "word_git_blob" in readback else stock["word_git_blob"] == "73f43007192eb5a38eb5abb591b871df3e52c7cd"
    cohort = occupancy["endpoint_cohort"]
    assert len(cohort) == len(set(cohort)) == 615 and cohort == sorted(cohort)
    assert not set(cohort).intersection({319, 863, 1355, 1568})
    assert stock["old_complete_paid"] == readback["paid"] and stock["complete_targets"] == readback["targets"]
    paid, targets = [Counter({int(rank): n for rank,n in readback[key].items()}) for key in ("paid","targets")]
    assert (sum(paid.values()), sum(targets.values()), targets[9], readback["copies"]) == (110519, 22461, 10888, 17)
    assert not readback["empty_root_credits"]
    old = targets.copy()
    old.subtract(paid)
    assert sum(r*n for r,n in old.items()) == readback["rank_surplus"] == 1424
    k_lo,k_hi = map(Fraction, admitted["crossing"])
    bit = Fraction(readback["bit_premise"])
    assert 0 < k_lo < k_hi == Fraction(stock["crossing_upper"]) < bit < MOONSHOT
    math = run_path(str(ROOT/"inputs/pricing.py"))
    cost,power,log = (math[key] for key in ("cost","power_bounds","log_bounds"))
    delta = {4:17, 5:17, 9:-17}
    uniform_derivative_lower = 17 * (power(9,bit)[0]*log(Fraction(9))[0]
        - sum(power(r,k_lo)[1]*log(Fraction(r))[1] for r in (4,5)))
    assert uniform_derivative_lower > 0 and cost(delta,bit)[1] < 1

    def scaled(edits, k):
        change = {r: edits*n for r,n in delta.items()}
        updated = targets.copy()
        updated.update(change)
        assert min(updated.values()) >= 0 and sum(updated.values()) == 22461+17*edits
        signed = updated.copy()
        signed.subtract(paid)
        assert sum(r*n for r,n in signed.items()) == 1424
        before = cost(old,k)
        credit = cost(change,k)
        margin = cost(signed,k)
        return dict(edits=edits,paid=paid,targets=updated,paid_delta={},target_delta=change,
            old_complete_margin=list(map(str,before)),gross_credit=list(map(str,credit)),
            complete_margin=list(map(str,margin)),complete_margin_with_one_extra_paid_rank1_upper=str(margin[1]-1))

    one, whole = (scaled(n,k_hi) for n in (1,len(cohort)))
    one_moon, whole_moon = (scaled(n,MOONSHOT) for n in (1,len(cohort)))
    assert Fraction(one["complete_margin"][0]) > 0 and Fraction(one["complete_margin_with_one_extra_paid_rank1_upper"]) < 0
    required = (-Fraction(one_moon["old_complete_margin"][1])) // Fraction(one_moon["gross_credit"][1]) + 1
    assert required > 0
    print(dumps(dict(head=HEAD, kappa=admitted["kappa"], word_sha256=WORD,
        caller_head=admitted["caller"], caller_sha256=admitted["caller_sha256"], input_sha256=PINS,
        old_crossing_lower=str(k_lo), old_crossing_upper=str(k_hi), retained_bit_premise=str(bit), moonshot=str(MOONSHOT),
        endpoint_cohort=cohort, cohort_cap=len(cohort), selected_bank_cap=24, build_cap=1, native_copies=17,
        old_paid=paid, old_targets=targets, signed_rank_surplus=1424, empty_root_credits=0,
        one_split=one, all_distinct_splits_optimistic=whole, one_split_at_moonshot=one_moon,
        all_distinct_splits_optimistic_at_moonshot=whole_moon, moonshot_minimum_edits_necessary=int(required),
        one_split_uniform_credit_through_bit_upper=str(cost(delta,bit)[1]),
        one_split_credit_derivative_lower=str(uniform_derivative_lower),
        scope="Fixed paid 4+5 on chart rank 4 or 5 for a chart-3 to chart-127 rank-nine helper. Grant one split per distinct cohort role and all ancillary costs free. Price only, no word decoding or support."),
        indent=2,sort_keys=True))


if __name__ == "__main__":
    assert __debug__
    main()
