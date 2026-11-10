#!/usr/bin/env python3
"""Independent source execution versus emitted primitive microcontrol.

The host trace simulator is verification apparatus, not the target machine.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from dataclasses import replace
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from source_binding import authenticate, need, vendor
from lower import Layout, compile_primitive, retirement_actions, state_bound

M = vendor("source_machine", "retained/machine.py")


class PrefixStop(Exception):
    pass


class Tape:
    def __init__(self, number, body, trace, head=0):
        self.number = number
        self.cells = {-1: 2} | dict(enumerate(body))
        self.head = head
        self.trace = trace
        self.visited = {head}
        self.highwater = max(head, len(body))

    def read(self):
        value = self.cells.get(self.head, 6)
        self.trace.append(("read", self.number, self.head, value))
        return value

    def write(self, value):
        self.trace.append(("write", self.number, self.head, value))
        self.cells[self.head] = value

    def move(self, direction):
        self.trace.append(("move", self.number, self.head, direction))
        self.head += direction
        self.visited.add(self.head)
        self.highwater = max(self.highwater, self.head)


class Rows:
    def __init__(self, table, budget=100000):
        self.table = table
        self.count = 0
        self.budget = budget

    def __getitem__(self, index):
        if self.count == self.budget:
            raise PrefixStop()
        self.count += 1
        return self.table[index]


def snapshot(tapes):
    return [(t.head, t.cells, sorted(t.visited), t.highwater) for t in tapes]


def simulate(program, tapes, limit=3000000):
    pc = program.initial
    steps = 0
    dispatches = 0
    while True:
        node = program.states[pc]
        op = node[0]
        if op == "stop":
            return (node[1], node[2]), steps, dispatches
        if steps == limit:
            return ("prefix", ""), steps, dispatches
        steps += 1
        if op == "nop":
            dispatches += 1
            pc = node[1]
        elif op == "read":
            pc = node[2][tapes[node[1]].read()]
        elif op == "write":
            tapes[node[1]].write(node[2])
            pc = node[3]
        elif op == "move":
            tapes[node[1]].move(node[2])
            pc = node[3]
        else:
            raise ValueError("unknown target operation")


def run_case(table, layout, bodies, heads=None, program=None, row_budget=100000,
             return_tapes=False):
    need(len(bodies) == layout.total_ports, "fixture global port inventory")
    heads = [0] * len(bodies) if heads is None else heads
    source_trace, target_trace = [], []
    source = [Tape(i, body, source_trace, heads[i]) for i, body in enumerate(bodies)]
    target = [Tape(i, body, target_trace, heads[i]) for i, body in enumerate(bodies)]
    rows = Rows(table, row_budget)
    controller = SimpleNamespace(payloads=source, primitive_work=layout.work,
                                 primitive_context=layout.contexts,
                                 services={("fixed-service",): rows})
    try:
        M.Controller.primitive(controller, ("fixed-service",), layout.fields)
        terminal = ("success", "")
    except ValueError as error:
        terminal = ("reject", str(error))
    except PrefixStop:
        terminal = ("prefix", "")
    if program is None:
        program = compile_primitive(table, layout)
    limit = len(source_trace) + rows.count if terminal[0] == "prefix" else 3000000
    got, clock, dispatches = simulate(program, target, limit)
    need(got == terminal, "source/target terminal mismatch")
    need(source_trace == target_trace, "source/target active trace mismatch")
    need(snapshot(source) == snapshot(target), "source/target tape/head/history mismatch")
    need(clock == len(source_trace) + rows.count, "C = A + U mismatch")
    need(dispatches == rows.count, "one target dispatch per source row")
    need(all(not (e[0] == "write" and e[1] in layout.contexts) for e in target_trace),
         "readonly context changed")
    inactive = set(range(layout.total_ports)) - set(layout.local_ports)
    need(all(e[1] not in inactive for e in target_trace), "inactive global tape touched")
    result = dict(terminal=terminal, actions=len(source_trace), rows=rows.count,
                  clock=clock, states=len(program.states),
                  bound=state_bound(len(table), layout), heads=[t.head for t in target],
                  trace_sha256=hashlib.sha256(repr(target_trace).encode()).hexdigest())
    return (result, target) if return_tapes else result


def code(value):
    return [(value >> bit) & 1 for bit in (2, 1, 0)]


def field(width, values):
    out = []
    for value in values:
        for bit in range(width):
            out += code((value >> bit) & 1)
        out += code(2)
    return out


def decode(tape, width):
    body = []
    i = 0
    while tape.cells.get(i, 6) != 6:
        body.append(tape.cells[i])
        i += 1
    symbols = [4 * body[j] + 2 * body[j + 1] + body[j + 2]
               for j in range(0, len(body), 3)]
    values = []
    for start in range(0, len(symbols), width + 1):
        bits = symbols[start:start + width]
        need(symbols[start + width] == 2, "numeric output delimiter")
        values.append(sum(v << j for j, v in enumerate(bits)) - (bits[-1] << width))
    return tuple(values)


def protocol_suite():
    result = []
    # Nontrivial global remapping; two global tapes remain entirely untouched.
    layout = Layout(7, (4, 1), (5, 0), (3,))
    context = 4  # local table index, not global port 3
    baseline = [[1, 0] * 4, code(0), [5, 4], [0, 1, 1], code(1), [0] * 9, [3, 3]]
    heads = [5, 0, 1, 0, 0, 7, 1]
    for symbol in range(7):
        bodies = [list(x) for x in baseline]
        bodies[3] = [symbol]
        table = (("branch", context, ((0, 1), (1, 1), (6, 1)), 2),
                 ("halt",), ("reject", "wrong default"))
        observation = run_case(table, layout, bodies, heads)
        need(observation["terminal"][0] == ("success" if symbol in (0, 1, 6) else "reject"),
             "raw context alphabet classification")
        result.append(observation)
    for symbol in range(7):
        bodies = [list(x) for x in baseline]
        bodies[3] = [symbol]
        table = (("move", context, 1), ("halt",))
        observation = run_case(table, layout, bodies, heads)
        need(observation["terminal"][0] == ("success" if symbol in (0, 1) else "reject"),
             "context frontier guard")
        result.append(observation)
    for first in (0, 1, 3):
        bodies = [list(x) for x in baseline]
        bodies[3] = [first, 0]
        moved_heads = heads[:]
        moved_heads[3] = 1
        # The source left-move checks LEFT only; it does not validate symbol 3.
        result.append(run_case((("move", context, -1), ("halt",)),
                               layout, bodies, moved_heads))
    left = run_case((("move", context, -1), ("halt",)), layout, baseline, heads)
    need(left["heads"][3] == 0 and left["terminal"][1] == "native context crossed its local origin",
         "context left rejection restores head")
    result.append(left)
    result.append(run_case((("write", context, 0), ("halt",)), layout, baseline, heads))
    # Raw descriptor scan. This is a protocol control, not a production header parser.
    scan = (("branch", context, ((0, 1), (1, 1), (6, 3)), 4),
            ("move", context, 1), ("goto", 0), ("halt",), ("reject", "bad header"))
    for size in (0, 1, 2, 11, 128):
        bodies = [list(x) for x in baseline]
        bodies[3] = [j % 2 for j in range(size)]
        result.append(run_case(scan, layout, bodies, heads))
    # Failed pre-retirement changes an initial prefix and fetches no table row.
    bodies = [list(x) for x in baseline]
    bodies[5] = [0, 1, 3, 0]
    bad_heads = heads[:]
    bad_heads[5] = 3
    failed = run_case((("halt",),), layout, bodies, bad_heads)
    need(failed["rows"] == 0 and failed["terminal"][1] == "contiguous binary body",
         "pre-retirement rejection precedes all source row fetches")
    result.append(failed)
    # A source reject leaves the newly written work intact and skips post-cleanup.
    table = (("write", 2, 6), ("move", 2, 1), ("move", context, 1),
             ("reject", "after private write"))
    failed, tapes = run_case(table, layout, baseline, heads, return_tapes=True)
    need([tapes[5].cells[i] for i in range(3)] == code(6), "failure retains staged private data")
    need(failed["heads"][3] == 1, "failure skips success context-origin return")
    result.append(failed)
    # A successful version retires actual encoded blanks and all new work bytes.
    table = table[:-1] + (("halt",),)
    good, tapes = run_case(table, layout, baseline, heads, return_tapes=True)
    need(all(value == 6 for index, value in tapes[5].cells.items() if index >= 0),
         "successful wrapper retires all coded private data")
    result.append(good)
    # Looping tables retain prefix equivalence and are not called completed.
    loop = (("branch", context, ((0, 0), (1, 0), (6, 0)), 0),)
    result.append(run_case(loop, layout, baseline, heads, row_budget=31))
    return result


def retirement_suite():
    checked = 0
    for length in range(33):
        for head in range(length + 4):
            trace = []
            tape = Tape(0, [j % 2 for j in range(length)], trace, head)
            M.retire(tape)
            need(len(trace) == retirement_actions(length, head), "literal retirement equation")
            need(tape.head == 0 and all(v == 6 for k, v in tape.cells.items() if k >= 0),
                 "retirement output")
            checked += 1
    layout = Layout(3, (0,), (1,), (2,))
    summaries = []
    for length, head, context_head in [(0, 0, 0), (3, 0, 4), (137, 203, 11)]:
        observation = run_case((("halt",),), layout,
                               [[], [j % 2 for j in range(length)], [0, 1] * 6],
                               [0, head, context_head])
        need(observation["clock"] == 2 * head + 5 * length + 24 + 2 * context_head,
             "full wrapper/header-return bill")
        summaries.append(observation)
    return dict(literal_cases=checked, wrapper_cases=summaries)


def provider_suite():
    exact = vendor("exact_tables", "retained/exact_scalar_tables.py")
    rounded = vendor("rounded_tables", "retained/rounded_tables.py")
    cases = []
    catalog = []
    # These retained arithmetic tables do not read the extra context. Its
    # preservation and returned head are still actual primitive obligations.
    for name, builder in (("exact", exact.compile_scalar), ("rounded", rounded.compile_rounded)):
        for coefficient in ("-2/3", "1/2", "3/2"):
            table, receipt = builder("SCALE", coefficient)
            layout = Layout(6, (3,), (1, 4), (2,))
            program = compile_primitive(table, layout)
            catalog.append(dict(kind=name, coefficient=coefficient, source_rows=len(table),
                                states=len(program.states), bound=state_bound(len(table), layout)))
            q = Fraction(coefficient)
            for width in range(1, 6):
                for value in range(-(1 << (width - 1)), 1 << (width - 1)):
                    bodies = [[5], [j % 2 for j in range(43)], [1, 0, 1, 1, 0],
                              field(width, (value, 0)), [1, 0] * 27, [4, 5]]
                    heads = [0, 31, 4, 0, 69, 1]
                    result, tapes = run_case(table, layout, bodies, heads, program=program,
                                             return_tapes=True)
                    y = q * value
                    if name == "rounded":
                        y = (q.numerator * value + q.denominator // 2) // q.denominator
                    admitted = (getattr(y, "denominator", 1) == 1
                                and -(1 << (width - 1)) <= y < (1 << (width - 1)))
                    need((result["terminal"][0] == "success") == admitted,
                         "independent exact/rounded arithmetic admission")
                    if admitted:
                        need(decode(tapes[3], width) == (int(y), 0), "independent numerical result")
                        need(all(tapes[i].head == 0 for i in layout.local_ports),
                             "complete provider return heads")
                    cases.append(result)
    return dict(cases=len(cases), successes=sum(x["terminal"][0] == "success" for x in cases),
                rejections=sum(x["terminal"][0] == "reject" for x in cases),
                actual_provider_catalog=catalog,
                max_clock=max(x["clock"] for x in cases),
                combined_trace_digest=hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest())


def controls_suite():
    caught = []
    def detects(name, table, layout, bodies, mutate, heads=None):
        program = mutate(compile_primitive(table, layout))
        try:
            run_case(table, layout, bodies, heads, program=program)
        except ValueError:
            caught.append(name)
        else:
            raise ValueError("undetected target mutant: " + name)
    def alter(program, index, node):
        states = list(program.states)
        states[index] = node
        return replace(program, states=tuple(states))
    layout = Layout(3, (0,), (1,), (2,))
    def skip_pre(program):
        # The first reachable source dispatch is the minimum-index nop.
        entry = next(i for i, n in enumerate(program.states) if n[0] == "nop")
        return replace(program, initial=entry)
    detects("omit_pre_retirement", (("halt",),), layout, [[], [1, 0, 1], [0]], skip_pre)
    def omit_post(program):
        # On a halt-only table, after its dispatch there are exactly three
        # final-origin loops before post-retirement. Bypass that last chain.
        states = program.states
        pc = next(n[1] for n in states if n[0] == "nop")
        for _ in range(3):
            read = states[pc][3]
            right = states[read][2][2]
            after = states[right][3]
            last = right
            pc = after
        success = next(i for i, n in enumerate(states) if n == ("stop", "success", ""))
        return alter(program, last, states[last][:-1] + (success,))
    detects("omit_post_retirement_clock", (("halt",),), layout,
            [[], [], [0]], omit_post)
    empty = Layout(2, (0,), (), (1,))
    table = (("move", 1, -1), ("halt",))
    def skip_restore(program):
        i = next(i for i, n in enumerate(program.states)
                 if n[0] == "move" and n[1:3] == (1, 1)
                 and program.states[n[3]] == ("stop", "reject", "native context crossed its local origin"))
        return alter(program, i, ("nop", program.states[i][3]))
    detects("omit_context_left_restoration", table, empty, [[], [0]], skip_restore)
    table = (("move", 1, 1), ("halt",))
    def cross_frontier(program):
        i = next(i for i, n in enumerate(program.states) if n[0] == "read" and n[1] == 1
                 and program.states[n[2][6]] == ("stop", "reject", "context frontier cannot be crossed"))
        node = program.states[i]
        edges = list(node[2]); edges[6] = edges[0]
        return alter(program, i, ("read", 1, tuple(edges)))
    detects("permit_context_frontier_crossing", table, empty, [[], []], cross_frontier)
    table = (("write", 1, 0), ("halt",))
    def write_context(program):
        i = next(i for i, n in enumerate(program.states) if n[0] == "nop")
        terminal = program.states[i][1]
        return alter(program, i, ("write", 1, 0, terminal))
    detects("physical_context_write", table, empty, [[], [1]], write_context)
    table = (("branch", 1, ((6, 1),), 2), ("halt",), ("reject", "wrong logical blank"))
    def confuse_blank(program):
        i = next(i for i, n in enumerate(program.states) if n[0] == "read" and n[1] == 1
                 and n[2][0] == n[2][1] and n[2][0] != n[2][6])
        node = program.states[i]
        edges = list(node[2]); edges[6] = edges[0]
        return alter(program, i, ("read", 1, tuple(edges)))
    detects("conflate_raw_and_coded_blank", table, empty, [[], []], confuse_blank)
    guards = []
    for name, bad in [
        ("aliased_context", Layout(2, (0,), (), (0,))),
        ("aliased_work", Layout(2, (0,), (1, 1), ())),
        ("missing_field", Layout(2, (), (0,), (1,))),
        ("bad_global_port", Layout(2, (0,), (), (2,))),
        ("boolean_port", Layout(2, (False,), (), (1,))),
    ]:
        try:
            compile_primitive((("halt",),), bad)
        except ValueError:
            guards.append(name)
        else:
            raise ValueError("layout guard escaped")
    return dict(detected_target_mutants=caught, rejected_layouts=guards)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    records = authenticate()
    protocol = protocol_suite()
    result = dict(schema=1, base="e54523517d0f03e58352e647c403a5af3e525a57",
                  source_files=len(records), protocol_cases=len(protocol),
                  protocol_trace_digest=hashlib.sha256(json.dumps(protocol, sort_keys=True).encode()).hexdigest(),
                  retirement=retirement_suite(), providers=provider_suite(), controls=controls_suite(),
                  scope="actual Controller.primitive; no recursive Controller or tariff conversion")
    result = json.loads(json.dumps(result))
    path = ROOT / "evidence/RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(result == json.loads(path.read_text()), "frozen evidence mismatch")
    print("PASS_CONTEXTUAL_PRIMITIVE_MICROCONTROL", result["protocol_cases"],
          result["providers"]["cases"], len(result["controls"]["detected_target_mutants"]))


if __name__ == "__main__":
    main()
