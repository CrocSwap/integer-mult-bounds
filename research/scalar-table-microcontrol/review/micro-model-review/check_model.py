"""Independent finite-control/model checks; not the author's runner.

Usage: python -B check_model.py /absolute/path/to/scalar-table-microcontrol
Prepared for @CubeJerry with OpenAI assistance.
"""
from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys


def need(value, message):
    if not value:
        raise RuntimeError(message)


def module(path):
    spec = importlib.util.spec_from_file_location("reviewed_lower", path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = result
    spec.loader.exec_module(result)
    return result


def delta(node, symbols):
    """Expand one compact state into the literal simultaneous TM rule.

    All symbol tuples are explicit in the calling finite enumeration. No
    extra state, scratch tape, or extra transition is used in expansion.
    The inactive cells are preserved mathematically, not written by a host
    tape backing-list operation.
    """
    writes = list(symbols)
    moves = [0] * len(symbols)
    op = node[0]
    if op == "nop":
        nxt = node[1]
    elif op == "read":
        nxt = node[2][symbols[node[1]]]
    elif op == "write":
        writes[node[1]] = node[2]
        nxt = node[3]
    elif op == "move":
        moves[node[1]] = node[2]
        nxt = node[3]
    else:
        raise RuntimeError("terminal state has no outgoing transition")
    return nxt, tuple(writes), tuple(moves)


def inspect(program):
    """Independent admission, without calling lower.check_program."""
    states = program.states
    p, n = program.ports, program.source_rows
    need(type(p) is int and p >= 1, "port count")
    need(type(n) is int and n >= 1, "source rows")
    need(program.initial == 0, "initial row")
    need(type(states) is tuple and len(states) <= 48*n+3*p+4, "state bound")
    counts = {op: 0 for op in ("nop", "read", "write", "move", "stop")}
    expanded = 0
    for identifier, node in enumerate(states):
        need(type(node) is tuple and node and node[0] in counts, "node opcode")
        op = node[0]
        counts[op] += 1
        need((identifier < n) == (op == "nop"), "exact dispatch partition")
        if op == "stop":
            need(len(node) == 3 and node[1] in ("success", "reject")
                 and type(node[2]) is str, "terminal state")
            continue
        if op == "nop":
            need(len(node) == 2, "nop arity")
            targets = (node[1],)
        else:
            need(type(node[1]) is int and 0 <= node[1] < p, "physical port")
            if op == "read":
                need(len(node) == 3 and type(node[2]) is tuple
                     and len(node[2]) == 7, "total read")
                targets = node[2]
            else:
                need(len(node) == 4 and type(node[2]) is int, "action arity")
                need(node[2] in range(7) if op == "write" else node[2] in (-1, 1),
                     "physical action")
                targets = (node[3],)
        need(all(type(x) is int and 0 <= x < len(states) for x in targets),
             "closed control graph")
        for symbols in itertools.product(range(7), repeat=p):
            nxt, writes, moves = delta(node, symbols)
            need(nxt in targets, "delta target")
            need(len(writes) == p and len(moves) == p, "same P tapes")
            need(all(type(x) is int and 0 <= x < 7 for x in writes), "same alphabet")
            need(all(x in (-1, 0, 1) for x in moves), "unit-or-stationary heads")
            need(sum(a != b for a, b in zip(writes, symbols)) <= 1,
                 "one addressed write")
            need(sum(x != 0 for x in moves) <= 1, "one addressed move")
            if op in ("nop", "read"):
                need(writes == symbols and not any(moves), "stationary read/dispatch")
            if op == "write":
                need(not any(moves), "write stays")
            if op == "move":
                need(writes == symbols, "move preserves symbols")
            expanded += 1
    need(counts["nop"] == n, "one dispatch per original row")
    return counts, expanded


def reject(check):
    try:
        check()
    except (RuntimeError, ValueError, TypeError, IndexError):
        return 1
    raise RuntimeError("negative control was accepted")


def main():
    package = Path(sys.argv[1]).resolve()
    lower = module(package / "lower.py")
    cases = []
    # All operators and every port; branching defaults and all seven keys.
    for p in (1, 2, 3):
        for n in (2, 3, 7):
            for port in range(p):
                rows = [
                    ("goto", 0), ("halt",), ("reject", "literal tag"),
                    ("move", port, -1), ("move", port, 1),
                    ("branch", port, (), n-1),
                    ("branch", port, tuple((s, s % n) for s in range(7)), n-1),
                ] + [("write", port, x) for x in range(7)]
                for row in rows:
                    table = (row,) + (("goto", 0),) * (n-2) + (("halt",),)
                    program = lower.compile_table(table, p)
                    counts, expanded = inspect(program)
                    cases.append((len(program.states), expanded, counts))
    # The maximal decoder construction remains affine in N. No traversal of
    # its runtime loops is required to establish finite state closure.
    large = lower.compile_table(tuple(("branch", 0, (), 0) for _ in range(101)), 1)
    large_counts, expanded = inspect(large)
    cases.append((len(large.states), expanded, large_counts))
    need(len(large.states) == 47*101+3+4, "independently derived branch count")

    # A closed self-loop need not halt: its dispatch is one transition and
    # performs no tape actions. Every prefix has C=U and A=0.
    loop = lower.compile_table((("goto", 0),), 2)
    state = loop.initial
    for steps in range(1, 258):
        state, symbols, moves = delta(loop.states[state], (6, 2))
        need(state == 0 and symbols == (6, 2) and moves == (0, 0), "loop prefix")

    # Independent checker must reject graph mutations; admission must reject
    # source grammar that is outside the proved finite/closed domain.
    good = lower.compile_table((("write", 0, 1), ("halt",)), 1)
    bad_states = list(good.states)
    bad_states[0] = ("nop", len(bad_states))
    negative = reject(lambda: inspect(lower.Program(1, 2, tuple(bad_states))))
    bad_states = list(good.states)
    bad_states[0] = ("move", 0, 1, 1)
    negative += reject(lambda: inspect(lower.Program(1, 2, tuple(bad_states))))
    malformed = [
        ((), 1), ((("halt",),), True), ((("halt",),), 0),
        ((("write", 0, 0),), 1), ((("move", 0, 1),), 1),
        ((("goto", True),), 1), ((("goto", -1),), 1),
        ((("branch", 0, ((0, 0), (0, 0)), 0),), 1),
        ((("branch", 0, ((7, 0),), 0),), 1),
        ((("branch", 0, ((True, 0),), 0),), 1),
        ((("branch", 1, (), 0),), 1),
        ((("write", 0, True), ("halt",)), 1),
        ((("move", 0, 0), ("halt",)), 1),
        ((("halt", 0),), 1), ((("reject", object()),), 1),
    ]
    negative += sum(reject(lambda t=t, p=p: lower.compile_table(t, p)) for t, p in malformed)
    result = {
        "status": "pass",
        "scope": "independent finite graph, literal simultaneous transition expansion and model closure",
        "source_sha256": hashlib.sha256((package / "lower.py").read_bytes()).hexdigest(),
        "graphs": len(cases),
        "state_instances": sum(x[0] for x in cases),
        "literal_transition_instances": sum(x[1] for x in cases),
        "maximal_branch_graph_states": len(large.states),
        "nonterminating_prefix_steps": 257,
        "negative_controls": negative,
        "limits": "Does not replace universal proof or independent original-executor operational simulation. No complete caller, tariff, or kappa claim.",
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
