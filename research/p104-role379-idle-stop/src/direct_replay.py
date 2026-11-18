#!/usr/bin/env python3
"""Independent rational interpreter for the #7636 comparison boundary."""

import argparse
import gzip
import hashlib
import json
import math
import os
import resource
import signal
import sys
import time
import traceback
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
from functools import cache
from pathlib import Path


A_CLOCKS = {127153, 127445, 127446, 127469, 130068}
CALLS = 17
PUBLIC = 1501
OWNED = 68
GATE = 1 << 224
PRICE_SCALE = 10**13
ARITY = {"MOVE": 5, "INIT": 3, "CLEAR": 3, "SCALE": 4, "ADD": 5, "COPY": 5}


@dataclass(frozen=True)
class SourcePin:
    head: str
    literal_sha: str
    gzip_sha: str
    invoice_sha: str
    certs_sha: str
    affected_sha: str
    events: int
    used_labels: int
    clears: int
    affected: int
    price: tuple[str, str]
    b_clocks: frozenset[int]


SOURCES = {
    7636: SourcePin(
        head="7e68d8dd62d9a38c0f3c942262a7a85ca7125b75",
        literal_sha="98b8c12ece2f323a6ff5cac8c7ed2f78ba3835438ea56b16bd7d4698ec5ad5b2",
        gzip_sha="1b4e33c3e3b69d1f1b42d019a2e372ac612fa28494bd8da18a734618f9bda659",
        invoice_sha="18adee673515c4ece7208b53c7cc17a2e121843d55f62067d2e43e341872f0d5",
        certs_sha="94809b766d041f6bb400df151de5702c5e8ec0a8a47c80ddfe5b2b3a5e0f09d2",
        affected_sha="cee6de59aa47c8633bf260490d4d5948b7e78276e92f2735765ef1c05a80c8ae",
        events=202668, used_labels=68, clears=180, affected=1023,
        price=("0.0036807241001", "0.0036807241002"), b_clocks=frozenset({131142, 131294}),
    ),
    7658: SourcePin(
        head="0a0e71c34a5ee5a1b59a8fe7bc6abd35a4d3dd82",
        literal_sha="fa84fcdecb534700cd00dc81b74889f549a653daa2fb3658cb8142e1eeb9b9e6",
        gzip_sha="dde0a987c2dd9e221208ca5043dfd6e2bdfbb8c4289fa20e2b93fae1696b3ea9",
        invoice_sha="26383ec33e4c4d552442b62f2bd7d9fd0a2fd0d357c1bcbf52ba913e11bb630e",
        certs_sha="02e0651a9a44c710225dd741d484f990e238bd5ac9e6510a7b90b17679879f47",
        affected_sha="741b7fd3306362d051c4d63b0d642ef47aaece842384d44423e997072f969f36",
        events=150010, used_labels=52, clears=234, affected=32,
        price=("0.00371676699784", "0.00371676699785"), b_clocks=frozenset({98054, 98204}),
    ),
}


class Refusal(ValueError):
    def __init__(self, code, detail, clock=None):
        super().__init__(f"{code} at {clock}: {detail}" if clock is not None else f"{code}: {detail}")
        self.record = dict(code=code, detail=detail, clock=clock)


def demand(condition, code, detail, clock=None):
    if not condition:
        raise Refusal(code, detail, clock)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def exact_json(raw):
    def unique_map(items):
        table = dict(items)
        demand(len(table) == len(items), "duplicate_key", "JSON object repeats a key")
        return table

    return json.loads(raw, object_pairs_hook=unique_map)


def read_pinned(path, expected, custody):
    raw = path.read_bytes()
    observed = digest(raw)
    demand(expected is None or observed == expected, "hash", f"{path.name}: expected {expected}, got {observed}")
    custody[path] = observed
    return raw


def read_word(path, gzip_hash, word_hash, custody):
    literal = gzip.decompress(read_pinned(path, gzip_hash, custody))
    demand(isinstance(word_hash, str) and word_hash == digest(literal), "literal_hash", path.name)
    return exact_json(literal)


def index(value, count, kind, clock=None):
    demand(type(value) is int and 0 <= value < count, kind, f"invalid index {value!r}", clock)
    return value


