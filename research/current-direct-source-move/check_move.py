"""A complete actual source MOVE with an independent original-circuit answer.

Fixture setup/observation is outside the sealed numerical call. The actual
providers receive only physical ports. Prepared for @CubeJerry with
substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hashlib import sha256
import json
import time
from types import SimpleNamespace

from direct_sources import HERE, activate, load, need
from direct_move import DirectMove
from ordinary import Ordinary
from macro_code import Code

S = activate()
HARDWARE = load("direct_move_primitive_hardware", HERE/"vendor/leaf/vendor/atomic/physical_hardware.py")
EVENT = 13096


def factory(capacity=64):
    return Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                    SimpleNamespace(families=0), (Code((("unreachable",),), 0),), capacity=capacity)


def rotate(value, phase):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def binary_map(rows, value):
    return sum(((row & value).bit_count() % 2) << j for j, row in enumerate(rows))


def phase(literal, value):
    return (literal["phase"]+sum(literal["linear_Z4"][j] for j in range(9) if value >> j & 1)
        +2*sum(1 for j in range(9) for k in range(j+1, 9)
               if value >> j & 1 and value >> k & 1 and literal["quadratic_rows"][j] >> k & 1)) % 4


def monomial(values, literal):
    output = [None]*512
    for address, value in enumerate(values):
        image = binary_map(literal["matrix_rows"], address) ^ literal["offset"]
        need(output[image] is None, "independent affine bijection")
        output[image] = rotate(value, phase(literal, address))
    return output


def evaluate(circuit, values):
    """Independent exact Gaussian circuit evaluator, with arbitrary input."""
    values, denominator = list(values), 0
    for gate in circuit:
        kind = gate[0]
        if kind == "P":
            output = [None]*512
            for index, value in enumerate(values):
                image = binary_map(gate[1], index)
                need(output[image] is None, "original circuit permutation")
                output[image] = value
            values = output
        elif kind == "X":
            values = [values[index ^ gate[1]] for index in range(512)]
        elif kind == "D":
            literal = dict(phase=0, linear_Z4=gate[2], quadratic_rows=gate[1])
            values = [rotate(value, phase(literal, index)) for index, value in enumerate(values)]
        elif kind == "phase":
            values = [rotate(value, gate[1]) for value in values]
        elif kind == "C":
            mask, sign = gate[1:]
            need(0 < mask < 512 and sign in (-1, 1), "original normalized signed C")
            output = []
            for index, (a, b) in enumerate(values):
                c, d = values[index ^ mask]
                output.append((a-sign*b+c+sign*d, b+sign*a+d-sign*c))
            values = output; denominator += 1
        else:
            raise ValueError("unrecognized original circuit primitive")
        while denominator and all(a % 2 == b % 2 == 0 for a, b in values):
            values = [(a//2, b//2) for a, b in values]; denominator -= 1
    return values, denominator


def encode_values(values, h=2):
    result = []
    for pair in values:
        for value in pair:
            need(-(1 << (h-1)) <= value < 1 << (h-1), "reference signed range")
            for symbol in [*((value >> j) & 1 for j in range(h)), 2]:
                result += [(symbol >> shift) & 1 for shift in (2, 1, 0)]
    return result


def encode_header(values):
    result = []
    for name in S.common.leaf_provider.SCHEMA:
        value = values[name]
        digits = [(value >> j) & 1 for j in range(max(1, value.bit_length()))]
        result += [1]*len(digits)+[0]+digits
    return result


def fixture(include_boundaries=False):
    triple, original, record = S.catalog.bind_move(S.catalog.catalog()[1][EVENT])
    need(record["rank"] == 1, "fixed bounded actual rank-one MOVE fixture")
    inputs, outputs, entry_answers, middle_answers = [], [], [], []
    for spectator in range(8):
        mask = (spectator & 1) | (((37*spectator+5) & 255) << 1)
        middle = [rotate((1, 0), spectator+2*((mask & y).bit_count() % 2)) for y in range(512)]
        initial = [rotate(middle[binary_map(record["right"]["matrix_rows"], x)
                                 ^ record["right"]["offset"]], -phase(record["right"], x))
                   for x in range(512)]
        need(monomial(initial, record["right"]) == middle, "complete preimage character fixture")
        transformed, half = evaluate([("C", 1, 1)], middle)
        need(half == 0 and all(abs(a) <= 1 and abs(b) <= 1 for a, b in transformed),
             "exact positive half and strict signed two-bit headroom")
        expected, denominator = evaluate(original.circuit, initial)
        need(denominator == 0 and expected == monomial(transformed, record["left"]),
             "independent full original circuit agrees with the actual source factorization")
        need(all(abs(a) <= 1 and abs(b) <= 1 for a, b in expected), "complete strict signed endpoint")
        inputs.append(initial); outputs.append(expected); entry_answers.append(middle); middle_answers.append(transformed)
    initial, expected, entrance, without_exit = [], [], [], []
    for address in range(4096):
        index = sum(((address >> (9-j)) & 1) << j for j in range(9))
        spectator = (address & 1) | (((address >> 10) & 3) << 1)
        initial.append(inputs[spectator][index]); expected.append(outputs[spectator][index])
        entrance.append(entry_answers[spectator][index])
        without_exit.append(middle_answers[spectator][index])
    need(initial != expected and without_exit != expected
         and [rotate(x, 1) for x in expected] != expected,
         "nonidentity complete MOVE, nontrivial exit and absolute phase discriminator")
    header = dict(outer=1, rows=1, stock=1, row_bits=4096*18,
                  within_bits=12, record_bits=18, p=9, d=9, K=1, G=1,
                  H=1, q0=3, qF=0, qB=0, D=9, f=1, rho=0,
                  active_start=2, back_start=11, selected_axes=9,
                  entry_start=2, remainder=0, cutoff=1)
    ordinary = triple, header, encode_values(initial), encode_values(expected)
    if include_boundaries:
        return (*ordinary, dict(entrance=encode_values(entrance),
                               positive_child=encode_values(without_exit),
                               exit=encode_values(expected), commit=encode_values(expected)))
    return ordinary


def put(tape, bits):
    tape.cells[tape.origin:] = bytearray(bits)
    tape.head, tape.high = tape.origin, tape.origin+len(bits)


def body(tape):
    values = tape.cells[tape.origin:]
    end = values.index(6) if 6 in values else len(values)
    need(all(x == 6 for x in values[end:]), "contiguous complete body and blank returned tail")
    return bytes(values[:end])


def run(progress=False, checkpoint=None):
    triple, header, initial, expected, expected_boundaries = fixture(True)
    engine = DirectMove(triple, factory)
    work = [HARDWARE.Tape(3+j % 5) for j in range(engine.port_count)]
    field, context = HARDWARE.Tape(9), HARDWARE.Tape(11)
    tapes = (*work, field, context)
    for tape in tapes:
        for j in range(tape.origin-1):
            tape.cells[j] = j % 2
    header_bits = encode_header(header)
    put(field, initial); put(context, header_bits)
    engine.bind(work, {engine.owner:S.abi.CodedPort(field)}, S.abi.BinaryContextPort(context))
    ancestors = [bytes(t.cells[:t.origin]) for t in tapes]
    total = lambda:sum(t.actions() for t in tapes)
    start_actions = total(); started = time.monotonic(); pieces = []
    initial_regions = sum(t.origin+1 for t in tapes)+len(initial)+len(header_bits)
    observations = []

    def observe_boundary(name):
        """Read-only harness checks; never a provider's numerical callback."""
        observed = time.monotonic(); before_observation = total()
        stage_body = body(work[0]); parent_body = body(context)
        need(stage_body == bytes(expected_boundaries[name]), "independent complete "+name+" stage")
        need(body(field) == bytes(expected if name == "commit" else initial),
             "protected public body at the actual "+name+" return boundary")
        need(parent_body == bytes(header_bits) and all(t.head == t.origin for t in tapes),
             "complete parent and all returned boundary heads")
        need(all(not body(t) for t in work[1:]) and
             all(bytes(t.cells[:t.origin]) == old for t, old in zip(tapes, ancestors)),
             "all completed/future private cohorts blank and ancestors preserved")
        cumulative = total()-start_actions
        record = dict(factor=name, stage_sha256=sha256(stage_body).hexdigest(),
                      parent_sha256=sha256(parent_body).hexdigest(),
                      public_sha256=sha256(body(field)).hexdigest(),
                      cumulative_run_actions=cumulative,
                      private_materialized_extents=[len(t.cells)-t.origin for t in work],
                      conservative_all_visited_cells=initial_regions+cumulative,
                      byte_validated_complete_boundary=True,
                      prior_cohorts_retained_in_space=True,
                      all_heads_at_origins=True, other_private_bodies_blank=True,
                      logging_is_read_only_harness=True)
        if checkpoint is not None:
            checkpoint.mkdir(parents=True, exist_ok=True)
            (checkpoint/(name+"-stage.bits")).write_bytes(stage_body)
            (checkpoint/(name+"-parent.bits")).write_bytes(parent_body)
            (checkpoint/(name+"-boundary.json")).write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")
        need(total() == before_observation, "read-only harness adds no claimed model action")
        record["harness_observation_seconds"] = round(time.monotonic()-observed,6)
        observations.append(record)

    def measured(name, method):
        def call(*args, **kwargs):
            before = total(); value = method(*args, **kwargs)
            row = dict(factor=name, physical_actions=total()-before)
            pieces.append(row)
            observe_boundary(name)
            if progress:
                print("RETURNED_FACTOR", json.dumps(dict(**row,elapsed_seconds=round(time.monotonic()-started,3)),sort_keys=True),flush=True)
            return value
        return call

    engine.entry.run = measured("entrance", engine.entry.run)
    engine.child.run = measured("positive_child", engine.child.run)
    engine.exit.run = measured("exit", engine.exit.run)
    engine.commit = measured("commit", engine.commit)
    old = Ordinary.run; ordinary_entries = [0]
    def forbidden(*args, **kwargs):
        ordinary_entries[0] += 1
        raise ValueError("ordinary-runtime-entry-trap")
    Ordinary.run = forbidden
    try:
        engine.run()
    finally:
        Ordinary.run = old
    elapsed = round(time.monotonic()-started, 3)
    need(body(field) == bytes(expected) and body(context) == bytes(header_bits),
         "complete independently predicted original MOVE and preserved parent")
    need(all(t.head == t.origin for t in tapes), "all source/private heads at origins")
    need(all(not body(t) for t in work), "whole stage and every factor cohort retired")
    need(all(bytes(t.cells[:t.origin]) == old for t, old in zip(tapes, ancestors)), "all caller ancestors preserved")
    for side in (engine.entry, engine.exit):
        need(not side.view.active and not side.native.pool.live and side.native.engine.closed
             and not side.native.engine.pool.live and all(v == 0 for v in side.native.engine.compact.calls.values()),
             "serial monomial closed with zero ordinary/Compact runtime entries")
    need(not engine.child.view.active and not engine.child.native.pool.live
         and not engine.child.native.engine.pool.live and ordinary_entries == [0],
         "positive child/header closed and no ordinary numerical runtime call")
    bill = {row["factor"]:row["physical_actions"] for row in pieces}
    actions = total()-start_actions; V = len(initial)
    need(bill["commit"] == 9*V+14 and
         actions == bill["entrance"]+bill["positive_child"]+bill["exit"]+22*V+35,
         "complete actual factors plus exact protected-stage administrative bill")
    return dict(source_event=EVENT, source_owner=engine.owner, source_raw=list(triple[1].token[2]),
                rank=engine.rank, columns=1, records=4096, physical_bits=V,
                header_bits=len(header_bits), private_ports=len(work), physical_actions=actions,
                factor_actions=bill, protected_admin_actions=22*V+35,
                ordinary_runtime_entries=ordinary_entries[0], endpoint_sha256=sha256(body(field)).hexdigest(),
                private_materialized_extents=[len(t.cells)-t.origin for t in work],
                byte_validated_boundaries=[{key:row[key] for key in (
                    "factor", "stage_sha256", "parent_sha256", "public_sha256",
                    "cumulative_run_actions", "conservative_all_visited_cells")}
                    for row in observations],
                harness_observation_seconds=round(sum(row["harness_observation_seconds"] for row in observations),6),
                exact_prefix_admission=True, stronger_input_divisibility_envelope=False,
                long_record_absorption_regime=False, complete_raw_MOVE_executed=True,
                enclosing_selected_caller_claim=False, elapsed_seconds=elapsed)


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(); parser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args()
    print("COMPLETE_DIRECT_MOVE", json.dumps(run(progress=True,checkpoint=args.checkpoint), sort_keys=True), flush=True)
