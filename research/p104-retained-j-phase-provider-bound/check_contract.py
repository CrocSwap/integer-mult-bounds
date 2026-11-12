"""Read frozen physical counts and price a retained J phase-response top-up."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from math import comb
from pathlib import Path
from runpy import run_path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/caller/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/caller/check_odd_caller_exact_grid.py": "abd5a5fd011b71e5b382cbc058855594d4f2fe7b049f375506675c0303180f54",
    "inputs/caller/check_odd_fixed_tape_counts.py": "e6246e9f8fbeae3077d82e585eafd3647c1a8758c58f33c7c13e7efa6c1e42bb",
    "inputs/caller/check_odd_physical_binding.py": "5c80c3b0415a7f91d216395248dd6f13297eed637732098e1ca8fb0548951b98",
    "inputs/caller/signed_child.py": "ef03444360f02225138be9b38e2f9a85f313eeaa910d63a365de0f16d228cb8b",
    "inputs/caller/upstream_application.py": "d98987db98553dc55bfc80e3ca47abfcd51c57af6f8cda61101391d8eae94184",
    "inputs/comparator/NATIVE-RESULT.json": "c6d1b00a83185ab0062397b363258b1f3f6685d755e9c1d4f7d3e7e511240812",
    "inputs/comparator/RESULT.json": "7f2d587c59f063b01f1e8b320084a7f0943f2f05d65e3e0f5e80448c6c8e8194",
    "inputs/prices/PREDECESSOR-PRICE.json": "bbc486a3eb0e2aed03dd09f400fa94de1a59312058a9826880999155b10453bf",
    "inputs/prices/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Duplicate JSON key")
    return result


def signed_residues(bits, negatives):
    distribution = [0] * 4
    for i in range(bits - negatives + 1):
        for j in range(negatives + 1):
            distribution[(i - j) % 4] += comb(bits - negatives, i) * comb(negatives, j)
    return distribution


def phase_contract(caller):
    type_a = caller["types"]["A"]
    assert (type_a["roles"], type_a["offset"], len(type_a["ports"])) == (36, 0, 96)
    assert type_a["alpha2"] == "-1" and type_a["beta2"] == "0"
    assert len(type_a["diagonal"]) == 36 and all(
        row[:2] == [-1, 0] and len(row[2:]) == 17 and set(row[2:]) <= {0, 1}
        for row in type_a["diagonal"])
    stages = []
    queries = []
    for clock, event in enumerate(caller["events"]):
        if event[0] == "J":
            _, stage, plane_a, plane_b = event
            assert len(set(plane_a)) == len(plane_a) == 4
            assert all(0 <= role < 36 for role in plane_a)
            assert len(set(plane_b[:2])) == 2 and plane_b[2:] == ["-1", "1/2"]
            stages.append(stage)
        elif event[0] == "A":
            if event[1] == "QUERY":
                assert event[2:] == [0, 1, -1]
                queries.append(clock)
            else:
                assert event[1] in ("ADD", "SCALE", "SWAP", "LAMBDA", "IDLE_ONE")
    assert stages == list(range(1, 18)) and queries == [1516, 1580, 1659, 1721]
    return {"stages": stages, "type_a_query_clocks": queries, "type_a_uniform_endpoint_q_power": -1,
            "phase_pairs": [["1", "-1"], ["i", "-i"]], "host_required_phase_rank_floor": 4}


def main():
    assert __debug__
    inputs = {}
    for rel, digest in PINS.items():
        raw = (ROOT / rel).read_bytes()
        if sha256(raw).hexdigest() != digest:
            raise ValueError(f"Changed input {rel}")
        if rel.endswith(".json"):
            inputs[rel] = loads(raw, object_pairs_hook=unique)

    caller = inputs["inputs/caller/CALLER.json"]
    phase_contract_receipt = phase_contract(caller)
    caller["types"]["A"]["diagonal"][0][0] = 1
    try:
        phase_contract(caller)
    except AssertionError:
        pass
    else:
        raise AssertionError("Corrupted endpoint q power accepted")
    assert signed_residues(2, 0) == [1, 2, 1, 0]
    assert signed_residues(2, 1) == [2, 1, 0, 1]

    predecessor = inputs["inputs/prices/PREDECESSOR-PRICE.json"]
    result = inputs["inputs/comparator/RESULT.json"]
    native = inputs["inputs/comparator/NATIVE-RESULT.json"]
    assert predecessor["head"] == HEAD and result["caller_sha256"] == predecessor["caller_sha256"] == CALLER
    assert result["status"].startswith("PASS") and native["status"].startswith("PASS")
    binding = result["checks"]["ODD-PHYSICAL-BINDING.json"]
    physical = binding["occurrence_and_geometry"]
    tape = result["checks"]["ODD-FIXED-TAPE-COUNTS.json"]
    assert binding["native_sha256"] == native["word_canonical_sha256"] == tape["native_sha256"]
    assert binding["caller_sha256"] == tape["caller_sha256"] == CALLER
    assert binding["aliased_main_rejected"]
    counts = native["native"]
    helpers = sum(counts["helpers"].values())
    moves = sum(counts["paid"].values())
    type_a = predecessor["type_a_ports"]
    type_b = 104 - type_a
    stage_count = physical["native_calls"]
    owner_labels, remainder = divmod(physical["reserved_native_banks"], stage_count)
    assert (type_a, type_b, helpers, moves, stage_count, owner_labels, remainder) == (96, 8, 1101, 6279, 17, 68, 0)
    assert physical["native_public"] == counts["public"] == 4 * type_a + 2 * type_b + helpers == 1501
    assert physical["fresh_helpers"] == stage_count * helpers == 18717
    assert physical["productive_fields"] == 104 * 36 + stage_count * helpers == 22461
    assert physical["native_contact_boundaries"] == 2 * (4 * type_a + 2 * type_b) * stage_count == 13600
    assert physical["paid_positions"] == moves * stage_count + physical["query_uses"] + physical["idle_uses"] == 110519
    assert physical["paid"] == predecessor["old_paid"]
    assert physical["targets"] == predecessor["targets"]
    assert counts["owned_peak"] == 50 and counts["lifetimes"] == 73
    assert physical["reserved_serial_query_lambda_bank"] == 1
    assert (tape["context_c"], tape["monomial_map_slots"], tape["scalar_services_upper"]) == (2430, 298808, 43825824)

    width = 8
    phase = signed_residues(width, 0)
    assert phase == [72, 64, 56, 64]
    required = 2 * Fraction(min(phase[0], phase[2]) + min(phase[1], phase[3]), 2**width)
    assert required == Fraction(15, 16)
    spectra = {r: [signed_residues(width * r, width * k) for k in range(r + 1)] for r in (1, 2)}
    assert spectra[2] == [[16512, 16384, 16256, 16384]] * 3
    capacity = {r: 1 - Fraction(min(min(counts) for counts in rows), 2**(width * r))
                for r, rows in spectra.items()}
    assert capacity == {1: Fraction(25, 32), 2: Fraction(385, 512)}
    ratios = {r: required / bound for r, bound in capacity.items()}
    assert ratios == {1: Fraction(6, 5), 2: Fraction(96, 77)}

    power_bounds = run_path(str(ROOT / "inputs/prices/pricing.py"))["power_bounds"]
    bit = Fraction(predecessor["retained_bit_premise"])
    crossing = Fraction(predecessor["old_crossing_upper"])
    assert 0 < crossing < bit < 1
    credit = 2 * type_a
    alternatives = {
        "two_same_volume_rank_one_top_ups": (1, Fraction(2)),
        "one_canonical_rank_two_with_required_enlargement": (2, ratios[2]),
        "one_same_volume_rank_at_least_three": (3, Fraction(1)),
        "one_rank_at_least_three_granting_reduced_volume": (3, required),
    }
    old_margin = Fraction(predecessor["old_complete_margin_at_crossing"][1])
    gains = {}
    for name, (rank, volume) in alternatives.items():
        credit_at_bit_upper = credit - type_a * volume * power_bounds(rank, bit)[0]
        margin_at_crossing_upper = old_margin + credit - type_a * volume * power_bounds(rank, crossing)[0]
        if rank == 1:
            assert credit_at_bit_upper == 0 and margin_at_crossing_upper == old_margin < 0
        else:
            assert credit_at_bit_upper < 0 and margin_at_crossing_upper < 0
        gains[name] = {"uniform_signed_moment_credit_upper_through_bit": str(credit_at_bit_upper),
                       "complete_margin_upper_at_old_crossing": str(margin_at_crossing_upper)}
    print(dumps({
        "head": HEAD, "caller_sha256": CALLER, "sha256": PINS,
        "exact_phase_contract": phase_contract_receipt,
        "controls": {"corrupted_endpoint_power_rejected": True, "known_two_bit_signed_residues": True},
        "native_per_stage": {"distinct_public_inputs": 1501, "distinct_public_returns": 1501,
            "type_a_main": 384, "type_b_main": 16, "independent_helper_inputs_and_returns": 1101,
            "owned_labels": owner_labels, "owned_lifetimes": counts["lifetimes"], "peak_owned": counts["owned_peak"],
            "unary_paid_moves": moves, "main_contact_boundaries": 800},
        "complete_price": {"deleted_rank_one_positions": credit, "retained_native_stages": stage_count,
            "complete_paid_positions": physical["paid_positions"], "productive_fields": physical["productive_fields"],
            "additional_ordinary_cost_granted_free": True, "signed_moment_credit_uppers": gains,
            "retained_bit_premise": str(bit)},
        "canonical_carrier_at_width_eight": {"phase_residues": phase, "core_residues_by_sign_count": spectra,
            "additional_displacement_lower_fraction": str(required), "max_displacement_fractions": {r:str(v) for r,v in capacity.items()},
            "necessary_volume_ratios": {r:str(v) for r,v in ratios.items()}},
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