def chart_catalogue(frames):
    masks = []
    for number, basis in enumerate(frames):
        vectors = [0]
        for vector in basis:
            index(vector, 512, "frame_vector")
            demand(vector not in vectors, "frame_dimension", f"dependent direction in chart {number}")
            vectors.extend([old ^ vector for old in vectors])
        masks.append(sum(1 << vector for vector in vectors))
    return masks, [len(basis) for basis in frames]


def strictly_inside(smaller, larger):
    return smaller != larger and (smaller & larger) == smaller


def touched(event):
    if event[0] in {"ADD", "COPY"}:
        return event[1], event[2]
    return (event[1],)


@cache
def coefficient(literal):
    demand(type(literal) is str, "scalar_encoding", repr(literal))
    result = Fraction(literal)
    demand(result != 0, "zero_scalar", literal)
    return result


def add_scaled(destination, donor, scalar):
    # Published rows and observations retain the old dictionary.
    out = destination.copy()
    for formal_input, donor_coefficient in donor.items():
        new = out.get(formal_input, 0) + scalar * donor_coefficient
        if new:
            out[formal_input] = new
        else:
            out.pop(formal_input, None)
    return out


def verify_clear(event, rows, certificate, clock):
    owned = event[1]
    reconstructed = {}
    for donor, scalar in certificate.items():
        index(donor, len(rows), "clear_donor", clock)
        demand(donor != owned, "clear_self", f"owned field {owned} used as its own witness", clock)
        demand(rows[donor] is not None, "clear_dead_donor", f"role {donor}", clock)
        reconstructed = add_scaled(reconstructed, rows[donor], scalar)
    demand(rows[owned] or not certificate, "clear_zero_certificate", f"owned field {owned}", clock)
    demand(reconstructed == rows[owned], "clear_reconstruction", f"owned field {owned}", clock)


@cache
def denominator_parts(denominator):
    two_power = (denominator & -denominator).bit_length() - 1
    odd = denominator >> two_power
    remaining = odd
    for prime in (3, 5):
        while remaining % prime == 0:
            remaining //= prime
    return two_power, odd, remaining == 1


class Grid:
    def __init__(self):
        self.two_power = 0
        self.odd_lcm = 1
        self.numerator_bits = 1

    def see(self, number, clock):
        two_power, odd, smooth = denominator_parts(number.denominator)
        demand(smooth, "grid_prime", f"coefficient has denominator {number.denominator}", clock)
        self.two_power = max(self.two_power, two_power)
        self.odd_lcm = math.lcm(self.odd_lcm, odd)
        self.numerator_bits = max(self.numerator_bits, abs(number.numerator).bit_length())


