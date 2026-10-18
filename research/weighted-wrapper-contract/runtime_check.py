"""Unchanged PR2808 body/padding on complete Boolean coordinate planes.

Weighted callees are checker-only permutations, not implemented suppliers.
No predecessor checker is used as our endpoint oracle. Apache-2.0.
"""
import importlib.util
import json
import sys
from contextlib import contextmanager
from hashlib import sha1, sha256
from pathlib import Path

from algebra import need

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
SOURCE = ROOT / "research/selected-outer-borrowing-wrapper"


def authenticate(root=ROOT):
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    count = 0
    for item in manifest["files"]:
        if item.get("usage") != "input":
            continue
        data = (root / item["path"]).read_bytes()
        need(sha256(data).hexdigest() == item["sha256"], "source SHA256: " + item["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(sha1(blob, usedforsecurity=False).hexdigest() == item["git_blob"],
             "source Git blob: " + item["path"])
        count += 1
    return count


def load_source(name, path):
    """Compile authenticated bytes directly, without source-adjacent bytecode."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


@contextmanager
def installed():
    authenticate()
    names = ("_weighted_audit_predecessor", "_weighted_audit_outer")
    need(not set(names).intersection(sys.modules), "private namespace starts empty")
    predecessor = load_source(names[0], SOURCE / "predecessor.py")
    try:
        with predecessor.installed():
            yield load_source(names[1], SOURCE / "outer.py")
    finally:
        for name in names:
            sys.modules.pop(name, None)


def digits(value, modulus, n):
    result = [0] * n
    for i in range(n - 1, -1, -1):
        value, result[i] = divmod(value, modulus)
    need(value == 0, "bounded digit vector")
    return result


def number(values, modulus):
    result = 0
    for value in values:
        result = result * modulus + value
    return result


def unpack(address, width, gap, suffix):
    address, tail = divmod(address, suffix)
    address, d = divmod(address, width)
    address, middle = divmod(address, gap)
    prefix, h = divmod(address, width)
    return prefix, h, middle, d, tail


def pack(prefix, h, middle, d, tail, width, gap, suffix):
    return (((prefix * width + h) * gap + middle) * width + d) * suffix + tail


def weighted_destination(address, modulus, weights, gap, suffix):
    width, n = modulus**len(weights), len(weights)
    prefix, h, middle, d, tail = unpack(address, width, gap, suffix)
    hv, dv = digits(h, modulus, n), digits(d, modulus, n)
    nh = number([a*x % modulus for a, x in zip(weights, reversed(dv))], modulus)
    nd = number([x*pow(a, -1, modulus) % modulus
                 for x, a in zip(reversed(hv), reversed(weights))], modulus)
    return pack(prefix, nh, middle, nd, tail, width, gap, suffix)


def body_destination(address, modulus, first, second, gap, suffix):
    """Scalar-coordinate oracle for the six steps, separate from map-table census."""
    width, n = modulus**len(first), len(first)
    prefix, h, middle, d, tail = unpack(address, width, gap, suffix)
    h, d = digits(h, modulus, n), digits(d, modulus, n)
    d = [(y-x) % modulus for x, y in zip(h, d)]
    for call, weights in enumerate((first, second)):
        h, d = ([a*x % modulus for a, x in zip(weights, reversed(d))],
                [x*pow(a, -1, modulus) % modulus
                 for x, a in zip(reversed(h), reversed(weights))])
        d = ([(x+y) % modulus for x, y in zip(h, d)] if call == 0 else
             [(x-y) % modulus for x, y in zip(h, d)])
    return pack(prefix, number(h, modulus), middle, number(d, modulus), tail,
                width, gap, suffix)


def literal_case(outer, *, q, w, first, second, prefixes=1, rows=1,
                 stock=1, gap=1, suffix=1):
    from cardinal_counts import Count
    from records import Tape
    from words import Arena, Ring

    modulus, n = q**w, len(first)
    volume = prefixes * rows * modulus**(2*n) * gap * suffix
    need(volume <= 7000 and len(second) == n, "bounded literal fixture")
    arena, indices = Arena(modulus.bit_length()+1), Arena(max(3, n.bit_length()+1))
    mod, atoms = arena.input(modulus), indices.input(n)
    ring = Ring(mod)
    counts = [Count.literal(x) for x in (prefixes, rows, stock, gap, suffix)]
    count_bytes = [bytes(x.tape.cells) for x in counts]
    expected = [body_destination(i, modulus, first, second, gap, suffix)
                for i in range(volume)]
    swap, width = [], modulus**n
    for i in range(volume):
        pref, h, middle, d, tail = unpack(i, width, gap, suffix)
        swap.append(pack(pref, d, middle, h, tail, width, gap, suffix))
    need(len(set(expected)) == volume, "expected body is a permutation")
    recovered, calls = [0] * volume, []
    # Reserve code zero for fabricated padding, so even origin zero has a
    # distinguishing one bit. This also detects an original bit replaced by zero.
    planes = max(1, volume.bit_length())
    try:
        for plane in range(planes):
            source = Tape()
            for i in range(volume):
                source.append(((i+1) >> plane) & 1)
            source.rewind()
            saved = bytes(source.cells)
            call_index = 0

            def callee(padded, row_count):
                nonlocal call_index
                weights = (first, second)[call_index]
                call_index += 1
                # Checker-only decoding and permutation. No runtime-cost claim.
                padded_count = sum(bit << j for j, bit in enumerate(row_count.tape.cells[1:])
                                   if bit in (0, 1))
                total = prefixes * padded_count * modulus**(2*n) * gap * suffix
                before, row_before = bytes(padded.cells), bytes(row_count.tape.cells)
                target = [0] * total
                for i in range(total):
                    target[weighted_destination(i, modulus, weights, gap, suffix)] = padded.cells[i+1]
                output = Tape()
                for bit in target:
                    output.append(bit)
                output.rewind()
                need(bytes(padded.cells) == before and padded.head == 1, "callee input restored")
                need(bytes(row_count.tape.cells) == row_before and row_count.tape.head == 1,
                     "callee rows restored")
                calls.append(padded_count)
                return output

            output = outer.body_ordinary(source, atoms, ring, q, *counts, callee)
            try:
                need(call_index == 2, "exactly two weighted calls")
                need(bytes(source.cells) == saved and source.head == output.head == 1,
                     "literal body preserves source and heads")
                need(len(output.cells) == volume+1, "complete returned payload")
                for destination, bit in enumerate(output.cells[1:]):
                    need(bit in (0, 1), "Boolean output")
                    recovered[destination] |= bit << plane
            finally:
                output.clear()
                source.clear()
        for origin, destination in enumerate(expected):
            need(recovered[destination] == origin+1, "literal source origin oracle")
        need([bytes(x.tape.cells) for x in counts] == count_bytes, "borrowed counts restored")
        need(all(x.tape.head == 1 for x in counts), "count heads restored")
        need(arena.live == {mod.slot, ring.one.slot} and indices.live == {atoms.slot},
             "native numerical scratch released")
    finally:
        for count in counts:
            count.close()
        ring.close()
        arena.free(mod)
        indices.free(atoms)
    return dict(q=q, w=w, first=list(first), second=list(second), prefixes=prefixes,
                rows=rows, stock=stock, gap=gap, suffix=suffix, addresses=volume,
                bit_planes=planes, agreeing_addresses=sum(a == b for a, b in zip(expected, swap)),
                padded_row_counts=sorted(set(calls)), weighted_calls=len(calls),
                origin_sha256=sha256(json.dumps(recovered, separators=(",", ":")).encode()).hexdigest())


def run():
    with installed() as outer:
        cases = [literal_case(outer, q=3, w=1, first=(1, 1), second=(1, 1),
                              prefixes=2, rows=3, stock=2, gap=2, suffix=2),
                 literal_case(outer, q=3, w=2, first=(4, 1), second=(4, 1)),
                 literal_case(outer, q=3, w=2, first=(4, 7), second=(4, 7)),
                 literal_case(outer, q=3, w=1, first=(2,), second=(1,))]
    need(cases[0]["agreeing_addresses"] == cases[0]["addresses"], "reduced-field positive")
    need(cases[1]["agreeing_addresses"] == 729, "higher-precision failure count")
    need(cases[2]["agreeing_addresses"] == 6561, "reciprocal positive")
    need(cases[3]["agreeing_addresses"] < 9, "different involutions fail")
    return cases
