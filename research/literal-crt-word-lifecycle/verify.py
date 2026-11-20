"""Exact finite corroboration, source replay and rejecting semantic controls.

Universal claims are proved in PROOF.md. Host decoding is verifier-only.
"""
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
import json
import random
import sys
import types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import hardware
import lifecycle
import source_binding
import source_check


def need(condition, message):
    if not condition:
        raise ValueError(message)


def fixture(p, free, history=0):
    history = max(history, p + 2)
    ports = []
    for slot in range(64):
        digits = [str(((slot + 3) * 37 >> (i % 11)) & 1) for i in range(p)]
        cells = ["L"] + (["_"] * (p + 1) if slot in free else digits + ["R"])
        cells += ["_"] * (history - len(cells))
        ports.append(hardware.Tape(cells, 1))
    stack = ["L"] + [str((slot >> j) & 1) for slot in free for j in range(6)] + ["R"]
    ports.extend((hardware.Tape(["L"] + ["0"] * p + ["R"], 1),
                  hardware.Tape(stack + ["_"] * (338 - len(stack))),
                  hardware.Tape(["_"] * 8), hardware.Tape(["_"] * 8)))
    return ports


def stack_value(ports):
    cells = ports[lifecycle.STACK].cells
    end = cells.index("R")
    need(cells[0] == "L" and (end - 1) % 6 == 0, "stack grammar")
    return [sum(int(cells[i + j]) << j for j in range(6)) for i in range(1, end, 6)]


def assert_boundary(ports, free, expected, before, p):
    need(stack_value(ports) == free and len(set(free)) == len(free), "exact ordered free stack")
    need(all(t.head == (1 if i <= 64 else 0) for i, t in enumerate(ports)), "every physical head restored")
    need(all(s == "_" for i in (66, 67) for s in ports[i].cells), "selectors completely retired")
    for slot in range(64):
        need(ports[slot].cells == expected[slot], f"full Word owner {slot} including historical tail")
        need(len(ports[slot].cells) == len(before[slot]), "no historical capacity refund")
    need(ports[64].cells == before[64], "borrowed template unchanged")


def primitive_checks(code, metadata):
    packets = instructions = 0
    counts = Counter()
    for p in (4, 7, 31, 257):
        for m in range(1, 57):
            free = list(range(63, 63 - m, -1))
            for kind in ("TAKE", "ZERO", "COPY"):
                ports = fixture(p, free, 1025 if m in (1, 56) else 0)
                before = [list(t.cells) for t in ports]
                expected = [list(t.cells) for t in ports[:64]]
                machine = hardware.Program(code, metadata)
                if kind == "COPY":
                    need(machine.run(ports, metadata["setters"][0])["instructions"] == 31, "exact paid setter")
                result = machine.run(ports, kind)
                slot = free[-1]
                need(result["status"] == f"ALLOC_{slot}", "actual top owner returned")
                if kind == "ZERO":
                    expected[slot][1:p + 2] = ["0"] * p + ["R"]
                elif kind == "COPY":
                    expected[slot][1:p + 2] = before[0][1:p + 2]
                expected_steps = {"TAKE": 36 * m + 155,
                                  "ZERO": 165 * p + 36 * m + 417,
                                  "COPY": 287 * p + 97 * m + 676}[kind]
                need(result["instructions"] == expected_steps, "exact complete graph count")
                assert_boundary(ports, free[:-1], expected, before, p)
                packets += 1
                instructions += machine.steps
                counts[kind] += 1
        for m in range(56):
            free = list(range(63, 63 - m, -1))
            ports = fixture(p, free, 1025 if m in (0, 55) else 0)
            before = [list(t.cells) for t in ports]
            expected = [list(t.cells) for t in ports[:64]]
            machine = hardware.Program(code, metadata)
            machine.run(ports, metadata["setters"][8])
            result = machine.run(ports, "FREE")
            need(result["status"] == "FREED" and result["instructions"] == 160 * p + 61 * m + 409,
                 "exact successful physical erase/release")
            expected[8][1:p + 2] = ["_"] * (p + 1)
            assert_boundary(ports, free + [8], expected, before, p)
            packets += 1
            instructions += machine.steps
            counts["FREE"] += 1
    # Every finite handle, both live and free, at every possible stack length.
    for m in range(57):
        free = list(range(63, 63 - m, -1))
        ports = fixture(4, free)
        before = [list(t.cells) for t in ports]
        machine = hardware.Program(code, metadata)
        for slot in range(64):
            machine.run(ports, metadata["setters"][slot])
            result = machine.run(ports, "IS_LIVE")
            need(result["status"] == ("FREE" if slot in free else "LIVE"), "all-handle physical liveness")
            expected_steps = 61 * (free.index(slot) + 1) + 89 if slot in free else 61 * m + 90
            need(result["instructions"] == expected_steps, "exact liveness count")
            assert_boundary(ports, free, before[:64], before, 4)
            packets += 1
            counts["IS_LIVE"] += 1
        instructions += machine.steps
    return {"packets": packets, "instructions": instructions, "entries": dict(counts)}


