#!/usr/bin/env python3
"""Exact finite audit of the written prime-power Newton-polygon formula."""
import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from math import gcd, isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('newton_cyclotomic', HERE / 'cyclotomic.py')
cyclotomic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cyclotomic)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def prime(n):
    return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))


def domain(limit=68):
    for p in range(2, limit + 1):
        if prime(p):
            a, r = 1, p
            while r <= limit:
                yield p, a, r
                a, r = a + 1, r * p


def counting_valuations(p, a):
    r = p ** a
    values = [0] * r
    for j in range(r - 2, -1, -1):
        s, weight = j + 1, 1
        while s % p == 0:
            weight *= p
            s //= p
        values[j] = values[j + 1] + weight
    return values


def lower_hull(values):
    hull = []
    for x, y in enumerate(values):
        while len(hull) >= 2:
            x0, y0 = hull[-2]
            x1, y1 = hull[-1]
            # Retain only genuine vertices: discard a collinear middle point.
            if (x1 - x0) * (y - y1) > (y1 - y0) * (x - x1):
                break
            hull.pop()
        hull.append((x, y))
    return hull


def predicted_vertices(p, a):
    r = p ** a
    return [(r - p ** k, k * (p - 1) * p ** (k - 1)) for k in range(a, 0, -1)] + [(r - 1, 0)]


def polygon_record(values, p, a):
    r, e = p ** a, (p - 1) * p ** (a - 1)
    require(len(values) == r, 'coefficient count')
    require(values == counting_valuations(p, a), 'coefficient valuation mismatch')
    hull = lower_hull(values)
    require(hull == predicted_vertices(p, a), 'Newton vertices mismatch')
    segments = []
    contacts = set()
    for k, (left, right) in zip(range(a, 0, -1), zip(hull, hull[1:])):
        x0, y0 = left
        x1, y1 = right
        lam = Fraction(y0 - y1, x1 - x0)
        require(lam == 1 + Fraction((k - 1) * (p - 1), p), 'root valuation')
        require(x1 - x0 == (p - 1) * p ** (k - 1), 'root multiplicity')
        edge_contacts = []
        for j in range(x0, x1 + 1):
            gap = Fraction(values[j] - y0) + lam * (j - x0)
            require(gap >= 0, 'coefficient below claimed edge')
            require((gap == 0) == ((r - j) % p ** (k - 1) == 0), 'edge-contact locus')
            if gap == 0:
                contacts.add(j)
                edge_contacts.append(j)
        segments.append({'valuation': str(lam), 'multiplicity': x1 - x0,
                         'valuation_with_vp_p_1': str(lam / e), 'contacts': edge_contacts})
    require(sum(s['multiplicity'] for s in segments) == r - 1, 'total degree')
    require(sum(Fraction(s['valuation']) * s['multiplicity'] for s in segments) == a * e, 'constant/product valuation')
    require(all(Fraction(s['valuation']) > 0 for s in segments), 'nonunit root obligation')
    return {'p': p, 'a': a, 'r': r, 'ramification_index': e,
            'coefficient_valuations': values, 'vertices': hull, 'segments': segments,
            'edge_contact_count': len(contacts)}


def reject(fn, name):
    try:
        fn()
    except (ValueError, TypeError):
        return name
    raise ValueError('negative control accepted: ' + name)


def controls():
    out = []
    original = counting_valuations(2, 3)
    mutant = original[:]
    mutant[0] = 0  # f(z)+1: r+1 is a unit; all its roots have valuation zero.
    require(lower_hull(mutant) == [(0, 0), (7, 0)], 'unit-constant control polygon')
    out.append(reject(lambda: polygon_record(mutant, 2, 3), 'unit_constant_changes_root_polygon'))
    omitted = original[:]
    omitted[0] -= 4  # Omit the s=4 factor from the constant coefficient.
    out.append(reject(lambda: polygon_record(omitted, 2, 3), 'omitted_ramified_factor'))
    wrong_ramification = original[:]
    wrong_ramification[0] = 3  # v_2(8), incorrectly used as v_pi(8).
    out.append(reject(lambda: polygon_record(wrong_ramification, 2, 3), 'mixed_valuation_normalizations'))
    reversed_order = list(reversed(original))
    out.append(reject(lambda: polygon_record(reversed_order, 2, 3), 'reversed_coefficient_order'))
    nonmonic = original[:]
    nonmonic[-1] = 1
    out.append(reject(lambda: polygon_record(nonmonic, 2, 3), 'nonunit_leading_coefficient'))
    out.append(reject(lambda: cyclotomic.tail_valuations(2, 3, 2), 'nonprimitive_root'))
    out.append(reject(lambda: cyclotomic.tail_valuations(4, 1, 1), 'composite_base'))
    out.append(reject(lambda: cyclotomic.tail_valuations(2, 0, 1), 'zero_exponent'))
    # Distinguish genuine vertices from extra collinear coefficient contacts.
    odd = polygon_record(counting_valuations(3, 2), 3, 2)
    require(odd['edge_contact_count'] == 5 and len(odd['vertices']) == 3, 'odd-prime contacts')
    out.append(reject(lambda: require(odd['edge_contact_count'] == len(odd['vertices']), 'missing contacts'), 'vertices_are_not_all_contacts'))
    return out


def check_sources():
    manifest = json.loads((HERE / 'SOURCE.json').read_text())
    root = HERE.parent.parent
    for name, digest in manifest['sha256'].items():
        require(hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, 'source drift: ' + name)
    return manifest['base_commit']


def run():
    base = check_sources()
    records = []
    embeddings = coefficients = 0
    exact_digest = hashlib.sha256()
    for p, a, r in domain():
        values = counting_valuations(p, a)
        record = polygon_record(values, p, a)
        primitive = [t for t in range(1, r) if gcd(t, r) == 1]
        for t in primitive:
            independent = cyclotomic.tail_valuations(p, a, t)
            require(independent == values, 'independent cyclotomic coefficient mismatch at r=%d t=%d' % (r, t))
            exact_digest.update((canonical([r, t, independent]) + '\n').encode())
            embeddings += 1
            coefficients += r
        record['primitive_powers'] = primitive
        records.append(record)
    negative = controls()
    return {'schema': 1, 'base_commit': base, 'assignment_seed': 68,
            'scope': 'Finite coefficient/polygon audit; the separate written proof gives the uniform statement.',
            'domain': 'Every prime power 2 <= r <= 68 and every primitive exponent 1 <= t < r.',
            'radices': len(records), 'primitive_embeddings': embeddings,
            'coefficient_obligations': coefficients, 'independent_valuation_sha256': exact_digest.hexdigest(),
            'negative_controls': negative, 'cases': records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-receipt', type=Path, help='Generate a receipt at the explicitly supplied path.')
    args = parser.parse_args()
    result = run()
    if args.write_receipt:
        args.write_receipt.write_text(json.dumps(result, indent=2) + '\n')
    else:
        expected = json.loads((HERE / 'EXPECTED.json').read_text())
        require(canonical(result) == canonical(expected), 'frozen receipt mismatch')
    print('PASS_NEWTON_NONUNIT_AUDIT: %d radices; %d primitive embeddings; %d coefficient obligations; %d negative controls' %
          (result['radices'], result['primitive_embeddings'], result['coefficient_obligations'], len(result['negative_controls'])))


if __name__ == '__main__':
    main()
