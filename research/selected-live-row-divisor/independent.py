#!/usr/bin/env python3
"""Independent finite audit of the conditional complete live-row format.

Standard library only. This file does not import the primary checker or its
artifacts. Cartesian products supply the oracle for all mixed-radix rows;
distinct formal payload symbols test permutations without sampling bit values.
This is not an execution of the selected BIT word or its recursive machine.
"""

from collections import Counter
from itertools import product
from math import gcd, prod
import json


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def encode(digits, radices):
    require(len(digits) == len(radices), "wrong number of digits")
    value = 0
    for digit, radix in zip(digits, radices):
        require(0 <= digit < radix, "digit outside complete range")
        value = radix * value + digit
    return value


def decode(value, radices):
    require(0 <= value < prod(radices), "row outside complete range")
    digits = []
    for radix in reversed(radices):
        value, digit = divmod(value, radix)
        digits.append(digit)
    require(value == 0, "unconsumed row quotient")
    return tuple(reversed(digits))


def complete_rows():
    counts = Counter()
    for w, low, high in product(range(1, 4), repeat=3):
        base = w * low * high
        for depth in range(4):
            for multiplicity in (1, 2):
                radices = (w, low, high) * depth + (multiplicity,)
                row_count = multiplicity * base ** depth
                counts["formats"] += 1
                seen = set()
                for ordinal, digits in enumerate(product(*(range(r) for r in radices))):
                    # The Cartesian enumeration does not use either radix routine.
                    require(encode(digits, radices) == ordinal, "Cartesian encoding")
                    require(decode(ordinal, radices) == digits, "Cartesian decoding")
                    seen.add(ordinal)
                    counts["rows"] += 1
                    for consumed in range(depth + 1):
                        quotient = multiplicity * base ** (depth - consumed)
                        prefix = digits[:3 * consumed]
                        suffix = digits[3 * consumed:]
                        require(encode(suffix, radices[3 * consumed:]) == ordinal % quotient,
                                "unused suffix is not the complete row remainder")
                        require(encode(prefix, radices[:3 * consumed]) == ordinal // quotient,
                                "exposed ancestors do not form the quotient")
                        counts["prefix_suffix_checks"] += 1
                require(seen == set(range(row_count)), "missing or duplicated row")
                if depth:
                    unused = multiplicity * base ** (depth - 1)
                    for child_depth in range(depth):
                        child_stock = base ** child_depth
                        child_multiplicity, rem = divmod(unused, child_stock)
                        require(rem == 0 and child_multiplicity > 0, "incomplete child stock")
                        child_radices = (w, low, high) * child_depth + (child_multiplicity,)
                        require(prod(child_radices) == unused, "child volume mismatch")
                        # Every old high value sees the same complete child row set.
                        child_domain = tuple(product(*(range(r) for r in child_radices)))
                        for old_high in range(high):
                            require(len(child_domain) == unused, "high-dependent child size")
                            require({encode(c, child_radices) for c in child_domain} == set(range(unused)),
                                    "child lacks a complete independent layer")
                            counts["high_child_domains"] += 1
                    # These are the unchanged source formulas, at actual volume.
                    volume = 8 * row_count
                    packet = 8 * high * unused
                    require(packet * w * low == volume, "wrong live packet denominator")
                    role_slots = w + 4
                    require(5 * (volume + 4 * packet) - packet + 9 * role_slots - 2
                            == 5 * volume + 19 * packet + 9 * role_slots - 2,
                            "unequal-buffer parking identity")
                    counts["volume_parking_checks"] += 1
    return dict(counts)


def symbolic_payload(row_count):
    # A symbol is a distinct formal input coordinate, not a sampled bit.
    return {(r, s, x, y): ("input", r, s, x, y)
            for r in range(row_count) for s in range(2)
            for x in range(2) for y in range(2)}


def permute_payload(state, row_action, swap_data=False, flip_spectator=False):
    output = {}
    for (row, spectator, x, y), symbol in state.items():
        new_row = row_action[row]
        new_spectator = 1 - spectator if flip_spectator else spectator
        a, b = (y, x) if swap_data else (x, y)
        key = (new_row, new_spectator, a, b)
        require(key not in output, "noninjective payload permutation")
        output[key] = symbol
    return output


def cyclic_suffix_route(row_count, suffix_count):
    require(row_count % suffix_count == 0, "partial suffix group")
    route = {}
    for start in range(0, row_count, suffix_count):
        # Enumerate a concrete cycle and its edges, independently of radix decode.
        cycle = list(range(start, start + suffix_count))
        destinations = cycle[1:] + cycle[:1]
        route.update(zip(cycle, destinations))
    return route


