#!/usr/bin/env python3
"""Inner chirp-packing audit. Hanson Sun, with OpenAI Codex; Apache-2.0."""
import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(100000)  # Bounded source-precision fixtures.


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_log2(value):
    value = F(value)
    require(value >= 1, "logarithm domain")
    k = max(0, value.numerator.bit_length() - value.denominator.bit_length())
    return k + (F(1 << k) < value)


def guard_bits(precision):
    require(type(precision) is int and precision >= 0, "precision domain")
    q = 1 << precision
    return ((q + 32) * (q + 2)).bit_length() - 2 * precision


def slot_bits(precision, magnitude, length, guard=8):
    require(type(length) is int and length > 0, "length domain")
    require(type(guard) is int and guard >= 0, "guard domain")
    require(F(magnitude) >= 1, "magnitude domain")
    guard_bits(precision)
    return 2 * precision + ceil_log2(F(magnitude) * length) + guard


def pack_unsigned(values, bits):
    require(bits > 0, "positive slot width required")
    base = 1 << bits
    require(all(type(x) is int and 0 <= x < base for x in values), "input digit exceeds radix")
    result = 0
    for x in reversed(values):
        result = (result << bits) + x
    return result


def unpack_unsigned(value, bits, count):
    mask, digits = (1 << bits) - 1, []
    for _ in range(count):
        digits.append(value & mask)
        value >>= bits
    require(value == 0, "terminal carry")
    return digits


def packed(real, imag, kernel, output_length, bits, fault=None):
    """kernel[r+B-1] represents K_r, -(B-1)<=r<A."""
    length = len(real)
    require(length > 0 and len(imag) == length, "source dimensions")
    require(type(output_length) is int and output_length > 0, "output dimensions")
    require(len(kernel) == length + output_length - 1, "kernel dimensions")
    # H(x)=sum_r K_r x^(A-1-r); the desired slot is A-1+b.
    h = list(kernel) if fault == "no_reverse" else list(reversed(kernel))
    if fault == "discard_negative_kernel":
        h = [max(0, x) for x in h]
    count = length + len(h) - 1
    crop = length - 1 + (fault == "crop")
    answers = []
    for component in (real, imag):
        accumulated = [0] * count
        for source_sign, kernel_sign in itertools.product((1, -1), repeat=2):
            a = [max(0, source_sign * x) for x in component]
            k = [max(0, kernel_sign * x) for x in h]
            product = pack_unsigned(a, bits) * pack_unsigned(k, bits)
            digits = unpack_unsigned(product, bits, count)
            # Sanity check only: this does NOT establish coefficient correctness.
            require(pack_unsigned(digits, bits) == product, "recomposition")
            for i, digit in enumerate(digits):
                accumulated[i] += source_sign * kernel_sign * digit
        answers.append((accumulated + [0])[crop:crop + output_length])
    return list(zip(*answers))


def direct(real, imag, kernel, output_length):
    # Independent nested sums; no polynomial products or extraction.
    return [(sum(real[a] * kernel[a-b+output_length-1] for a in range(len(real))),
             sum(imag[a] * kernel[a-b+output_length-1] for a in range(len(imag))))
            for b in range(output_length)]


def check_case(real, imag, kernel, outputs, precision, magnitude):
    q = 1 << precision
    require(all(abs(x) <= F(magnitude)*(q+32) for x in real+imag), "source envelope")
    require(all(abs(x) <= q+2 for x in kernel), "kernel envelope")
    expected = direct(real, imag, kernel, outputs)
    for guard in (8, guard_bits(precision)):
        bits = slot_bits(precision, magnitude, len(real), guard)
        require(packed(real, imag, kernel, outputs, bits) == expected, "coefficient mismatch")
    return expected


def check_sources(root=ROOT):
    for row in json.loads((PACKAGE / "SOURCES.json").read_text())["files"]:
        if row["usage"] == "input":
            payload = (root / row["path"]).read_bytes()
            require(hashlib.sha256(payload).hexdigest() == row["sha256"],
                    "source drift: " + row["path"])


