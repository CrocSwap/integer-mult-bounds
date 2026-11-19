"""Emit the phase-corrected Bell measurements for the compiled Clifford row.

Use --emit for the identity fibre in order. Labels have four low Z bits
and four high X bits. apoursh with substantial OpenAI Codex assistance.
Apache-2.0. Phase correction is from PR7799.
"""
import argparse
from functools import cache
import json
from typing import NamedTuple

from compile_row import DENOMINATOR, IDENTITY, SEED, apply, iter_terms, pairing


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() % 2


def q0(v):
    return parity((v >> 4) & v)


def transvection(axis, vector):
    return vector ^ (axis if pairing(axis, vector) else 0)


def decompose(matrix):
    """Write a symplectic map as a sequence of transvections in application order."""
    columns = list(matrix)
    corrections = []
    for i, target in enumerate(IDENTITY):
        source = columns[i]
        if source == target:
            continue
        if pairing(source, target):
            axes = (source ^ target,)
        else:
            middle = next(v for v in range(256)
                          if pairing(v, source) and pairing(v, target)
                          and all(pairing(source ^ v, fixed) == 0 for fixed in IDENTITY[:i]))
            axes = (source ^ middle, middle ^ target)
        for axis in axes:
            columns = [transvection(axis, v) for v in columns]
            corrections.append(axis)
    require(tuple(columns) == IDENTITY, "transvection reduction failed")
    return tuple(reversed(corrections))


def step(axis, v, bell):
    """Phase exponent modulo four of a transvection on one unphased Weyl label."""
    out = transvection(axis, v)
    exponent = 0
    if out != v:
        exponent = 1 + q0(axis) + 2 * parity((axis & 15) & (v >> 4))
    if bell:
        if q0(axis):
            exponent += 1
        else:
            exponent += 2 + 2 * parity((out & 15) & (axis >> 4))
            out ^= axis
    return out, exponent % 4


def label_sum(labels):
    total = 0
    for label in labels:
        total ^= label
    return total


@cache
def transported_seed(matrix):
    """Return the six output labels and the seed's transport phase exponent."""
    labels = list(SEED)
    weight = label_sum(SEED)
    phase = 0
    for axis in decompose(matrix):
        next_weight, gamma = step(axis, weight, False)
        values = [step(axis, label, True) for label in labels]
        labels = [value for value, _ in values]
        phase += sum(theta for _, theta in values) - gamma
        weight = next_weight
    # Independent affine check. q(Sv+b)=q(v) fixes the offset b uniquely.
    offset = labels[0]
    require(all(q0(apply(matrix, u) ^ offset) == q0(u) for u in (0, *IDENTITY)),
            "Bell offset violates transpose parity")
    require(all(label == apply(matrix, v) ^ offset for v, label in zip(SEED, labels, strict=True))
            and weight == label_sum(labels), "misordered symplectic transport")
    return tuple(labels), phase % 4


class Read(NamedTuple):
    numerator: int
    input_labels: tuple[int, ...]
    output_labels: tuple[int, ...]
    correction_i: int


def iter_reads(target=IDENTITY):
    """Weight is numerator/DENOMINATOR. Multiply the corrected singleton by i^correction_i."""
    for term in iter_terms(target):
        i, phase_i = transported_seed(term.input_map)
        j, phase_j = transported_seed(term.output_map)
        yield Read(term.numerator, i, j, (phase_i - phase_j) % 4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit one JSON object per identity-fibre read")
    args = parser.parse_args()
    pairs = set()
    for read in iter_reads():
        pair = read.input_labels, read.output_labels
        require(pair not in pairs, "repeated literal Bell address")
        pairs.add(pair)
        if args.emit:
            print(json.dumps(dict(read._asdict(), denominator=DENOMINATOR)))
    if not args.emit:
        print(f"PASS_BELL_READS distinct_pairs={len(pairs)}")


if __name__ == "__main__":
    main()
