"""Independent source comparison and adversarial terminal-service checks."""
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from types import ModuleType, SimpleNamespace
import json
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from terminal import Port, compile_terminal, digest, execute, need, relocate

SOURCE = HERE / "inputs/frozen/research/combined-crt-literal-services"


def sources():
    import integration
    integration.authenticate()
    manifest = json.loads((SOURCE / "SOURCE-PINS.json").read_text())
    rows = {Path(row["path"]).name: row for row in manifest["files"]}
    loaded, receipts = [], []
    for name, filename in (("words", "old-words.py"), ("records", "old-records.py"),
                           ("entry", "old-entry.py"), ("producer", "old-producer.py")):
        path = SOURCE / "inputs" / filename
        data = path.read_bytes()
        need(sha256(data).hexdigest() == rows[filename]["sha256"], "exact source bytes")
        module = ModuleType(name)
        module.__file__ = str(path)
        sys.modules[name] = module
        exec(compile(data, str(path), "exec"), module.__dict__)
        loaded.append(module)
        receipts.append({"file": filename, "sha256": sha256(data).hexdigest(),
                         "pin": rows[filename]["pin"]})
    return (*loaded, receipts)


def fixture(w, r, e, p, lengths=(0, 0, 0), rotation=0, frozen_shape=False):
    guide = e.Port(w)
    for _ in range(p):
        guide.append(w.ONE)
    guide.rewind()
    guards = tuple(e.Port(w) for _ in range(8))
    for i, guard in enumerate(guards):
        guard.cells.extend((r.RETURN, i % 2, w.BLANK, w.ONE))
        if not frozen_shape:
            guard.cells.append(w.BLANK)
            guard.head = 1 + (i % 3)
    entry = e.Entry(w, r, guide, guards)
    for i, word in enumerate(entry.arena.words[8:]):
        extra = 5*i + i % 3 if frozen_shape else 3*i + (p+i) % 7
        word.cells.extend([w.BLANK] * extra)
    entry.arena.template.cells.extend([w.BLANK] * (41 if frozen_shape else p % 11 + 37))
    alphabet = (0, 1, 3, *range(5, 14))
    for i, (record, n) in enumerate(zip((entry.left, entry.right, entry.output), lengths)):
        record.cells.extend([alphabet[j % len(alphabet)] for j in range(n)])
        if not frozen_shape:
            record.cells.extend([w.BLANK] * (1 + 13*i + p % 9))
    order = list(reversed(range(8, 64)))
    rotation %= len(order)
    order = order[rotation:] + order[:rotation]
    entry.arena.available[:] = order
    return entry, guide, guards


def bind(entry, order=None, frozen_shape=False):
    if order is None:
        order = list(entry.arena.available)  # fixture construction only
    selectors = [SimpleNamespace(cells=["_"]*(8 if frozen_shape else 8+2*i), head=0) for i in range(4)]
    cells = ["L", *(str((slot >> j) & 1) for slot in order for j in range(6)), "R"]
    cells.extend(["_"] * (338 + (0 if frozen_shape else 23) - len(cells)))
    stack = SimpleNamespace(cells=cells, head=0)
    raw = [word.port for word in entry.arena.words] + selectors + [entry.arena.template.port, stack,
                                                               entry.left, entry.right, entry.output]
    return tuple(Port(t, byte_symbols=(i < 64 or i == 68 or i >= 70)) for i, t in enumerate(raw))


def snapshot(ports):
    return [(id(t.cells), tuple(t.cells), t.head) for t in ports]


def complete(ports, old):
    need([id(t.cells) for t in ports] == [row[0] for row in old], "same physical owners")
    need([len(t.cells) for t in ports] == [len(row[1]) for row in old], "retained history costs")
    need(snapshot(ports[:8]) == old[:8], "dirty protected owners preserved")
    for i, tape in enumerate(ports[8:], 8):
        blank = "_" if i in (*range(64, 68), 69) else 4
        need(all(cell == blank for cell in tape.cells), "all admitted owned histories blank")
        need(tape.head == (0 if i in (*range(64, 68), 69) else 1), "terminal head restoration")


