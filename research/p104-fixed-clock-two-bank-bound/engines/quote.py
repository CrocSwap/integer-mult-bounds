"""Quote fixed-clock split-chart replacements using authenticated receipts."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/R116-PRICE.json": "8226a2b9c9240455d6fcdaf3a38929e3336e89f35aed3f15b81564f07ed8387f",
    "inputs/R116-LEAD.json": "1d7d7b122757d4345cfea3fa7d1c8525211939b913e900e9974fb93fc5b18e5e",
    "inputs/R116-INDEPENDENT.json": "f777aaa05cbcb9f6067d9b04220abe9aab01f8eaac5c407b078e0c295ca1f2b7",
    "inputs/7334-RESULT.json": "7f2d587c59f063b01f1e8b320084a7f0943f2f05d65e3e0f5e80448c6c8e8194",
}


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def checked(path):
    raw = (ROOT / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError("changed dependency " + path)
    return loads(raw, object_pairs_hook=unique)


def main():
    assert __debug__
    quote, lead, independent, baseline = map(checked, PINS)
    assert lead["counts"] == {
        "early_excluded": 4124,
        "late_peer_at_c": 0,
        "late_peer_at_c_with_exactly_one_crossed_scalar": 0,
        "late_tested": 4124,
        "survivors": 0,
    }
    assert independent["complete"] and len(independent["rows"]) == 4
    assert all(row["chart_C_cut_count"] == 0 for row in independent["rows"])
    assert [r["key"] for r in independent["rows"]] == [r["key"] for r in quote["cases"]]
    banks = []
    for case in quote["cases"]:
        first, last, mover = case["key"]
        entrance, middle, exit_chart = case["charts"]
        peer = case["peer"]
        for clock, event in case["original_pair"]:
            op, destination, source, coefficient, chart = event
            assert op == "ADD" and chart == middle and {destination, source} == {mover, peer}
            assert first < clock < last
            banks.append(dict(
                key=[first, last, mover, clock], destination=destination, source=source,
                coefficient=coefficient, old_coframe=middle,
                new_coframe=exit_chart if destination == mover else middle,
                exclude_other_operand=True, include_destination_as_diagonal=True,
            ))
    assert len(banks) == 8 and len({tuple(b["key"]) for b in banks}) == 8
    assert quote["paid_delta"] == {"1": -34, "2": 17}
    assert 0 < Fraction(quote["one_upper"]) < Fraction(quote["whole_upper"]) < 1

    old_ordinary = 782_715_464
    old_tape_services, old_tape_maps = 43_825_824, 298_808
    encoded = dumps(baseline)
    assert str(old_ordinary) in encoded and str(old_tape_services) in encoded and str(old_tape_maps) in encoded
    numerator_bits, denominator_bits = 24, 26
    add_charge = 4 * (numerator_bits + denominator_bits + 1 + numerator_bits)
    scale_charge = 4 * (numerator_bits + denominator_bits + 1)
    edit_charge = 18 * (2 * (2 * add_charge + scale_charge) + 1000)
    service_delta = 17 * (2 * 3 - 2) * 32
    assert (add_charge, scale_charge, edit_charge, service_delta) == (300, 204, 46944, 2176)
    print(dumps(dict(
        head=quote["head"], caller=quote["caller"], kappa=quote["kappa"], pins=PINS,
        word_sha256=quote["word_sha256"], payload_sha256=quote["payload_sha256"],
        windows=quote["cases"], banks=banks, limits=dict(windows=4, banks=8, events=76466, seconds=20),
        paid_delta=quote["paid_delta"], all_four_relaxed_paid_delta=quote["compatible_paid_delta"],
        old_paid=quote["old_paid"], one_paid=quote["one_new_paid"],
        four_relaxed_paid=quote["optimistic_all_four_paid"], productive=quote["productive"],
        rank_surplus=quote["rank_surplus"], one_upper=quote["one_upper"],
        four_relaxed_upper=quote["whole_upper"], fixed_target_complete_upper=quote["fixed_target_complete_upper"],
        conditional_ordinary=dict(old=old_ordinary, add_unit_upper=add_charge, scale_unit_upper=scale_charge,
            one_upper=old_ordinary+edit_charge, four_relaxed_upper=old_ordinary+4*edit_charge,
            retained_upper=10**9, extra_rank2_routing_unit=1000, conservative_copy_count=18),
        conditional_tape=dict(old_scalar_services=old_tape_services,
            one_scalar_services_upper=old_tape_services+service_delta,
            four_scalar_services_upper=old_tape_services+4*service_delta,
            old_maps=old_tape_maps, one_maps=old_tape_maps-34, four_maps=old_tape_maps-136,
            records_per_map_upper=85264),
        scope="Four frozen fixed-clock two-public-bank replacements. No new owned lifetime or paid operation. Exact grid and envelope require fresh verification.",
    ), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
