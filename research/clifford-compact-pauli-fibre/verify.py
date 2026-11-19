"""Cross-check public full-fibre contraction against signed dense coordinates."""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from functools import reduce
from operator import xor
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fibre import Q, apply, fibre, parity, iter_reads, label_sum
from raw_row import coefficient_numerator, matrix_addresses, probe_at, raw_plan, split_address


def require(ok, message):
    if not ok:
        raise ValueError(message)


def repeat_nibble(x):
    return x * ((2**52 - 1) // 15)


def dense_entry(row, column):
    """The full vector of integer weights at one raw address, using #7800 only."""
    x = (row ^ column) & 15
    corrected_col = column ^ repeat_nibble(x)
    n = coefficient_numerator(row, corrected_col)
    actual = split_address(column)
    t = reduce(xor, actual[:-1], 0)
    return x, actual[-1] ^ t, n


def literal(chart):
    _, offset, cols, terms, a, b, den = chart
    out = [[0, 0] for _ in range(256)]
    for param in range(1 << len(cols)):
        address = offset ^ apply(cols, param)
        x, column, n = dense_entry(*divmod(address, 1 << 52))
        if not n:
            continue
        scalar = Q.multiply_i((a*n, b*n), Q.value(dict(terms), param))
        for z in range(16):
            sign = (-1)**parity(z & column)
            for j in range(2):
                out[16*x+z][j] += scalar[j]*sign
    return [tuple(Fraction(v, 4096 << den) for v in val) for val in out]


def support_and_literal():
    rng = Random(7801)
    count = 0
    hits = set()
    total = 0
    for shifts, bucket in raw_plan().items():
        total += sum(bool(n) for n in bucket.numerators) << (52-len(bucket.masks))
        # Mix independent pair/singleton directions, a second shift, complex
        # phases and a translation into each of the 16 Pauli X sectors.
        sig = next(i for i, n in enumerate(bucket.numerators) if n)
        anchors = [bucket.point_at(sig, j) for j in (0, 1, 2, 4)]
        raw = [(r << 52) | c for r,c in (matrix_addresses(shifts, p) for p in anchors)]
        offset = raw[0] ^ repeat_nibble(count % 16)
        dirs = [v ^ raw[0] for v in raw[1:]] + [1, 2, 2 << 52, 1 << 27]
        circuit = [('C', v, rng.choice((-1,1))) for v in dirs] + [('phase', count % 4)]
        chart = Q.signature(104, circuit, initial=offset)
        result, stats = fibre(chart)
        require(result == literal(chart), "Off-image literal contraction in every Pauli component")
        require(any(q != (0,0) for q in result), "Degenerate fixture")
        hits.add(stats['singleton_dimension'])
        count += 1
    require(total == 151 * 2**47 and total * 16 == 340021771866472448, "Dense support union")
    return count, hits


def literal_bell_weights():
    groups = defaultdict(list)
    for read in iter_reads():
        labels = read.output_labels + read.input_labels
        groups[tuple(q >> 4 for q in labels)].append(read)
    checked = 0
    for shifts, bucket in raw_plan().items():
        sig = next(i for i, n in enumerate(bucket.numerators) if n)
        for x in range(16):
            row, diag = matrix_addresses(shifts, bucket.point_at(sig, 17*x))
            col = diag ^ repeat_nibble(x)
            a, b = row & 15, col & 15
            frees = split_address(row)[1:12:2] + split_address(col)[1:12:2]
            outputs = [0]*16
            for read in groups[shifts]:
                wo, wi = label_sum(read.output_labels), label_sum(read.input_labels)
                # Trace against the Pauli matrix at *corrected* row and column.
                column = b ^ (wi >> 4)
                require((a ^ (wo >> 4) ^ column) == x, "Singleton trace diagonal")
                sign = parity((wo & a) ^ (wi & b))
                labels = read.output_labels + read.input_labels
                sign ^= reduce(xor, (parity(f & lab) for f, lab in zip(frees, labels, strict=True)), 0)
                for z in range(16):
                    outputs[z] += read.numerator * (-1)**(sign ^ parity(z & column))
            xx, cc, n = dense_entry(row, col)
            require(xx == x and n and outputs == [n*(-1)**parity(z & cc) for z in range(16)],
                    "Direct Bell corrections disagree with translated scalar weights")
            checked += 16
    return checked


def all_slice_ranks():
    r, c, _ = probe_at(0)
    offset = (r << 52) | c
    for e in range(9):
        gates = [('C', 1 << (i if i < 4 else 52+i-4), (-1)**i) for i in range(e)]
        state = Q.signature(104, gates, initial=offset)
        out, stats = fibre(state)
        require(stats['singleton_dimension'] == e and out == literal(state),
                "Singleton Walsh rank or a complex component changed")
    out, stats = fibre(Q.signature(104, []))
    require(not stats['supported_terms'] and out == [(0,0)]*256, "Empty Bell intersection")


def pauli_columns():
    for x,z,phase in [(0,0,0),(1,2,1),(7,7,2),(15,3,3),(14,15,0),(3,13,1)]:
        # The X^x Z^z columns are assembled directly in computational coordinates.
        shift = repeat_nibble(x) << 52
        phases = tuple((1 << j,2) for j in Q.bits(repeat_nibble(z)))
        scalar = Q.multiply_i((1,0), phase)
        state = (104,shift,tuple((1<<j)|(1<<(j+52)) for j in range(52)),
                 phases,*scalar,26)
        result,_ = fibre(state)
        expected = [(0,0)]*256
        expected[16*x+z] = scalar
        require(result == expected, "Pauli convention, scaling or phase lost")
    # Controlled-Z changes symplectic action. Its exact tensor is outside this fibre.
    cz = tuple(((1<<(4*j)) | (2<<(4*j)),2) for j in range(13))
    state = (104,0,tuple((1<<j)|(1<<(j+52)) for j in range(52)),cz,1,0,26)
    require(all(x == (0,0) for x in fibre(state)[0]), "Unexpected coefficient from another fibre")


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    for record in json.loads((root/'SOURCE-PINS.json').read_text())['predecessor_files']:
        require(sha256((root/record['local']).read_bytes()).hexdigest() == record['sha256'],
                "Pinned predecessor content changed")
    n, dims = support_and_literal()
    all_slice_ranks()
    pauli_columns()
    print("PASS", literal_bell_weights(), "entries checked by literal Bell correction and Pauli trace")
    print("PASS", n, "weighted shift fixtures against all 256 literal dense outputs; singleton ranks",sorted(dims))
    print("PASS six one-hot phase-sensitive columns and a different symplectic fibre")
    print("PASS 151*2^51 exact dense probes across sixteen disjoint translations")
