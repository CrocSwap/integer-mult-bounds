"""Independent tests of Bell contraction from arbitrary computational entries.

Small matrices use Gaussian-integer numerators and explicit denominators.
The full four-qubit address counts require no full-size tensor allocation.
apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""

from functools import cache
from itertools import combinations_with_replacement, product
from math import isqrt, prod
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(v):
    return v.bit_count() % 2


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def conj(a):
    return a[0], -a[1]


def scale(a, n):
    return a[0] * n, a[1] * n


def xor_sum(labels):
    value = 0
    for label in labels:
        value ^= label
    return value


def kron(a, b):
    return [[u * v for u in row_a for v in row_b] for row_a in a for row_b in b]


def literal_weyl(label, qubits):
    # Ordinary Kronecker construction; row and column signs are read from
    # the resulting matrix, independently of the address allocator below.
    d = 2**qubits
    z, x = divmod(label, d)
    w = [[1]]
    for bit in reversed(range(qubits)):
        sign = -1 if z & (1 << bit) else 1
        gate = [[0, sign], [1, 0]] if x & (1 << bit) else [[1, 0], [0, sign]]
        w = kron(w, gate)
    return w


def indexed_word(pairs, singleton, d):
    index = 0
    for row, col in pairs:
        index = (index * d + row) * d + col
    return index * d + singleton


def signed_addresses(labels, d):
    # Indices differ by the prescribed pair shifts. A base-d suffix is
    # reserved for the singleton, so these are the start offsets of blocks.
    parts = [divmod(label, d) for label in labels]
    for cols in product(range(d), repeat=len(parts)):
        pairs = [(col ^ x, col) for col, (_, x) in zip(cols, parts)]
        sign = (-1) ** (sum(parity(z & col) for col, (z, _) in zip(cols, parts)) % 2)
        yield indexed_word(pairs, 0, d), sign


def raw_singleton_row(inp, out, i, j, d):
    # Weights are the *numerators* of Bell contractions. Multiplying by
    # sqrt(d) accounts for raw observations of normalized tensor columns.
    zw, xw = divmod(xor_sum(inp), d)
    zv, xv = divmod(xor_sum(out), d)
    row, col = i ^ xv, j ^ xw
    endpoint_sign = (-1) ** (parity(zv & row) ^ parity(zw & col))
    inbound = tuple(signed_addresses(inp, d))
    return {(a + row, b + col): sa * sb * endpoint_sign
            for a, sa in signed_addresses(out, d) for b, sb in inbound}


def literal_basis(labels, singleton, qubits):
    d = 2**qubits
    # Flatten each literal Weyl in row-major order and take their tensor
    # product followed by a singleton unit vector; drop zeros only afterward.
    numerators = [1]
    for label in labels:
        w = literal_weyl(label, qubits)
        numerators = [a * b for a in numerators for row in w for b in row]
    return {i*d + singleton: a for i, a in enumerate(numerators) if a}


def datum(i, j):
    # An arbitrary observation, free of any promise of a Clifford mixture.
    return ((i*i + 11*i*j + 7*j + 3) % 43 - 21,
            (5*i + 3*j*j + i*j + 4) % 47 - 23)


def evaluate(row):
    total = (0, 0)
    for (i, j), a in row.items():
        total = add(total, scale(datum(i, j), a))
    return total


def reference_block(inp, out, qubits):
    d = 2**qubits
    left = [literal_basis(out, i, qubits) for i in range(d)]
    right = [literal_basis(inp, j, qubits) for j in range(d)]
    bare = [[evaluate({(a, b): sa*sb for a, sa in u.items() for b, sb in v.items()})
             for v in right] for u in left]
    w_out = literal_weyl(xor_sum(out), qubits)
    w_in = literal_weyl(xor_sum(inp), qubits)
    result = []
    for u in w_out:
        row = []
        for v in w_in:  # right inverse of the input Weyl is its transpose
            entry = (0, 0)
            for i, s in enumerate(u):
                for j, t in enumerate(v):
                    if s and t:
                        entry = add(entry, scale(bare[i][j], s * t))
            row.append(entry)
        result.append(row)
    return result


def targets():
    # Four-dimensional unitary numerators: identity, phase on qubit 1,
    # one rephased Hadamard, and a two-qubit Walsh matrix.
    for kind, denominator in (("I", 1), ("S", 1), ("h", 2), ("HH", 2)):
        entries = {}
        for i, j in product(range(4), repeat=2):
            sign = (-1) ** parity(i & j)
            if kind == "I" and i == j:
                entries[i, j] = (1, 0)
            elif kind == "S" and i == j:
                entries[i, j] = (0, 1) if i & 1 else (1, 0)
            elif kind == "h" and i >> 1 == j >> 1:
                local = (-1) ** (i & j & 1)
                entries[i, j] = (local, local)
            elif kind == "HH":
                entries[i, j] = (sign, 0)
        require(sum(a*a+b*b for a, b in entries.values()) == 4 * denominator**2,
                "target normalization")
        yield entries, denominator


def compare(inp, out, with_traces):
    d = 4
    ref = reference_block(inp, out, 2)
    rows = {}
    seen = set()
    for i, j in product(range(d), repeat=2):
        line = raw_singleton_row(inp, out, i, j, d)
        require(len(line) == d**(2*len(inp)) and not seen.intersection(line),
                "singleton support or disjointness")
        require(evaluate(line) == ref[i][j], "computational-address contraction mismatch")
        rows[i, j] = line
        seen.update(line)
    trace_cases = 0
    if with_traces:
        for target, den in targets():
            # Actual scalar denominator is d*den. The common numerator
            # scale is sqrt(d) from undoing column and Bell normalizations.
            weights = {address: scale(conj(coeff), isqrt(d)*sgn)
                       for ij, coeff in target.items() for address, sgn in rows[ij].items()}
            require(len(weights) == len(target)*d**(2*len(inp)), "trace read count")
            actual = (0, 0)
            for (a, b), coeff in weights.items():
                actual = add(actual, mul(coeff, datum(a, b)))
            reference = (0, 0)
            for (i, j), coeff in target.items():
                reference = add(reference, mul(conj(coeff), ref[i][j]))
            # Literal Bell elements contribute 1/d^k for k input-output
            # pairs after multiplying the two 1/sqrt(d) factors per pair.
            k = len(inp)
            require(scale(actual, d**k) == scale(reference, isqrt(d)**(2*k+1)),
                    "normalized raw-entry units")
            require(d * den in (4, 8), "trace denominator")
            trace_cases += 1
    return len(rows), trace_cases


def check_shears():
    # Literal diagonal Clifford phases. The phase ratio at each y relative
    # to zero determines which Z-character it adds to the Bell label.
    bits = 4
    d = 2**bits
    positions = tuple(combinations_with_replacement(range(bits), 2))
    for mask in range(1 << len(positions)):
        forms = [0] * bits
        for k, (i, j) in enumerate(positions):
            if mask & (1 << k):
                forms[i] |= 1 << j
                forms[j] |= 1 << i
        diagonal = sum(((row >> i) & 1) << i for i, row in enumerate(forms))
        q = []
        for y in range(d):
            phase = 0
            for k, (i, j) in enumerate(positions):
                if mask & (1 << k) and y & (1 << i) and y & (1 << j):
                    phase += 1 if i == j else 2
            q.append(phase % 4)
        for x in range(d):
            add_z = diagonal ^ sum(parity(row & x) << i for i, row in enumerate(forms))
            for y in range(d):
                require((q[y ^ x] + q[y] - q[x]) % 4 == 2*parity(y & add_z),
                        "affine shear changed a shift or gave a wrong Z-character")
    # Two distinct frequencies with identical physical support can cancel.
    a = raw_singleton_row((0,), (0,), 0, 0, 4)
    b = raw_singleton_row((4,), (0,), 0, 0, 4)
    c = raw_singleton_row((1,), (0,), 0, 0, 4)
    require(a.keys() == b.keys() and not a.keys() & c.keys(), "shift class partition")
    require(sum(a[k] + b[k] != 0 for k in a) * 2 == len(a),
            "unmerged support-count control")
    return (1 << len(positions))*d*d


ROOTS = ((1, 0), (0, 1), (-1, 0), (0, -1))


@cache
def weyl4(label):
    # The compiler numbers a Weyl as (X << 4) | Z. literal_weyl uses
    # the opposite convention. Read the signs from the full 16x16 matrix.
    x, z = divmod(label, 16)
    return literal_weyl((z << 4) | x, 4)


def split_coordinate(index):
    nibbles = tuple((index >> (4*j)) & 15 for j in reversed(range(13)))
    return tuple(zip(nibbles[0:12:2], nibbles[1:12:2])), nibbles[12]


def impulse_read(read, output, inp):
    outs, a = output
    ins, b = inp
    prefactor = prod(weyl4(t)[i][j] for t, (i, j) in zip(read.output_labels, outs))
    prefactor *= prod(weyl4(t)[i][j] for t, (i, j) in zip(read.input_labels, ins))
    if not prefactor:
        return 0, 0
    left = weyl4(xor_sum(read.output_labels))
    right = weyl4(xor_sum(read.input_labels))
    singleton = sum(left[i][a] * right[i][b] for i in range(16))
    return scale(ROOTS[read.correction_i], read.numerator * prefactor * singleton)


def check_compiled_impulses(reads, coefficient_numerator):
    # Coordinates count from zero in big-endian row/column base-16 order.
    # The first impulse occurs in several reads whose contributions cancel.
    points = ((0xddcc7700cc024, 0x88dd66ff99024, 0),
              (0x55ff11bb5546b, 0x22225577bb31b, 128),
              (0x5544cc7766576, 0xff99dd4466316, -128),
              (0xffaadd01ff5df, 0xcc775598ee2af, 512),
              (0xcc22eecd77e62, 0x8811bb76cc5d2, -512),
              (0, 1, 0))
    for n, (i, j, expected) in enumerate(points):
        output, inp = split_coordinate(i), split_coordinate(j)
        direct = (0, 0)
        supporting = 0
        for read in reads:
            value = impulse_read(read, output, inp)
            supporting += int(value != (0, 0))
            direct = add(direct, value)
        require(direct == (expected, 0), "literal 13-copy impulse value")
        require(coefficient_numerator(i, j) == expected, "compiled raw row impulse value")
        if n == 0:
            require(supporting >= 2, "cancellation control had no contributing reads")
        elif n == len(points) - 1:
            require(not supporting, "outside-support control unexpectedly contributed")
    return len(points)


def transvection_numerator(axis):
    # Twice the dyadic Clifford lift (1+i)(I+iP)/2, P=i^q W_axis.
    x, z = divmod(axis, 16)
    phase = mul((1, 1), ROOTS[1 + parity(x & z)])
    w = weyl4(axis)
    return [[add((1, 1) if i == j else (0, 0), scale(phase, w[i][j]))
             for j in range(16)] for i in range(16)]


def literal_action_column(gate, label, col, bell):
    # One literal column of G W G^T or G W G*, with G twice the lift.
    x, _ = divmod(label, 16)
    w = weyl4(label)
    result = [(0, 0)] * 16
    for k, right in enumerate(gate[col]):
        if right == (0, 0):
            continue
        factor = scale(right if bell else conj(right), w[k ^ x][k])
        for i in range(16):
            if gate[i][k ^ x] != (0, 0):
                result[i] = add(result[i], mul(factor, gate[i][k ^ x]))
    return result


def check_transvections(step):
    cases = 0
    nonreal = 0
    for axis in (1, 0x10, 0x11, 0x23, 0x35, 0x55, 0x8f, 0xff):
        gate = transvection_numerator(axis)
        for label in range(256):
            for bell in (False, True):
                new_label, exponent = step(axis, label, bell)
                expected = weyl4(new_label)
                unit = scale(ROOTS[exponent], 4)
                nonreal += exponent % 2
                for col in (0, 1, 2, 4, 8, 15):
                    actual = literal_action_column(gate, label, col, bell)
                    require(actual == [scale(unit, row[col]) for row in expected],
                            "transport phase or symplectic shift")
                    cases += 1
    require(nonreal > 0, "transport test lacks nonreal phases")
    return cases


def main():
    # Local imports provide the product under test. The literal references
    # above do not call its symplectic, phase or Walsh routines.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from bell_reads import iter_reads, step
    from raw_row import coefficient_numerator

    impulses = check_compiled_impulses(tuple(iter_reads()), coefficient_numerator)
    transported = check_transvections(step)
    counts = [0, 0]
    for a, b in product(range(16), repeat=2):
        n, t = compare((a,), (b,), with_traces=True)
        counts[0] += n
        counts[1] += t
    for a, b in (((9, 12), (5, 14)), ((2, 15), (4, 11))):
        n, t = compare(a, b, with_traces=True)
        counts[0] += n
        counts[1] += t
    shear_cases = check_shears()
    d, k = 16, 6
    per_entry = prod([d, d] * k)
    require(per_entry == 2**48 and d**2 * per_entry == 2**56,
            "four-qubit block size")
    require(isqrt(d)**(2*k+1) == 4*d**k and d*per_entry == 2**52,
            "four-qubit scale and monomial trace size")
    print("PASS_RAW_BELL_CONTRACTION", f"singleton_entries={counts[0]}",
          f"target_traces={counts[1]}", f"literal_shear_phase_checks={shear_cases}",
          f"four_qubit_reads_per_entry={per_entry}", f"literal_impulses={impulses}",
          f"transvection_columns={transported}")


if __name__ == "__main__":
    main()