def interpret(word, masks, dimensions, certificates):
    """MOVE changes chart and retains the same formal common-ambient row."""
    table_size = PUBLIC + OWNED
    frame_count = len(masks)
    row = [{formal_input: Fraction(1)} for formal_input in range(PUBLIC)] + [None] * OWNED
    chart = [index(chart_id, frame_count, "initial_chart") for chart_id in word["initial"]] + [None] * OWNED
    observations, erasures = [], []
    open_lifetime, finished_lifetimes = {}, []
    peak, labels = 0, set()
    counts, paid, move_pairs = Counter(), Counter(), Counter()
    paid_owned = Counter()
    nondyadic = Counter()
    scalar_units = 0
    grid = Grid()

    for clock, event in enumerate(word["program"]):
        demand(type(event) is list and len(event) >= 2, "event", repr(event), clock)
        operation = event[0]
        demand(operation in ARITY and len(event) == ARITY[operation], "event_shape", repr(event), clock)
        refs = [index(ref, table_size, "role", clock) for ref in touched(event)]
        target = refs[0]
        private = target >= PUBLIC
        counts[operation] += 1
        protected = operation == "COPY" or any(ref >= PUBLIC for ref in refs)
        before = tuple((chart[ref], row[ref]) for ref in refs) if protected else None
        scalars = ()

        if operation == "INIT":
            demand(private and row[target] is None, "init_lifetime", str(target), clock)
            here = index(event[2], frame_count, "chart", clock)
            row[target], chart[target] = {}, here
            open_lifetime[target] = here
            labels.add(target)
            peak = max(peak, len(open_lifetime))
        else:
            for ref in refs:
                demand(row[ref] is not None, "dead_operand", str(ref), clock)
            if operation == "MOVE":
                _, _, begin, end, flag = event
                index(begin, frame_count, "chart", clock)
                index(end, frame_count, "chart", clock)
                demand(type(flag) is bool and flag == private, "move_ownership", str(target), clock)
                demand(begin == chart[target], "move_origin", f"role {target} starts at {chart[target]}, got {begin}", clock)
                forwards = strictly_inside(masks[begin], masks[end])
                backwards = private and strictly_inside(masks[end], masks[begin])
                demand(forwards or backwards, "owned_nesting" if private else "public_ascent", f"{begin} to {end}", clock)
                rank = abs(dimensions[end] - dimensions[begin])
                paid[rank] += 1
                if private:
                    paid_owned[rank] += 1
                move_pairs[(begin, end)] += 1
                chart[target] = end
            elif operation == "CLEAR":
                here = index(event[2], frame_count, "chart", clock)
                demand(private and here == chart[target], "clear_lifetime", str(target), clock)
                ordinal = len(erasures)
                demand(ordinal < len(certificates), "extra_clear", str(target), clock)
                expected, terms = certificates[ordinal]
                demand(tuple(event) == expected, "clear_order", f"ordered CLEAR {ordinal}", clock)
                verify_clear(event, row, terms, clock)
                erasures.append((clock, tuple(event), row[target]))
                finished_lifetimes.append((target, open_lifetime.pop(target), here))
                row[target], chart[target] = None, None
            else:
                here = index(event[-1], frame_count, "chart", clock)
                demand(all(chart[ref] == here for ref in refs), "scalar_chart", repr(event), clock)
                amount = coefficient(event[-2])
                if operation == "SCALE":
                    row[target] = {i: amount * value for i, value in row[target].items()}
                    scalars = row[target].values()
                else:
                    donor = refs[1]
                    demand(donor != target, "scalar_alias", str(target), clock)
                    if operation == "COPY":
                        demand(not row[target], "copy_nonzero", str(target), clock)
                    row[target] = add_scaled(row[target], row[donor], amount)
                    scalars = (row[target][i] for i in row[donor] if i in row[target])
                grid.see(amount, clock)
                if denominator_parts(amount.denominator)[1] > 1:
                    nondyadic[operation] += 1
                numerator = abs(amount.numerator)
                additions = numerator.bit_count() if operation in {"ADD", "COPY"} else 0
                scalar_units += 4 * (numerator.bit_length() + amount.denominator.bit_length() + 1 + additions)
        for number in scalars:
            grid.see(number, clock)
        if protected:
            after = tuple((chart[ref], row[ref]) for ref in refs)
            observations.append((clock, tuple(event), before, after))

    demand(not open_lifetime, "live_owned_at_end", repr(open_lifetime))
    demand(len(erasures) == len(certificates), "clear_count", str(len(erasures)))
    demand(chart[:PUBLIC] == word["final"], "final_charts", "declared public output charts")
    primary = set(word["live"]) | {port + 112 for port in word["live"]}
    primary.update(word["hosted"]["X2"], word["hosted"]["Y2"])
    targets, altered_helpers = Counter(), []
    for role, (initial, final) in enumerate(zip(word["initial"], word["final"], strict=True)):
        if role in primary:
            continue
        if row[role] != {role: 1}:
            altered_helpers.append(role)
        rank = dimensions[final] - dimensions[initial]
        demand(rank > 0, "helper_rank", f"public role {role}, rank {rank}")
        targets[rank] += 1
    return dict(rows=row, charts=chart, observations=observations, erasures=erasures,
                lifetimes=finished_lifetimes, peak=peak, labels=sorted(labels), counts=counts,
                paid=paid, paid_owned=paid_owned, targets=targets, move_pairs=move_pairs, altered_helpers=altered_helpers,
                grid=vars(grid), nondyadic=dict(nondyadic), scalar_units=scalar_units)


def source_certificates(raw, source_program, clear_count):
    table = exact_json(raw)
    demand(isinstance(table, dict) and set(table) == {"clear_event_index"}, "certificate_schema", "CLEAR index")
    table = table["clear_event_index"]
    clocks = [i for i, event in enumerate(source_program) if event[0] == "CLEAR"]
    demand(len(clocks) == clear_count and set(table) == {str(i) for i in clocks}, "certificate_coverage", repr(len(table)))
    result = []
    for clock in clocks:
        terms = {}
        for key, value in table[str(clock)].items():
            role = index(int(key), PUBLIC + OWNED, "clear_donor", clock)
            demand(str(role) == key, "clear_donor_spelling", key, clock)
            terms[role] = coefficient(value)
        result.append((tuple(source_program[clock]), terms))
    return result