def chronology_checks(code, metadata):
    rng = random.Random(20261120)
    p, free = 19, list(reversed(range(8, 64)))
    ports = fixture(p, free, 2049)
    machine = hardware.Program(code, metadata)
    expected = [list(t.cells) for t in ports[:64]]
    before = [list(t.cells) for t in ports]
    live = set(range(8))
    # A different noninitial stack permutation makes top-order errors observable.
    operations = []
    for _ in range(360):
        if live - set(range(8)) and (not free or rng.randrange(3) == 0):
            slot = rng.choice(sorted(live - set(range(8))))
            machine.run(ports, metadata["setters"][slot])
            got = machine.run(ports, "FREE")
            need(got["status"] == "FREED", "trace release")
            expected[slot][1:p + 2] = ["_"] * (p + 1)
            free.append(slot)
            live.remove(slot)
            operations.append(["FREE", slot])
        else:
            source = rng.choice(sorted(live))
            machine.run(ports, metadata["setters"][source])
            got = machine.run(ports, "COPY")
            slot = free.pop()
            need(got["status"] == f"ALLOC_{slot}", "trace allocation top")
            expected[slot][1:p + 2] = expected[source][1:p + 2]
            live.add(slot)
            operations.append(["COPY", source, slot])
        assert_boundary(ports, free, expected, before, p)
    for slot in sorted(live - set(range(8)), reverse=True):
        machine.run(ports, metadata["setters"][slot])
        machine.run(ports, "FREE")
        expected[slot][1:p + 2] = ["_"] * (p + 1)
        free.append(slot)
    assert_boundary(ports, free, expected, before, p)
    need(machine.run(ports, "CLOSE")["instructions"] == 1395, "complete metadata retirement")
    need(all(s == "_" for t in ports[65:] for s in t.cells), "all metadata bodies blank")
    need(all(len(t.cells) == 2049 for t in ports[:64]), "all physical histories retained after retirement")
    return {"seed": 20261120, "operations": len(operations), "instructions": machine.steps,
            "final_free_order": free, "retained_numeric_cells": sum(len(t.cells) for t in ports[:64])}


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def source_modules():
    w = load("words", HERE / "inputs/old-words.py")
    r = load("records", HERE / "inputs/old-records.py")
    e = load("entry", HERE / "inputs/old-entry.py")
    p = load("producer", HERE / "inputs/old-producer.py")
    return w, r, e, p


def canonical(r, w, pairs):
    tape = r.Tape()
    for pair in pairs:
        tape.append(r.ROOT)
        for value in pair:
            for bit in range(max(1, value.bit_length())):
                tape.append((value >> bit) & 1)
            tape.append(r.WORD_END)
        tape.append(r.RECORD_END)
    tape.append(w.RIGHT)
    tape.rewind()
    return tape


def current_entry(w, r, e, p):
    guide = e.Port(w)
    for _ in range(p):
        guide.append(w.ONE)
    guide.rewind()
    guards = tuple(e.Port(w) for _ in range(8))
    for i, guard in enumerate(guards):
        guard.cells.extend((r.RETURN, i % 2, w.BLANK, w.ONE))
    entry = e.Entry(w, r, guide, guards)
    for i, word in enumerate(entry.arena.words[8:]):
        word.cells.extend([w.BLANK] * (3 * i))
    return entry, guide, guards


@contextmanager
def blocked_lifecycle(w):
    names = ("zero", "copy", "free")
    original = {name: getattr(w.Arena, name) for name in names}
    erase = w.Word.erase
    def forbidden(*args, **kwargs):
        raise ValueError("OLD_LIFECYCLE_UNAVAILABLE")
    for name in names:
        setattr(w.Arena, name, forbidden)
    w.Word.erase = forbidden
    try:
        yield
    finally:
        for name, method in original.items():
            setattr(w.Arena, name, method)
        w.Word.erase = erase


def decode_word(word, w):
    end = word.cells.index(w.RIGHT, 1)
    return sum(int(bit) << j for j, bit in enumerate(word.cells[1:end]))


