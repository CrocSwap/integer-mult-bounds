#!/usr/bin/env python3
"""Exact low-bit and signed phase fusion checks with frozen local #7834 sources."""

import argparse
import ast
from collections import Counter
from dataclasses import dataclass
from hashlib import sha1, sha256
import importlib.util
import json
from math import gcd, isqrt, prod
from pathlib import Path
from random import Random
import sys


SOURCE_HEAD = "4f0c67d5bb41d4af5501dcd40b3b388b35e0ff02"


def check(test, message):
    if not test:
        raise ArithmeticError(message)


def bit(value, position):
    return (value >> position) & 1


def shift_add_signed(value, short, width=None):
    """Signed shift-add, optionally consuming only a fixed-width low return."""
    multiplier = abs(short)
    accumulated = 0
    shift = 0
    mask = None if width is None else (1 << width) - 1
    while multiplier:
        if multiplier & 1:
            accumulated += value << shift
            if mask is not None:
                accumulated &= mask
        multiplier >>= 1
        shift += 1
    return -accumulated if short < 0 else accumulated


def fused_residue(x, second_x, y, second_y, carry, m, d):
    mask = (1 << m) - 1
    x &= mask
    second_y &= mask
    carry &= mask
    wide_return = x * (((y & mask) + second_y) & mask)
    if d >= m or not second_y:
        return (wide_return + carry) & mask
    s = (second_y & -second_y).bit_length() - 1
    short_width = m - d - s
    if short_width <= 0:
        return (wide_return + carry) & mask
    short_mask = (1 << short_width) - 1
    q = (((second_x & mask) >> d) - (x >> d)) & short_mask
    if short_width == 1:
        correction = q  # second_y >> s is odd
    else:
        correction = shift_add_signed((second_y >> s) & short_mask, q, short_width)
    return (wide_return + carry + (correction << (d + s))) & mask


def check_low_bits():
    residues = checked_carries = 0
    for m in range(1, 6):
        size = 1 << m
        for d in range(m + 1):
            width = 1 << d
            for x in range(size):
                for second_x in range(x % width, size, width):
                    for y in range(size):
                        for second_y in range(size):
                            source = x * y + second_x * second_y
                            if fused_residue(x, second_x, y, second_y, 0, m, d) != source % size:
                                raise ArithmeticError((m, d, x, second_x, y, second_y))
                            residues += 1
                            if m <= 3:
                                for carry in range(size):
                                    got = bit(fused_residue(x, second_x, y, second_y, carry, m, d), m - 1)
                                    check(got == bit(source + carry, m - 1), "arbitrary carry")
                                    checked_carries += 1
    rng = Random(1267834)
    signed_cases = 1024
    for _ in range(signed_cases):
        x, y, second_y, q = (rng.randint(-(1 << 41), 1 << 41) for _ in range(4))
        carry = rng.randint(-(1 << 81), 1 << 81)
        m = rng.randint(1, 61)
        d = rng.randint(0, m + 2)
        second_x = x + (q << d)
        got = fused_residue(x, second_x, y, second_y, carry, m, d)
        check(got == (x * y + second_x * second_y + carry) % (1 << m), "signed residue")
    return {"full_residue_cases": residues, "explicit_carry_cases": checked_carries,
            "signed_random_cases": signed_cases}


