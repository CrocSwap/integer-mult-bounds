"""Complete finite packets and independent direct endpoint specifications."""
from array import array
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from math import prod
import sys
import time

from algebra import Header, eye, gl2, good, lifts, need, projection
from control import Program
from engine import ChildRequest, Engine
from streams import Shape, Tape


def token(index):
    return ((index * 2654435761) & 0xffffffff) ^ 0xa5c39e71


def digest(records):
    data = array("I", records)
    need(data.itemsize == 4, "32-bit opaque record format")
    if sys.byteorder != "little":
        data.byteswap()
    return sha256(data.tobytes()).hexdigest()


def old_context():
    matrix = eye(64)
    matrix[0][4] = matrix[4][0] = 1
    matrix[4][4] = 2
    header = Header(3, 1, tuple(map(tuple, matrix)), tuple(range(4)))
    program = Program(3, 1, 64).child("good", header)
    need(good(header).pivots == (2, 1, 1, 1), "actual64 preparation for incoming nonuniform weights")
    return program, (header,), (2, 1, 1, 1)


def direct_projector(header):
    """Closed 2x2 adjugate formula, independent of the preparation's elimination."""
    (a, b), (c, d) = header.matrix
    B = header.modulus
    inverse = pow(a * d - b * c, -1, B)
    p = ((a * d * inverse % B, -a * b * inverse % B),
         (c * d * inverse % B, -c * b * inverse % B))
    if header.axes == (1,):
        p = tuple(tuple((int(i == j) - p[i][j]) % B for j in range(2)) for i in range(2))
    return p


def body_map(shape, weights, header=None):
    """Direct F_A or R_A(P); only the checker performs address indexing."""
    n, B, radices = shape.atoms, shape.modulus, shape.radices
    inverse = [pow(a, -1, B) for a in weights]
    p = direct_projector(header) if header is not None else None
    out = []
    for coordinates in product(*(range(r) for r in radices)):
        head, tail = list(coordinates[:n]), list(coordinates[n + 1:])
        new_head, new_tail = head[:], tail[:]
        if p is None:
            for i in range(n):
                new_head[i] = weights[i] * tail[n - 1 - i] % B
                new_tail[n - 1 - i] = inverse[i] * head[i] % B
        else:
            f = n // 2
            for j in range(f):
                difference = [(tail[n - 1 - (k * f + j)] - inverse[k * f + j] * head[k * f + j]) % B
                              for k in range(2)]
                transformed = [sum(p[i][k] * difference[k] for k in range(2)) % B for i in range(2)]
                for i, change in enumerate(transformed):
                    position = i * f + j
                    new_head[position] = (head[position] + weights[position] * change) % B
                    new_tail[n - 1 - position] = (tail[n - 1 - position] - change) % B
        target = 0
        for value, radix in zip(new_head + [coordinates[n]] + new_tail, radices):
            target = target * radix + value
        out.append(target)
    need(sorted(out) == list(range(len(out))) and all(out[out[i]] == i for i in range(len(out))),
         "direct residual/weighted endpoint is an involution")
    return out


def mismatch(tape, headers, shape, weights, residual=False):
    rows = prod(shape.radices)
    common = None if residual else body_map(shape, weights)
    for parent, header in enumerate(headers):
        mapping = body_map(shape, weights, header) if residual else common
        for stock in range(shape.unused):
            base = (parent * shape.unused + stock) * rows * shape.suffix
            for row, original in enumerate(mapping):
                for suffix in range(shape.suffix):
                    address = base + row * shape.suffix + suffix
                    expected = token(base + original * shape.suffix + suffix)
                    if tape.records[address] != expected:
                        return [address, int(tape.records[address]), expected]
    return None


def configuration(name):
    if name in ("high_good", "high_bad"):
        low = ((1, 1), (1, 2 if name == "high_good" else 0))
        headers = tuple(lifts(low, 3, 2))
        return headers, ((),) * 81, Shape(2, 9), Program(3, 2, 2, 2), (2, 2), 1, False
    program, history, weights = old_context()
    if name == "nested_unit":
        headers = (Header(3, 1, ((1, 1), (1, 0)), (0,)),)
        return headers, (history,), Shape(4, 3, 48), program, weights, 2, True
    need(name == "wide_leaf", "known finite case")
    headers = (Header(3, 1, ((1, 1), (1, 2)), (0,)),)
    return headers, (history,), Shape(4, 3, 2, 2, 3), program, weights, 2, False


