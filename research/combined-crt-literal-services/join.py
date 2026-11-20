"""One fixed 70-role union of the pinned arithmetic and lifecycle graphs.

Only state offsets and a fixed injective role map change. Source control,
typed object checks, and supplied backing grants remain outside the graph.
Apache-2.0; prepared for Jerry Chen / @CubeJerry with OpenAI assistance.
"""
from collections import Counter
from contextlib import contextmanager
from hashlib import sha256, sha1
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROLE_MAP = (*range(64), 68, 69, 64, 65)
ARITHMETIC_HASH = "8911a498e8e36409ca3b48395e7d754f49b4e452c273db821756867cea95a045"
LIFECYCLE_HASH = "48863284a4af10cdbb4d16cbecba07dfbadabc57ee8d21f635181acc7e0d0d73"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, filename):
    module = types.ModuleType(name)
    module.__file__ = str(HERE / "inputs" / filename)
    sys.modules[name] = module
    exec(compile(Path(module.__file__).read_bytes(), module.__file__, "exec"), module.__dict__)
    return module


def authenticate():
    manifest = json.loads((HERE / "SOURCE-PINS.json").read_text())
    registered = json.loads((HERE / "SOURCES.json").read_text())
    aliases = {row["local_input"]: row for row in registered["files"] if "local_input" in row}
    need(set(aliases) == {row["path"] for row in manifest["files"]}, "registered source closure")
    for row in manifest["files"]:
        original = aliases[row["path"]]
        need(original["path"] == row["origin_path"]
             and all(original[k] == row[k] for k in ("pin", "git_blob", "sha256")),
             "local input must equal its registered original source")
        data = (ROOT / row["path"]).read_bytes()
        need(sha256(data).hexdigest() == row["sha256"], "source SHA-256: " + row["path"])
        need(sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == row["git_blob"],
             "source Git blob: " + row["path"])
    return len(manifest["files"])


def digest(code):
    """Same canonical JSON as predecessors, streamed without a second huge string."""
    h = sha256()
    h.update(b"[")
    for i, row in enumerate(code):
        if i:
            h.update(b",")
        h.update(json.dumps(row, separators=(",", ":"), sort_keys=True).encode())
    h.update(b"]")
    return h.hexdigest()


def compile_union():
    authenticate()
    divider = load("joined_divider", "divider-divider.py")
    arithmetic = load("joined_arithmetic", "arithmetic.py")
    lifecycle = load("joined_lifecycle", "lifecycle-lifecycle.py")
    acode, labels, ameta = arithmetic.compile_arithmetic(divider)
    del labels
    lcode, lmeta = lifecycle.compile_program()
    need(len(acode) == 1304162 and digest(acode) == ARITHMETIC_HASH, "unchanged arithmetic graph")
    need(len(lcode) == 130936 and digest(lcode) == LIFECYCLE_HASH, "unchanged lifecycle graph")
    offset = len(acode)

    def relocate(row):
        op = row[0]
        if op == "R":
            return (op, ROLE_MAP[row[1]], {s: pc + offset for s, pc in row[2].items()})
        if op in ("W", "M"):
            return (op, ROLE_MAP[row[1]], row[2])
        if op == "J":
            return (op, row[1] + offset)
        need(op == "H", "literal opcode")
        return row

    code = acode + tuple(relocate(row) for row in lcode)
    entries = {"A:" + k: v for k, v in ameta["entries"].items()}
    entries.update({"L:" + k: offset + v for k, v in lmeta["entries"].items()})
    entries.update({"A:SET_" + str(role) + "_" + str(slot): pc
                    for role, row in enumerate(ameta["setters"]) for slot, pc in enumerate(row)})
    entries.update({"L:SET_" + str(slot): offset + pc for slot, pc in enumerate(lmeta["setters"])})
    meta = {
        "roles": 70, "locations": len(code), "arithmetic_locations": offset,
        "lifecycle_locations": len(lcode), "lifecycle_role_map": list(ROLE_MAP),
        "entries": entries, "entry_names": {pc: name for name, pc in entries.items()},
        "arithmetic_logical_pcs": ameta["logical_to_physical"],
        "arithmetic_setters": ameta["setters"],
        "lifecycle_metadata": dict(lmeta, entries={k: offset + v for k, v in lmeta["entries"].items()},
                                   setters=[offset + pc for pc in lmeta["setters"]]),
    }
    need(len(code) == 1435098, "exact disjoint state union")
    return code, meta