def check_threshold():
    """Compute full carry signatures from the original two products."""
    rows = signatures = collisions = 0
    for m in range(1, 7):
        size = 1 << m
        for d in range(m + 1):
            for second_y in range(size):
                x, y = 1, size - 1
                rows += 1
                expected_period = size // gcd(size, second_y << d)
                residue_to_signature, signature_to_residue = {}, {}
                for q in range(size >> d):
                    source = x * y + (x + (q << d)) * second_y
                    signature = sum(bit(source + carry, m - 1) << carry for carry in range(size))
                    residue = q % expected_period
                    previous = residue_to_signature.setdefault(residue, signature)
                    reverse = signature_to_residue.setdefault(signature, residue)
                    check(previous == signature and reverse == residue, "hidden offset period")
                    collisions += (q >= expected_period)
                    signatures += 1
                check(len(signature_to_residue) == expected_period, "hidden offset census")
    # Same wide product and carry. Ignoring the hidden top bit gives a false return.
    x, y, second_y, carry, m, d = 83, 117, 155, 177, 8, 7
    values = [bit(x * y + (x + (q << d)) * second_y + carry, m - 1) for q in (0, 1)]
    dropped_bit = bit(x * (y + second_y) + carry, m - 1)
    q1 = bit(fused_residue(x, x + (1 << d), y, second_y, carry, m, d), m - 1)
    check(values == [1, 0] and dropped_bit == 1 and q1 == 0, "no-side-information negative control")
    return {"fixed_right_rows": rows, "carry_signatures": signatures,
            "same_residue_collisions": collisions, "required_parity_witness": {
                "m": m, "d": d, "x": x, "y": y, "second_y": second_y, "carry": carry,
                "wide_return_modulo": (x * (y + second_y)) % (1 << m), "expected_bits": values,
                "bit_with_correction_omitted": dropped_bit, "bit_with_correction": q1}}


def pinned_bytes(path, blob):
    raw = path.read_bytes()
    actual = sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest()
    check(actual == blob, f"source identity for {path.name}")
    return raw


def load_pinned(name, path, blob):
    raw = pinned_bytes(path, blob)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module, sha256(raw).hexdigest()


def finite_geometries(path):
    source = pinned_bytes(path, "94a78b3c297b67b9aa1d07a3c67546ddb0f5ff75")
    tree = ast.parse(source)
    declarations = {"Geometry", "ceil_log", "prime", "choose"}
    tree.body = [node for node in tree.body if getattr(node, "name", None) in declarations]
    namespace = dict(dataclass=dataclass, isqrt=isqrt)
    exec(compile(tree, str(path), "exec"), namespace)
    return {n: namespace["choose"](n) for n in (144, 145, 1800)}, sha256(source).hexdigest()


def guarded_phase_raw(payload, phase, multiply, delta_cap):
    x, y = payload
    u, v = phase
    same_sign = (u < 0) == (v < 0)
    delta = u - (v if same_sign else -v)
    w = v.bit_length()
    if abs(delta) <= delta_cap and u.bit_length() == w:
        real_factor = (x if same_sign else -x) - y
        imag_factor = x + (y if same_sign else -y)
        if max(real_factor.bit_length(), imag_factor.bit_length()) <= w:
            real = multiply(v, real_factor) + shift_add_signed(x, delta)
            imag = multiply(v, imag_factor) + shift_add_signed(y, delta)
            return (real, imag), delta
    return (multiply(x, u) - multiply(y, v), multiply(x, v) + multiply(y, u)), None


def patched_diagonal(fine, counts, delta_cap):
    def diagonal(tape, diag, volume, scale, conjugate=False):
        diag.home()

        def apply(_, payload):
            phase = diag.read()
            if conjugate:
                phase = fine.conj(phase)
            raw, delta = guarded_phase_raw(payload, phase, lambda a, b: fine.mul(a, b, tape.trace), delta_cap)
            counts[delta] += 1
            return tuple(fine.tz(value, scale) for value in raw)

        return fine.map_tape(tape, volume, apply)

    return diagonal


def check_phase_raw():
    cases = matched = full_carry = 0
    for x in range(-8, 8):
        for y in range(-8, 8):
            for u in range(-8, 8):
                for v in range(-8, 8):
                    calls = []

                    def counted(a, b):
                        calls.append(max(a.bit_length(), b.bit_length()))
                        return a * b

                    actual, delta = guarded_phase_raw((x, y), (u, v), counted, 2)
                    expected = (x * u - y * v, x * v + y * u)
                    check(actual == expected, "raw signed phase product")
                    if delta is None:
                        check(len(calls) == 4, "phase fallback")
                    else:
                        original = [max(a.bit_length(), b.bit_length()) for a, b in
                                    ((x, u), (y, v), (x, v), (y, u))]
                        check(len(set(original + calls)) == 1 and len(calls) == 2, "width guard")
                        for carry in (-128, -1, 0, 1, 128):
                            check([bit(t + carry, 4) for t in actual] ==
                                  [bit(t + carry, 4) for t in expected], "phase carry")
                            full_carry += 1
                        matched += 1
                    cases += 1
    return {"cases": cases, "width_preserving_fusions": matched, "signed_carry_checks": full_carry}