def run_case(name, progress=False):
    started = time.perf_counter()
    if progress:
        print("START " + name, file=sys.stderr, flush=True)
    headers, histories, shape, program, weights, cutoff, recurse = configuration(name)
    B = shape.modulus
    for header in headers:
        need(projection(header) == direct_projector(header), "full-ring prepared projector vs adjugate")
    engine = Engine(cutoff, recurse_one_unit=recurse)
    volume = len(histories) * shape.records
    need(volume < 1 << 32, "unique opaque input labels")
    sentinel = [0xdeadbeef, 0, 1, 0xffffffff]
    outer = engine.parking.push(Tape(engine.meter, sentinel))
    checkpoints = []
    def observe(axis, tape):
        need(mismatch(tape, headers, shape, weights, residual=axis == 0) is None,
             "complete direct endpoint after residual " + str(axis))
        checkpoints.append(digest(tape.records))
    result = engine.node_packet(Tape(engine.meter, (token(i) for i in range(volume))),
                                histories, headers, shape, program, observe)
    need(result.head == 0 and len(result.records) == volume, "complete caller return boundary")
    restored = engine.parking.pop(outer)
    need(list(restored.records) == sentinel and restored.head == 0 and engine.parking.closed(),
         "buried caller payload and stack restoration")
    need(len(engine.calls) == engine.meter["completed_leaves"] + engine.meter["fresh_stock_calls"],
         "each child has a completed leaf or real internal implementation")
    leaf_atoms = sum(call[1] for call in engine.calls) - (2 if recurse else 0)
    need(engine.meter["digit_swaps"] == 4 * program.width * leaf_atoms,
         "literal completed-leaf digit-exchange inventory")
    if name.startswith("high_"):
        need(len(headers) == 3**4 and all(call[2:4] == (81, volume) for call in engine.calls),
             "one entire81-lift packet per child")
    if recurse:
        need(engine.meter["unit_reset_internal_calls"] == engine.meter["fresh_stock_calls"] == 1
             and engine.meter["fresh_low_packets"] == 48 and engine.meter["parking_max_depth"] == 2,
             "real unit-reset descendant and fresh-stock layer")
        need(max(call[4] for call in engine.calls) == 3 and engine.control["max_frozen_slot"] == 2,
             "actual full-ring fields retain global age after reset")
    profile = Counter((call[0], call[1], call[2], call[3], call[4], call[5]) for call in engine.calls)
    current_values = Counter(str(direct_projector(h)[0][0]) for h in headers)
    report = {"q": program.q, "width": program.width, "atoms": shape.atoms,
              "current_high_headers": len(headers), "unused_rows": shape.unused,
              "gap": shape.gap, "suffix_records": shape.suffix, "payload_bits_per_record": 32,
              "records": volume, "current_P00_histogram": dict(current_values),
              "incoming_weights": list(weights), "older_field_dimensions": [h.dimension for h in histories[0]],
              "completed_child_calls": len(engine.calls), "completed_node_packets": engine.node_calls,
              "residual_branches": dict(engine.residuals), "child_profile": [list(key) + [count] for key, count in sorted(profile.items())],
              "child_trace_sha256": sha256(json.dumps(engine.calls, separators=(",", ":")).encode()).hexdigest(),
              "residual_and_final_sha256": checkpoints, "payload_work": engine.meter.summary(),
              "control_work": dict(engine.control), "parking_empty": engine.parking.closed()}
    if progress:
        print("PASS " + name + " seconds=" + format(time.perf_counter() - started, ".3f"),
              file=sys.stderr, flush=True)
    return report


def rejection_controls():
    controls = {}
    header = tuple(lifts(((1, 1), (1, 2)), 3, 2))[1]
    shape, program = Shape(2, 9), Program(3, 2, 2, 2)
    engine = Engine(fault="low_only_generated_header")
    observed = []
    engine.node_packet(Tape(engine.meter, (token(i) for i in range(shape.records))),
                       ((),), (header,), shape, program,
                       lambda axis, tape: observed.append(mismatch(tape, (header,), shape, (2, 2), axis == 0)))
    need(observed[0] is not None, "low-only generated preparation must fail")
    controls["low_only_full_ring_field"] = observed[0]

    program, history, weights = old_context()
    header = Header(3, 1, ((1, 1), (1, 0)), (0,))
    shape = Shape(4, 3)
    engine = Engine(2, fault="omit_reversal")
    observed = []
    engine.node_packet(Tape(engine.meter, (token(i) for i in range(shape.records))),
                       (history,), (header,), shape, program,
                       lambda axis, tape: observed.append(mismatch(tape, (header,), shape, weights, axis == 0)))
    need(engine.skipped_reversal and observed[0] is not None, "orientation child omission must fail")
    controls["omitted_orientation_child"] = observed[0]

    unit = program.child("unit", header, size=2)
    engine = Engine(1, fault="compact_history_after_reset")
    shape = Shape(2, 3, 48)
    try:
        engine.caller(Tape(engine.meter, (token(i) for i in range(shape.records))),
                      (history + (header,),), shape, unit)
    except ValueError as error:
        need(str(error) == "child global field scope" and engine.parking.closed(), "reset rejection and parking cleanup")
        controls["compacted_global_slots_after_unit"] = str(error)
    else:
        raise ValueError("unit reset lost old field coordinates without rejection")

    parent = Program(3, 2, 2, 2)
    h = tuple(lifts(((1, 1), (1, 2)), 3, 2))[0]
    child = parent.child("good", h)
    shape = Shape(2, 9).child(0, 3, 1)
    request = ChildRequest(shape, child, 81, 81 * shape.records, 2, "complete high packet")
    engine = Engine()
    try:
        request.admit(Tape(engine.meter, range(shape.records)), ((h,),))
    except ValueError as error:
        controls["split_high_packet_admission"] = str(error)
    else:
        raise ValueError("a separately sliced child satisfied the whole-packet request")

    engine, shape = Engine(), Shape(2, 3, 47)
    source = Tape(engine.meter, range(shape.records))
    try:
        engine.caller(source, ((),), shape, Program(3, 1, 2))
    except ValueError as error:
        need(str(error) == "fresh complete GL2 stock" and source.head == 0, "fresh-row admission")
        controls["insufficient_fresh_rows"] = str(error)
    else:
        raise ValueError("incomplete GL2 stock admitted")
    try:
        Shape(4, 3).child(3, 5, 2)
    except ValueError as error:
        controls["chunk_crosses_old_gap"] = str(error)
    else:
        raise ValueError("child chunk crossed the old gap")
    return controls


def run(progress=False):
    need(len(gl2(3)) == 48, "complete GL2 low classes")
    return {"cases": {name: run_case(name, progress) for name in
                      ("high_good", "high_bad", "nested_unit", "wide_leaf")},
            "rejection_controls": rejection_controls(),
            "scope": "Complete stated generic packets with real completed children; not the selected GL64 owner/hosting execution, a binary transition-table compiler or a new saving."}
