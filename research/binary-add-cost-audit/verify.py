#!/usr/bin/env python3
"""Exact source-bound accounting for PR2449's binary counted ADD.

Independent audit for ywz65 with substantial OpenAI Codex assistance.
Apache-2.0. Imported runtime bytes retain Jose Manuel's NOTICE.
"""
import argparse
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
KEYS = ("reads", "writes", "moves")


def need(ok, why):
    if not ok:
        raise ValueError(why)


def unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def read(path):
    return json.loads(path.read_text(encoding="utf8"), object_pairs_hook=unique)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def authenticate():
    sources = read(HERE / "SOURCES.json")["pending_sources"]
    need(len(sources) == 1 and sources[0]["head"] ==
         "ef4640fbf9c360ef66dbc5d29916e741d515bf39", "reviewed source head")
    files = sources[0]["files"]
    need({p["path"] for p in files} == {"source/"+name for name in
         ("words.py", "records.py", "stream.py", "PROOF.md", "README.md", "NOTICE.md")},
         "source inventory")
    for pin in files:
        need(sha256((HERE / pin["path"]).read_bytes()).hexdigest() == pin["sha256"],
             "source hash " + pin["path"])
    sys.path.insert(0, str(HERE / "source"))
    return tuple(importlib.import_module(name) for name in ("words", "records", "stream"))


def bill(n, k):
    need(type(n) is type(k) is int and n >= 0 and k >= max(2, n.bit_length()), "counter domain")
    if not n:
        return (2*k+12, 3*k+5, 4*k+16)
    s = n.bit_count()
    return (7*n-2*s+2*k+11, 2*n-s+3*k+4, 6*n-2*s+4*k+14)


def actual(meter):
    return tuple(getattr(meter, key) for key in KEYS)


def plus(*rows):
    return tuple(sum(row[i] for row in rows) for i in range(3))


def scale(n, row):
    return tuple(n*x for x in row)


def empty_tape(tape):
    need(tape.head == 1 and tape.cells[0] == 2 and
         all(x == 4 for x in tape.cells[1:]), "erased local tape")


def audit_arena(arena, protected):
    need(arena.live == {word.slot for word in protected}, "owned register closure")
    for word in arena.words:
        need(word.head == 1, "restored numerical head")
        if word.slot not in arena.live:
            need(all(x == 4 for x in word.cells[1:]), "erased numerical scratch")


def countdowns(words, stream):
    digest, cases, decrements = sha256(), 0, 0
    for n in range(513):
        for k in (max(2, n.bit_length()+1), max(2, n.bit_length()+7)):
            arena = words.Arena(k, capacity=2)
            word = arena.input(n)
            original = bytes(word.cells)
            arena.meter = words.Meter()
            counter = stream.Counter(word)
            count = 0
            while not counter.finished:
                counter.decrement()
                count += 1
            need(count == n, "countdown endpoint")
            counter.close()
            empty_tape(counter.tape)
            need(actual(counter.tape.meter) == bill(n, k), "exact countdown lifecycle bill")
            need(actual(arena.meter) == (3*k+3, 0, 2*k+4), "counter encoded-input traffic")
            need(bytes(word.cells) == original and word.head == 1, "preserved counter input")
            digest.update(canonical([n, k, actual(counter.tape.meter)]).encode())
            arena.free(word)
            audit_arena(arena, ())
            cases += 1
            decrements += n
    return {"cases": cases, "decrements": decrements, "digest": digest.hexdigest()}


def stream_counter_bill(m, u, g, s, c):
    length = m.bit_length()+1
    ranges = plus(*(plus(bill((c*x) % m, length), bill(m-(c*x) % m, length)) for x in range(m)))
    return scale(2, plus(bill(u, u.bit_length()+1),
                        scale(u, bill(m, length)),
                        scale(u*m, bill(g, g.bit_length()+1)),
                        scale(u*g, ranges),
                        scale(u*m*m*g, bill(s, s.bit_length()+1))))


def expected(bits, m, u, g, s, c):
    out = []
    for prefix in range(u):
        for x in range(m):
            for gap in range(g):
                for y in range(m):
                    start = (((prefix*m+x)*g+gap)*m+(y-c*x) % m)*s
                    out.extend(bits[start:start+s])
    return out


