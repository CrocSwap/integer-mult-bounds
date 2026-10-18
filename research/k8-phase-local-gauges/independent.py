"""Literal-lowerer oracle and distance-transform DP, independently implemented.

Philipp with substantial OpenAI Codex assistance; Apache-2.0.
This is algorithmic independence, not independent human review.
"""
from collections import defaultdict
from fractions import Fraction
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


v = module('phase_verify', HERE / 'verify.py')
lower = module('credited_pr696', v.ROOT / 'research/complex-dyadic-lowering/lower.py').lower


def p2(k):
    return Fraction(2**k) if k >= 0 else Fraction(1, 2**(-k))


def oracle(events, helper):
    """All runs, padded exponent domain, literal predecessor macro lengths.

    Unlike the main all-pairs transition recurrence, use two linear passes for
    the exact distance transform min_j (old[j] + |k-j|).
    """
    groups, current = [], []
    for event in events + [['stop']]:
        if event[0] != 'scalar':
            if current:
                groups.append(current)
            current = []
        else:
            g = event[1]
            if g[0] == 'add' and ['L', helper] in (g[1], g[2]):
                q = Fraction(g[3], g[4])
                n, d = abs(q.numerator), q.denominator
                e = 0
                while n % 2 == 0:
                    n //= 2
                    e += 1
                while d > 1:
                    d //= 2
                    e -= 1
                sign = 1 if g[1] == ['L', helper] else -1
                current.append((g, q, sign, -sign * e))
    answer, vertices = 0, 0
    for group in groups:
        lo = min([0] + [x[3] for x in group]) - 2
        hi = max([0] + [x[3] for x in group]) + 2
        ks = range(lo, hi + 1)
        costs = [abs(k) for k in ks]
        oldprice = 0
        for gate, q, sign, _ in group:
            oldprice += len(lower(gate))
            for i in range(1, len(costs)):
                costs[i] = min(costs[i], costs[i - 1] + 1)
            for i in range(len(costs) - 2, -1, -1):
                costs[i] = min(costs[i], costs[i + 1] + 1)
            for i, k in enumerate(ks):
                r = q * p2(sign * k)
                costs[i] += len(lower(['add', gate[1], gate[2], r.numerator, r.denominator]))
            vertices += len(costs)
        answer += min(costs[i] + abs(k) for i, k in enumerate(ks)) - oldprice
    return answer, vertices


def reconstruct(events, helper, plan):
    """Read the explicit schedule and build a separate literal gauge stream."""
    assignment, last = {}, set()
    for segment in plan:
        v.need(len(segment['terms']) == len(segment['path']), 'path cardinality')
        for term, k in zip(segment['terms'], segment['path']):
            v.need(term[0] not in assignment, 'duplicate event')
            assignment[term[0]] = k
        last.add(segment['terms'][-1][0])
    result, gauge = [], 0
    for index, event in enumerate(events):
        if event[0] != 'scalar':
            v.need(gauge == 0, 'non-scalar identity boundary')
            result.append(event)
            continue
        gate = event[1][:]
        if index in assignment:
            v.need(gate[0] == 'add' and ['L', helper] in (gate[1], gate[2]), 'incident schedule event')
            target = assignment[index]
            if target != gauge:
                q = p2(target - gauge)
                result.append(['scalar', ['scale', ['L', helper], q.numerator, q.denominator], event[2]])
            gauge = target
        if gate[0] == 'add':
            exponent = gauge if gate[1] == ['L', helper] else -gauge if gate[2] == ['L', helper] else 0
            q = Fraction(gate[3], gate[4]) * p2(exponent)
            gate[3:5] = [q.numerator, q.denominator]
        result.append(['scalar', gate, event[2]])
        if index in last and gauge:
            q = p2(-gauge)
            result.append(['scalar', ['scale', ['L', helper], q.numerator, q.denominator], event[2]])
            gauge = 0
    v.need(gauge == 0, 'final identity')
    return result


def primitive_replay(events, orientation):
    """All 713 formal columns, including initially dirty coefficient work."""
    roles = [('L', i) for i in range(704)] + [('C', i) for i in range(8)] + [('W', 0)]
    rows = {role: {i: Fraction(1)} for i, role in enumerate(roles)}
    count = 0
    for event in events:
        if event[0] != 'scalar':
            continue
        for op in lower(event[1]):
            count += 1
            tag, target = op[0], op[1]
            if tag == 'clear':
                rows[target] = {}
            elif tag == 'copy':
                rows[target] = dict(rows[op[2]])
            elif tag in ('double', 'halve', 'negate'):
                coefficient = {'double': 2, 'halve': Fraction(1, 2), 'negate': -1}[tag]
                rows[target] = {i: q * coefficient for i, q in rows[target].items()}
            else:
                v.need(tag in ('add', 'subtract'), 'primitive opcode')
                sign = 1 if tag == 'add' else -1
                for i, q in rows[op[2]].items():
                    new = rows[target].get(i, 0) + sign * q
                    if new:
                        rows[target][i] = new
                    else:
                        rows[target].pop(i, None)
    for i in range(704):
        expected = {i: Fraction(1)}
        if orientation == 'forward' and 112 <= i < 224:
            expected[i - 112] = Fraction(1)
        if orientation == 'backward' and i < 112:
            expected[i + 112] = Fraction(-1)
        v.need(rows['L', i] == expected, 'literal endpoint ' + str(i))
    v.need(all(not rows['C', i] for i in range(8)), 'literal centers')
    v.need(not rows['W', 0], 'literal work restoration')
    return count


def main():
    lib = v.engine()
    word, programs, _, _ = lib.load()
    cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
    total_vertices, rows_checked, primitives = 0, 0, 0
    for scenario in ('orientations', 'on_pr1214', 'wrapped_example'):
        for orientation, original in programs.items():
            events = original
            if scenario == 'on_pr1214':
                for h in (251, 427):
                    events = lib.transform(events, word, h, -2 if orientation == 'forward' else 2)
            result = cert[scenario][orientation]
            for helper, wanted, _, _ in result['rows']:
                actual, vertices = oracle(events, helper)
                v.need(actual == wanted, 'independent minimum ' + str(helper))
                total_vertices += vertices
                rows_checked += 1
            candidate = reconstruct(events, result['helper'], result['schedule'])
            v.need(v.sha(v.canonical(candidate)) == result['candidate_sha256'], 'independent candidate')
            count = primitive_replay(candidate, orientation)
            v.need(count == result['after']['real_primitives'], 'literal full invoice')
            primitives += count
    print('PASS_INDEPENDENT_PHASE_GAUGES', 'helper_minima', rows_checked,
          'padded_vertices', total_vertices, 'literal_primitives', primitives, 'columns', 713)


if __name__ == '__main__':
    main()
