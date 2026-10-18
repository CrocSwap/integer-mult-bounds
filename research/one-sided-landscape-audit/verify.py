#!/usr/bin/env python3
"""Exact documented-reduction audit, Arham Tahir/Codex, Apache-2.0.

No predecessor implementation or optimization library is imported.
"""
from copy import deepcopy
import csv
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from math import comb
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
G = (0, 1, 2, 4, 8, 12, 20, 36)
FRAME_G = (0, 1, 2, 4, 8, 12, 20, 32)
N = (0, 1, 3, 6, 12, 20, 36, 63, 120)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dp_pass(weights, d):
    """Test all deletions, independently of the source's heaviest-tail shortcut."""
    a = len(weights)
    if not (1 <= d <= 8 and all(type(w) is int and 1 <= w <= 7 for w in weights)):
        return False
    if a < d or (d >= 2 and a < d + 2):
        return False
    for k in range(1, d + 1):
        for remaining in combinations(weights, a - d + k):
            if k == 1:
                cost = sum(remaining)
                frame = sum(FRAME_G[w] for w in remaining)
                general = sum(G[w] for w in remaining)
                frame_possible = cost >= 14 and frame >= 56
                root_possible = (cost >= 15 and frame >= 53 and len(remaining) >= 3
                                 and not (len(remaining) == 3 and max(remaining) <= 6))
                other_possible = cost >= 14 and general >= 70
                if not (frame_possible or root_possible or other_possible):
                    return False
            elif sum(G[w] for w in remaining) < 112 - N[8 - k]:
                return False
    mass = sum(G[w] for w in weights)
    if d == 8 and mass + a < 224:
        return False
    if d == 7 and mass + 3 * a < 222:
        return False
    return True


def fits(weights, capacities):
    for placement in product(range(len(capacities)), repeat=len(weights)):
        if all(sum(w for w, b in zip(weights, placement) if b == j) <= cap
               for j, cap in enumerate(capacities)):
            return True
    return False


def basis_kill(weights, d):
    if d < 4:
        return False
    for anchors in combinations(weights, len(weights) - d):
        if fits(anchors, (6, 6)):
            return True
        if 1 in anchors:
            remaining = list(anchors)
            remaining.remove(1)
            if fits(remaining, (6, 6)):
                return True
    return False


def pencil_kill(weights, d):
    e = len(weights) - d
    return d >= 3 and e >= 2 and sum(G[w] for w in sorted(weights)[:e - 1]) <= 4


def triple_kill(weights, d):
    return len(weights) - d == 2 and comb(sum(w <= 6 for w in weights), 3) > 8


def lp_check(fixture):
    """Check the full unsymmetrized quotient LP using exact subset sums."""
    d, weights = fixture['d'], fixture['weights']
    a = len(weights)
    x = [Fraction(0) for _ in range(1 << a)]
    occupied = set()
    for mask, value in fixture['primal']:
        require(type(mask) is int and 0 < mask < 1 << a, 'LP mask')
        require(mask not in occupied, 'LP duplicate mask')
        occupied.add(mask)
        value = Fraction(value)
        require(value >= 0, 'LP negative')
        x[mask] = value
    subtotal = x.copy()
    for bit in range(a):
        for mask in range(1 << a):
            if mask >> bit & 1:
                subtotal[mask] += subtotal[mask ^ (1 << bit)]
    for mask in range(1, 1 << a):
        dimension = mask.bit_count() + 8 - d
        upper = 112 if dimension >= 8 else N[dimension]
        require(subtotal[mask] <= upper, 'LP subset cap')
    for bit, weight in enumerate(weights):
        use = sum(x[mask] for mask in occupied if mask >> bit & 1)
        require(use <= G[weight], 'LP piece cap')
    total = subtotal[-1]
    require(total == 112, 'LP objective')
    require(total >= 112 - N[8 - d], 'LP required coverage')
    return (1 << a) - 1, len(occupied), total


def followup_boundary(weights, d):
    """Check applicability only; no geometric covering census is replayed."""
    e = len(weights) - d
    require(e == 2 and min(weights) == 5, 'follow-up family')
    for anchors in combinations(weights, e):
        require(not fits(anchors, (7, 4)), '7+4 extension applies')
        require(not fits(anchors, (6, 6, 3)), '6+6+3 extension applies')
        for removed in ((), (1,), (1, 1), (2,)):
            remaining = list(anchors)
            for w in removed:
                if w not in remaining:
                    break
                remaining.remove(w)
            else:
                require(not fits(remaining, (6, 6)), '6+6+two-lines extension applies')
    # Only empty S has cap<=9, leaving e'=2 and one small piece, below L1's four.
    require(all(G[w] > 9 for w in weights), 'nonempty Lemma-P anchor')
    require(sum(w <= 6 for w in weights) == 1, 'Lemma-P small-piece count')
    # RRC deletes d-1 pieces (K0 and M), leaving three with cap at least 84.
    minimum_cap = min(sum(G[w] for w in kept)
                      for kept in combinations(weights, e + 1))
    require(minimum_cap == 84 and minimum_cap > 77, 'RRC cap boundary')
    return minimum_cap


