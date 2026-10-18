"""Exact rational/residue scope comparison; Apache-2.0.

Gareth Davidson, substantial OpenAI Codex assistance. The borrowed word and
dense residue executor are unchanged PR1057/1159 sources. Localization and
Newton inversion are standard algebra, not claimed new methods.
"""
from collections import Counter
from fractions import Fraction as F
from math import lcm
from pathlib import Path
import runpy

C = runpy.run_path(str(Path(__file__).with_name("common.py")))
need = C["need"]


def encode(value):
    value = F(value)
    return [value.numerator, value.denominator]


def residue(value, width):
    value = F(value)
    need(value.denominator % 2 == 1, "nonunit reduced denominator")
    modulus = 1 << width
    return (value.numerator * pow(value.denominator, -1, modulus)) % modulus


def multiply(a, b):
    return [[sum((x * y for x, y in zip(row, col)), F(0)) for col in zip(*b)] for row in a]


def product(factors):
    length = len(factors[0])
    result = [[F(i == j) for j in range(length)] for i in range(length)]
    for matrix in factors:
        result = multiply(matrix, result)
    return result


def rational_bound(factors, x, y):
    need(type(x) is int and type(y) is int and x >= 0 and y >= 0, "endpoint bound domain")
    growth = F(1)
    for matrix in factors:
        growth *= max(sum(abs(a) for a in row) for row in matrix)
    radius = y + x * growth
    bound = max(F(x), radius)
    width = 1
    while (1 << (width - 1)) <= bound:
        width += 1
    return dict(product_norm_bound=encode(growth), endpoint_radius=encode(radius), width=width)


def validate(factors, width, x, y):
    need(type(width) is int and width >= 1, "positive width")
    need(type(factors) is list and len(factors) > 0, "nonempty rational factors")
    length = len(factors[0])
    need(length > 0 and all(len(a) == length and all(len(row) == length for row in a)
                           for a in factors), "square rational matrices")
    need(all(F(z).denominator % 2 for a in factors for row in a for z in row), "nonunit reduced denominator")
    # This explicit admission route checks the complete rational product.
    # Its arbitrary-precision arithmetic/preparation cost is separate and paid.
    endpoint = product(factors)
    need(all(z.denominator == 1 for row in endpoint for z in row), "completed map not integral")
    info = rational_bound(factors, x, y)
    need(max(F(x), F(*info["endpoint_radius"])) < 1 << (width - 1), "strict signed recovery guard")
    return endpoint, info


def scale_fixture(factors, denominator=3):
    """Central scales alternate 1/q,q; a last unpaired factor has scale one."""
    n = len(factors)
    exponents = [-1 if i % 2 == 0 else 1 for i in range(n)]
    if n % 2:
        exponents[-1] = 0
    scales = [F(denominator) ** e for e in exponents]
    return [[[F(z) * scale for z in row] for row in matrix]
            for matrix, scale in zip(factors, scales)], exponents


def prefix_basis(word, factors, width, x_bound, y_bound):
    """Independent exact rational matrices on all five arrays, no residue code."""
    length = len(factors[0])
    size = 5 * length
    state = [[F(i == j) for j in range(size)] for i in range(size)]
    denominators = 1
    witness = None
    limits = [x_bound] * length + [y_bound] * length + [1 << (width - 1)] * (3 * length)
    peak_bound = F(max(limits))
    for at, (source, target, factor, sign) in enumerate(word):
        source_rows = state[source * length:(source + 1) * length]
        delta = multiply(factors[factor], source_rows)
        for i in range(length):
            row = [a + sign * b for a, b in zip(state[target * length + i], delta[i])]
            state[target * length + i] = row
            for j, value in enumerate(row):
                before = denominators
                denominators = lcm(denominators, value.denominator)
                if denominators != before:
                    witness = dict(leaf=at, row=target * length + i, column=j, value=encode(value))
            peak_bound = max(peak_bound, sum(abs(a) * b for a, b in zip(row, limits)))
    expected = [[F(i == j) for j in range(size)] for i in range(size)]
    endpoint = product(factors)
    # The caller supplies either the positive word or its literal inverse.
    positive = all(state[length+i][j] - expected[length+i][j] == endpoint[i][j]
                   for i in range(length) for j in range(length))
    negative = all(state[length+i][j] - expected[length+i][j] == -endpoint[i][j]
                   for i in range(length) for j in range(length))
    need(positive or negative, "basis target map")
    direction = 1 if positive else -1
    for i in range(length):
        for j in range(length):
            expected[length+i][j] += direction * endpoint[i][j]
    need(state == expected, "arbitrary dirty basis restoration")
    scaled = denominators * peak_bound
    need(scaled.denominator == 1, "common denominator bound integral")
    return dict(columns=size, leaf_prefixes=len(word), endpoint_direction=direction,
                least_common_prefix_denominator=denominators, denominator_witness=witness,
                rational_absolute_prefix_bound=encode(peak_bound),
                common_numerator_bound=str(scaled.numerator),
                common_numerator_sufficient_bits=scaled.numerator.bit_length() + 1)