def meter_total(entry, guide, guards):
    objects = [guide, *guards, *entry.owned]
    meters = {id(t.meter): t.meter for t in objects}
    meters[id(entry.arena.meter)] = entry.arena.meter
    return sum(m.reads + m.writes + m.moves for m in meters.values())


@contextmanager
def seal(w, e, entry):
    changes = [(w.Word, name) for name in ("read", "write", "step", "rewind", "erase", "zero", "msb", "inspect")]
    changes += [(w.Arena, name) for name in ("zero", "copy", "free", "literal")]
    changes += [(e.Entry, "close")]
    changes += [(e.Port, name) for name in ("read", "write", "step", "rewind", "clear", "retire")]
    old = [(cls, name, getattr(cls, name)) for cls, name in changes]
    counter = {"calls": 0}

    def unavailable(*args, **kwargs):
        counter["calls"] += 1
        raise ValueError("NO_RAW_WORD_PORT_ENTRY_OR_HOST_LIVE_SERVICE")

    parent = type(entry.arena)

    class SealedArena(parent):
        @property
        def live(self):
            return unavailable()

        @property
        def available(self):
            return unavailable()

    entry.arena.__class__ = SealedArena
    for cls, name, _ in old:
        setattr(cls, name, unavailable)
    try:
        yield counter
    finally:
        for cls, name, value in old:
            setattr(cls, name, value)
        entry.arena.__class__ = parent


def positive(code, meta, w, r, e, p, lengths, rotation):
    entry, guide, guards = fixture(w, r, e, p, lengths, rotation)
    ports = bind(entry)
    old = snapshot(ports)
    guide_before = (tuple(guide.cells), guide.head)
    with seal(w, e, entry) as counter:
        got = execute(code, meta, ports)
        need(got["status"] == "CLOSED" and counter["calls"] == 0, "literal terminal return")
        entry.closed = True  # fixed finite halt flag; no decoded scientific state
    complete(ports, old)
    need((tuple(guide.cells), guide.head) == guide_before, "guide untouched")
    expected = 7*p + 7*sum(lengths) + 2928
    need(got["instructions"] == expected, "all-width complete path price")
    phases = {"TERMINAL": 1100, "NUMERICAL_MARKERS": 392, "TEMPLATE": 7*p+11,
              **{"record_"+str(70+i): 7*n+10 for i, n in enumerate(lengths)},
              "METADATA_CLOSE": 1395}
    need(got["phases"] == phases, "independent segment prices")
    source, sg, sd = fixture(w, r, e, p, lengths, rotation)
    before = meter_total(source, sg, sd)
    source.close()
    native = meter_total(source, sg, sd)-before
    need(native == 5*p + 5*sum(lengths) + 433, "exact original Entry.close native actions")
    need(entry.closed == source.closed and
         [tuple(t.cells) for t in entry.owned] == [tuple(t.cells) for t in source.owned] and
         [t.head for t in entry.owned] == [t.head for t in source.owned], "exact source retirement observables")
    need(execute(code, meta, ports)["status"] == "REJECTED", "second closure rejected")
    return {"p": p, "record_lengths": list(lengths), "stack_rotation": rotation,
            "original_native_actions": native, "literal": got, "sealed_fallback_calls": counter["calls"]}


def canonical(r, w, pairs):
    tape = r.Tape()
    for pair in pairs:
        tape.append(r.ROOT)
        for value in pair:
            for j in range(max(1, value.bit_length())):
                tape.append((value >> j) & 1)
            tape.append(r.WORD_END)
        tape.append(r.RECORD_END)
    tape.append(w.RIGHT)
    tape.rewind()
    return tape


