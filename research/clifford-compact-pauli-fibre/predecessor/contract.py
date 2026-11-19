"""Contract #7800's identity row with a #5704 affine-quadratic observation.

apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from functools import cache
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
for record in json.loads((HERE / "RETAINED.json").read_text()):
    if sha256((HERE / record["local"]).read_bytes()).hexdigest() != record["sha256"]:
        raise ValueError("Changed retained source: " + record["local"])
sys.path[:0] = [str(HERE / "source" / "engine"), str(HERE / "source" / "row")]
from contractions import Q, gauss, solution
from raw_row import RAW_DENOMINATOR, iter_reads, label_sum, pack, split_address


def parity(bits):
    return bits.bit_count() & 1


def transpose(columns, vector):
    return sum(parity(column & vector) << j for j, column in enumerate(columns))


def apply(columns, vector):
    out = 0
    for j in Q.bits(vector):
        out ^= columns[j]
    return out


class BinaryMap:
    """One elimination: a kernel basis and a right inverse on the image."""
    def __init__(self, columns):
        self.pivots = {}
        self.kernel = []
        for j, column in enumerate(columns):
            word, witness = column, 1 << j
            while word:
                bit = word.bit_length() - 1
                if bit not in self.pivots:
                    self.pivots[bit] = (word, witness)
                    break
                pivot, preimage = self.pivots[bit]
                word ^= pivot
                witness ^= preimage
            if not word:
                self.kernel.append(witness)

    def preimage(self, word):
        witness = 0
        while word:
            pivot = self.pivots.get(word.bit_length() - 1)
            if pivot is None:
                return None
            word ^= pivot[0]
            witness ^= pivot[1]
        return witness


def polar(dimension, phase):
    columns = [0] * dimension
    for mask, coefficient in phase.items():
        if mask.bit_count() == 2:
            a, b = Q.bits(mask)
            columns[a] ^= 1 << b
            columns[b] ^= 1 << a
        elif mask and coefficient & 1:
            columns[mask.bit_length() - 1] ^= mask
    return columns


class Spectrum:
    """Return a Fourier coefficient as a rotation of one exact Gauss sum."""
    def __init__(self, dimension, phase):
        self.phase = phase
        self.map = BinaryMap(polar(dimension, phase))
        equations = []
        for r in self.map.kernel:
            q = Q.value(phase, r)
            Q.need(q % 2 == 0, "An element of the radical has even phase")
            equations.append((r, q // 2))
        _, forms = solution(dimension, equations)
        self.origin = sum((form & 1) << j for j, form in enumerate(forms))
        twisted = dict(phase)
        Q.affine(twisted, self.origin << 1, 2)
        self.value = gauss(dimension, twisted)
        Q.need(self.value != (0, 0), "Nonzero Fourier anchor")

    def rotation(self, frequency):
        u = self.map.preimage(self.origin ^ frequency)
        if u is None:
            return None
        return (2 * parity(self.origin & u) - Q.value(self.phase, u)) % 4


def address_parts(address):
    """Linear map from raw 104 bits to (52 shift bits, 52 free bits)."""
    row, col = divmod(address, 1 << 52)
    r, c = split_address(row), split_address(col)
    pairs = r[:-1] + c[:-1]
    shifts = [a ^ b for a, b in zip(pairs[::2], pairs[1::2], strict=True)]
    return pack([*shifts, r[-1] ^ c[-1]]), pack([*pairs[1::2], r[-1]])


@cache
def read_plan():
    plan = defaultdict(list)
    for read in iter_reads():
        labels = read.output_labels + read.input_labels
        singleton = label_sum(labels)
        Q.need(singleton < 16 and read.correction_i == 0, "Identity trace convention")
        shift = pack([t >> 4 for t in labels])
        frequency = pack([*(t & 15 for t in labels), singleton])
        plan[shift].append((frequency, read.numerator))
    return {s: tuple(terms) for s, terms in sorted(plan.items())}


def contract(state, plan=None, denominator=RAW_DENOMINATOR):
    """Linear (unconjugated) observation contraction on a signature() output.

    A plan maps a packed shift to (frequency, signed integer weight) pairs.
    Each weight has the stated common denominator.
    """
    n, offset, cols, terms, real, imag, exponent = state
    Q.need(n == 104, "This row consumes a 104-bit state")
    if plan is None:
        plan = read_plan()
    shift0, point0 = address_parts(offset)
    parts = [address_parts(c) for c in cols]
    support = BinaryMap(s for s, _ in parts)
    points = [v for _, v in parts]
    intersections = []
    for shift, table in plan.items():
        witness = support.preimage(shift ^ shift0)
        if witness is not None:
            intersections.append((witness, table))
    counts = Counter(buckets=len(intersections), dimension=len(support.kernel), gauss=0)
    if not intersections:
        return (Fraction(0), Fraction(0)), dict(counts)

    kernel = support.kernel
    phase = dict(terms)
    restricted = Q.substitute(phase, [transpose(kernel, 1 << j) << 1 for j in range(len(cols))])
    restricted.pop(0, None)
    spectrum = Spectrum(len(kernel), restricted)
    counts["gauss"] = 1
    polar_cols = polar(len(cols), phase)
    point_directions = [apply(points, k) for k in kernel]
    total = [0, 0]
    for witness, table in intersections:
        point = point0 ^ apply(points, witness)
        twist = transpose(kernel, apply(polar_cols, witness))
        constant = Q.value(phase, witness)
        for frequency, weight in table:
            counts["terms"] += 1
            exponent_i = spectrum.rotation(twist ^ transpose(point_directions, frequency))
            if exponent_i is None:
                continue
            counts["supported"] += 1
            angle = (constant + 2 * parity(point & frequency) + exponent_i) % 4
            total[angle % 2] += weight if angle < 2 else -weight
    numerator = Q.multiply((real, imag), Q.multiply(spectrum.value, total))
    return tuple(Fraction(x, denominator << exponent) for x in numerator), dict(counts)


def one_cell(state, shifts, masks, signature, numerator):
    """Contract the actual weight numerator/4096 on a single Walsh cell."""
    frequencies = [(apply(masks, w), numerator * (-1)**parity(w & signature))
                   for w in range(1 << len(masks))]
    return contract(state, {pack(shifts): frequencies}, RAW_DENOMINATOR << len(masks))


def main():
    """Evaluate a literal #5704 circuit on one computational basis input."""
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON with circuit and optional initial address")
    args = parser.parse_args()
    data = args.input.read_bytes()
    request = json.loads(data)
    counters = {}
    state = Q.signature(104, request["circuit"], initial=request.get("initial", 0), counters=counters)
    result, execution = contract(state)
    print(json.dumps({"real": str(result[0]), "imag": str(result[1]), "input_bytes": len(data),
                      "producer": counters, "consumer": execution}, sort_keys=True))


if __name__ == "__main__":
    main()
