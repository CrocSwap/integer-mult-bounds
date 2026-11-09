"""Independent operational witness for the retained CodedPort semantics.

Prepared for @CubeJerry with OpenAI assistance. Apache-2.0.
The expected trace is derived here from literal codeword operations, not
from the author's generated microstate graph or verification oracle.
"""
import argparse
import hashlib
import importlib.util
import itertools
import json
import types
from pathlib import Path

BLANK = 6
LEFT = 2


class Tape:
    def __init__(self, cells, head=1, label=0):
        self.cells = dict(cells)
        self.head = head
        self.label = label
        self.trace = []

    def read(self):
        value = self.cells.get(self.head, BLANK)
        self.trace.append(("read", self.label, self.head, value))
        return value

    def write(self, value):
        if type(value) is not int or value not in range(7):
            raise ValueError("bad physical symbol")
        self.trace.append(("write", self.label, self.head, value))
        self.cells[self.head] = value

    def move(self, direction):
        if direction not in (-1, 1):
            raise ValueError("bad physical unit move")
        self.trace.append(("move", self.label, self.head, direction))
        self.head += direction
        if self.head < 0:
            raise ValueError("one-sided physical boundary")

    def snapshot(self):
        return self.head, sorted(self.cells.items()), self.trace


def load(path, name):
    import sys
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def expected_read(cells, head=1, label=0):
    """Return status/value, endpoint and trace from the three-bit definition."""
    value_at = lambda at: cells.get(at, BLANK)
    trace = [("read", label, head, value_at(head))]
    if value_at(head) == BLANK:
        return ("ok", 4), head, trace
    number = 0
    for j in range(3):
        bit = value_at(head + j)
        trace.append(("read", label, head + j, bit))
        if bit not in (0, 1):
            return ("reject", "whole virtual codeword"), head + j, trace
        number = (number << 1) | bit
        trace.append(("move", label, head + j, 1))
    for j in range(3, 0, -1):
        trace.append(("move", label, head + j, -1))
    return (("ok", number) if number != 7 else ("reject", "unused virtual codeword")), head, trace


def expected_write(cells, value, head=1, label=0):
    after = dict(cells)
    trace = []
    for j in range(3):
        bit = (value >> (2 - j)) & 1
        after[head + j] = bit
        trace.extend((("write", label, head + j, bit),
                      ("move", label, head + j, 1)))
    trace.extend(("move", label, head + j, -1) for j in (3, 2, 1))
    return after, head, trace


def primitive_checks(source):
    counts = {"read": 0, "write": 0, "right_move": 0,
              "left_move": 0, "origin": 0}
    # Includes every valid code, unused111, every malformed symbol position,
    # and every partially materialized codeword. Leading blank deliberately
    # short-circuits even when later physical cells are materialized.
    for word in itertools.product(range(7), repeat=3):
        cells = {0: LEFT, **{i + 1: x for i, x in enumerate(word)}}
        tape = Tape(cells)
        expected, head, trace = expected_read(cells)
        try:
            observed = ("ok", source.CodedPort(tape).read())
        except ValueError as exc:
            observed = ("reject", str(exc))
        if (observed, tape.head, tape.trace, tape.cells) != (expected, head, trace, cells):
            raise AssertionError(("read", word, observed, expected, tape.snapshot()))
        counts["read"] += 1
    for value in range(7):
        for word in itertools.product(range(7), repeat=3):
            cells = {0: LEFT, **{i + 1: x for i, x in enumerate(word)}}
            expected_cells, head, trace = expected_write(cells, value)
            tape = Tape(cells)
            source.CodedPort(tape).write(value)
            if tape.snapshot() != (head, sorted(expected_cells.items()), trace):
                raise AssertionError(("write", value, word, tape.snapshot()))
            counts["write"] += 1
    for symbol in range(7):
        cells = {0: LEFT, 1: symbol, 2: 5, 3: 3}
        tape = Tape(cells)
        expected_cells = dict(cells)
        trace = [("read", 0, 1, symbol)]
        if symbol == BLANK:
            expected_cells, _, extra = expected_write(cells, 4)
            trace.extend(extra)
        trace.extend(("move", 0, j, 1) for j in (1, 2, 3))
        source.CodedPort(tape).move(1)
        if tape.snapshot() != (4, sorted(expected_cells.items()), trace):
            raise AssertionError(("right_move", symbol, tape.snapshot()))
        counts["right_move"] += 1
    for head in (1, 4, 7):
        for symbol in range(7):
            cells = {0: LEFT, head - 1: symbol}
            if head == 1 and symbol != LEFT:
                continue  # out of the physical-origin precondition
            tape = Tape(cells, head)
            trace = [("move", 0, head, -1), ("read", 0, head - 1, symbol)]
            if symbol == LEFT:
                trace.append(("move", 0, head - 1, 1))
                expected = "reject"
                final = head
            else:
                trace.extend((("move", 0, head - 1, -1),
                              ("move", 0, head - 2, -1)))
                expected = "ok"
                final = head - 3
            try:
                source.CodedPort(tape).move(-1)
                observed = "ok"
            except ValueError:
                observed = "reject"
            if observed != expected or tape.snapshot() != (final, sorted(cells.items()), trace):
                raise AssertionError(("left_move", head, symbol, tape.snapshot()))
            counts["left_move"] += 1
    for head in range(1, 41):
        cells = {0: LEFT, **{i: (i % 2) for i in range(1, head + 5)}}
        tape = Tape(cells, head)
        trace = [("move", 0, head, -1)]
        for at in range(head - 1, -1, -1):
            trace.append(("read", 0, at, cells[at]))
            if at:
                trace.append(("move", 0, at, -1))
        trace.append(("move", 0, 0, 1))
        source.origin(tape)
        if tape.snapshot() != (1, sorted(cells.items()), trace) or len(trace) != 2 * head + 1:
            raise AssertionError(("origin", head, tape.snapshot()))
        counts["origin"] += 1
    return counts


