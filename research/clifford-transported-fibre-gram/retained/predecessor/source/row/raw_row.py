"""Exact computational-basis coefficients of the compiled identity decoder.

A row or column address is a 52-bit integer, with the first register in
the most significant nibble. A returned numerator has denominator 4096.
apoursh, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import islice
import json

from bell_reads import iter_reads, label_sum
from compile_row import DENOMINATOR


BITS = 52
RAW_DENOMINATOR = 4 * DENOMINATOR


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pack(nibbles):
    return sum(nibble << (4 * i) for i, nibble in enumerate(nibbles))


def split_address(address):
    if not isinstance(address, int) or not 0 <= address < 1 << BITS:
        raise ValueError("row and column must be unsigned 52-bit addresses")
    return tuple((address >> (4 * j)) & 15 for j in reversed(range(13)))


@dataclass(frozen=True)
class Bucket:
    masks: tuple[int, ...]
    numerators: tuple[int, ...]

    def signature(self, point):
        return sum(((mask & point).bit_count() % 2) << j for j, mask in enumerate(self.masks))

    def point_at(self, signature, index):
        """Unrank the free bits, then solve the parity equations by leading bit."""
        pivots = sorted((mask.bit_length()-1, j) for j, mask in enumerate(self.masks))
        pivot_bits = {bit for bit, _ in pivots}
        point = 0
        for bit in range(BITS):
            if bit not in pivot_bits:
                point |= (index & 1) << bit
                index >>= 1
        for bit, j in pivots:
            target = (signature >> j) & 1
            value = target ^ ((self.masks[j] & point).bit_count() % 2)
            point |= value << bit
        return point


def make_bucket(terms):
    masks = []
    pivots = {}
    weights = Counter()
    for frequency, weight in terms:
        address = 0
        while frequency:
            bit = frequency.bit_length()-1
            if bit not in pivots:
                pivots[bit] = len(masks)
                masks.append(frequency)
            j = pivots[bit]
            frequency ^= masks[j]
            address ^= 1 << j
        weights[address] += weight
    # Orthogonality of the independent masks makes every sign pattern attainable.
    table = [weights[i] for i in range(1 << len(masks))]
    step = 1
    while step < len(table):
        for start in range(0, len(table), 2 * step):
            for i in range(start, start + step):
                a, b = table[i], table[i+step]
                table[i], table[i+step] = a+b, a-b
        step *= 2
    return Bucket(tuple(masks), tuple(table))


@cache
def raw_plan():
    terms = defaultdict(list)
    for read in iter_reads():
        labels = read.output_labels + read.input_labels
        shifts = tuple(t >> 4 for t in labels)
        singleton = label_sum(labels)
        require(singleton < 16, "identity trace is not diagonal in this term")
        require(read.correction_i == 0, "identity term has an unexpected phase")
        frequency = pack([*(t & 15 for t in labels), singleton])
        terms[shifts].append((frequency, read.numerator))
    return {key: make_bucket(value) for key, value in sorted(terms.items())}


def coefficient_numerator(row, column):
    r, c = split_address(row), split_address(column)
    if r[-1] != c[-1]:
        return 0
    pairs = r[:-1] + c[:-1]
    shifts = tuple(a ^ b for a, b in zip(pairs[::2], pairs[1::2], strict=True))
    bucket = raw_plan().get(shifts)
    if bucket is None:
        return 0
    point = pack((*pairs[1::2], r[-1]))
    return bucket.numerators[bucket.signature(point)]


def matrix_addresses(shifts, point):
    addresses = []
    singleton = (point >> 48) & 15
    for start in (0, 6):
        address = 0
        for index in range(start, start+6):
            v = (point >> (4*index)) & 15
            address = (address << 8) | ((v ^ shifts[index]) << 4) | v
        addresses.append((address << 4) | singleton)
    return tuple(addresses)


def probe_at(index):
    """One nonzero coordinate, in deterministic bucket/signature/free-bit order."""
    if not isinstance(index, int) or index < 0:
        raise ValueError("probe index must be a nonnegative integer")
    for shifts, bucket in raw_plan().items():
        size = 1 << (BITS-len(bucket.masks))
        for signature, numerator in enumerate(bucket.numerators):
            if numerator != 0:
                if index < size:
                    point = bucket.point_at(signature, index ^ (index >> 1))
                    row, col = matrix_addresses(shifts, point)
                    return row, col, numerator
                index -= size
    raise ValueError("probe index outside the nonzero support")


def cell_geometry(shifts, bucket):
    def address(signature, index):
        row, column = matrix_addresses(shifts, bucket.point_at(signature, index))
        return (row << BITS) | column

    origin = address(0, 0)
    directions = [origin ^ address(0, 1 << j) for j in range(BITS - len(bucket.masks))]
    return address, directions


def iter_probes():
    """Stream the exact nonzero support of the identity row in probe_at order."""
    for shifts, bucket in raw_plan().items():
        address, directions = cell_geometry(shifts, bucket)
        size = 1 << len(directions)
        for signature, numerator in enumerate(bucket.numerators):
            if not numerator:
                continue
            pointer = address(signature, 0)
            for i in range(size):
                row, col = divmod(pointer, 1 << BITS)
                yield row, col, numerator
                if i + 1 < size:
                    # Consecutive reflected Gray words flip this one free bit.
                    delta = i + 1
                    pointer ^= directions[(delta & -delta).bit_length() - 1]


def first_last_addresses():
    """Extrema of the nonzero row on a row-major tape, over affine Walsh cells."""
    first, last = 1 << (2*BITS), -1
    for shifts, bucket in raw_plan().items():
        address, generators = cell_geometry(shifts, bucket)
        pivots = {}
        for v in generators:
            while v:
                bit = v.bit_length() - 1
                if bit not in pivots:
                    pivots[bit] = v
                    break
                v ^= pivots[bit]
        require(len(pivots) == BITS - len(bucket.masks), "address map lost a free bit")
        directions = [pivots[bit] for bit in sorted(pivots, reverse=True)]
        for i, n in enumerate(bucket.numerators):
            if not n:
                continue
            lo = hi = address(i, 0)
            for direction in directions:
                lo = min(lo, lo ^ direction)
                hi = max(hi, hi ^ direction)
            first, last = min(first, lo), max(last, hi)
    return first, last


def check_diagonal_columns():
    # For U=Z^z, the raw column is supported on equal row and column
    # addresses. There r=s for every pair, leaving 24 pair bits and one
    # free singleton. Push these free bits through the parity equations.
    outputs = [0] * 16
    for shifts, bucket in raw_plan().items():
        require(shifts[:6] == shifts[6:], "diagonal fixture shift layout")
        image = {0}
        for bit in range(24):
            basis_point = (1 << bit) | (1 << (bit+24))
            character = bucket.signature(basis_point)
            image |= {s ^ character for s in image}
        multiplicity = 2**24 // len(image)
        shift_sum = label_sum(shifts[:6])
        for singleton in range(16):
            offset = bucket.signature(singleton << 48)
            total = sum(bucket.numerators[s ^ offset] for s in image) * multiplicity
            for z in range(16):
                sign = (-1) ** (((shift_sum ^ singleton) & z).bit_count() % 2)
                outputs[z] += sign * total
    require(outputs == [RAW_DENOMINATOR * 4**13] + [0]*15,
            "normalized diagonal Clifford recovery from raw address weights")


def check():
    counts = Counter()
    cells = 0
    checked = 0
    plan = raw_plan()
    for shifts, bucket in plan.items():
        size = 1 << (BITS - len(bucket.masks))
        cells += len(bucket.numerators)
        for signature, n in enumerate(bucket.numerators):
            counts[n] += size
            for index in (0, size-1):
                point = bucket.point_at(signature, index)
                require(bucket.signature(point) == signature, "unranking a Walsh class")
                require(coefficient_numerator(*matrix_addresses(shifts, point)) == n,
                        "raw address lookup mismatch")
                checked += 1
    expected = {0: 77827831060496384, 128: 10133099161583616, -128: 10133099161583616,
                512: 492581209243648, -512: 492581209243648}
    require(counts == expected and len(plan) == 22, "raw coefficient multiplicities")
    support = sum(count for n, count in counts.items() if n)
    require(support == 151 * 2**47, "raw query bill")
    require(sum(n*n*count for n,count in counts.items()) == RAW_DENOMINATOR**2 * 2**45,
            "computational and Bell row norms disagree")
    for index in (0, 1, support//2, support-2, support-1):
        row, col, n = probe_at(index)
        require(n == coefficient_numerator(row, col) and n != 0, "nonzero-support unranking")
    require(list(islice(iter_probes(), 64)) == [probe_at(i) for i in range(64)],
            "stream order disagrees with indexed access")
    check_diagonal_columns()
    first, last = first_last_addresses()
    require(first == 0x00000000000210000000000021 and first + last == (1 << (2*BITS)) - 1,
            "row-major tape extrema")
    for address in (first, last):
        require(coefficient_numerator(*divmod(address, 1 << BITS)) != 0, "inactive tape endpoint")
    print(f"PASS_RAW_IDENTITY_ROW buckets={len(plan)} Walsh_cells={cells}"
          f" boundary_lookups={checked} nonzero_coordinates={support} squared_norm=2^45"
          f" first={first:026x} last={last:026x}")


def integer(text):
    return int(text, 0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--entry", type=integer, nargs=2, metavar=("ROW", "COLUMN"))
    action.add_argument("--probe-index", type=integer,
                        help="unrank one nonzero coordinate, starting at zero")
    args = parser.parse_args()
    if args.entry is not None:
        row, col = args.entry
        numerator = coefficient_numerator(row, col)
    elif args.probe_index is not None:
        row, col, numerator = probe_at(args.probe_index)
    else:
        check()
        return
    print(json.dumps({"row": row, "column": col, "numerator": numerator,
                      "denominator": RAW_DENOMINATOR}))


if __name__ == "__main__":
    main()