def exact_source_terminal(code, meta, w, r, e, producer):
    # The unchanged producer is fixture preparation, with its original providers.
    # This does not rerun or claim the frozen joined arithmetic invocation.
    entry, guide, guards = fixture(w, r, e, 7, frozen_shape=True)
    left, right = canonical(r, w, [(5, 1)]), canonical(r, w, [(7, 2)])
    result = entry.invoke(producer, left, right)
    entry.consume(result)
    ports = bind(entry, frozen_shape=True)
    old = snapshot(ports)
    borrowed = [(tuple(t.cells), t.head) for t in (guide, *guards, left, right)]
    need(len({id(t.cells) for t in (*ports, guide, left, right)}) == 76,
         "complete unchanged 76-owner physical source context")
    predecessor = json.loads((SOURCE / "RESULT.json").read_text())["source"]["physical_context_capacities"]
    # The frozen receipt orders guide/borrowed records before the three owned
    # records; this extension gives the latter their new fixed service roles.
    comparable = [len(t.cells) for t in (*ports[:70], guide, left, right, *ports[70:])]
    need(comparable == predecessor, "all 76 capacities equal the frozen source receipt")
    with seal(w, e, entry) as blocked:
        got = execute(code, meta, ports)
        need(got["status"] == "CLOSED" and blocked["calls"] == 0, "exact source terminal is wholly literal")
        entry.closed = True
    complete(ports, old)
    need(borrowed == [(tuple(t.cells), t.head) for t in (guide, *guards, left, right)], "all terminal borrowed owners unchanged")
    need(got["instructions"] == 2977, "exact source-terminal cost")
    return {"scope": "Original producer prepares fixture; only terminal interval is new literal execution.",
            "p": 7, "left": [[5, 1]], "right": [[7, 2]], "literal": got,
            "physical_context_roles": 76,
            "capacity_match_to_frozen_source_receipt": True,
            "context_capacities": [len(t.cells) for t in (*ports, guide, left, right)],
            "sealed_fallback_calls": blocked["calls"]}


def controls(code, meta, w, r, e):
    output = []
    def fresh(order=None):
        entry, _, _ = fixture(w, r, e, 7)
        return entry, bind(entry, order)
    entry, ports = fresh()
    before = snapshot(ports)
    ports[69].cells[:] = ["_"]*len(ports[69].cells)
    after_erasure = snapshot(ports)
    need(execute(code, meta, ports)["status"] == "REJECTED", "premature metadata close rejected")
    need(snapshot(ports) == after_erasure, "ordering rejection before numerical mutation")
    output.append("metadata retired first: rejected without a new write")
    entry, ports = fresh(list(reversed(range(9, 64))))
    before = snapshot(ports)
    need(execute(code, meta, ports)["status"] == "REJECTED", "live owned slot rejects terminal guard")
    need([tuple(t.cells) for t in ports] == [x[1] for x in before], "short stack rejection before writes")
    output.append("55-entry free stack: rejected before erasure")
    entry, ports = fresh()
    ports[69].cells[331:337] = ports[69].cells[1:7]
    need(execute(code, meta, ports)["status"] == "CLOSED", "duplicate-stack premise control")
    output.append("56 duplicate-containing records pass the count guard: inherited uniqueness is necessary")
    entry, ports = fresh()
    alias = (*ports[:72], ports[70])
    try:
        execute(code, meta, alias)
    except ValueError as exc:
        need(str(exc) == "distinct fixed physical owners", "physical alias guard")
    else:
        raise ValueError("record alias accepted")
    output.append("record backing alias rejected")
    entry, ports = fresh()
    with seal(w, e, entry) as blocked:
        try:
            entry.close()
        except ValueError:
            pass
        need(blocked["calls"] == 1, "sentinel actually called")
        try:
            entry.arena.live
        except ValueError:
            pass
        need(blocked["calls"] == 2, "host membership sentinel actually called")
    output.append("raw Entry.close and host membership sentinels active")
    for role in (9, 70):
        entry, ports = fresh()
        need(len(ports[role].cells)-1 > (8 if role < 64 else 1),
             "dirty control is strictly beyond the current numerical/record frame")
        ports[role].cells[-1] = 1
        old = snapshot(ports)
        need(execute(code, meta, ports)["status"] == "CLOSED", "dirty-tail control executes stated local path")
        try:
            complete(ports, old)
        except ValueError as exc:
            need(str(exc) == "all admitted owned histories blank", "dirty historical suffix counterexample")
        else:
            raise ValueError("dirty tail magically retired")
        output.append("dirty old tail on role " + str(role) + " survives: clean-history premise necessary")
    entry, ports = fresh()
    old = snapshot(ports)
    mutation = list(code)
    last = max(i for i, row in enumerate(code) if row == ("W", 70, "_"))
    mutation[last] = ("J", last+1)
    need(execute(tuple(mutation), meta, ports)["status"] == "CLOSED", "returning marker-erasure mutant")
    try:
        complete(ports, old)
    except ValueError:
        pass
    else:
        raise ValueError("missing record marker erasure escaped")
    output.append("returning missing-record-erasure mutation detected")
    code70, meta70 = compile_terminal(False)
    entry, ports = fresh()
    outside = snapshot(ports[70:])
    partial = execute(code70, meta70, ports[:70])
    need(partial["status"] == "NUMERICAL_CLOSED" and partial["instructions"] == 2947,
         "70-role addressable subset")
    need(snapshot(ports[70:]) == outside and all(t.cells[0] == 2 for t in ports[70:]), "70-role footprint obstruction witness")
    output.append("70-role service preserves all three unwanted record markers")
    return output, {"states": len(code70), "sha256": meta70["sha256"], "source_p7_cost": 2947}


