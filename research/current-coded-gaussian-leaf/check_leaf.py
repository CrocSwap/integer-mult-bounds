"""Complete current packets against direct tensor coefficients, not butterflies.

Fixture construction/inspection may use Python integers and arrays; the sealed
physical call cannot. Prepared for @CubeJerry with substantial OpenAI assistance.
"""
from argparse import ArgumentParser
from hashlib import sha256
import json
from leaf_provider import Provider, S, SCHEMA
from leaf_sources import need

DenseTape = S.codec.DenseTape


def code(symbols):
    return [((value >> shift) & 1) for value in symbols for shift in (2, 1, 0)]


def encoded_header(values):
    bits = []
    for key in SCHEMA:
        digits = [int(x) for x in bin(values[key])[2:][::-1]]
        bits.extend([1] * len(digits) + [0] + digits)
    return bits


def packet(records, width):
    symbols = []
    for record in records:
        for real, imag in record:
            for value in (real, imag):
                need(-(1 << (width - 1)) <= value < 1 << (width - 1), "checker signed input")
                symbols.extend((value >> i) & 1 for i in range(width))
                symbols.append(2)
    return code(symbols)


def complex_product(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def oracle(records, values, inverse=False):
    """One direct 2^f by 2^f Gaussian tensor per spectator/row fibre."""
    f, K, rho, a, start = (values[k] for k in ("f", "K", "rho", "within_bits", "active_start"))
    masks = tuple(1 << (a - 1 - start - j * K - rho) for j in range(f))
    fullmask = sum(masks)
    count = 1 << a
    out = [None] * len(records)
    for row in range(values["outer"] * values["rows"]):
        for fixed in range(count):
            if fixed & fullmask:
                continue
            addresses = [fixed | sum(m for j, m in enumerate(masks) if bits >> j & 1)
                         for bits in range(1 << f)]
            for y, address in enumerate(addresses):
                answer = []
                for c in range(len(records[0])):
                    real = imag = 0
                    for x, source in enumerate(addresses):
                        scalar = (1, 0)
                        for j in range(f):
                            sign = 1 if (x ^ y) >> j & 1 == 0 else -1
                            if inverse:
                                sign = -sign
                            scalar = complex_product(scalar, (1, sign))
                        product = complex_product(scalar, records[row * count + source][c])
                        real += product[0]; imag += product[1]
                    divisor = 1 << f
                    need(real % divisor == imag % divisor == 0, "checker exact Gaussian tensor grid")
                    answer.append((real // divisor, imag // divisor))
                out[row * count + address] = tuple(answer)
    return out


def fixture(*, f=1, K=1, rho=0, before=1, after=1, h=8, r=2, rows=1, outer=1,
            inverse=False, fault=None):
    a = before + f * K + after
    b = 6 * r * (h + 1)
    values = dict(outer=outer, rows=rows, stock=1, row_bits=(1 << a) * b,
                  within_bits=a, record_bits=b, p=max(2, f), d=max(2, f), K=K, G=1,
                  H=1, q0=3, qF=0, qB=0, D=max(2, f), f=f, rho=rho,
                  active_start=before, back_start=before + f * K, selected_axes=f,
                  entry_start=before, remainder=0, cutoff=max(2, f))
    reserve = 1 << ((f + 1) // 2)
    records = [tuple((reserve * ((i + 3 * j) % 7 - 3),
                      reserve * ((i // 3 + 2 * j) % 7 - 3)) for j in range(r))
               for i in range(outer * rows * (1 << a))]
    if fault == "overflow":
        records = [((0, 0),) for _ in records]
    expected = oracle(records, values, inverse)
    if fault == "parity":
        last = list(records[-1]); real, imag = last[-1]
        last[-1] = (real + 1, imag); records[-1] = tuple(last)
    elif fault == "overflow":
        need(f == 1 and h == 3 and r == 1, "checker targeted signed overflow")
        records = [((0, 0),) for _ in records]
        mask = 1 << (a - 1 - before - rho)
        low = (1 << a) - 1 - mask
        records[-(1 << a) + low] = ((3, 3),)
        records[-1] = ((3, -3),)
    elif fault == "cutoff":
        need(f > 1, "checker nonleaf width")
        values["cutoff"] = f - 1
    return values, packet(records, h), packet(expected, h)


def load(tape, raw):
    tape.cells[tape.origin:] = bytearray(raw)
    tape.head, tape.high = tape.origin, tape.origin + len(raw)


def body(tape):
    result = []
    for value in tape.cells[tape.origin:]:
        if value == 6:
            break
        result.append(value)
    return result


def run_case(*, reuse=None, return_state=False, inverse=False, fault=None, **case):
    values, initial, expected = fixture(inverse=inverse, fault=fault, **case)
    if reuse is None:
        owner = Provider(inverse)
        work = tuple(DenseTape(3 + i % 4) for i in range(owner.port_count))
        field, context = DenseTape(9), DenseTape(11)
        for tape in (*work, field, context):
            for i in range(tape.origin - 1):
                tape.cells[i] = i % 2
        owner.bind(work)
    else:
        owner, work, field, context = reuse
        need(owner.inverse == inverse, "compiled direction preserved across reuse")
    load(field, initial)
    header = encoded_header(values)
    load(context, header)
    ancestors = tuple(bytes(t.cells[:t.origin]) for t in (*work, field, context))
    before_actions = sum(t.actions() for t in (*work, field, context))
    error = None
    try:
        owner.run(S.abi.CodedPort(field), S.abi.BinaryContextPort(context))
    except (S.linear.CoefficientDomainError, ValueError) as caught:
        error = caught
    if fault in ("parity", "overflow"):
        need(type(error) is S.linear.CoefficientDomainError, "named arithmetic rejection")
    elif fault == "cutoff":
        need(type(error) is ValueError and "elementary PAID branch" in str(error), "nonleaf rejection")
    else:
        if error is not None:
            raise error
    need(body(field) == (initial if fault else expected), "independent direct Gaussian tensor endpoint")
    need(body(context) == header, "exact complete header preserved")
    need(field.head == field.origin and context.head == context.origin, "public heads restored")
    need(all(t.head == t.origin and all(x == 6 for x in t.cells[t.origin:]) for t in work),
         "all reached private current bodies physically erased")
    need(all(bytes(t.cells[:t.origin]) == saved for t, saved in zip((*work, field, context), ancestors)),
         "suspended ancestor bytes untouched")
    need(owner.engine.closed and not owner.engine.pool.live and not owner.pool.live, "closed fixed inventory")
    report = dict(case=case, inverse=inverse, rejection=fault,
                  records=values["outer"] * values["rows"] * (1 << values["within_bits"]),
                  physical_bits=len(initial), physical_actions=sum(t.actions() for t in (*work, field, context)) - before_actions,
                  work_ports=owner.port_count, retained_cells=sum(len(t.cells) for t in work),
                  endpoint_sha256=sha256(bytes(body(field))).hexdigest())
    return (report, (owner, work, field, context)) if return_state else report


def main():
    parser = ArgumentParser()
    parser.add_argument("case", choices=("single", "spaced", "inverse", "multiple", "reject", "reuse"))
    args = parser.parse_args()
    if args.case == "single":
        result = run_case(f=1, K=2, rho=0)
    elif args.case == "spaced":
        result = run_case(f=2, K=2, rho=1)
    elif args.case == "inverse":
        result = run_case(f=3, K=1, inverse=True)
    elif args.case == "multiple":
        result = run_case(f=2, K=1, rows=3, outer=2, r=3)
    elif args.case == "reject":
        parity, state = run_case(f=1, fault="parity", return_state=True)
        retry = run_case(f=1, reuse=state)
        overflow = run_case(f=1, h=3, r=1, fault="overflow")
        cutoff = run_case(f=2, fault="cutoff")
        result = dict(parity=parity, retry=retry, overflow=overflow, cutoff=cutoff)
    else:
        large, state = run_case(f=2, after=3, return_state=True)
        small = run_case(f=1, reuse=state)
        fresh = run_case(f=1)
        need(small["physical_actions"] == fresh["physical_actions"], "old backing is not rescanned")
        need(small["retained_cells"] >= fresh["retained_cells"], "historical backing remains charged")
        result = dict(large=large, reused=small, fresh=fresh)
    print("PASS_CURRENT_CODED_GAUSSIAN_LEAF " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