def exact_compare(reference, candidate):
    demand(reference["charts"] == candidate["charts"], "end_charts", "final public and private charts")
    demand(reference["lifetimes"] == candidate["lifetimes"], "owned_order", "ordered owned lifetimes")
    demand(reference["peak"] == candidate["peak"], "owned_peak", "maximum simultaneous lifetimes")
    for kind in ("erasures", "observations"):
        left, right = reference[kind], candidate[kind]
        demand(len(left) == len(right), "protected_count", kind)
        for a, b in zip(left, right, strict=True):
            demand(a[1:] == b[1:], "protected_value", f"{kind} at source clock {a[0]}", b[0])
    for role, (a, b) in enumerate(zip(reference["rows"], candidate["rows"], strict=True)):
        demand(a == b, "final_row", f"public row {role} full formal-input coefficient map")


def literal_changes(source, candidate):
    """Recover short edit blocks using shared literal anchors on both tapes."""
    i, j = 0, 0
    changes = []
    previous_window = 0
    while i < len(source) and j < len(candidate):
        if source[i] == candidate[j]:
            i += 1
            j += 1
            previous_window += 1
            continue
        matches = []
        for old_size in range(9):
            for new_size in range(9):
                old_anchor = source[i + old_size:i + old_size + 5]
                new_anchor = candidate[j + new_size:j + new_size + 5]
                if len(old_anchor) == 5 and old_anchor == new_anchor:
                    matches.append((old_size + new_size, old_size, new_size))
        matches.sort()
        demand(matches and matches[0][0] > 0, "literal_alignment", "no anchor near edit", i)
        demand(len(matches) == 1 or matches[0][0] != matches[1][0], "literal_alignment", "nonunique anchor", i)
        _, old_size, new_size = matches[0]
        demand(previous_window >= 5, "literal_alignment", "no shared prefix near edit", i)
        changes.append(dict(source_start=i, source=source[i:i + old_size],
                            candidate_start=j, candidate=candidate[j:j + new_size]))
        i += old_size
        j += new_size
        previous_window = 0
    demand(i == len(source) and j == len(candidate), "literal_tail", "unmatched terminal events")
    return changes


def verify_scope(changes, program, variant, b_clocks):
    permitted = b_clocks if variant == "B" else A_CLOCKS | b_clocks
    removed = {j for edit in changes for j in range(edit["source_start"], edit["source_start"] + len(edit["source"]))}
    demand(removed == permitted, "scope", f"replaced source clocks {sorted(removed)}")
    a_insertions, b_insertions = [], []
    for edit in changes:
        if edit["source_start"] in b_clocks:
            b_insertions.extend(edit["candidate"])
        else:
            a_insertions.extend(edit["candidate"])
    demand(b_insertions == [["MOVE", 379, 748, 1072, False]], "idle_replacement", repr(b_insertions))
    first, last = sorted(b_clocks)
    demand(program[first] == ["MOVE", 379, 748, 1065, False] and program[last] == ["MOVE", 379, 1065, 1072, False],
           "idle_source", "role 379's two leg identities")
    demand(not any(379 in touched(event) for event in program[first + 1:last]), "idle_intervening_operand", "role 379")
    if variant == "C":
        demand(all(set(touched(event)) <= {902, 1091} for event in a_insertions), "contact_operands", repr(a_insertions))
        contacts = [event for event in a_insertions if event[0] == "ADD"]
        demand(len(contacts) == 1 and contacts[0][1:3] == [1091, 902] and contacts[0][4] == 373,
               "contact_chart", repr(contacts))


def histogram(raw):
    result = Counter()
    for rank, quantity in raw.items():
        parsed = int(rank)
        demand(str(parsed) == rank and parsed > 0, "invoice_rank", repr(rank))
        demand(type(quantity) is int and quantity > 0, "invoice_count", repr(quantity))
        result[parsed] = quantity
    return result


def delta(before, after):
    return {rank: after[rank] - before[rank] for rank in sorted(before.keys() | after.keys())
            if after[rank] != before[rank]}


