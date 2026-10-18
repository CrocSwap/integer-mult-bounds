"""Finite grid-bounded coefficient synthesis. Apache-2.0.

Prepared for Philipp (@mightyOil) with substantial OpenAI Codex assistance.
The comparison is Gareth Davidson's pinned PR837 code and Sagar Thakrar's
PR696 copy/unit lowering, retained verbatim under vendor/ with attribution.
"""
from collections import deque
from fractions import Fraction as Q
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("grid_pr837", HERE / "vendor/pr837/lower.py")
horner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(horner)
reference_lower = horner.reference.lower
WORK = ("W", 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def solve(n, denominator):
    """BFS over the *entire* bounded directed graph, not only to the goal."""
    need(type(n) is int and type(denominator) is int and 1 <= n <= 127,
         "numerator outside search domain")
    need(denominator in (1, 2, 4, 8, 16) and Q(n, denominator).numerator == n,
         "denominator outside reduced search domain")
    bound = n * denominator
    previous = {denominator: None}
    distance = {denominator: 0}
    queue = deque([denominator])
    edges = 0
    while queue:
        m = queue.popleft()
        outgoing = [(2*m, "double"), (m+denominator, "add"),
                    (m-denominator, "subtract"), (-m, "negate")]
        if m % 2 == 0:
            outgoing.append((m//2, "halve"))
        for nxt, operation in outgoing:
            if abs(nxt) > bound:
                continue
            edges += 1
            if nxt not in previous:
                previous[nxt] = (m, operation)
                distance[nxt] = distance[m] + 1
                queue.append(nxt)
    goal = min((n, -n), key=lambda state: (distance.get(state, float("inf")), state < 0))
    need(goal in previous, "coefficient unreachable")
    operations = []
    cursor = goal
    while previous[cursor] is not None:
        cursor, operation = previous[cursor]
        operations.append(operation)
    return {"numerator": n, "denominator": denominator,
            "operations": list(reversed(operations)),
            "end_sign": 1 if goal > 0 else -1,
            "preparation_steps": distance[goal],
            "graph_vertices": 2*bound+1, "reachable_vertices": len(previous),
            "reachable_edges_with_multiplicity": edges}


def comparisons(entry):
    """Actual frozen PR837 four-candidate comparator; no feasibility filtering."""
    n, d = entry["numerator"], entry["denominator"]
    op = ["add", ["T", 0], ["S", 0], n, d]
    return {name: len(word) for name, word in horner.candidates(op).items()}


def improved(entry):
    return entry["preparation_steps"] + 3 < min(comparisons(entry).values())


def lower(op, entries):
    """Replace only strict improvements over *all four* unbounded Horner words."""
    baseline = reference_lower(op)  # Validate macro type, dyadic and aliases first.
    if op[0] != "add":
        return baseline
    q = Q(op[3], op[4])
    entry = entries.get(abs(q))
    if entry is None or not improved(entry):
        return baseline
    source, target = tuple(op[2]), tuple(op[1])
    word = [("copy", WORK, source)]
    for operation in entry["operations"]:
        need(operation in ("double", "halve", "negate", "add", "subtract"),
             "unknown synthesized operation")
        word.append((operation, WORK, source) if operation in ("add", "subtract")
                    else (operation, WORK))
    sign = (1 if q > 0 else -1) * entry["end_sign"]
    word.extend([("add" if sign > 0 else "subtract", target, WORK), ("clear", WORK)])
    return word
