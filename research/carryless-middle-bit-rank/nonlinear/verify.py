#!/usr/bin/env python3
"""Check the finite nonlinear escape and its fixed-encoding gate minimum."""

import datetime as dt
import json
import resource
import time
from itertools import product


MASKS = (1, 3, 5, 15, 7, 9, 11, 13)


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Gates:
    def __init__(self):
        self.ands = 0
        self.xors = 0

    def xor(self, *inputs):
        self.xors += len(inputs) - 1
        result = 0
        for bit in inputs:
            result ^= bit
        return result

    def and_(self, left, right):
        self.ands += 1
        return left & right

    def counts(self):
        return {"AND": self.ands, "XOR": self.xors}


def bits(word, width):
    return tuple((word >> i) & 1 for i in range(width))


def encode(word, gates):
    one, x1, x2, x3, x4 = bits(word, 5)
    require(one == 1, "the circuit is defined on odd words")
    p = gates.xor(x2, x3)
    a = gates.xor(p, x4)
    b = gates.xor(x1, x4, gates.and_(x1, a), gates.and_(x2, gates.xor(x3, x4)))
    c = gates.xor(x1, x3, gates.and_(x4, p))
    return (1, a, b, c)


def convolve(a, b, gates):
    columns = [[] for _ in range(len(a) + len(b) - 1)]
    for i, j in product(range(len(a)), range(len(b))):
        if i == 0:
            value = b[j]
        elif j == 0:
            value = a[i]
        else:
            value = gates.and_(a[i], b[j])
        columns[i + j].append(value)
    return tuple(gates.xor(*column) for column in columns)


def decode(coefficients, gates):
    _, z1, z2, z3, z4, z5, z6 = coefficients
    a = gates.xor(z1, z5)
    b = gates.xor(z4, z6)
    c = gates.xor(z2, z3)
    left = gates.and_(z3, gates.xor(a, b))
    center = gates.and_(z4, z5)
    right = gates.and_(z6, gates.xor(a, z2))
    return gates.xor(c, b, z5, left, center, right)


def bitmask(coordinates):
    return sum(bit << i for i, bit in enumerate(coordinates))


def polynomial_oracle(a, b):
    result = 0
    for j in range(4):
        if (b >> j) & 1:
            result ^= a << j
    return result


def reduce_to_quotient(vector, basis):
    for pivot, other in basis:
        if (vector >> pivot) & 1:
            vector ^= other
    return vector


def row_basis(vectors):
    basis = []
    for vector in vectors:
        residual = reduce_to_quotient(vector, basis)
        if residual:
            basis.append((residual.bit_length() - 1, residual))
            basis.sort(reverse=True)
    return tuple(basis)


def minimum_decoder_gates(rows, target):
    """Decide all circuits with at most two decoder ANDs on reachable wires."""
    sample_count = len(rows)
    one = (1 << sample_count) - 1
    variable_columns = [bitmask(row[i] for row in rows) for i in range(1, 7)]
    basis = row_basis([one, *variable_columns])

    def residue(vector):
        return reduce_to_quotient(vector, basis)

    linear_forms = [0]
    for col in variable_columns:
        linear_forms += [form ^ col for form in linear_forms]
    target_class = residue(target)
    class_to_first_and = {}
    classes_using_left_factor = {}
    for left in linear_forms:
        classes = set()
        for right in linear_forms:
            gate = left & right
            gate_class = residue(gate)
            classes.add(gate_class)
            class_to_first_and.setdefault(gate_class, gate)
        classes_using_left_factor[left] = classes

    require(target_class not in class_to_first_and, "unexpected zero- or one-AND decoder")
    require(
        all((target_class ^ gate_class) not in class_to_first_and
            for gate_class in class_to_first_and),
        "unexpected two parallel ANDs",
    )
    serial_classes_checked = 0
    for gate_class, first_and in class_to_first_and.items():
        for left in linear_forms:
            result_class = target_class ^ residue(left & first_and)
            solutions = classes_using_left_factor[left]
            require(result_class not in solutions, "unexpected two serial ANDs")
            require((result_class ^ gate_class) not in solutions,
                    "unexpected two serial ANDs with reused first AND")
            serial_classes_checked += 2
    return {
        "affine_span_rank": len(basis),
        "one_gate_quotient_classes": len(class_to_first_and),
        "parallel_quotient_classes_checked": len(class_to_first_and),
        "serial_quotient_checks": serial_classes_checked,
        "minimum_ANDs_for_this_encoding": 3,
    }


