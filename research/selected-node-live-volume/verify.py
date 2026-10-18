#!/usr/bin/env python3
"""Literal complete-node data-content census on authenticated source exports."""
import argparse
from collections import Counter
from contextlib import contextmanager
import hashlib
import importlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
PINS = {
    "SNAPSHOTS.json": "59ae3e56eb51cc91dd36b24311f4266e6cfd99b76d7c5254aa46076bbdeb47ec",
    "SOURCES.json": "f43d4b7ecbfc1d1e5f9eb0d955da846266eadd0c0bda95cb7c090641d7834091",
}
SITES = {
    "driver": {"clone_packet", "xor_family"},
    "fresh_rows": {"split", "merge"},
    "selection": {"packet_operation"},
    "routes": {"high_key", "partition", "route_cube", "route_packet"},
    "episode": {"xor_packet"},
    "packet_engine": {"run"},
    "stream": {"add_pass"},
    "bitstream": {"digit_swap", "digit_complement", "translate_one"},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    for name, digest in PINS.items():
        require(hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest() == digest, "manifest binding: " + name)
    manifest = json.loads((PACKAGE / "SNAPSHOTS.json").read_text())
    require(manifest["commit"] == "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1", "caller pin")
    require(len(manifest["files"]) == 41, "complete snapshot inventory")
    actual = {p.relative_to(PACKAGE).as_posix() for directory in ("vendor", "sources")
              for p in (PACKAGE / directory).rglob("*") if p.is_file()}
    require(actual == set(manifest["files"]), "exact retained source inventory")
    for name, entry in manifest["files"].items():
        path = PACKAGE / name
        require(not path.is_symlink(), "regular snapshot")
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry["sha256"], "source SHA256: " + name)
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == entry["git_blob"], "source Git blob: " + name)
    return manifest


def modules(manifest):
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(PACKAGE / "vendor"), str(PACKAGE / "vendor/vendor")]
    names = ("words", "records", "cardinal_counts", "directory", "model", "node", "peel", "fresh_rows")
    result = SimpleNamespace(**{name: importlib.import_module(name) for name in names})
    for name in names:
        file = Path(getattr(result, name).__file__).resolve()
        require(file.is_relative_to(PACKAGE / "vendor") and
                file.relative_to(PACKAGE).as_posix() in manifest["files"], "runtime import: " + name)
    for module in tuple(sys.modules.values()):
        file = getattr(module, "__file__", None)
        if file and Path(file).resolve().is_relative_to(PACKAGE / "vendor"):
            require(Path(file).relative_to(PACKAGE).as_posix() in manifest["files"], "bound import")
    return result


class Meter:
    def __init__(self, m, expected):
        self.m, self.expected = m, expected
        self.phase = "setup"
        self.total = self.peak = 0
        self.phases, self.allocations = Counter(), Counter()
        self.active = {}
        self.witness = None

    def mark(self, tape, site):
        tape.content_site, tape.content_live = site, 0
        self.allocations[site] += 1

    def census(self):
        direct = sum(sum(value != self.m.words.BLANK for value in tape.cells[1:])
                     for tape in self.active.values())
        require(direct == self.total, "independent direct content census")
        return sorted(tape.content_live for tape in self.active.values())

    def update(self, tape, symbol, old):
        delta = int(symbol != self.m.words.BLANK) - int(old != self.m.words.BLANK)
        tape.content_live += delta
        self.total += delta
        if tape.content_live:
            self.active[id(tape)] = tape
        else:
            self.active.pop(id(tape), None)
        require(tape.content_live >= 0 and self.total >= 0, "nonnegative live content")
        self.peak = max(self.peak, self.total)
        self.phases[self.phase] = max(self.phases[self.phase], self.total)
        if self.total == self.expected and self.witness is None:
            self.witness = {"phase": self.phase, "tapes": self.census()}
        require(self.total <= self.expected, "complete-node content cap")

    @contextmanager
    def install(self):
        tape_type, meter = self.m.records.Tape, self
        old_init, old_write = tape_type.__init__, tape_type.write
        def initialize(tape):
            old_init(tape)
            frame = sys._getframe(1)
            for _ in range(4):
                if frame.f_code.co_name not in ("<listcomp>", "<dictcomp>"):
                    break
                frame = frame.f_back
            require(frame.f_code.co_name not in ("<listcomp>", "<dictcomp>"), "bounded allocation frame")
            file, name = Path(frame.f_code.co_filename), frame.f_code.co_name
            if file.stem in SITES and name in SITES[file.stem]:
                require(file.resolve().is_relative_to(PACKAGE / "vendor"), "allocation source")
                meter.mark(tape, file.stem + "." + name)
        def write(tape, symbol):
            old = tape.cells[tape.head] if tape.head < len(tape.cells) else meter.m.words.BLANK
            old_write(tape, symbol)
            if hasattr(tape, "content_site"):
                require(tape.head >= 1, "data excludes LEFT marker")
                meter.update(tape, symbol, old)
        tape_type.__init__, tape_type.write = initialize, write
        patches = []
        for module, name in ((self.m.peel, "run"), (self.m.fresh_rows, "split"), (self.m.fresh_rows, "merge")):
            original = getattr(module, name)
            def phase(*args, _original=original, _name=name, **kwargs):
                meter.phase = "peel" if _name == "run" else _name
                return _original(*args, **kwargs)
            patches.append((module, name, original))
            setattr(module, name, phase)
        try:
            yield
        finally:
            for module, name, original in reversed(patches):
                setattr(module, name, original)
            tape_type.__init__, tape_type.write = old_init, old_write


