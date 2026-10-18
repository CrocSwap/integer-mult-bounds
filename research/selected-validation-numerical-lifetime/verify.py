#!/usr/bin/env python3
"""Literal source lifetime checks; Ross Richardson with OpenAI Codex, Apache-2.0."""
import argparse
import hashlib
import importlib
import importlib.abc
import importlib.util
import json
import math
from pathlib import Path
import sys
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
SNAPSHOT_HASH = "69ee10977b78aacd151042b8be962363e2690a6a019e8e93bedd4b130daa853a"


def need(value, message):
    if not value:
        raise ValueError(message)


def strict_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def authenticate():
    path = ROOT / "evidence/PR2801-SNAPSHOT.json"
    need(hashlib.sha256(path.read_bytes()).hexdigest() == SNAPSHOT_HASH, "snapshot pin")
    data = strict_json(path)
    need(data["head"] == "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1", "runtime head")
    expected = {row["path"] for row in data["files"]}
    need({str(p.relative_to(ROOT)) for p in (ROOT / "vendor").iterdir()
          if p.is_file() and p.suffix in (".py", ".md")} == expected, "source inventory")
    sources = {}
    for row in data["files"]:
        content = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(content).hexdigest() == row["sha256"], "source sha256")
        blob = b"blob " + str(len(content)).encode() + b"\0" + content
        need(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob")
        if row["path"].endswith(".py"):
            sources[Path(row["path"]).stem] = content
    return sources


class SourceLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, sources):
        self.sources = sources

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.sources:
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        # Execute exactly authenticated bytes. Never consult .pyc or sys.path.
        module.__file__ = str(ROOT / "vendor" / (module.__name__ + ".py"))
        exec(compile(self.sources[module.__name__], module.__file__, "exec"), module.__dict__)


@contextmanager
def runtime():
    sources = authenticate()
    saved = {name: sys.modules.pop(name) for name in sources if name in sys.modules}
    loader = SourceLoader(sources)
    sys.meta_path.insert(0, loader)
    try:
        yield SimpleNamespace(**{name: importlib.import_module(name) for name in sources})
    finally:
        sys.meta_path.remove(loader)
        for name in sources:
            sys.modules.pop(name, None)
        sys.modules.update(saved)


class Specifications(dict):
    def __init__(self, q, events, current_good):
        identity = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
        super().__init__()
        self[0] = SimpleNamespace(code=0, good=current_good, low=identity,
                                 template=SimpleNamespace(q=q, rank=1))
        for kind, code, rank, *_ in events:
            self[code] = SimpleNamespace(code=code, good=(kind == 0), low=identity,
                                        template=SimpleNamespace(q=q, rank=rank))
        self.catalogue = SimpleNamespace(requests=[SimpleNamespace(kind="LOCAL")])
        self.fixed_plan = SimpleNamespace(dimension=64, good=current_good, rank=1)

    def bind(self, request_id, common, low):
        need(request_id == 0 and common and low == self[0].low, "fixture request")
        return self[0]

    def plan(self, code):
        need(code == 0, "fixture plan")
        return self.fixed_plan