def signed_invoice(pinned, original, candidate):
    demand(pinned["schema"] == "integer-mult-recursive-invoice/v1", "invoice_schema", str(pinned["schema"]))
    demand(pinned["contract"]["model"] == "mixed-target-unnormalized-power-v1"
           and pinned["contract"]["ambient_rank"] == 145
           and pinned["contract"]["boundary"] == "complete signed #7113 caller application with 17 native calls",
           "invoice_contract", str(pinned["contract"]))
    residual, invoice = {}, {}
    for key in ("paid", "targets"):
        current = histogram(pinned[key])
        residual[key], invoice[key] = Counter(), Counter()
        for rank in current.keys() | original[key].keys() | candidate[key].keys():
            kept = current[rank] - CALLS * original[key][rank]
            demand(kept >= 0, "invoice_negative_residual", f"{key} at rank {rank}")
            if kept:
                residual[key][rank] = kept
            count = kept + CALLS * candidate[key][rank]
            if count:
                invoice[key][rank] = count
    return {"schema": pinned["schema"], "contract": pinned["contract"], **invoice}, residual


def signed_weights(invoice):
    paid, targets = (histogram({str(k): v for k, v in invoice[key].items()}) for key in ("paid", "targets"))
    return {rank: rank * change for rank, change in delta(paid, targets).items()}


def quantize(lower, upper):
    return Fraction(math.floor(lower * GATE), GATE), Fraction(math.ceil(upper * GATE), GATE)


def log_one_to_two(z):
    """2 atanh(z), where 0 <= z <= 1/3. Bound the positive omitted tail."""
    square = z * z
    term, total = z, Fraction(0)
    for i in range(96):
        total += term / (2 * i + 1)
        term *= square
    return 2 * total, 2 * (total + term / (193 * (1 - square)))


@cache
def log_integer(number):
    exponent = number.bit_length() - 1
    divisor = 1 << exponent
    lower, upper = log_one_to_two(Fraction(number - divisor, number + divisor))
    two_lo, two_hi = log_one_to_two(Fraction(1, 3))
    return quantize(lower + exponent * two_lo, upper + exponent * two_hi)


@cache
def exp_minus_small(value):
    """Even and odd partial sums bound exp(-x) for 0 <= x < 1."""
    demand(0 <= value < 1, "price_exponential_domain", str(value))
    term, total = Fraction(1), Fraction(1)
    for k in range(1, 33):
        term = -term * value / k
        total += term
    return quantize(total - term * value / 33, total)


def signed_price(weights, start, end, derivative=False):
    lo = hi = Fraction(0)
    for rank, weight in weights.items():
        log_lo, log_hi = log_integer(rank)
        power_lo = exp_minus_small(end * log_hi)[0]
        power_hi = exp_minus_small(start * log_lo)[1]
        if derivative:
            power_lo, power_hi = power_lo * log_lo, power_hi * log_hi
            weight = -weight
        a, b = weight * power_lo, weight * power_hi
        lo += min(a, b)
        hi += max(a, b)
    return lo, hi


def approximate_grid(weights):
    """Propose neighboring 13-place decimals. Only the exact sign test accepts them."""
    log = {rank: math.log(rank) for rank in weights}
    low, high = 0, PRICE_SCALE // 100
    while high - low > 1:
        middle = (low + high) // 2
        estimate = math.fsum(weight * math.exp(-middle / PRICE_SCALE * log[rank]) for rank, weight in weights.items())
        if estimate > 0:
            low = middle
        else:
            high = middle
    return (f"0.{low:013d}", f"0.{high:013d}")


def decimal_text(value, places):
    sign = "-" if value < 0 else ""
    quotient, suffix = divmod(abs(value), 10**places)
    return f"{sign}{quotient}.{suffix:0{places}d}"


def outward_decimal(interval, places=26):
    scale = 10**places
    return [decimal_text(math.floor(interval[0] * scale), places), decimal_text(math.ceil(interval[1] * scale), places)]


def price_bracket(weights, bracket):
    left, right = map(Fraction, bracket)
    lower = signed_price(weights, left, left)
    upper = signed_price(weights, right, right)
    slope = signed_price(weights, left, right, derivative=True)
    demand(left < right and lower[0] > 0 > upper[1] and slope[1] < 0, "price_bracket", repr(bracket))
    return dict(kappa=list(bracket), at_lower=outward_decimal(lower), at_upper=outward_decimal(upper),
                derivative=outward_decimal(slope), weighted_surplus=sum(weights.values()))


def with_event(word, clock, changed):
    tape = list(word["program"])
    tape[clock] = changed
    return {**word, "program": tape}


