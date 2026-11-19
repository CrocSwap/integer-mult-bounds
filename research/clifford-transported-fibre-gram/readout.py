"""Decode specified symplectic fibres of one compact chart in the compiled Bell basis."""
import argparse
from fractions import Fraction
from functools import cache
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "retained"))
from fibre import PartialWalsh, Q, SingletonBasis, iter_reads, label_sum, pack, walsh
from bell_reads import decompose, step
from compile_row import IDENTITY, is_symplectic

ZERO = (0, 0)


@cache
def base_reads():
    return tuple(iter_reads())


@cache
def target_axes(target):
    if not is_symplectic(target):
        raise ValueError("Expected eight columns of a binary symplectic matrix")
    return decompose(target)


def transports(target):
    """One 256-label table per action, including both absolute phase exponents."""
    axes = target_axes(target)
    def follow(label, bell):
        phase = 0
        for axis in axes:
            label, increment = step(axis, label, bell)
            phase += increment
        return label, phase % 4
    return [[follow(i, action) for i in range(256)] for action in (False, True)]


def translated_reads(target):
    ordinary, bell = transports(target)
    for read in base_reads():
        lifted = [bell[t] for t in read.output_labels]
        outputs = tuple(t for t, _ in lifted)
        _, gamma = ordinary[label_sum(read.output_labels)]
        transport = (sum(p for _, p in lifted) - gamma) % 4
        yield read._replace(output_labels=outputs, correction_i=(read.correction_i - transport) % 4)


def rotate_right(matrix, target, adjoint):
    """Right-multiply by the canonical lift or adjoint. Return numerator and power of two."""
    axes = target_axes(tuple(target))
    sign = -1 if adjoint else 1
    for axis in (axes if adjoint else reversed(axes)):
        x, z = divmod(axis, 16)
        exponent = ((x & z).bit_count() & 1) + sign
        result = [ZERO]*256
        for c in range(16):
            phase = (exponent + 2*(z & c).bit_count()) % 4
            for r in range(16):
                j = r + (c << 4)
                a, b = matrix[j]
                t, u = Q.multiply_i(matrix[r + ((c ^ x) << 4)], phase)
                v, w = a+t, b+u
                result[j] = v-sign*w, w+sign*v
        matrix = result
    return matrix, len(axes)


def decode_paulis(matrix):
    """Numerators of all trace pairings with X^x Z^z (without the 1/16)."""
    outputs = []
    for x in range(16):
        diag = [matrix[(c ^ x) | (c << 4)] for c in range(16)]
        a, b = map(list, zip(*diag))
        walsh(a)
        walsh(b)
        outputs.extend(zip(a,b))
    return outputs


def synthesize_paulis(coefficients):
    """Entries of sum c_(x,z) X^x Z^z; Walsh in z is its own transpose."""
    if len(coefficients) != 256:
        raise ValueError("Expected 256 coefficient pairs")
    result = [ZERO]*256
    for x in range(16):
        left, right = map(list, zip(*coefficients[16*x:16*x+16]))
        walsh(left)
        walsh(right)
        for c, val in enumerate(zip(left, right)):
            result[(x ^ c) | (c << 4)] = val
    return result


class BatchReadout:
    """Compile the transformed observation once, independent of the target list."""
    def __init__(self, chart):
        self.transform = PartialWalsh(chart)
        self.basis = SingletonBasis(self.transform)

    def evaluate(self, target):
        target = tuple(target)
        basis = self.basis
        size = len(basis.points)
        bins = {s: ([0]*size,[0]*size) for s in range(256) if basis.cosets.split(s)[0] == s}
        hits = 0
        for read in translated_reads(target):
            labels = read.output_labels + read.input_labels
            out, inp = label_sum(read.output_labels), label_sum(read.input_labels)
            point = (pack([t & 15 for t in labels]) << 56) | (pack([t >> 4 for t in labels]) << 8)
            move = (out >> 4) | (inp & 240)
            phase_mask = (out & 15) | ((inp & 15) << 4)
            found = basis.locate(point, move, phase_mask)
            if found is not None:
                s, freq, phase = found
                phase = (phase + read.correction_i) % 4
                bins[s][phase % 2][freq] += read.numerator if phase < 2 else -read.numerator
                hits += 1
        weighted = [ZERO]*256
        for s,(real,imag) in bins.items():
            walsh(real)
            walsh(imag)
            for i,v in enumerate(basis.points):
                weighted[s ^ v] = Q.multiply_i((real[i],imag[i]), basis.chirp[i])
        gauged, power = rotate_right(weighted,target,True)
        denominator = 1 << (self.transform.denominator + power)
        coeffs = [tuple(Fraction(a,denominator) for a in Q.multiply(self.transform.scalar,entry))
                  for entry in decode_paulis(gauged)]
        return coeffs, dict(terms=4265, hits=hits, lift_steps=power,
                            walsh_additions=256*(len(basis.support)+4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="JSON with circuit, optional initial address, and targets")
    args = parser.parse_args()
    data = json.loads(args.input.read_bytes())
    compiled = BatchReadout(Q.signature(104,data["circuit"],initial=data.get("initial",0)))
    outputs = []
    for t in data["targets"]:
        alphas, stats = compiled.evaluate(t)
        outputs.append({"target":t,"coefficients":[[str(a),str(b)] for a,b in alphas], **stats})
    print(json.dumps({"chart_gauss_sums":1,"outputs":outputs}))