def destination(address, atoms, weights, gap, active=None):
    address, tail = divmod(address, 3 ** atoms)
    head, gap_digit = divmod(address, gap)
    h, t = [0] * atoms, [0] * atoms
    for i in range(atoms - 1, -1, -1):
        head, h[i] = divmod(head, 3)
        tail, t[i] = divmod(tail, 3)
    new_h, new_t = list(h), list(t)
    for i in range(atoms) if active is None else active:
        new_h[i] = weights[i] * t[atoms - 1 - i] % 3
        new_t[atoms - 1 - i] = pow(weights[i], -1, 3) * h[i] % 3
    a = b = 0
    for x, y in zip(new_h, new_t):
        a, b = 3 * a + x, 3 * b + y
    return (a * gap + gap_digit) * 3 ** atoms + b


def setup(m, atoms, prefixes, gap):
    catalogue = m.model.Catalogue()
    topology = m.model.Topology(catalogue)
    arena, indices = m.words.Arena(3), m.words.Arena(8)
    modulus = arena.input(3)
    ring = m.words.Ring(modulus)
    context = m.directory.Context(ring, catalogue.codes)
    size, depth = indices.input(atoms), indices.input(0)
    weights = tuple(1 + (i % 2 == 0) for i in range(atoms))
    incoming = m.model.Incoming(context, indices, weights)
    consumer = m.model.Consumer(context, indices, object(), size, depth, catalogue, incoming)
    caller = m.node.Node(context, indices, consumer.program, size, depth, topology, consumer, incoming)
    values = [m.cardinal_counts.Count.literal(v) for v in (prefixes, 192, 1, gap, 1)]
    return SimpleNamespace(**locals())