def rejected(expected, action):
    try:
        action()
    except Refusal as error:
        demand(error.record["code"] in expected, "wrong_control_rejection", repr(error.record))
        return error.record
    raise Refusal("control_accepted", repr(expected))


def adverse_controls(word, candidate, masks, dimensions, certificates, changes, invoice_seed, original):
    direct_clock = next(edit["candidate_start"] + i for edit in changes
                        for i, event in enumerate(edit["candidate"])
                        if event == ["MOVE", 379, 748, 1072, False])
    direct = word["program"][direct_clock]
    wrong_end = next(b for b, rank in enumerate(dimensions)
                     if rank == dimensions[direct[3]] and not strictly_inside(masks[direct[2]], masks[b]))
    wrong_chart = with_event(word, direct_clock, [*direct[:3], wrong_end, False])
    chart = rejected({"public_ascent"}, lambda: interpret(wrong_chart, masks, dimensions, certificates))
    demand(chart["clock"] == direct_clock, "wrong_control_clock", repr(chart))

    # A final-hub public ADD preserves the paid/target ranks and changes a real output.
    last_clear = candidate["erasures"][-1][0]
    clock, event = next((i, word["program"][i]) for i in range(len(word["program"]) - 1, last_clear, -1)
                        if word["program"][i][0] == "ADD" and max(touched(word["program"][i])) < PUBLIC)
    wrong = [*event[:3], str(-coefficient(event[3])), event[4]]
    mutated = interpret(with_event(word, clock, wrong), masks, dimensions, certificates)
    good_invoice = signed_invoice(invoice_seed, original, candidate)[0]
    control_invoice = signed_invoice(invoice_seed, original, mutated)[0]
    demand(good_invoice == control_invoice, "control_price_changed", f"sign mutation at {clock}")
    good = rejected({"final_row"}, lambda: exact_compare(candidate, mutated))

    first_event, first_terms = certificates[0]
    invalid = [(first_event, {**first_terms, first_event[1]: Fraction(1)}), *certificates[1:]]
    clear = rejected({"clear_self"}, lambda: interpret(word, masks, dimensions, invalid))
    return dict(chart=dict(literal_before=direct, literal_after=wrong_chart["program"][direct_clock], rejection=chart),
                coefficient=dict(clock=clock, literal_before=event, literal_after=wrong, invoice_identical=True, rejection=good),
                certificate=dict(rejection=clear))


def ordered_proof_trace(result):
    def serial_row(row):
        return None if row is None else [(i, str(value)) for i, value in sorted(row.items())]

    def serialize(data):
        return digest(json.dumps(data, separators=(",", ":")).encode())

    return {
        "final_rows_sha256": serialize([serial_row(row) for row in result["rows"]]),
        "ordered_clear_sha256": serialize([(event, serial_row(row)) for _, event, row in result["erasures"]]),
        "ordered_protected_sha256": serialize([(event,
                                                [(chart, serial_row(row)) for chart, row in before],
                                                [(chart, serial_row(row)) for chart, row in after])
                                               for _, event, before, after in result["observations"]]),
        "peak_owned": result["peak"],
        "owned_label_count": len(result["labels"]),
        "owned_lifetimes": len(result["lifetimes"]),
        "owned_moves": sum(result["paid_owned"].values()),
        "owned_add_zero_refills": owned_add_zero_refills(result["observations"]),
        "ordered_clear_values": len(result["erasures"]),
        "ordered_owned_or_copy_observations": len(result["observations"]),
        "protected_observations_by_opcode": Counter(event[0] for _, event, _, _ in result["observations"]),
        "nonzero_public_output_coefficients": sum(len(row) for row in result["rows"][:PUBLIC]),
        "events_by_opcode": result["counts"],
        "changed_operation_grid": result["grid"],
        "non_dyadic_literal_events": result["nondyadic"],
        "literal_scalar_units": result["scalar_units"],
        "tape_move_pair_count": len(result["move_pairs"]),
        "native_paid": result["paid"],
        "native_paid_owned": result["paid_owned"],
        "native_helper_targets": result["targets"],
    }


def owned_add_zero_refills(observations):
    count = 0
    pending = set()
    for _, (operation, target, *_), before, after in observations:
        if operation in {"INIT", "CLEAR"}:
            pending.discard(target)
        elif operation == "ADD" and target >= PUBLIC:
            if target in pending and before[1][1]:
                count += 1
                pending.remove(target)
            if not after[0][1]:
                pending.add(target)
    return count