def read_rows(raw):
    rows = list(csv.DictReader(raw.decode('utf-8').splitlines()))
    require(len(rows) == 603, 'input row count')
    keys = set()
    for row in rows:
        d, e, slack = (int(row[k]) for k in ('d', 'e', 'slack'))
        weights = json.loads(row['weights'])
        require(4 <= d <= 8 and 4 <= slack <= 7, 'input row domain')
        require(all(type(w) is int and 1 <= w <= 7 for w in weights), 'input weights')
        require(len(weights) - d == e and sum(weights) - 8 * d == slack,
                'input row arithmetic')
        key = d, tuple(sorted(weights))
        require(key not in keys, 'input duplicate row')
        keys.add(key)
    return keys


def source_checks():
    pins = json.loads((PACKAGE / 'SOURCES.json').read_text(encoding='utf-8'))
    for item in pins['files']:
        if item['usage'] == 'input':
            require(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest()
                    == item['sha256'], 'source pin ' + item['path'])
    for item in pins['external_inputs']:
        raw = (PACKAGE / item['local_path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item['sha256'], 'external source hash')
        blob = b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw
        require(hashlib.sha1(blob).hexdigest() == item['git_blob'], 'external Git blob')
    for item in pins.get('coordination_evidence', []):
        require(hashlib.sha256((PACKAGE / item['local_path']).read_bytes()).hexdigest()
                == item['sha256'], 'coordination source hash')


def audit(fixtures, rows):
    require(len(fixtures) == 4 and [f['d'] for f in fixtures] == list(range(5, 9)),
            'fixture domain')
    result = []
    for fixture in fixtures:
        d, w = fixture['d'], fixture['weights']
        require(w == [5] + [7] * (d + 1), 'fixture weights')
        require(dp_pass(w, d), 'DP excludes fixture')
        require(not basis_kill(w, d), 'Basis excludes fixture')
        require(not pencil_kill(w, d), 'Pencil excludes fixture')
        require(not triple_kill(w, d), 'triple excludes fixture')
        require((d, tuple(w)) not in rows, 'fixture present in source rows')
        subset_count, nonzero, total = lp_check(fixture)
        minimum = followup_boundary(w, d)
        # The author identified this additional premise during the audit.
        # Only its application is checked here; span<=4 itself is inherited.
        require(fits((5, 7), (7, 5)) and G[5] + G[7] < 53 and 4 < d,
                'conditional dominance application')
        result.append({'d': d, 'slack': 12 - d, 'e': 2, 'weights': w,
                       'LP_optimum': str(total), 'LP_need': 112 - N[8 - d],
                       'subset_constraints': subset_count, 'nonzero_terms': nonzero,
                       'minimum_RRC_cap': minimum, 'present_in_603': False,
                       'conditional_75_dominance': {'anchors': [5, 7],
                                                   'support_cap': 48,
                                                   'inherited_span_bound': 4,
                                                   'strictly_below_d': True}})
    return result


def rejects(action, expected):
    try:
        action()
    except ValueError as error:
        require(expected in str(error), 'wrong rejection: ' + str(error))
        return
    raise ValueError('accepted fault: ' + expected)


def controls(fixtures, rows):
    require(not dp_pass([1] * 7, 5), 'DP rejection control')
    require(basis_kill([7] * 6 + [6] * 4, 8), 'Basis exclusion control')
    require(pencil_kill([7] * 9 + [1], 8), 'Pencil exclusion control')
    require(triple_kill([6] * 7, 5), 'triple exclusion control')
    require((4, tuple([4, 4] + [6] * 5)) in rows, 'present-row positive control')
    require(dp_pass([4, 4] + [6] * 5, 4), 'present-row DP control')
    bad = deepcopy(fixtures[0]); bad['primal'][0][0] = 0
    rejects(lambda: lp_check(bad), 'LP mask')
    bad = deepcopy(fixtures[0]); bad['primal'].append(bad['primal'][0].copy())
    rejects(lambda: lp_check(bad), 'LP duplicate mask')
    bad = deepcopy(fixtures[0]); bad['primal'][0][1] = '-1'
    rejects(lambda: lp_check(bad), 'LP negative')
    bad = deepcopy(fixtures[0]); bad['primal'] = []
    rejects(lambda: lp_check(bad), 'LP objective')
    bad = deepcopy(fixtures[0]); bad['primal'][0][1] = '113'
    rejects(lambda: lp_check(bad), 'LP subset cap')
    bad = {'d': 5, 'weights': [1] + [7] * 6, 'primal': [[1, '2']]}
    rejects(lambda: lp_check(bad), 'LP piece cap')
    expanded = set(rows); expanded.add((5, tuple(fixtures[0]['weights'])))
    rejects(lambda: audit(fixtures, expanded), 'fixture present')
    return 13


def main():
    source_checks()
    rows = read_rows((PACKAGE / 'inputs/pr2985-rows.csv').read_bytes())
    fixtures = json.loads((PACKAGE / 'WITNESSES.json').read_text(encoding='utf-8'))
    report = {'scope': 'baseline controls and conditional dominance application; span premise not replayed; no decoder or kappa',
              'cases': audit(fixtures, rows), 'controls': controls(fixtures, rows)}
    expected = json.loads((PACKAGE / 'RESULT.json').read_text(encoding='utf-8'))
    require(report == expected, 'result receipt mismatch')
    print(json.dumps(report, indent=2))
    print('PASS_ONE_SIDED_INPUT_BOUNDARY cases=4 full_subset_constraints=1916 controls=13 no_new_kappa')


if __name__ == '__main__':
    main()