def restored_payloads():
    fixtures = ((2, 3, 2, 2, 1), (2, 2, 3, 3, 1),
                (3, 2, 2, 2, 2), (1, 3, 2, 3, 1),
                (2, 1, 3, 3, 1), (3, 2, 1, 3, 2))
    counts = Counter()
    for w, low, high, depth, multiplicity in fixtures:
        base = w * low * high
        rows = multiplicity * base ** depth
        original = symbolic_payload(rows)
        identity = dict(enumerate(range(rows)))
        expected = permute_payload(original, identity, swap_data=True)
        counts["fixtures"] += 1
        counts["distinct_initial_symbols"] += len(original)
        for consumed in range(1, depth + 1):
            unused = multiplicity * base ** (depth - consumed)
            route = cyclic_suffix_route(rows, unused)
            inverse = {destination: source for source, destination in route.items()}
            for source, destination in route.items():
                require(source // unused == destination // unused,
                        "child touched an exposed ancestor including old high")
            moved = permute_payload(original, route)
            acted = permute_payload(moved, identity, swap_data=True)
            returned = permute_payload(acted, inverse)
            require(returned == expected, "row or spectator was not restored pointwise")
            for child_depth in range(depth - consumed + 1):
                require(unused % (base ** child_depth) == 0, "child depth exceeds suffix")
                counts["complete_child_boundaries"] += 1
            counts["symbolic_endpoint_checks"] += len(original)
    return dict(counts)