def negative_controls(source_path):
    text = source_path.read_text()
    mutations = {
        "blank_decodes_as_five": ("if t.read() == BLANK:\n            return 4",
                                 "if t.read() == BLANK:\n            return 5"),
        "read_rewinds_only_two": ("for _ in range(3):\n            t.move(-1)\n        need(value < 7",
                                  "for _ in range(2):\n            t.move(-1)\n        need(value < 7"),
        "unused_code_accepted": ("need(value < 7, \"unused virtual codeword\")",
                                 "need(value < 8, \"unused virtual codeword\")"),
        "write_reversed_bits": ("for shift in (2, 1, 0):\n            emit(self.tape",
                                "for shift in (0, 1, 2):\n            emit(self.tape"),
        "wrong_blank_materialization": ("self.write(4)", "self.write(5)"),
        "left_rejection_fails_restore": (
            "if t.read() == LEFT:\n                t.move(1)\n                raise ValueError(\"native routine crossed",
            "if t.read() == LEFT:\n                t.move(-1)\n                raise ValueError(\"native routine crossed"),
    }
    killed = []
    import sys
    for name, (old, new) in mutations.items():
        if text.count(old) != 1:
            raise AssertionError(("mutation target", name, text.count(old)))
        module = types.ModuleType("independent_mutation_" + name)
        sys.modules[module.__name__] = module
        exec(compile(text.replace(old, new), str(source_path), "exec"), module.__dict__)
        try:
            primitive_checks(module)
        except (AssertionError, ValueError):
            killed.append(name)
        else:
            raise AssertionError(("survived mutation", name))
    return killed


class CountedTable:
    def __init__(self, rows):
        self.rows = rows
        self.fetched = 0

    def __getitem__(self, item):
        self.fetched += 1
        return self.rows[item]


def source_execution(source, rows, snapshots):
    ports = [Tape(cells, head, label) for label, (cells, head) in enumerate(snapshots)]
    journal = []
    for port in ports:
        port.trace = journal
    counted = CountedTable(rows)
    try:
        source.execute_table(counted, ports)
        status = "halt"
        label = ""
    except ValueError as exc:
        status = "reject"
        label = str(exc)
    return {"status": status, "label": label, "rows": counted.fetched, "actions": len(journal),
            "trace": journal, "heads": [p.head for p in ports],
            "cells": [sorted(p.cells.items()) for p in ports]}


