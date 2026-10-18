#!/usr/bin/env python3
"""Literal finite-width integer-matrix echo backend. Apache-2.0.

Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
Uses the unchanged credited PR1057 address word; does not synthesize a new tree.
"""
from collections import Counter
from pathlib import Path
import runpy

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
need = C["need"]


def dimensions(factors):
    need(type(factors) is list and len(factors) > 0, "nonempty factors")
    length = len(factors[0])
    need(length > 0 and all(type(a) is list and len(a) == length for a in factors), "matrix dimensions")
    need(all(type(row) is list and len(row) == length and all(type(x) is int for x in row)
             for a in factors for row in a), "integer matrix coefficients")
    return length


def bound(factors, x_bound, y_bound):
    dimensions(factors)
    need(type(x_bound) is int and type(y_bound) is int and min(x_bound, y_bound) >= 0,
         "nonnegative integer endpoint bounds")
    norms = [max(sum(abs(x) for x in row) for row in a) for a in factors]
    growth = 1
    for k in norms:
        growth *= k
    radius = y_bound + x_bound * growth
    return dict(norms=norms, product=growth, endpoint_radius=radius,
                width=max(1, max(x_bound, radius).bit_length() + 1))


def signed(value, width):
    return value if value < 1 << (width - 1) else value - (1 << width)


