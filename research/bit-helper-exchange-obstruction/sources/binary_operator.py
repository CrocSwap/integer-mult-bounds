#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Binary operator and caller recount, adapted from the S9 three-ingress replay."""

from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
import gzip
from hashlib import sha256
import json
from typing import NamedTuple


WORD_GZIP = "d28f0d28d9d87d5fe57b8ef19e12faf98014f0bbef781987ce22daaa82f21cb9"
WORD = "d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d"
LAYOUT = "a0ffffd99fb9b91f0013695877480766319ac51b926ed00dd5f7ec32f2d1e1a6"
CALLER = "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b"
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