def mathematical_execution(rows, snapshots):
    """Closed small-table oracle using the explicitly derived primitive traces."""
    cells = [dict(snapshot[0]) for snapshot in snapshots]
    heads = [snapshot[1] for snapshot in snapshots]
    trace = []
    pc = 0
    fetched = 0
    status = None
    label = ""
    while status is None:
        fetched += 1
        if fetched > 1000:
            raise ValueError("review fixture is not bounded")
        row = rows[pc]
        if row[0] == "halt":
            for port in range(len(cells)):
                head = heads[port]
                trace.append(("move", port, head, -1))
                head -= 1
                while True:
                    value = cells[port].get(head, BLANK)
                    trace.append(("read", port, head, value))
                    if value == LEFT:
                        break
                    trace.append(("move", port, head, -1))
                    head -= 1
                    if head < 0:
                        raise ValueError("missing physical origin in review fixture")
                trace.append(("move", port, head, 1))
                heads[port] = head + 1
            status = "halt"
        elif row[0] == "reject":
            status = "reject"
            label = row[1]
        elif row[0] == "goto":
            pc = row[1]
        elif row[0] == "branch":
            port = row[1]
            outcome, heads[port], actions = expected_read(cells[port], heads[port], port)
            trace.extend(actions)
            if outcome[0] == "reject":
                status = "reject"
                label = outcome[1]
            else:
                # Explicit scan gives the source's last-duplicate-wins rule.
                pc = row[3]
                for key, destination in row[2]:
                    if key == outcome[1]:
                        pc = destination
        elif row[0] == "write":
            port = row[1]
            cells[port], heads[port], actions = expected_write(
                cells[port], row[2], heads[port], port)
            trace.extend(actions)
            pc += 1
        elif row[0] == "move":
            port = row[1]
            head = heads[port]
            if row[2] == 1:
                value = cells[port].get(head, BLANK)
                trace.append(("read", port, head, value))
                if value == BLANK:
                    cells[port], _, actions = expected_write(cells[port], 4, head, port)
                    trace.extend(actions)
                trace.extend(("move", port, head + j, 1) for j in range(3))
                heads[port] = head + 3
                pc += 1
            else:
                trace.append(("move", port, head, -1))
                value = cells[port].get(head - 1, BLANK)
                trace.append(("read", port, head - 1, value))
                if value == LEFT:
                    trace.append(("move", port, head - 1, 1))
                    status = "reject"
                    label = "native routine crossed its local origin"
                else:
                    trace.extend((("move", port, head - 1, -1),
                                  ("move", port, head - 2, -1)))
                    heads[port] = head - 3
                    pc += 1
        else:
            raise ValueError("unknown fixture opcode")
    return {"status": status, "label": label, "rows": fetched, "actions": len(trace),
            "trace": trace, "heads": heads,
            "cells": [sorted(c.items()) for c in cells]}


def execution_cases():
    branch = (("branch", 0, ((0, 1), (1, 2), (2, 1), (3, 2), (4, 1), (5, 2), (6, 1)), 2),
              ("halt",), ("reject", "branch rejection"))
    for word in itertools.product(range(7), repeat=3):
        cells = {0: LEFT, **{i + 1: x for i, x in enumerate(word)}}
        yield "branch-" + "".join(map(str, word)), branch, [(cells, 1)]
        for value in range(7):
            yield "write-%s-%s" % (value, word), (("write", 0, value), ("reject", "end")), [(cells, 1)]
    for symbol in range(7):
        yield "right-%d" % symbol, (("move", 0, 1), ("reject", "end")), [({0: LEFT, 1: symbol, 2: 5, 3: 3}, 1)]
    for head in (1, 4, 7):
        for symbol in range(7):
            if head == 1 and symbol != LEFT:
                continue
            yield "left-%d-%d" % (head, symbol), (("move", 0, -1), ("reject", "end")), [({0: LEFT, head - 1: symbol}, head)]
    for head in range(1, 41):
        cells = {0: LEFT, **{i: (i % 2) for i in range(1, head + 5)}}
        yield "origin-%d" % head, (("halt",),), [(cells, head)]
    for value in range(7):
        code = {i + 1: (value >> (2 - i)) & 1 for i in range(3)}
        # Default dispatch, duplicate branch keys, and empty branch map.
        for branches in ((), ((value, 2),), ((value, 1), (value, 2)), ((value, 2), (value, 1))):
            table = (("branch", 0, branches, 1), ("halt",), ("reject", "chosen"))
            yield "branch-map-%s-%s" % (value, branches), table, [({0: LEFT, **code}, 1)]
    for value in range(7):
        table = (("goto", 2), ("reject", "unreachable"), ("write", 1, value),
                 ("move", 0, 1), ("move", 1, 1), ("write", 0, 6),
                 ("move", 0, -1), ("branch", 1, ((4, 8),), 9),
                 ("halt",), ("reject", "bad blank"))
        yield "multiport-%d" % value, table, [({0: LEFT}, 1), ({0: LEFT}, 1), ({0: LEFT, 1: 0}, 1)]
    yield "zero-port-halt", (("halt",),), []
    yield "zero-port-reject", (("reject", "zero"),), []


def table_checks(source):
    count = 0
    for name, rows, snapshots in execution_cases():
        expected = mathematical_execution(rows, snapshots)
        observed = source_execution(source, rows, snapshots)
        if expected != observed:
            raise AssertionError(("table", name, expected, observed))
        count += 1
    return count


def admitted_case(rows, snapshots):
    if not snapshots:
        return False
    for row in rows:
        if row[0] == "branch" and len({pair[0] for pair in row[2]}) != len(row[2]):
            return False
    return True