def ancestral_root(width, events):
    value = width
    for kind, _code, rank, _field, _reverse, half in reversed(events):
        if kind == 0:
            need(value % rank == 0, "integral backward good extent")
            value = 64 * (value // rank)
        else:
            value *= 128 if half else 64
    return value


def fixture(m, width=64, q=5, exponent=1, unit=2, events=(), borrowed=3, good=True,
            full=False):
    need(64 <= width < 128 and exponent >= 1 and math.gcd(unit, q) == 1, "fixture domain")
    modulus = q ** exponent
    need(0 < unit < modulus, "fixture unit")
    root = ancestral_root(width, events)
    residues = m.words.Arena(modulus.bit_length()+1, 4200 if full else 64)
    indices = m.words.Arena(max(8, root.bit_length()+1), 96)
    ring = m.words.Ring(residues.literal(modulus))
    specifications = Specifications(q, events, good)
    program = m.records.Program.fixture(indices, residues, root, unit, events, code_bits=8)
    high = [[0] * 64 for _ in range(64)]
    encoded = [(event[1], high) for event in events]
    fields = m.records.Fields.fixture(indices, residues, encoded + ([] if full else [(0, high)]),
                                      code_bits=8)
    size, depth = indices.literal(width), indices.literal(len(events))
    extras_r = [residues.literal(i % modulus) for i in range(borrowed)]
    extras_i = [indices.literal(i) for i in range(borrowed)]
    context = None
    counts = []
    if full:
        need(exponent == 1, "bounded complete directory domain")
        codes = SimpleNamespace(q=q, dimension=64, bits=8, limit=256)
        context = m.directory.Context(ring, codes)
        counts = [m.cardinal_counts.Count.literal(1) for _ in range(4)]
    return SimpleNamespace(**locals())


def saved_arena(arena):
    return {slot: (bytes(arena.words[slot].cells), arena.words[slot].head) for slot in arena.live}


class Census:
    def __init__(self, case, bounds=None):
        self.case = case
        self.arenas = (case.residues, case.indices)
        self.saved = tuple(saved_arena(a) for a in self.arenas)
        self.baseline = tuple(len(a.live) for a in self.arenas)
        self.bounds = bounds
        self.phase = "setup"
        self.peaks = {}
        self.events = self.scans = 0
        self.joint_peak = 0
        self.orig_zero = case.m.words.Arena.zero

    def zero(self, arena):
        result = self.orig_zero(arena)
        if arena in self.arenas:
            self.sample(scan=False)
        return result

    def sample(self, scan=False):
        self.events += 1
        extra = tuple(len(a.live)-n for a, n in zip(self.arenas, self.baseline))
        self.joint_peak = max(self.joint_peak,
                              sum(n*(a.bits+1) for n, a in zip(extra, self.arenas)))
        previous = self.peaks.setdefault(self.phase, [0, 0])
        old = tuple(previous)
        for j, count in enumerate(extra):
            previous[j] = max(previous[j], count)
            if self.bounds is not None:
                need(count <= self.bounds[j], "numerical lifetime budget")
        grew_index = previous[1] > old[1]
        grew_residue = previous[0] > old[0]
        census_peak = grew_index or (grew_residue and
                                    (previous[0] <= 16 or previous[0] & (previous[0]-1) == 0))
        if scan or census_peak:
            for arena in self.arenas:
                occupied = sum(c not in (self.case.m.words.LEFT, self.case.m.words.BLANK)
                               for word in (*arena.words, arena.template) for c in word.cells)
                need(occupied == (len(arena.live)+1)*(arena.bits+1), "occupied-cell census")
                self.scans += 1

    @contextmanager
    def measuring(self):
        census = self
        def zero(arena):
            return census.zero(arena)
        with patch.object(self.case.m.words.Arena, "zero", zero):
            yield

    def restored(self):
        need(tuple(saved_arena(a) for a in self.arenas) == self.saved, "entry numerical preservation")
        self.sample(scan=True)


def local_index_bound(events):
    return 10 if not events else 15 if any(e[5] for e in events) else 14


def run_callback(m, bounds=None, **args):
    case = fixture(m, **args)
    meter = Census(case, bounds or (12, local_index_bound(case.events)))
    tapes = bytes(case.program.tape.cells), bytes(case.fields.tape.cells)
    with meter.measuring():
        meter.phase = "validation"
        frame = m.controller.Callback(case.ring, case.indices, case.program, case.fields,
                                      case.specifications, 0, allow_fallback=True)
        need(frame.final_size.inspect() == case.width and frame.depth.inspect() == len(case.events),
             "independent chronological endpoint")
        need(frame.root_size.inspect() == case.root and frame.root_unit.inspect() == case.unit,
             "independent root decode")
        need(frame.high_cap.inspect() == case.q**(case.exponent-1), "independent prime-power cap")
        need(frame.pending.empty() and frame.values.empty(), "validation never evaluates weights")
        need((len(case.residues.live)-meter.baseline[0], len(case.indices.live)-meter.baseline[1]) == (2, 6),
             "owned initialized Callback inventory")
        meter.sample(scan=True)
        frame.close()
        meter.restored()
    need(tapes == (bytes(case.program.tape.cells), bytes(case.fields.tape.cells)), "serialized preservation")
    need(case.program.tape.head == case.fields.tape.head == 1, "serialized head restoration")
    need(meter.peaks["validation"][1] == local_index_bound(case.events), "sharp callback index peak")
    return record(case, meter, "callback")


def run_prefix(m, bounds=(4096, 23), **args):
    case = fixture(m, full=True, **args)
    meter = Census(case, bounds)
    consumer = m.consumer.Consumer(case.context, case.indices, case.program, case.specifications,
                                   case.size, case.depth)
    tapes = bytes(case.program.tape.cells), bytes(case.fields.tape.cells)
    original_produce, original_callback = m.consumer.produce, m.consumer.Callback
    boundary = []
    def produce(*args):
        meter.phase = "directory"
        output = original_produce(*args)
        meter.phase = "setup"
        return output
    def callback(*args, **kwargs):
        need(tuple(len(a.live)-b for a, b in zip(meter.arenas, meter.baseline)) == (0, 8),
             "eight persistent caller indices")
        meter.phase = "validation"
        return original_callback(*args, **kwargs)
    def stop_at_run(source, events, layout, directory, prefixes, fields, coefficient, observe=None):
        # This is the exact endpoint of the claim. No packet/trace execution is asserted.
        meter.phase = "boundary"
        meter.sample(scan=True)
        need(tuple(len(a.live)-b for a, b in zip(meter.arenas, meter.baseline)) == (0, 8),
             "validated boundary inventory")
        need(layout.total.inspect() == 2*case.width and fields.inspect() == len(case.events)+1,
             "caller geometry endpoint")
        need(case.program.tape.head == 1, "program head at boundary")
        events.close()
        boundary.append(True)
        return source
    with meter.measuring(), patch.object(m.consumer, "produce", produce), \
            patch.object(m.consumer, "Callback", callback), patch.object(m.packet_engine, "run", stop_at_run):
        source = m.records.Tape()
        result = consumer.apply(source, 0, True, case.specifications[0].low, case.fields.tape,
                                *case.counts[:1], case.counts[1], case.counts[2], case.counts[3])
        need(result is source and boundary == [True], "one checked prefix endpoint")
        meter.restored()
    need(tapes == (bytes(case.program.tape.cells), bytes(case.fields.tape.cells)), "prefix input bytes")
    need(case.program.tape.head == case.fields.tape.head == 1, "prefix input heads")
    need(meter.peaks["validation"][1] == 8+local_index_bound(case.events), "sharp composed index peak")
    exact_joint = max(4096*(case.residues.bits+1),
                      2*(case.residues.bits+1)+(8+local_index_bound(case.events))*(case.indices.bits+1))
    need(meter.joint_peak == exact_joint, "exact joint prefix content")
    return record(case, meter, "prefix")


def record(case, meter, kind):
    return {"kind": kind, "q": case.q, "exponent": case.exponent, "unit": case.unit,
            "width": case.width, "events": [list(e) for e in case.events], "borrowed": case.borrowed,
            "good": case.good, "peak": meter.peaks, "allocation_and_boundary_samples": meter.events,
            "cell_scans": meter.scans, "joint_additional_symbols": meter.joint_peak}


def cases():
    good = (0, 1, 1, 0, 0, 0)
    pair = (1, 2, 1, 126, 1, 0)
    unit = (2, 2, 1, 0, 0, 0)
    half = (2, 2, 1, 0, 0, 1)
    result = []
    with runtime() as m:
        for events in [(), (good,), (pair,), (unit,), (half,), (good, pair, unit, half), (half,)*8]:
            for q, exponent in [(3, 1), (5, 1), (3, 3), (7, 2)]:
                result.append(run_callback(m, events=events, q=q, exponent=exponent))
        for rank in range(1, 43):
            width = ((64+rank-1)//rank)*rank
            result.append(run_callback(m, width=width, events=((0, 1, rank, 0, 0, 0),), borrowed=7))
        for events in [(), (good,), (pair,), (unit,), (half,), (good, pair, unit, half)]:
            for width, q, good_flag in [(64, 5, True), (127, 3, False)]:
                result.append(run_prefix(m, events=events, width=width, q=q, good=good_flag))
    return {"schema": 1, "callback_bound": [12, 15], "prefix_bound": [4096, 23],
            "scope": "successful occupied numerical contents; no payload, physical reserve or new kappa",
            "fixtures": result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = cases()
    path = ROOT / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2)+"\n")
    else:
        check_receipt(result, path)
    print("PASS_VALIDATION_LIFETIME fixtures="+str(len(result["fixtures"]))+" callback=12/15 prefix=4096/23 no_new_kappa")


def check_receipt(result, path):
    expected = strict_json(path)
    need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True), "typed fixed receipt")


if __name__ == "__main__":
    main()
