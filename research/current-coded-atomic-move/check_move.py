"""Full source matrix and complete coded hardware packet checks.

The expected result comes from the original source circuit, never from the
right/C/left lowered recipe. Runtime providers receive no value oracle.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from argparse import ArgumentParser
from dataclasses import replace
from hashlib import sha256
import json
from types import SimpleNamespace

from atomic_move import AtomicMove, S, source_boundary
from move_sources import need
from ordinary import Ordinary
from macro_code import Code
from physical_hardware import Tape as PhysicalTape


def ordinary_factory():
    return Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)), SimpleNamespace(families=0),
                    (Code((("unreachable",),), 0),), capacity=64)


def gauss_mul(z, w):
    a, b = z; c, d = w
    return a*c-b*d, a*d+b*c


def rotate(z, phase):
    return gauss_mul(z, ((1, 0), (0, 1), (-1, 0), (0, -1))[phase % 4])


def source_matrix():
    _triple, _record, original, _report = source_boundary()
    dimension = 1 << original.n
    columns = []
    for basis in range(dimension):
        vector = [(0, 0)]*dimension
        vector[basis] = (1, 0)
        denominator = 0
        for gate in original.circuit:
            kind = gate[0]
            if kind == "P":
                result = [(0, 0)]*dimension
                for address, value in enumerate(vector):
                    image = sum(((row & address).bit_count() % 2) << j
                                for j, row in enumerate(gate[1]))
                    result[image] = value
                vector = result
            elif kind == "X":
                vector = [vector[address ^ gate[1]] for address in range(dimension)]
            elif kind == "D":
                quadratic, linear = gate[1:]
                result = []
                for address, value in enumerate(vector):
                    occupied = [j for j in range(original.n) if address >> j & 1]
                    exponent = sum(linear[j] for j in occupied)
                    exponent += 2*sum((quadratic[j] >> k) & 1
                                      for j in occupied for k in occupied if j < k)
                    result.append(rotate(value, exponent))
                vector = result
            elif kind == "phase":
                vector = [rotate(value, gate[1]) for value in vector]
            elif kind == "C":
                mask, sign = gate[1:]
                result = []
                for address, value in enumerate(vector):
                    first = gauss_mul((1, sign), value)
                    second = gauss_mul((1, -sign), vector[address ^ mask])
                    result.append((first[0]+second[0], first[1]+second[1]))
                vector = result; denominator += 1
            else:
                raise ValueError("unexpected original source gate " + kind)
        while denominator and all(a % 2 == b % 2 == 0 for a, b in vector):
            vector = [(a//2, b//2) for a, b in vector]; denominator -= 1
        # Independent evaluator agrees with the authenticated canonical source
        # on every matrix coefficient, including its absolute normalization.
        need((vector, denominator) == original.zero_state(basis), "complete original source column")
        columns.append((tuple((row, value) for row, value in enumerate(vector) if value != (0, 0)), denominator))
    need(len(columns) == 512 and all(len(column) == 2 and den == 1 for column, den in columns),
         "whole rank-nine source matrix with its exact half denominator")
    digest = sha256(json.dumps(columns, separators=(",", ":")).encode()).hexdigest()
    return columns, dict(columns=512, coefficient_positions=512*512,
                         nonzero_entries=sum(len(c) for c, _d in columns), matrix_sha256=digest)


def factorization_check(columns):
    """Compare literal lowerings against the independently evaluated full U."""
    record = source_boundary()[1]

    def apply_monomial(index, value, literal, extra_phase=0):
        phase = literal["phase"]+extra_phase
        phase += sum(literal["linear_Z4"][j] for j in range(9) if index >> j & 1)
        phase += 2*sum(1 for j in range(9) for k in range(j+1, 9)
                       if index >> j & 1 and index >> k & 1 and literal["quadratic_rows"][j] >> k & 1)
        image = literal["offset"] ^ sum(((row & index).bit_count() % 2) << j
                                        for j, row in enumerate(literal["matrix_rows"]))
        return image, rotate(value, phase)

    def column(index, phase=0, sign=1, mask=1, omit_exit=False):
        image, coefficient = apply_monomial(index, (1, 0), record["right"], phase)
        result = {}
        for row, multiplier in ((image, (1, sign)), (image ^ mask, (1, -sign))):
            value = gauss_mul(coefficient, multiplier)
            if not omit_exit:
                row, value = apply_monomial(row, value, record["left"])
            need(row not in result, "distinct complete source output positions")
            result[row] = value
        return tuple(sorted(result.items())), 1

    need(all(column(j) == wanted for j, wanted in enumerate(columns)),
         "all 512 complete source columns equal right/positive-C/left including absolute phase")
    faults = dict(wrong_entrance_phase=dict(phase=1), wrong_C_direction=dict(sign=-1),
                  wrong_C_axis=dict(mask=2), omitted_exit=dict(omit_exit=True))
    mismatches = {name: sum(column(j, **change) != wanted for j, wanted in enumerate(columns))
                  for name, change in faults.items()}
    need(all(count > 0 for count in mismatches.values()), "full original matrix detects each source factorization fault")
    return dict(columns=512, coefficient_positions=512*512,
                exact_absolute_phase_factorization=True, fault_column_mismatches=mismatches)


def header_bits(values):
    result = []
    for name in S.monomial.SCHEMA:
        digits = [int(x) for x in bin(values[name])[2:][::-1]]
        result += [1]*len(digits) + [0] + digits
    return result


def encode(values, width):
    bits = []
    for real, imag in values:
        for component in (real, imag):
            need(-(1 << (width-1)) <= component < (1 << (width-1)), "oracle signed field range")
            symbols = [(component >> bit) & 1 for bit in range(width)] + [2]
            for symbol in symbols:
                bits.extend((symbol >> shift) & 1 for shift in (2, 1, 0))
    return bits


def active_positions(header):
    return [header["within_bits"]-1-(header["active_start"]+j*header["f"]*header["K"]+header["rho"])
            for j in range(9)]


def replace_column(address, column, positions):
    for j, bit in enumerate(positions):
        address = (address & ~(1 << bit)) | (((column >> j) & 1) << bit)
    return address


def right_destination(address, header):
    literal = source_boundary()[1]["right"]
    positions = active_positions(header)
    column = sum(((address >> bit) & 1) << j for j, bit in enumerate(positions))
    image = literal["offset"] ^ sum(((row & column).bit_count() % 2) << j
                                    for j, row in enumerate(literal["matrix_rows"]))
    return replace_column(address, image, positions)


def fixture(columns, bad=False):
    # Complete rank-nine source and all three reservation spectators. The
    # reduced H=G=K=1 descriptor belongs to the local adapter domain; it is not
    # the enormous enclosing producer's H=dG, K=128G allocation.
    a, width, record_bits = 12, 2, 18
    header = dict(outer=1, rows=1, stock=1, row_bits=(1 << a)*record_bits, within_bits=a,
                  record_bits=record_bits, p=9, d=9, K=1, G=1, H=1, q0=3, qF=0, qB=0,
                  D=9, f=1, rho=0, active_start=2, back_start=11, selected_axes=9,
                  entry_start=2, remainder=0, cutoff=9)
    initial = [rotate((1, 0), ((j*7) ^ (j >> 2) ^ (j >> 7)).bit_count()) for j in range(1 << a)]
    rejected_index = None
    if bad:
        target = (1 << a)-1
        candidates = [j for j in range(1 << a) if right_destination(j, header) == target]
        need(len(candidates) == 1, "unique late positive-child input address")
        rejected_index = candidates[0]
        initial[rejected_index] = (0, 0)
    positions = active_positions(header)
    expected = [[0, 0] for _ in initial]
    for address, value in enumerate(initial):
        column = sum(((address >> bit) & 1) << j for j, bit in enumerate(positions))
        rows, denominator = columns[column]
        need(denominator == 1, "source exact denominator")
        for destination, coefficient in rows:
            image = replace_column(address, destination, positions)
            product = gauss_mul(coefficient, value)
            expected[image][0] += product[0]; expected[image][1] += product[1]
    if not bad:
        need(all(a % 2 == b % 2 == 0 for a, b in expected), "common-grid exact full-source result")
        expected = [(a//2, b//2) for a, b in expected]
        need(encode(initial, width) != encode(expected, width), "nontrivial complete MOVE witness")
    return header, encode(initial, width), None if bad else encode(expected, width), rejected_index


def body(tape):
    values = tape.cells[tape.origin:]
    try:
        stop = values.index(6)
    except ValueError:
        stop = len(values)
    need(all(x == 6 for x in values[stop:]), "no hidden nonblank tail")
    return list(values[:stop])


def put(tape, bits):
    tape.cells[tape.origin:] = bytearray(bits)
    tape.head, tape.high = tape.origin, tape.origin + len(bits)


def hardware():
    engine = AtomicMove(source_boundary()[0], ordinary_factory)
    tapes = [PhysicalTape(3+j % 5) for j in range(engine.port_count)]
    field, context = PhysicalTape(9), PhysicalTape(11)
    for tape in (*tapes, field, context):
        for j in range(tape.origin-1):
            tape.cells[j] = j % 2
    engine.bind(tapes, {236: S.abi.CodedPort(field)}, S.abi.BinaryContextPort(context))
    return engine, tapes, field, context


def packet(columns, bad=False, reuse=None):
    engine, work, field, context = hardware() if reuse is None else reuse
    header, initial, expected, bad_index = fixture(columns, bad)
    encoded_header = header_bits(header)
    put(field, initial); put(context, encoded_header)
    all_tapes = (*work, field, context)
    ancestors = [bytes(t.cells[:t.origin]) for t in all_tapes]
    before = sum(t.actions() for t in all_tapes)
    enters = engine.entry.calls
    leaves = engine.exit.calls
    error = None
    try:
        engine.run()
    except S.leaf.linear.CoefficientDomainError as caught:
        error = str(caught)
    need(error == ("inexact Gaussian halving" if bad else None), "expected actual late-child outcome")
    need(engine.entry.calls == enters+1, "right monomial fully returned before child")
    need(engine.exit.calls == leaves+(0 if bad else 1), "chronological exit invocation")
    need(body(field) == (initial if bad else expected), "complete original-circuit endpoint or whole-MOVE rollback")
    need(body(context) == encoded_header, "all source descriptor bytes restored")
    need(all(t.head == t.origin for t in all_tapes), "all public/private heads returned")
    need(all(all(x == 6 for x in t.cells[t.origin:]) for t in work), "all historical private bodies blank")
    need(all(bytes(t.cells[:t.origin]) == old for t, old in zip(all_tapes, ancestors)), "caller ancestor bytes intact")
    result = dict(records=1 << header["within_bits"], physical_bits=len(initial), signed_component_bits=2,
                  descriptor=header, bad_initial_index=bad_index, rejection=error,
                  physical_actions=sum(t.actions() for t in all_tapes)-before,
                  fixed_private_ports=engine.port_count,
                  retained_private_cells=sum(len(t.cells) for t in work),
                  endpoint_sha256=sha256(bytes(body(field))).hexdigest(),
                  stage_blank=True, original_preserved_on_rejection=bool(bad))
    return result, (engine, work, field, context)


def controls(columns):
    triple = source_boundary()[0]
    changes = [(triple[2], triple[1], triple[0]),
               (triple[0], replace(triple[1], rank=2), triple[2]),
               (triple[0], replace(triple[1], rank=True), triple[2]),
               (replace(triple[0], fields=(237,)), triple[1], triple[2]),
               (replace(triple[0], token=("outer", triple[0].token)), triple[1], triple[2])]
    for wrong in changes:
        try:
            AtomicMove(wrong, ordinary_factory)
        except ValueError:
            pass
        else:
            raise ValueError("wrong source triple accepted")
    engine, work, field, context = hardware()
    aliases = [([work[0]]*len(work), {236: S.abi.CodedPort(field)}, S.abi.BinaryContextPort(context)),
               (work, {236: S.abi.CodedPort(field)}, S.abi.BinaryContextPort(field)),
               (work, {236: S.abi.CodedPort(work[0])}, S.abi.BinaryContextPort(context))]
    for args in aliases:
        try:
            engine.bind(*args)
        except ValueError:
            pass
        else:
            raise ValueError("obvious ownership alias accepted")
    need(any(rotate(value, 1) != value for rows, _den in columns for _row, value in rows),
         "absolute phase discriminator")
    return dict(source_rejections=len(changes), alias_rejections=len(aliases), absolute_phase_discriminated=True)


def main():
    parser = ArgumentParser()
    parser.add_argument("mode", choices=("source", "packet", "failure", "all"))
    args = parser.parse_args()
    columns, matrix = source_matrix()
    result = dict(source=source_boundary()[3], matrix=matrix, controls=controls(columns))
    if args.mode == "packet":
        result["packet"] = packet(columns)[0]
    elif args.mode == "failure":
        result["failure"] = packet(columns, bad=True)[0]
    elif args.mode == "all":
        result["failure"], state = packet(columns, bad=True)
        result["valid_retry"] = packet(columns, reuse=state)[0]
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
