"""One fixed 73-role execution of the frozen prefix and literal terminal.

Apache-2.0. Prepared for Jerry Chen / CubeJerry with OpenAI assistance.
"""
from collections import Counter
from contextlib import contextmanager
from hashlib import sha256, sha1
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FROZEN = HERE / "inputs/frozen/research/combined-crt-literal-services"
sys.path.insert(0, str(HERE))
import terminal

need = terminal.need


def check_source_bytes(data, row):
    need(sha256(data).hexdigest() == row["sha256"], "pinned source SHA-256")
    need(sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest() == row["git_blob"], "pinned source Git blob")


def authenticate():
    manifest = json.loads((HERE / "SOURCE-PINS.json").read_text())
    registered = json.loads((HERE / "SOURCES.json").read_text())
    aliases = {r["local_input"]:r for r in registered["files"] if "local_input" in r}
    need(set(aliases) == {r["path"] for r in manifest["files"]}, "registered compact source closure")
    for row in manifest["files"]:
        need(aliases[row["path"]]["path"] == row["origin_path"] and
             all(aliases[row["path"]][k] == row[k] for k in ("pin","git_blob","sha256")),
             "registered exact original source")
        data = (ROOT / row["path"]).read_bytes()
        check_source_bytes(data,row)
    return len(manifest["files"])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def providers():
    authenticate()
    joined = load("join", FROZEN / "join.py")
    observed = load("frozen_verify", FROZEN / "verify.py")
    return joined, observed


def compile_all(joined):
    prefix, meta = joined.compile_union()
    need(joined.digest(prefix) == "31ce4975d2189002ad03f2279eabe34d99d97da6c5f5a40f9642734b3e9ec148", "unchanged public prefix")
    end, endmeta = terminal.compile_terminal()
    need(endmeta["sha256"] == "f060e7097028921bda8945724d0b9668cdc20e9d6552d65215a925ee5bd78914", "fixed terminal graph")
    offset = len(prefix)
    code = prefix + terminal.relocate(end, offset)
    meta = dict(meta, roles=73, locations=len(code), terminal_offset=offset, terminal_meta=endmeta)
    meta["entries"] = dict(meta["entries"], **{"T:CLOSE": offset})
    meta["entry_names"] = {pc:name for name,pc in meta["entries"].items()}
    need(len(code) == 1438047, "fixed complete graph size")
    return code, meta


class Tracker:
    def __init__(self, raw):
        self.raw = tuple(raw)
        need(len(raw) == 76 and len({id(t.cells) for t in raw}) == 76, "76 distinct persistent owners")
        self.roles = {id(t):i for i,t in enumerate(raw)}
        self.identities = [id(t.cells) for t in raw]
        self.capacities = [len(t.cells) for t in raw]
        self.intervals = [[t.head,t.head] for t in raw]
        self.actions = Counter()
        self.actions_by_role = [Counter() for _ in raw]
        self.calls = Counter()

    def touch(self, role, kind, op):
        tape = self.raw[role]
        need(id(tape.cells) == self.identities[role] and len(tape.cells) == self.capacities[role],
             "same supplied history at every primitive action")
        need(0 <= tape.head < len(tape.cells), "all source actions inside supplied history window")
        self.intervals[role][0] = min(self.intervals[role][0], tape.head)
        self.intervals[role][1] = max(self.intervals[role][1], tape.head)
        self.actions[kind+":"+op] += 1
        self.actions_by_role[role][kind+":"+op] += 1

    def invariant(self):
        need(self.identities == [id(t.cells) for t in self.raw], "persistent physical identity")
        need(self.capacities == [len(t.cells) for t in self.raw], "no implicit grant, replacement or history refund")


class Bridge(terminal.Port):
    def __init__(self, backing, tracker, role, meter=None, byte_symbols=True):
        super().__init__(backing, byte_symbols)
        self.tracker, self.role, self.meter = tracker, role, meter

    def tick(self, op):
        self.tracker.touch(self.role, "literal", op)
        if self.meter is not None:
            field = {"R":"reads", "W":"writes", "M":"moves"}[op]
            setattr(self.meter, field, getattr(self.meter, field)+1)

    def read(self):
        value = super().read()
        self.tick("R")
        return value

    def write(self, symbol):
        super().write(symbol)
        self.tick("W")

    def step(self, direction):
        super().move(direction)
        self.tick("M")


