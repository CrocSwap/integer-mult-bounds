#!/usr/bin/env python3
"""Check the signed products and charged continuation at the registered #7834 head."""

import argparse
from collections import Counter
from contextlib import contextmanager
from functools import cache
from hashlib import sha1, sha256
from inspect import getsource
from itertools import product as combinations
import json
from math import prod
from pathlib import Path
from random import Random
import sys
from unittest.mock import patch


HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def bind_sources(source_path):
    pins = json.loads((HERE / "SOURCE-BLOBS.json").read_text())
    files = {}
    for name, expected in sorted(pins["git_blobs"].items()):
        data = (source_path / name).read_bytes()
        git_blob = sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        require(git_blob == expected, f"source blob changed: {name}")
        files[name] = {"git_blob": git_blob, "sha256": sha256(data).hexdigest()}
    sys.path.insert(0, str(source_path))
    return {"head": pins["head"], "path": pins["path"], "files": files}


def signed_mix(first, second):
    """Return first+s*second with the sign s that cancels magnitudes."""
    if (first < 0) == (second < 0):
        return first - second, -1
    return first + second, 1


def cross_parts(a, b, c, d, mul, trace):
    """Exact Gaussian product numerators using three equally bounded products."""
    x, s = signed_mix(a, b)
    y, t = signed_mix(c, d)
    mixed = mul(x, y, trace)
    if s == t:
        ac = mul(a, c, trace)
        bd = mul(b, d, trace)
        cross = mixed - ac - bd
        return ac - bd, cross if s == 1 else -cross
    ad = mul(a, d, trace)
    bc = mul(b, c, trace)
    cross = ad - bc if s == 1 else bc - ad
    return mixed + cross, ad + bc


def trunc_zero(value, divisor):
    quotient, remainder = divmod(value, divisor)
    return quotient + int(value < 0 and remainder != 0)


def raw_checks():
    def check_product(a, b, trace):
        return a * b

    cases = 0
    carried = 0
    for a, b, c, d in combinations(range(-4, 5), repeat=4):
        actual = cross_parts(a, b, c, d, check_product, None)
        exact = a * c - b * d, a * d + b * c
        require(actual == exact, "signed numerator mismatch")
        x, _ = signed_mix(a, b)
        y, _ = signed_mix(c, d)
        require(abs(x) <= max(abs(a), abs(b)), "left mixture widened")
        require(abs(y) <= max(abs(c), abs(d)), "right mixture widened")
        cases += 1
        for divisor, carry in combinations((4, 8, 16), (-23, -7, -1, 0, 1, 7, 23)):
            for total, original in zip(actual, exact, strict=True):
                quotient, digit = divmod(total + carry, divisor)
                expected = original + carry
                expected_digit = expected & (divisor - 1)
                expected_carry = expected >> (divisor.bit_length() - 1)
                require((quotient, digit) == (expected_carry, expected_digit), "integer carry failed")
                magnitude = abs(expected) // divisor
                signed = -magnitude if expected < 0 else magnitude
                require(trunc_zero(total + carry, divisor) == signed, "signed q-grid drop changed")
                carried += 1
    separating = {
        "scale": 4,
        "summands": [[3, 1], [4, 0]],
        "common_sum": 4,
        "sum_of_signed_drops": [0, 1],
    }
    return {"quadruples": cases, "carry_and_drop_comparisons": carried,
            "individually_dropped_collision": separating}


@contextmanager
def candidate():
    """Change just the multiplication joins in memory."""
    import axis_program
    import fine_ring
    import product

    calls = Counter()

    def parts(a, b, c, d, trace):
        calls["ring_products"] += 1
        return cross_parts(a, b, c, d, fine_ring.mul, trace)

    def times(a, b, divisor, trace):
        calls["times"] += 1
        real, imag = cross_parts(*a, *b, fine_ring.mul, trace)
        return fine_ring.tz(real, divisor), fine_ring.tz(imag, divisor)

    source = getsource(fine_ring.ring_products)
    target = "real = mul(a, c, trace) - mul(b, d, trace)\n        imag = mul(a, d, trace) + mul(b, c, trace)"
    require(source.count(target) == 1, "the two ring joins changed")
    rewritten = source.replace(target, "real, imag = _parts(a, b, c, d, trace)")
    namespace = dict(fine_ring.__dict__, _parts=parts)
    exec(compile(rewritten, "<gaussian ring join control>", "exec"), namespace)
    with (
        patch.object(fine_ring, "times", times),
        patch.object(axis_program, "times", times),
        patch.object(product, "times", times),
        patch.object(fine_ring, "ring_products", namespace["ring_products"]),
    ):
        yield calls