def choose_test_payload(q, f, phase, fine):
    rng = Random(20261120)
    scale = 1 << f
    u, v = phase
    same_sign = (u < 0) == (v < 0)
    for _ in range(32):
        x, y = tuple(rng.randrange(-(1 << (q - 2)), 1 << (q - 2)) << (f - q) for _ in range(2))
        dropped = (v * ((x if same_sign else -x) - y), v * (x + (y if same_sign else -y)))
        original = (x * u - y * v, x * v + y * u)
        if tuple(fine.tz(n, scale) for n in dropped) != tuple(fine.tz(n, scale) for n in original):
            return x, y
    raise ArithmeticError("missing nonzero correction control")


def selected_diagonal(fine, operation, payload, phase, width, scale, conjugate=False):
    trace = fine.Trace()
    source, diagonal = (fine.Tape(width, trace) for _ in range(2))
    source.append(payload)
    diagonal.append(phase)
    result = operation(source, diagonal, 1, scale, conjugate)
    result.home()
    received = result.read()
    result.release()
    diagonal.release()
    check(trace.live == 0, "single-record owned banks")
    return received, trace


def high_width_fixture(fine, word):
    sources, radices, f, q, index = (3, 7), (8, 8), 8200, 8186, 9
    width, scale = f + len(radices) + 3, 1 << f
    check(f == q + (radices[1]).bit_length() + 10, "ordinary chirp internal width")
    calls = []

    def integer_return(a, b):
        calls.append(max(a.bit_length(), b.bit_length()))
        return a * b

    # Keep the actual source dispatcher. Replace only its cold worker return.
    prior = word.physical_product
    word.physical_product = integer_return
    try:
        trace = fine.Trace()
        phase, twist = fine.make_diagonals(sources, radices, width, f, trace)
        coefficient = phase.cells[index]
        row_hash = sha256(str(coefficient).encode()).hexdigest()
        phase.release()
        twist.release()
        check(trace.live == 0, "public phase banks")
        # cos(pi/8)^2 and sin(pi/8)^2 are (2 +/- sqrt(2))/4.
        # Their floors after scaling by 2^(2*f) use exact integer square roots.
        radical = isqrt(1 << (4 * f - 3))
        dc = isqrt((1 << (2 * f - 1)) + radical)
        ds = isqrt((1 << (2 * f - 1)) - radical - 1)
        direct_coefficient = (-((2 * ds * dc) >> f), (dc * dc - ds * ds) >> f)
        check(coefficient == direct_coefficient, "independent integer phase formula")
        check(tuple(abs(a).bit_length() for a in coefficient) == (f, f), "high phase width")
        check(abs(coefficient[0]) - abs(coefficient[1]) == -1, "nonzero rounded phase offset")
        payload = choose_test_payload(q, f, coefficient, fine)
        check(sum(n * n for n in payload) <= 1 << (2 * f - 2), "admitted half disk")
        receipts = {}
        for conjugate in (False, True):
            counts = Counter()
            calls.clear()
            want, before = selected_diagonal(fine, fine.scalar_diagonal, payload, coefficient, width, scale, conjugate)
            baseline = calls.copy()
            calls.clear()
            have, after = selected_diagonal(fine, patched_diagonal(fine, counts, 2), payload, coefficient,
                                            width, scale, conjugate)
            direct = coefficient if not conjugate else fine.conj(coefficient)
            x, y = payload
            u, v = direct
            exact = (fine.tz(x * u - y * v, scale), fine.tz(x * v + y * u, scale))
            check(have == want == exact, "high phase scaled output")
            check(before.fast_words == 4 and after.fast_words == 2 and baseline == [f] * 4 and calls == [f] * 2,
                  "matched high word grades")
            check(sum(counts.values()) == 1 and abs(next(iter(counts))) == 1, "bounded nonzero correction")
            receipts[str(conjugate).lower()] = {"baseline_fast_widths": baseline, "fused_fast_widths": calls.copy(),
                                                  "delta": next(iter(counts)), "cleaned_owned_banks": True}
        return {"sources": sources, "radices": radices, "q": q, "f": f, "index": index,
                "coordinate": [1, 1], "phase_sha256": row_hash, "same_grid_results": receipts,
                "independent_integer_phase_formula": True,
                "correction_changes_truncated_output": True,
                "execution": "actual source dispatcher with an exact integer test double for the physical worker",
                "ingress": "legal direct chirp_middle fixture, outside product.choose geometries"}
    finally:
        word.physical_product = prior