def prepare(factors, width):
    """Literal bounded-register preparation for this declared descriptor class.

    Original signed numerators must fit w+2 bits and denominators lie in 1..M-1.
    Larger descriptors need an additional streamed reduction implementation.
    Four work registers have the SAME capacities as PR1159, and are reused.
    Every read, inverse check, move, reduction, write and private clear is paid.
    """
    modulus, mask = 1 << width, (1 << width) - 1
    flat = [F(z) for a in factors for row in a for z in row]
    denominators = sorted({z.denominator for z in flat})
    need(all(q % 2 and 0 < q < modulus for q in denominators), "preparation unit descriptor range")
    need(all(-(1 << (width + 1)) <= z.numerator < 1 << (width + 1) for z in flat),
         "preparation numerator descriptor range")
    counts = Counter()
    length = len(factors[0])
    entries = len(flat)
    numerator_bits = max(abs(z.numerator).bit_length()+1 for z in flat)
    denominator_bits = max(z.denominator.bit_length() for z in flat)
    coefficient_start = 5*length*width
    inverse_start = coefficient_start + entries*width
    descriptor_start = inverse_start + len(denominators)*width
    descriptor_stride = numerator_bits + denominator_bits
    trace, head, travel, scans = [], 0, 0, 0

    def visit(position, bits, kind):
        nonlocal head, travel, scans
        travel += abs(position-head)
        scans += 2*(bits-1)
        head = position
        trace.append([position, bits, kind])

    def home():
        nonlocal head, travel
        travel += head
        head = 0
    peaks = {role: 0 for role in "acvp"}
    work = {role: 1 for role in "acvp"}
    bits = dict(a=width+1, c=width, v=width+2, p=2*width)

    def put(op, role, value):
        counts[op] += 1
        need(-(1 << (bits[role]-1)) <= value < 1 << (bits[role]-1) if role == "v"
             else 0 <= value < 1 << bits[role], "preparation work overflow")
        work[role] = value
        peaks[role] = max(peaks[role], abs(value))

    def clear():
        for role in "acvp":
            put("zero", role, 0)

    inverses, iterations = {}, {}
    for q in denominators:
        clear()
        first = next(i for i, z in enumerate(flat) if z.denominator == q)
        visit(descriptor_start+first*descriptor_stride+numerator_bits, denominator_bits, "read")
        put("read_denominator", "c", q)
        counts["check_odd"] += 1
        need(work["c"] % 2 == 1, "unit inverse")
        put("set_one", "a", 1)
        correct, steps = 1, 0
        while correct < width:
            put("mul", "p", work["c"] * work["a"])
            put("low", "p", work["p"] & mask)
            put("subtract", "v", 2 - work["p"])
            put("low", "v", work["v"] & mask)
            put("mul", "p", work["a"] * work["v"])
            put("low", "p", work["p"] & mask)
            put("move", "a", work["p"])
            correct *= 2
            steps += 1
        put("mul", "p", work["c"] * work["a"])
        put("low", "p", work["p"] & mask)
        counts["check_one"] += 1
        need(work["p"] == 1, "prepared inverse incorrect")
        counts["write_inverse"] += 1
        visit(inverse_start+denominators.index(q)*width, width, "write")
        inverses[q], iterations[q] = work["a"], steps
        clear()
        home()
    inverse_counts = dict(counts)
    clear()  # Explicit coefficient-program startup.
    encoded = []
    for index, value in enumerate(flat):
        visit(descriptor_start+index*descriptor_stride, numerator_bits, "read")
        put("read_numerator", "v", value.numerator)
        put("low", "v", work["v"] & mask)
        visit(descriptor_start+index*descriptor_stride+numerator_bits, denominator_bits, "read")
        put("read_denominator", "c", value.denominator)
        visit(inverse_start+denominators.index(value.denominator)*width, width, "read")
        put("read_inverse", "c", inverses[work["c"]])
        put("mul", "p", work["c"] * work["v"])
        put("low", "p", work["p"] & mask)
        counts["write_coefficient"] += 1
        visit(coefficient_start+index*width, width, "write")
        encoded.append(work["p"])
        clear()
        home()
    need(all(v == 0 for v in work.values()), "preparation private closure")
    matrices = []
    at = 0
    for _ in factors:
        matrices.append([encoded[at+i*length:at+(i+1)*length] for i in range(length)])
        at += length*length
    return matrices, dict(counts=dict(counts), commands=sum(counts.values()),
                          inverse_counts=inverse_counts, inverse_commands=sum(inverse_counts.values()),
                          iterations={str(q): n for q, n in iterations.items()},
                          inverse_table=[[q, inverses[q]] for q in denominators],
                          inverse_table_bits=len(denominators)*width,
                          work_bits=sum(bits.values()), work_peaks=peaks,
                          original_descriptor_fixed_bits=entries*descriptor_stride,
                          descriptor_layout=dict(numerator_bits=numerator_bits, denominator_bits=denominator_bits,
                                                 coefficient_start=coefficient_start, inverse_start=inverse_start,
                                                 descriptor_start=descriptor_start),
                          external_memory=dict(accesses=len(trace), bit_actions=sum(x[1] for x in trace),
                              interfield_bit_travel=travel, head_bit_moves=travel+scans,
                              trace_sha256=C["digest"](trace),
                              data_coefficient_inverse_descriptor_bits=descriptor_start+entries*descriptor_stride),
                          original_descriptor_bits=sum(max(1, abs(z.numerator).bit_length()+1)
                                                       + z.denominator.bit_length() for z in flat))