def run(args, custody, report):
    pin = SOURCES[args.source_pr]
    source = read_word(args.source_word or args.data / "word.json.gz", pin.gzip_sha, pin.literal_sha, custody)
    demand(source["schema"] == "p104-accumulated-block-composition/2", "word_schema", source["schema"])
    demand(source["public"] == len(source["initial"]) == len(source["final"]) == PUBLIC
           and source["owned_fields"] == OWNED and len(source["program"]) == pin.events and len(source["frames"]) == 1096,
           "source_denominator", "public, owned, event and chart totals")
    if args.source_pr == 7658:
        demand(source["initial"][457] == 281, "source_entrance", "row 457 enters at chart 281")
    if args.candidate is not None:
        candidate = read_word(args.candidate, args.candidate_gzip_sha, args.candidate_json_sha, custody)
        demand({k: v for k, v in source.items() if k != "program"} ==
               {k: v for k, v in candidate.items() if k != "program"}, "word_header", "candidate header differs")
        changes = literal_changes(source["program"], candidate["program"])
        verify_scope(changes, source["program"], args.variant, pin.b_clocks)
    certificate_bytes = read_pinned(args.source_certificates or args.data / "clear-certificates.json", pin.certs_sha, custody)
    certs = source_certificates(certificate_bytes, source["program"], pin.clears)
    affected_bytes = read_pinned(args.data / "affected-pairs-new.json", pin.affected_sha, custody)
    affected = {tuple(pair) for pair in exact_json(affected_bytes)}
    demand(len(affected) == pin.affected, "affected_census", str(len(affected)))
    pinned_invoice = exact_json(read_pinned(args.source_invoice or args.data / "invoice-new.json", pin.invoice_sha, custody))
    masks, dimensions = chart_catalogue(source["frames"])
    before = interpret(source, masks, dimensions, certs)
    demand(before["peak"] == 50 and len(before["labels"]) == pin.used_labels, "owned_denominator", "peak or used label count")
    if args.source_pr == 7636:
        demand(sum(before["paid_owned"].values()) == 47, "owned_moves", "source MOVE count")
    if args.source_pr == 7658:
        demand(owned_add_zero_refills(before["observations"]) == 0, "owned_zero_refill", "source has an exact-zero join")
    demand(not before["altered_helpers"], "helper_identity", repr(before["altered_helpers"]))
    source_invoice, residual = signed_invoice(pinned_invoice, before, before)
    source_weights = signed_weights(source_invoice)
    report["source"] = dict(pr=args.source_pr, head=pin.head, literal_sha256=pin.literal_sha, gzip_sha256=pin.gzip_sha,
                            full_signed_invoice=source_invoice, caller_residual=residual,
                            price=price_bracket(source_weights, pin.price), trace=ordered_proof_trace(before),
                            public=PUBLIC, allocated_owned=OWNED, frames=len(masks),
                            affected_predecessor_census=len(affected),
                            clear_certificate_term_counts=sorted(Counter(len(terms) for _, terms in certs).items()))
    if args.candidate is None:
        report["result"] = "PASS_SOURCE_REPLAY_AND_CONDITIONAL_PRICE"
        return

    after = interpret(candidate, masks, dimensions, certs)
    exact_compare(before, after)
    invoice, _ = signed_invoice(pinned_invoice, before, after)
    weights = signed_weights(invoice)
    bracket = approximate_grid(weights)
    candidate_price = price_bracket(weights, bracket)
    demand(Fraction(bracket[0]) > Fraction(pin.price[1]), "strict_price_improvement", repr(bracket))
    if args.claim:
        claim = Fraction(args.claim)
        demand(claim > Fraction(pin.price[1]), "claim_exceeds_source", args.claim)
        sign = signed_price(weights, claim, claim)
        preceding = signed_price(source_weights, claim, claim)
        demand(sign[0] > 0 > preceding[1], "claim_price_sign", args.claim)
        candidate_price.update(claim=args.claim, at_claim=outward_decimal(sign), source_at_claim=outward_decimal(preceding))

    source_pairs, candidate_pairs = before["move_pairs"], after["move_pairs"]
    changed_pair_counts = [[*pair, source_pairs[pair], candidate_pairs[pair]]
                           for pair in sorted(source_pairs.keys() | candidate_pairs.keys())
                           if source_pairs[pair] != candidate_pairs[pair]]
    changes_out = {key: delta(source_invoice[key], invoice[key]) for key in ("paid", "targets")}
    ordinary_variable_delta = CALLS * (after["scalar_units"] - before["scalar_units"]
                                      + 1000 * (sum(after["paid"].values()) - sum(before["paid"].values())))
    report["candidate"] = dict(variant=args.variant, literal_sha256=args.candidate_json_sha, gzip_sha256=args.candidate_gzip_sha,
                               literal_changes=changes, full_signed_invoice=invoice, full_signed_delta=changes_out,
                               price=candidate_price, trace=ordered_proof_trace(after),
                               changed_pair_multiplicities=changed_pair_counts,
                               pairs_new_to_word=sorted(candidate_pairs.keys() - source_pairs.keys()),
                               pairs_removed_from_word=sorted(source_pairs.keys() - candidate_pairs.keys()),
                               affected_census_with_literal_edit=len(affected | {tuple(pair[:2]) for pair in changed_pair_counts}),
                               changed_native_ordinary_units_at_17_calls=ordinary_variable_delta)
    report["controls"] = adverse_controls(candidate, after, masks, dimensions, certs, changes, pinned_invoice, before)
    report["result"] = "PASS_PAIRED_EXACT_REPLAY_AND_CONDITIONAL_PRICE"


