"""Exact certificates for a finite menu of nonnegative child rows.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Classical M-matrix alternative and Bellman policy iteration.
"""
from fractions import Fraction as Q
import argparse
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rational(x):
    require(type(x) in (int, str), 'Use integers or rational strings')
    q = Q(x)
    require(max(abs(q.numerator).bit_length(), q.denominator.bit_length()) <= 8192,
            'Rational exceeds the 8192-bit budget')
    return q


def parse(problem):
    require(type(problem) is dict and set(problem) == {'schema', 'rows'}
            and problem['schema'] == 'adaptive-row-bill/v1', 'Invalid problem')
    raw = problem['rows']
    require(type(raw) is list and 1 <= len(raw) <= 64, 'Use 1..64 types')
    n = len(raw)
    rows = []
    for choices in raw:
        require(type(choices) is list and 1 <= len(choices) <= 64,
                'Use 1..64 choices per type')
        parsed = []
        for row in choices:
            require(type(row) is list and len(row) == n, 'Wrong row width')
            values = list(map(rational, row))
            require(all(x >= 0 for x in values), 'Negative child coefficient')
            parsed.append(values)
        rows.append(parsed)
    return rows


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), Q(0))


def fixed_policy(matrix):
    """Return the unit-toll total or a nonnegative subeigenvector."""
    n = len(matrix)
    a = [[Q(i == j)-matrix[i][j] for j in range(n)]+[Q(1)]
         for i in range(n)]
    for k in range(n):
        if a[k][k] <= 0:
            v = [Q(0)]*n
            v[k] = Q(1)
            for i in reversed(range(k)):
                v[i] = -dot(a[i][i+1:n], v[i+1:])/a[i][i]
            return None, v
        for i in range(k+1, n):
            if a[i][k]:
                factor = a[i][k]/a[k][k]
                for j in range(k, n+1):
                    a[i][j] -= factor*a[k][j]
    total = [Q(0)]*n
    for i in reversed(range(n)):
        total[i] = (a[i][n]-dot(a[i][i+1:n], total[i+1:]))/a[i][i]
    return total, None


def certify(problem, limit=4096):
    rows = parse(problem)
    require(type(limit) is int and limit > 0, 'Invalid policy budget')
    policy = [0]*len(rows)
    for step in range(limit):
        total, witness = fixed_policy([r[a] for r, a in zip(rows, policy)])
        if witness is not None:
            result = {'schema': 'adaptive-row-certificate/v1', 'status': 'unsafe',
                      'policy': policy, 'witness': list(map(str, witness))}
            check(problem, result)
            return result
        updated = policy.copy()
        for i, choices in enumerate(rows):
            values = [dot(row, total) for row in choices]
            best = max(range(len(choices)), key=values.__getitem__)
            if values[best] > total[i]-1:
                updated[i] = best
        if updated == policy:
            q = max((x-1)/x for x in total)
            result = {'schema': 'adaptive-row-certificate/v1', 'status': 'safe',
                      'policy': policy, 'total': list(map(str, total)),
                      'ratio': str(q)}
            check(problem, result)
            return result
        policy = updated
    raise ValueError('Policy budget exhausted; no certificate produced')


def check(problem, result):
    """Check row inequalities and one attaining policy, without elimination."""
    rows = parse(problem)
    n = len(rows)
    require(type(result) is dict and result.get('schema') == 'adaptive-row-certificate/v1',
            'Invalid certificate')
    policy = result.get('policy')
    require(type(policy) is list and len(policy) == n
            and all(type(a) is int and 0 <= a < len(rows[i])
                    for i, a in enumerate(policy)), 'Invalid policy')
    def vector(name):
        value = result.get(name)
        require(type(value) is list and len(value) == n, 'Wrong '+name+' width')
        return list(map(rational, value))
    if result.get('status') == 'unsafe':
        v = vector('witness')
        require(all(x >= 0 for x in v) and any(v), 'Invalid witness')
        require(all(dot(rows[i][a], v) >= v[i] for i, a in enumerate(policy)),
                'False unsafe witness')
        return True
    require(result.get('status') == 'safe', 'Invalid status')
    total = vector('total')
    q = rational(result.get('ratio'))
    require(all(x >= 1 for x in total) and 0 <= q < 1, 'Invalid total or ratio')
    for i, choices in enumerate(rows):
        require(all(1+dot(row, total) <= total[i] for row in choices),
                'An allowed row exceeds the bill')
        require(1+dot(choices[policy[i]], total) == total[i], 'Policy does not attain total')
        require(all(dot(row, total) <= q*total[i] for row in choices),
                'False common contraction ratio')
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem', type=Path)
    parser.add_argument('--check', type=Path)
    parser.add_argument('--policy-limit', type=int, default=4096)
    args = parser.parse_args()
    problem = json.loads(args.problem.read_text())
    if args.check:
        check(problem, json.loads(args.check.read_text()))
        print('PASS_ADAPTIVE_ROW_CERTIFICATE')
    else:
        print(json.dumps(certify(problem, args.policy_limit), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
