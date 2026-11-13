"""Check the grouped Type B seam by independently inverting both exact Laurent sectors."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal
from sys import version_info
from time import perf_counter

PINS = {
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/7481-APPLICATION.json": "1d93fae969ff24ecb91bb4bee6af74daaa9ea99141bcf630a77eeb1a167b1799",
}
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CASE = "type-b-root36-through-36-37-pre3058-even-first"
ROOTS, OFFSET, CUT, CAP = (36, 37), 36, 3058, 30
STAGES = 17
ONE, ZERO = (Q(1), Q(0)), (Q(0), Q(0))
UNIT_MASK = (0,) * STAGES
END_MASK = (1,) * STAGES
FIRST_MASK = (1,) * 8 + (0,) * 9
LAST_MASK = (0,) * 8 + (1,) * 9


def emit(**result):
    print(dumps(result, sort_keys=True, default=str), flush=True)


def unique_pairs(pairs):
    result = dict(pairs)
    assert len(result) == len(pairs), "duplicate JSON keys"
    return result


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def subtract(a, b):
    return a[0] - b[0], a[1] - b[1]


def multiply(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def conjugate(a):
    return a[0], -a[1]


def mask(stages):
    counts = Counter(stages)
    assert all(1 <= j <= STAGES for j in counts)
    return tuple(counts[j] for j in range(1, STAGES + 1))


def combine(out, source, sign, scalar=ONE, phase=0, body=UNIT_MASK):
    for (parity, exponents), coefficient in source.items():
        quotient, new_parity = divmod(parity + phase, 2)
        key = new_parity, tuple(a + b for a, b in zip(exponents, body, strict=True))
        value = multiply(scalar, coefficient)
        if quotient % 2 and sign == -1:
            value = -value[0], -value[1]
        total = add(out.get(key, ZERO), value)
        if total == ZERO:
            out.pop(key, None)
        else:
            out[key] = total


def trans(rows, event, sign, inverse):
    direction = -1 if inverse else 1
    if event[0] == "A":
        return
    if event[0] == "J":
        _, stage, aroles, (first, second, alpha, beta) = event
        assert all(role < OFFSET for role in aroles) and OFFSET <= first < second < 72
        assert (Q(alpha), Q(beta)) == (Q(-1), Q(1, 2))
        first -= OFFSET
        second -= OFFSET
        x, y = rows[first], rows[second]
        f, s = {}, {}
        factors = tuple(direction * exponent for exponent in mask((stage,)))
        if inverse:
            # J=B_j[[1,-q],[q^-1/2,1/2]]; det of the normalized matrix is 1.
            combine(f, x, sign, (Q(1, 2), 0), body=factors)
            combine(f, y, sign, phase=1, body=factors)
            combine(s, x, sign, (Q(-1, 2), 0), phase=-1, body=factors)
            combine(s, y, sign, body=factors)
        else:
            combine(f, x, sign, body=factors)
            combine(f, y, sign, (Q(-1), 0), phase=1, body=factors)
            combine(s, x, sign, (Q(1, 2), 0), phase=-1, body=factors)
            combine(s, y, sign, (Q(1, 2), 0), body=factors)
        rows[first], rows[second] = f, s
        return
    family, op, role, *args = event
    assert family == "B" and OFFSET <= role < 72
    i = role - OFFSET
    if op == "SWAP":
        j = args[0] - OFFSET
        assert 0 <= j < 36 and i != j
        rows[i], rows[j] = rows[j], rows[i]
        return
    if op == "ADD":
        donor, coefficient = args
        assert OFFSET <= donor < 72 and donor != role
        result = rows[i].copy()
        combine(result, rows[donor - OFFSET], sign, (direction * Q(coefficient), 0))
    else:
        result = {}
        if op == "SCALE":
            combine(result, rows[i], sign, (Q(args[0]) ** direction, 0))
        elif op == "LAMBDA":
            orientation, = args
            assert orientation in (-1, 1)
            # LAMBDA is 1 in q²=+1 and orientation*i in q²=-1.
            scalar = ONE if sign == 1 else (Q(0), Q(direction * orientation))
            combine(result, rows[i], sign, scalar)
        else:
            assert op in ("IDLE_ONE", "IDLE_ODD")
            phase = args[1] if op == "IDLE_ODD" else 0
            factors = tuple(direction * exponent for exponent in mask(args[0]))
            combine(result, rows[i], sign, phase=direction * phase, body=factors)
    rows[i] = result


def unit(role, parity, exponents, scalar):
    rows = [{} for _ in range(36)]
    rows[role - OFFSET] = {(parity, exponents): scalar}
    return rows


def endpoints(tape, sign):
    columns = []
    for role in ROOTS:
        # q³ = sign*q in this sector.
        rows = unit(role, 1, END_MASK, (Q(sign), Q(0)))
        for clock in range(len(tape) - 1, -1, -1):
            trans(rows, tape[clock], sign, inverse=True)
            if clock == CUT:
                columns.append(list(rows))
        assert rows == unit(role, 0, UNIT_MASK, ONE)
    return columns


def coefficients(columns):
    a, b = ({(role, parity, exponents): v
             for role, row in enumerate(col, OFFSET)
             for (parity, exponents), v in row.items()} for col in columns)
    return {k: (a.get(k, ZERO), b.get(k, ZERO)) for k in sorted(a.keys() | b.keys())}


def gram(rows):
    m00, m01, m11 = ZERO, ZERO, ZERO
    for a, b in rows:
        m00 = add(m00, multiply(conjugate(a), a))
        m01 = add(m01, multiply(conjugate(a), b))
        m11 = add(m11, multiply(conjugate(b), b))
    det = subtract(multiply(m00, m11), multiply(conjugate(m01), m01))
    assert det[1] == 0 and det[0] >= 0
    rank = 2 if det[0] else int(m00 != ZERO or m11 != ZERO)
    return rank, det[0]


def parse_key(key):
    role, parity, factors = key
    return role, parity, mask(factors)


def forbidden(key):
    return key[1:] != (0, FIRST_MASK)


def check_lead_minor(source, entries):
    first, second = map(parse_key, source["keys"])
    assert first != second and forbidden(first) and forbidden(second)
    actual = entries[first], entries[second]
    expected = tuple(tuple(tuple(Q(v) for v in pair) for pair in row) for row in source["rows"])
    assert actual == expected
    (a, b), (c, d) = actual
    det = subtract(multiply(a, d), multiply(b, c))
    assert det == tuple(Q(v) for v in source["determinant"]) != ZERO
    return det


def surviving_suffix(tape, entries, rank, sign):
    row = next((v for k, v in entries.items() if forbidden(k) and v != (ZERO, ZERO)), None)
    if rank == 0:
        basis = ONE, ZERO
    else:
        assert rank == 1
        a, b = row
        basis = b, (-a[0], -a[1])
    prefix = [{} for _ in range(36)]
    for key, (a, b) in entries.items():
        result = add(multiply(a, basis[0]), multiply(b, basis[1]))
        if result != ZERO:
            assert not forbidden(key)
            role = key[0]
            prefix[role - OFFSET][0, UNIT_MASK] = result
    assert any(prefix)
    rows = list(prefix)
    for event in tape[CUT:]:
        trans(rows, event, sign, inverse=False)
    expected = [{} for _ in range(36)]
    for role, value in zip(ROOTS, basis, strict=True):
        coeff = (sign * value[0], sign * value[1])
        if coeff != ZERO:
            expected[role - OFFSET][1, LAST_MASK] = coeff
    assert rows == expected
    return {"sector_kernel": basis, "divided_prefix_rows": {
                role: row[0, UNIT_MASK] for role, row in enumerate(prefix, OFFSET) if row},
            "formal_suffix_on_divided_prefix": True,
            "physical_exposure_independent_input_and_suffix_unverified": True}


def controls(tape):
    samples = [tape[1423], tape[CUT], ["B", "LAMBDA", 36, -1], ["B", "IDLE_ODD", 37, [8], -1],
               ["B", "ADD", 36, 37, "-2/3"], ["B", "SCALE", 37, "-3/5"], ["B", "SWAP", 36, 37]]
    for event in samples:
        for sign in (1, -1):
            a = unit(36, 1, FIRST_MASK, (Q(2, 3), Q(5, 7)))
            a[1][0, UNIT_MASK] = (Q(-1, 2), Q(4))
            for inverse in (False, True):
                transformed = list(a)
                trans(transformed, event, sign, inverse)
                trans(transformed, event, sign, not inverse)
                assert transformed == a, (event, sign, inverse)
    assert gram([((Q(1), Q(1)), ZERO), (ZERO, (Q(2), Q(-1)))]) == (2, Q(10))
    assert gram([(ONE, ONE), ((Q(2), 0), (Q(2), 0))]) == (1, Q(0))


def main():
    assert __debug__ and version_info[:2] == (3, 12)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("lead_receipt", type=Path)
    parser.add_argument("lead_sha256")
    args = parser.parse_args()
    started = perf_counter()
    completed = []

    def on_cap(_signal, _frame):
        emit(status="INDEPENDENT_CAP", completed_sectors=completed, unresolved=[CASE],
             cap_seconds=CAP, seconds=perf_counter() - started)
        raise SystemExit(124)

    signal(SIGALRM, on_cap)
    alarm(CAP)
    data = {p: (args.root / p).read_bytes() for p in PINS}
    assert {p: sha256(raw).hexdigest() for p, raw in data.items()} == PINS
    caller = loads(data["inputs/7113-CALLER.json"], object_pairs_hook=unique_pairs)
    app = loads(data["inputs/7481-APPLICATION.json"], object_pairs_hook=unique_pairs)
    assert app["caller_sha256"] == PINS["inputs/7113-CALLER.json"] and app["caller_head"] == CALLER
    tape = caller["events"]
    kind = caller["types"]["B"]
    assert caller["roles"] == 72 and caller["stages"] == 17 and len(tape) == 4783
    assert kind["offset"] == 36 and kind["ports"] == [15, 17, 27, 34, 35, 42, 47, 55]
    assert kind["diagonal"][:2] == [[-1, 0] + [1] * STAGES] * 2
    assert tape[1423] == ["J", 8, [8, 0, 18, 26], [36, 37, "-1", "1/2"]]
    assert tape[CUT] == ["J", 9, [9, 0, 18, 27], [36, 37, "-1", "1/2"]]
    assert not any(e[:2] == ["B", "QUERY"] for e in tape)
    controls(tape)
    raw_lead = args.lead_receipt.read_bytes()
    assert sha256(raw_lead).hexdigest() == args.lead_sha256
    lead = loads(raw_lead, object_pairs_hook=unique_pairs)
    assert lead["case"] == CASE and lead["clock"] == CUT and tuple(lead["old_roots"]) == ROOTS
    assert lead["tested"] == 1
    assert lead["status"] in ("EXACT_GROUPED_PREFIX_EXCLUSION", "PREFIX_SURVIVOR_SUFFIX_UNTESTED")
    entries_by_sign = {sign: coefficients(endpoints(tape, sign)) for sign in (1, -1)}
    result = {}
    for sign, entries in entries_by_sign.items():
        rank, determinant = gram(row for key, row in entries.items() if forbidden(key))
        assert rank == lead["sectors"][str(sign)]["rank"]
        stage = {"forbidden_rank": rank, "forbidden_gram_determinant": determinant,
                 "full_cut_coefficient_rows": len(entries),
                 "allowed_nonzero_rows": sum(not forbidden(key) for key in entries)}
        if rank == 2:
            stage["lead_minor_determinant"] = check_lead_minor(lead["sectors"][str(sign)], entries)
        result[str(sign)] = stage
        completed.append(sign)
    excluded = any(stage["forbidden_rank"] == 2 for stage in result.values())
    assert excluded == (lead["status"] == "EXACT_GROUPED_PREFIX_EXCLUSION")
    if not excluded:
        for sign, entries in entries_by_sign.items():
            stage = result[str(sign)]
            stage.update(surviving_suffix(tape, entries, stage["forbidden_rank"], sign))
    emit(status="PASS_INDEPENDENT_GROUPED_PREFIX_EXCLUSION" if excluded else "FORMAL_PREFIX_AND_SUFFIX_ONLY",
         case=CASE, old_roots=ROOTS, cut=CUT, tested=1, unresolved=[] if excluded else [CASE],
         sectors=result, original_endpoints_both_sectors=True, input_pins=PINS, caller_head=CALLER,
         lead_sha256=args.lead_sha256, cap_seconds=CAP, seconds=perf_counter() - started)
    alarm(0)


if __name__ == "__main__":
    main()
