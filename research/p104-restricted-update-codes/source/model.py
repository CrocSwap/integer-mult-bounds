"""Exact pointwise defects of the pinned P104 floor word. Apache-2.0.

New census implementation by Ross Richardson with OpenAI Codex assistance.
The literal word and prefix lattice are credited to Tekalign and Nick Petalas.
"""

from collections import Counter
import hashlib
import itertools
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def shape(rank):
    need(type(rank) is int and 1 <= rank <= 7, "word rank must be 1..7")
    return 2 << rank


def lift(values, rank):
    out = list(values)
    need(len(out) == shape(rank), "real vector dimension")
    need(all(type(x) is int for x in out), "integer coordinates required")
    for bit in range(rank):
        for address in range(1 << rank):
            if address & (1 << bit):
                continue
            other = address | (1 << bit)
            a, b = 2 * address, 2 * other
            dr, di = out[a] - out[b], out[a + 1] - out[b + 1]
            sr, si = out[b] + dr // 2, out[b + 1] + di // 2
            # Rotation by i followed by the second literal floor shear.
            br, bi = sr - (-di) // 2, si - dr // 2
            out[a], out[a + 1] = br - di, bi + dr
            out[b], out[b + 1] = br, bi
    return out


def numerator(values, rank):
    """A_r x = 2^r U_r x, without any divisions or floating point."""
    out = list(values)
    need(len(out) == shape(rank), "real vector dimension")
    for bit in range(rank):
        for address in range(1 << rank):
            if address & (1 << bit):
                continue
            other = address | (1 << bit)
            a, b = 2 * address, 2 * other
            ar, ai, br, bi = out[a], out[a + 1], out[b], out[b + 1]
            out[a], out[a + 1] = ar - ai + br + bi, ar + ai - br + bi
            out[b], out[b + 1] = ar + ai + br - bi, -ar + ai + br + bi
    return out


def defect(values, rank):
    return tuple((1 << rank) * a - b
                 for a, b in zip(lift(values, rank), numerator(values, rank), strict=True))