def source_checks(code, metadata):
    w, r, e, producer = source_modules()
    reports = []
    for p, left, right in ((7, [(5, 1)], [(7, 2)]),
                           (12, [(5, 1), (7, 2)], [(11, 7)]),
                           (12, [(3, 1)], [(5, 4), (7, 6)])):
        reference, _, _ = current_entry(w, r, e, p)
        ordinary = reference.invoke(producer, canonical(r, w, left), canonical(r, w, right))
        answer = (decode_word(ordinary["lower"], w), decode_word(ordinary["product"], w),
                  bytes(ordinary["stream"].cells), ordinary["left_valid"])
        # Independent CRT characterization of the reconstructed left integer.
        previous, congruences = 1, []
        for modulus, value in left:
            congruences.append((modulus, (previous * value) % modulus))
            previous *= modulus
        lower = next(x for x in range(previous) if all(x % mod == residue for mod, residue in congruences))
        need(answer[0] == lower and answer[1] == previous, "independent finite CRT oracle")
        reference.consume(ordinary)
        reference.close()
        entry, guide, guards = current_entry(w, r, e, p)
        borrowed = [(bytes(t.cells), t.head) for t in (guide, *guards)]
        identities = [id(t.cells) for t in (*entry.owned, *guards)]
        machine = hardware.Program(code, metadata)
        owner = source_binding.Owner(entry.arena, machine, hardware.Tape(["_"] * 338),
                                     hardware.Tape(["_"] * 8), hardware.Tape(["_"] * 8))
        with blocked_lifecycle(w):
            result = entry.invoke(producer, canonical(r, w, left), canonical(r, w, right))
            actual = (decode_word(result["lower"], w), decode_word(result["product"], w),
                      bytes(result["stream"].cells), result["left_valid"])
            need(actual == answer, "pinned complete current numerical producer output")
            entry.consume(result)
        entry.close()
        owner.close()
        need(borrowed == [(bytes(t.cells), t.head) for t in (guide, *guards)], "all actual borrowed guards/guide")
        need(identities == [id(t.cells) for t in (*entry.owned, *guards)], "same source physical owners")
        need(all(t.head == 1 and all(s == w.BLANK for s in t.cells) for t in entry.owned),
             "complete source Word histories and existing closure")
        need(all(t.head == 0 and set(t.cells) <= {"_"} for t in owner.ports[65:]),
             "new metadata retirement")
        kinds = Counter(row[0] for row in owner.operations if isinstance(row[0], str))
        reports.append({"p": p, "left": [list(row) for row in left], "right": [list(row) for row in right],
                        "lower": answer[0], "product": answer[1],
                        "lifecycle_instructions": machine.steps, "lifecycle_calls": machine.calls,
                        "entry_counts": dict(kinds), "source_owned_cells_after_close": sum(len(t.cells) for t in entry.owned)})
    return reports


def rejection_controls(code, metadata):
    results = []
    for name, p, free, entry, slot, mutate in (
        ("protected_free", 4, list(reversed(range(8, 64))), "FREE", 0, None),
        ("double_free", 4, list(reversed(range(8, 64))), "FREE", 8, None),
        ("copy_free_word", 4, list(reversed(range(8, 64))), "COPY", 8, None),
        ("short_template", 3, list(reversed(range(8, 64))), "ZERO", None, None),
        ("dirty_output", 4, list(reversed(range(8, 64))), "ZERO", None, lambda q: q[8].cells.__setitem__(1, "1")),
        ("short_live_word", 3, list(reversed(range(9, 64))), "FREE", 8, None),
        ("malformed_handle", 4, list(reversed(range(9, 64))), "FREE", 8, lambda q: q[66].cells.__setitem__(7, "_")),
        ("live_word_at_close", 4, list(reversed(range(9, 64))), "CLOSE", None, None),
    ):
        ports = fixture(p, free)
        machine = hardware.Program(code, metadata)
        if slot is not None:
            machine.run(ports, metadata["setters"][slot])
        if mutate:
            mutate(ports)
        need(machine.run(ports, entry)["status"] == "MALFORMED", name)
        results.append(name)
    ports = fixture(4, [])
    machine = hardware.Program(code, metadata)
    before = [(list(t.cells), t.head) for t in ports]
    need(machine.run(ports, "TAKE")["status"] == "EXHAUSTED", "empty stack rejection")
    need(before == [(list(t.cells), t.head) for t in ports], "empty TAKE preserves boundary")
    results.append("empty_take")
    # Returning corruption: every head and selector restores, but the wrong
    # physical result handle must be rejected by an independent owner oracle.
    mutant = tuple(("H", "ALLOC_9") if row == ("H", "ALLOC_8") else row for row in code)
    ports = fixture(4, list(reversed(range(8, 64))))
    got = hardware.Program(mutant, metadata).run(ports, "ZERO")
    need(got["status"] == "ALLOC_9" and ports[8].cells[1] == "0" and ports[9].cells[1] == "_",
         "returning wrong-owner fault present")
    need(got["status"] != f"ALLOC_{8}" and all(t.head == (1 if i <= 64 else 0) for i, t in enumerate(ports)),
         "owner oracle catches a fully returned semantic fault")
    results.append("returning_wrong_owner")
    return results


def main():
    code, metadata = lifecycle.compile_program()
    need(set(row[0] for row in code) == {"R", "W", "M", "J", "H"}, "literal graph alphabet")
    result = {"status": "PASS_LITERAL_CRT_WORD_LIFECYCLE", "graph_sha256": lifecycle.digest(code),
              "source_binding": source_check.check(),
              "locations": len(code), "logical_locations": metadata["logical_locations"],
              "primitive": primitive_checks(code, metadata), "chronology": chronology_checks(code, metadata),
              "actual_source": source_checks(code, metadata), "controls": rejection_controls(code, metadata),
              "scope": "Local lifecycle substitution. Retained raw arithmetic/higher controller in source replay. No new kappa."}
    if "--record" not in sys.argv:
        expected = json.loads((HERE / "RESULT.json").read_text())
        need(result == expected, "complete typed receipt differs from RESULT.json")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