def lifted_replay(word, factors, initial, coefficients, width, dense, x_bound, y_bound):
    """Every native primitive, paired with separate exact Fraction leaf updates."""
    initial_fraction = [[F(x) for x in row] for row in initial]
    need(max(abs(x) for x in initial_fraction[0]) <= x_bound, "actual input exceeds declared bound")
    need(max(abs(x) for x in initial_fraction[1]) <= y_bound, "actual output entry exceeds declared bound")
    rational = [row[:] for row in initial_fraction]
    modulus = 1 << width
    start = [[x % modulus for x in row] for row in initial]
    peak_numerator, peak_denominator, prefix_count = 1, 1, 0

    def observe(at, record, data):
        nonlocal peak_numerator, peak_denominator, prefix_count
        source, target, factor, sign = word[at]
        need(tuple(record) == tuple(word[at]), "literal leaf order")
        delta = [sum((a*b for a, b in zip(row, rational[source])), F(0)) for row in factors[factor]]
        rational[target] = [a+sign*b for a, b in zip(rational[target], delta)]
        need(data == [[residue(x, width) for x in row] for row in rational], "rational/residue prefix")
        for row in rational:
            for x in row:
                peak_numerator = max(peak_numerator, abs(x.numerator))
                peak_denominator = max(peak_denominator, x.denominator)
        prefix_count += 1

    final, report = dense.execute(dense.primitive_word(word, len(factors[0])), coefficients, start, width, observe)
    for i in (0, 2, 3, 4):
        need(rational[i] == initial_fraction[i] and final[i] == start[i], "dirty data restoration")
    need(all(x.denominator == 1 for x in rational[1]), "completed output not integral")
    need([dense.signed(x, width) for x in final[1]] == rational[1], "signed endpoint recovery")
    return dict(target=[int(x) for x in rational[1]], primitive=report, leaf_prefixes=prefix_count,
                numerator_peak_signed_bits=peak_numerator.bit_length()+1,
                denominator_peak=peak_denominator, final_residues=final)
