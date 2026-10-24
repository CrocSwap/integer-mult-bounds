#!/usr/bin/env python3
"""Source-bound request traces and local suspension checks, not full-node acceptance.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import contextmanager
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
from pathlib import Path
import re
import sys
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ADAPTER = ROOT / "research/selected-complex-compact-adapters"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reject(name, action):
    try:
        action()
    except ValueError:
        return name
    raise ValueError("mutation accepted: " + name)


@contextmanager
def actual_modules():
    """Execute authenticated source bytes directly, without bytecode imports."""
    saved = {name: sys.modules.get(name) for name in ("streams", "compact", "monomial")}
    try:
        loaded = []
        for name in saved:
            module = ModuleType(name)
            module.__file__ = str(ADAPTER / (name + ".py"))
            sys.modules[name] = module
            exec(compile(Path(module.__file__).read_bytes(), module.__file__, "exec"), module.__dict__)
            loaded.append(module)
        yield tuple(loaded)
    finally:
        for name, old in saved.items():
            if old is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            require(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "source bytes: " + row["path"])
    bit = (ROOT / "research/unconditional-batched-crt/BIT.md").read_text()
    match = re.search(r"a2=c\(1-c\^2\)=(\d+\.\d+)", bit)
    require(match is not None, "actual ordinary saving")
    a2 = Q(match[1])
    require(0 < a2 < 1 and a2 == Q("0.001733394791695384296"), "saving range")
    return a2


def guard_checks():
    cases = 0
    for p in (2, 3, 17, 257, 4096, 10**6):
        logceil = (p - 1).bit_length()
        g = 4 * logceil + 6
        k = 128 * g
        require(k >= g + 4 * logceil + 10, "actual sufficient spacing")
        for f in (1, 2, min(p, 13)):
            n = f - 1
            delta = n * (Q(2, 2**g) + Q(8, 2**(k - g)))
            require(n <= p and delta <= Q(5, 128 * p**3), "complete-range bad density")
            cases += 1
    return cases


def request_trace(compact, monomial, f, late, wrong_n=False, unsplit_root=False):
    """Run the actual lowering; replace payload execution only by explicit recording."""
    g, k, rho = 10, 1280, 0
    n = f - 1
    width = (146 if unsplit_root else n) * g
    fields = (("u", width), ("t", width), ("v0", f * k), ("v1", f * k), ("b", width))
    layout = compact.Layout(fields, 8)
    recipe = {"matrix_rows": [3, 2] if late else [1, 3], "offset": 0,
              "quadratic_rows": [0, 0], "linear_Z4": [0, 0], "phase": 0}
    captured = []

    def record(source, reached_layout, word):
        if wrong_n:
            word = compact.Compact(f, word.K, word.G, word.rho, word.source, word.target, word.late)
        word.validate(reached_layout)
        operations = word.operations()
        swaps = [op for op in operations if op[0] == "swap"]
        rotations = [op for op in operations if op[0] == "rotate"]
        widths = [reached_layout.width(op[1]) for op in swaps]
        require(all(reached_layout.width(op[1]) == reached_layout.width(op[2]) for op in swaps),
                "equal reached ordinary fields")
        require(widths == [n * g] * (12 if late else 4), "actual all-column ordinary width/count")
        require(len(rotations) == (10 if late else 4), "actual rotation count")
        captured.append({"f": f, "late": late, "width": n * g, "swaps": len(swaps), "rotations": len(rotations)})
        return source

    monomial.execute = record
    monomial.phase_pass = lambda source, *args, **kwargs: source
    monomial.digit_permutation = lambda source, *args, **kwargs: source
    monomial.flip_digit = lambda source, *args, **kwargs: source
    sentinel = object()
    require(monomial.execute_monomial(sentinel, layout, recipe, f, k, g, rho, 4) is sentinel,
            "lowering request trace")
    require(len(captured) == int(f > 1), "no zero-width ordinary request at f=1")
    return captured


def cycle(streams, prefix_size, scan_ancestors=False, drop_spectator=False,
          omit_descriptor=False, omit_erase=False):
    """Tiny relative-stack caller trace with a supplied completed child result."""
    meter = streams.Meter()
    labels = list(product(range(2), range(3), range(2), range(2), range(2)))
    borrowed = bytes(((j * 13 + b * 7 + (j >> b)) & 1) for j in range(len(labels)) for b in range(4))
    parent = streams.Tape(meter, borrowed)
    selected = streams.Tape(meter)
    for family, cover, stock, active, spectator in labels:
        value = parent.read(4)
        if family == 1 and cover == 2 and (not drop_spectator or spectator == 0):
            selected.write(value)
    parent.finish()
    parent.rewind()
    dirty = bytes((i * 5 + (i >> 2)) & 1 for i in range(prefix_size))
    descriptor = bytes((1, 0, 1, 1))
    size = len(descriptor) + len(borrowed)
    backing = bytearray(dirty + bytes(size))
    head = prefix_size
    if scan_ancestors:
        ancestor = streams.Tape(meter, dirty)
        ancestor.head = prefix_size
        ancestor.rewind()
        ancestor.read(prefix_size)
    for bit in descriptor + parent.read(len(borrowed)):
        backing[head] = bit
        head += 1
        meter.writes += 1
        meter.moves += 1
    parent.finish()
    parent.rewind()
    meter.moves += size
    head -= size
    recovered = bytes(backing[head:head + len(descriptor)])
    meter.reads += len(descriptor)
    meter.moves += len(descriptor)
    head += len(descriptor)
    require((b"" if omit_descriptor else recovered) == descriptor, "return descriptor")
    restored = streams.Tape(meter)
    for _ in borrowed:
        restored.write(bytes((backing[head],)))
        head += 1
        meter.reads += 1
        meter.moves += 1
    restored.rewind()
    # The opaque completed child's payload is supplied; its recursive work is excluded.
    child_result = streams.Tape(meter, bytes(bit ^ 1 for bit in selected.data))
    output = streams.Tape(meter)
    expected = bytearray()
    for j, (family, cover, stock, active, spectator) in enumerate(labels):
        old = restored.read(4)
        chosen = family == 1 and cover == 2
        output.write(child_result.read(4) if chosen else old)
        expected.extend(bit ^ int(chosen) for bit in borrowed[j * 4:(j + 1) * 4])
    restored.finish()
    child_result.finish()
    output.rewind()
    for tape in (restored, selected, child_result):
        tape.erase()
        require(not tape.data and tape.head == 0, "owned local work return")
    meter.moves += size
    head -= size
    if not omit_erase:
        for _ in range(size):
            backing[head] = 0
            head += 1
            meter.writes += 1
            meter.moves += 1
        meter.moves += size
        head -= size
    require(backing[:prefix_size] == dirty, "dirty ancestors preserved")
    require(not any(backing[prefix_size:]) and head == prefix_size, "local stack erasure/head return")
    require(parent.data == borrowed and parent.head == 0, "borrowed parent preserved")
    require(output.data == expected, "complete gather/return/replace endpoint")
    return meter.reads + meter.writes + meter.moves + meter.erases


def main():
    a2 = authenticate()
    guard_cases = guard_checks()
    controls = []
    with actual_modules() as (streams, compact, monomial):
        requests = [request_trace(compact, monomial, f, late) for f, late in product((1, 2, 3, 13), (False, True))]
        controls.append(reject("wrong_compact_n", lambda: request_trace(compact, monomial, 2, False, wrong_n=True)))
        controls.append(reject("unsplit_root_reservoir", lambda: request_trace(compact, monomial, 2, False, unsplit_root=True)))
        extents = (16, 257, 4096)
        costs = [cycle(streams, n) for n in extents]
        require(len(set(costs)) == 1, "local movement independent of dirty ancestor extent")
        controls.append(reject("global_ancestor_rewind", lambda: require(cycle(streams, 4096, scan_ancestors=True) == costs[0], "ancestor traversal is not local")))
        for name, flag in (("missing_complete_spectator", "drop_spectator"),
                           ("missing_return_descriptor", "omit_descriptor"),
                           ("un-erased_local_stack", "omit_erase")):
            controls.append(reject(name, lambda flag=flag: cycle(streams, 257, **{flag: True})))
        ancestor = streams.Tape(streams.Meter(), bytes((1, 0, 1, 1)))
        ancestor.erase()
        controls.append(reject("naive_full_backing_erase", lambda: require(ancestor.data == bytes((1, 0, 1, 1)), "erased protected ancestor")))
    n, polylog_degree = 100000, 3
    require(2**(a2 * n).__floor__() > (2 * n)**polylog_degree, "per-axis/polylog separation fixture")
    path_ratios = [Q(322560, 73)**d for d in (2, 4, 8)]
    require(all(ratio > 1 for ratio in path_ratios), "ancestor scan/local bill countermodel")
    print(json.dumps({"status": "PASS_COMPLEX_NODE_NONCHILD_INVOICE", "guard_cases": guard_cases,
                      "request_trace": requests, "ancestor_extents": extents, "local_payload_primitives": costs,
                      "controls_rejected": controls,
                      "scope": "conditional compact/scan invoice and exact locality gap; no physical N(i) acceptance"}, sort_keys=True))


if __name__ == "__main__":
    main()
