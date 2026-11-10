"""Complete current-format physical packets and an independent address oracle.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Fixture construction and observation may inspect arrays; the sealed call cannot.
"""
from argparse import ArgumentParser
import json
from types import SimpleNamespace
from phase_adapter import Provider, SCHEMA, S
from phase_binding import need
from codec import DenseTape
from ordinary import Ordinary
from macro_code import Code


def factory():
    return Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)), SimpleNamespace(families=0),
                    (Code((("unreachable",),), 0),), capacity=64)


def literal(affine=True):
    return dict(matrix_rows=(1, 3) if affine else (1, 2), offset=0,
                linear_Z4=(1, 2), quadratic_rows=(2, 0), phase=1)


def coded(symbols):
    return [((value >> shift) & 1) for value in symbols for shift in (2, 1, 0)]


def header_bits(values):
    result = []
    for name in SCHEMA:
        digits = [int(bit) for bit in bin(values[name])[2:][::-1]]
        result.extend([1] * len(digits) + [0] + digits)
    return result


def load(tape, body):
    tape.cells[tape.origin:] = bytearray(body)
    tape.head, tape.high = tape.origin, tape.origin + len(body)


def body(tape):
    out = []
    for value in tape.cells[tape.origin:]:
        if value == 6:
            break
        out.append(value)
    return out


def rotate(pair, phase):
    a, b = pair
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def endpoint(address, values, recipe):
    f, K, rho, rank = values["f"], values["K"], values["rho"], len(recipe["matrix_rows"])
    bits, start = values["within_bits"], values["active_start"]
    phase, destination = f * recipe["phase"], address
    for j in range(f):
        positions = [bits - 1 - (start + (i * f + j) * K + rho) for i in range(rank)]
        column = sum(((address >> position) & 1) << i for i, position in enumerate(positions))
        phase += sum(recipe["linear_Z4"][i] for i in range(rank) if column >> i & 1)
        phase += 2 * sum(1 for i in range(rank) for k in range(i + 1, rank)
                         if column >> i & 1 and column >> k & 1 and recipe["quadratic_rows"][i] >> k & 1)
        result = recipe["offset"] ^ sum(((row & column).bit_count() % 2) << i
                                         for i, row in enumerate(recipe["matrix_rows"]))
        for i, position in enumerate(positions):
            if ((column ^ result) >> i) & 1:
                destination ^= 1 << position
    return destination, phase % 4


def encode(records, h):
    out = []
    for record in records:
        for pair in record:
            for value in pair:
                need(-(1 << (h - 1)) <= value < 1 << (h - 1), "checker signed component range")
                out.extend(coded([(value >> bit) & 1 for bit in range(h)] + [2]))
    return out


