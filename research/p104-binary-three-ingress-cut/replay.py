#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the fixed-observation binary three-ingress cut using pinned public inputs."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
import json
from pathlib import Path
from typing import NamedTuple


COMPARATOR = "14c74c6a67108f675ac1196a5f2415ead0920e71"
WORD_COMMIT = "89a67c404226d51028e135de2b9169e9020d57af"
CALLER_COMMIT = "e54523517d0f03e58352e647c403a5af3e525a57"
WORD_GZIP = "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9"
WORD = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"
LAYOUT = "a0ffffd99fb9b91f0013695877480766319ac51b926ed00dd5f7ec32f2d1e1a6"
CALLER = "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b"
APPLICATION = "1b2d87e93ae023f5ffd464546af53281b6cb4963dfd76ae4742e0a5540b752fa"
TARGET = "0.003889928046155"
BRIDGE_PACKET = 3553
BRIDGE_OWNER = 411


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path, digest, compressed=False):
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == digest, f"SHA-256 mismatch for {path}")
    return json.loads(gzip.decompress(raw) if compressed else raw)


def canonical_hash(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rational_rank(rows):
    work = [list(row) for row in rows]
    rank = 0
    for column in range(8):
        pivot = next((j for j in range(rank, len(work)) if work[j][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for row in work[rank + 1:]:
            factor = row[column] / work[rank][column]
            if factor:
                row[column:] = [x - factor * y for x, y in zip(row[column:], work[rank][column:])]
        rank += 1
    return rank


def annihilates(left, right):
    return all(sum(x * y for x, y in zip(row, dual)) == 0 for row in left for dual in right)


class Atlas:
    def __init__(self, frames):
        self.body = {}
        self.dual = {}
        for label, rows in frames.items():
            chart = int(label)
            body, dual = (tuple(tuple(map(Fraction, row)) for row in rows[k]) for k in ("B", "A"))
            require(len(body) == rows["dim"] and len(body + dual) == 8, f"frame counts at {chart}")
            require(all(len(row) == 8 for row in body + dual), f"frame dimensions at {chart}")
            require(rational_rank(body + dual) == 8 and annihilates(body, dual),
                    f"frame rank and orthogonality at {chart}")
            self.body[chart], self.dual[chart] = body, dual

    @cache
    def grade(self, first, second):
        low, high = sorted((first, second), key=lambda chart: len(self.body[chart]))
        difference = len(self.body[high]) - len(self.body[low])
        return difference if difference > 0 and annihilates(self.body[low], self.dual[high]) else 0

    def main_contacts(self, starts, ends):
        for j in range(111):
            head, body = self.body[starts[j]], self.body[ends[j + 111]]
            require((len(head), len(body), len(self.body[starts[j + 111]]),
                     len(self.body[ends[j]])) == (1, 7, 0, 8), f"contact dimensions at {j}")
            require(annihilates(head, body) and rational_rank(head + body) == 8,
                    f"contact decomposition at {j}")
        return 111


class Observation(NamedTuple):
    label: int
    time: int
    row: int


class Packet(NamedTuple):
    source: int
    receiver: int
    clock: int
    arrival: Observation
    grade: int


class Tape(NamedTuple):
    stock: dict
    demand: dict
    packets: dict
    output: list
    dirty: int
    last_retirement: int


def run_tape(word, atlas, reverse, omit=None):
    """Track whole-field chart tags and coefficient rows over all public inputs."""
    public, private = word["public"], word["owned_fields"]
    start, end = [word[k] for k in (("final", "start") if reverse else ("start", "final"))]
    program = word["program"]
    identifiers = dict(zip((i for i, event in enumerate(program) if event[0] == "MOVE"),
                           range(public, public + len(program))))
    cells = [(chart, 1 << owner) for owner, chart in enumerate(start)] + [None] * private
    stock, demand, packets = defaultdict(list), defaultdict(list), {}
    for owner, chart in enumerate(start):
        stock[chart].append(Observation(owner, -1, 1 << owner))
    order = range(len(program) - 1, -1, -1) if reverse else range(len(program))
    opens, retires = ("CLEAR", "INIT") if reverse else ("INIT", "CLEAR")
    dirty, last_retirement = 0, None

    for time, clock in enumerate(order):
        if clock == omit:
            continue
        operation, address, *args = program[clock]
        require(0 <= address < len(cells), f"field address at {clock}")
        cell = cells[address]
        if operation in (opens, retires):
            chart, = args
            require(address >= public and chart in atlas.body, f"private chart at {clock}")
            if operation == opens:
                require(cell is None, f"activation of a live field at {clock}")
                cells[address] = chart, 0
            else:
                require(cell is not None and cell[0] == chart, f"private retirement at {clock}")
                dirty += bool(cell[1])
                cells[address] = None
                last_retirement = clock
        elif operation == "ADD":
            peer, chart = args
            require(0 <= peer < len(cells) and peer != address, f"ADD operands at {clock}")
            other = cells[peer]
            require(cell is not None and other is not None and cell[0] == other[0] == chart,
                    f"ADD chart at {clock}")
            cells[peer if reverse else address] = chart, cell[1] ^ other[1]
        elif operation == "SWAP":
            peer, = args
            require(0 <= peer < len(cells) and peer != address and cell is not None
                    and cells[peer] is not None, f"SWAP operands at {clock}")
            cells[address], cells[peer] = cells[peer], cell
        else:
            require(operation == "MOVE" and address >= public, f"operation at {clock}")
            source, receiver = args[::-1] if reverse else args
            grade = atlas.grade(source, receiver)
            require(cell is not None and cell[0] == source and grade > 0, f"MOVE ports at {clock}")
            arrival = Observation(identifiers[clock], time, cell[1])
            packets[arrival.label] = Packet(source, receiver, clock, arrival, grade)
            demand[source].append(arrival)
            stock[receiver].append(arrival)
            cells[address] = receiver, cell[1]

    require(all(cell is None for cell in cells[public:]), "unretired private field")
    require([chart for chart, _ in cells[:public]] == end, "wrong public endpoints")
    output = [row for _, row in cells[:public]]
    for owner, chart in enumerate(end):
        demand[chart].append(Observation(~owner, len(program), output[owner]))
    return Tape(stock, demand, packets, output, dirty, last_retirement)


def expected_operator(reverse):
    rows = [1 << owner for owner in range(680)]
    for j in range(111):
        dst, src = (j, j + 111) if reverse else (j + 111, j)
        rows[dst] ^= 1 << src
    return rows


def native_checks(word, atlas):
    packets = {row[1] for row in word["program"] if row[0] == "MOVE"}
    deleted_add, = [j for j, row in enumerate(word["program"])
                    if row[0] == "ADD" and row[1] in packets and row[2] == BRIDGE_OWNER]
    out = {}
    bridge_bit = 1 << BRIDGE_OWNER
    for reverse in (False, True):
        tape = run_tape(word, atlas, reverse)
        expected = expected_operator(reverse)
        require(tape.output == expected, "complete native operator")
        require(tape.dirty == 3554, "dirty private retirement count")
        bridge = tape.packets[BRIDGE_PACKET]
        route = (1, 509) if reverse else (509, 1)
        require((bridge.source, bridge.receiver, bridge.clock, bridge.arrival.row, bridge.grade) ==
                (*route, 31290, bridge_bit, 4), "protected owner-411 bridge geometry and row")
        require(tape.output[BRIDGE_OWNER] == bridge_bit, "protected owner-411 return")
        require([k for k, p in tape.packets.items() if p.arrival.row & bridge_bit] == [BRIDGE_PACKET],
                "protected owner-411 isolation in all paid packets")
        changed = run_tape(word, atlas, reverse, omit=deleted_add).output
        require([a ^ b for a, b in zip(changed, expected)] ==
                [bridge_bit if i == BRIDGE_OWNER else 0 for i in range(680)],
                "omitting the owner-411 ADD must flip exactly one coefficient")
        try:
            run_tape(word, atlas, reverse, omit=tape.last_retirement)
        except ValueError as error:
            require(str(error) == "unretired private field", "dirty retirement omission disposition")
        else:
            raise ValueError("omitting a dirty retirement was accepted")
        out[reverse] = tape
    return out[False], out[True], deleted_add


def reduce_xor(row, basis):
    # Ascending pivots make this a linear reduction on actual public coefficient rows.
    for bit, vector in basis:
        if row & bit:
            row ^= vector
    return row


def xor_basis(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row & -row
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return sorted(pivots.items())


def directions(plane, rows):
    basis = xor_basis(rows)
    return [i for i, row in enumerate(plane, 1) if reduce_xor(row, basis) == 0]


def independent_choices(first, second):
    return [(a, b) for a in first for b in second if a != b]


def find_rank_gaps(tape):
    gaps = []
    tested = 0
    for receiver, received in sorted(tape.stock.items()):
        ingress = sorted(obs.label for obs in received
                         if obs.label in tape.packets and obs.label != BRIDGE_PACKET)
        if len(ingress) < 2:
            continue
        tested += 1
        holdout = set(ingress)
        fixed = xor_basis(obs.row for obs in received if obs.label not in holdout)
        added_rank = len(xor_basis(reduce_xor(obs.row, fixed) for obs in received
                                   if obs.label in holdout))
        require(added_rank == len(ingress), f"independent ingress quotient at {receiver}")
        demand_rank = len(xor_basis(reduce_xor(obs.row, fixed) for obs in tape.demand[receiver]))
        if demand_rank < added_rank:
            gaps.append((receiver, ingress, demand_rank))
    return tested, gaps


def causal_closure(assignment, readers, stock, plane):
    """Allow unlimited retention and grant every fixed payload except the two readers."""
    held_back = {reader.label for reader in readers}
    deposits = set()
    released = set()
    previous = None
    while previous != (len(deposits), len(released)):
        previous = (len(deposits), len(released))
        for port, (source, direction) in enumerate(assignment):
            sender_basis = xor_basis(obs.row for obs in stock[source]
                                     if obs.label not in held_back or obs.label in released)
            if reduce_xor(plane[direction - 1], sender_basis) == 0:
                deposits.add(port)
        received = xor_basis(plane[assignment[port][1] - 1] for port in deposits)
        released.update(reader.label for reader in readers if reduce_xor(reader.row, received) == 0)
    return len(deposits), sorted(released)


def check_bank(receiver, ingress, demand_rank, tape, atlas, changing_receivers):
    packets = [tape.packets[k] for k in ingress]
    readers = [obs for obs in tape.demand[receiver] if obs.row]
    require(len(ingress) == 3 and demand_rank == len(readers) == 2, f"bank dimensions at {receiver}")
    require({obs.label for obs in tape.stock[receiver]} == set(ingress), f"zero stock at {receiver}")
    require(all(p.grade == 1 for p in packets), f"three original grade-one sends at {receiver}")
    require(all(p.arrival.time < r.time for p in packets for r in readers), f"reader order at {receiver}")
    require(all(r.label in tape.packets for r in readers), f"protected exterior readers at {receiver}")
    require(all(r.label != BRIDGE_PACKET for r in readers), f"fixed owner-411 at {receiver}")

    u, v = (reader.row for reader in readers)
    plane = (u, v, u ^ v)
    require(all(plane) and len(set(plane)) == 3, f"two distinct directions at {receiver}")
    a, b, c = (p.arrival.row for p in packets)
    require((u, v) == (a ^ c, a ^ b), f"original reader rows at {receiver}")
    sources = sorted(source for source in atlas.body if atlas.grade(source, receiver) == 1)
    require(len(sources) == 4 and not changing_receivers.intersection(sources),
            f"four grade-one suppliers outside the joint cut at {receiver}")

    stock = tape.stock
    all_clock = {s: directions(plane, (o.row for o in stock[s])) for s in sources}
    before_readers = {s: [directions(plane, (o.row for o in stock[s] if o.time < r.time))
                          for r in readers] for s in sources}
    fixed_options = [directions(plane, (o.row for o in stock[p.source] if o.time < p.arrival.time))
                     for p in packets]
    require([all_clock[p.source] for p in packets] == fixed_options == [[], [3], [3]],
            f"fixed port intersections at {receiver}")

    fixed_cases = []
    for first, second in combinations(range(3), 2):
        keep = first, second
        require(not independent_choices(*(fixed_options[i] for i in keep)),
                f"fixed ports could meet original deadlines at {receiver}")
        require(not independent_choices(*(all_clock[packets[i].source] for i in keep)),
                f"fixed ports could span the plane with all stock at {receiver}")
        fixed_cases.append([ingress[i] for i in keep])

    mandatory = {}
    for direction, reader in enumerate(readers, 1):
        source = tape.packets[reader.label].receiver
        basis = xor_basis(o.row for o in stock[source] if o.label != reader.label)
        residue = reduce_xor(reader.row, basis)
        require(all_clock[source] == [direction] and residue and direction not in
                before_readers[source][direction - 1], f"reader indispensability at {source}")
        mandatory[source, direction] = reader.label

    expected_sources = {p.source for p in packets} | {source for source, _ in mandatory}
    require(set(sources) == expected_sources, f"geometry enumeration at {receiver}")
    stock_matches = []
    for first, second in combinations_with_replacement(sources, 2):
        for a_dir, b_dir in independent_choices(all_clock[first], all_clock[second]):
            assignment = ((first, a_dir), (second, b_dir))
            forced = [mandatory[port] for port in assignment if port in mandatory]
            require(forced, f"uncertified stock-only assignment at {receiver}")
            delivered, released = causal_closure(assignment, readers, stock, plane)
            require(delivered < 2 and len(released) < 2, f"causally feasible assignment at {receiver}")
            stock_matches.append({"assignment": assignment, "mandatory_readers": forced,
                                  "rooted_deliveries": delivered, "rooted_readers": released})
    require(len(stock_matches) == 3, f"stock-only roster at {receiver}")
    return {
        "receiver": receiver,
        "original_ingresses": [[p.arrival.label, p.source, p.arrival.time] for p in packets],
        "readers": [[r.label, tape.packets[r.label].receiver, r.time] for r in readers],
        "fixed_clock_directions": fixed_options,
        "fixed_port_cases": fixed_cases,
        "all_clock_directions": all_clock,
        "directions_strictly_before_each_reader": before_readers,
        "stock_matches": stock_matches,
    }


def polynomial_shift(poly, factor):
    return {
        (term[0] ^ factor[0],) + tuple(a + b for a, b in zip(term[1:], factor[1:])): row
        for term, row in poly.items()
    }


def polynomial_xor(left, right):
    result = left.copy()
    for term, row in right.items():
        combined = result.get(term, 0) ^ row
        if combined:
            result[term] = combined
        else:
            result.pop(term, None)
    return result


def caller_monomial(stages, query=False):
    return (int(query),) + tuple(int(i in stages) for i in range(1, 19))


def caller_operator(caller, reverse):
    """Use exact stage exponent tuples and the involution q^2 = 1."""
    n = caller["roles"]
    rows = [{(0,) * 19: 1 << i} for i in range(n)]
    query = caller_monomial((), True)
    events = reversed(caller["events"]) if reverse else caller["events"]
    for op, *args in events:
        if op in ("ADD", "QUERY"):
            dst, src = args[::-1] if reverse else args
            term = polynomial_shift(rows[src], query) if op == "QUERY" else rows[src]
            rows[dst] = polynomial_xor(rows[dst], term)
        elif op == "SWAP":
            a, b = args
            rows[a], rows[b] = rows[b], rows[a]
        elif op == "LOCAL":
            stage, src, dst = args
            if reverse:
                src, dst = dst, src
            factor = caller_monomial((stage,))
            rows[dst] = polynomial_shift(polynomial_xor(rows[dst], polynomial_shift(rows[src], query)), factor)
            rows[src] = polynomial_shift(rows[src], factor)
        elif op == "IDLE_ONE":
            role, stages = args
            rows[role] = polynomial_shift(rows[role], caller_monomial(stages))
        else:
            raise ValueError(f"unexpected caller event {op}")
    return rows


def binary_invoice(word, caller, atlas, tape):
    roles, ports, stages = (caller[k] for k in ("roles", "ports", "stages"))
    require((roles, ports, stages, caller["native_per_stage"], caller["body_rank"], caller["ambient_rank"])
            == (38, 111, 18, 2, 7, 127), "paired caller dimensions")
    stage_order, touched = [], defaultdict(set)
    stage_ids = set(range(1, 19))
    native_paid = Counter(packet.grade for packet in tape.packets.values())
    native_targets = Counter(atlas.grade(a, b) for a, b in zip(word["start"][222:], word["final"][222:]))
    require(0 not in native_targets and sum(native_targets.values()) == 458, "helper target geometry")
    paid, targets = Counter(), Counter()
    for op, *args in caller["events"]:
        if op == "LOCAL":
            stage, a, b = args
            require(0 <= a < roles and 0 <= b < roles and a != b and stage in stage_ids
                    and not (touched[stage] & {a, b}), "disjoint local calls at each stage")
            touched[stage].update((a, b))
            stage_order.append(stage)
            paid.update(native_paid)
            targets.update(native_targets)
        elif op == "IDLE_ONE":
            a, mask = args
            require(0 <= a < roles and mask and len(set(mask)) == len(mask)
                    and set(mask) <= stage_ids, "charged caller idle mask")
            paid[7 * len(mask)] += ports
        else:
            a, b = args
            require(op in ("ADD", "SWAP", "QUERY") and 0 <= a < roles and 0 <= b < roles
                    and a != b, "caller operation")
            if op == "QUERY":
                paid[1] += ports
    require(stage_order == [stage for stage in range(1, 19) for _ in range(2)], "36 actual local calls")
    roots = []
    require(len(caller["diagonal"]) == roles, "caller public diagonal length")
    for i, entry in enumerate(caller["diagonal"]):
        mask = entry["stages"]
        require(entry["q"] == 1 and mask and len(set(mask)) == len(mask)
                and set(mask) <= stage_ids, "root productive mask")
        roots.append({caller_monomial(mask, True): 1 << i})
        targets[1 + 7 * len(mask)] += ports
    require(caller_operator(caller, False) == roots == caller_operator(caller, True),
            "all paired caller polynomial coefficients")
    require(sum(targets.values()) == 36 * 458 + ports * roles, "complete productive invoice")
    return native_paid, native_targets, paid, targets


def ordinary_boundary(word, caller, paid, targets):
    """Count the incumbent under the source's raw tape and routing allowance model."""
    events = Counter(event[0] for event in caller["events"])
    calls, queries, idles = (events[k] for k in ("LOCAL", "QUERY", "IDLE_ONE"))
    ports, roles = caller["ports"], caller["roles"]
    owned, public, scratch = word["owned_fields"], word["public"], 4
    native_records = calls * 16 * (owned + public + scratch) * len(word["program"])
    caller_records = ports * (8 * (events["ADD"] + 3 * events["SWAP"]) + 256 * (calls + queries + roles))
    route_groups = 4 * (sum(paid.values()) + sum(targets.values())) + 8 * ports * (calls + idles)
    route_records = route_groups * 80 * 134 * 135
    records = native_records + caller_records + route_records
    fields = calls * (owned + scratch) + 2 * ports * roles * len(caller["events"])
    fields += 16 * ports * (calls + queries + roles)
    require(records == 934_182_831_504 < 10**12 and fields == 6_998_544 < 10**7,
            "incumbent ordinary record and field census")
    return {"native_calls": calls, "caller_events": dict(events), "raw_records": records,
            "raw_records_limit": 10**12, "owned_fields": fields, "owned_fields_limit": 10**7}


def logarithm_unit(value):
    """Bound log(value) for 1 <= value <= 2 by a rational series and geometric tail."""
    z = (value - 1) / (value + 1)
    square = z * z
    partial, power = Fraction(0), z
    for n in range(64):
        partial += 2 * power / (2 * n + 1)
        power *= square
    return partial, partial + 2 * power / (129 * (1 - square))


def alternating_exponential(x, degree):
    total = term = Fraction(1)
    for n in range(1, degree + 1):
        term *= -x / n
        total += term
    return total


def floor_grid(value, grid):
    return value.numerator * grid // value.denominator


def ceil_grid(value, grid):
    return -floor_grid(-value, grid)


@cache
def price(grade):
    """Enclose grade^(1-kappa) on a 10^-60 rational grid."""
    exponent = grade.bit_length() - 1
    ln2_low, ln2_high = logarithm_unit(Fraction(2))
    scaled_low, scaled_high = logarithm_unit(Fraction(grade, 2**exponent))
    kappa = Fraction(TARGET)
    grid = 10**60
    lo = Fraction(floor_grid(kappa * (exponent * ln2_low + scaled_low), grid), grid)
    hi = Fraction(ceil_grid(kappa * (exponent * ln2_high + scaled_high), grid), grid)
    require(0 <= lo <= hi < 1, "decreasing alternating exponential terms")
    # exp(-x) decreases with x. Odd truncation is below and even truncation above.
    lower = Fraction(floor_grid(grade * alternating_exponential(hi, 33), grid), grid)
    upper = Fraction(ceil_grid(grade * alternating_exponential(lo, 32), grid), grid)
    return lower, upper


def signed_moment(coefficients):
    low = high = Fraction(0)
    for grade, copies in coefficients.items():
        lo, hi = price(grade)
        low += copies * (lo if copies >= 0 else hi)
        high += copies * (hi if copies >= 0 else lo)
    return low, high


def margin(paid, targets):
    coeffs = targets.copy()
    coeffs.subtract(paid)
    return signed_moment(coeffs)


def decimal_bounds(interval, digits=45):
    grid = 10**digits

    def format_fixed(n):
        whole, fraction = divmod(abs(n), grid)
        sign = "-" if n < 0 else ""
        return f"{sign}{whole}.{fraction:0{digits}d}"

    return [format_fixed(floor_grid(interval[0], grid)), format_fixed(ceil_grid(interval[1], grid))]


def deficit(signed):
    return -signed[1], -signed[0]


def prices(paid, targets, application, banks, calls):
    require(application["binary_word"] == WORD and
            application["word_sha256"] == "7660985e0b618cdbee13e4190a4c6d5f91fbdf01a8f7a5186fdde8b980c19b48" and
            application["caller"] == "156fdf3a4a129b39225fd6ca51011de27974d7f104e8b04907c17ed5344bc858" and
            application["layout_sha256"] == "f7de788c4a559282d35a9fce42f841a0e8de5a4015db871e718f9245569b0aa7",
            "comparator finite application identities")
    rational_invoice = application["application"]["invoice"]
    rational_paid, rational_targets = (
        Counter({int(k): n for k, n in rational_invoice[key].items()}) for key in ("paid", "targets")
    )
    binary_margin = margin(paid, targets)
    rational_margin = margin(rational_paid, rational_targets)
    require(3 < -binary_margin[1] < 4 and 9 < -rational_margin[1] < 10,
            "both complete base invoices are short")
    require(Fraction(0) < 1 - Fraction(TARGET) < 1, "increasing positive grade tariff")
    credit = signed_moment({1: 2 * calls, 2: -calls})
    require(credit[0] > 0, "a mixed-grade pair bounds nonpositive credits from three or more sends")

    # Evaluate the optimistic aggregate bill as one signed moment on all jobs.
    revised = paid.copy()
    revised[1] -= 2 * calls * banks
    revised[2] += calls * banks
    best_case = margin(revised, targets)
    require(best_case[1] < 0, "optimistic all-bank residual binary deficit")
    hypothetical = paid.copy()
    hypothetical[1] -= calls
    cheap_once = margin(hypothetical, targets)
    require(cheap_once[0] > 0, "economic significance of one infeasible grade-one pair")
    return {
        "model": "mixed-target-unnormalized-power-v1",
        "kappa": TARGET,
        "binary": {"paid": paid, "targets": targets, "signed_margin": decimal_bounds(binary_margin),
                   "deficit": decimal_bounds(deficit(binary_margin))},
        "rational_48_call_application": {
            "paid": rational_paid, "targets": rational_targets, "signed_margin": decimal_bounds(rational_margin),
            "deficit": decimal_bounds(deficit(rational_margin)),
        },
        "infeasible_single_bank_grade_one_pair_margin": decimal_bounds(cheap_once),
        "optimistic_mixed_grade_credit_per_bank_36_calls": decimal_bounds(credit),
        "optimistic_mixed_grade_credit_all_banks_36_calls": decimal_bounds(tuple(banks * v for v in credit)),
        "optimistic_price_floor_paid_histogram_all_banks": revised,
        "optimistic_binary_margin_at_price_floor": decimal_bounds(best_case),
        "optimistic_binary_deficit_at_price_floor": decimal_bounds(deficit(best_case)),
    }


def controls():
    u, v = 0b011, 0b101
    plane = (u, v, u ^ v)
    readers = [Observation(2, 10, u), Observation(3, 12, v)]
    first = [Observation(0, 0, u), Observation(3, 12, v)]
    second = [Observation(1, 1, v)]
    assignment = ((0, 1), (1, 2))
    require(causal_closure(assignment, readers, {0: first, 1: second}, plane) == (2, [2, 3]),
            "feasible rooted encoding control")
    require(causal_closure(assignment, readers, {0: [readers[0]], 1: second}, plane) == (1, [3]),
            "self-dependent encoding control")
    with_redundancy = [readers[0], Observation(4, 2, 0b001), Observation(5, 3, 0b010)]
    require(causal_closure(assignment, readers, {0: with_redundancy, 1: second}, plane) == (2, [2, 3]),
            "alternative XOR synthesis after removing the literal direct reader")
    require(directions(plane, [o.row for o in with_redundancy if o.time < 3]) == []
            and directions(plane, [o.row for o in with_redundancy if o.time < 4]) == [1],
            "strict deadline membership control")
    require(not independent_choices([3], [3]), "duplicate direction control")
    return ["rooted encoding", "circular reader", "alternative XOR synthesis", "strict deadline", "duplicate direction"]


def replay(word, caller, application):
    require(canonical_hash(word) == WORD, "canonical binary word")
    require(canonical_hash({k: word[k] for k in ("frames", "start", "final")}) == LAYOUT,
            "canonical binary layout")
    require(word["schema"] == "BIT-functional-GL-kernel-native/1"
            and (word["public"], word["owned_fields"]) == (680, 3554), "native tape dimensions")
    atlas = Atlas(word["frames"])
    require(len(atlas.body) == 636, "physical atlas cardinality")
    contacts = atlas.main_contacts(word["start"], word["final"])
    forward, adjoint, bridge_add = native_checks(word, atlas)
    require(len(forward.packets) == len(adjoint.packets) == 2874, "MOVE packet count")
    require({(k, p.source, p.receiver, p.grade, p.clock) for k, p in forward.packets.items()}
            == {(k, p.receiver, p.source, p.grade, p.clock) for k, p in adjoint.packets.items()},
            "adjoint packet directions and charges")
    scanned_forward, no_gaps = find_rank_gaps(forward)
    scanned_adjoint, gaps = find_rank_gaps(adjoint)
    changing = {receiver for receiver, _, _ in gaps}
    require(not no_gaps and changing == set(range(510, 519)), "only nine rank-deficient screened banks")
    banks = [check_bank(receiver, ingress, rank, adjoint, atlas, changing) for receiver, ingress, rank in gaps]
    changed_ingresses = [r[0] for bank in banks for r in bank["original_ingresses"]]
    require(len(set(changed_ingresses)) == len(changed_ingresses) == 27 and BRIDGE_PACKET not in changed_ingresses,
            "disjoint joint bills and independently owned bridge")
    require(not set(changed_ingresses).intersection(r[0] for bank in banks for r in bank["readers"]),
            "protected readers stay fixed when a subset of banks changes")
    native_paid, native_targets, paid, targets = binary_invoice(word, caller, atlas, forward)
    ordinary = ordinary_boundary(word, caller, paid, targets)
    return {
        "status": "target_excluded_in_fixed_observation_native_scalar_contract",
        "sources": {"comparator_head": COMPARATOR, "binary_word_commit": WORD_COMMIT,
                    "binary_word_gzip_sha256": WORD_GZIP, "binary_word_canonical_sha256": WORD,
                    "binary_layout_sha256": LAYOUT, "caller_commit": CALLER_COMMIT,
                    "caller_gzip_sha256": CALLER, "rational_application_sha256": APPLICATION},
        "census": {"public_coefficients_each_orientation": 680**2, "dirty_retirements_each_orientation": 3554,
                   "forward_banks_with_two_or_more_editable_ingresses": scanned_forward,
                   "adjoint_banks_with_two_or_more_editable_ingresses": scanned_adjoint,
                   "frame_labels": len(atlas.body), "main_contacts": contacts,
                   "nested_paid_moves": len(forward.packets), "native_paid": native_paid,
                   "native_targets": native_targets, "caller_role_pairs_each_orientation": 38**2},
        "owner_411": {"packet": BRIDGE_PACKET, "grade": forward.packets[BRIDGE_PACKET].grade,
                      "literal_move_clock": 31290, "adjoint_move_clock": 11667,
                      "omitted_add_clock": bridge_add, "coefficient_changes_each_orientation": 1,
                      "dirty_retirement_omission_rejected_at_literal_clocks":
                      [forward.last_retirement, adjoint.last_retirement]},
        "synthetic_controls": controls(),
        "banks": banks,
        "counts": {"fixed_port_cases": sum(len(bank["fixed_port_cases"]) for bank in banks),
                   "grade_one_pairs_of_distinct_source_charts": 6 * len(banks),
                   "grade_one_source_pair_multisets_including_repetition": 10 * len(banks),
                   "clock_free_stock_matches": sum(len(bank["stock_matches"]) for bank in banks),
                   "reader_removal_span_tests": sum(len(bank["readers"]) for bank in banks),
                   "grade_one_cases_with_causal_encoding": 0},
        "ordinary_binary_incumbent": ordinary,
        "price": prices(paid, targets, application, len(banks), ordinary["native_calls"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", required=True, type=Path, help="pinned #7786 WORD.json.gz")
    parser.add_argument("--caller", required=True, type=Path, help="pinned EFREE-CALLER.json.gz")
    parser.add_argument("--rational-application", required=True, type=Path, help="pinned #7830 DOUBLE-APPLICATION.json")
    args = parser.parse_args()
    word = load_json(args.word, WORD_GZIP, compressed=True)
    caller = load_json(args.caller, CALLER, compressed=True)
    application = load_json(args.rational_application, APPLICATION)
    print(json.dumps(replay(word, caller, application), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
