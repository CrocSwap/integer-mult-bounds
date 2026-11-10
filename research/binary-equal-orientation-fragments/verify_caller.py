#!/usr/bin/env python3
"""Exact changed-header proof fixtures; Python standard library only.

Jerry Chen / @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
The interpreter is written separately from the retained predecessor caller.
Written proofs, rather than these finite fixtures, supply universal claims.
"""
from ast import FunctionDef, If, dump, parse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
SOURCE_SHA256 = "e99e4287091c6ce4ec9a563cb9ac6f45be35ff1ef421b4efa8c200cb9d639d6c"
ZERO = (Q(0), Q(0))
ONE = (Q(1), Q(0))


def need(ok, label):
    if not ok:
        raise ValueError(label)


def zmul(a, b):
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def accumulate(out, incoming, factor=ONE):
    for key, value in incoming.items():
        old = out.get(key, ZERO)
        value = zmul(value, factor)
        value = (old[0] + value[0], old[1] + value[1])
        if value == ZERO:
            out.pop(key, None)
        else:
            out[key] = value
    return out


def shifted(row, q=0, l=0, r=0):
    out = {}
    for (column, oldq, oldl, oldr), value in row.items():
        accumulate(out, {(column, (oldq + q) % 4, oldl + l, oldr + r): value})
    return out


def scaled(row, value):
    return accumulate({}, row, (Q(value), Q(0)))


def eye(size):
    return [{(i, 0, 0, 0): ONE} for i in range(size)]


def phase_s(row):
    out = accumulate({}, shifted(row, q=3), (Q(1, 2), Q(1, 2)))
    return accumulate(out, shifted(row, q=1), (Q(1, 2), Q(-1, 2)))


def lambda_phase(row, sign):
    need(sign in (-1, 1), "lambda sign")
    out = accumulate({}, row, (Q(1, 2), Q(sign, 2)))
    return accumulate(out, shifted(row, q=2), (Q(1, 2), Q(-sign, 2)))


def execute(events, size):
    rows = eye(size)
    for event in events:
        op = event[0]
        if op == "SCALE":
            _, dst, value = event
            rows[dst] = scaled(rows[dst], value)
        elif op == "SWAP":
            _, a, b = event
            rows[a], rows[b] = rows[b], rows[a]
        elif op == "LAMBDA":
            _, dst, sign = event
            rows[dst] = lambda_phase(rows[dst], sign)
        elif op == "QUERY":
            _, dst, src, exponent = event
            accumulate(rows[dst], shifted(rows[src], q=exponent))
        elif op == "LOCAL":
            _, body, src, dst = event
            need(src != dst and body in ("L", "R"), "native ports/body")
            accumulate(rows[dst], shifted(rows[src], q=-1))
            for port in (src, dst):
                rows[port] = shifted(rows[port], l=int(body == "L"), r=int(body == "R"))
        elif op == "IDLE_ONE":
            _, dst, body = event
            need(body in ("L", "R"), "idle body")
            rows[dst] = shifted(rows[dst], l=int(body == "L"), r=int(body == "R"))
        else:
            raise ValueError("unknown event " + op)
    return rows


def word(size):
    need(size in (4, 6), "interface size")
    events = []

    def emit(*event):
        events.append(list(event))

    def native(body, dst, src):
        emit("LAMBDA", dst, -1)
        emit("LOCAL", body, src, dst)
        emit("LAMBDA", dst, 1)

    def query(dst, src, sign):
        if sign == -1:
            emit("SCALE", dst, "-1")
        emit("LAMBDA", dst, -1)
        emit("QUERY", dst, src, -1)
        emit("LAMBDA", dst, 1)
        if sign == -1:
            emit("SCALE", dst, "-1")

    native("L", 2, 3)
    query(3, 2, -1)
    query(2, 3, 1)
    emit("SWAP", 2, 3)
    emit("SCALE", 2, "-1")
    emit("IDLE_ONE", 0, "L")
    emit("IDLE_ONE", 1, "L")
    native("R", 0, 1)
    if size == 6:
        emit("IDLE_ONE", 4, "R")
        emit("IDLE_ONE", 5, "R")
    return events


def endpoint(size, inverse=False):
    rows = eye(size)
    degree = -1 if inverse else 1
    cross = phase_s(rows[1])
    accumulate(rows[0], cross, (Q(-1 if inverse else 1), Q(0)))
    for i in (0, 1):
        rows[i] = shifted(rows[i], l=degree, r=degree)
    for i in (2, 3):
        rows[i] = shifted(phase_s(rows[i]), l=degree)
    if size == 6:
        for i in (4, 5):
            rows[i] = shifted(rows[i], r=degree)
    return rows


def compose(left, right):
    need(len(left) == len(right), "composition dimensions")
    out = []
    for row in left:
        new = {}
        for (column, q, l, r), coefficient in row.items():
            accumulate(new, shifted(right[column], q, l, r), coefficient)
        out.append(new)
    return out


def specialize_q_one(rows):
    out = []
    for row in rows:
        new = {}
        for (column, q, l, r), coefficient in row.items():
            accumulate(new, {(column, 0, l, r): coefficient})
        out.append(new)
    return out


def bit_specialization(rows):
    """First q^2=1 over Q(i), then require integers, then reduce mod two."""
    out = []
    for row in rows:
        integral = {}
        for (column, q, l, r), coefficient in row.items():
            accumulate(integral, {(column, q % 2, l, r): coefficient})
        new = set()
        for key, coefficient in integral.items():
            need(coefficient[1] == 0 and coefficient[0].denominator == 1,
                 "integral combined BIT coefficient")
            if coefficient[0].numerator % 2:
                new.add(key)
        out.append(new)
    return out


