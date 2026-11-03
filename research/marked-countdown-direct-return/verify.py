#!/usr/bin/env python3
"""Exact source-native Counter and complete sign-call comparison. Apache-2.0."""
import builtins
import hashlib
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parent
PIN = "f72e91cf10c4cd52be615c94a1dcfacbf4b3cf0ce0691f471408be712cb8eee6"
KEYS = ("reads", "writes", "moves")
ORDER = ("words", "records", "stream", "cardinality", "counts", "bitstream", "linear_sign")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def strict_load(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            need(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def bad(value):
        raise ValueError("nonfinite JSON " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad)


def authenticate(root=ROOT):
    raw = (root / "SOURCE-PINS.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PIN, "source manifest")
    manifest = strict_load(raw)
    sources = {}
    for item in manifest["files"]:
        path = root / item["path"]
        need(not path.is_symlink(), "source symlink")
        data = path.read_bytes()
        need(len(data) == item["bytes"], "source length")
        need(hashlib.sha256(data).hexdigest() == item["sha256"], "source digest")
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data)
        need(blob.hexdigest() == item["git_blob"], "source git blob")
        sources[path.name] = data
    need(len(sources) == 11, "source closure")
    return sources


def load_world(sources, changed):
    modules, tapes = {}, []
    def importer(name, globals=None, locals=None, fromlist=(), level=0):
        need(level == 0 and name in modules, "undeclared runtime import")
        return modules[name]
    def load(name, raw):
        module = types.ModuleType(name)
        module.__dict__["__builtins__"] = dict(vars(builtins), __import__=importer)
        module.__dict__["__file__"] = str(ROOT / "inputs" / (name + ".py"))
        exec(compile(raw, module.__dict__["__file__"], "exec"), module.__dict__)
        modules[name] = module
        return module
    for name in ORDER:
        load(name, sources[name + ".py"])
    old_init = modules["records"].Tape.__init__
    def tracked_init(tape):
        old_init(tape)
        tapes.append(tape)
    modules["records"].Tape.__init__ = tracked_init
    raw = (ROOT / "newcountdown.py").read_bytes() if changed else sources["6495-countdown.py"]
    replacement = load("replacement", raw)
    counter = modules["stream"].Counter
    for name in ("cardinality", "bitstream", "linear_sign"):
        need(modules[name].Counter is counter, "Counter alias identity")
    counter.decrement = replacement.decrement
    return modules, tapes


def meter(tape):
    return [getattr(tape.meter, key) for key in KEYS]


def difference(a, b):
    return [x - y for x, y in zip(a, b)]


def state(counter):
    return [list(counter.tape.cells), counter.tape.head, counter.finished]


def word(world, n, pad):
    need(type(n) is int and n >= 0 and type(pad) is int and pad >= 0, "fixture integer")
    tape = world["records"].Tape()
    for i in range(max(1, n.bit_length()) + pad):
        tape.append((n >> i) & 1)
    tape.append(3)
    tape.rewind()
    return tape


def counter_case(old_world, new_world, n, pad):
    inputs = [word(world, n, pad) for world in (old_world, new_world)]
    protected = [(bytes(t.cells), t.head) for t in inputs]
    initial = [meter(t) for t in inputs]
    counters = [world["stream"].Counter(t) for world, t in zip((old_world, new_world), inputs)]
    need(state(counters[0]) == state(counters[1]), "constructor state")
    digest = hashlib.sha256()
    for x in range(n, 0, -1):
        before = [meter(c.tape) for c in counters]
        for c in counters:
            c.decrement()
        need(state(counters[0]) == state(counters[1]), "literal decrement state")
        for t, expected in zip(inputs, protected):
            need((bytes(t.cells), t.head) == expected, "protected input")
        delta = difference(difference(meter(counters[0].tape), before[0]),
                           difference(meter(counters[1].tape), before[1]))
        expected = [3, 3, 6] if x == 1 else [2, 0, 2] if x & 1 else [0, 0, 0]
        need(delta == expected, "one-step traffic")
        digest.update((json.dumps(state(counters[0]), separators=(",", ":")) + "\n").encode())
    before_close = state(counters[0])
    for c in counters:
        c.close()
    need(state(counters[0]) == state(counters[1]), "closed literal state")
    need(counters[0].tape.head == 1 and all(x == 4 for x in counters[0].tape.cells[1:]),
         "closed private blank")
    totals = [[a + b for a, b in zip(meter(c.tape), difference(meter(t), start))]
              for c, t, start in zip(counters, inputs, initial)]
    savings = difference(totals[0], totals[1])
    c = (n + 1) // 2
    need(savings == ([2*c+1, 3, 2*c+4] if n else [0, 0, 0]), "complete countdown traffic")
    return {"N": n, "padding": pad, "old": totals[0], "new": totals[1],
            "savings": savings, "state_sha256": digest.hexdigest(),
            "finished_state": before_close, "closed_state": state(counters[0])}


def counter_domains():
    return list(range(258)) + [511, 512, 513, 1023, 1024, 1025,
                               2047, 2048, 2049, 4095, 4096, 4097]


def rejects(function, *args):
    try:
        function(*args)
    except ValueError:
        return True
    raise ValueError("negative control accepted")


def controls(old_world, new_world):
    out = {}
    for label, world in (("old", old_world), ("new", new_world)):
        zero = world["stream"].Counter(word(world, 0, 4))
        out[label + "_finished"] = rejects(zero.decrement)
        invalid = world["stream"].Counter(word(world, 2, 0))
        invalid.tape.cells[2] = 3
        out[label + "_invalid_terminator"] = rejects(invalid.decrement)
    out["duplicate_json"] = rejects(strict_load, '{"a":1,"a":2}')
    out["nonfinite_json"] = rejects(strict_load, '{"a":NaN}')
    return out


def total_meter(tapes, arena):
    return [sum(getattr(t.meter, key) for t in tapes) + getattr(arena.meter, key)
            for key in KEYS]


def caller_run(world, tapes, m, b, s, pattern):
    arena = world["words"].Arena(max(2, m.bit_length() + 1))
    modulus = arena.input(m)
    ring = world["words"].Ring(modulus)
    base_b, base_s = world["counts"].Count.literal(b), world["counts"].Count.literal(s)
    before, suffix = base_b.marginal(), base_s.marginal()
    base_b.close()
    base_s.close()
    source = world["records"].Tape()
    payload = [(17*i + i//3 + pattern) & 1 for i in range(b*m*s)]
    for bit in payload:
        source.append(bit)
    source.rewind()
    protected = [(bytes(t.cells), t.head) for t in (source, before.tape, suffix.tape)]
    live = set(arena.live)
    origins, counters = {}, []
    tape_class, counter_class = world["records"].Tape, world["stream"].Counter
    old_append, old_init = tape_class.append, counter_class.__init__
    def observed_append(tape, symbol):
        origins.setdefault(id(tape), []).append(source.head - 1)
        old_append(tape, symbol)
    def observed_init(counter, value):
        old_init(counter, value)
        counters.append(counter)
    tape_class.append, counter_class.__init__ = observed_append, observed_init
    start = total_meter(tapes, arena)
    try:
        output = world["linear_sign"].sign_address(source, ring, 2, before, suffix)
    finally:
        tape_class.append, counter_class.__init__ = old_append, old_init
    bill = difference(total_meter(tapes, arena), start)
    expected = [(row*m + (-x) % m)*s + bit for row in range(b)
                for x in range(m) for bit in range(s)]
    need(origins[id(output)] == expected, "actual output source-coordinate map")
    need(list(output.cells[1:]) == [payload[i] for i in expected] and output.head == 1,
         "actual output payload/head")
    need([(bytes(t.cells), t.head) for t in (source, before.tape, suffix.tape)] == protected,
         "caller protected source/extents")
    need(set(arena.live) == live, "numerical temporary ownership return")
    for counter in counters:
        need(counter.finished and counter.tape.head == 1 and
             all(x == 4 for x in counter.tape.cells[1:]), "caller private counter blank")
    digest = hashlib.sha256(json.dumps(expected, separators=(",", ":")).encode()).hexdigest()
    return {"bill": bill, "source_coordinates_sha256": digest,
            "payload_sha256": hashlib.sha256(bytes(output.cells[1:])).hexdigest(),
            "counter_allocations": len(counters), "volume": len(payload)}


def caller_case(old_world, old_tapes, new_world, new_tapes, m, b, s, pattern):
    old = caller_run(old_world, old_tapes, m, b, s, pattern)
    new = caller_run(new_world, new_tapes, m, b, s, pattern)
    for key in ("source_coordinates_sha256", "payload_sha256", "counter_allocations", "volume"):
        need(old[key] == new[key], "caller observed state " + key)
    k = b * (4*(m-2) + m*int(s > 1))
    positive = 1 + b + 2*b*int(m > 2) + k
    odd = (b+1)//2 + 2*b*((m-1)//2) + b*(m//2) + k*((s+1)//2)
    expected = [2*odd+positive, 3*positive, 2*odd+4*positive]
    savings = difference(old["bill"], new["bill"])
    need(savings == expected, "complete caller traffic delta")
    return {"M": m, "B": b, "S": s, "pattern": pattern, "old": old,
            "new": new, "savings": savings, "positive_countdowns": positive,
            "odd_value_visits": odd}


def receipt(smoke=False, caller_first=False):
    sources = authenticate()
    old_world, old_tapes = load_world(sources, False)
    new_world, new_tapes = load_world(sources, True)
    pairs = [(1, 0), (1, 4), (17, 4)] if smoke or caller_first else [
        (n, pad) for n in counter_domains() for pad in (0, 1, 4)]
    cases = [counter_case(old_world, new_world, n, pad) for n, pad in pairs]
    shapes = [(2, 1, 1, 0)] if caller_first else [
        (m, b, s, pattern) for m in (2, 3, 4, 5, 8, 9) for b in (1, 2, 3)
        for s in (1, 2, 3, 4, 7, 8, 9) for pattern in (0, 1)]
    callers = [] if smoke else [caller_case(old_world, old_tapes, new_world, new_tapes, *shape)
                                for shape in shapes]
    return {"schema_version": 1, "source_manifest_sha256": PIN,
            "scope": "first-falsification" if smoke else "caller-boundary" if caller_first else "complete-caller",
            "counter_cases": cases, "caller_cases": callers,
            "controls": controls(old_world, new_world)}


def compare(actual, expected):
    need(type(actual) is type(expected), "receipt type")
    if type(expected) is dict:
        need(actual.keys() == expected.keys(), "receipt keys")
        for key in expected:
            compare(actual[key], expected[key])
    elif type(expected) is list:
        need(len(actual) == len(expected), "receipt list length")
        for a, b in zip(actual, expected):
            compare(a, b)
    else:
        need(actual == expected, "receipt value")


def main():
    need(sys.argv[1:] in ([], ["--emit"], ["--first-only"], ["--caller-first"]), "unsupported argument")
    result = receipt(sys.argv[1:] == ["--first-only"], sys.argv[1:] == ["--caller-first"])
    if sys.argv[1:]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        compare(strict_load((ROOT / "RESULT.json").read_bytes()), result)
        print("PASS_MARKED_COUNTDOWN_DIRECT_RETURN")


if __name__ == "__main__":
    main()