class Machine:
    def __init__(self, code, meta, audit):
        self.code, self.metadata, self.audit = code, meta, audit
        self.logical = set(meta["arithmetic_logical_pcs"])
        self.ports = None
        self.phase = "NEW"
        self.instructions = self.calls = self.arena_actions = self.record_actions = 0
        self.entries, self.entry_instructions = Counter(), Counter()
        self.receipts = []

    def bind(self, ports):
        need(self.phase == "NEW" and len(ports) == 73, "one fixed binding")
        need(len({id(t.cells) for t in ports}) == 73, "73 distinct service owners")
        self.ports, self.phase = ports, "BOUND"

    def run(self, ports, entry, limit=20000000):
        need(ports is self.ports, "no service role rebinding")
        pc = self.metadata["entries"][entry] if isinstance(entry,str) else entry
        name = self.metadata["entry_names"][pc]
        if self.phase == "BOUND":
            need(name == "A:ACQUIRE", "selectors acquired exactly once")
        elif self.phase == "SELECTORS_READY":
            need(name == "L:INIT", "lifecycle initialized exactly once")
        else:
            need(self.phase == "ACTIVE", "single live terminal phase")
            need(name not in ("A:ACQUIRE","L:INIT","A:RETIRE","L:CLOSE"),
                 "predecessor setup/retirement entry is private")
        terminal_call = name == "T:CLOSE"
        if terminal_call:
            self.phase = "CLOSING"
        before = self.audit.before(ports,name)
        steps = logical = arena = records = 0
        numeric = {"R":0,"W":0,"M":0}
        operations = Counter()
        while True:
            row = self.code[pc]
            op = row[0]
            steps += 1
            logical += pc in self.logical
            operations[op] += 1
            need(steps <= limit, "bounded replay watchdog")
            if op in ("R","W","M"):
                role, port = row[1], ports[row[1]]
                if role < 64:
                    numeric[op] += 1
                arena += role < 64 or role == 68
                records += role >= 70
            if op == "R":
                symbol = port.read()
                need(symbol in row[2], "admitted literal symbol")
                pc = row[2][symbol]
            elif op == "W":
                port.write(row[2]); pc += 1
            elif op == "M":
                port.step(row[2]); pc += 1
            elif op == "J":
                pc = row[1]
            elif op == "H":
                result = {"entry":name,"status":row[1],"instructions":steps,
                          "arithmetic_logical_instructions":logical,"numeric_actions":numeric,
                          "arena_actions":arena,"record_actions":records,"operations":dict(operations)}
                self.audit.after(ports,name,before,result)
                self.instructions += steps; self.calls += 1
                self.arena_actions += arena; self.record_actions += records
                self.entries[name] += 1; self.entry_instructions[name] += steps
                self.receipts.append(result)
                if terminal_call:
                    self.phase = "CLOSED" if row[1] == "CLOSED" else "FAILED"
                elif name == "A:ACQUIRE":
                    need(row[1] == "READY", "selector setup completed")
                    self.phase = "SELECTORS_READY"
                elif name == "L:INIT":
                    need(row[1] == "READY", "lifecycle setup completed")
                    self.phase = "ACTIVE"
                return result
            else:
                raise ValueError("nonliteral instruction")