class Program:
    """Replay instrumentation is separate from the fixed R/W/M/J/H graph."""
    def __init__(self, code, metadata, observer=None):
        self.code, self.metadata, self.observer = code, metadata, observer
        self.logical_pcs = set(metadata["arithmetic_logical_pcs"])
        self.instructions = self.arena_actions = self.calls = 0
        self.entries, self.entry_instructions = Counter(), Counter()
        self.history = [None] * 70
        self.receipts = []

    def run(self, ports, entry, limit=20000000):
        need(len(ports) == 70 and len({id(t.cells) for t in ports}) == 70,
             "70 distinct actual physical owners")
        pc = self.metadata["entries"][entry] if isinstance(entry, str) else entry
        name = self.metadata["entry_names"].get(pc, "PC_" + str(pc))
        token = self.observer.before(ports, name) if self.observer else None
        count = logical = 0
        numeric = {"R": 0, "W": 0, "M": 0}
        writes = [0] * 70
        touched = [[t.head, t.head] for t in ports]
        initial_capacities = tuple(len(t.cells) for t in ports)
        arena = 0
        while True:
            row = self.code[pc]
            op = row[0]
            count += 1
            logical += pc in self.logical_pcs
            need(count <= limit, "bounded replay watchdog")
            if op in ("R", "W", "M"):
                role = row[1]
                port = ports[role]
                if role < 64:
                    numeric[op] += 1
                arena += role < 64 or role == 68
            if op == "R":
                symbol = port.read()
                need(symbol in row[2], "symbol outside this entry's admitted alphabet")
                pc = row[2][symbol]
            elif op == "W":
                port.write(row[2])
                writes[role] += 1
                pc += 1
            elif op == "M":
                port.step(row[2])
                need(0 <= port.head < len(port.cells), "supplied physical window")
                touched[role][0] = min(touched[role][0], port.head)
                touched[role][1] = max(touched[role][1], port.head)
                pc += 1
            elif op == "J":
                pc = row[1]
            elif op == "H":
                result = {"entry": name, "status": row[1], "instructions": count,
                          "arithmetic_logical_instructions": logical,
                          "numeric_actions": numeric, "arena_actions": arena,
                          "writes": writes, "history": touched}
                need(tuple(len(t.cells) for t in ports) == initial_capacities, "no implicit grant or refund")
                self.instructions += count
                self.arena_actions += arena
                self.calls += 1
                self.entries[name] += 1
                self.entry_instructions[name] += count
                for i, interval in enumerate(touched):
                    previous = self.history[i]
                    self.history[i] = interval if previous is None else [
                        min(previous[0], interval[0]), max(previous[1], interval[1])]
                if self.observer:
                    self.observer.after(ports, name, token, result)
                self.receipts.append({k: v for k, v in result.items() if k not in ("writes", "history")})
                return result
            else:
                raise ValueError("nonliteral opcode")


class LifecycleView:
    """The unchanged lifecycle Owner sees its original ABI on the fixed union."""
    def __init__(self, machine, ports):
        self.machine, self.ports = machine, ports
        self.metadata = machine.metadata["lifecycle_metadata"]

    def run(self, supplied, entry):
        need(len(supplied) == 68, "lifecycle ABI")
        for local, physical in enumerate(ROLE_MAP):
            need(supplied[local].cells is self.ports[physical].cells
                 and supplied[local].head == self.ports[physical].head, "fixed lifecycle role binding")
        pc = self.metadata["entries"][entry] if isinstance(entry, str) else entry
        return self.machine.run(self.ports, pc)


