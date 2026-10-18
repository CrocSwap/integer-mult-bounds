"""Separate literal-phase enumeration and dense arithmetic oracle; Apache-2.0.
Ross Richardson with substantial OpenAI Codex assistance. This does not import model.py.
"""
from itertools import product


def boundary_census(k):
    """All nine normalized choices in every gap, with separate reader symbols.

    Every previous response receives actual output rotations. No alignment
    predicate or shortest-path recurrence is used to admit a schedule.
    """
    admitted, prices = 0, set()
    for digits in product(range(9), repeat=k+1):
        workspace = original_output = 0
        responses = []
        work_operations = output_operations = 0
        for i, digit in enumerate(digits):
            u, v = divmod(digit, 3)
            workspace = (workspace+u) % 3
            original_output = (original_output+v) % 3
            responses = [(phase+v) % 3 for phase in responses]
            work_operations += u != 0
            output_operations += v != 0
            if i < k:
                responses.append(workspace)
                workspace = (workspace+1) % 3
        if workspace == original_output == 0 and not any(responses):
            admitted += 1
            prices.add((work_operations, output_operations))
    return dict(k=k, schedules=9**(k+1), admitted=admitted,
                operation_pairs=[list(p) for p in sorted(prices)])


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def permutation(blocks):
    p = [[0]*(3*blocks) for _ in range(3*blocks)]
    for i in range(3*blocks):
        p[i][3*(i//3)+(i-1)%3] = 1
    return p


def literal_admission(r):
    return multiply(r, permutation(len(r[0])//3)) == multiply(permutation(len(r)//3), r)


def declared_matrix(node):
    if 'matrix' in node:
        return node['matrix']
    rs = [declared_matrix(c) for c in node['children']]
    return [[sum(a) for a in zip(*rows)] for rows in zip(*rs)]


def expected(node, registers, contract):
    r = declared_matrix(node)
    n, m = len(r), len(r[0])
    result = identity(registers)
    for i in range(n):
        result[i][n:n+m] = r[i][:]
    if contract == 'reader':
        for i in range(m):
            result[n+i] = [0]*registers
            result[n+i][n+3*(i//3)+(i-1)%3] = 1
    return result


def expected_inverse(node, registers, contract):
    r = declared_matrix(node)
    n, m = len(r), len(r[0])
    result = identity(registers)
    # Invert the triangular block matrix directly, independently of word reversal.
    pinv = multiply(permutation(m//3), permutation(m//3))
    response = multiply(r, pinv) if contract == 'reader' else r
    for i in range(n):
        result[i][n:n+m] = [-x for x in response[i]]
    if contract == 'reader':
        for i in range(m):
            result[n+i] = [0]*registers
            result[n+i][n:n+m] = pinv[i]
    return result


def replay(word, registers, initial=None):
    state = identity(registers) if initial is None else [row[:] for row in initial]
    peak = max(sum(abs(x) for x in row) for row in state)
    for instruction in word:
        if instruction[0] == 'A':
            _, dest, src, sign = instruction
            state[dest] = [a+sign*b for a, b in zip(state[dest], state[src])]
        elif instruction[0] == 'N':
            dest = instruction[1]
            state[dest] = [-x for x in state[dest]]
        elif instruction[0] == 'R':
            _, a, power = instruction
            rows = state[a:a+3]
            state[a:a+3] = rows[-power:]+rows[:-power]
            dest = a
        else:
            raise ValueError('unknown instruction')
        peak = max(peak, sum(abs(x) for x in state[dest]))
    return state, peak


def vector_replay(word, data):
    result = data[:]
    for op in word:
        if op[0] == 'A':
            result[op[1]] += op[3]*result[op[2]]
        elif op[0] == 'N':
            result[op[1]] *= -1
        elif op[0] == 'R':
            _, a, power = op
            rows = result[a:a+3]
            result[a:a+3] = rows[-power:]+rows[:-power]
        else:
            raise ValueError('unknown instruction')
    return result


def invoice(word):
    """Reconstruct field/data-access records rather than use algebraic counts."""
    reads = writes = fields = steps = travel = cursor = 0
    adds = negations = 0
    for op in word:
        addresses = []
        if op[0] == 'A':
            adds += 1
            addresses = [(op[2], 'read'), (op[1], 'read'), (op[1], 'write')]
        elif op[0] == 'N':
            negations += 1
            addresses = [(op[1], 'read'), (op[1], 'write')]
        else:
            raise ValueError('expanded instructions required')
        for address, action in addresses:
            travel += abs(cursor-address)
            cursor = address
            reads += action == 'read'
            writes += action == 'write'
        fields += len(op)
        steps += 1
    travel += cursor
    return dict(add=adds, neg=negations, dispatch=steps, reads=reads, writes=writes,
                descriptor_fields=fields, address_travel=travel)