class Audit:
    def __init__(self, old, p):
        self.old, self.p = old.Audit(p), p

    def before(self, ports, name):
        if name == "T:CLOSE":
            return [(id(t.cells),tuple(t.cells),t.head) for t in ports]
        return self.old.before(ports[:70],name), [(id(t.cells),tuple(t.cells),t.head) for t in ports[70:]]

    def after(self, ports, name, before, result):
        if name != "T:CLOSE":
            self.old.after(ports[:70],name,before[0],result)
            need(before[1] == [(id(t.cells),tuple(t.cells),t.head) for t in ports[70:]], "prefix leaves every bound record owner unchanged")
            return
        need(result["status"] == "CLOSED" and result["instructions"] == 7*self.p+2928, "exact consumed terminal result and price")
        need(len(self.old.free) == 56, "ghost terminal ownership agrees with physical guard")
        for role,tape in enumerate(ports):
            need(id(tape.cells) == before[role][0] and len(tape.cells) == len(before[role][1]), "terminal retains owner history")
            if role < 8:
                need((tuple(tape.cells),tape.head) == before[role][1:], "protected owner untouched")
            else:
                metadata = role in (*range(64,68),69)
                need(set(tape.cells) <= ({"_"} if metadata else {4}), "all owned historical cells blank")
                need(tape.head == (0 if metadata else 1), "terminal heads restored")


def bind_entry(joined, entry, machine, guide, left, right):
    hardware = joined.load("hardware", "lifecycle-hardware.py")
    owner_module = joined.load("joined_lifecycle_owner", "lifecycle-source_binding.py")
    selectors = tuple(hardware.Tape(["_"]*8) for _ in range(4))
    stack = hardware.Tape(["_"]*338)
    raw = (*[word.port for word in entry.arena.words], *selectors, entry.arena.template.port,
           stack, entry.left, entry.right, entry.output, guide, left, right)
    tracker = Tracker(raw)
    ports = tuple(Bridge(t,tracker,i,
                         entry.arena.meter if i < 64 or i == 68 else t.meter if i >= 70 else None,
                         byte_symbols=i < 64 or i == 68 or i >= 70) for i,t in enumerate(raw[:73]))
    machine.bind(ports)

    class Bound(joined.BoundEntry):
        def __init__(self):
            self.ports, self.arena, self.machine = ports, entry.arena, machine
            need(machine.run(ports,"A:ACQUIRE")["status"] == "READY", "selector grant")
            self.owner = owner_module.Owner(entry.arena,joined.LifecycleView(machine,ports),stack,selectors[0],selectors[1])
            self.arithmetic_calls = []

        def close(self):
            need(not entry.closed, "source finite live phase")
            need(machine.run(ports,"T:CLOSE")["status"] == "CLOSED", "literal Entry close")
            entry.closed = True

    return Bound(), tracker


@contextmanager
def retained_observation(w, r, e, tracker):
    changes = []
    for cls,kind in ((w.Word,"retained_word"),(e.Port,"retained_entry_port"),(r.Tape,"retained_borrowed_record")):
        for name,op in (("read","R"),("write","W"),("step","M")):
            original = getattr(cls,name)
            def wrapped(obj,*args,original=original,kind=kind,op=op,cls=cls):
                raw = obj.port if cls is w.Word else obj
                out = original(obj,*args)
                role = tracker.roles[id(raw)]
                exact_kind = ("retained_guide" if role == 73 else "retained_owned_record") if cls is e.Port else kind
                tracker.touch(role,exact_kind,op)
                return out
            changes.append((cls,name,original))
            setattr(cls,name,wrapped)
    files = {str(FROZEN/"inputs"/name):name for name in ("old-words.py","old-records.py","old-entry.py","old-producer.py")}
    def trace(frame,event,arg):
        filename = files.get(frame.f_code.co_filename)
        if filename is None or frame.f_code.co_name in ("cells","head"):
            return None
        key = filename+":"+frame.f_code.co_name
        if event == "call":
            tracker.calls[key] += 1
            frame.f_trace_lines = False
        return trace
    previous = sys.gettrace()
    sys.settrace(trace)
    try:
        yield
    finally:
        sys.settrace(previous)
        for cls,name,original in changes:
            setattr(cls,name,original)


@contextmanager
def block_close(e):
    old = e.Entry.close
    counter = {"calls":0}
    def forbidden(*args,**kwargs):
        counter["calls"] += 1
        raise ValueError("ORIGINAL_ENTRY_CLOSE_UNAVAILABLE")
    e.Entry.close = forbidden
    try:
        yield counter
    finally:
        e.Entry.close = old