def word_dispatch_checks():
    """Exercise the actual selector; the expensive child body has an exact oracle."""
    import fine_ring
    import word_multiply

    width = word_multiply.BASE_BITS
    q = width + 3
    divisor = 1 << q
    below = (1 << (width - 1)) + 1
    above = (1 << width) + 1
    endpoint_checks = 0
    fast_transitions = Counter()

    def physical_oracle(a, b):
        return a * b

    with patch.object(word_multiply, "physical_product", physical_oracle):
        for bits in combinations((0, below, above, -below, -above), repeat=4):
            a, b, c, d = bits
            radius_sq = ((5 * divisor) // 16 - 1) ** 2
            require(a * a + b * b <= radius_sq and c * c + d * d <= radius_sq,
                    "test record exceeds the pointwise entrance disk")
            old = fine_ring.Trace()
            exact = fine_ring.times((a, b), (c, d), divisor, old)
            new = fine_ring.Trace()
            p, r = cross_parts(a, b, c, d, word_multiply.product, new)
            actual = trunc_zero(p, divisor), trunc_zero(r, divisor)
            require(actual == exact, "dispatch endpoint changed")
            require((old.scalar_products, new.scalar_products) == (4, 3), "word count changed")
            require(new.fast_words <= old.fast_words, "avoidable larger dispatch")
            require(new.max_scalar_operand <= old.max_scalar_operand, "avoidable width increase")
            fast_transitions[f"{old.fast_words}->{new.fast_words}"] += 1
            endpoint_checks += 1
        b = below
        naive = fine_ring.Trace()
        word_multiply.product(b, b, naive)
        word_multiply.product(b, b, naive)
        word_multiply.product(b + b, b + b, naive)
        require((naive.scalar_products, naive.fast_words) == (3, 1),
                "unprotected join should cross the physical cutoff on this input")
    require(fast_transitions["4->3"] > 0 and fast_transitions["2->2"] > 0,
            "test should see both strict and tied physical counts")
    return {"selector": "actual word_multiply.product",
            "physical_child": "exact bigint oracle only for selector controls",
            "threshold_bits": width, "checks": endpoint_checks,
            "fast_word_transitions": dict(sorted(fast_transitions.items())),
            "unconditionally_additive_mix_negative_control": {
                "component_formula_for_all_four": "2^8191+1",
                "pointwise_grid_bits": q,
                "original_operand_bits": width,
                "mixed_operand_bits": width + 1,
                "baseline_fast": 0,
                "naive_fast": 1,
            }}


def ring_expected(first, second, r, divisor):
    output = []
    for offset in range(0, len(first), r):
        real = [0] * r
        imag = [0] * r
        for i, (a, b) in enumerate(first[offset:offset + r]):
            for j, (c, d) in enumerate(second[offset:offset + r]):
                k = (i + j) % r
                sign = 1 if i + j < r else -1
                real[k] += sign * (a * c - b * d)
                imag[k] += sign * (a * d + b * c)
        output.extend((trunc_zero(a, divisor), trunc_zero(b, divisor))
                      for a, b in zip(real, imag, strict=True))
    return output


def ring_checks():
    import fine_ring

    def execute(first, second, r, outer, f):
        trace = fine_ring.Trace()
        x = fine_ring.Tape(f + 8, trace)
        y = fine_ring.Tape(f + 8, trace)
        for left, right in zip(first, second, strict=True):
            x.append(left)
            y.append(right)
        out = fine_ring.ring_products(x, y, r, outer, f)
        out.home()
        projections = [out.read() for _ in range(len(first))]
        out.release()
        require(trace.live == 0 and x.released and y.released, "ring banks still live")
        return projections, vars(trace)

    seed = Random(7834)
    tested = []
    for r, outer, f in ((4, (2,), 16), (8, (4, 8), 36), (16, (8,), 61)):
        n = r * prod(outer)
        endpoint = 1 << (f - 2)
        a = [(seed.randint(-endpoint, endpoint), seed.randint(-endpoint, endpoint))
             for _ in range(n)]
        b = [(seed.randint(-endpoint, endpoint), seed.randint(-endpoint, endpoint))
             for _ in range(n)]
        a[r - 1] = (-endpoint, endpoint)
        b[r - 1] = (endpoint, endpoint)
        original, old = execute(a, b, r, outer, f)
        with candidate() as calls:
            fused, new = execute(a, b, r, outer, f)
        require(original == fused == ring_expected(a, b, r, r << f), "negacyclic return changed")
        require(calls == {"ring_products": prod(outer)}, "ring path did not execute")
        movement = ("reads", "writes", "travel", "resets", "erased", "high_water")
        require(all(old[k] == new[k] for k in movement), "ring tape behavior changed")
        require(old["scalar_products"] - new["scalar_products"] == prod(outer),
                "ring count changed outside the join")
        tested.append({"r": r, "outer": outer, "f": f, "coefficients": n,
                       "word_products_old_new": [old["scalar_products"], new["scalar_products"]],
                       "payload_trace": {k: new[k] for k in (*movement, "live")}})
    return tested


def pre_carry_oracle(left, right, width, size):
    mask = (1 << width) - 1
    x, y = int(left, 2), int(right, 2)
    coeff = [0] * size
    for i in range((len(left) + width - 1) // width):
        for j in range((len(right) + width - 1) // width):
            coeff[i + j] += ((x >> (i * width)) & mask) * ((y >> (j * width)) & mask)
    return coeff


@contextmanager
def observed_sparse_drop():
    """Witness an actual individually rounded sparse sum without changing it."""
    import fine_ring
    import sparse_tapes

    multiply_line = sparse_tapes.multiply_line
    witness = {}
    visited = 0

    def compare(line, page, offsets, unit, owner):
        nonlocal visited
        visited += 1
        if not witness:
            n = len(line.cells)
            for i in range(n):
                row = page.cells[i*len(offsets):(i + 1)*len(offsets)]
                for component in (0, 1):
                    raw = [line.cells[(i + h) % n][component] * c
                           for h, (c, _) in zip(offsets, row, strict=True)]
                    actual = sum(fine_ring.tz(value, unit) for value in raw)
                    postponed = fine_ring.tz(sum(raw), unit)
                    if actual != postponed:
                        witness.update({"line_call": visited, "row": i, "component": component,
                                        "scale_bits": unit.bit_length() - 1,
                                        "nonzero_product_count": sum(value != 0 for value in raw),
                                        "sum_of_drops_minus_drop_of_sum": actual - postponed,
                                        "nonzero_signed_products_hex": [hex(x) for x in raw if x]})
                        break
                if witness:
                    break
        return multiply_line(line, page, offsets, unit, owner)

    with patch.object(sparse_tapes, "multiply_line", compare):
        yield witness


def full_checks(interior, regression_only=False):
    import product

    fixtures = [
        (format(741503, "b"), format(466013, "b")),
        ("0", "111101"),
        ("0100010111001", "0111010010110010"),
        ("1" * 144, "1" * 144),
        ("1".zfill(1801), "11"),
    ]
    if regression_only:
        fixtures = fixtures[:1]
    elif interior:
        fixtures.append((format(741503, "0145b"), format(466013, "0145b")))

    catalogue_once = cache(product.catalogue)
    evidence = []
    with patch.object(product, "catalogue", catalogue_once):
        for a, b in fixtures:
            with observed_sparse_drop() as witness:
                original, old = product.multiply(a, b)
            with candidate() as calls:
                result, new = product.multiply(a, b)
            require(original == result, "complete multiplier output changed")
            require(result == format(int(a, 2) * int(b, 2), f"0{2 * max(len(a), len(b))}b"),
                    "complete product disagrees with the independent integer product")
            if old["path"] == "elementary":
                require(old == new and not calls, "the fallback entered the modified joins")
                evidence.append({"input_bits": [len(a), len(b)], "path": old["path"],
                                 "fused_parents": {}})
                continue
            require(old["path"] == "gaussian", "the complete Gaussian route was not used")
            require(bool(witness), "the concrete sparse grid control did not observe a drop change")
            tr_old, tr_new = old.pop("trace"), new.pop("trace")
            require(old == new, "complete normalization, recovery or public routing receipt changed")
            require(new["coefficients"] == pre_carry_oracle(a, b, new["digit_bits"], prod(new["sources"])),
                    "the coefficients entering the carry scan changed")
            require(tr_new["live"] == tr_old["live"] == 0, "tape still live after complete product")
            require(tr_old["scalar_products"] - tr_new["scalar_products"] == sum(calls.values()),
                    "observed word savings differ from the localized joins")
            require(calls["ring_products"] == tr_old["rings"], "synthetic ring attempt did not execute")
            require(tr_new["fast_words"] == tr_old["fast_words"] == 0,
                    "finite control unexpectedly crossed the short-word cutoff")
            movement = ("reads", "writes", "travel", "resets", "erased", "high_water", "live")
            require(all(tr_old[k] == tr_new[k] for k in movement), "full record movements changed")
            evidence.append({
                "input_bits": [len(a), len(b)],
                "path": old["path"],
                "sources": new["sources"],
                "targets": new["targets"],
                "fused_parents": dict(calls),
                "word_products_old_new": [tr_old["scalar_products"], tr_new["scalar_products"]],
                "fast_words_old_new": [tr_old["fast_words"], tr_new["fast_words"]],
                "coefficients": len(new["coefficients"]),
                "max_residual_squared_numerator": new["max_residual_squared_numerator"],
                "radius_numerator": new["radius_numerator"],
                "payload_trace": {k: tr_new[k] for k in movement},
                "reached_postponed_drop_failure": witness,
            })
    return evidence


def wrapper_checks():
    """Use signed atom addresses to test the documented fitted body endpoint."""
    def add(a, b, modulus):
        return tuple((x + y) % modulus for x, y in zip(a, b, strict=True))

    def subtract(a, b, modulus):
        return tuple((x - y) % modulus for x, y in zip(a, b, strict=True))

    def root(h, d):
        return d[::-1], h[::-1]

    def body(h, d, modulus):
        x, y = root(h, subtract(d, h, modulus))
        z, w = root(x, add(x, y, modulus))
        return z, subtract(z, w, modulus)

    count = 0
    for modulus, n in ((3, 2), (3, 3), (2, 4)):
        for h, d in combinations(combinations(range(modulus), repeat=n), repeat=2):
            require(body(h, d, modulus) == (d, h), "two-root address identity failed")
            count += 1
    n = 64
    empty = (0,) * n
    basis = (1,) + empty[:-1]
    modulus = 213 * (1 << 80) + 1
    first = root(empty, subtract(basis, empty, modulus))
    second = root(basis, subtract(basis, basis, modulus))
    require(add(*first, modulus) == add(*second, modulus), "missing equal-sum control")
    require(first[0] != second[0], "the separate next input should differ")
    require(body(empty, basis, modulus) != body(basis, basis, modulus),
            "the two legal endpoint addresses must differ")
    return {"abstract_address_checks": count, "production_width_collision": n,
            "modulus_for_collision": modulus, "h_either_zero_or_first_basis": True,
            "d_first_basis": True, "sum_in_both_cases": "e_63", "first_return_differs": True,
            "physical_compact_root_executed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=HERE / "source")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--interior", action="store_true", help="also replay the costly 145-bit geometry")
    mode.add_argument("--regression-only", action="store_true", help="replay just the full 20-bit product")
    args = parser.parse_args()
    result = {"source": bind_sources(args.source.resolve())}
    if not args.regression_only:
        result.update({
            "signed_arithmetic": raw_checks(),
            "dispatch": word_dispatch_checks(),
            "signed_ring_tapes": ring_checks(),
            "charged_wrapper": wrapper_checks(),
        })
    result["complete_finite_products"] = full_checks(args.interior, args.regression_only)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
