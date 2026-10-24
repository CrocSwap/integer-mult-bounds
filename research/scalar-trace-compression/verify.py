#!/usr/bin/env python3
"""Exact changed scalar graph; Apache-2.0, substantial OpenAI assistance.

Native construction/interpreters are retained from PR4441/PR4470 with credit.
This package changes ADD dependencies, rather than only their frame labels.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(value, message):
    if not value:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def roles(event):
    if event[0] == 'scalar':
        return {tuple(r) for r in event[1][1:] if isinstance(r, list)}
    if event[0] == 'warp':
        return {tuple(event[1])}
    return set()


def is_add(event):
    return (event[0] == 'scalar' and event[1][0] == 'add'
            and all(r[0] == 'L' for r in event[1][1:3]))


def add(dst, src, coefficient, frame):
    return ['scalar', ['add', list(dst), list(src),
                       coefficient.numerator, coefficient.denominator], frame]


def combine(program):
    """Merge equal elementary matrices only across commuting instructions."""
    out, previous, writes, reads, barriers = [], {}, {}, {}, {}
    phase, merged, cancelled = -1, 0, 0
    for event in program:
        if event[0] == 'climb':
            continue
        index = len(out)
        if is_add(event):
            a, b = map(tuple, event[1][1:3])
            prior = previous.get((a, b), -1)
            barrier = max(phase, writes.get(b, -1), reads.get(a, -1),
                          barriers.get(a, -1), barriers.get(b, -1))
            if prior > barrier:
                old = out[prior]
                value = Q(*old[1][3:5]) + Q(*event[1][3:5])
                merged += 1
                if value:
                    out[prior] = add(a, b, value, old[2])
                else:
                    out[prior] = None
                    previous.pop((a, b))
                    cancelled += 1
                continue
            previous[a, b] = index
        if event[0] == 'scalar' and event[1][0] == 'add':
            a, b = map(tuple, event[1][1:3])
            writes[a], reads[b] = index, index
        else:
            for role in roles(event):
                barriers[role] = index
        if event[0] == 'phase':
            phase = index
        out.append(deepcopy(event))
    return [event for event in out if event is not None], (merged, cancelled)


def triangles(program, spaces):
    """A B A^-1 shortcuts, requiring all moved-across roles to be disjoint."""
    deleted, replacements, counts = set(), {}, Counter()
    for i, first in enumerate(program):
        if i in deleted or i in replacements or not is_add(first):
            continue
        a, b = map(tuple, first[1][1:3])
        alpha = Q(*first[1][3:5])
        j = None
        for pos in range(i+1, min(i+180, len(program))):
            event = program[pos]
            if pos in deleted or pos in replacements or event[0] == 'phase':
                break
            if roles(event) & {a, b}:
                j = pos
                break
        if j is None or not is_add(program[j]):
            continue
        middle = program[j]
        x, y = map(tuple, middle[1][1:3])
        union = {a, b, x, y}
        if len(union) != 3:
            continue
        k = None
        for pos in range(j+1, min(j+180, len(program))):
            event = program[pos]
            if pos in deleted or pos in replacements or event[0] == 'phase':
                break
            if roles(event) & union:
                k = pos
                break
        if k is None or not is_add(program[k]):
            continue
        last = program[k]
        if last[1][1:3] != first[1][1:3] or Q(*last[1][3:5]) != -alpha:
            continue
        if any(roles(event) & union for event in program[i+1:j]):
            continue
        frame = middle[2]
        if not spaces[first[2]] <= spaces[frame] <= spaces[last[2]]:
            continue
        beta = Q(*middle[1][3:5])
        if x == b and y not in {a, b}:
            replacement = [middle, add(a, y, -alpha*beta, frame)]
            kind = 'source_update'
        elif y == a and x not in {a, b}:
            replacement = [add(x, a, beta, frame), add(x, b, alpha*beta, frame)]
            kind = 'target_update'
        else:
            continue
        deleted.update((i, j, k))
        replacements[j] = replacement
        counts[kind] += 1
    result = []
    for index, event in enumerate(program):
        if index in replacements:
            result.extend(replacements[index])
        elif index not in deleted:
            result.append(event)
    return result, dict(sorted(counts.items()))


def synthesize(canonical, program, spaces):
    current, result = canonical['start'][:], []

    def climb(role, frame):
        old = current[role]
        if old == frame:
            return
        need(spaces[old] < spaces[frame], 'Strict positive nested transport')
        result.append(['climb', 'trace', role, old, frame,
                       len(canonical['frames'][frame])-len(canonical['frames'][old])])
        current[role] = frame

    for event in program:
        if event[0] == 'scalar':
            for role in sorted(roles(event)):
                if role[0] == 'L':
                    climb(role[1], event[2])
        elif event[0] == 'warp':
            climb(event[1][1], event[3])
            current[event[1][1]] = event[4]
        result.append(deepcopy(event))
    for role, frame in enumerate(canonical['final']):
        climb(role, frame)
    return result


def paid(program):
    return Counter(event[5] if event[0] == 'climb' else event[4]
                   for event in program if event[0] in ('climb', 'center'))


def controls():
    # Three genuinely noncommuting operations cannot be merged as equal ADDs.
    gates = [add(('L', 0), ('L', 1), Q(1), 0),
             add(('L', 1), ('L', 2), Q(1), 0),
             add(('L', 0), ('L', 1), Q(-1), 0)]
    need(combine(gates)[1] == (0, 0), 'A changed source blocks commutation')
    reduced, count = triangles(gates, [frozenset({0})])
    need(count == {'source_update': 1} and len(reduced) == 2,
         'Noncommutation is repaired by the actual compensating ADD')
    # Dense exact arithmetic, separate from the native sparse/free-word engines.
    def matrix(program):
        rows = [[Q(i == j) for j in range(3)] for i in range(3)]
        for event in program:
            _, dst, src, numerator, denominator = event[1]
            rows[dst[1]] = [a+Q(numerator, denominator)*b
                            for a, b in zip(rows[dst[1]], rows[src[1]])]
        return rows
    need(matrix(gates) == matrix(reduced), 'Exact dense triangle identity')
    wrong = deepcopy(reduced)
    wrong[-1][1][3] *= -1
    need(matrix(gates) != matrix(wrong), 'A wrong correction sign is detected')
    dependent = [gates[0], add(('L', 2), ('L', 0), Q(1), 0), gates[2]]
    need(combine(dependent)[1] == (0, 0), 'A reader of the target blocks commutation')


def run():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'Changed authenticated input: '+row['path'])
    controls()
    joint = load(ROOT/'research/joint-helper-lattice/native_joint.py', 'trace_joint_source')
    c, original, *_ = joint.construct()
    spaces = [joint.F.span(basis) for basis in c['frames']]
    v = joint.F.load(ROOT/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py',
                     'trace_free_rows')
    x = joint.F.load(ROOT/'research/kappa-rebuild/complex/native_extensions.py', 'trace_literal')
    result = {'status': 'PASS_CHANGED_NATIVE_SCALAR_GRAPH', 'directions': {},
              'new_kappa': None, 'paid_moment_changed': False}
    for direction, source in original.items():
        combined, merge_counts = combine(source)
        simplified, triangle_counts = triangles(combined, spaces)
        candidate = synthesize(c, simplified, spaces)
        need(paid(candidate) == paid(source), 'The complete paid profile is unchanged')
        original_edges = {(e[3], e[4]) for e in source if e[0] == 'climb'}
        new_edges = {(e[3], e[4]) for e in candidate if e[0] == 'climb'}
        need(new_edges <= original_edges, 'Every physical transport retains its old exact phase recipe')
        backward = direction == 'backward'
        rows, receipt = x.literal_replay(v, c, candidate, backward)
        for role in range(632):
            need(rows['L', role] == v.expected(('L', role), [], backward, False),
                 'Every arbitrary-input endpoint, including free warp words')
        rebound = deepcopy(c)
        rebound['local_profile'] = dict(paid(candidate))
        second = v.replay(candidate, rebound, [], backward, False)
        _, baseline = x.literal_replay(v, c, source, backward)
        need(Q(receipt['max_formal_prefix_l1']) < 2**192, 'Retained scalar-prefix envelope')
        wrong = deepcopy(candidate)
        next(e for e in wrong if e[0] == 'climb')[5] += 1
        try:
            v.replay(wrong, rebound, [], backward, False)
        except ValueError:
            pass
        else:
            raise ValueError('An under/overcharged transport was accepted')
        scalar_count = lambda p: sum(e[0] == 'scalar' for e in p)
        result['directions'][direction] = {
            'combined_pairs': merge_counts[0], 'cancelled_pairs': merge_counts[1],
            'triangles': triangle_counts, 'removed_scalar_macros': scalar_count(source)-scalar_count(candidate),
            'primitive_allowance_before': baseline['real_scalar_allowance'],
            'primitive_allowance_after': receipt['real_scalar_allowance'],
            'paid': {str(rank): count for rank, count in sorted(paid(candidate).items())},
            'all_632_columns_two_interpreters': True,
            'new_physical_transport_edges': len(new_edges-original_edges),
            'owned_center_cleared': receipt['arbitrary_owned_C0_cleared'],
            'prefix_l1': receipt['max_formal_prefix_l1'],
            'second_scalar_allowance': second['conservative_real_scalar_primitive_allowance'],
            'program_sha256': sha256(json.dumps(candidate, sort_keys=True).encode()).hexdigest()}
        print('PASS_TRACE_NATIVE', direction, flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    receipt = run()
    path = HERE/'RESULT.json'
    if args.write:
        path.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    else:
        need(receipt == json.loads(path.read_text()), 'Deterministic receipt')
    print('PASS_CHANGED_NATIVE_SCALAR_GRAPH no_new_kappa')
