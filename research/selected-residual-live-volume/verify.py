#!/usr/bin/env python3
"""Source-bound nonblank Boolean payload census; stdlib, no production edits.

Implementation: Codex gpt-6-astra at max effort. Source credits: vendor/NOTICE.md.
Default replay never writes. --write-result exclusively creates RESULT.json.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
import hashlib
import importlib
from itertools import product
import json
from math import prod
from pathlib import Path
import platform
import sys
import time
from types import SimpleNamespace


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
HEAD = "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1"
MANIFEST_HASHES = {
    "SNAPSHOTS.json": "aea4533a906e77f35e4846f13c7726feab367bf12d6d09960b7d5f2f4a678316",
    "SOURCES.json": "9f38e3f4d996ef62e4c646485fb65dcc6f358ef2ab562c81f4c0726a2fc5e9df",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rejected(operation, message):
    try:
        operation()
    except ValueError as error:
        require(message in str(error), f"wrong rejection: {error}")
        return str(error)
    raise ValueError(f"negative control accepted: {message}")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def authenticate(manifests, read=Path.read_bytes):
    # Pin manifests too: removing an unimported dependency must not pass.
    for name, digest in MANIFEST_HASHES.items():
        require(sha256(manifests[name]) == digest, f"manifest binding: {name}")
    snapshots = json.loads(manifests["SNAPSHOTS.json"])
    sources = json.loads(manifests["SOURCES.json"])
    require(snapshots["commit"] == HEAD and snapshots["pr"] == 2697, "frozen PR2697 head")
    files = snapshots["files"]
    require(len(files) == 22, "complete 22-export manifest")
    actual = {str(p.relative_to(PACKAGE)) for p in (PACKAGE / "vendor").rglob("*") if p.is_file()}
    require(actual == set(files), "complete export inventory (including importable bytes)")
    entries = [(PACKAGE / path, entry) for path, entry in files.items()]
    # Historical provenance is pinned by this manifest and checked against its
    # Git base by the package runner, not against a moving working-tree file.
    entries += [(ROOT / entry["path"], entry) for entry in sources["files"]
                if entry["usage"] == "input"]
    for path, entry in entries:
        require(not path.is_symlink(), f"regular source export: {path.name}")
        try:
            data = read(path)
        except OSError as error:
            raise ValueError(f"missing source: {path.name}") from error
        require(sha256(data) == entry["sha256"], f"source SHA256: {path.name}")
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == entry["git_blob"], f"source git blob: {path.name}")
    return snapshots


def load_sources(snapshots):
    sys.dont_write_bytecode = True
    sys.path[:0] = [str(PACKAGE / "vendor"), str(PACKAGE / "vendor/vendor")]
    names = ("packet_engine", "layout", "cardinal_counts", "records", "words", "numeric",
             "plan", "trace", "forms")
    modules = SimpleNamespace(**{name: importlib.import_module(name) for name in names})
    imported = []
    for path in snapshots["files"]:
        if path.endswith(".py"):
            name = Path(path).stem
            module = sys.modules.get(name)
            if module is not None:
                require(Path(module.__file__).resolve() == PACKAGE / path, f"bound import: {name}")
                imported.append(path)
    return modules, sorted(imported)


class Bit(int):
    """An observational origin tag; the stored cell remains an ordinary bit."""
    def __new__(cls, value, origin):
        result = int.__new__(cls, value)
        result.origin = origin
        return result


class PayloadMeter:
    def __init__(self, modules, source, volume, fibre):
        self.m = modules
        self.volume, self.fibre = volume, fibre
        self.records = {}
        self.total = self.peak = 0
        self.event_index = -1
        self.running = False
        self.check_intermediate = None
        self.events, self.snapshots = [], []
        self.allocation_counts = Counter()
        self.register(source, "borrowed", range(volume))
        self.source = source
        self.original = bytes(source.cells)

    def register(self, tape, role, origins=()):
        count = sum(cell in (0, 1) for cell in tape.cells)
        record = SimpleNamespace(tape=tape, role=role, live=count,
                                 origins={i + 1: origin for i, origin in enumerate(origins)})
        self.records[id(tape)] = record  # Strong references: GC never disposes payload.
        self.total += count
        self.peak = max(self.peak, self.total)

    def allocation_role(self, frame):
        while frame.f_code.co_name == "<listcomp>":
            frame = frame.f_back
        path, function = Path(frame.f_code.co_filename), frame.f_code.co_name
        if path == PACKAGE / "vendor/packet_engine.py" and function == "run":
            require(frame.f_lineno in (32, 38), "known packet allocation site")
            return "packet" if frame.f_lineno == 32 else "local"
        if path == PACKAGE / "vendor/vendor/stream.py" and function == "add_pass":
            self.allocation_counts[function] += 1
            return "primitive_output" if self.allocation_counts[function] % 3 == 0 else "bucket"
        if path == PACKAGE / "vendor/vendor/bitstream.py":
            if function in ("digit_swap", "digit_complement"):
                return "primitive_output" if frame.f_lineno in (47, 77) else "bucket"
            if function == "translate_one":
                self.allocation_counts[function] += 1
                return "primitive_output" if self.allocation_counts[function] % 3 == 0 else "bucket"
        return None

    @contextmanager
    def instrument(self):
        Tape = self.m.records.Tape
        original_init, original_read, original_write = Tape.__init__, Tape.read, Tape.write
        meter = self

        def init(tape):
            original_init(tape)
            role = meter.allocation_role(sys._getframe(1))
            if role is not None:
                meter.register(tape, role)

        def read(tape):
            value = original_read(tape)
            record = meter.records.get(id(tape))
            if record is not None and value in (0, 1):
                require(tape.head in record.origins, "origin for every live payload bit")
                return Bit(value, record.origins[tape.head])
            return value

        def write(tape, symbol):
            record = meter.records.get(id(tape))
            require(record is not None or not isinstance(symbol, Bit), "unclassified payload copy")
            if record is None:
                return original_write(tape, symbol)
            require(tape is not meter.source or not meter.running, "borrowed source write during execution")
            require(symbol in (0, 1, meter.m.words.BLANK), "Boolean payload alphabet")
            old = tape.cells[tape.head] if tape.head < len(tape.cells) else meter.m.words.BLANK
            if symbol in (0, 1):
                require(isinstance(symbol, Bit), "payload write retains its origin")
                record.origins[tape.head] = symbol.origin
            else:
                record.origins.pop(tape.head, None)
            original_write(tape, symbol)
            delta = int(symbol in (0, 1)) - int(old in (0, 1))
            record.live += delta
            meter.total += delta
            meter.peak = max(meter.peak, meter.total)
            if meter.events:
                event = meter.events[-1]
                event["observed"] = max(event["observed"], meter.total)
                if meter.total == event["expected"] and event["capture"]:
                    meter.snapshots.append(meter.census(sys._getframe(1)))
                    event["capture"] = False

        Tape.__init__, Tape.read, Tape.write = init, read, write
        try:
            yield
        finally:
            Tape.__init__, Tape.read, Tape.write = original_init, original_read, original_write

    def census(self, frame=None):
        engine, primitive = None, None
        while frame is not None:
            if (frame.f_code.co_name in ("add_pass", "digit_swap", "digit_complement", "translate_one")
                    and frame.f_code.co_filename.startswith(str(PACKAGE / "vendor"))):
                primitive = frame.f_locals
            if (Path(frame.f_code.co_filename) == PACKAGE / "vendor/packet_engine.py"
                    and frame.f_code.co_name == "run"):
                engine = frame.f_locals
                break
            frame = frame.f_back
        roles, total = Counter(), 0
        for record in self.records.values():
            actual = sum(cell in (0, 1) for cell in record.tape.cells)
            require(actual == record.live == len(record.origins), "direct census equals write meter")
            total += actual
            if not actual:
                continue
            role = record.role
            if primitive is not None and role == "primitive_output" and record.tape is primitive.get("source"):
                role = "primitive_current"
            if engine is not None and record.tape is not self.source:
                for variable, name in (("current", "current"), ("output", "outer_output"), ("local", "local")):
                    if record.tape is engine.get(variable):
                        role = name
                        break
            roles[role] += actual
        require(total == self.total, "direct total equals write meter")
        return {"primitive": self.event_index, "cells": total, "roles": dict(sorted(roles.items()))}

    def source_unchanged(self):
        require(bytes(self.source.cells) == self.original, "borrowed source immutability")
        require(self.records[id(self.source)].origins == {i + 1: i for i in range(self.volume)},
                "borrowed source origins")

    def no_leaks(self, output):
        self.census()
        for record in self.records.values():
            if record.tape is not self.source and record.tape is not output:
                require(record.live == 0, "no leaked owned payload")

    def observe_events(self, iterator, modulus):
        try:
            for event in iterator:
                if event.kind in ("enter", "return"):
                    yield event
                    continue
                self.event_index += 1
                extra = 3 if event.kind == "sign" or (event.kind == "atom_swap" and modulus > 3) else 2
                expected = (2 + int(self.event_index > 0)) * self.volume + extra * self.fibre
                capture = not any(e["kind"] == event.kind and e["later"] == (self.event_index > 0)
                                  for e in self.events)
                entry = {"kind": event.kind, "later": self.event_index > 0,
                         "expected": expected, "observed": self.total, "capture": capture}
                self.events.append(entry)
                yield event
                require(entry["observed"] == expected, f"exact {event.kind} lifetime peak")
                if self.check_intermediate is not None:
                    self.check_intermediate(sys._getframe(1).f_locals["current"], self.event_index + 1)
                self.source_unchanged()
        finally:
            iterator.close()


def bound(actual, budget):
    require(actual <= budget, f"payload budget exceeded: {actual} > {budget}")


def permutation(modulus, prefixes, before, gap, suffix, parent_size, transform):
    radices = [prefixes, before] + [modulus] * parent_size + [gap] + [modulus] * parent_size + [suffix]
    result = [None] * prod(radices)
    for origin, coordinates in enumerate(product(*(range(r) for r in radices))):
        prefix, pre = coordinates[:2]
        atoms = list(coordinates[2:2 + parent_size] + coordinates[3 + parent_size:-1])
        transformed = transform(prefix, atoms)
        destination = [prefix, pre] + transformed[:parent_size] + [coordinates[2 + parent_size]]
        destination += transformed[parent_size:] + [coordinates[-1]]
        index = 0
        for digit, radix in zip(destination, radices):
            require(0 <= digit < radix, "canonical expected address")
            index = index * radix + digit
        require(result[index] is None, "independent address bijection")
        result[index] = origin
    require(None not in result, "complete expected address domain")
    return result


def fixture(m, name, modulus, prefixes, before, gap, suffix, kinds=(), branch=None,
            embedded_extra=0, missing_return=False):
    n = (2 if branch is not None else 1) + embedded_extra
    R = before * gap * suffix * modulus ** (2 * n)
    v = prefixes * R
    residues = m.words.Arena(modulus.bit_length() + 1)
    modword = residues.input(modulus)
    ring = m.words.Ring(modword)
    indices = m.words.Arena(8)
    columns, depth, size = (indices.input(i) for i in (1, 0, n))
    projector = [[1, 1], [0, 0]] if branch == "good" else [[0, 0], [0, 1]]
    plan = (m.plan.compile_plan(projector, 1, 3, branch == "good") if branch is not None
            else m.plan.Plan(1, 1, True, ()))
    geometry = m.numeric.Geometry(plan, indices, columns, depth, 7, object())
    extents = [m.cardinal_counts.Count.literal(i) for i in (before, gap, suffix)]
    layout = m.layout.Layout(geometry, size, ring, 3, *extents)
    prefix_count, field_count = (m.cardinal_counts.Count.literal(i) for i in (prefixes, 1))
    source, directory = m.records.Tape(), m.records.Tape()
    bits = [(i ^ (i >> 1) ^ (i >> 3)) & 1 for i in range(v)]
    for bit in bits:
        source.append(bit)
    source.rewind()
    for prefix in range(prefixes):
        m.records.append_finite(directory, prefix, 4)
        directory.append(m.records.RECORD_END)
    directory.rewind()
    directory_bytes = bytes(directory.cells)
    pages = []
    weights = [[1 + p % 2, 2 - p % 2] for p in range(prefixes)]
    if branch is not None:
        for prefix in range(prefixes):
            matrix = [[residues.input(value) for value in row] for row in projector]
            form = (m.forms.good_form(matrix, 1, ring) if plan.good else m.forms.fallback_form(matrix, ring))
            for row in matrix:
                residues.free_many(*row)
            def weight(coordinate, p=prefix):
                return residues.input(weights[p][coordinate.inspect()])
            pages.append(m.numeric.Page(plan, form, ring, indices, columns, weight, depth, 7,
                                        geometry.parent_identity))

    calls = Counter()
    def coefficient(fields, request):
        fields.rewind()
        prefix = m.records.read_finite(fields, 4)
        require(fields.read() == m.records.RECORD_END, "complete fixture raw field")
        fields.rewind()
        require(0 <= prefix < prefixes, "fixture prefix ordinal")
        calls[prefix] += 1
        return pages[prefix].evaluate(request) if pages else residues.input((prefix + 1) % modulus)

    def literal_events():
        for kind in kinds:
            first, second = indices.input(0), indices.input(1)
            try:
                if kind == "sign":
                    yield m.trace.Event(kind, second)
                elif kind == "add":
                    yield m.trace.Event(kind, second, first)
                else:
                    yield m.trace.Event(kind, first, second)
            finally:
                indices.free_many(first, second)

    def events():
        iterator = m.trace.execute(geometry) if branch is not None else literal_events()
        try:
            for event in iterator:
                if not (missing_return and event.kind == "return"):
                    yield event
        finally:
            iterator.close()

    def transform(prefix, atoms, steps=None):
        if branch is not None:
            a = weights[prefix]
            differences = [(atoms[3 - i] - pow(a[i], -1, modulus) * atoms[i]) % modulus for i in range(2)]
            delta = [sum(projector[i][j] * differences[j] for j in range(2)) % modulus for i in range(2)]
            return [(atoms[i] + a[i] * delta[i]) % modulus for i in range(2)] + [
                (atoms[2 + i] - delta[1 - i]) % modulus for i in range(2)]
        # Independent logical-to-physical embedding; intervening atoms stay fixed.
        left, right = 0, 1 + 2 * embedded_extra
        for kind in kinds[:steps]:
            if kind == "add":
                atoms[right] = (atoms[right] + (prefix + 1) * atoms[left]) % modulus
            elif kind == "atom_swap":
                atoms[left], atoms[right] = atoms[right], atoms[left]
            else:
                atoms[right] = -atoms[right] % modulus
        return atoms

    expected = permutation(modulus, prefixes, before, gap, suffix, n, transform)
    meter = PayloadMeter(m, source, v, R)
    def check_endpoint(tape, expected_origins):
        require(list(tape.cells[1:]) == [bits[i] for i in expected_origins], "actual Boolean endpoint")
        origins = meter.records[id(tape)].origins
        require([origins[i + 1] for i in range(v)] == expected_origins, "independent unique-origin endpoint")
        require(len(set(origins.values())) == v, "every original payload cell exactly once")

    if branch is None:
        def check_intermediate(tape, steps):
            expected_origins = permutation(modulus, prefixes, before, gap, suffix, n,
                                           lambda p, a: transform(p, a, steps))
            check_endpoint(tape, expected_origins)
        meter.check_intermediate = check_intermediate
    boundaries, output = [], None
    controls = {}
    try:
        with meter.instrument():
            def run():
                meter.running = True
                try:
                    return m.packet_engine.run(source, meter.observe_events(events(), modulus), layout,
                                               directory, prefix_count, field_count, coefficient,
                                               observe=boundaries.append)
                finally:
                    meter.running = False
            if missing_return:
                controls["missing_child_return"] = rejected(run, "complete child lifetime")
            else:
                output = run()
                require(output.head == source.head == directory.head == 1, "restored payload/directory heads")
                check_endpoint(output, expected)
                if branch is not None:
                    require(boundaries and boundaries == ["enter", "return"] * (len(boundaries) // 2),
                            "whole-packet completed-child entry/return")
                else:
                    require(not boundaries, "literal primitive boundary domain")
                adds = sum(e["kind"] == "add" for e in meter.events)
                require(calls == Counter({p: 2 * adds for p in range(prefixes)}) if adds else not calls,
                        "each ADD requests its actual prefix twice")
                bound(meter.peak, 3 * v + 3 * R)
                if meter.events:
                    require(meter.snapshots and max(s["cells"] for s in meter.snapshots) == meter.peak,
                            "direct tape census at the measured global peak")
                else:
                    require(output is source and meter.census()["cells"] == v, "empty trace aliases borrowed input")
            meter.source_unchanged()
            require(bytes(directory.cells) == directory_bytes, "borrowed directory immutability")
            meter.no_leaks(output)
            if name == "sign-w2-p2":
                peak = next(s for s in meter.snapshots if s["cells"] == meter.peak)
                roles = peak["roles"]
                require(roles["borrowed"] == roles["current"] == v and roles["bucket"] == R
                        and roles["primitive_output"] == roles["primitive_current"] == R,
                        "concrete four-fibre sharpness witness")
                # False budgets come from P,R, independently of the measured peak.
                for label, budget, omitted in (
                        ("omitted_borrowed_source", 2 * v + 3 * R, roles["borrowed"]),
                        ("premature_current_disposal", 2 * v + 3 * R, roles["current"]),
                        ("omitted_bucket_output_overlap", 3 * v + 2 * R, roles["bucket"])):
                    require(peak["cells"] - budget == omitted, "underbudget matches its concrete omitted tape")
                    controls[label] = rejected(lambda b=budget: bound(meter.peak, b),
                                               "payload budget exceeded")
                original_bit = source.cells[1]
                try:
                    source.write(Bit(1 - original_bit, 0))
                    controls["borrowed_payload_mutation"] = rejected(meter.source_unchanged,
                                                                    "borrowed source immutability")
                finally:
                    source.write(Bit(original_bit, 0))
                meter.source_unchanged()
            if output is not None and output is not source:
                output.clear()
            meter.no_leaks(None)
            require(meter.total == v, "only the borrowed source remains after output disposal")
        return {"name": name, "modulus": modulus, "prefixes": prefixes,
                "before_gap_suffix": [before, gap, suffix], "parent_size": n, "R": R, "v": v,
                "primitive_counts": dict(sorted(Counter(e["kind"] for e in meter.events).items())),
                "child_returns": boundaries.count("return"), "peak": meter.peak,
                "censuses": meter.snapshots, "controls": controls}
    finally:
        for page in pages:
            page.close()
        layout.close()
        geometry.close()
        for extent in extents + [prefix_count, field_count]:
            extent.close()
        indices.free_many(columns, depth, size)
        ring.close()
        residues.free(modword)
        require(not indices.live and not residues.live, "fixture arithmetic ownership restored")
        directory.clear()
        source.clear()


def verify():
    manifests = {name: (PACKAGE / name).read_bytes() for name in MANIFEST_HASHES}
    snapshots = authenticate(manifests)
    corrupted = json.loads(manifests["SNAPSHOTS.json"])
    corrupted["files"].pop("vendor/driver.py")
    incomplete = dict(manifests, **{"SNAPSHOTS.json": json.dumps(corrupted).encode()})
    controls = {"incomplete_manifest": rejected(lambda: authenticate(incomplete), "manifest binding")}
    target = PACKAGE / "vendor/packet_engine.py"
    def corrupt_read(path):
        data = path.read_bytes()
        return data + b"\n" if path == target else data
    controls["source_byte_mutation"] = rejected(lambda: authenticate(manifests, corrupt_read), "source SHA256")
    m, imported = load_sources(snapshots)
    cases = [fixture(m, "empty-alias", 3, 1, 1, 1, 1)]
    for modulus in (3, 9):
        for kind in ("add", "atom_swap", "sign"):
            for prefixes in (1, 2):
                cases.append(fixture(m, f"{kind}-w{1 if modulus == 3 else 2}-p{prefixes}",
                                     modulus, prefixes, 2, 3, 2, kinds=(kind, kind)))
    cases.append(fixture(m, "embedded-gap", 3, 2, 1, 2, 1,
                         kinds=("add", "atom_swap", "sign"), embedded_extra=1))
    for branch in ("good", "fallback"):
        cases.append(fixture(m, f"completed-{branch}", 3, 2, 1, 2, 1, branch=branch))
    cases.append(fixture(m, "missing-return", 3, 1, 1, 1, 1, branch="good", missing_return=True))
    authenticate(manifests)
    return {
        "schema_version": 1,
        "status": "PASS_SOURCE_BOUND_RESIDUAL_PAYLOAD",
        "implementation": "Codex gpt-6-astra at max effort",
        "source_credits": "vendor/NOTICE.md",
        "source_head": HEAD,
        "manifest_sha256": MANIFEST_HASHES,
        "checker_sha256": sha256(Path(__file__).read_bytes()),
        "authenticated_exports": 22,
        "authenticated_repository_inputs": 0,
        "imported_source_modules": imported,
        "reproduce": ["python3 -B research/selected-residual-live-volume/verify.py",
                      "python3 -B -O research/selected-residual-live-volume/verify.py"],
        "claim": {
            "metric": "live nonblank Boolean payload cells on distinct tapes, including borrowed source",
            "premises": ["P >= 1 complete prefix fibres of nonblank Boolean cells",
                         "R > 0 full fibre volume including all spectators; v = P*R",
                         "q fixed odd prime; M = q^w, w >= 1; valid complete primitive/leaf trace",
                         "source callbacks allocate no payload; source and prefix directory are borrowed",
                         "successful execution with production cleanup; completed leaves only"],
            "bound": "3*v + 3*R",
            "exact_primitive_peak": {
                "ADD_or_w1_atom_swap": "(2 + (primitive_index > 0))*v + 2*R",
                "sign_or_w_ge_2_atom_swap": "(2 + (primitive_index > 0))*v + 3*R",
                "empty_trace": "v"
            },
            "lifetime": {"borrowed": "v", "distinct_current_after_first_primitive": "v",
                         "outer_output_during_last_fibre": "(P-1)*R",
                         "ADD_local_source_buckets_output": "3*R",
                         "multi_digit_swap_or_sign_local_original_current_buckets_output": "4*R",
                         "outer_copy_phase_local_plus_changed": "2*R"},
            "sharp_when": "a non-first primitive is a sign or an atom swap with w >= 2; every completed leaf supplies a later sign",
            "proof_sources": ["vendor/packet_engine.py:10-63", "vendor/vendor/stream.py:111-163",
                              "vendor/vendor/bitstream.py:29-160", "vendor/layout.py:26-60",
                              "vendor/vendor/trace.py:53-167"],
            "caller_corollary": {
                "K": "number of distinct retained staged packets of volume v; count any live private packet",
                "MOVE": "(K-1)*v + (3*v+3*R) = (K+2)*v+3*R",
                "COPY": "K*v + (3*v+3*R) = (K+3)*v+3*R; borrowed engine input is a fresh clone",
                "aliases": "count distinct tape identities once; MOVE input is already staged; COPY clone is separate",
                "ERASE": "buffers.pop(private).clear() disposes the private payload",
                "sources": ["vendor/driver.py:36-49", "vendor/driver.py:95-141", "vendor/consumer.py:20-58"],
                "scope": "source-derived staged roles plus residual only; Driver.local not executed; not total caller reserve"
            }
        },
        "fixture_domain": "q=3; complete declared Boolean address domains with deterministic bits and unique origins; not GL64",
        "checks": ["exact byte and git-blob authentication before imports", "all checks survive -O",
                   "actual Boolean bits and distinct origin permutation", "borrowed source/directory immutability",
                   "meter equals direct tape census at peak", "owned payload cleanup and child return"],
        "binding_controls": controls,
        "cases": cases,
        "not_verified": ["full selected GL64 execution or selected 64-dimensional coefficient callbacks",
                         "route or directory storage", "markers, numerical/controller/count tapes, Python capacity",
                         "larger recursive calls, total caller reserve, new kappa or complete multiplication theorem",
                         "arbitrary exception-path primitive cleanup or formal-kernel verification"]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true", help="create RESULT.json; refuse overwrite")
    args = parser.parse_args()
    path = PACKAGE / "RESULT.json"
    require(not args.write_result or not path.exists(), "refuse to overwrite RESULT.json")
    start = time.monotonic()
    result = verify()
    if args.write_result:
        result["generation"] = {"python": platform.python_version(),
                                "implementation": platform.python_implementation(),
                                "portable_command": ["python3", "-B",
                                    str(Path(__file__).relative_to(ROOT)), "--write-result"],
                                "seconds": round(time.monotonic() - start, 3)}
        with path.open("x") as file:
            json.dump(result, file, indent=2, sort_keys=True)
            file.write("\n")
    elif path.exists():
        recorded = json.loads(path.read_text())
        recorded.pop("generation", None)  # Environment/timing are provenance, not mathematical evidence.
        require(json.dumps(recorded, sort_keys=True) == json.dumps(result, sort_keys=True),
                "RESULT.json exact typed replay")
    print(json.dumps({"status": result["status"], "fixtures": len(result["cases"]),
                      "seconds": round(time.monotonic() - start, 3), "python": platform.python_version(),
                      "optimization": sys.flags.optimize, "result_present": path.exists()}, sort_keys=True))


if __name__ == "__main__":
    main()
