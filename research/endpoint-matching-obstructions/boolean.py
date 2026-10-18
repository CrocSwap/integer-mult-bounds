"""Necessary support encoding and independent resolution replay. See PROOF.md."""
from itertools import permutations

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

def coefficients(records):
    answer = []
    targets = [set(), set(), set()]
    for record in sorted(records, key=lambda r: (r['output'], r['column'], r['group'])):
        poly = {}
        for path in record['paths']:
            trajectory = (record['column'], *path, record['output'])
            mask = sum(1 << (9*k+3*trajectory[k+1]+trajectory[k]) for k in range(len(trajectory)-1))
            poly[mask] = poly.get(mask, 0)+1
        answer.append({k: record[k] for k in ('output', 'column', 'rank', 'frame')} | {'poly': poly})
        if record['rank'] == 3:
            targets[record['column']].add(record['frame'])
    return answer, targets

def formula(records, blocks, certificates):
    coefs, targets = coefficients(records)
    cnf = encode_support(coefs, targets, blocks)
    frames = {(v[1],v[2]): i for i,v in enumerate(cnf['labels']) if v and v[0]=='frame'}
    terms = {v[1]: i for i,v in enumerate(cnf['labels']) if v and v[0]=='term'}
    for certificate in certificates:
        cnf['clauses'].append([-frames[j,f] for j,f in enumerate(certificate['frames'])])
    endpoints = []
    for permutation in permutations(range(3)):
        variable = len(cnf['labels'])
        endpoints.append(variable)
        cnf['labels'].append(['endpoint_matching', list(permutation)])
        for i,j in enumerate(permutation):
            for frame in sorted(targets[j]):
                paths = sorted({terms[mask] for c in coefs if (c['output'],c['column'],c['rank'],c['frame']) == (i,j,3,frame) for mask in c['poly']})
                cnf['clauses'].append([-variable,-frames[j,frame],*paths])
    cnf['clauses'].append(endpoints)
    cnf['variables'] = len(cnf['labels'])-1
    return cnf, coefs

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

def check(cnf, answer):
    clauses = [set(c) for c in cnf['clauses']]
    n = cnf['variables']
    if answer['status'] == 'support_feasible':
        model = answer['model']
        if len(model) != n or any(type(v) is not int or v not in (0, 1) for v in model):
            raise ValueError('Invalid Boolean model')
        if not all(any(bool(model[abs(v)-1]) == (v > 0) for v in c) for c in clauses):
            raise ValueError('Boolean model violates a clause')
        return 0
    if answer['status'] == 'resource_limit':
        if answer['model'] is not None:
            raise ValueError('Timeout claims a model')
        return 0
    if answer['status'] != 'support_obstruction' or answer['model'] is not None:
        raise ValueError('Invalid SAT status')
    for step in answer['resolution']:
        if not 0 <= step['start'] < len(clauses):
            raise ValueError('Invalid resolution source')
        derived = set(clauses[step['start']])
        for pivot, source in step['resolve']:
            if not 1 <= pivot <= n or not 0 <= source < len(clauses):
                raise ValueError('Invalid resolution edge')
            parent = clauses[source]
            if pivot in derived and -pivot in parent:
                left, right = pivot, -pivot
            elif -pivot in derived and pivot in parent:
                left, right = -pivot, pivot
            else:
                raise ValueError('Resolution pivot is not complementary')
            derived = (derived-{left}) | (parent-{right})
            if any(-v in derived for v in derived):
                raise ValueError('Tautological resolvent')
        if set(step['clause']) != derived:
            raise ValueError('Wrong learned clause')
        clauses.append(derived)
    if not clauses or clauses[-1]:
        raise ValueError('Resolution does not end in the empty clause')
    return len(answer['resolution'])