def stage_rows(rows, bit):
    dimension = len(rows)
    result = [[0] * dimension for _ in rows]
    for column in range(dimension):
        x = [row[column] for row in rows]
        for address in range(dimension // 2):
            if address & (1 << bit):
                continue
            other = address | (1 << bit)
            a, b = 2 * address, 2 * other
            ar, ai, br, bi = x[a], x[a + 1], x[b], x[b + 1]
            numerators = (ar - ai + br + bi, ar + ai - br + bi,
                          ar + ai + br - bi, -ar + ai + br + bi)
            need(all(n % 2 == 0 for n in numerators), "prefix parity was not imposed")
            for target, n in zip((a, a + 1, b, b + 1), numerators, strict=True):
                result[target][column] = n // 2
    return result


def transversal(rank):
    """An exact binary transversal via an index-two subgroup chain.

    Track original-input columns separately from their ideal current images.
    This does not compute or depend on a Hermite normal form.
    """
    dimension = shape(rank)
    original = [[int(i == j) for j in range(dimension)] for i in range(dimension)]
    current = [row[:] for row in original]
    generators, stage_indices = [], []
    for bit in range(rank):
        before = len(generators)
        for address in range(1 << rank):
            if address & (1 << bit):
                continue
            other = address | (1 << bit)
            for component in range(2):
                first, second = 2 * address + component, 2 * other + component
                odd = [j for j in range(dimension)
                       if (current[first][j] - current[second][j]) % 2]
                if not odd:
                    continue
                pivot = odd[0]
                generators.append(tuple(row[pivot] for row in original))
                for matrix in (original, current):
                    for row in matrix:
                        old = row[pivot]
                        for j in odd[1:]:
                            row[j] -= old
                        row[pivot] = 2 * old
        current = stage_rows(current, bit)
        stage_indices.append(len(generators) - before)
    return original, generators, stage_indices


def representatives(generators, dimension):
    """Enumerate every binary sum in reflected Gray order."""
    value = [0] * dimension
    previous = 0
    yield tuple(value)
    for i in range(1, 1 << len(generators)):
        gray = i ^ (i >> 1)
        changed = gray ^ previous
        bit = changed.bit_length() - 1
        sign = 1 if gray & changed else -1
        value = [x + sign * y for x, y in zip(value, generators[bit], strict=True)]
        yield tuple(value)
        previous = gray


def census(rank):
    need(type(rank) is int and 1 <= rank <= 3, "complete census rank must be 1..3")
    dimension = shape(rank)
    _, generators, stage_indices = transversal(rank)
    images = Counter(defect(x, rank) for x in representatives(generators, dimension))
    labels = len(images)
    fixed_bits = (labels - 1).bit_length()
    signed_width = max(abs(v) for image in images for v in image).bit_length() + 1
    image_stream = json.dumps(sorted(images.items()), separators=(",", ":")).encode()
    return {
        "rank": rank, "real_dimension": dimension,
        "coset_bits": len(generators), "cosets": 1 << len(generators),
        "stage_indices": stage_indices, "defect_values": labels,
        "fixed_label_bits": fixed_bits,
        "fiber_histogram": {str(k): v for k, v in sorted(Counter(images.values()).items())},
        "signed_defect_coordinate_bits": signed_width,
        "max_abs_scaled_defect": max(abs(v) for image in images for v in image),
        "image_fiber_sha256": hashlib.sha256(image_stream).hexdigest(),
    }


def full_box(rank):
    need(rank <= 2, "full-box exhaustive domain is rank 1 or 2")
    q = 1 << (rank // 2 + 1)
    return Counter(defect(x, rank) for x in itertools.product(range(q), repeat=shape(rank)))


def signed_encode(values, width):
    need(type(width) is int and width >= 2, "signed width")
    need(all(-(1 << (width - 1)) <= x < (1 << (width - 1)) for x in values),
         "signed defect encoding overflow")
    return sum((x % (1 << width)) << (width * i) for i, x in enumerate(values))


def table_invoice(address_bits, images, width):
    """A fixed full-address scan, including equality compute/uncompute.

    images is a Counter whose multiplicities count the addressed input rows.
    Costs omit no logical scan gates, but physical routing remains additional.
    """
    need(type(address_bits) is int and address_bits >= 2, "lookup address width")
    rows = 1 << address_bits
    need(sum(images.values()) == rows, "full address table required")
    return {
        "address_bits": address_bits, "rows": rows,
        "output_bits": len(next(iter(images))) * width,
        "clean_equality_work_bits": address_bits - 1,
        "toffoli": 2 * (address_bits - 1) * rows,
        "x": address_bits * rows,
        "cnot": sum(count * signed_encode(value, width).bit_count()
                    for value, count in images.items()),
        "explicit_table_bits": rows * len(next(iter(images))) * width,
    }


def pair_gates():
    """Structured rank-one defect XOR oracle, using two clean parity bits.

    Source bits 0..3; parity work 4,5; target coordinate i uses 6+2i,7+2i.
    """
    gates = [("cnot", 0, 4), ("cnot", 2, 4),
             ("cnot", 1, 5), ("cnot", 3, 5)]
    for i in range(4):
        gates += [("cnot", 4, 6 + 2 * i), ("cnot", 5, 6 + 2 * i)]
    gates += [("x", 5), ("toffoli", 4, 5, 7),
              ("toffoli", 4, 5, 11), ("x", 5),
              ("x", 4), ("toffoli", 4, 5, 9),
              ("toffoli", 4, 5, 13), ("x", 4)]
    gates += [("cnot", 3, 5), ("cnot", 1, 5),
              ("cnot", 2, 4), ("cnot", 0, 4)]
    return gates


def run_gates(bits, gates):
    result = list(bits)
    need(all(type(x) is int and x in (0, 1) for x in result), "bit state")
    for gate in gates:
        name, *indices = gate
        need(len(set(indices)) == len(indices), "gate aliases")
        need(all(0 <= i < len(result) for i in indices), "gate index")
        if name == "x" and len(indices) == 1:
            result[indices[0]] ^= 1
        elif name == "cnot" and len(indices) == 2:
            result[indices[1]] ^= result[indices[0]]
        elif name == "toffoli" and len(indices) == 3:
            result[indices[2]] ^= result[indices[0]] & result[indices[1]]
        else:
            raise ValueError("unknown gate")
    return result


if __name__ == "__main__":
    print(json.dumps([census(r) for r in range(1, 4)], indent=2))
