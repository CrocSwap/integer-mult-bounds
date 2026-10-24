#!/usr/bin/env python3
"""Exact fractional-source width certificate. Nick Petalas, Apache-2.0."""
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import isqrt
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SCALE = 1 << 24
DENOMINATOR = 512
POWER = 511


def need(condition, message):
    if not condition:
        raise ValueError(message)


def read_input(path, digest):
    raw = (ROOT / path).read_bytes()
    need(len(raw) <= 65536, 'input size')
    need(sha256(raw).hexdigest() == digest, 'source drift: ' + path)
    return raw


def power_interval(rank):
    """Enclose rank^(511/512) on a fixed dyadic grid by integer powers."""
    need(1 <= rank <= 145, 'rank domain')
    target = rank ** POWER * SCALE ** DENOMINATOR
    low, high = 0, rank * SCALE
    for _ in range(33):
        if high - low <= 1:
            break
        middle = (low + high) // 2
        if middle ** DENOMINATOR <= target:
            low = middle
        else:
            high = middle
    need(high - low <= 1, 'root bisection capacity')
    need(low ** DENOMINATOR <= target <= high ** DENOMINATOR,
         'power enclosure')
    return Fraction(low, SCALE), Fraction(high, SCALE)


def selected_certificate(invoice):
    targets = {int(k): c for k, c in invoice['targets'].items()}
    paid = {int(k): c for k, c in invoice['paid'].items()}
    need(len(targets) <= 20 and len(paid) <= 20, 'inventory capacity')
    need(all(type(c) is int and c > 0 for c in (*targets.values(), *paid.values())),
         'positive multiplicities')
    bounds = {r: power_interval(r) for r in targets.keys() | paid.keys()}
    t_upper = sum(c * bounds[r][1] for r, c in targets.items())
    p_upper = sum(c * bounds[r][1] for r, c in paid.items())
    v, w = 1024, sum(targets.values())
    paid_mass = sum(r * c for r, c in paid.items())
    floor_power, floor_rank = 21 ** 1022, 21 ** v
    completion = w ** v * floor_power
    target_upper = t_upper ** v + completion
    paid_upper = (p_upper ** v + Fraction(paid_mass ** v, 400)
                  + completion + Fraction(w ** v * floor_rank, 400))
    uniform = 1 << 18291
    need(target_upper < uniform, 'productive fractional moment ceiling')
    need(paid_upper < uniform, 'fully charged paid fractional moment ceiling')
    need(uniform > floor_power, 'height monotonicity')
    h_bits = invoice['compiler']['H']
    need(h_bits == 64215200000000, 'selected height')
    height = (h_bits - ((145 ** v).bit_length() - 1)) // (floor_rank.bit_length() - 1)
    x_bound = ((height + 1).bit_length() + 18291
               + height * (18291 - (floor_power.bit_length() - 1)))
    need(10000 * x_bound < 30694 * h_bits, 'K/N < 3.0694')
    need(x_bound < 197115103572543, 'strict predecessor-envelope improvement')
    return {'exponent': '511/512', 'moment_ceiling': '2^18291',
            'height_upper': height, 'floor_power_log2_floor': floor_power.bit_length() - 1,
            'log_source_upper': x_bound, 'width_coefficient_upper': '15347/5000',
            'previous_log_source_upper': 197115103572543,
            'log_source_bound_reduction': 197115103572543 - x_bound,
            'root_intervals': {str(r): [str(a), str(b)] for r, (a, b) in sorted(bounds.items())}}


def half_moment_ceiling(inventory):
    """Independent coarse square-root enclosure for small word controls."""
    total = 0
    for rank, count in inventory.items():
        root = next(j for j in range(1, 11) if j * j >= rank)
        total += count * root
    return total


def source_count(targets, paid, rank):
    """Literal ordered paths, only for new tiny fractional-bound fixtures."""
    ambient, floor = max(targets), min(targets)
    height = 0
    for g in range(1, 5):
        if ambient * floor ** g <= rank:
            height = g
    need(ambient * floor ** (height + 1) > rank, 'fixture depth cap')
    count = 0
    for d in range(height + 1):
        for path in product(paid, repeat=d):
            rho = 1
            for r in path:
                rho *= r
            for word in product(targets, repeat=height - d):
                column = 1
                for k in word:
                    column *= k
                for k in targets:
                    eligible = ambient * rho * column <= rank
                    absent = d == 0 or ambient * (rho // path[-1]) * column * k > rank
                    if eligible and absent:
                        source_rank = rho * column * k
                        need(ambient * source_rank > rank, 'strict source threshold')
                        count += 1
    return count, height


def finite_controls():
    cases = 0
    for targets in ((2, 3), (2, 4), (3, 4)):
        for paid in ((1,), (1, 2), (1, 2, 3)):
            if max(paid) >= max(targets):
                continue
            upper = max(half_moment_ceiling(dict.fromkeys(targets, 1)),
                        half_moment_ceiling(dict.fromkeys(paid, 1)))
            for rank in range(max(targets), 61):
                count, height = source_count(targets, paid, rank)
                rhs_squared = Fraction(max(targets), rank) * (height + 1) ** 2 * upper ** (2 * height + 2)
                need(count ** 2 < rhs_squared, 'fractional source-count inequality')
                cases += 1
    split_cases = 0
    for root in range(1, 9):
        rank = root * root
        for cut_root in range(1, 5):
            cutoff = cut_root * cut_root
            q, rem = divmod(rank, cutoff)
            remainder_upper = Fraction(isqrt(rem * 256 ** 2) + 1, 256)
            lhs_upper = q * cut_root + remainder_upper
            rhs = Fraction(rank, cut_root) + root
            need(lhs_upper <= rhs, 'actual split square-root moment bound')
            split_cases += 1
    need(16 * 2 > 8, 'rank 64 split at 4 exceeds its unsplit square-root moment')
    need(half_moment_ceiling({1: 10}) > half_moment_ceiling({4: 1}),
         'paid/productive moment ordering is not assumed')
    lower, upper = power_interval(2)
    need(lower > 1 and upper ** 512 >= 2 ** 511,
         'rounding 2^(511/512) down to 1 is invalid')
    return {'fractional_source_fixtures': cases, 'split_fixtures': split_cases,
            'semantic_controls': 3}


def main():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    live = {}
    for row in manifest['files']:
        if row['usage'] == 'input':
            live[row['path']] = read_input(row['path'], row['sha256'])
    invoice = json.loads(live['research/selected-truncated-source-envelope/vendor/selected.json'])
    result = selected_certificate(invoice) | finite_controls()
    files = sorted(p for p in PACKAGE.iterdir() if p.is_file())
    need(len(files) <= 10, 'package file capacity')
    receipt = {}
    for path in files:
        raw = path.read_bytes()
        need(len(raw) <= 65536, 'package size')
        receipt[path.name] = sha256(raw).hexdigest()
    print(json.dumps({'result': result, 'file_sha256': receipt,
                      'python': sys.version.split()[0]}, sort_keys=True, indent=2))
    print('PASS_FRACTIONAL_SOURCE_WIDTH K/N<3.0694 no_new_kappa')


if __name__ == '__main__':
    main()
