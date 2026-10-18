"""Independent path enumeration and literal integer/Laurent proof replay."""
from collections import defaultdict
from itertools import combinations, permutations, product

from model import Engine, FREE


def layers(program):
    result = [[[] for _ in range(3)]]
    for gate in program:
        if gate[0] == 'mix3':
            result.append([[] for _ in range(3)])
        else:
            assert gate[0] in ('paid', 'free')
            op = ('C', gate[2], 0) if gate[0] == 'paid' else FREE[gate[2]]
            result[-1][gate[1]].append(op)
    return result


def group(ring, operations):
    g = 0
    for op in operations:
        g = ring.transitions(op, g)
    return g


def path_rows(ring, program):
    stages = layers(program)
    blocks = len(stages)-1
    rows = [{} for _ in range(3)]
    for trajectory in product(range(3), repeat=blocks+1):
        operations, mask = [], 0
        for k, role in enumerate(trajectory):
            operations.extend(stages[k][role])
            if k < blocks:
                mask |= 1 << (9*k+3*trajectory[k+1]+role)
        key = (group(ring, operations) << 2) | trajectory[0]
        polynomial = rows[trajectory[-1]].setdefault(key, {})
        polynomial[mask] = polynomial.get(mask, 0)+1
    return tuple(rows), blocks


def rank_formula(program, cnf):
    """Build strengthened clauses from unary products, not path polynomials."""
    ring, stages = Engine(), layers(program)
    assert len(stages) == 4
    selectors = {(x[1], x[2]): i for i, x in enumerate(cnf['labels']) if x and x[0] == 'frame'}
    products = defaultdict(list)
    for i in range(3):
        for j in range(3):
            products[group(ring, stages[1][j]+stages[2][i])].append(3*i+j)
    counts = defaultdict(int)
    for cells in sorted(tuple(v) for v in products.values()):
        if len({p//3 for p in cells}) != len(cells) or len({p % 3 for p in cells}) != len(cells):
            continue
        i, j = divmod(cells[0], 3)
        guards = {}
        for r in range(3):
            for s in range(3):
                g = group(ring, stages[0][s]+stages[1][j]+stages[2][i]+stages[3][r])
                frame, rank = ring.frame_info(g)
                if rank == 3:
                    guards[r, s] = selectors[s, frame]
        for s, frames in enumerate(cnf['target_frames']):
            for frame in frames:
                f = selectors[s, frame]
                if any(guards.get((r, s)) == f for r in range(3)):
                    continue
                for position in cells:
                    cnf['clauses'].append([-f, -(10+position), -(3*(position % 3)+s+1)])
                    counts['zero_column'] += 1
        for r in range(3):
            allowed = sorted({guards[r, s] for s in range(3) if (r, s) in guards})
            for position in cells:
                cnf['clauses'].append([-(19+3*r+position//3), -(10+position), *allowed])
                counts['zero_row'] += 1
        for size in range(1, len(cells)+1):
            variables = []
            for rs in combinations(range(3), size):
                for ss in permutations(range(3), size):
                    matching = tuple(zip(rs, ss))
                    if any(p not in guards for p in matching):
                        continue
                    cnf['labels'].append(['rank_matching', list(cells), list(map(list, matching))])
                    v = len(cnf['labels'])-1
                    variables.append(v)
                    for f in sorted({guards[p] for p in matching}):
                        cnf['clauses'].append([-v, f])
            for subset in combinations(cells, size):
                cnf['clauses'].append([*(-(10+p) for p in subset), *variables])
                counts['rank_bound'] += 1
    cnf['variables'] = len(cnf['labels'])-1
    cnf['strengthening_counts'] = dict(counts)
    return cnf


def diagonal_trace(equations, certificate):
    a = [list(row) for row in equations['matrix']]
    b = list(equations['rhs_parity'])
    n = len(equations['nonzero_entries'])
    transform = [[int(i == j) for j in range(n)] for i in range(n)]
    for step in certificate['steps']:
        op, *args = step
        if op == 'row_swap':
            i, j = args
            assert 0 <= i < len(a) and 0 <= j < len(a) and i != j
            a[i], a[j] = a[j], a[i]
            b[i], b[j] = b[j], b[i]
        elif op == 'row_negate':
            i, = args
            a[i] = [-v for v in a[i]]
            b[i] = -b[i]
        elif op == 'row_add':
            i, j, amount = args
            assert i != j and type(amount) is int
            a[i] = [a[i][k]+amount*a[j][k] for k in range(n)]
            b[i] += amount*b[j]
        elif op == 'col_swap':
            i, j = args
            assert 0 <= i < n and 0 <= j < n and i != j
            for row in a+transform:
                row[i], row[j] = row[j], row[i]
        else:
            assert op == 'col_add'
            i, j, amount = args
            assert i != j and type(amount) is int
            for row in a+transform:
                row[i] += amount*row[j]
    rank = certificate['rank']
    assert certificate['column_transform'] == transform and certificate['rhs'] == b
    assert [a[i][i] for i in range(rank)] == certificate['diagonal']
    assert all(v > 0 for v in certificate['diagonal'])
    assert all(not a[i][j] for i in range(len(a)) for j in range(n) if i != j or i >= rank)


def determinant_identity(equations, certificate, signs):
    """One direct Leibniz expansion of the product, not successive products."""
    rank = certificate['rank']
    transform = certificate['column_transform']
    dimension = len(transform)-rank
    entries = {old: new for new, old in enumerate(equations['nonzero_entries'])}
    coefficients = defaultdict(int)
    all_permutations = tuple(permutations(range(3)))
    for choices in product(all_permutations, repeat=equations['blocks']):
        chosen = [9*k+3*r+permutation[r] for k, permutation in enumerate(choices) for r in range(3)]
        if any(entry not in entries for entry in chosen):
            continue
        exponents = [sum(transform[entries[entry]][j] for entry in chosen) for j in range(len(transform))]
        phase = sum(exponents[i]*signs[i] for i in range(rank))
        phase += sum(p[i] > p[j] for p in choices for i in range(3) for j in range(i+1, 3))
        coefficients[tuple(exponents[rank:])] += (-1)**(phase % 2)
    return {e: c for e, c in coefficients.items() if c}


def binomial_certificate(expected, result):
    assert result['equations'] == expected
    cert = result['diagonalization']
    diagonal_trace(expected, cert)
    odd = any(v % 2 for v in cert['rhs'][cert['rank']:])
    if result['status'] == 'inconsistent_torus':
        assert odd
        return
    assert not odd and result['status'] in ('all_components_singular', 'exact_rational_point')
    choices = []
    for d, b in zip(cert['diagonal'], cert['rhs']):
        assert d == 1 or (d == 2 and b % 2 == 0)
        choices.append([b % 2] if d == 1 else [0, 1])
    expected_signs = list(map(list, product(*choices)))
    if result['status'] == 'all_components_singular':
        assert [c['signs'] for c in result['components']] == expected_signs
    for component in result['components']:
        assert component['signs'] in expected_signs
        polynomial = determinant_identity(expected, cert, component['signs'])
        assert bool(polynomial) != component['determinant_product_zero']
        if result['status'] == 'all_components_singular':
            assert not polynomial