def main():
    started = time.monotonic()
    w, r, e, producer, pinned = sources()
    code, meta = compile_terminal()
    need(all(row[0] in ("R", "W", "M", "J", "H") for row in code), "literal instruction set")
    need(all(0 <= row[1] < 73 for row in code if row[0] in ("R", "W", "M")), "fixed bounded tape operands")
    targets = [q for row in code for q in (row[2].values() if row[0] == "R" else [row[1]] if row[0] == "J" else [])]
    need(all(0 <= q < len(code) for q in targets), "all terminal branches stay in the appended segment")
    shifted = relocate(code, 1435098)
    for original, appended in zip(code, shifted):
        if original[0] == "R":
            need(appended[1] == original[1] and
                 {s:q-1435098 for s,q in appended[2].items()} == original[2], "exact branch relocation")
        elif original[0] == "J":
            need(appended[1]-1435098 == original[1], "exact jump relocation")
        else:
            need(appended == original, "unchanged literal role/action/flag")
    cases = [positive(code, meta, w, r, e, p, lengths, rotation)
             for p in (4, 5, 7, 19, 257)
             for lengths, rotation in (((0, 0, 0), 0), ((1, 2, 3), 7), ((13, 0, 19), 31), ((131, 6, 47), 55))]
    source = exact_source_terminal(code, meta, w, r, e, producer)
    negative, subset = controls(code, meta, w, r, e)
    out = {"status": "PASS_LITERAL_CRT_ENTRY_CLOSE", "terminal_graph": {k:v for k,v in meta.items() if k != "labels"},
           "frozen_union_states": 1435098, "extended_union_states": 1435098+len(code),
           "relocated_suffix_sha256": digest(shifted),
           "frozen_union_head": "7a6334dceef9d03fb5b1aeec4269a2911c0112b4",
           "sources": pinned, "cases": cases, "exact_source_terminal": source,
           "controls": negative, "seventy_role_subset": subset}
    if "--record" not in sys.argv:
        need(json.loads(json.dumps(out)) == json.loads((HERE / "TERMINAL-RESULT.json").read_text()), "deterministic receipt")
    print(json.dumps(out, sort_keys=True, indent=2))
    print(json.dumps({"seconds": round(time.monotonic()-started, 3),
                      "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}), file=sys.stderr)


if __name__ == "__main__":
    main()