def direct_bit_word(size):
    """Independent set/XOR execution of the short normalized word."""
    rows = [{(i, 0, 0, 0)} for i in range(size)]

    def shift(row, s=0, l=0, r=0):
        return {(col, (olds + s) % 2, oldl + l, oldr + r)
                for col, olds, oldl, oldr in row}

    def query(dst, src):
        rows[dst] ^= shift(rows[src], s=1)

    query(2, 3)
    rows[2], rows[3] = shift(rows[2], l=1), shift(rows[3], l=1)
    query(3, 2)
    query(2, 3)
    rows[2], rows[3] = rows[3], rows[2]
    rows[0], rows[1] = shift(rows[0], l=1), shift(rows[1], l=1)
    query(0, 1)
    rows[0], rows[1] = shift(rows[0], r=1), shift(rows[1], r=1)
    if size == 6:
        rows[4], rows[5] = shift(rows[4], r=1), shift(rows[5], r=1)
    return rows


def source_binding(data):
    need(sha256(data).hexdigest() == SOURCE_SHA256, "retained source SHA256")
    tree = parse(data)
    construct = next(n for n in tree.body if isinstance(n, FunctionDef) and n.name == "construct")
    query = next(n for n in construct.body if isinstance(n, FunctionDef) and n.name == "query")
    supplier = next(n for n in construct.body if isinstance(n, FunctionDef) and n.name == "supplier")
    leaf = next(n for n in supplier.body if isinstance(n, If))
    expected_query = parse("def query(x,y):\n emit('LAMBDA',x,-1);emit('QUERY',x,y,-1);emit('LAMBDA',x,1)").body[0]
    expected_leaf = parse("if 'stage' in t:\n emit('LAMBDA',x,-1);emit('LOCAL',t['stage'],y,x);emit('LAMBDA',x,1);return").body[0]
    need(dump(query) == dump(expected_query), "literal query wrapper AST")
    need(dump(leaf) == dump(expected_leaf), "literal native wrapper AST")


def symbolic_invoice(a, b, thin_queries=2):
    """Compare coefficients of formal H(r); no concavity/float assumptions."""
    def linear(terms):
        out = Counter()
        for rank, coefficient in terms:
            out[rank] += coefficient
        return {rank: coefficient for rank, coefficient in out.items() if coefficient}

    old = [(a + b + 1, 2), (a + b, -2), (1, -1)]
    six = [(a + 1, 2), (b, 2), (a, -2), (b, -2), (1, -thin_queries)]
    four = [(a + 1, 2), (a, -2), (1, -thin_queries)]
    delta = [(a + 1, 2), (a, -2), (a + b + 1, -2), (a + b, 2), (1, -1)]
    need(linear(six) == linear(four), "whole suffix jobs cancel")
    need(linear(six + [(r, -c) for r, c in old]) == linear(delta),
         "complete local invoice, including extra thin query")


def main():
    source = (HERE / "frozen" / "caller6726.py").read_bytes()
    source_binding(source)
    reports = []
    for size in (4, 6):
        events = word(size)
        rows = execute(events, size)
        need(rows == endpoint(size), "every arbitrary-input forward coefficient")
        inverse = endpoint(size, inverse=True)
        need(compose(inverse, rows) == eye(size), "left mathematical inverse")
        need(compose(rows, inverse) == eye(size), "right mathematical inverse")
        need(bit_specialization(rows) == direct_bit_word(size), "independent characteristic-two transfer")
        counts = Counter(event[0] for event in events)
        expected_counts = {"LOCAL": 2, "QUERY": 2, "IDLE_ONE": size - 2,
                           "LAMBDA": 8, "SCALE": 3, "SWAP": 1}
        need(dict(counts) == expected_counts, "all literal events counted")
        reports.append({"inputs": size, "forward_coefficients": size * size,
                        "events": len(events), "opcodes": dict(sorted(counts.items())),
                        "word_sha256": sha256(json.dumps(events, separators=(",", ":")).encode()).hexdigest()})

    for a in range(1, 33):
        for b in range(1, 33):
            symbolic_invoice(a, b)

    controls = {}
    events = word(6)
    target = endpoint(6)
    failures = []
    for index, event in enumerate(events):
        mutant = events[:index] + events[index + 1:]
        need(execute(mutant, 6) != target, "deleted event not rejected: " + str(index))
        failures.append([index, event[0]])
    controls["every_single_event_deletion_rejected"] = failures

    phase_fault = deepcopy(events)
    phase_fault[next(i for i, event in enumerate(events) if event[0] == "QUERY")][-1] = 1
    wrong_phase = execute(phase_fault, 6)
    need(wrong_phase != target, "reversed q exponent rejected")
    need(specialize_q_one(wrong_phase) == specialize_q_one(target), "q=1 blind-spot control")
    controls["q_exponent_fault_rejected_full_ring_but_missed_at_q_one"] = True

    alias = deepcopy(events)
    alias[-2][1] = 2
    need(execute(alias, 6) != target, "fresh input alias rejected")
    controls["fresh_input_alias_rejected"] = True

    try:
        symbolic_invoice(8, 16, thin_queries=1)
    except ValueError:
        controls["unpriced_extra_query_rejected"] = True
    else:
        raise ValueError("unpriced extra query accepted")

    try:
        source_binding(source + b"\n# mutation\n")
    except ValueError:
        controls["changed_frozen_source_rejected"] = True
    else:
        raise ValueError("changed source accepted")

    receipt = {"result": "PASS", "source_sha256": SOURCE_SHA256,
               "interfaces": reports, "symbolic_invoice_pairs": 1024,
               "controls": controls}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
