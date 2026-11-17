#!/usr/bin/env python3
"""Corroborate the new divisor; never import or replay a predecessor verifier."""
import argparse
import hashlib
import json
import platform
from itertools import combinations_with_replacement
from pathlib import Path

from width import (MAX_N, library, literal_census, maximum_visits, plateaus,
                   require, semigroup, validate_rule)

ROOT = Path(__file__).resolve().parent


def fixtures():
    rules = []
    for ambient in range(3, 9):
        for targets in combinations_with_replacement(range(2, ambient + 1), 2):
            for paid in ((1,), (1, 1), (min(targets) - 1,)):
                for maximum in (ambient - 1, 2 * ambient - 1, 5 * ambient + 1):
                    rules.append((ambient, targets, paid, maximum))
    rules.extend([(4, (3, 3), (2, 2), 12),
                  (7, (3, 5, 7), (1, 2), 100),
                  (8, (4, 6), (1, 2, 3), 128),
                  (9, (3, 6, 9), (2, 2), 180)])
    return sorted(set(rules))


def check_libraries():
    counts = dict(libraries=0, base_only_libraries=0, width_rows=0, plateau_rows=0, strict_divisors=0,
                  exact_additive_visits=0, strict_visit_bounds=0)
    digest = hashlib.sha256()
    for ambient, targets, paid, maximum in fixtures():
        rows, widths, children, refined, old = library(ambient, targets, paid, maximum)
        require(all(refined % b == 0 for b in widths), "new divisor misses a width")
        require(old % refined == 0, "new divisor does not divide old divisor")
        counts['libraries'] += 1
        counts['base_only_libraries'] += maximum < ambient
        counts['width_rows'] += maximum
        counts['strict_divisors'] += refined < old
        for low, high, sources, exits, bound, tau in rows:
            actual = maximum_visits(children, low, high)
            require(actual == bound, "literal maximum differs from new visit bound")
            counts['plateau_rows'] += 1
            counts['exact_additive_visits'] += actual == bound
            counts['strict_visit_bounds'] += bound < tau
            require(all(child < low for child in exits), "paid exit did not leave plateau")
            require(min(sources) > low // ambient, "fresh-source floor fails")
        encoded = [ambient, targets, paid, maximum, widths, refined, old]
        digest.update(json.dumps(encoded, separators=(',', ':')).encode())
    counts['computed_library_sha256'] = digest.hexdigest()
    return counts


def check_sharpness():
    """For cap one the refinement is exact, including truncated last plateaus."""
    cases = 0
    for ambient in range(3, 101):
        for maximum in (ambient, ambient + (ambient - 1) // 2, 2 * ambient - 1):
            rows, widths, children, refined, old = library(ambient, (2, 3), (1,), maximum)
            low, high, sources, exits, bound, tau = rows[0]
            require(bound == (maximum - ambient) // 2 + 1, "wrong endpoint rounding")
            require(refined == 2 ** bound, "unexpected cap-one divisor")
            require(max(widths) == refined, "cap-one divisor is not attained")
            require(maximum_visits(children, low, high) == bound, "visit bound not attained")
            require(old == 2 ** ambient and sources == {2: 1, 3: 1} and exits == (1,),
                    "sharpness fixture changed")
            cases += 1
    return {'attaining_truncated_plateaus': cases,
            'A64_N127_old_divisor': str(2 ** 64),
            'A64_N127_new_divisor': str(2 ** 32)}


def reject(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError('accepted invalid case: ' + message)


def check_controls():
    invalid = (
        ('boolean ambient', lambda: validate_rule(True, (2,), (1,), 4)),
        ('unbounded library', lambda: validate_rule(2, (2,), (1,), MAX_N + 1)),
        ('no productive role', lambda: validate_rule(4, (), (1,), 8)),
        ('no paid site', lambda: validate_rule(4, (2,), (), 8)),
        ('unseparated ranks', lambda: validate_rule(4, (2,), (2,), 8)),
        ('target beyond ambient', lambda: validate_rule(4, (5,), (1,), 8)),
        ('rank-one target', lambda: validate_rule(4, (1,), (1,), 8)),
        ('noninteger rank', lambda: validate_rule(4, (2.0,), (1,), 8)),
        ('unit generator', lambda: semigroup((1, 2), 20)),
        ('zero census cap', lambda: literal_census(4, (2, 3), (1,), 0)),
        ('zero maximum', lambda: plateaus(4, (2, 3), (1,), 0)),
    )
    for name, call in invalid:
        reject(call, name)
    rows, widths, children, refined, old = library(64, (2, 3), (1,), 127)
    semantic = {'lowered exponent': refined // 2 % max(widths) != 0}
    wrong_visits = 1 + (127 - 64) // max(rows[0][2])
    semantic['maximum source replaces minimum'] = 2 ** wrong_visits % max(widths) != 0
    # Dropping the final +1 omits one actual visit.
    rows, widths, children, refined, old = library(7, (2, 3), (1,), 13)
    semantic['dropped final plus one'] = 2 ** ((13 - 7) // 2) % max(widths) != 0
    # A same-plateau exit invalidates the minimum-complement argument.
    fake = [()] * 8
    fake[6], fake[7] = (5,), (6,)
    semantic['same-plateau exits'] = maximum_visits(fake, 5, 7) > 1 + (7 - 5) // 3
    # Repeated exits are separate cuts, each requiring two copies.
    sources, exits = literal_census(4, (3, 3), (2, 2), 3)
    rows, widths, children, refined, old = library(4, (3, 3), (2, 2), 12)
    semantic['pooled chronological cuts'] = (
        exits == (4, 4, 4, 4) and widths[4] == 2 and widths[12] == 8 and widths[12] != 4)
    for name, detected in semantic.items():
        require(detected, 'semantic control failed: ' + name)
    return {'controls': len(invalid) + len(semantic)}


def receipt(result):
    names = ('PROOF.md', 'README.md', 'SOURCES.json', 'TASK.json',
             'VERIFY.json', 'verify.py', 'width.py')
    files = [ROOT / name for name in names]
    return {'result': result, 'python': platform.python_version(),
            'sources': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path)
    args = parser.parse_args()
    result = {**check_libraries(), **check_sharpness(), **check_controls()}
    if args.record is not None:
        require(args.record.is_absolute(), 'record path must be absolute')
        path = args.record.resolve()
        require(not path.is_relative_to(ROOT),
                'record must be external to the package')
        with path.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(receipt(result), indent=2, sort_keys=True) + '\n')
    print('PASS_ADDITIVE_PLATEAU_WIDTH ' + json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