def unit_class_table(m):
    modulus = 1 << m
    period = 1 << (m - 2)
    return {
        (sign * pow(5, t, modulus)) % modulus: (t + (sign == -1) * (period // 2)) % period
        for sign, t in product((1, -1), range(period))
    }


def odd_product_rank(m):
    domain = range(1, 1 << m, 2)
    rows = [bitmask(((x * y) >> (m - 1)) & 1 for y in domain) for x in domain]
    mask = (1 << len(domain)) - 1
    rank = len(row_basis(rows))
    complement_rank = len(row_basis(row ^ mask for row in rows))
    require(rank == complement_rank == (1 << (m - 3)) + 1, "wrong odd-product rank")
    require(len(set(rows)) == 1 << (m - 2), "wrong distinct row count")
    require(all(row not in (0, mask) for row in rows), "unexpected constant row")
    return {"m": m, "rank": rank, "affine_offset_rank": complement_rank,
            "distinct_rows": len(set(rows)), "matrix_side": len(domain)}


def main():
    utc_start = dt.datetime.now(dt.timezone.utc).isoformat()
    wall_start = time.monotonic()
    cpu_start = time.process_time()
    classes = unit_class_table(5)
    domain = range(1, 32, 2)
    representatives = [pow(5, t, 32) for t in range(8)]
    received = {}
    target = {}
    output_collisions = {}
    charged_breakdown = {
        "left_encoder": {"AND": 3, "XOR": 8},
        "right_encoder": {"AND": 3, "XOR": 8},
        "one_binary_convolution": {"AND": 9, "XOR": 9},
        "nonlinear_decoder": {"AND": 3, "XOR": 10},
    }
    for x, y in product(domain, repeat=2):
        left, right, convolution, decoder = (Gates() for _ in range(4))
        a, b = encode(x, left), encode(y, right)
        require(bitmask(a) == MASKS[classes[x]], "left encoding disagrees with power table")
        require(bitmask(b) == MASKS[classes[y]], "right encoding disagrees with power table")
        coefficients = convolve(a, b, convolution)
        word = bitmask(coefficients)
        require(word == polynomial_oracle(bitmask(a), bitmask(b)), "convolution disagrees")
        value = (x * y >> 4) & 1
        require(decode(coefficients, decoder) == value, "different odd product bit")
        require(value == (pow(5, classes[x] + classes[y], 32) >> 4), "bad unit quotient")
        for gates, expected in zip((left, right, convolution, decoder), charged_breakdown.values()):
            require(gates.counts() == expected, "gate count differs from fixed charge")
        require(output_collisions.setdefault(word, value) == value, "ambiguous convolution")
        received[x, y] = coefficients
        target[x, y] = value

    # Two distinct unordered input pairs can yield the same channel return.
    require(received[1, 1] == received[15, 1], "missing non-recovery control")
    require(received[1, 25] == received[5, 5], "missing distinct-class collision control")
    rows = [received[x, y] for x, y in product(representatives, repeat=2)]
    target_bits = bitmask(target[x, y] for x, y in product(representatives, repeat=2))
    optimization = minimum_decoder_gates(rows, target_bits)
    rank_controls = [odd_product_rank(m) for m in range(3, 10)]
    usage = resource.getrusage(resource.RUSAGE_SELF)
    print(json.dumps({
        "result": "pass",
        "m": 5,
        "operand_scope": "unsigned odd x,y in [1,31]",
        "output": "bit 4 of ordinary x*y, zero-based",
        "checked_pairs": len(received),
        "distinct_channel_returns": len(output_collisions),
        "polynomial_input_widths": [4, 4],
        "polynomial_output_width": 7,
        "minimum_widths_any_decoder": [4, 4],
        "minimum_widths_affine_decoder": [5, 5],
        "decoder_ANF_degree": 2,
        "degree_is_minimum_at_witness_width": True,
        "gate_counts": charged_breakdown,
        "total_gate_counts": {kind: sum(row[kind] for row in charged_breakdown.values())
                              for kind in ("AND", "XOR")},
        "fixed_encoding_optimality": optimization,
        "polynomial_collision_inputs": [[1, 25], [5, 5]],
        "odd_rank_controls": rank_controls,
        "source_comparator_only": {"PR": 7830, "head": "87fbf4f7b35b0f18ab12b5767775a9a424cf0b15"},
        "canonical_main_pin": "e54523517d0f03e58352e647c403a5af3e525a57",
        "kappa_target": "0.003884928046155",
        "P104_qualification": None,
        "limits": {"CPU_seconds": resource.getrlimit(resource.RLIMIT_CPU)[0],
                   "address_space_bytes": resource.getrlimit(resource.RLIMIT_AS)[0]},
        "utc_start": utc_start,
        "utc_end": dt.datetime.now(dt.timezone.utc).isoformat(),
        "wall_seconds": time.monotonic() - wall_start,
        "CPU_seconds": time.process_time() - cpu_start,
        "maximum_RSS_KiB": usage.ru_maxrss,
    }, indent=2))


if __name__ == "__main__":
    main()
