#!/usr/bin/env python3
"""Independent algebraic enclosure of the selected complex recursive moment.

Prepared for arkfx with substantial OpenAI Codex assistance; Apache-2.0.
Only standard-library arithmetic is used. No supplier/pricing code is imported.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import isqrt
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEPTH = 163  # 160 + assignment seed 83 modulo 16
BITS = 256


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(n, d):
    return -(-n // d)


def root_bounds(pair, scale):
    """Outward square root of a nonnegative interval in scale units."""
    lo, hi = pair
    require(0 <= lo <= hi, 'invalid root interval')
    lower = isqrt(lo * scale)
    upper = isqrt(hi * scale)
    upper += upper * upper < hi * scale
    return lower, upper


def mul_bounds(left, right, scale):
    return left[0] * right[0] // scale, ceil_div(left[1] * right[1], scale)


def power_bounds(base, exponent, depth=DEPTH, bits=BITS):
    """Enclose base**exponent by binary exponents and repeated square roots."""
    require(type(base) in (Q, int) and type(exponent) in (Q, int), 'exact inputs required')
    base, exponent = Q(base), Q(exponent)
    require(base >= 1 and 0 <= exponent <= 1, 'power domain')
    require(type(depth) is int and 1 <= depth <= 4096, 'depth domain')
    require(type(bits) is int and 8 <= bits <= 4096, 'precision domain')
    scale = 1 << bits
    initial = (base.numerator * scale // base.denominator,
               ceil_div(base.numerator * scale, base.denominator))
    denominator = 1 << depth
    lower_n = exponent.numerator * denominator // exponent.denominator
    upper_n = ceil_div(exponent.numerator * denominator, exponent.denominator)
    roots = []
    current = initial
    for _ in range(depth):
        current = root_bounds(current, scale)
        roots.append(current)

    def dyadic(n):
        if n == denominator:
            return initial
        result = (scale, scale)
        for i, bounds in enumerate(roots, 1):
            if n & (1 << (depth - i)):
                result = mul_bounds(result, bounds, scale)
        return result

    return Q(dyadic(lower_n)[0], scale), Q(dyadic(upper_n)[1], scale)


def moment(profile, m, live, saving, surcharge=False):
    require(type(m) is int and m > 1 and type(live) is int and live > 0, 'parent domain')
    require(type(surcharge) is bool, 'surcharge domain')
    require(profile and all(type(r) is int and 0 < r < m and
                           type(n) is int and n > 0 for r, n in profile.items()), 'child domain')
    lo = hi = Q(0)
    for r, count in sorted(profile.items()):
        lower, upper = power_bounds(Q(m, r), saving)
        weight = Q(r * count, m * live)
        lo += weight * lower
        hi += weight * upper
    if surcharge:
        lower, upper = power_bounds(m, saving)
        weight = Q(32 * m * sum(profile.values()), live * 10**16)
        lo += weight * lower
        hi += weight * upper
    return lo, hi


def profile_dict(data):
    require(type(data) is dict and data, 'profile object required')
    result = {}
    for rank, count in data.items():
        require(type(rank) is str and str(int(rank)) == rank and
                type(count) is int and count > 0, 'invalid profile entry')
        result[int(rank)] = count
    return result


def load_inputs():
    sources = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    data = {}
    for label, item in sources['files'].items():
        path = (ROOT / item['path']).resolve()
        require(path.is_relative_to(ROOT), 'source path escapes checkout')
        raw = path.read_bytes()
        require(sha256(raw).hexdigest() == item['sha256'], 'source hash: ' + label)
        data[label] = json.loads(raw)
    assembly, owner, invoice, idle, selected = [data[n] for n in
                                              ('assembly', 'owner', 'invoice', 'idle', 'selected')]
    require(selected['audited_source_head'] == sources['selected_source_head'], 'selected source head')
    require(selected['certificate'] == sources['files']['assembly']['path'], 'selected certificate path')
    require(selected['certificate_sha256'] == sources['files']['assembly']['sha256'], 'selected certificate hash')
    require(selected['kappa'] == assembly['kappa'], 'selected kappa')
    local = Counter()
    counts = Counter()
    calls = invoice['selected_calls']
    require(len(calls) == 72 and len({(c['stage'], c['replica']) for c in calls}) == 72,
            'selected calls')
    require({(c['stage'], c['replica']) for c in calls} ==
            {(s, r) for s in range(9) for r in range(8)}, 'call domain')
    for call in calls:
        require(call['orientation'] == ('forward' if call['stage'] % 2 == 0 else 'backward'),
                'call orientation')
        provider = invoice['providers'][call['provider_id']]
        local.update(profile_dict(provider['paid_profile']))
        counts[call['provider_id']] += 1
    require(dict(counts) == invoice['provider_counts'] == assembly['provider_counts'] ==
            {'ck': 8, 'jp8': 64}, 'provider multiplicities')
    require(dict(local) == profile_dict(invoice['selected_local_paid_profile']), 'local profile')
    profile = local + Counter(profile_dict(idle['rank_profile']))
    require(dict(profile) == profile_dict(owner['paid_profile']) ==
            profile_dict(assembly['complex_profile']), 'complete profile')
    require(sum(idle['rank_profile'].values()) == idle['children'] ==
            owner['explicit_idle_remainder_children'], 'idle count')
    require(owner['template_sha256'] == invoice['template_sha256'] == idle['template_sha256'],
            'receipt template binding')
    require(owner['live'] == invoice['live'] == 7168 and owner['physical'] == invoice['physical'] == 7670,
            'live and physical stocks')
    mass = sum(r * n for r, n in profile.items())
    require(mass == owner['rank_mass'] == 520704 and 73 * owner['live'] - mass ==
            owner['deficit'] == 2560, 'rank mass and deficit')
    require(assembly['surcharge_model']['complex'] is False, 'native complex charge')
    return assembly, dict(profile), dict(local), sources


def algebraic_controls():
    """Integer qth-power comparisons use no root/power enclosure algorithm."""
    rng = random.Random(83)
    fixtures = [(Q(73, r), Q(p, q)) for r in range(1, 73)
                for q in range(2, 14) for p in sorted({1, q - 1})]
    fixtures += [(Q(1), Q(0)), (Q(1), Q(1)), (Q(73), Q(0)), (Q(73), Q(1))]
    fixtures += [(Q(rng.randrange(2, 200)), Q(rng.randrange(1, q), q))
                 for q in [rng.randrange(2, 32) for _ in range(83)]]
    for base, exponent in fixtures:
        lo, hi = power_bounds(base, exponent)
        require(lo**exponent.denominator <= base**exponent.numerator <= hi**exponent.denominator,
                'integer-power oracle')
    # Coarse depth forces a visible exponent bracket. Using the lower exponent
    # for both endpoints incorrectly excludes this rational-power value.
    lo, hi = power_bounds(Q(73, 48), Q(1, 3), depth=8, bits=32)
    require(lo**3 < Q(73, 48) < hi**3, 'coarse exponent bracket')
    lower_dyadic_hi = power_bounds(Q(73, 48), Q(85, 256), depth=8, bits=32)[1]
    require(lower_dyadic_hi**3 < Q(73, 48), 'truncated exponent mutant not detected')
    # Rounding the upper root down fails even at an exact dyadic exponent.
    scale = 1 << 32
    bad_upper = Q(isqrt(2 * scale * scale), scale)
    require(bad_upper**2 < 2 <= power_bounds(2, Q(1, 2), bits=32)[1]**2,
            'upper-root rounding mutant not detected')
    bad = [(Q(1, 2), Q(1, 2)), (Q(2), Q(-1)), (Q(2), Q(2)), (2.0, Q(1, 2)),
           (Q(2), 0.5)]
    for base, exponent in bad:
        try:
            power_bounds(base, exponent)
        except ValueError:
            pass
        else:
            raise ValueError('invalid power accepted')
    return {'integer_power_comparisons': len(fixtures), 'kernel_mutants': 2,
            'rejected_power_inputs': len(bad)}


def build_certificate():
    assembly, profile, local, sources = load_inputs()
    rows = []
    for label, key, surcharge in [('native', 'complex_lower', False),
                                   ('conservative', 'conservative_complex_lower', True)]:
        lower = Q(assembly[key])
        for saving, accepted in [(lower, True), (lower + Q(1, 10**24), False)]:
            lo, hi = moment(profile, 73, 7168, saving, surcharge)
            require(hi < 1 if accepted else lo > 1, 'strict endpoint: ' + label)
            recorded = (assembly['moments'] if label == 'native' else assembly['conservative_moments'])
            original = next(x for x in recorded if x['side'] ==
                            ('complex' if label == 'native' else 'conservative_complex') and
                            Q(x['endpoint']) == saving)
            require(original['accept'] is accepted and original['surcharge'] is surcharge,
                    'recorded endpoint decision')
            rows.append({'model': label, 'saving': str(saving), 'surcharge': surcharge,
                         'accept': accepted, 'moment_minus_one': [str(lo - 1), str(hi - 1)]})
    native = Q(assembly['complex_lower'])
    conservative = Q(assembly['conservative_complex_lower'])
    require(moment(profile, 73, 7168, native, True)[0] > 1, 'old surcharge at native endpoint')
    require(moment(profile, 73, 7168, conservative + Q(1, 10**24), False)[1] < 1,
            'omitted conservative charge')
    require(moment(local, 73, 7168, native + Q(1, 10**24))[1] < 1, 'omitted idle children')
    require(moment(profile, 73, 7670, native + Q(1, 10**24))[1] < 1, 'physical stock denominator')
    changed = Counter(profile)
    changed[2] -= 2
    changed[1] += 1
    changed[3] += 1
    require(sum(changed.values()) == sum(profile.values()) and
            sum(r*n for r, n in changed.items()) == sum(r*n for r, n in profile.items()),
            'equal mass/count control')
    require(moment(dict(changed), 73, 7168, native + Q(1, 10**24))[1] < 1,
            'equal mass/count profile must change decision')
    require(moment(profile, 73, 7168, Q(0)) == (Q(520704, 73*7168),) * 2,
            'zero-saving exact moment')
    controls = algebraic_controls()
    controls['mathematical_controls'] = 6
    return {'status': 'PASS_PR626_ROOT_MOMENT', 'base_commit': sources['base_commit'],
            'assignment_seed': 83, 'method': {'dyadic_exponent_depth': DEPTH, 'fixed_point_bits': BITS},
            'profile': {str(r): n for r, n in sorted(profile.items())},
            'calls': 72, 'children': sum(profile.values()), 'rank_mass': 520704,
            'live': 7168, 'm': 73, 'deficit': 2560, 'endpoints': rows, 'controls': controls}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true',
                        help='explicitly replace this package certificate after recomputing all checks')
    args = parser.parse_args()
    certificate = build_certificate()
    path = HERE / 'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(json.dumps(certificate, indent=2) + '\n', encoding='utf-8')
    else:
        require(json.loads(path.read_text(encoding='utf-8')) == certificate, 'certificate differs')
    print(certificate['status'])
    print(f"4 strict endpoints; 72 calls; {certificate['children']} children; "
          f"{certificate['controls']['integer_power_comparisons']} integer-power controls; "
          '2 kernel mutants; 6 mathematical controls.')


if __name__ == '__main__':
    main()
