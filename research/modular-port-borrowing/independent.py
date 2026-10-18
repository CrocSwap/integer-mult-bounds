"""Separate recursive event and exact matrix checker; no backend imports.

Apache-2.0. Gareth Davidson, with substantial OpenAI Codex assistance.
"""
from functools import lru_cache
import hashlib
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(None)
def shapes(n):
    if n == 1:
        return (None,)
    result = []
    for a in range(1, n):
        for left in shapes(a):
            for right in shapes(n - a):
                result.append((left, right))
    for a in range(1, n - 1):
        for b in range(1, n - a):
            for left in shapes(a):
                for middle in shapes(b):
                    for right in shapes(n - a - b):
                        result.append((left, middle, right))
    return tuple(result)


def label(shape):
    index = 0

    def walk(node):
        nonlocal index
        if node is None:
            result = index
            index += 1
            return result
        return tuple(walk(child) for child in node)

    return walk(shape)


def interval(node):
    if type(node) is int:
        return node, node + 1
    return interval(node[0])[0], interval(node[-1])[1]


def events(tree, sign=1):
    """Explicit binary/ternary templates, independently implemented control stack."""
    templates = {2: ((0, 1), (1, 1), (0, -1), (1, -1)),
                 3: ((0, 1), (1, 1), (2, 1), (1, -1), (0, -1), (1, 1), (2, -1), (1, -1))}
    stack = [("call", tree, 0, 1, sign)]
    while stack:
        action, node, source, target, q = stack.pop()
        lo, hi = interval(node)
        if action == "return":
            yield "return", source, target, lo, hi, q
            continue
        require(source != target and target != 0, "invalid event ports")
        yield "enter", source, target, lo, hi, q
        stack.append(("return", node, source, target, q))
        if type(node) is int:
            yield "leaf", source, target, node, q
            continue
        ports = [source] + [r for r in (2, 3, 1, 4) if r not in (source, target)][:len(node) - 1] + [target]
        require(len(ports) == len(node) + 1 and len(set(ports)) == len(ports), "connector availability")
        word = templates[len(node)]
        if q < 0:
            word = tuple((i, -s) for i, s in reversed(word))
        for child, direction in reversed(word):
            stack.append(("call", node[child], ports[child], ports[child + 1], direction))


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, column)) for column in zip(*b)] for row in a]


def product(factors, lo=0, hi=None):
    length = len(factors[0])
    result = [[int(i == j) for j in range(length)] for i in range(length)]
    for factor in factors[lo:len(factors) if hi is None else hi]:
        result = multiply(factor, result)
    return result


def matvec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def endpoint(factors, entry, sign, modulus=None):
    value = matvec(product(factors), entry[0])
    result = [row[:] for row in entry]
    result[1] = [y + sign * x for y, x in zip(entry[1], value)]
    if modulus:
        result = [[x % modulus for x in row] for row in result]
    return result


def basis_trace(tree, factors, width, sign, expected_word=None):
    """All ordinary data columns; integer lift and residue maps at every leaf.

    Snapshot every recursive entry and compare every return to its direct
    product shear, including children borrowing ancestor ports.
    """
    length = len(factors[0])
    dimension, modulus = 5 * length, 1 << width
    integer = [[int(i == j) for j in range(dimension)] for i in range(dimension)]
    residue = [row[:] for row in integer]
    stack, leaves, returns, seen, peak = [], 0, 0, [], 1
    transcript = hashlib.sha256()
    products = {}
    for event in events(tree, sign):
        action, source, target, *rest = event
        if action == "enter":
            lo, hi, q = rest
            stack.append((event, [row[:] for row in residue]))
        elif action == "leaf":
            factor, q = rest
            seen.append([source, target, factor, q])
            for state, reduce in ((integer, False), (residue, True)):
                before = [row[:] for row in state[source * length:(source + 1) * length]]
                increment = multiply(factors[factor], before)
                for i in range(length):
                    state[target * length + i] = [a + q * b for a, b in zip(state[target * length + i], increment[i])]
                    if reduce:
                        state[target * length + i] = [x % modulus for x in state[target * length + i]]
            require(residue == [[x % modulus for x in row] for row in integer], "prefix quotient mismatch")
            require(residue[:length] == [[int(i == j) for j in range(dimension)] for i in range(length)],
                    "external source overwritten")
            peak = max(peak, max(abs(x) for row in integer for x in row))
            transcript.update(json.dumps([seen[-1], residue], separators=(",", ":")).encode())
            leaves += 1
        else:
            lo, hi, q = rest
            start, saved = stack.pop()
            require(start == ("enter", source, target, lo, hi, q), "return nesting")
            key = (lo, hi)
            if key not in products:
                products[key] = product(factors, lo, hi)
            increment = multiply(products[key], saved[source * length:(source + 1) * length])
            expected = [row[:] for row in saved]
            for i in range(length):
                expected[target * length + i] = [(a + q * b) % modulus for a, b in
                                                zip(expected[target * length + i], increment[i])]
            require(residue == expected, "recursive return contract")
            returns += 1
    require(not stack, "unclosed recursive stack")
    if expected_word is not None:
        require(seen == [list(row) for row in expected_word], "independent literal word")
    identity = [[int(i == j) for j in range(dimension)] for i in range(dimension)]
    expected = [row[:] for row in identity]
    matrix = product(factors)
    for i in range(length):
        for j in range(length):
            expected[length + i][j] += sign * matrix[i][j]
    require(integer == expected, "integer whole-word endpoint")
    require(residue == [[x % modulus for x in row] for row in expected], "residue whole-word endpoint")
    return dict(leaves=leaves, recursive_returns=returns, columns=dimension,
                transcript_sha256=transcript.hexdigest(), integer_basis_prefix_peak=str(peak))


def concrete_prefixes(word, factors, initial, width):
    """Direct integer matrix updates, independent of scalar lowering/reductions."""
    modulus = 1 << width
    signed = lambda x: x if x < modulus // 2 else x - modulus
    data = [[signed(x) for x in row] for row in initial]
    peak = max(abs(x) for row in data for x in row)
    for source, target, factor, sign in word:
        increment = matvec(factors[factor], data[source])
        data[target] = [a + sign * b for a, b in zip(data[target], increment)]
        peak = max(peak, max(abs(x) for row in data for x in row))
        yield [row[:] for row in data], peak