def admit(factors, initial, width, x_bound, y_bound):
    length = dimensions(factors)
    need(type(width) is int and width > 0, "positive integer width")
    modulus = 1 << width
    need(type(initial) is list and len(initial) == 5
         and all(type(row) is list and len(row) == length for row in initial), "five data arrays")
    need(all(type(x) is int and 0 <= x < modulus for row in initial for x in row), "canonical data residues")
    info = bound(factors, x_bound, y_bound)
    need(max(x_bound, info["endpoint_radius"]) < modulus // 2, "strict signed recovery guard")
    need(max(abs(signed(x, width)) for x in initial[0]) <= x_bound, "input bound")
    need(max(abs(signed(x, width)) for x in initial[1]) <= y_bound, "output entry bound")
    return info


def primitive_word(word, length):
    """Yield commands; only four scalar work registers, no array clear/copy."""
    for role in ("a", "v", "c", "p"):
        yield ("zero", role)
    for source, target, factor, sign in word:
        need(type(sign) is int and sign in (-1, 1), "leaf sign")
        need(type(source) is int and type(target) is int and 0 <= source < 5
             and 0 < target < 5 and source != target, "distinct protected leaf ports")
        need(type(factor) is int and factor >= 0, "factor id")
        for i in range(length):
            yield ("zero", "a")
            for j in range(length):
                yield ("read", "v", source, j)
                yield ("coeff", "c", factor, i, j)
                yield ("mul", "p", "c", "v")
                yield ("low", "p")
                yield ("add", "a", "p", 1)
                yield ("low", "a")
            yield ("read", "v", target, i)
            yield ("add", "v", "a", sign)
            yield ("low", "v")
            yield ("write", target, i, "v")
        for role in ("a", "v", "c", "p"):
            yield ("zero", role)
        yield ("boundary", source, target, factor, sign)


def execute(program, factors, initial, width, observer=None):
    """Run every literal scalar command, checking declared work widths.

    Initial work is deliberately nonzero. Startup and per-leaf zeroing are
    explicit commands. Python integers model bounded register operations;
    checks reject overflow of the specified intermediate work capacities.
    """
    length = dimensions(factors)
    need(type(width) is int and width > 0, "positive integer width")
    modulus, mask = 1 << width, (1 << width) - 1
    need(len(initial) == 5 and all(len(row) == length for row in initial), "data shape")
    need(all(type(x) is int and 0 <= x < modulus for row in initial for x in row), "canonical data residues")
    data = [row[:] for row in initial]
    coefficients = [[[x & mask for x in row] for row in a] for a in factors]
    work = dict(a=1, v=1, c=1, p=1)
    counts, reduced, maxima = Counter(), Counter(), dict(a=0, v=0, c=0, p=0)
    widths = dict(a=width + 1, v=width + 2, c=width, p=2 * width)
    head, distance, accesses, boundaries = 0, 0, 0, 0
    leaf_size = length * (6 * length + 5) + 4
    commands = 0

    def visit(address):
        nonlocal head, distance, accesses
        distance += abs(address - head)
        head = address
        accesses += 1

    for command in program:
        op, *args = command
        if op == "boundary":
            need(commands == 4 + (boundaries + 1) * leaf_size, "complete leaf primitive count")
            need(all(x == 0 for x in work.values()), "private work not cleared")
            need(data[0] == initial[0], "external input changed")
            distance += head
            head = 0
            if observer:
                observer(boundaries, tuple(args), data)
            boundaries += 1
            continue  # Annotation, not an executed data primitive; dispatcher is billed separately.
        commands += 1
        counts[op] += 1
        if op == "zero":
            role, = args
            work[role] = 0
            counts["zero_" + role] += 1
        elif op == "read":
            role, row, col = args
            work[role] = data[row][col]
            visit(row * length + col)
        elif op == "coeff":
            role, f, i, j = args
            need(type(f) is int and 0 <= f < len(factors), "coefficient factor range")
            work[role] = coefficients[f][i][j]
            visit(5 * length + (f * length + i) * length + j)
        elif op == "mul":
            role, a, b = args
            work[role] = work[a] * work[b]
        elif op == "add":
            role, source, sign = args
            need(type(sign) is int and sign in (-1, 1), "ADD sign")
            work[role] += sign * work[source]
            counts["add_" + role] += 1
        elif op == "low":
            role, = args
            reduced[role] += not 0 <= work[role] < modulus
            work[role] &= mask
            counts["low_" + role] += 1
        elif op == "write":
            row, col, role = args
            need(0 < row < 5 and 0 <= col < length, "protected output write")
            need(0 <= work[role] < modulus, "unreduced data write")
            data[row][col] = work[role]
            visit(row * length + col)
            continue
        else:
            raise ValueError("unknown primitive " + op)
        need(role in widths, "private register id")
        value = work[role]
        if role == "v":
            need(-(1 << (widths[role] - 1)) <= value < 1 << (widths[role] - 1), "signed work overflow")
        else:
            need(0 <= value < 1 << widths[role], "unsigned work overflow")
        maxima[role] = max(maxima[role], abs(value))
    need(all(x == 0 for x in work.values()) and head == 0, "final work/head closure")
    need(commands == 4 + boundaries * leaf_size, "complete program count")
    return data, dict(counts=dict(counts), commands=commands, leaves=boundaries,
                      nontrivial_reductions=dict(reduced), work_peaks=maxima,
                      work_widths=widths, work_bits=sum(widths.values()),
                      intercell_steps=distance, accesses=accesses,
                      head_bit_moves=width * distance + 2 * (width - 1) * accesses,
                      data_bit_actions=width * accesses)


def invoice(word, length, n, width):
    """Closed operation formulas and separate address itinerary, no primitive compiler."""
    count = len(word)
    square = count * length * length
    rows = count * length
    counts = dict(zero=count * (length + 4) + 4,
                  zero_a=rows + count + 1, zero_v=count + 1, zero_c=count + 1, zero_p=count + 1,
                  read=square + rows, coeff=square, mul=square,
                  low=2 * square + rows, low_a=square, low_p=square, low_v=rows,
                  add=square + rows, add_a=square, add_v=rows, write=rows)
    distance = 0
    for source, target, factor, _ in word:
        itinerary = [0]
        for i in range(length):
            for j in range(length):
                itinerary += [source * length + j, 5 * length + (factor * length + i) * length + j]
            itinerary += [target * length + i] * 2
        itinerary += [0]
        distance += sum(abs(a - b) for a, b in zip(itinerary, itinerary[1:]))
    access = 2 * square + 2 * rows
    b = max(1, (n - 1).bit_length()) + 2 * 3 + 1
    return dict(counts=counts, commands=count * (6 * length * length + 5 * length + 4) + 4,
                leaves=count, intercell_steps=distance, accesses=access,
                head_bit_moves=width * distance + 2 * (width - 1) * access,
                data_bit_actions=width * access, data_bits=5 * length * width,
                coefficient_bits=n * length * length * width, work_bits=5 * width + 3,
                program_record_bits=b, program_bits=count * b, program_read_bits=count * b,
                program_forward_and_rewind_bits=2 * count * b,
                address_events=access, address_bits=max(1, (5 * length + n * length * length - 1).bit_length()),
                preparation_reductions=n * length * length + 2 * length,
                decoded_target_cells=length)
