"""Source-bound finite tape replay and independently interpreted event ledger.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Observer decoding and predecessor oracle arithmetic are outside the runtime.
"""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path, data):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


def sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    authenticated = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256 drift")
        need(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
             == row["git_blob"], "source blob drift")
        authenticated[row["path"]] = data
    vendor = json.loads((PACKAGE / "VENDOR.json").read_text())
    data = (PACKAGE / vendor["path"]).read_bytes()
    need(hashlib.sha256(data).hexdigest() == vendor["sha256"], "retained caller drift")
    return authenticated, data


def bits(value, width):
    return tuple((value >> bit) & 1 for bit in range(width))


def integer(values):
    return sum(value << bit for bit, value in enumerate(values))


def state(values):
    return values[0], values[1], integer(reversed(values[2:17]))


def audit(machine, initial):
    """Reconstruct all tapes from unit events without using Tape methods."""
    cells = {key: list(value) for key, value in initial.items()}
    heads = dict.fromkeys(cells, 0)
    counts, phases = Counter(), Counter()
    for phase, name, op, position, value in machine.events:
        need(position == heads[name], "event head continuity")
        need(0 <= position < len(cells[name]), "event bounds")
        if op == "M":
            need(value in (-1, 1), "unit head move")
            heads[name] += value
            need(0 <= heads[name] < len(cells[name]), "moved head bounds")
        elif op == "R":
            need(value == cells[name][position], "event read content")
        elif op == "W":
            need(name not in ("input", "rom") and value in (0, 1), "event ownership")
            cells[name][position] = value
        else:
            raise ValueError("unknown event")
        counts[op] += 1
        phases[phase] += 1
    for tape in machine.tapes:
        need(cells[tape.name] == tape.cells and heads[tape.name] == tape.head,
             "independent event final state")
        need(tape.head == 0, "head restoration")
    need(cells["input"] == list(initial["input"]), "borrowed input unchanged")
    need(cells["rom"] == list(initial["rom"]), "borrowed ROM unchanged")
    need(not any(cells["work"]) and not any(cells["scratch"]), "private erasure")
    need(machine.query_count == 3, "exact three query epochs")
    encoded = json.dumps(machine.events, separators=(",", ":")).encode()
    return dict(actions=len(machine.events), operations=dict(sorted(counts.items())),
                phases=dict(sorted(phases.items())), trace_sha256=hashlib.sha256(encoded).hexdigest())


def fixtures():
    data, retained = sources()
    paths = ("research/unconditional-batched-crt/check_batched_crt.py",
             "research/crt-reservoir-placement/allocator.py",
             "research/crt-arbitrary-source-repair/verify.py")
    modules = [load("key_reference_%d" % n, ROOT / path, data[path])
               for n, path in enumerate(paths)]
    caller = load("key_retained_caller", PACKAGE / "vendor/pr4716-caller.py", retained)
    root = caller.RootCaller(*modules)
    word = root.word(6)
    need(root.fixed.prefixes == (1, 11) and root.fixed.product == 143
         and root.fixed.target_inverse == 5 and word.targets == (9,), "fixed caller scope")
    weights = tuple(p * c * a % 143 for m, p, c, a in root.fixed.terms)
    need(weights == (78, 11), "exact cached CRT weights")
    # Compile physical coordinates from the pinned placement, not from witnesses.
    coordinates = []
    for axis, width in enumerate(root.widths[:3]):
        positions = []
        for bit in range(width):
            candidates = [ybit for ybit in range(15)
                          if root.coordinates(1 << ybit)[axis] == 1 << bit]
            need(len(candidates) == 1, "unique transported descriptor")
            positions.append(candidates[0])
        coordinates.append(tuple(positions))
    rom = tuple(value for offset in range(17) for value in root.network(offset)[6][1])
    need(len(rom) == 544, "complete readonly row ROM")
    engine = load("key_engine", PACKAGE / "engine.py", (PACKAGE / "engine.py").read_bytes())
    return root, word, rom, tuple(coordinates), engine


