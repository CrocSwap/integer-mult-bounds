"""Adversarial controls for global field age, stack order and fibre charges."""
from dataclasses import replace
from hashlib import sha256
from math import comb, factorial, gcd
from random import Random

from control import FrozenTape, Meter, Program, Step, Table, evaluate, header_offsets, need
from reference import value as reference


def table(tag, modulus, seed, numerator_row=None):
    rng = Random(seed)
    units = [x for x in range(1, modulus) if gcd(x, modulus) == 1]
    pivots = tuple(rng.choice(units) for _ in range(64))
    diagonal = tuple(rng.choice(units) for _ in range(128))
    permutation = list(range(128))
    rng.shuffle(permutation)
    if numerator_row is not None:
        # Both requests in a field-1 pair reach the head bank.
        j = permutation.index(numerator_row)
        permutation[1], permutation[j] = permutation[j], permutation[1]
    return Table(tag, pivots, diagonal, tuple(permutation))


def run_value(program, tables, index):
    e = program.root_size * program.width
    need((program.width - 1)**10000 < e**17 <= program.width**10000,
         "test fixture has a compatible original root width")
    need(len(program.steps) <= 2 * (max(2, e) - 1).bit_length(), "global depth includes resets")
    meter = Meter()
    tape = FrozenTape(tables, program.q**program.width, meter)
    original = tape.data
    got = evaluate(program, tape, index)
    expected = reference(program, tables, len(program.steps), index)
    need(got == expected, "iterative and recursive generated weights")
    need(tape.data == original and tape.head == 0, "readonly frozen fields and restored head")
    depth = len(program.steps)
    need(meter.requests <= (1 << (depth + 1)) - 1, "binary evaluator request bound")
    need(meter.maximum_stack_items <= 4 * depth + 1, "linear live stack")
    need(all(slot < depth for slot in meter.field_reads), "no fresh-field capture")
    return got, meter