def fixture(recipe, *, f=1, K=1, rho=0, H=1, rows=1, outer=1, h=4, coefficients=2,
            inverse=False, bad_field=False):
    rank = len(recipe["matrix_rows"])
    e, a = rank * f, 3 * H + rank * f * K
    b = 6 * coefficients * (h + 1)
    values = dict(outer=outer, rows=rows, stock=1, row_bits=(1 << a) * b, within_bits=a,
        record_bits=b, p=max(e, 2), d=e, K=K, G=1, H=H, q0=3, qF=0, qB=0, D=e,
        f=f, rho=rho, active_start=2 * H, back_start=2 * H + e * K,
        selected_axes=e, entry_start=2 * H, remainder=0, cutoff=rank)
    total = outer * rows * (1 << a)
    maximum = (1 << (h - 1)) - 1
    modulus = 2 * maximum + 1
    records = [tuple(((i + 3 * c) % modulus - maximum,
                      (i // modulus + 5 * c) % modulus - maximum)
                     for c in range(coefficients)) for i in range(total)]
    expected = [None] * total
    for row in range(outer * rows):
        for address in range(1 << a):
            destination, phase = endpoint(address, values, recipe)
            source_index, target_index = ((row * (1 << a) + destination, row * (1 << a) + address)
                                          if inverse else
                                         (row * (1 << a) + address, row * (1 << a) + destination))
            expected[target_index] = tuple(rotate(pair, -phase if inverse else phase)
                                           for pair in records[source_index])
    if bad_field:
        need(not inverse, "this guard fixture uses the forward phase boundary")
        bad = max(i for i in range(total) if endpoint(i % (1 << a), values, recipe)[1] == 1)
        record = list(records[bad])
        record[-1] = (record[-1][0], -(1 << (h - 1)))
        records[bad] = tuple(record)
    return values, encode(records, h), encode(expected, h)


def run_case(*, reuse=None, return_state=False, affine=True, guard=False, **case):
    recipe = literal(affine)
    values, initial, expected = fixture(recipe, bad_field=guard, **case)
    if reuse is None:
        owner = Provider(recipe, factory, case.get("inverse", False))
        work = [DenseTape(3 + i % 5) for i in range(owner.port_count)]
        field, context = DenseTape(9), DenseTape(11)
        for tape in (*work, field, context):
            for i in range(tape.origin - 1):
                tape.cells[i] = i % 2
        owner.bind(work)
    else:
        owner, work, field, context = reuse
        need(owner.inverse == case.get("inverse", False), "same compiled direction in reused owner")
    load(field, initial)
    encoded_header = header_bits(values)
    load(context, encoded_header)
    ancestors = [bytes(t.cells[:t.origin]) for t in (*work, field, context)]
    before = sum(t.actions() for t in (*work, field, context))
    calls_before = dict(owner.engine.compact.calls)
    rejected = False
    try:
        owner.run(S.abi.CodedPort(field), S.abi.BinaryContextPort(context))
    except S.phase.SignedHeadroomError:
        rejected = True
    need(rejected == guard, "expected phase-specific signed guard outcome")
    need(body(field) == (initial if guard else expected), "independent full signed-record endpoint")
    need(body(context) == encoded_header, "all 23 context fields preserved")
    need(field.head == field.origin and context.head == context.origin, "public and context origin restoration")
    need(all(t.head == t.origin and all(x == 6 for x in t.cells[t.origin:]) for t in work),
         "all native historical bodies physically erased at current origins")
    need(all(bytes(t.cells[:t.origin]) == original for t, original in zip((*work, field, context), ancestors)),
         "ancestor bytes and local physical origins protected")
    need(not owner.pool.live and owner.engine.closed and not owner.engine.pool.live
         and owner.engine.compact.closed, "closed reusable owner and child scopes")
    report = dict(case=case, affine=affine, signed_guard_rejected=rejected,
        records=values["outer"] * values["rows"] * (1 << values["within_bits"]),
        coefficients=case.get("coefficients", 2), physical_bits=len(initial),
        physical_actions=sum(t.actions() for t in (*work, field, context)) - before,
        native_ports=owner.port_count, retained_cells=sum(len(t.cells) for t in work),
        compact_calls={key: value - calls_before[key] for key, value in owner.engine.compact.calls.items()})
    return (report, (owner, work, field, context)) if return_state else report


def main():
    parser = ArgumentParser()
    parser.add_argument("case", choices=("single", "forward", "inverse", "phase", "guard", "reuse"))
    args = parser.parse_args()
    if args.case == "single":
        result = run_case(f=1, K=2, rho=0)
    elif args.case in ("forward", "inverse"):
        result = run_case(f=2, K=1, inverse=args.case == "inverse")
    elif args.case == "phase":
        result = run_case(f=2, K=1, affine=False, outer=2, rows=2, coefficients=3)
    elif args.case == "guard":
        first, owner = run_case(guard=True, affine=False, coefficients=3, return_state=True)
        second = run_case(reuse=owner, affine=False, coefficients=3)
        result = dict(rejection=first, valid_retry=second)
    else:
        first, owner = run_case(H=2, affine=False, return_state=True)
        second = run_case(H=1, affine=False, reuse=owner)
        third = run_case(H=1, affine=False)
        need(second["physical_actions"] == third["physical_actions"], "old backing does not increase a fresh short call")
        need(second["retained_cells"] >= third["retained_cells"], "retained backing is honestly charged")
        result = dict(large=first, reused_small=second, fresh_small=third)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