def generated_execution(program, snapshots, want_path=False):
    """Independent direct graph traversal, not the author's emulator."""
    ports = [Tape(cells, head, label) for label, (cells, head) in enumerate(snapshots)]
    journal = []
    for port in ports:
        port.trace = journal
    state = program.initial
    clock = 0
    dispatches = 0
    path = []
    while True:
        if clock > 10000:
            raise ValueError("nonterminating review fixture")
        path.append(state)
        node = program.states[state]
        operation = node[0]
        if operation == "stop":
            status = "halt" if node[1] == "success" else "reject"
            label = node[2]
            break
        clock += 1
        if operation == "nop":
            dispatches += 1
            state = node[1]
        elif operation == "read":
            state = node[2][ports[node[1]].read()]
        elif operation == "write":
            ports[node[1]].write(node[2])
            state = node[3]
        elif operation == "move":
            ports[node[1]].move(node[2])
            state = node[3]
        else:
            raise AssertionError(("unknown generated state", node))
    result = {"status": status, "label": label, "rows": dispatches, "actions": len(journal),
              "trace": journal, "heads": [p.head for p in ports],
              "cells": [sorted(p.cells.items()) for p in ports]}
    if clock != result["rows"] + result["actions"]:
        raise AssertionError(("clock", clock, result))
    return (result, clock, path) if want_path else result


def lowering_checks(lower):
    cases = 0
    excluded = 0
    programs = {}
    clock_total = 0
    for name, rows, snapshots in execution_cases():
        if not admitted_case(rows, snapshots):
            excluded += 1
            continue
        key = rows, len(snapshots)
        if key not in programs:
            programs[key] = lower.compile_table(*key)
        expected = mathematical_execution(rows, snapshots)
        observed, clock, _ = generated_execution(programs[key], snapshots, True)
        if observed != expected or clock != expected["rows"] + expected["actions"]:
            raise AssertionError(("lowering", name, expected, observed, clock))
        cases += 1
        clock_total += clock
    return {"cases": cases, "excluded_duplicate_or_zero_port_cases": excluded,
            "distinct_programs": len(programs), "microsteps": clock_total}


def lowering_negative_controls(lower):
    killed = []
    def check(name, rows, snapshots, mutate):
        program = lower.compile_table(rows, len(snapshots))
        expected = mathematical_execution(rows, snapshots)
        _, _, path = generated_execution(program, snapshots, True)
        states = list(program.states)
        initial = mutate(states, path, program.initial)
        mutated = types.SimpleNamespace(states=tuple(states), initial=initial)
        try:
            observed = generated_execution(mutated, snapshots)
        except (AssertionError, ValueError, IndexError):
            killed.append(name)
        else:
            if expected == observed:
                raise AssertionError(("survived lowering mutation", name))
            killed.append(name)
    check("remove_row_dispatch", (("halt",),), [({0: LEFT}, 1)],
          lambda states, path, initial: states[initial][1])
    def flip_first_write(states, path, initial):
        at = next(s for s in path if states[s][0] == "write")
        node = states[at]
        states[at] = node[:2] + (1 - node[2],) + node[3:]
        return initial
    check("wrong_generated_write", (("write", 0, 4), ("reject", "end")),
          [({0: LEFT}, 1)], flip_first_write)
    def wrong_blank(states, path, initial):
        at = next(s for s in path if states[s][0] == "read")
        node = states[at]
        edges = list(node[2]); edges[6] = edges[0]
        states[at] = node[:2] + (tuple(edges),)
        return initial
    check("blank_treated_as_code", (("branch", 0, ((4, 1),), 2), ("halt",), ("reject", "end")),
          [({0: LEFT}, 1)], wrong_blank)
    def skip_final_move(states, path, initial):
        at = next(s for s in reversed(path) if states[s][0] == "move")
        node = states[at]
        states[at] = ("nop", node[3])
        return initial
    check("left_reject_loses_restore", (("move", 0, -1), ("halt",)),
          [({0: LEFT}, 1)], skip_final_move)
    check("unused_code_loses_last_rewind", (("branch", 0, (), 1), ("halt",)),
          [({0: LEFT, 1: 1, 2: 1, 3: 1}, 1)], skip_final_move)
    check("halt_origin_loses_final_move", (("halt",),),
          [({0: LEFT, 1: 1, 2: 0, 3: 1}, 4)], skip_final_move)
    return killed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    source_path = args.package / "vendor/machine.py"
    source = load(source_path, "independent_original_machine")
    result = {"source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
              "primitive_trace_checks": primitive_checks(source),
              "negative_controls_killed": negative_controls(source_path),
              "table_trace_checks": table_checks(source)}
    lower_path = args.package / "lower.py"
    if lower_path.exists():
        lower = load(lower_path, "independently_reviewed_lowering")
        result["lower_sha256"] = hashlib.sha256(lower_path.read_bytes()).hexdigest()
        result["generated_state_checks"] = lowering_checks(lower)
        result["lowering_negative_controls_killed"] = lowering_negative_controls(lower)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