def evaluator_checks():
    cases, requests, reads, moves, max_stack = 0, 0, 0, 0, 0
    full_branch = []
    for depth in (0, 1, 2, 4, 8, 10):
        steps = tuple(Step("pair", 10 + j, field=1, reverse=bool(j % 2)) for j in range(depth))
        program = Program(3, 2, 64**(depth + 1), 2, steps)
        tables = tuple(table(s.tag, 9, j + 40, 2) for j, s in enumerate(steps))
        for index in (0, 1, 17, 63):
            _, meter = run_value(program, tables, index)
            need(meter.requests == (1 << (depth + 1)) - 1, "worst binary request tree attained")
            cases += 1
            requests += meter.requests
            reads += meter.bit_reads
            moves += meter.head_moves
            max_stack = max(max_stack, meter.maximum_stack_items)
        full_branch.append({"depth": depth, "requests_per_value": meter.requests})
    for reverse in (False, True):
        steps = (Step("good", 100, rank=42), Step("pair", 101, field=1, reverse=reverse),
                 Step("good", 102, rank=7))
        program = Program(5, 2, 64**4 + 17, 2, steps)
        tables = tuple(table(s.tag, 25, j + 150, 2) for j, s in enumerate(steps))
        size = program.extents()[-1]
        for index in sorted({0, 1, size // 2, size - 1}):
            _, meter = run_value(program, tables, index)
            cases += 1
            requests += meter.requests
            reads += meter.bit_reads
            moves += meter.head_moves
            max_stack = max(max_stack, meter.maximum_stack_items)
    return {"coordinate_checks": cases, "requests": requests, "control_bits_read": reads,
            "charged_control_head_moves": moves, "maximum_stack_items": max_stack,
            "full_binary_trees": full_branch}


def reset_checks():
    steps = (Step("good", 200, rank=42), Step("unit", 201),
             Step("good", 202, rank=7), Step("pair", 203, field=1, reverse=True))
    program = Program(3, 2, 64**4, 2, steps)
    cases, records, digest = 0, 0, sha256()
    values_by_current = {}
    for old in (0, 1):
        for dead in (0, 1):
            for current in range(3):
                live = table(202, 9, 20 + current)
                pivots = list(live.pivots)
                pivots[0], pivots[3] = 1, 1 + 3 * current
                live = replace(live, pivots=tuple(pivots))
                tables = (table(200, 9, old), table(201, 9, 10 + dead),
                          live, table(203, 9, 30, 35))
                size = program.extents()[-1]
                observations = []
                for index in sorted({0, 1, size // 2, size - 1}):
                    weight, meter = run_value(program, tables, index)
                    need(set(meter.field_reads) == {2, 3}, "unit reset preserves global slots")
                    observations.append(weight)
                    cases += 1
                if current in values_by_current:
                    need(observations == values_by_current[current], "dead expression ancestry is irrelevant")
                values_by_current[current] = observations
                # Complete body fibres for one coefficient, with dirty payload labels.
                weight = observations[0]
                inverse = pow(weight, -1, 9)
                outputs = set()
                for unused in range(3):
                    for head in range(9):
                        for tail in range(9):
                            out = (unused, weight * tail % 9, inverse * head % 9)
                            need((weight * out[2] % 9, inverse * out[1] % 9) == (head, tail),
                                 "complete weighted pair inverse")
                            outputs.add(out)
                            digest.update(bytes((old, dead, current, unused, head, tail, *out)))
                            records += 1
                need(len(outputs) == 3 * 81, "unused stock and complete fibre bijection")
    need(len({tuple(x) for x in values_by_current.values()}) > 1, "live high table affects weights")
    tables = tuple(table(s.tag, 9, j + 17, 2) for j, s in enumerate(steps))
    rejected = []
    for name, modified in (("compact old fields without rebinding", tables[2:]),
                            ("capture current fresh field", tables + (table(204, 9, 9),)),
                            ("swap frozen field bindings", (tables[0], tables[1], tables[3], tables[2]))):
        try:
            evaluate(program, FrozenTape(modified, 9, Meter()), 0)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("invalid field boundary accepted: " + name)
    # A reset can itself lead to another internal Pair without a Good node.
    shorter = Program(3, 2, 64**4, 2,
                      (Step("good", 210, rank=42), Step("unit", 211, half=True),
                       Step("pair", 212, field=64, reverse=True)))
    short_tables = tuple(table(s.tag, 9, j + 60, 2) for j, s in enumerate(shorter.steps))
    _, meter = run_value(shorter, short_tables, 0)
    need(set(meter.field_reads) == {2}, "orientation reset uses next global slot")
    large_tag = 1 << 300
    broad = Program(3, 2, 128, 2, (Step("good", large_tag),))
    run_value(broad, (table(large_tag, 9, 17),), 0)
    try:
        FrozenTape((), 9, Meter()).unused_stock
    except ValueError:
        rejected.append("unused stock read")
    return {"coordinate_checks": cases + 2, "complete_body_records": records,
            "large_low_tag_bits": large_tag.bit_length(),
            "live_table_values": {str(k): v for k, v in values_by_current.items()},
            "payload_map_sha256": digest.hexdigest(), "controls": rejected,
            "scope": "Prepared-table grammar and complete small pair fibres; no selected full matrix producer or recursive payload dispatcher."}


def counters():
    total, maximum_bits, preparations = 0, 0, 0
    for before in (1, 2, 5):
        for middle in (1, 7, 257):
            for radix in (1, 3, 9):
                for coefficient, carry in ((-2, 1), (1, -1), (4, 3)):
                    meter = {"fibres": 0, "active_preparations": 0, "active_bits_read": 0}
                    got = list(header_offsets(before, radix, middle, coefficient, carry, meter))
                    expected = [(coefficient * ((prefix // middle) % radix) + carry) % radix
                                for prefix in range(before * radix * middle)]
                    need(got == expected, "separate source counter equals flat-index specification")
                    need(meter["active_preparations"] == (0 if radix == 1 else before * radix),
                         "spectator middle does not multiply coefficient preparation")
                    need(meter["active_bits_read"] <= before * radix * radix.bit_length(),
                         "active counter reads exclude spectator length")
                    total += len(got)
                    preparations += meter["active_preparations"]
                    maximum_bits = max(maximum_bits, radix.bit_length())
    root = Program(3, 1, 1, 2, ())
    result, meter = run_value(root, (), 0)
    need(result == 2 and meter.bit_reads == 0, "width-one root has no ancestry")
    # One chosen forbidden full-prefix scan defeats a claimed constant C=7.
    w, q, candidate_C = 2, 3, 7
    spectator_bits = (candidate_C + 1) * q**(w - 1)
    need(spectator_bits > candidate_C * q**(w - 1), "unrelated prefix cannot enter local bound")
    return {"header_fibres": total, "active_preparations": preparations,
            "maximum_active_counter_bits": maximum_bits,
            "width_one_ancestry_reads": meter.bit_reads,
            "forbidden_scan_control": {"w": w, "q": q, "candidate_C": candidate_C,
                                       "spectator_bits": spectator_bits}}


def bounds():
    power = 1800
    constant = (1 << power) * factorial(power)
    cases = 0
    for w in list(range(1, 129)) + [256, 512, 1024, 1536, 1800, 2048, 4096]:
        need(w**power <= factorial(power) * comb(w + power - 1, power), "rising product bound")
        need(comb(w + power - 1, power) <= 1 << (w + power - 1), "Pascal row bound")
        need(w**power <= constant * 2**(w - 1), "all-width absorption sample")
        cases += 1
    need(3 * 10000 + 3 * 17 == 30051 < 1800 * 17, "exact polynomial exponent implication")
    for e in range(2, 4097):
        h = 2 * (e - 1).bit_length()
        need(1 << (h + 1) <= 8 * e * e, "global-depth tree bound")
    return {"preparation_power": power, "exponent_numerator": 30051, "denominator": 17,
            "absorption_constant": "2^1800 * 1800!", "constant_bits": constant.bit_length(),
            "constant_sha256": sha256(constant.to_bytes((constant.bit_length() + 7) // 8, "big")).hexdigest(),
            "sampled_widths": cases, "depth_checks": 4095,
            "scope": "Exact samples support the stated all-integer binomial proof; they are not its quantifier justification."}


def run():
    return {"evaluator": evaluator_checks(), "reset": reset_checks(),
            "counters": counters(), "bounds": bounds()}
