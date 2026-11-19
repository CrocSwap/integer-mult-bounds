"""All 256 Pauli outputs of the width-13 identity symplectic fibre, exactly."""
import argparse
from fractions import Fraction
from functools import cache
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "predecessor"))
from contract import BinaryMap, Q, Spectrum, apply, iter_reads, label_sum, pack, parity, polar, split_address, transpose

MASK48 = (1 << 48) - 1


def separate(address):
    rows, cols = map(split_address, divmod(address, 1 << 52))
    pairs = rows[:-1] + cols[:-1]
    shifts = pack([a ^ b for a, b in zip(pairs[::2], pairs[1::2], strict=True)])
    singleton = rows[-1] | (cols[-1] << 4)
    return (shifts << 8) | singleton, pack(pairs[1::2])


@cache
def plan():
    records = []
    for read in iter_reads():
        labels = read.output_labels + read.input_labels
        fixed = pack([t >> 4 for t in labels])
        wave = pack([t & 15 for t in labels])
        out, inp = label_sum(read.output_labels), label_sum(read.input_labels)
        move = (out >> 4) | ((inp >> 4) << 4)
        sign = (out & 15) | ((inp & 15) << 4)
        Q.need(read.correction_i == 0 and out >> 4 == inp >> 4, "Identity-fibre conventions")
        records.append(((wave << 56) | (fixed << 8), move, sign, read.numerator))
    return tuple(records)


class Section(BinaryMap):
    """Linear reduction, including a canonical remainder for inconsistent right sides."""
    def split(self, word):
        witness = 0
        for bit, (pivot, preimage) in self.descending:
            if word >> bit & 1:
                word ^= pivot
                witness ^= preimage
        return word, witness

    def __init__(self, columns):
        super().__init__(columns)
        self.descending = sorted(self.pivots.items(), reverse=True)


class PartialWalsh:
    """Return affine support equations and a quadratic phase on all Bell/singleton bits."""
    def __init__(self, state):
        n, offset, cols, terms, real, imag, denominator = state
        Q.need(n == 104, "This decoder consumes 104-bit charts")
        self.offset, self.free_offset = separate(offset)
        parts = [separate(c) for c in cols]
        self.fixed = Section(f for f, _ in parts)
        self.free = [v for _, v in parts]
        self.phase = dict(terms)
        kernel = self.fixed.kernel
        restricted = Q.substitute(self.phase, [transpose(kernel, 1 << j) << 1 for j in range(len(cols))])
        restricted.pop(0, None)
        spectrum = Spectrum(len(kernel), restricted)
        self.spectrum_map = Section(polar(len(kernel), restricted))
        self.restricted = restricted
        self.anchor = spectrum.origin
        self.scalar = Q.multiply((real, imag), spectrum.value)
        self.denominator = denominator + 12  # numerator / 4096 after the final trace
        self.free_kernel = [apply(self.free, k) for k in kernel]
        polar_columns = polar(len(cols), self.phase)
        self.twist_columns = [transpose(kernel, col) for col in polar_columns]

    def slice(self, word):
        fixed, wave = word & ((1 << 56)-1), word >> 56
        rem, t = self.fixed.split(fixed ^ self.offset)
        free = self.free_offset ^ apply(self.free, t)
        frequency = apply(self.twist_columns, t) ^ transpose(self.free_kernel, wave)
        residual, u = self.spectrum_map.split(frequency ^ self.anchor)
        syndrome = rem | (residual << 56)
        phase = (Q.value(self.phase, t) + 2*parity(wave & free)
                 - Q.value(self.restricted, u) + 2*parity(self.anchor & u)) % 4
        return syndrome, phase


def walsh(values):
    """Unnormalized binary Walsh transform in place, on real Gaussian components."""
    stride = 1
    while stride < len(values):
        for start in range(0, len(values), 2*stride):
            for i in range(start, start + stride):
                a, b = values[i], values[i + stride]
                values[i], values[i + stride] = a + b, a - b
        stride *= 2


class SingletonBasis:
    def __init__(self, transform):
        self.transform = transform
        zero_syndrome, zero_phase = transform.slice(0)
        singletons = [transform.slice(1 << i) for i in range(104)]
        self.affine = Section(s ^ zero_syndrome for s, _ in singletons[:8])
        self.support = self.affine.kernel
        self.cosets = Section(self.support)
        # The extension of the phase off its support is a quadratic polynomial.
        # Its polar columns restricted to the eight singleton directions identify
        # each read's modulating sign without a separate phase fit at each output.
        self.twists = []
        for h in self.support:
            twist = 0
            slope = (transform.slice(h)[1] - zero_phase) % 4
            for i, (_, base) in enumerate(singletons):
                delta = (transform.slice((1 << i) ^ h)[1] - base - slope) % 4
                Q.need(delta in (0, 2), "Non-quadratic phase derivative")
                twist |= (delta // 2) << i
            self.twists.append(twist)
        self.points = [apply(self.support, u) for u in range(1 << len(self.support))]
        self.chirp = [(transform.slice(v)[1] - zero_phase) % 4 for v in self.points]

    def locate(self, labels, move, sign):
        syndrome, _ = self.transform.slice(labels)
        remainder, witness = self.affine.split(syndrome)
        if remainder:
            return None
        representative, _ = self.cosets.split(witness ^ move)
        raw_point = representative ^ move
        word = labels | raw_point
        frequency = transpose(self.twists, word) ^ transpose(self.support, sign)
        phase = (self.transform.slice(word)[1] + 2*parity(raw_point & sign)) % 4
        return representative, frequency, phase


def fibre(state):
    """Return the linear decoder as pairs of Fractions at index 16*x+z."""
    transform = PartialWalsh(state)
    basis = SingletonBasis(transform)
    size = len(basis.points)
    bins = {s: ([0]*size, [0]*size) for s in range(256) if basis.cosets.split(s)[0] == s}
    supported = 0
    for labels, move, sign, weight in plan():
        hit = basis.locate(labels, move, sign)
        if hit is not None:
            s, freq, phase = hit
            bins[s][phase % 2][freq] += weight if phase < 2 else -weight
            supported += 1
    matrices = [[0]*256, [0]*256]
    for s, (real, imag) in bins.items():
        walsh(real)
        walsh(imag)
        for i, v in enumerate(basis.points):
            a, b = Q.multiply_i((real[i], imag[i]), basis.chirp[i])
            matrices[0][s ^ v], matrices[1][s ^ v] = a, b
    outputs = []
    for x in range(16):
        real, imag = [[m[(b ^ x) | (b << 4)] for b in range(16)] for m in matrices]
        walsh(real)
        walsh(imag)
        for item in zip(real, imag, strict=True):
            value = Q.multiply(transform.scalar, item)
            outputs.append(tuple(Fraction(a, 1 << transform.denominator) for a in value))
    stats = dict(gauss=1, gauss_variables=len(transform.fixed.kernel),
                 singleton_dimension=len(basis.support), supported_terms=supported,
                 accumulation_updates=supported, walsh_adds=256*(len(basis.support)+4))
    return outputs, stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON with a #5704 circuit and optional initial address")
    data = parser.parse_args().input.read_bytes()
    request = json.loads(data)
    state = Q.signature(104, request["circuit"], initial=request.get("initial", 0))
    values, stats = fibre(state)
    print(json.dumps({"input_bytes":len(data), "outputs":[[str(a),str(b)] for a,b in values], **stats}))
