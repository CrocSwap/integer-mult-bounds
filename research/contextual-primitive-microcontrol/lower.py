"""Finite microcontrol for the retained Controller.primitive interface.

All graph construction happens before runtime inputs vary. The target graph
has only fixed read, write, unit-move, no-op and terminal states. Python graph
lists/sets and integer state identifiers are construction apparatus.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from dataclasses import dataclass
from source_binding import need, vendor

OLD = vendor("old_lower", "retained/lower.py")


@dataclass(frozen=True)
class Layout:
    total_ports: int
    fields: tuple
    work: tuple = ()
    contexts: tuple = ()

    @property
    def local_ports(self):
        return self.fields + self.work + self.contexts

    def validate(self):
        need(type(self.total_ports) is int and self.total_ports >= 1,
             "positive fixed global port count")
        need(all(type(v) is tuple for v in (self.fields, self.work, self.contexts)),
             "fixed ordered port tuples")
        need(bool(self.fields), "nonempty actual primitive fields")
        ports = self.local_ports
        need(all(type(i) is int and 0 <= i < self.total_ports for i in ports),
             "fixed global port index")
        need(len(set(ports)) == len(ports), "data, work and context ports distinct")
        return self


def successors(node):
    if node[0] == "stop":
        return ()
    if node[0] == "read":
        return node[2]
    return (node[-1],)


def redirect(node, mapping):
    if node[0] == "stop":
        return node
    if node[0] == "read":
        return ("read", node[1], tuple(mapping.get(i, i) for i in node[2]))
    return node[:-1] + (mapping.get(node[-1], node[-1]),)


def trim(states, initial):
    """Construction-time reachable graph; removes obsolete coded context paths."""
    todo = [initial]
    seen = set()
    while todo:
        here = todo.pop()
        if here in seen:
            continue
        seen.add(here)
        todo.extend(successors(states[here]))
    order = sorted(seen)
    mapping = {old: new for new, old in enumerate(order)}
    return tuple(redirect(states[i], mapping) for i in order), mapping[initial]


def state_bound(table_rows, layout):
    layout.validate()
    return 52 * table_rows + 3 * len(layout.local_ports) + 18 * len(layout.work) + 9


def compile_primitive(table, layout):
    """Compile one statically selected Controller.primitive(token, fields).

    The source wrapper retires work in order, executes a finite table with
    coded fields/work and raw readonly contexts, then retires work again on
    success. It does not run the post-retirement on rejection. A fixed
    service-token lookup is resolved here, never performed by the target.
    """
    layout.validate()
    local = layout.local_ports
    coded_count = len(layout.fields) + len(layout.work)
    table = OLD.validate(table, len(local))
    old = OLD.compile_table(table, len(local))
    states = list(old.states)

    def emit(node):
        states.append(tuple(node))
        return len(states) - 1

    def error(label):
        return emit(("stop", "reject", label))

    bad_context = error("binary context alphabet")
    readonly = error("native context is read-only")
    frontier = error("context frontier cannot be crossed")
    left = error("native context crossed its local origin")
    bad_body = error("contiguous binary body")

    # The predecessor's coded-port lowering is retained verbatim for coded
    # rows. Replace only raw-context row entries, then discard unreachable
    # old expansions. Each source row still has exactly one dispatch no-op.
    for pc, row in enumerate(table):
        op = row[0]
        if op not in ("branch", "write", "move") or row[1] < coded_count:
            continue
        port = row[1]
        if op == "branch":
            cases = dict(row[2])
            edges = tuple(cases.get(s, row[3]) if s in (0, 1, 6)
                          else bad_context for s in range(7))
            start = emit(("read", port, edges))
        elif op == "write":
            start = readonly
        elif row[2] == 1:
            move = emit(("move", port, 1, pc + 1))
            start = emit(("read", port, tuple(move if s in (0, 1)
                                               else frontier for s in range(7))))
        else:
            restore = emit(("move", port, 1, left))
            test = emit(("read", port, tuple(restore if s == 2 else pc + 1
                                              for s in range(7))))
            start = emit(("move", port, -1, test))
        states[pc] = ("nop", start)

    def origin(port, nxt):
        start = len(states)
        states.extend([
            ("move", port, -1, start + 1),
            ("read", port, tuple(start + 2 if s == 2 else start for s in range(7))),
            ("move", port, 1, nxt),
        ])
        return start

    def retire(port, nxt):
        finish = origin(port, nxt)
        scan = len(states)
        states.extend([
            None,
            ("write", port, 6, scan + 2),
            ("move", port, 1, scan),
        ])
        states[scan] = ("read", port, tuple(scan + 1 if s in (0, 1)
                                             else finish if s == 6 else bad_body
                                             for s in range(7)))
        return origin(port, scan)

    # All old table-origin returns lead through the post wrapper. Redirect
    # only the old/context graph, not the newly added retirement-to-success.
    success = next(i for i, node in enumerate(states)
                   if node == ("stop", "success", ""))
    before_cleanup = len(states)
    cleanup = success
    for local_work in reversed(range(len(layout.fields), coded_count)):
        cleanup = retire(local_work, cleanup)
    if cleanup != success:
        for i in range(before_cleanup):
            states[i] = redirect(states[i], {success: cleanup})
    initial = old.initial
    for local_work in reversed(range(len(layout.fields), coded_count)):
        initial = retire(local_work, initial)

    states, initial = trim(states, initial)
    mapped = []
    for node in states:
        mapped.append(node if node[0] in ("nop", "stop")
                      else (node[0], local[node[1]]) + node[2:])
    program = OLD.Program(layout.total_ports, len(table), tuple(mapped), initial)
    OLD.check_program(program)
    need(len(program.states) <= state_bound(len(table), layout), "finite state bound")
    need(all(node[0] != "write" or node[1] not in layout.contexts
             for node in program.states), "readonly context has no target writes")
    return program


def retirement_actions(length, initial_head):
    """Successful literal retirement of a finite contiguous binary body."""
    need(type(length) is int and length >= 0 and type(initial_head) is int
         and initial_head >= 0, "nonnegative body and local head")
    return 2 * initial_head + 5 * length + 7