def run_case(root, word, rom, coordinates, engine, value, back, mode="correct"):
    address = (value[0], value[1], *reversed(bits(value[2], 15)), back)
    machine = engine.KeyMachine(address, rom, coordinates, mode)
    initial = {tape.name: tuple(tape.cells) for tape in machine.tapes}
    output = machine.run()
    trace = []
    source = root.source(6, trace)
    origin = word.run(value, source, inverse=True)
    expected = word.ideal(origin, source)
    need(state(output) == expected and output[17] == back, "literal key equality")
    epochs = []
    for snapshot, oracle in zip(machine.snapshots, trace):
        active, scratch, answer = snapshot
        actual = dict(current_y=integer(reversed(active[2:17])),
                      coordinates=[integer(scratch[0:4]), integer(scratch[4:8]),
                                   integer(scratch[8:13])],
                      offset=integer(scratch[46:52]), bit=answer)
        need(actual["current_y"] == oracle["current_y"]
             and tuple(actual["coordinates"]) == oracle["coordinates"]
             and actual["offset"] == oracle["offset"] and answer == oracle["bit"],
             "current-state query trace")
        epochs.append(actual)
    invoice = audit(machine, initial)
    return dict(input=list(value), back=back, key=list(expected), epochs=epochs, **invoice)


def verify():
    root, word, rom, coordinates, engine = fixtures()
    # Known discriminators, invalid/padded fields, wrap boundaries and mixed high bits.
    ys = (4, 6, 0, 511, 512, 1023, 1024, 16383, 16384, 30724, 31236, 32767)
    cases = [run_case(root, word, rom, coordinates, engine, (u, t, y), (u ^ t))
             for y in ys for u, t in ((0, 1), (1, 1))]
    need([x["current_y"] for x in cases[0]["epochs"]] == [4, 31236, 31236], "first witness")
    need([x["current_y"] for x in cases[1]["epochs"]] == [4, 4, 31236], "last-query witness")
    controls = []
    for mode, value in (("stale_second", (0, 1, 4)), ("stale_third", (1, 1, 4)),
                        ("drop_high", (0, 1, 4)), ("omit_clear", (0, 1, 4)),
                        ("omit_return", (0, 1, 4)), ("bad_weight", (0, 1, 4)),
                        ("invalid_left_enabled", (0, 1, 6))):
        try:
            run_case(root, word, rom, coordinates, engine, value, 0, mode)
        except ValueError as exc:
            controls.append({"mode": mode, "rejected_by": str(exc)})
        else:
            raise ValueError("undetected control: " + mode)
    wrong = (tuple(reversed(coordinates[0])), *coordinates[1:])
    try:
        run_case(root, word, rom, wrong, engine, (0, 1, 4), 0)
    except ValueError as exc:
        controls.append({"mode": "wrong_transport_descriptor", "rejected_by": str(exc)})
    else:
        raise ValueError("undetected descriptor control")
    # Event completeness: even a correct output does not certify a corrupted ledger.
    machine = engine.KeyMachine((0, 1, *reversed(bits(4, 15)), 0), rom, coordinates)
    initial = {tape.name: tuple(tape.cells) for tape in machine.tapes}
    machine.run()
    index = next(i for i, e in enumerate(machine.events) if e[2] == "M")
    machine.events.pop(index)
    try:
        audit(machine, initial)
    except ValueError as exc:
        controls.append({"mode": "missing_unit_move_event", "rejected_by": str(exc)})
    else:
        raise ValueError("undetected event ledger control")
    return dict(status="PASS_CRT_TRANSPORTED_KEY_TAPE", cases=cases, controls=controls,
                coordinate_y_bits=coordinates, rom_bits=544,
                rom_sha256=hashlib.sha256(bytes(rom)).hexdigest(),
                scope="Fixed finite tape-action census; setup and Boolean control time excluded")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = verify()
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(encoded)
    else:
        need((PACKAGE / "RESULT.json").read_text() == encoded, "frozen receipt equality")
    print(result["status"], len(result["cases"]), "cases", len(result["controls"]), "controls")


if __name__ == "__main__":
    main()