def run_fixture(m, atoms, prefixes, gap):
    s = setup(m, atoms, prefixes, gap)
    fibre, rows = 3 ** (2 * atoms) * gap, prefixes * 192
    volume = rows * fibre
    require(composite_geometry(4, 3, 48, prefixes, 1, fibre, 16)[0] == volume, "complete model geometry")
    expected = 3 * volume if atoms == 2 else max(4 * volume, 3 * volume + 3 * volume // prefixes)
    meter = Meter(m, expected)
    source, directory = m.records.Tape(), m.records.Tape()
    meter.mark(source, "borrowed")
    def observe(kind, *labels):
        if kind == "global":
            meter.phase = labels[0]
    with meter.install():
        for i in range(volume):
            source.append(((i * 13) ^ (i >> 3) ^ (i >> 7) ^ 0x53) & 1)
        source.rewind()
        original = bytes(source.cells)
        output = s.caller.run(source, directory, *s.values, observe)
    require(bytes(source.cells) == original, "borrowed input preserved")
    for row in range(rows):
        for address in range(fibre):
            target = row * fibre + destination(address, atoms, s.weights, gap) + 1
            require(output.cells[target] == original[row * fibre + address + 1], "independent node endpoint")
    require(meter.peak == expected and meter.witness is not None, "sharp complete-node peak")
    require(meter.total == 2 * volume and set(meter.active) == {id(source), id(output)}, "all data scratch erased")
    require(source.head == output.head == directory.head == 1, "node head return")
    meter.census()
    result = {"atoms": atoms, "old_prefixes": prefixes, "gap": gap, "volume": volume,
              "peak": meter.peak, "phases": dict(meter.phases), "witness": meter.witness,
              "allocations": dict(meter.allocations), "output_sha256": hashlib.sha256(output.cells).hexdigest()}
    finish(m, s, source, output, directory)
    return result


def finish(m, s, source, output, directory):
    for tape in (source, output, directory):
        tape.clear()
    s.incoming.close()
    for value in s.values:
        value.close()
    s.context.close()
    s.ring.close()
    s.arena.free(s.modulus)
    s.indices.free_many(s.size, s.depth)
    require(not s.arena.live and not s.indices.live, "numerical arena cleanup")


def peel_fixture(m, prefixes, gap, budget=None):
    s = setup(m, 3, prefixes, gap)
    fibre, volume = 729 * gap, prefixes * 729 * gap
    expected = 3 * volume + 3 * fibre
    meter = Meter(m, expected if budget is None else budget)
    source, directory = m.records.Tape(), m.records.Tape()
    meter.mark(source, "borrowed")
    fresh = m.cardinal_counts.Count.literal(1)
    with meter.install():
        for i in range(volume):
            source.append(((i * 7) ^ (i >> 2) ^ (i >> 5)) & 1)
        source.rewind()
        original = bytes(source.cells)
        output = m.peel.run(source, s.context, s.indices, s.size, s.depth, s.consumer.program,
                            directory, s.values[0], fresh, *s.values[2:], s.incoming)
    require(bytes(source.cells) == original, "peel borrowed input")
    for row in range(prefixes):
        for address in range(fibre):
            target = row * fibre + destination(address, 3, s.weights, gap, (2,)) + 1
            require(output.cells[target] == original[row * fibre + address + 1], "independent peel endpoint")
    require(meter.peak == expected and meter.witness is not None, "sharp peel peak")
    require(meter.total == 2 * volume and len(meter.active) == 2, "peel data cleanup")
    result = {"old_prefixes": prefixes, "gap": gap, "volume": volume, "peak": meter.peak,
              "witness": meter.witness, "allocations": dict(meter.allocations)}
    fresh.close()
    finish(m, s, source, output, directory)
    return result


def composite_geometry(families, roles, lows, prefixes, highs, fibre, key):
    values = (families, roles, lows, prefixes, highs, fibre, key)
    require(all(type(value) is int and value >= 1 for value in values), "positive integer geometry")
    require(key <= fibre, "route key fits fibre")
    packet = prefixes * highs * fibre
    volume = families * lows * packet
    extra = max((roles + 1) * packet + max(lows * packet, 3 * highs * (fibre + key)),
                (roles + 3) * packet + 3 * fibre)
    require(extra <= volume, "complete global extras fit one input")
    return volume, extra


def compare_receipt(receipt, expected):
    require(json.dumps(receipt, sort_keys=True) == json.dumps(expected, sort_keys=True), "exact typed receipt")


def validate_output(args):
    if args.write_result:
        require(args.case is None and not args.peel_only, "full receipt requires full replay")
        require(not args.write_result.resolve().is_relative_to(PACKAGE), "external receipt only")
        require(not args.write_result.exists(), "receipt must not exist")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", type=Path)
    parser.add_argument("--case", type=int, choices=range(2))
    parser.add_argument("--peel-only", action="store_true")
    args = parser.parse_args()
    validate_output(args)
    m = modules(authenticate())
    if args.peel_only:
        for prefixes, gap in ((1, 1), (2, 1), (3, 1), (1, 2)):
            print(json.dumps(peel_fixture(m, prefixes, gap)), flush=True)
        return
    cases = ((2, 1, 1), (3, 1, 1))
    if args.case is not None:
        print(json.dumps(run_fixture(m, *cases[args.case]), sort_keys=True), flush=True)
        return
    results = []
    result = run_fixture(m, *cases[0])
    results.append(result)
    print(json.dumps({k: result[k] for k in ("atoms", "old_prefixes", "volume", "peak", "phases")}), flush=True)
    peels = [peel_fixture(m, p, g) for p, g in ((1, 1), (2, 1), (3, 1), (1, 2))]
    geometry = [composite_geometry(28416, 661, n, c, h, 81, 16)
                for n in (1, 48) for c in (1, 2, 3) for h in (1, 81)]
    receipt = {"status": "PASS_SELECTED_NODE_LIVE_VOLUME", "fixtures": results,
               "peel_fixtures": peels, "geometry": geometry}
    if args.write_result:
        with args.write_result.open("x") as handle:
            handle.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        compare_receipt(receipt, expected)
    print(receipt["status"])


if __name__ == "__main__":
    main()
