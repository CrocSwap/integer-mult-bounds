"""Necessary Boolean support conditions, with replayable DPLL refutations.

Over C, one nonzero monomial cannot sum to zero. Two or more may or may not
cancel. SAT is therefore only a relaxation; UNSAT excludes the whole word.
"""
from collections import Counter
from itertools import permutations
import time

from model import Engine, generic_paths, coefficient_records


def encode_support(records, targets, blocks):
    clauses, labels = [], [None]
    rank_support = [[any(r['output'] == i and r['column'] == j and r['rank'] == 3
                         for r in records) for j in range(3)] for i in range(3)]
    # Augmentation sends every group element to 1 and preserves invertibility.
    # Its possible nonzero entries must admit a determinant matching.
    if not any(all(rank_support[r][p[r]] for r in range(3)) for p in permutations(range(3))):
        clauses.append([])
    def variable(label):
        labels.append(label)
        return len(labels)-1
    for k in range(blocks):
        for r in range(3):
            for c in range(3):
                variable(['entry', k, r, c])
    # Nonsingular matrix => at least one nonzero determinant summand.
    matchings = []
    for k in range(blocks):
        choices = []
        for permutation in permutations(range(3)):
            v = variable(['matching', k, list(permutation)])
            choices.append(v)
            for row, col in enumerate(permutation):
                clauses.append([-v, 9*k+3*row+col+1])
        clauses.append(choices)
        matchings.append(choices)
    frames = []
    for column, candidates in enumerate(targets):
        choices = {frame: variable(['frame', column, frame]) for frame in sorted(candidates)}
        clauses.append(list(choices.values()))
        for i, a in enumerate(choices.values()):
            for b in list(choices.values())[i+1:]:
                clauses.append([-a, -b])
        frames.append(choices)
    terms = {}
    for record in records:
        paths = []
        for mask, coefficient in sorted(record['poly'].items()):
            assert coefficient != 0 and mask.bit_count() == blocks
            if mask not in terms:
                v = variable(['term', mask])
                factors = [i+1 for i in range(9*blocks) if mask & (1 << i)]
                for factor in factors:
                    clauses.append([-v, factor])
                clauses.append([v, *(-factor for factor in factors)])
                terms[mask] = v
            paths.append(terms[mask])
        guard = [frames[record['column']][record['frame']]] if record['rank'] == 3 else []
        for v in paths:
            clauses.append([-v, *(p for p in paths if p != v), *guard])
    return {'clauses': clauses, 'labels': labels, 'variables': len(labels)-1,
            'blocks': blocks, 'target_frames': [sorted(t) for t in targets],
            'rank_supported_entries': rank_support}


def compile_support(program):
    ring = Engine()
    rows, blocks = generic_paths(ring, program, 3)
    records, targets = coefficient_records(ring, rows)
    return encode_support(records, targets, blocks)


class Limit(Exception):
    pass


def solve(cnf, seconds=1, max_nodes=40000):
    started = time.monotonic()
    encoded, frequency = [], Counter()
    for clause in cnf['clauses']:
        positive = sum(1 << (v-1) for v in set(clause) if v > 0)
        negative = sum(1 << (-v-1) for v in set(clause) if v < 0)
        assert not positive & negative
        encoded.append((positive, negative))
        for v in clause:
            frequency[abs(v)] += 1
    nodes, propagations = 0, 0
    def visit(yes, no):
        nonlocal nodes, propagations
        nodes += 1
        if nodes > max_nodes or time.monotonic()-started >= seconds:
            raise Limit
        units = []
        while True:
            changed, best = False, None
            for index, (positive, negative) in enumerate(encoded):
                if positive & yes or negative & no:
                    continue
                remaining = (positive | negative) & ~(yes | no)
                if not remaining:
                    return None, {'units': units, 'conflict': index}
                count = remaining.bit_count()
                if count == 1:
                    variable = remaining.bit_length()
                    literal = variable if remaining & positive else -variable
                    units.append([literal, index])
                    if literal > 0:
                        yes |= remaining
                    else:
                        no |= remaining
                    propagations += 1
                    changed = True
                elif best is None or count < best[0]:
                    best = count, remaining
            if not changed:
                break
        if best is None:
            return [int(bool(yes & (1 << i))) for i in range(cnf['variables'])], None
        candidates = [i+1 for i in range(cnf['variables']) if best[1] & (1 << i)]
        variable = max(candidates, key=lambda i: (frequency[i], -i))
        bit = 1 << (variable-1)
        model, positive = visit(yes | bit, no)
        if model is not None:
            return model, None
        model, negative = visit(yes, no | bit)
        if model is not None:
            return model, None
        return None, {'units': units, 'split': variable, 'positive': positive, 'negative': negative}
    try:
        model, proof = visit(0, 0)
        status = 'support_feasible' if model is not None else 'support_obstruction'
    except Limit:
        model, proof, status = None, None, 'resource_limit'
    return {'status': status, 'model': model, 'proof': proof, 'nodes': nodes,
            'propagations': propagations, 'elapsed_seconds': time.monotonic()-started,
            'limits': {'seconds': seconds, 'nodes': max_nodes}}


def verify(cnf, result):
    """Literal-list clause replay; independent of the bitset solving routine."""
    clauses = cnf['clauses']
    if result['status'] == 'support_feasible':
        model = result['model']
        assert len(model) == cnf['variables'] and all(v in (0, 1) for v in model)
        assert all(any(bool(model[abs(v)-1]) == (v > 0) for v in clause) for clause in clauses)
        assert result['proof'] is None
        return 0
    if result['status'] == 'resource_limit':
        assert result['proof'] is None and result['model'] is None
        return 0
    assert result['status'] == 'support_obstruction' and result['model'] is None
    nodes = 0
    def check(node, assignment):
        nonlocal nodes
        nodes += 1
        assignment = dict(assignment)
        def residual(index):
            assert 0 <= index < len(clauses)
            literals = []
            for literal in clauses[index]:
                variable = abs(literal)
                if variable not in assignment:
                    literals.append(literal)
                else:
                    assert assignment[variable] != (literal > 0), ('already satisfied', index)
            return literals
        for literal, reason in node['units']:
            assert residual(reason) == [literal]
            assert abs(literal) not in assignment
            assignment[abs(literal)] = literal > 0
        if 'conflict' in node:
            assert not residual(node['conflict'])
        else:
            v = node['split']
            assert 1 <= v <= cnf['variables'] and v not in assignment
            check(node['positive'], {**assignment, v: True})
            check(node['negative'], {**assignment, v: False})
    check(result['proof'], {})
    return nodes


def selected_support(cnf, result):
    assert result['status'] == 'support_feasible'
    entries = [[0]*9 for _ in range(cnf['blocks'])]
    frames = [None]*3
    for label, value in zip(cnf['labels'][1:], result['model']):
        if label[0] == 'entry':
            _, k, r, c = label
            entries[k][3*r+c] = value
        elif label[0] == 'frame' and value:
            frames[label[1]] = label[2]
    return {'entry_support': entries, 'frames': frames}