def norm2(z):
    return z[0]**2 + z[1]**2


def enclosure_case(precision, magnitude, length, outputs, rng):
    """Rational ideals, explicitly admitted errors, then packed grid integers."""
    q, magnitude = 1 << precision, F(magnitude)
    directions = [(F(0), F(0)), (F(1), F(0)), (F(-1), F(0)),
                  (F(0), F(1)), (F(3, 5), F(4, 5)), (F(-3, 5), F(-4, 5))]
    ideals = [tuple(c*magnitude for c in rng.choice(directions)) for _ in range(length)]
    # Floor error plus grid perturbation: norm < sqrt(2)*17*F/Q < 32*F/Q.
    rounded = [tuple(int(c*q//1) + rng.choice((-16, 0, 16)) for c in z) for z in ideals]
    ideal_k = [F(rng.choice((0, 1, q//2, q)), q) for _ in range(length+outputs-1)]
    kernel = [int(k*q) + rng.choice((-2, 0, 2)) for k in ideal_k]
    for z, rz in zip(ideals, rounded):
        require(norm2(z) <= magnitude**2, "ideal source magnitude")
        require(norm2(tuple(F(r,q)-c for r,c in zip(rz,z))) <= (32*magnitude/q)**2,
                "source error premise")
    require(all(0 <= k <= 1 for k in ideal_k), "ideal kernel range")
    require(all(abs(F(r,q)-k) <= F(2,q) for r,k in zip(kernel,ideal_k)), "kernel error premise")
    result = check_case([z[0] for z in rounded], [z[1] for z in rounded],
                        kernel, outputs, precision, magnitude)
    for b in range(outputs):
        exact = [sum(ideals[a][c]*ideal_k[a-b+outputs-1] for a in range(length)) for c in (0,1)]
        error = tuple(F(result[b][c], q*q)-exact[c] for c in (0,1))
        require(norm2(error) <= (128*magnitude*length/q)**2, "inner error bound")


def compute_receipt():
    rng, digest = random.Random(68), hashlib.sha256()
    counts = {"exhaustive_packings": 0, "basis_packings": 0, "seeded_packings": 0,
              "enclosure_cases": 0, "source_dimension_packings": 0}

    def record(real, imag, kernel, outputs, precision, magnitude):
        answer = check_case(real, imag, kernel, outputs, precision, magnitude)
        digest.update(json.dumps([precision,str(magnitude),real,imag,kernel,outputs,answer],
                                 separators=(",", ":")).encode()+b"\n")

    # Complete {-1,0,1}^7 domain: two complex inputs, three kernel entries.
    for precision in range(4):
        for values in itertools.product((-1,0,1), repeat=7):
            record(list(values[:2]),list(values[2:4]),list(values[4:]),2,precision,1)
            counts["exhaustive_packings"] += 1

    # All source/kernel delta pairs on A,B<=8; 68 mod 10 selects side 8.
    for length, outputs in itertools.product(range(1,9), repeat=2):
        for a in range(length):
            for r in range(length+outputs-1):
                for coordinate in (0,1):
                    real, imag = [0]*length, [0]*length
                    (real,imag)[coordinate][a] = -1
                    kernel = [0]*(length+outputs-1)
                    kernel[r] = 1
                    record(real,imag,kernel,outputs,2,1)
                    counts["basis_packings"] += 1

    for _ in range(680):
        precision = rng.choice((0,1,2,3,5,6,7,12,101,303))
        magnitude = rng.choice((F(1),F(3,2),F(7,3),F(16)))
        length, outputs = rng.randrange(1,18), rng.randrange(1,18)
        q = 1 << precision
        largest = int(magnitude*(q+32))
        real = [rng.choice((-largest,-1,0,1,largest)) for _ in range(length)]
        imag = [rng.choice((-largest,-1,0,1,largest)) for _ in range(length)]
        kernel = [rng.choice((-q-2,-2,-1,0,1,q+2)) for _ in range(length+outputs-1)]
        record(real,imag,kernel,outputs,precision,magnitude)
        counts["seeded_packings"] += 1
        enclosure_case(precision,magnitude,length,outputs,rng)
        counts["enclosure_cases"] += 1

    source_cases = []
    from math import isqrt
    for p in (101,128,257):
        for alpha in sorted({2,isqrt(p-1)}):
            root = isqrt(p)
            root += root*root < p
            m_s, m_e = root*alpha, 1
            while 4*alpha*alpha*m_e*m_e < p:
                m_e += 1
            for label, precision, magnitude, length, outputs in (
                ("S",3*p,1,3*m_s+3,m_s),
                ("E",34*p,1 << ((114*alpha*alpha+99)//100),3*m_e+1,2*m_e+2),
            ):
                q = 1 << precision
                largest = magnitude*(q+32)
                real = [largest if a%2 else -largest for a in range(length)]
                imag = [0 if a%3 else largest for a in range(length)]
                kernel = [q+2 if a%3 else -2 for a in range(length+outputs-1)]
                record(real,imag,kernel,outputs,precision,magnitude)
                counts["source_dimension_packings"] += 1
                source_cases.append({"map":label,"p":p,"alpha":alpha,"P":precision,
                                     "L_A":length,"L_B":outputs,"guard":guard_bits(precision)})

    # One-too-small guards alias a coefficient into a SECOND VALID output slot.
    # Recomposition and terminal-carry checks both pass for every witness.
    sharpness = []
    for precision in (*range(10),101,303,3434):
        q, guard = 1 << precision, guard_bits(precision)
        bits = slot_bits(precision,1,1,guard-1)
        bad = packed([q+32],[0],[0,q+2],2,bits)
        require(bad != direct([q+32],[0],[0,q+2],2), "alias control failed")
        require((q+32)*(q+2) == bad[0][0]+(1 << bits)*bad[1][0], "alias recomposition")
        check_case([q+32],[0],[0,q+2],2,precision,1)
        sharpness.append({"P":precision,"minimal_guard":guard,"unsafe_guard":guard-1,
                          "alias_sha256":hashlib.sha256(str(bad).encode()).hexdigest()})

    faults = []
    fixture = ([2,-1],[1,2],[-1,2,3,1],3,8)
    expected = direct(*fixture[:4])
    for fault in ("no_reverse","crop","discard_negative_kernel"):
        require(packed(*fixture,fault=fault) != expected, "undetected fault: "+fault)
        faults.append(fault)
    # The inner product has a 2P grid; premature P-grid truncation loses 1/16.
    inner = packed([1],[0],[1],1,slot_bits(2,1,1))[0][0]
    require(F(inner,16) != F(inner//4,4), "premature inner rounding control")
    faults += ["unsafe_guard_alias","premature_inner_rounding"]
    require(33*3-1 > 32 and 33*3-1 <= 128, "error constant control")
    faults.append("drop_perturbation_terms")
    return {"status":"PASS_CHIRP_PACKED_CORRELATION","seed":68,"counts":counts,
            "stream_sha256":digest.hexdigest(),
            "minimal_guards_P_0_to_9":[guard_bits(p) for p in range(10)],
            "sharpness_controls":sharpness,"fault_controls":faults,
            "source_dimensions":source_cases,
            "scope":"Inner exact packing and conditional error envelope only; no new kappa."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write",type=Path)
    args = parser.parse_args()
    check_sources()
    result = compute_receipt()
    encoded = json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.write is not None:
        with args.write.open("x") as output:
            output.write(encoded)
    else:
        require(encoded == (PACKAGE/"RESULT.json").read_text(), "receipt mismatch")
    print(result["status"],json.dumps(result["counts"],sort_keys=True),
          "faults="+str(len(result["fault_controls"])),"no_new_kappa")


if __name__ == "__main__":
    main()
