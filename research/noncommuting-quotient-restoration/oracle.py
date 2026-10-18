"""Separately represented numerical columns and six-coordinate boundary census.

No import of model.py. Apache-2.0; substantial OpenAI Codex assistance.
"""
from itertools import product

ONE = tuple(range(6))
PA = (2, 3, 0, 1, 5, 4)
PB = (1, 0, 4, 5, 2, 3)
R = (1, -1, -1, 1, 1, -1)


def multiply(left, right):
    # Pull permutations, independently of the primary three-point group model.
    return tuple(right[left[i]] for i in range(6))


def reciprocal(p):
    return tuple(p.index(i) for i in range(6))


def group():
    found = {ONE}
    pending = [ONE]
    while pending:
        p = pending.pop()
        for g in (PA, PB):
            q = multiply(g, p)
            if q not in found:
                found.add(q)
                pending.append(q)
    return tuple(sorted(found))


def sign(p):
    transformed = [0] * 6
    for i in range(6):
        transformed[p[i]] = R[i]
    if tuple(transformed) == R:
        return 1
    if tuple(transformed) == tuple(-x for x in R):
        return -1
    raise ValueError('not a sign-character permutation')


def operation_counts(p):
    if p == ONE:
        return 0, 0
    if sign(p) == -1:
        return 9, 3  # Three swaps, each three ADDs and a NEG.
    return 12, 0     # Two three-cycles, each six signed ADDs.


def run(word, incoming):
    values = list(incoming)
    for op in word:
        if op[0] == 'ADD':
            values[op[1]] += op[3] * values[op[2]]
        elif op[0] == 'NEG':
            values[op[1]] = -values[op[1]]
        else:
            raise ValueError('unknown instruction')
    return values


def columns(word, dimension):
    images = []
    for col in range(dimension):
        values = [int(col == i) for i in range(dimension)]
        images.append(run(word, values))
    return [list(row) for row in zip(*images)]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def expected_batch(width, count=6, permutation=ONE):
    result = identity(13 * width)
    for j in range(6):
        for t in range(width):
            result[6 * width + j * width + t] = [0] * (13 * width)
            result[6 * width + j * width + t][6 * width + permutation[j] * width + t] = 1
    phase = sign(permutation)
    for t in range(width):
        d = 12 * width + t
        result[d][d] = phase
        for j in range(6):
            result[d][6 * width + j * width + t] = phase * count * R[j]
    return result


def expected_echo(width, matrix, direction=1):
    result = identity(13 * width)
    for t in range(width):
        for s in range(6 * width):
            result[12 * width + t][s] = direction * 6 * sum(R[j] * matrix[j * width + t][s] for j in range(6))
    return result


def access_invoice(word):
    counts = {'ADD': 0, 'NEG': 0, 'instructions': 0, 'data_reads': 0,
              'data_writes': 0, 'data_accesses': 0, 'descriptor_records': 0,
              'origin_return_word_moves': 0}
    for op in word:
        visits = [op[2] + 1, op[1] + 1, op[1] + 1] if op[0] == 'ADD' else [op[1] + 1, op[1] + 1]
        current = 0
        for address in visits + [0]:
            counts['origin_return_word_moves'] += abs(address - current)
            current = address
        counts[op[0]] += 1
        counts['instructions'] += 1
        counts['descriptor_records'] += 1
        counts['data_writes'] += 1
        counts['data_reads'] += len(visits) - 1
        counts['data_accesses'] += len(visits)
    return counts


def boundary_census(cases, prices):
    """Enumerate H0..H5; the terminal H6 is uniquely forced by restoration.

    There are 6^6 = 46,656 endpoint-correct normalized schedules, including
    entrance operations. Output signs are uniquely forced by coefficient +6.
    This is a complete enumeration, not the primary shortest-path algorithm.
    """
    actions = group()
    answer = [{ 'output_cuts':list(oc), 'workspace_cuts':list(wc),
                'eligible':0, 'minima':[None for _ in prices]} for oc, wc in cases]
    count = 0
    for selected in product(actions, repeat=6):
        p = selected[0]
        adds, negs = operation_counts(p)
        negs += sign(p) == -1
        cuts = []
        for i, g in enumerate((PA, PB) * 3):
            p = multiply(g, p)
            h = selected[i + 1] if i < 5 else reciprocal(p)
            a, n = operation_counts(h)
            adds += a
            negs += n + (sign(h) == 1)
            p = multiply(h, p)
            cuts.append(p)
        if p != ONE:
            raise ValueError('terminal restoration failed')
        count += 1
        for index, (output_cuts, workspace_cuts) in enumerate(cases):
            if any(sign(cuts[i-1]) != 1 for i in output_cuts) or any(cuts[i-1] != ONE for i in workspace_cuts):
                continue
            record = answer[index]
            record['eligible'] += 1
            for j, (a, n) in enumerate(prices):
                cost = adds * a + negs * n
                if record['minima'][j] is None or cost < record['minima'][j]:
                    record['minima'][j] = cost
    return count, answer
