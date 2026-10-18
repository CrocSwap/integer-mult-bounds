#!/usr/bin/env python3
"""Direct set-based LP arithmetic, separate from verify.py; same AI author.

This is a second arithmetic method, not independent human review. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path

N = (0, 1, 3, 6, 12, 20, 36, 63, 120)
G = {5: 12, 7: 36, 1: 1}


def check(fixture):
    d = fixture['d']
    weights = fixture['weights']
    roles = tuple(range(len(weights)))
    terms = []
    seen = set()
    for mask, value in fixture['primal']:
        support = frozenset(i for i in roles if mask & (2 ** i))
        amount = Fraction(value)
        if not support or support in seen or amount < 0 or mask >= 2 ** len(roles):
            raise ValueError('bad term')
        seen.add(support)
        terms.append((support, amount))
    count = 0
    for size in range(1, len(roles) + 1):
        upper = N[size + 8 - d] if size + 8 - d < 8 else 112
        for selected in combinations(roles, size):
            selected = set(selected)
            actual = sum(amount for support, amount in terms if support.issubset(selected))
            if actual > upper:
                raise ValueError('subset bound')
            count += 1
    for i, w in enumerate(weights):
        if sum(amount for support, amount in terms if i in support) > G[w]:
            raise ValueError('piece capacity')
    if sum(amount for support, amount in terms) != 112:
        raise ValueError('objective')
    return count


def reject(fixture):
    try:
        check(fixture)
    except ValueError:
        return
    raise ValueError('mutation accepted')


def main():
    fixtures = json.loads(Path(__file__).with_name('WITNESSES.json').read_text(encoding='utf-8'))
    count = sum(check(f) for f in fixtures)
    if count != 1916:
        raise ValueError('coverage count')
    for fixture in fixtures:
        # Reverse every role, including its capacity and every subset label.
        moved = deepcopy(fixture)
        a = len(moved['weights'])
        moved['weights'].reverse()
        for term in moved['primal']:
            term[0] = sum(2 ** (a - 1 - i) for i in range(a) if term[0] & 2 ** i)
        if check(moved) != (2 ** a) - 1:
            raise ValueError('permutation coverage')
    bad = deepcopy(fixtures[0]); bad['primal'].pop()
    reject(bad)
    bad = deepcopy(fixtures[0]); bad['primal'][0][1] = '113'
    reject(bad)
    bad = deepcopy(fixtures[0]); bad['weights'] = [1] * len(bad['weights'])
    reject(bad)
    bad = deepcopy(fixtures[0]); bad['d'] = 8
    reject(bad)
    print('PASS_DIRECT_INPUT_LP cases=4 constraints=1916 reversed_roles=4 rejected_mutants=4')


if __name__ == '__main__':
    main()