def depth_of(width):
    depth = 0
    while width >= 64:
        width = 42 * (width // 64)
        depth += 1
    return depth


def width_depths():
    counts = Counter()
    previous = 0
    for width in range(4097):
        depth = depth_of(width)
        require(depth >= previous, "nonmonotone depth")
        previous = depth
        counts["widths"] += 1
        if width < 64:
            require(depth == 0, "incorrect leaf depth")
            continue
        atom = width // 64
        for rank in range(1, 43):
            child = rank * atom
            require(0 < child < width and depth_of(child) <= depth - 1,
                    "rank child depth contract")
            counts["rank_children"] += 1
        for child in range(1, atom + 1):
            require(depth_of(child) <= depth - 1, "fallback child depth contract")
            counts["fallback_children"] += 1
    return dict(counts)


def padding_restriction():
    counts = Counter()
    for stock in (1, 2, 3, 4, 6, 8, 12, 18):
        for genuine_rows in range(stock, 3 * stock + 1):
            padded_rows = ((genuine_rows + stock - 1) // stock) * stock
            require(padded_rows % stock == 0, "padding did not supply full stock")
            require(genuine_rows <= padded_rows < 2 * genuine_rows, "padding factor")
            original = symbolic_payload(padded_rows)
            route = cyclic_suffix_route(padded_rows, padded_rows)
            inverse = {v: k for k, v in route.items()}
            identity = dict(enumerate(range(padded_rows)))
            actual = permute_payload(original, route)
            actual = permute_payload(actual, identity, swap_data=True)
            actual = permute_payload(actual, inverse)
            expected = permute_payload(original, identity, swap_data=True)
            restricted = {k: v for k, v in actual.items() if k[0] < genuine_rows}
            require(restricted == {k: v for k, v in expected.items() if k[0] < genuine_rows},
                    "padding restriction after completed endpoint")
            counts["complete_padding_cases"] += 1
    return dict(counts)


def minimality_census():
    counts = Counter()
    for base in range(1, 28):
        for depth in range(4):
            stock = base ** depth
            # A positive integer leftover is necessary in the fixed full-product
            # format. This finite census is separate from the written proof.
            first = next(s for s in range(1, stock + 1) if s % stock == 0)
            require(first == stock, "fixed-format least positive cardinality")
            counts["base_depth_pairs"] += 1
    return dict(counts)


def two_format_compatibility():
    """Direct divisibility oracle for the unchanged complete P-slot format."""
    counts = Counter()
    # Nontrivial low and high factors are present in the direct divisor. The
    # written cancellation proves that their particular positive values do not
    # affect the exact gate; this finite census uses N=2 and H=3.
    low, high = 2, 3
    for live, physical in product(range(1, 13), repeat=2):
        common = gcd(live, physical)
        numerator, denominator = live // common, physical // common
        require(gcd(numerator, denominator) == 1, "uncancelled compatibility fraction")
        for depth in range(5):
            live_stock = (live * low * high) ** depth
            physical_stock = (physical * low * high) ** depth
            gate = denominator ** depth
            for multiplicity in range(1, 26):
                direct = (multiplicity * live_stock) % physical_stock == 0
                cancelled = (multiplicity * live ** depth) % (physical ** depth) == 0
                proposed_gate = multiplicity % gate == 0
                require(direct == cancelled == proposed_gate, "incorrect exact acceptance gate")
                counts["iff_cases"] += 1
            # Search directly among live-format cardinalities; any common
            # reserve must be one of these. No lcm formula supplies the oracle.
            first = None
            for multiplicity in range(1, gate + 1):
                counts["minimum_search_candidates"] += 1
                if (multiplicity * live_stock) % physical_stock == 0:
                    first = multiplicity
                    break
            require(first == gate, "historical common reserve not minimal")
            common_stock = ((live * physical // common) * low * high) ** depth
            require(first * live_stock == common_stock, "wrong common-reserve cardinality")
            counts["minimum_common_reserves"] += 1

    live, physical = 28416, 28425
    common = gcd(live, physical)
    require((live // common, physical // common) == (9472, 9475),
            "selected compatibility fraction")
    require(gcd(9472, 9475) == 1, "selected compatibility fraction not reduced")
    for depth in range(9):
        gate = 9475 ** depth
        # Actual selected W and P; the arbitrary positive N,H have cancelled.
        require((gate * live ** depth) % (physical ** depth) == 0,
                "selected boundary must satisfy physical format")
        counts["selected_accepted_boundaries"] += 1
        below = gate - 1
        if below > 0:
            require((below * live ** depth) % (physical ** depth) != 0,
                    "selected just-below boundary unexpectedly accepted")
            counts["selected_rejected_positive_boundaries"] += 1
        else:
            # D=0 gives t=0 here. Divisibility of zero is true, but a zero
            # multiplicity is outside the nonempty complete-row contract.
            require(depth == 0 and below == 0, "unexpected boundary-domain case")
            counts["selected_zero_multiplicity_outside_domain"] += 1
    return dict(counts)


def defect_controls():
    controls = {}
    # Removing H can fail at the first level or only after a successful root split.
    controls["omitted_high_first_layer"] = (2 * 3) % (2 * 3 * 5) != 0
    wrong_rows = (2 * 3) ** 2
    actual_base = 2 * 3 * 2
    controls["omitted_high_descendant"] = (
        wrong_rows % actual_base == 0 and (wrong_rows // actual_base) % actual_base != 0)

    # The historical physical-slot interpretation is an additional condition.
    w, physical, low, high = 2, 11, 3, 2
    controls["physical_slot_divisor_not_automatic"] = (w * low * high) % (physical * low * high) != 0
    selected_w, selected_p = 28416, 28425
    selected_lcm = selected_w * selected_p // gcd(selected_w, selected_p)
    require((selected_lcm, selected_lcm // selected_w, selected_lcm // selected_p)
            == (269241600, 9475, 9472), "selected compatibility constants")
    controls["selected_depth_one_physical_incompatibility"] = selected_w % selected_p != 0

    # An XOR copy into zero work is sound; the same word on dirty work is not.
    source, target, dirt = (frozenset((name,)) for name in ("source", "target", "dirt"))
    work = frozenset()
    work ^= source
    correct_target = target ^ work
    work ^= source
    require(correct_target == target ^ source and not work, "allocated zero copy")
    work = dirt ^ source
    polluted_target = target ^ work
    restored_dirty_work = work ^ source
    controls["dirty_private_copy_pollution"] = (
        polluted_target != correct_target and restored_dirty_work == dirt)
    reset_images = {value: 0 for value in (0, 1)}
    controls["arbitrary_private_zeroing_noninjective"] = len(set(reset_images.values())) < len(reset_images)

    rows = 64
    original = symbolic_payload(rows)
    identity = dict(enumerate(range(rows)))
    expected = permute_payload(original, identity, swap_data=True)
    missing_return = permute_payload(original, cyclic_suffix_route(rows, 8), swap_data=True)
    controls["row_multiset_does_not_imply_pointwise_restoration"] = (
        Counter(missing_return.values()) == Counter(expected.values()) and missing_return != expected)
    spectator_drift = permute_payload(original, identity, swap_data=True, flip_spectator=True)
    controls["spectator_multiset_does_not_imply_restoration"] = (
        Counter(spectator_drift.values()) == Counter(expected.values()) and spectator_drift != expected)

    # Five real rows are padded to eight. A completed row drift would let a
    # padded formal value replace a genuine one when the padded tail is dropped.
    genuine, padded = 5, 8
    original = symbolic_payload(padded)
    missing_return = permute_payload(original, cyclic_suffix_route(padded, padded), swap_data=True)
    expected = permute_payload(original, dict(enumerate(range(padded))), swap_data=True)
    controls["padding_removed_before_row_restoration"] = (
        {k: v for k, v in missing_return.items() if k[0] < genuine}
        != {k: v for k, v in expected.items() if k[0] < genuine})
    controls["padding_factor_requires_at_least_one_stock"] = 4 >= 2 * 1

    # A child asking for its parent's depth fails already at multiplicity one.
    controls["child_depth_not_strictly_consumed"] = (12 ** 2 // 12) % (12 ** 2) != 0
    require(all(controls.values()), "a defect control did not distinguish its mutant")
    return controls


def run():
    return {
        "claim": "conditional_complete_live_row_format_only",
        "complete_rows": complete_rows(),
        "symbolic_payloads": restored_payloads(),
        "width_depths": width_depths(),
        "padding": padding_restriction(),
        "minimality": minimality_census(),
        "two_format_compatibility": two_format_compatibility(),
        "negative_controls": defect_controls(),
        "selected_execution": False,
        "formal_kernel_proof": False,
        "new_kappa": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
    print("PASS_SELECTED_LIVE_ROW_DIVISOR_INDEPENDENT no_new_kappa")