def run_stream(words, records, stream, m, u, g, s, c, bits, changing=False):
    arena = words.Arena(m.bit_length()+1)
    modulus = arena.input(m)
    ring = words.Ring(modulus)
    extent_arenas = [words.Arena(x.bit_length()+1, capacity=2) for x in (u, g, s)]
    extents = tuple(a.input(x) for a, x in zip(extent_arenas, (u, g, s)))
    snapshots = tuple(bytes(w.cells) for w in (modulus, *extents))
    tapes = []
    def factory():
        tape = records.Tape()
        tapes.append(tape)
        return tape
    source = factory()
    for bit in bits:
        source.append(bit)
    source.rewind()
    source.meter = words.Meter()
    calls = []
    def coefficient():
        value = (c+len(calls)) % m if changing else c
        calls.append(value)
        return arena.literal(value)  # Fixture only: callback arithmetic billed separately.
    original_inspect = words.Word.inspect
    def forbidden(_word):
        raise ValueError("runtime decoded word")
    words.Word.inspect = forbidden
    try:
        out, traffic = stream.add_pass(source, ring, *extents, coefficient, factory)
    finally:
        words.Word.inspect = original_inspect
    observed = list(out.cells[1:])
    need(out.head == source.head == 1, "payload heads restored")
    need(list(source.cells[1:]) == bits, "preserved source payload")
    need(calls == ([c, (c+1) % m] if changing else [c, c]), "two complete-pass callback calls")
    for tape in tapes[1:3]:
        empty_tape(tape)
    need(snapshots == tuple(bytes(w.cells) for w in (modulus, *extents)), "preserved control inputs")
    counter_actual = tuple(traffic["counters"][key] for key in KEYS)
    if not changing:
        need(counter_actual == stream_counter_bill(m, u, g, s, c), "complete counter composition bill")
    payload_actual = plus(*(actual(tape.meter) for tape in tapes))
    volume = len(bits)
    need(payload_actual == (10*volume+13, 3*volume, 10*volume+16), "complete payload movement bill")
    need(sum(counter_actual) <= 696*volume, "uniform counter envelope")
    audit_arena(arena, (modulus, ring.one))
    ring.close()
    arena.free(modulus)
    audit_arena(arena, ())
    for a, w in zip(extent_arenas, extents):
        a.free(w)
        audit_arena(a, ())
    return observed, counter_actual, payload_actual


def payloads(words, records, stream):
    digest, cases, bit_visits = sha256(), 0, 0
    shapes = [(m, 1, 1, 1) for m in range(2, 6)] + [(3, 2, 1, 1), (3, 1, 2, 1), (3, 1, 1, 2)]
    for m, u, g, s in shapes:
        volume = u*m*g*m*s
        for c in range(m):
            for origin in range(volume):
                bits = [int(i == origin) for i in range(volume)]
                out, cb, pb = run_stream(words, records, stream, m, u, g, s, c, bits)
                need(out == expected(bits, m, u, g, s, c), "independent ADD endpoint")
                restored, _, _ = run_stream(words, records, stream, m, u, g, s, (-c) % m, out)
                need(restored == bits, "inverse bit restoration")
                digest.update(canonical([m, u, g, s, c, origin, out, cb, pb]).encode())
                cases += 1
                bit_visits += 2*volume
    return {"forward_inverse_basis_cases": cases, "bit_visits": bit_visits, "digest": digest.hexdigest()}


def controls(words, records, stream):
    out = []
    need(bill(1, 2) != (19, 10, 24), "terminal transition control")
    out.append("omitted n=1 transition correction changes exact bill")
    arena = words.Arena(4096, capacity=2)
    word = arena.input(1)
    c = stream.Counter(word)
    c.decrement()
    c.close()
    need(sum(actual(c.tape.meter)) > 696, "unbounded spectator padding violates volume-only bound")
    try:
        stream.positive_extent(word)
    except ValueError as exc:
        need("canonical" in str(exc), "canonical padding rejection")
    else:
        raise ValueError("padded spectator accepted")
    out.append("padded singleton breaks volume bound and is rejected by source")
    arena.free(word)
    bits = [int(i == 3) for i in range(9)]
    bad, _, _ = run_stream(words, records, stream, 3, 1, 1, 1, 1, bits, changing=True)
    need(bad != expected(bits, 3, 1, 1, 1, 1), "changed split/merge coefficient must corrupt endpoint")
    out.append("different split and merge coefficients corrupt payload")
    changed = expected(bits, 3, 1, 1, 1, 1)
    need(expected(changed, 3, 1, 1, 1, 1) != bits, "wrong inverse sign control")
    out.append("same-sign inverse fails")
    need(bill(0, 3) != (0, 0, 0), "zero-range setup is charged")
    out.append("zero target range still charges setup and closure")
    return out


def compute():
    words, records, stream = authenticate()
    return {"schema_version": 1, "source_head": "ef4640fbf9c360ef66dbc5d29916e741d515bf39",
            "countdowns": countdowns(words, stream), "payloads": payloads(words, records, stream),
            "controls": controls(words, records, stream),
            "limits": "fixed current prefix, deterministic restored coefficient callback; callback arithmetic billed conditionally; no residual or global caller"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = compute()
    if args.out:
        with args.out.open("x", encoding="utf8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        need(canonical(result) == canonical(read(HERE / "RESULT.json")), "receipt mismatch")
    print("PASS_BINARY_ADD_COST_AUDIT counter_cases=" + str(result["countdowns"]["cases"]) +
          " basis_cases=" + str(result["payloads"]["forward_inverse_basis_cases"]) + " no_new_kappa")


if __name__ == "__main__":
    main()