class BoundEntry:
    def __init__(self, arena, machine):
        hardware = load("hardware", "lifecycle-hardware.py")
        owner_module = load("joined_lifecycle_owner", "lifecycle-source_binding.py")
        selectors = tuple(hardware.Tape(["_"] * 8) for _ in range(4))
        stack = hardware.Tape(["_"] * 338)
        self.ports = tuple(hardware.WordPort(w) for w in arena.words) + selectors + (
            hardware.WordPort(arena.template), stack)
        self.arena, self.machine = arena, machine
        need(machine.run(self.ports, "A:ACQUIRE")["status"] == "READY", "arithmetic selector acquisition")
        self.owner = owner_module.Owner(arena, LifecycleView(machine, self.ports), stack,
                                        selectors[0], selectors[1])
        self.arithmetic_calls = []

    def primitive(self, raw, left, right, kind):
        need(raw.arena is self.arena, "one bound eager Entry")
        count = 0 if kind == "COMPARE" else 2 if kind == "DIVIDE" else 1
        before = self.machine.instructions
        outputs = self.owner.reserve(self.arena, left, right, count)
        if count == 0:
            slots = (left.slot, right.slot, left.slot, right.slot)
        elif count == 1:
            slots = (left.slot, right.slot, outputs[0].slot, outputs[0].slot)
        else:
            slots = (left.slot, right.slot, outputs[0].slot, outputs[1].slot)
        for role, slot in enumerate(slots):
            pc = self.machine.metadata["arithmetic_setters"][role][slot]
            need(self.machine.run(self.ports, pc)["status"] == "BOUND", "arithmetic setter")
        got = self.machine.run(self.ports, "A:" + kind)
        self.arithmetic_calls.append({"kind": kind, "slots": list(slots),
                                      "complete_instructions": self.machine.instructions - before,
                                      "body_instructions": got["instructions"], "status": got["status"]})
        if kind == "DIVIDE":
            need(got["status"] == "DONE", "division accepted")
            return outputs
        tags = {"COMPARE": {"CMP_NEG": -1, "CMP_EQ": 0, "CMP_POS": 1},
                "ADD": {"ADD_C0": 0, "ADD_C1": 1},
                "SUBTRACT": {"SUB_B0": 0, "SUB_B1": 1}}[kind]
        need(got["status"] in tags, "simple arithmetic accepted")
        flag = tags[got["status"]]
        return flag if count == 0 else (outputs[0], flag)

    @contextmanager
    def install(self, words):
        names = {"compare": "COMPARE", "add": "ADD", "subtract": "SUBTRACT", "divmod": "DIVIDE"}
        previous = {name: getattr(words.Unsigned, name) for name in names}
        for name, kind in names.items():
            def run(raw, left, right, kind=kind):
                return self.primitive(raw, left, right, kind)
            setattr(words.Unsigned, name, run)
        try:
            yield
        finally:
            for name, old in previous.items():
                setattr(words.Unsigned, name, old)

    def close(self):
        self.owner.close()
        need(all(t.head == 0 and set(t.cells) <= {"_"} for t in self.ports[64:68]),
             "all four selectors retired")
        need(self.ports[69].head == 0 and set(self.ports[69].cells) <= {"_"},
             "stack retired")


@contextmanager
def forbid_old(words):
    """Old providers are saved only for restoration, never used by the wrappers."""
    changes = [(words.Arena, name) for name in ("zero", "copy", "free")]
    changes += [(words.Word, "erase")]
    changes += [(words.Unsigned, name) for name in ("compare", "add", "subtract", "divmod", "shift_add_bit")]
    previous = [(cls, name, getattr(cls, name)) for cls, name in changes]
    counter = {"calls": 0}

    def unavailable(*args, **kwargs):
        counter["calls"] += 1
        raise ValueError("OLD_ARITHMETIC_OR_LIFECYCLE_UNAVAILABLE")

    for cls, name, _ in previous:
        setattr(cls, name, unavailable)
    try:
        yield counter
    finally:
        for cls, name, method in previous:
            setattr(cls, name, method)

