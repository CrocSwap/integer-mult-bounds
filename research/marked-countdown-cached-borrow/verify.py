#!/usr/bin/env python3
"""Exact evidence for the new cached-borrow decrement and its caller saving.

Produced by Nick Petalas. Apache-2.0.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from countdown import decrement
SOURCE = "research/linear-sign-total-traffic/sources/"
MODULES = ("words", "records", "stream", "cardinality", "counts", "bitstream", "linear_sign")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    data = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            payload = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(payload).hexdigest() == row["sha256"], "source hash")
            data[Path(row["path"]).stem] = payload
    require(set(data) == set(MODULES), "complete seven-module closure")
    return data


@contextmanager
def loaded(data):
    """Compile only seven authenticated modules; never consume cached bytecode."""
    previous = {name: sys.modules.get(name) for name in MODULES}
    modules = {}
    try:
        for name in MODULES:
            module = types.ModuleType(name)
            module.__file__ = str(ROOT / SOURCE / (name + ".py"))
            sys.modules[name] = modules[name] = module
            exec(compile(data[name], module.__file__, "exec"), module.__dict__)
        words = modules["words"]
        require((words.ZERO, words.ONE, words.LEFT, words.RIGHT, words.BLANK) == tuple(range(5)),
                "pinned tape alphabet")
        yield modules
    finally:
        for name, original in previous.items():
            if original is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original


def meter(tape):
    m = tape.meter
    return [m.reads, m.writes, m.moves]


def counter_fixture(modules, n, digits):
    words, baseline = modules["words"], modules["stream"].Counter

    class CachedCounter(baseline):
        decrement = decrement

    arena = words.Arena(digits)
    source = arena.input(n)
    initial = bytes(source.cells)
    old, new = baseline(source), CachedCounter(source)
    for remaining in range(n, 0, -1):
        require(not old.finished and not new.finished, "early completion")
        old.decrement()
        new.decrement()
        require(old.tape.cells == new.tape.cells and old.finished == new.finished,
                "identical canonical counter state")
        require(old.tape.head == new.tape.head == 1, "first-digit head")
        actual = sum(bit << j for j, bit in enumerate(new.tape.cells[1:]) if bit in (0, 1))
        require(actual == remaining - 1, "decoded observation after execution")
    require(old.finished and new.finished, "complete countdown")
    old.close()
    new.close()
    require(all(x == words.BLANK for x in new.tape.cells[1:]), "private blank return")
    require(old.tape.head == new.tape.head == 1, "closed head")
    require(bytes(source.cells) == initial and source.head == 1, "input preserved")
    old_bill, new_bill = meter(old.tape), meter(new.tape)
    require([a - b for a, b in zip(old_bill, new_bill, strict=True)] == [n, 0, 0],
            "exact read-only saving")
    try:
        new.decrement()
    except ValueError:
        pass
    else:
        raise ValueError("finished decrement accepted")
    arena.free(source)
    return [n, digits, old_bill, new_bill]


class Caller:
    def __init__(self, modules, cached):
        self.modules, self.tapes, self.counters, self.origin = modules, [], [], None
        owner, original_tape = self, modules["records"].Tape
        baseline = modules["stream"].Counter

        class TracedTape(original_tape):
            def __init__(self):
                super().__init__()
                self.payload, self.origins = False, {}
                owner.tapes.append(self)

            def read(self):
                symbol = super().read()
                if self.payload and symbol in (0, 1):
                    owner.origin = self.head - 1
                return symbol

            def write(self, symbol):
                if symbol in (0, 1):
                    self.origins[self.head] = owner.origin
                super().write(symbol)

        class CachedCounter(baseline):
            decrement = decrement

        chosen = CachedCounter if cached else baseline

        def counter(word):
            result = chosen(word)
            owner.counters.append(result)
            return result

        self.Tape = TracedTape
        for module in modules.values():
            if hasattr(module, "Tape"):
                module.Tape = TracedTape
            if hasattr(module, "Counter"):
                module.Counter = counter

    def bill(self, arena):
        result = [arena.meter.reads, arena.meter.writes, arena.meter.moves]
        for tape in self.tapes:
            result = [a + b for a, b in zip(result, meter(tape), strict=True)]
        return result


def check_sign_state(caller, arena, source, output, before, suffix, initial, params):
    m, b, s = params
    wanted = []
    for address in range(m * b * s):
        row, inner = divmod(address, s)
        outer, atom = divmod(row, m)
        wanted.append((outer * m + (-atom) % m) * s + inner)
    require([output.origins[i + 1] for i in range(m * b * s)] == wanted,
            "every output source coordinate")
    require(bytes(output.cells[1:]) == bytes(initial[i + 1] for i in wanted), "output bits")
    require(bytes(source.cells) == initial and source.head == output.head == 1,
            "source and output heads")
    require(before.tape.head == suffix.tape.head == 1, "extent heads")
    for counter in caller.counters:
        require(counter.finished and counter.tape.head == 1, "counter closed at origin")
        require(all(x == 4 for x in counter.tape.cells[1:]), "every private counter blank")
    require(len(arena.live) == 2, "temporary numerical slots returned")
    return hashlib.sha256(json.dumps(wanted).encode()).hexdigest()


def forbidden_decode(_word):
    raise ValueError("runtime decode")


def sign_fixture(data, params, cached):
    with loaded(data) as modules:
        caller = Caller(modules, cached)
        m, b, s = params
        words = modules["words"]
        arena = words.Arena(m.bit_length() + 1)
        modulus = arena.input(m)
        ring = words.Ring(modulus)
        bc, sc = modules["counts"].Count.literal(b), modules["counts"].Count.literal(s)
        before, suffix = bc.marginal(), sc.marginal()
        bc.close()
        sc.close()
        source = caller.Tape()
        source.cells.extend((i * 7 + i // 3) % 2 for i in range(m * b * s))
        source.payload = True
        initial = bytes(source.cells)
        protected = {slot: bytes(arena.words[slot].cells) for slot in arena.live}
        extents = (bytes(before.tape.cells), bytes(suffix.tape.cells))
        old_inspect = words.Word.inspect
        words.Word.inspect = forbidden_decode
        start = caller.bill(arena)
        try:
            output = modules["linear_sign"].sign_address(source, ring, 3, before, suffix)
            end = caller.bill(arena)
            digest = check_sign_state(caller, arena, source, output, before, suffix, initial, params)
            require(set(protected) == arena.live, "same numerical owners")
            require(all(bytes(arena.words[k].cells) == v and arena.words[k].head == 1
                        for k, v in protected.items()), "borrowed numerical state")
            require((bytes(before.tape.cells), bytes(suffix.tape.cells)) == extents,
                    "borrowed extent state")
            output.clear()
            source.clear()
        finally:
            words.Word.inspect = old_inspect
            before.close()
            suffix.close()
            ring.close()
            arena.free(modulus)
        require(not arena.live, "fixture cleanup")
        return [[y - x for x, y in zip(start, end, strict=True)], digest, len(caller.counters)]


def sign_checks(data):
    rows = []
    for m in (2, 3, 9, 25, 65):
        for b in (1, 3):
            for s in (1, 2, 7):
                params = (m, b, s)
                old, new = sign_fixture(data, params, False), sign_fixture(data, params, True)
                saving = b * (3 * m - 4 + 4 * (m - 2) * s + (m * s if s != 1 else 0))
                require(old[1:] == new[1:], "same complete address map and counter inventory")
                require([a - z for a, z in zip(old[0], new[0], strict=True)] == [saving, 0, 0],
                        "complete caller exact saving")
                rows.append([*params, saving, old, new])
    return rows


def controls(modules):
    baseline = modules["stream"].Counter
    arena = modules["words"].Arena(3)
    source = arena.input(1)
    counter = baseline(source)
    counter.tape.cells[1] = 3
    try:
        decrement(counter)
    except ValueError:
        pass
    else:
        raise ValueError("nonbinary borrow terminator accepted")
    counter.tape.cells[1] = 1
    decrement(counter)
    require(counter.finished, "restored positive control")
    counter.close()
    arena.free(source)
    return ["finished decrement rejects", "invalid terminator rejects"]


def hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(PACKAGE.iterdir()) if p.is_file() and p.name != "RESULT.json"}


def run():
    data = authenticate()
    with loaded(data) as modules:
        counters = [counter_fixture(modules, n, max(2, n.bit_length()) + padding)
                    for n in range(129) for padding in (0, 1, 7)]
        rejected = controls(modules)
    signs = sign_checks(data)
    return {"status": "PASS_MARKED_COUNTDOWN_CACHED_BORROW", "counter_cases": len(counters),
            "decrement_states": sum(row[0] for row in counters),
            "counter_digest": hashlib.sha256(json.dumps(counters).encode()).hexdigest(),
            "sign_cases": len(signs), "sign_addresses": sum(r[0] * r[1] * r[2] for r in signs),
            "sign_rows": signs, "controls": rejected, "source_files": len(data), "hashes": hashes()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-result", action="store_true")
    args = parser.parse_args()
    result = run()
    if not args.emit_result:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "generated receipt equality")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