def cap(source_pr):
    usable = sorted(os.sched_getaffinity(0))
    # The two independent pinned replays can use different available CPUs.
    chosen = usable[-1] if source_pr == 7658 else usable[len(usable) // 2]
    os.sched_setaffinity(0, {chosen})
    address = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (address, address))
    resource.setrlimit(resource.RLIMIT_CPU, (240, 241))

    def timeout(_signum, _frame):
        raise Refusal("timeout", "240-second elapsed-time cap")

    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(240)
    return dict(cpu=chosen, address_space_bytes=address, cpu_seconds=240, wall_seconds=240)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--source-pr", type=int, choices=tuple(SOURCES), default=7636)
    parser.add_argument("--source-word", type=Path)
    parser.add_argument("--source-certificates", type=Path)
    parser.add_argument("--source-invoice", type=Path)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--candidate-gzip-sha")
    parser.add_argument("--candidate-json-sha")
    parser.add_argument("--variant", choices=("B", "C"))
    parser.add_argument("--claim")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.candidate is not None and not (args.candidate_gzip_sha and args.candidate_json_sha and args.variant):
        parser.error("a candidate requires both hashes and its variant")
    if args.source_pr == 7658 and args.variant == "C":
        parser.error("#7658 is pinned only for the standalone role-379 edit")
    report = {"schema": "p104-independent-exact-replay/2", "limits": cap(args.source_pr),
              "started": datetime.now(timezone.utc).isoformat(),
              "price_convention": "sum (targets_r - paid_r) * r^(1-C)",
              "assurance": "Exact literal row and certificate replay with the pinned source's conditional #7113 invoice residual."}
    custody = {}
    start = time.perf_counter()
    with args.out.open("x") as output:
        try:
            run(args, custody, report)
            for path, expected in custody.items():
                demand(digest(path.read_bytes()) == expected, "input_changed_during_run", path.name)
            roles = {
                args.source_word or args.data / "word.json.gz": "source_gzip",
                args.source_certificates or args.data / "clear-certificates.json": "clear_certificates",
                args.source_invoice or args.data / "invoice-new.json": "source_invoice",
                args.data / "affected-pairs-new.json": "source_affected_census",
                args.candidate: "candidate_gzip",
            }
            report["input_bytes_rechecked"] = {roles[path]: sha for path, sha in custody.items()}
        except Exception as error:
            report["result"] = "REFUSED"
            report["error"] = error.record if isinstance(error, Refusal) else repr(error)
            traceback.print_exc()
        report["finished"] = datetime.now(timezone.utc).isoformat()
        report["elapsed_seconds"] = time.perf_counter() - start
        used = resource.getrusage(resource.RUSAGE_SELF)
        report["resource_usage"] = dict(user_cpu_seconds=used.ru_utime, system_cpu_seconds=used.ru_stime, max_rss_kib=used.ru_maxrss)
        json.dump(report, output, indent=2, sort_keys=True)
        output.write("\n")
    signal.alarm(0)
    print(report["result"])
    return report["result"] == "REFUSED"


if __name__ == "__main__":
    sys.exit(main())
