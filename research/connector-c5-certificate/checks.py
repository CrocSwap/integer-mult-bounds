"""Constructive audit of the predecessor's anonymous cardinality variables.

Owned code: Alexander Richard Towell, substantial OpenAI Codex assistance.
Apache-2.0. The reconstructed counter is Knuth's irredundant sequential
encoding as implemented by PySAT; this is not a new cardinality algorithm.
"""
from pathlib import Path
import importlib.util


def build_instance(k=6, c=5, weights=frozenset({2, 6})):
    path = Path(__file__).parent / 'vendor' / 'search_sat.py'
    spec = importlib.util.spec_from_file_location('pinned_connector_search', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cnf, pool, _ = module.build(k, c, True, weights)
    return cnf, pool


def at_most(literals, bound, top):
    """Return clauses, last ID, and constructive semantics for counter variables.

    y[k,j] means >= k+1 true literals among literals[:j+k+1]. This meaning
    satisfies every clause whenever the whole input has <= bound true literals.
    This routine covers 1 <= bound < len(literals)-1, the only target cases.
    """
    if not 1 <= bound < len(literals) - 1:
        raise ValueError('counter bound outside audited interior domain')
    variables = {}
    meaning = []
    clauses = []

    def y(k, j):
        nonlocal top
        if (k, j) not in variables:
            top += 1
            variables[k, j] = top
            meaning.append((top, tuple(literals[:j + k + 1]), k + 1))
        return variables[k, j]

    rows = len(literals) - bound
    for j in range(rows):
        clauses.append([-literals[j], y(0, j)])
        for k in range(bound - 1):
            a = y(k, j)
            if j < rows - 1:
                clauses.append([-a, y(k, j + 1)])
            clauses.append([-literals[j + k + 1], -a, y(k + 1, j)])
        a = y(bound - 1, j)
        if j < rows - 1:
            clauses.append([-a, y(bound - 1, j + 1)])
        clauses.append([-literals[j + bound], -a])
    return clauses, top, meaning


def satisfied(clauses, assignment):
    return all(any(assignment[abs(x)] == (x > 0) for x in clause)
               for clause in clauses)


def audit_counter_bridge(cnf, pool):
    """Compare every target cardinality clause with the explained construction."""
    k, c = 6, 5
    length = k * c
    offset = length * (1 + k * (k - 1) // 2)
    top = length * k
    for j in range(k):
        xs = [pool.id(('x', p, j)) for p in range(length)]
        for literals, bound in [([-x for x in xs], length - c), (xs, c)]:
            clauses, top, _ = at_most(literals, bound, top)
            if cnf.clauses[offset:offset + len(clauses)] != clauses:
                raise ValueError('cardinality bridge differs from pinned generator')
            offset += len(clauses)
    return k


def normalize(word):
    """Relabel by first occurrence, as allowed by the invariant mask family."""
    labels = {}
    return [labels.setdefault(x, len(labels)) for x in word]


def word_assignment(word, k, c, pool):
    """Construct every variable from a canonical floor word; no SAT solver."""
    if len(word) != k * c or any(word.count(j) != c for j in range(k)):
        raise ValueError('not a floor word')
    if normalize(word) != list(word):
        raise ValueError('word must be relabeled by first occurrence')
    counts = [0] * k
    prefixes = [tuple(counts)]
    for j in word:
        counts[j] += 1
        prefixes.append(tuple(counts))
    assignment = {}
    for var, obj in pool.id2obj.items():
        match obj:
            case ('x', p, j):
                value = word[p] == j
            case ('e', t, j, v):
                value = prefixes[t][j] % c == v
            case ('f', p, j):
                value = prefixes[p + 1][j] > 0
            case ('y', mask, s, t):
                value = all((prefixes[s][j] + prefixes[t][j]) % c ==
                            ((mask >> j) & 1) for j in range(k))
            case _:
                raise ValueError('unexpected generator variable')
        assignment[var] = value
    top = len(word) * k
    for j in range(k):
        xs = [pool.id(('x', p, j)) for p in range(len(word))]
        for literals, bound in [([-x for x in xs], len(word) - c), (xs, c)]:
            _, top, meaning = at_most(literals, bound, top)
            for var, prefix, threshold in meaning:
                assignment[var] = sum(assignment[abs(x)] == (x > 0)
                                      for x in prefix) >= threshold
    return assignment


def covers(word, k, c, weights):
    """Literal integer-prefix check, independent of CNF and its variables."""
    counts = [0] * k
    prefixes = [tuple(counts)]
    for j in word:
        counts[j] += 1
        prefixes.append(tuple(counts))
    seen = {tuple((a + b) % c for a, b in zip(s, t))
            for i, s in enumerate(prefixes) for t in prefixes[i:]}
    return all(tuple((mask >> j) & 1 for j in range(k)) in seen
               for mask in range(1, 1 << k) if mask.bit_count() in weights)