def complete_chirp(fine, geometry, inverse=False):
    sources, radices, q = geometry
    scale = 1 << q
    values = [(((5 * i + 7) % 19 - 9) * scale // 64, ((11 * i + 5) % 23 - 11) * scale // 64)
              for i in range(prod(radices))]
    before, after = fine.Trace(), fine.Trace()
    want = fine.chirp_middle(values, sources, radices, q, inverse=inverse, trace=before)
    counts = Counter()
    original = fine.scalar_diagonal
    try:
        fine.scalar_diagonal = patched_diagonal(fine, counts, 2)
        have = fine.chirp_middle(values, sources, radices, q, inverse=inverse, trace=after)
    finally:
        fine.scalar_diagonal = original
    check(have == want and before.live == after.live == 0, "complete chirp and lifetimes")
    fused = sum(n for delta, n in counts.items() if delta is not None)
    check(before.fast_words == after.fast_words == 0 and fused > 0, "unmocked bounded-base control")
    check(before.scalar_products - after.scalar_products == 2 * fused, "whole-middle dispatch census")
    return {"geometry": geometry, "inverse": inverse, "outputs": len(have), "source_words": before.scalar_products,
            "fused_words": after.scalar_products, "guard_census": {str(delta): n for delta, n in counts.items()},
            "source_fast_words": before.fast_words, "fused_fast_words": after.fast_words,
            "out_sha256": sha256(str(have).encode()).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True,
                        help="checkout directory with the three pinned #7834 Python modules")
    args = parser.parse_args()
    source_dir = args.source_dir.resolve()
    word_path = source_dir / "word_multiply.py"
    word, word_hash = load_pinned("word_multiply", word_path,
                                  "b148a60eac955722520e193f8bde0687635407ee")
    fine, fine_hash = load_pinned("fine_ring_7834", source_dir / "fine_ring.py",
                                  "b18da6275e31ac0bcc4174ec86106532c0cb5958")
    emitted, product_hash = finite_geometries(source_dir / "product.py")
    first = emitted[144]
    check((first.sources, first.targets, first.precision) == ((5, 7), (8, 8), 128), "emitted first geometry")
    check((emitted[145].sources, emitted[145].targets) == ((31, 29), (32, 32)), "emitted second geometry")
    result = {
        "status": "exact_local_scalar_fusion",
        "sources": {"#7834_head": SOURCE_HEAD, "fine_ring_sha256": fine_hash, "word_multiply_sha256": word_hash,
                    "product_sha256": product_hash,
                    "#7838_head": "cd9ce5a555977b469bd848199bc36025bd82fdcb",
                    "#7838_role": "different carryless channel ABI without side information"},
        "low_bits": check_low_bits(), "threshold": check_threshold(), "phase_raw": check_phase_raw(),
        "emitted_geometry_control": {n: vars(g) for n, g in emitted.items()},
        "full_unmocked_chirp_controls": [complete_chirp(fine, geometry, inverse)
                                         for geometry in ((first.sources, first.targets, first.precision),
                                                          (emitted[145].sources, emitted[145].targets,
                                                           emitted[145].precision),
                                                          ((3, 7), (8, 8), 82))
                                         for inverse in (False, True)],
        "matched_dispatch_control": high_width_fixture(fine, word),
        "physical_recursive_p104_or_bit_credit": 0,
        "kappa": None,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
