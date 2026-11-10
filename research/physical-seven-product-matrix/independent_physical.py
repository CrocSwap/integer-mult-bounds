"""Independent physical I/O adapter for the classical matrix oracle.

Host integers appear only in fixture encoding, output observation and the
classical oracle, outside the no_decode physical invocation.
@CubeJerry, with substantial OpenAI assistance. Apache-2.0.
"""

import time
from types import ModuleType, FunctionType, MethodType


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tape_closure(owner, Tape):
    """Observer-only reachability, independent of the kernel's forbidden list."""
    pending, seen, found = [owner], set(), set()
    while pending:
        item = pending.pop()
        if id(item) in seen:
            continue
        seen.add(id(item))
        if isinstance(item, Tape):
            found.add(item)
        elif isinstance(item, dict):
            pending.extend(item.values())
        elif isinstance(item, (tuple, list, set, frozenset)):
            pending.extend(item)
        elif not isinstance(item, (type, ModuleType, FunctionType, MethodType)):
            namespace = getattr(item, "__dict__", None)
            if namespace is not None:
                pending.extend(namespace.values())
    return found


def write_fixture(tape, values, width):
    limit = 1 << (width-1)
    for value in values:
        require(-limit <= value < limit, "fixture fits signed input width")
        raw = value % (1 << width)
        for bit in range(width):
            tape.append((raw >> bit) & 1)
    tape.rewind()


def observe_return(tape, entries, width, blank):
    tape.rewind()
    values = []
    for _ in range(entries):
        raw = 0
        for bit in range(width):
            value = tape.read()
            require(value in (0, 1), "complete independent observed record")
            raw |= value << bit
            tape.step(1)
        values.append(raw-(1 << width) if raw & (1 << (width-1)) else raw)
    require(tape.read() == blank, "exact independent return extent")
    tape.rewind()
    return tuple(values)


def run(kernel_class, oracle):
    from cardinal_counts import Count
    from check_support import no_decode
    from records import Tape
    from session import erase_marker
    from words import BLANK

    owner = kernel_class()
    discovered = tape_closure(owner, Tape)
    require(set(owner.forbidden()) == discovered, "complete independently discovered owned tape closure")
    rows = []
    for case in oracle.fixtures():
        n, w, wide = case["dimension"], case["width"], case["wide"]
        first, second = Tape(), Tape()
        write_fixture(first, case["first"], w)
        write_fixture(second, case["second"], w)
        block, width, output_width = Count.literal(n), Count.literal(w), Count.literal(wide)
        counts = (block, width, output_width)
        ports = (first, second, *(x.tape for x in counts))
        before_ports = tuple((bytes(t.cells), t.head) for t in ports)
        before = (owner.nodes, owner.leaves, owner.pushes, owner.pops, owner.arithmetic.products)
        started = time.monotonic()
        with no_decode():
            result = owner.run(first, second, block, width, output_width)
        elapsed = time.monotonic()-started
        require(owner.pending and owner.closed and result is owner.output, "protected returned owner")
        require(before_ports == tuple((bytes(t.cells), t.head) for t in ports),
                "independent borrowed-content/head restoration")
        actual = observe_return(result, n*n, wide, BLANK)
        evidence = oracle.check(case["first"], case["second"], actual, n, w, wide)
        after = (owner.nodes, owner.leaves, owner.pushes, owner.pops, owner.arithmetic.products)
        delta = tuple(b-a for a, b in zip(before, after))
        ell = n.bit_length()-1
        nodes, leaves = (7**(ell+1)-1)//6, 7**ell
        require(delta == (nodes, leaves, nodes-1, nodes-1, leaves),
                "complete physical seven-child tree and actual scalar calls")
        owner.consume()
        owner.idle()
        require(discovered == tape_closure(owner, Tape), "fixed owner role inventory under reuse")
        require(all(t.head == 1 and all(bit == BLANK for bit in t.cells) for t in discovered),
                "independent complete owned backing erasure")
        evidence.update(name=case["name"], seconds=elapsed, counters=delta,
                        owned_roles=len(discovered),
                        retained_owned_cells=sum(len(t.cells) for t in discovered))
        rows.append(evidence)
        for tape in (first, second):
            tape.clear()
            erase_marker(tape)
        for count in counts:
            count.close()
            erase_marker(count.tape)
    return {"method": "independent classical integer products and raw bit I/O",
            "fixtures": rows, "oracle_selfcheck": oracle.selfcheck()}
