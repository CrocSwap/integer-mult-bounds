"""Exact resource audit of the unchanged PR2310 generated-weight interpreter.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
New work: Apache-2.0. The separately pinned interpreter is Jose Manuel's.
"""
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
import ast
import hashlib
import importlib.util
import itertools
import json
from math import factorial, gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ALPHA = Fraction(21, 32)
LIMITS = {
    "requests": Fraction(21, 16),
    "table_reads": Fraction(441, 512),
    "ring_operations": Fraction(441, 512),
    "events": Fraction(2205, 1024),
    "head_pages": Fraction(972405, 262144),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def reject(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("failure control accepted: " + label)


def pins():
    source = json.loads((HERE / "SOURCES.json").read_text())
    entries = source["vendored_sources"]
    need({e["path"] for e in entries} == {
        "sources/pr2310/" + name
        for name in ("control.py", "README.md", "PROOF.md", "NOTICE.md")
    }, "complete pinned predecessor input set")
    for entry in entries:
        data = (HERE / entry["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == entry["sha256"],
             "predecessor SHA256: " + entry["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(hashlib.sha1(blob).hexdigest() == entry["git_blob"],
             "predecessor Git blob: " + entry["path"])
        need(entry["commit"] == "a5258f548bfb6da71c3b72733fbbd2fb4995c929",
             "exact PR2310 source head")
    return {e["path"]: e["sha256"] for e in entries}


def load_source():
    path = HERE / "sources/pr2310/control.py"
    spec = importlib.util.spec_from_file_location("pr2310_request_mass_source", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    tree = ast.parse(path.read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == "evaluate")
    pops = [n for n in ast.walk(function) if isinstance(n, ast.Assign)
            and isinstance(n.value, ast.Call)
            and isinstance(n.value.func, ast.Attribute)
            and isinstance(n.value.func.value, ast.Name)
            and n.value.func.value.id == "pending"
            and n.value.func.attr == "pop"]
    need(len(pops) == 1, "one unchanged interpreter event-pop site")
    return module, pops[0].lineno


@dataclass(frozen=True)
class Kind:
    name: str
    rank: int = 0
    branches: int = 0

    def child(self, extent):
        f = extent // 64
        if self.name == "good":
            return self.rank * f
        if self.name == "half":
            return f // 2
        return f

    def inverse_extent(self, child):
        if self.name == "good":
            return 64 * ((child + self.rank - 1) // self.rank)
        return (128 if self.name == "half" else 64) * child

    @property
    def b(self):
        return 1 if self.name == "good" else self.branches

    @property
    def table(self):
        return int(self.name in ("good", "pair"))

    @property
    def constants(self):
        return 2 - self.branches if self.name == "pair" else 0

    @property
    def ring(self):
        return 3 if self.name == "pair" else self.table


ALPHABET = (Kind("good", 1), Kind("good", 7), Kind("good", 42),
            Kind("pair", branches=0), Kind("pair", branches=1),
            Kind("pair", branches=2), Kind("unit"), Kind("half"))


def extents(kinds, root):
    sizes = [root]
    for kind in kinds:
        sizes.append(kind.child(sizes[-1]))
        need(0 < sizes[-1] < sizes[-2], "positive proper child")
    return sizes


def minimal_root(kinds):
    root = 1
    for kind in reversed(kinds):
        root = kind.inverse_extent(root)
    return root


def counts(kinds):
    """Level multiplicities, independent of the interpreter's execution order.

    Constants are events but not recursive value requests. Ages remain global
    even when a reset annihilates all requests to older levels.
    """
    multiplicities = [0] * (len(kinds) + 1)
    multiplicities[-1] = 1
    for level in range(len(kinds), 0, -1):
        multiplicities[level - 1] = multiplicities[level] * kinds[level - 1].b
    reads = {level: multiplicities[level] * kind.table
             for level, kind in enumerate(kinds, 1)}
    tables = sum(reads.values())
    constants = sum(multiplicities[i] * k.constants
                    for i, k in enumerate(kinds, 1))
    requests = sum(multiplicities)
    return {
        "requests": requests,
        "table_reads": tables,
        "ring_operations": sum(multiplicities[i] * k.ring
                               for i, k in enumerate(kinds, 1)),
        "events": requests + tables + constants,
        "head_pages": 2 * sum(i * amount for i, amount in reads.items()),
        "field_reads": {i - 1: amount for i, amount in reads.items() if amount},
    }


def check_limits(root, final, expected):
    for key, limit in LIMITS.items():
        need(final * expected[key] * limit.denominator <= root * limit.numerator,
             "complete-vector bound: " + key)


def make_source_case(source, kinds, root, q=5, width=2, reverse=False):
    steps, tables = [], []
    modulus = q ** width
    units = [i for i in range(1, modulus) if gcd(i, q) == 1]
    for age, kind in enumerate(kinds):
        tag = 100 + age
        permutation = list(range(128))
        field = 1
        if kind.name == "pair":
            a, b = {0: (64, 65), 1: (1, 65), 2: (1, 2)}[kind.branches]
            permutation[a], permutation[b] = permutation[b], permutation[a]
            field = a
        steps.append(source.Step(
            "unit" if kind.name == "half" else kind.name, tag,
            rank=kind.rank if kind.name == "good" else 7,
            field=field, reverse=reverse, half=kind.name == "half"))
        tables.append(source.Table(tag,
            tuple(units[(j + age) % len(units)] for j in range(64)),
            tuple(units[(3 * j + age) % len(units)] for j in range(128)),
            tuple(permutation)))
    program = source.Program(q, width, root, units[-1], tuple(steps))
    meter = source.Meter()
    tape = source.FrozenTape(tuple(tables), modulus, meter)
    return program, tape, meter


def execute(source, pop_line, kinds, root, *, all_coordinates=True,
            q=5, width=2, reverse=False):
    program, tape, meter = make_source_case(source, kinds, root, q, width, reverse)
    sizes = extents(kinds, root)
    need(program.extents() == sizes, "source extent binding")
    expected = counts(kinds)
    indices = range(sizes[-1]) if all_coordinates else (sizes[-1] - 1,)
    emitted = len(indices)
    event_count = 0
    values = hashlib.sha256()

    def local_trace(frame, event, arg):
        nonlocal event_count
        if event == "line" and frame.f_lineno == pop_line:
            event_count += 1
        return local_trace

    def trace(frame, event, arg):
        return local_trace if frame.f_code is source.evaluate.__code__ else None

    previous_trace = sys.gettrace()
    sys.settrace(trace)
    try:
        for index in indices:
            value = source.evaluate(program, tape, index)
            values.update((str(value) + ",").encode())
    finally:
        sys.settrace(previous_trace)
    observed = {
        "requests": meter.requests,
        "table_reads": len(meter.field_reads),
        "ring_operations": meter.ring_operations,
        "events": event_count,
        "head_pages": meter.head_moves // tape.page_bits,
    }
    wanted = {key: emitted * expected[key] for key in LIMITS}
    need(observed == wanted, "level recurrence equals unchanged source meters")
    need(meter.head_moves == wanted["head_pages"] * tape.page_bits,
         "integral complete-page round trips")
    need(meter.bit_reads == wanted["table_reads"] * tape.page_bits,
         "complete-page bit reads")
    need(meter.combines == wanted["table_reads"], "one continuation per table")
    need(dict(Counter(meter.field_reads)) ==
         {slot: n * emitted for slot, n in expected["field_reads"].items()},
         "global field ages and reset pruning")
    need(tape.head == 0 and meter.maximum_stack_items <= 2 * len(kinds) + 1,
         "head and stack boundary")
    check_limits(root, sizes[-1], expected)
    return {"root": root, "final": sizes[-1], "emitted": emitted,
            "observed": observed, "page_bits": tape.page_bits,
            "maximum_stack_items": meter.maximum_stack_items,
            "value_trace_sha256": values.hexdigest()}


def analytic_constants():
    # The written proof extends each finite maximum by its decreasing ratio.
    sequences = {
        "requests": lambda h: (h + 1) * ALPHA ** h,
        "table_reads": lambda h: h * ALPHA ** h,
        "ring_operations": lambda h: h * ALPHA ** h,
        "events": lambda h: (2 * h + 1) * ALPHA ** h,
        "head_pages": lambda h: h * (h + 1) * ALPHA ** h,
    }
    maxima = {}
    for key, sequence in sequences.items():
        values = [sequence(h) for h in range(33)]
        maximum = max(values)
        need(maximum == LIMITS[key], "sharp rational envelope constant")
        maxima[key] = {"value": str(maximum), "at_depth": values.index(maximum)}
    need(10000 + 3 * 17 <= 592 * 17, "root-coupled integer exponent")
    # A=591 does not follow from e^17 <= w^10000 by this exponent comparison.
    need(10000 + 3 * 17 > 591 * 17, "envelope exponent boundary")
    return {"maxima": maxima, "preparation_exponent": 592,
            "absorption_constant_bits": (2 ** 592 * factorial(592)).bit_length(),
            "previous_absorption_constant_bits":
                (2 ** 1800 * factorial(1800)).bit_length()}


def abstract_census():
    digest, checked = hashlib.sha256(), 0
    for depth in range(6):
        for indices in itertools.product(range(len(ALPHABET)), repeat=depth):
            kinds = tuple(ALPHABET[i] for i in indices)
            minimum = minimal_root(kinds)
            expected = counts(kinds)
            for offset in (0, 1, 63):
                root = minimum + offset
                final = extents(kinds, root)[-1]
                check_limits(root, final, expected)
                digest.update(canonical([indices, root, final, expected]).encode() + b"\n")
                checked += 1
    return {"alphabet_size": len(ALPHABET), "maximum_depth": 5,
            "root_offsets": [0, 1, 63], "cases": checked,
            "trace_sha256": digest.hexdigest()}


def source_census(source, pop_line):
    digest, programs, coordinates = hashlib.sha256(), 0, 0
    totals = Counter()
    rings = ((3, 1), (3, 2), (5, 1), (5, 2), (7, 2), (3, 3))
    for depth in range(4):
        for indices in itertools.product(range(len(ALPHABET)), repeat=depth):
            kinds = tuple(ALPHABET[i] for i in indices)
            q, width = rings[programs % len(rings)]
            row = execute(source, pop_line, kinds, minimal_root(kinds),
                          q=q, width=width, reverse=bool(programs % 2))
            digest.update(canonical([indices, q, width, programs % 2, row]).encode() + b"\n")
            programs += 1
            coordinates += row["emitted"]
            totals.update(row["observed"])
    # Cover every legal Good rank, not just the three census representatives.
    for rank in range(1, 43):
        row = execute(source, pop_line, (Kind("good", rank),), 127)
        digest.update(canonical(["all_ranks", rank, row]).encode() + b"\n")
        programs += 1
        coordinates += row["emitted"]
        totals.update(row["observed"])
    deep = (Kind("pair", branches=2),) * 10
    deep_row = execute(source, pop_line, deep, 64 ** 10)
    digest.update(canonical(["binary_depth_ten", deep_row]).encode() + b"\n")
    programs += 1
    coordinates += deep_row["emitted"]
    totals.update(deep_row["observed"])
    return {"programs": programs, "coordinates": coordinates,
            "totals": dict(totals), "trace_sha256": digest.hexdigest(),
            "rings": [list(r) for r in rings], "deep_binary": deep_row}


def sharpness(source, pop_line):
    result = {}
    for depth in (1, 2, 4):
        kinds = (Kind("good", 42),) * depth
        root = 64 ** depth
        row = execute(source, pop_line, kinds, root,
                      all_coordinates=depth < 4)
        # At depth four, one exact coordinate trace is scaled by the proven
        # coordinate-independent event recurrence; no full-vector run is claimed.
        c = counts(kinds)
        ratios = {key: str(Fraction(row["final"] * c[key], root)) for key in LIMITS}
        keys = {1: ("requests",), 2: ("table_reads", "ring_operations", "events"),
                4: ("head_pages",)}[depth]
        for key in keys:
            need(Fraction(ratios[key]) == LIMITS[key], "attaining legal grammar")
        result[str(depth)] = {"execution": row, "full_vector_ratios": ratios,
                              "attains": list(keys),
                              "coverage": "all coordinates" if depth < 4 else
                                  "one coordinate plus exact multiplicity proof"}
    return result


def controls(source, pop_line):
    labels = []
    labels.append(reject(lambda: check_limits(64, 43, counts((Kind("good", 43),))),
                         "Good43 breaks the sharp request constant"))
    labels.append(reject(lambda: source.Program(5, 2, 64, 1,
        (source.Step("good", 1, rank=43),)).extents(),
        "pinned interpreter rejects rank43"))
    labels.append(reject(lambda: check_limits(64, 32, counts((Kind("pair", branches=2),))),
                         "binary branching without its width loss breaks the bound"))
    kinds = (Kind("pair", branches=2),)
    row = execute(source, pop_line, kinds, 64)
    wrong = counts((Kind("pair", branches=1),))
    labels.append(reject(lambda: need(row["observed"]["requests"] == wrong["requests"],
                                     "second recursive bank was discarded"),
                         "discarded Pair branch changes actual work"))
    kinds = (Kind("good", 42), Kind("unit"), Kind("good", 42))
    row = execute(source, pop_line, kinds, minimal_root(kinds))
    wrong = counts((Kind("good", 42), Kind("good", 1), Kind("good", 42)))
    labels.append(reject(lambda: need(row["observed"]["table_reads"] ==
        row["emitted"] * wrong["table_reads"], "reset did not prune"),
        "traversing discarded reset ancestry changes work"))
    labels.append(reject(lambda: need(row["observed"]["head_pages"] ==
        2 * row["observed"]["table_reads"], "global field age was compacted"),
        "post-reset field remains at its global physical age"))
    kinds = (Kind("good", 42),) * 2
    labels.append(reject(lambda: check_limits(4096, 4096, counts(kinds)),
                         "root-many requests at a smaller child exceed the contract"))
    labels.append(reject(lambda: source.Program(5, 2, 64, 1,
        (source.Step("unit", 1, half=True),)).extents(),
        "zero-width half reset is inadmissible"))
    p, tape, _ = make_source_case(source, (Kind("good", 42),), 64)
    tape.count = 0
    labels.append(reject(lambda: source.evaluate(p, tape, 0),
                         "missing global frozen table rejected"))
    # Both orientations must have the same work despite different atom maps.
    kinds = (Kind("good", 42), Kind("pair", branches=2), Kind("good", 7))
    root = minimal_root(kinds)
    left = execute(source, pop_line, kinds, root, reverse=False)
    right = execute(source, pop_line, kinds, root, reverse=True)
    need(left["observed"] == right["observed"], "orientation-invariant resource count")
    return {"rejections": labels, "positive_orientation_pair": True}


def build_receipt():
    source_hashes = pins()
    source, pop_line = load_source()
    return {
        "schema_version": 1,
        "status": "SCOPED_PROOF_WITH_FINITE_SOURCE_CHECKS_NO_NEW_KAPPA",
        "predecessor_sha256": source_hashes,
        "analytic": analytic_constants(),
        "abstract_census": abstract_census(),
        "source_census": source_census(source, pop_line),
        "sharpness": sharpness(source, pop_line),
        "controls": controls(source, pop_line),
    }
