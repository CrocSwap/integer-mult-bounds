#!/usr/bin/env python3
"""Reconstruct final gen4 banks and finite accounting from the actual word.

The orchestrator must freshly run the immutable baseline, scalar replay and
exact chart checker before invoking this integration component.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
import sys
if not __debug__:
    raise SystemExit("Assertions required; refusing -O")
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(0)

from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import price as pricing


def read(path):
    return json.loads(Path(path).read_text())


def cutoff(delta, coefficient):
    assert 0 < delta <= 1 and isinstance(coefficient, int) and coefficient >= 1
    return max(1, pricing.ceil_fraction(36 / delta**2),
               pricing.ceil_fraction(2 * (4 + (coefficient - 1).bit_length()) / delta))


def signed_bounds(records, n):
    result = []
    for reverse in (False, True):
        norms, largest, open_copy = [1] * (n + 1), 1, False
        for op, a, b, coefficient, frame, category in (reversed(records) if reverse else records):
            if op == 1:
                norms[a] += abs(coefficient) * norms[b]
                largest = max(largest, norms[a])
            elif op == (3 if reverse else 2):
                assert not open_copy and b == n
                norms[b], open_copy = norms[a], True
            elif op == (2 if reverse else 3):
                assert open_copy and b == n
                norms[b], open_copy = 0, False
        assert not open_copy
        result.append(dict(reverse=reverse, bits=largest.bit_length(),
                           cancellation_free_signed_row_l1_upper=str(largest)))
    return result


def exact_banks(initial, final, frames):
    families, endpoint_pairs = defaultdict(list), set()
    for role in range(3520, 19930):
        before, after = initial[str(role)], final[str(role)]
        endpoint_pairs.add((before, after))
        rank = frames[str(after)]["dim"] - frames[str(before)]["dim"]
        assert 0 < rank <= 24
        families[rank].append(role)
    assert {r: len(roles) for r, roles in families.items()} == {
        24: 13884, 4: 1760, 3: 706, 5: 12, 6: 48
    }
    for before, after in endpoint_pairs:
        for b in frames[str(before)]["B"]:
            for a in frames[str(after)]["A"]:
                assert sum(Q(x) * Q(y) for x, y in zip(a, b)) == 0
    patterns, slots, bank, columns, wrong_columns = [], {}, 0, 0, 0
    for rank, roles in sorted(families.items()):
        blocks, count = 120 // rank, 60 * len(roles)
        assert blocks * rank == 120 and blocks <= 40 and count % blocks == 0
        patterns.append(dict(width=rank, blocks=blocks, banks_per_stage=count//blocks,
                             occurrences_per_stage=count))
        slots[rank] = []
        for _ in range(count // blocks):
            slots[rank].extend((bank, j * rank, j + 1) for j in range(blocks))
            bank += 1
        for reverse in (False, True):
            permutation = list(range(240))
            for j in (reversed(range(blocks)) if reverse else range(blocks)):
                for a in range(j * rank, (j + 1) * rank):
                    permutation[a], permutation[120+a] = permutation[120+a], permutation[a]
            assert permutation == list(range(120, 240)) + list(range(120))
            columns += 240
        for omitted in range(blocks):
            for repetitions in (0, 2):
                permutation = list(range(240))
                for j in range(blocks):
                    for _ in range(repetitions if j == omitted else 1):
                        for a in range(j * rank, (j + 1) * rank):
                            permutation[a], permutation[120+a] = permutation[120+a], permutation[a]
                wrong = sum(permutation[j] != (j + 120) % 240 for j in range(240))
                assert wrong == 2 * rank
                wrong_columns += wrong
    assignments, mass, digest = 0, 0, hashlib.sha256()
    for stage in range(5):
        for rank, roles in sorted(families.items()):
            assert len(slots[rank]) == len(roles) * 60
            for j, role in enumerate(roles):
                for replica in range(60):
                    bank_id, offset, scalar = slots[rank][j * 60 + replica]
                    assert 1 <= scalar <= 40 and offset + rank <= 120
                    digest.update(f"{stage},{replica},{role},{bank_id},{offset},{rank},{scalar}\n".encode())
                    assignments += 1
                    mass += rank
    assert assignments == 4923000 and bank == 171361 and mass == 5 * 120 * bank
    literal_stock = 4 * 1760 * 60 + 5 * bank
    assert literal_stock == 1279205 and literal_stock % 5 == 0
    return dict(status="PASS_ACTUAL_ROLE_REPLICA_STAGE_BANK_TILING",
                actual_role_replica_stage_assignments=assignments,
                assignment_sha256=digest.hexdigest(), patterns=patterns,
                residual_role_counts={r: len(roles) for r, roles in families.items()},
                exact_nested_endpoint_pairs=len(endpoint_pairs), banks_per_stage=bank,
                covered_rank_mass=mass, literal_stock=literal_stock,
                normalized_stock=literal_stock//5, max_block_scalar=40,
                endpoint_columns_checked=columns, omission_repeat_wrong_columns=wrong_columns)


def admit(candidate, export, baseline, chart_path, price_path):
    candidate, export, baseline = map(lambda p: Path(p).resolve(), (candidate, export, baseline))
    chart_path, price_path = Path(chart_path).resolve(), Path(price_path).resolve()
    supplied_price = read(price_path)
    base_package = Path(supplied_price["base_package"]).resolve()
    price = pricing.compute(candidate, base_package)
    assert price == supplied_price, "Price must reproduce from the actual candidate word"
    full = read(baseline / "verification.json")
    assert full["status"] == "PASS_IMMUTABLE_PARITY_FUSED_GEN4_FIVE_STAGE_BANKED_CONSTRUCTION"
    assert full["inputs_unchanged"] and full["manifest_sha256"] == pricing.BASE_MANIFEST_SHA256
    assert set(full["fresh_stages"]) == {"virtual", "raw", "bit", "scalar", "primes", "banks", "complex", "math", "finite"}
    assert len(full["negative_controls"]) == 9
    primes = read(baseline / "primes.json")
    assert primes["all_remaining_factors_below_2_power_80"]
    native = read(candidate / "COHORT-FIVE-STAGE-COLUMNS.json")
    assert native["status"] == "PASS_GENERIC_FIVE_STAGE_FORMAL_COLUMNS_AND_COMPUTED_PREFIX"
    assert native["formal_columns_checked"] == 23450 and native["independent_dirty_registers"] == 16410
    assert len(native["negative_controls"]) == 6 and all(x["rejected"] for x in native["negative_controls"])
    assert native["copied_center_original_source_immutable"] and native["fresh_center_copies"] == 120
    state = read(export / "249-states.json")
    initial, final = read(candidate / "COHORT249-INITIAL.json"), read(candidate / "COHORT249-FINAL.json")
    frames = read(export / "frames.json")["frames"]
    frames.update(read(candidate / "COHORT249-FRAMES.json"))
    assert set(initial) == set(final) == {str(i) for i in range(19930)}
    assert all(initial[str(i)] == state["initial"][str(i)] and final[str(i)] == state["final"][str(i)] for i in range(3520))
    changed_entrances = {i for i in range(3520, 19930) if initial[str(i)] != state["initial"][str(i)]}
    changed_exits = {i for i in range(3520, 19930) if final[str(i)] != state["final"][str(i)]}
    assert len(changed_entrances) == 60 and len(changed_exits) == 440 and not changed_entrances & changed_exits
    assert Counter(frames[str(initial[str(i)])]["dim"] for i in changed_entrances) == {18: 48, 19: 12}
    assert all(frames[str(state["initial"][str(i)])]["dim"] == 0 and frames[str(final[str(i)])]["dim"] == 24 for i in changed_entrances)
    assert all(frames[str(initial[str(i)])]["dim"] == 20 and frames[str(final[str(i)])]["dim"] == 23 and frames[str(state["final"][str(i)])]["dim"] == 24 for i in changed_exits)
    records, local, operations, coefficients = pricing.word_inventory(candidate)
    old_records = pricing.read_word(export / "COHORT249-RECORDS.bin")
    assert [x for x in records if x[0] in (2, 3)] == [x for x in old_records if x[0] in (2, 3)]
    current, open_copy = {int(i): f for i, f in initial.items()}, None
    for op, a, b, c, frame, category in records:
        if op == 0:
            assert current[a] == b and frames[str(c)]["dim"] - frames[str(b)]["dim"] == frame
            current[a] = c
        elif op == 1:
            assert current[a] == current[b] == frame
            assert a != open_copy
        elif op == 2:
            assert open_copy is None and current[a] == c and b == 19930
            current[b], open_copy = frame, b
        else:
            assert open_copy == b and current[a] == c and current[b] == frame
            del current[b]
            open_copy = None
    assert open_copy is None and current == {int(i): f for i, f in final.items()}
    old_pairs = {(b, c, rank) for op, a, b, c, rank, z in old_records if op == 0 and rank}
    required_charts = {(b, c, rank) for op, a, b, c, rank, z in records if op == 0 and rank} - old_pairs
    for role in changed_entrances | changed_exits:
        before, after = initial[str(role)], final[str(role)]
        required_charts.add((before, after, frames[str(after)]["dim"] - frames[str(before)]["dim"]))
    chart = read(chart_path)
    chart_details_path = chart_path.with_name("COMBINED-CHARTS.json")
    charts = read(chart_details_path)
    assert {(c["before"], c["after"], c["rank"]) for c in charts} == required_charts
    assert len(charts) == len(required_charts) == chart["unique_projectors_checked"] == 4004
    assert chart["retired_endpoints"] == 500 and chart["all_entries_below_two_to_80"]
    assert int(chart["max_numerator"]) < 2**80 and int(chart["max_denominator"]) < 2**80
    assert chart["max_factors"] == max(c["factors"] for c in charts) == 208
    normalizer = max(186, chart["max_factors"]) + 119 + 120
    assert normalizer == 447
    bank = exact_banks(initial, final, frames)
    stock, normalized_stock = bank["literal_stock"], bank["normalized_stock"]
    assert normalized_stock == price["stock"] == 255841
    adds, units, copies = operations[1], sum(c * n for c, n in coefficients.items()), operations[2]
    assert adds == native["local_scalar_additions"] == 626610 and units == 630130 and copies == 24
    assert dict(local) == dict(native["local_raw_H"]) == {int(k): n for k, n in price["local_histogram"].items()}
    bounds = signed_bounds(records, 19930)
    assert bounds == native["signed_lift_prefix"]
    forward, backward = (int(row["cancellation_free_signed_row_l1_upper"]) for row in bounds)
    payload = 64 * forward**3 * backward**2
    assert payload == int(native["payload_prefix_upper"]) and payload.bit_length() == 91 and payload < 2**104
    m, replicas, v, helpers = 120, 60, 1760, 16410
    calls, mass = price["calls"], price["rank_mass"]
    assert m * normalized_stock - mass == 52800
    literal_histogram = {int(k): 5 * n for k, n in price["histogram"].items()}
    children = sum(literal_histogram.values())
    assert children == 5 * calls and sum(k*n for k, n in literal_histogram.items()) == 5 * mass
    weighted = replicas * (5 * adds + 6 * v)
    unit = replicas * (5 * units + 6 * v)
    routes = replicas * (24 * v + 10 * helpers)
    dimension, doubled = m*m, 2*m
    good, high = 8*m*m + 8, 16*(dimension+1)**2
    selectors = 2 * 5 * replicas * ((stock-1) + helpers * m * normalizer)
    assert selectors == 528906962400 < 2**40
    items = dict(unit_scalar_additions=unit, high_affine=routes*high,
                 low_role_transpositions=routes*(stock+24), good_wrappers=children*good,
                 matrix_preparation=children*128*doubled**3, invertibility_tests=16*m**3,
                 copy_erase_episodes=120*replicas, edge_descriptors=children,
                 bank_selectors=selectors, fixed_unit=1)
    coefficient = sum(items.values())
    assert coefficient == 92323631924982001 < 2**80 and stock+24 < 2**80
    prime, residue = pricing.PRIME, 4
    for _ in range(125):
        residue = (residue * residue - 2) % prime
    assert residue == 0 and all(127 % divisor for divisor in range(2, 12))
    rho = Q(2*m**3, prime)
    assert rho == Q(price["rare_density"]) and prime > 2**80
    cutoffs = []
    for row in price["ordinary_gaps"]:
        delta = min(Q(value) for value in row["gaps"].values())
        exponent = cutoff(delta, coefficient)
        assert exponent * delta**2 >= 36 and exponent * delta >= 2*(4+(coefficient-1).bit_length())
        cutoffs.append(dict(level=row["level"], minimum_gap=delta, log2_cutoff=exponent))
    assert len(cutoffs) == 8
    rejected = []
    for name, delta, constant in [("zero cutoff gap", Q(0), coefficient), ("zero coefficient", Q(1, 2), 0)]:
        try:
            cutoff(delta, constant)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError("Invalid finite cutoff admitted")
    moment_slack = 1 - Q(price["first_engine_interval"][1])
    linear_slack = 1 - Q(mass, 120*normalized_stock) - rho*Q(32*m*calls, normalized_stock)
    assert moment_slack > 0 and linear_slack > 0
    sources = [Path(__file__).resolve(), Path(pricing.__file__).resolve(), Path(__file__).with_name("charts.cpp"),
               chart_path, chart_details_path, price_path, export / "249-states.json", export / "frames.json",
               export / "COHORT249-RECORDS.bin"]
    sources += [candidate/name for name in ("COHORT249-RECORDS.bin", "COHORT249-INITIAL.json", "COHORT249-FINAL.json",
                                           "COHORT249-FRAMES.json", "COHORT-FIVE-STAGE-COLUMNS.json")]
    sources += [baseline/name for name in ("verification.json", "finite.json", "banks.json", "scalar.json", "primes.json", "complex.json")]
    bindings = {str(path.resolve()): pricing.sha(path) for path in sources}
    bank.update(source_word_sha256=price["source_word_sha256"], selector_charge=selectors,
                normalizer_factor_bound=normalizer)
    invoice = dict(
        status="PASS_SOURCE_BOUND_GEN4_RETIREMENT_ENTRANCE_FIXED_PRIME_FINITE_INVOICE",
        source_word_sha256=price["source_word_sha256"], source_bindings=bindings,
        original_package_manifest_sha256=full["manifest_sha256"], price_independently_recomputed=True,
        fixed_prime=prime, lucas_lehmer_steps=125, lucas_lehmer_residue=residue, rare_density=rho,
        normalized_stock=normalized_stock, literal_stock=stock, physical_replicas=replicas, stages=5,
        local_additions=adds, local_unit_expanded_additions=units, local_copy_episodes=copies,
        global_weighted_additions=weighted, global_unit_expanded_additions=unit,
        literal_histogram=literal_histogram, literal_positive_rank_children=children,
        literal_rank_mass=5*mass, literal_deficit=264000, bank_assignments=4923000,
        bank_selector_charge=selectors, normalizer_factor_bound=normalizer,
        new_chart_factor_max=chart["max_factors"], primitive_coefficient_items=items,
        full_counted_primitive_coefficient=coefficient, primitive_coefficient_bits=coefficient.bit_length(),
        signed_lift_prefix=bounds, payload_prefix_upper=payload, payload_prefix_bits=91,
        moment_slack=moment_slack, linear_slack=linear_slack, ordinary_levels=8,
        ordinary_cutoffs=cutoffs, rejected_controls=rejected, all_47_constraints_positive=True,
        kappa=price["kappa"], kappa_decimal=price["kappa_decimal"], gain_percent=price["gain_percent"],
        exceeds_PR276_0p1_percent=True,
        full_constant_rule="C_full dominates the displayed finite coefficient and every retained primitive, wrapper, "
                           "setup, row, padding and preceding ordinary-level constant. Enlarge each cutoff with "
                           "ceil(log2(C_full)); no recursive child is absorbed.",
        scope="Conditional on the pinned PR276 all-size compiler, weighted chart, restored row, selectors, routing, "
              "prime supply, recovery, complex symbolic and analytic hypotheses. The orchestration must regenerate "
              "the baseline, actual candidate, scalar replay and exact chart audit."
    )
    return pricing.serial(bank), pricing.serial(invoice)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--charts", type=Path, required=True)
    parser.add_argument("--price", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bank, invoice = admit(args.candidate, args.export, args.baseline, args.charts, args.price)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, value in [("BANK-ASSIGNMENT-REPLAY.json", bank), ("FINITE-INVOICE.json", invoice)]:
        (args.output/name).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")
    print("PASS integrated finite admission", invoice["kappa_decimal"], flush=True)


if __name__ == "__main__":
    main()
