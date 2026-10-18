#!/usr/bin/env python3
"""Check count backing on authenticated source, independently of count values."""

import argparse
import ast
import hashlib
import itertools
import json
import sys
import types
import weakref
from contextlib import contextmanager
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
SOURCE = "research/selected-layout-numerical-lifetime/vendor/"
PIN = "390e317eeea06aa53874f3bf87f7407d349f42c2c544b33e4d4fe58ba65083d6"
MODULES = (
    "words",
    "records",
    "stream",
    "cardinality",
    "counts",
    "cardinal_counts",
    "layout",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(repo=REPO):
    raw = (PACKAGE / "SOURCES.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == PIN, "source manifest identity")
    entries = [e for e in json.loads(raw)["files"] if e["usage"] == "input"]
    expected = {
        SOURCE + name + ".py" for name in (*MODULES, "numeric", "stream_runner")
    }
    expected.add(SOURCE + "NOTICE.md")
    require(len(entries) == len(expected), "unique input inventory")
    require({e["path"] for e in entries} == expected, "complete input inventory")
    result = {}
    for entry in entries:
        data = (repo / entry["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry["sha256"], "source hash")
        blob = hashlib.sha1(
            b"blob " + str(len(data)).encode() + b"\0" + data
        ).hexdigest()
        require(blob == entry["git_blob"], "source Git blob")
        result[Path(entry["path"]).stem] = data
    return result


def extract(data, name, kind, scope):
    nodes = [
        node
        for node in ast.parse(data).body
        if isinstance(node, kind) and node.name == name
    ]
    require(len(nodes) == 1, "one exact source definition")
    tree = ast.Module(body=nodes, type_ignores=[])
    exec(compile(tree, "authenticated/" + name, "exec"), scope)
    return scope[name]


@contextmanager
def source_modules(repo=REPO):
    data = authenticate(repo)
    missing = object()
    previous = {name: sys.modules.get(name, missing) for name in MODULES}
    modules = {}
    try:
        for name in MODULES:
            module = types.ModuleType(name)
            module.__file__ = str(repo / (SOURCE + name + ".py"))
            sys.modules[name] = module
            exec(compile(data[name], module.__file__, "exec"), module.__dict__)
            modules[name] = module
        scope = {"Unsigned": modules["words"].Unsigned, "need": require}
        modules["Geometry"] = extract(data["numeric"], "Geometry", ast.ClassDef, scope)
        scope = {"need": require, "add_pass": modules["stream"].add_pass}
        modules["action"] = extract(
            data["stream_runner"], "action", ast.FunctionDef, scope
        )
        yield types.SimpleNamespace(**modules)
    finally:
        for name, old in previous.items():
            if old is missing:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old


class Census:
    def __init__(self):
        self.roots = weakref.WeakValueDictionary()
        self.base = set()
        self.peak = self.natural_peak = self.tapes = self.writes = 0
        self.budget = None

    def observe(self):
        require(len(self.roots) <= 32, "finite tape inventory")
        total = natural = count = 0
        for identity, tape in self.roots.items():
            require(len(tape.cells) <= 2048, "finite tape extent")
            if identity not in self.base:
                total += len(tape.cells)
                natural += len(tape.cells) if tape.category == "natural" else 0
                count += 1
        self.peak = max(self.peak, total)
        self.natural_peak = max(self.natural_peak, natural)
        self.tapes = max(self.tapes, count)
        require(self.budget is None or total <= self.budget, "backing budget exceeded")

    def start(self, budget=None):
        self.base = set(self.roots)
        self.peak = self.natural_peak = self.tapes = self.writes = 0
        self.budget = budget

    def tape_type(self, original, category):
        census = self

        class Observed(original):
            def __init__(self):
                super().__init__()
                self.category = category
                census.roots[id(self)] = self
                census.observe()

            def write(self, symbol):
                super().write(symbol)
                census.writes += 1
                require(census.writes <= 1000000, "finite write budget")
                census.observe()

        return Observed


@contextmanager
def counted(m):
    census = Census()
    old = [module.Tape for module in (m.cardinality, m.counts, m.stream)]
    try:
        for module, original, category in zip(
            (m.cardinality, m.counts, m.stream),
            old,
            ("natural", "natural", "counter"),
            strict=True,
        ):
            module.Tape = census.tape_type(original, category)
        yield census
    finally:
        for module, original in zip(
            (m.cardinality, m.counts, m.stream), old, strict=True
        ):
            module.Tape = original


def value(count):
    require(count.tape.head == 1, "count head restored")
    cells = count.tape.cells
    end = cells.index(3, 1)
    require(all(bit in (0, 1) for bit in cells[1:end]), "binary count")
    return sum(bit << i for i, bit in enumerate(cells[1:end]))


def saved(counts):
    return [(bytes(count.tape.cells), count.tape.head) for count in counts]


def product_peak(a, b):
    require(a > 0 and b > 0, "positive product domain")
    aa, bb, cc = a.bit_length(), b.bit_length(), (a * b).bit_length()
    trailing = (b & -b).bit_length() - 1
    return aa + bb + cc + 6 + max(0, aa + 2 - trailing)


def product_case(m, a, b, short=False):
    require(1 <= a <= 65535 and 1 <= b <= 65535, "bounded product fixture")
    with counted(m) as census:
        operands = [m.cardinal_counts.Count.literal(n) for n in (a, b)]
        baseline = saved(operands)
        expected = product_peak(a, b)
        census.start(expected - 1 if short else expected)
        result = m.cardinal_counts.Count.product(*operands)
        require(value(result) == a * b, "independent integer product")
        require(saved(operands) == baseline, "borrowed product inputs restored")
        require(census.peak == expected, "exact product backing peak")
        extent = len(result.tape.cells)
        require(extent == (a * b).bit_length() + 2, "canonical result backing")
        result.close()
        require(len(result.tape.cells) == extent, "clear retains backing")
        require(all(c == 4 for c in result.tape.cells[1:]), "clear erases content")
        return [a, b, expected, census.tapes]


def setup(m, q, width, n, spectators, index_bits):
    require(q in (3, 5) and width in (1, 2) and n in (1, 2), "bounded context")
    require(
        len(spectators) == 3 and all(1 <= x <= 5 for x in spectators),
        "bounded spectators",
    )
    require(index_bits in (8, 12, 64, 256), "bounded index encoding")
    modulus = q**width
    arena = m.words.Arena(modulus.bit_length() + 1, capacity=64)
    index = m.words.Arena(index_bits, capacity=64)
    ring = m.words.Ring(arena.literal(modulus))
    columns, depth, parent = (index.literal(x) for x in (1, 0, n))
    geometry = m.Geometry(
        types.SimpleNamespace(dimension=n), index, columns, depth, 0, object()
    )
    counts = [m.cardinal_counts.Count.literal(x) for x in spectators]
    layout = m.layout.Layout(geometry, parent, ring, q, *counts)
    return types.SimpleNamespace(**locals())


def expected_extents(modulus, n, spectators, a, b):
    before, gap, suffix = spectators
    last = a if b is None else b
    result = [before * modulus**a * (gap if a >= n else 1)]
    if b is not None:
        result.append(modulus ** (b - a - 1) * (gap if a < n <= b else 1))
    result.append(suffix * modulus ** (2 * n - last - 1) * (gap if last < n else 1))
    return result


def extent_case(m, q, width, n, spectators, a, b, index_bits=12, short=False):
    require(
        0 <= a < 2 * n and (b is None or a < b < 2 * n), "ordered fixture positions"
    )
    with counted(m) as census:
        case = setup(m, q, width, n, spectators, index_bits)
        positions = [case.index.literal(a)]
        if b is not None:
            positions.append(case.index.literal(b))
        expected = expected_extents(case.modulus, n, spectators, a, b)
        widths = [x.bit_length() for x in expected]
        ss, ww = sum(x + 2 for x in widths), max(widths)
        bound = ss + max(index_bits + 2, 3 * ww + 9)
        borrowed = saved(case.counts)
        census.start(1 if short else bound)
        result = case.layout.extents(*positions)
        require([value(x) for x in result] == expected, "independent extent values")
        require(saved(case.counts) == borrowed, "borrowed extent inputs restored")
        returned = sum(len(x.tape.cells) for x in result)
        require(
            returned == sum(x + 3 for x in widths), "exact returned marginal backing"
        )
        require(
            len(census.roots) == len(case.counts) + len(result),
            "no retained extent scratch",
        )
        peak, natural_peak = census.peak, census.natural_peak
        require(peak <= bound, "all-parameter extent bound")
        row = [q, width, n, list(spectators), a, b, index_bits, peak, bound, returned]
        for count in result:
            count.close()
        case.layout.close()
        case.geometry.close()
        return row, natural_peak


def add_oracle(bits, extents, modulus, coefficient):
    before, middle, suffix = extents
    expected = [0] * len(bits)
    for outer, x, mid, y, tail in itertools.product(
        range(before), range(modulus), range(middle), range(modulus), range(suffix)
    ):
        old = (((outer * modulus + x) * middle + mid) * modulus + y) * suffix + tail
        new_y = (y + coefficient * x) % modulus
        new = (((outer * modulus + x) * middle + mid) * modulus + new_y) * suffix + tail
        expected[new] = bits[old]
    return expected


def action_case(m, coefficient, spectators=(1, 1, 1), a=0, b=1):
    with counted(m) as census:
        case = setup(m, 3, 1, 1, spectators, 12)
        source = m.records.Tape()
        extents = expected_extents(3, 1, spectators, a, b)
        volume = extents[0] * extents[1] * extents[2] * 9
        require(volume <= 144, "bounded complete ADD fibre")
        bits = [((i * 13 + i // 3) % 7) & 1 for i in range(volume)]
        for bit in bits:
            source.append(bit)
        source.rewind()
        original = bytes(source.cells)
        first, second = case.index.literal(b), case.index.literal(a)
        event = types.SimpleNamespace(
            kind="add", first=first, second=second, request=object()
        )
        calls = []

        def prepare(_request):
            calls.append(1)
            require(len(calls) <= 2, "exactly two native coefficient requests")
            return case.arena.literal(coefficient)

        census.start()
        output = m.action(source, event, case.layout, prepare)
        expected = add_oracle(bits, extents, 3, coefficient)
        require(list(output.cells[1:]) == expected, "complete native ADD permutation")
        require(
            bytes(source.cells) == original and source.head == 1,
            "borrowed payload restored",
        )
        require(len(calls) == 2, "both source traversals reached")
        require(len(census.roots) == len(case.counts), "action count scratch released")
        return [coefficient, list(spectators), volume, census.peak]


def rejected(operation, phrase):
    try:
        operation()
    except ValueError as error:
        require(phrase in str(error), "expected rejection reason")
        return
    raise ValueError("control incorrectly accepted")


def digest(rows):
    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


def run():
    with source_modules() as m:
        products = [product_case(m, a, b) for a in range(1, 65) for b in range(1, 65)]
        products += [
            product_case(m, a, b) for a, b in ((257, 256), (1025, 1024), (7, 4096))
        ]
        extents = []
        for n, spectators, index_bits in itertools.product(
            (1, 2), ((1, 1, 1), (2, 3, 5)), (8, 64)
        ):
            for a in range(2 * n):
                extents.append(
                    extent_case(m, 3, 1, n, spectators, a, None, index_bits)[0]
                )
                for b in range(a + 1, 2 * n):
                    extents.append(
                        extent_case(m, 3, 1, n, spectators, a, b, index_bits)[0]
                    )
        extents += [
            extent_case(m, q, w, 2, (2, 3, 5), a, b)[0]
            for q, w in ((3, 2), (5, 1))
            for a, b in ((0, 1), (0, 3), (2, 3))
        ]
        actions = [
            action_case(m, c, spectators)
            for c in range(3)
            for spectators in ((1, 1, 1), (2, 3, 2))
        ]
        rejected(lambda: product_case(m, 3, 5, short=True), "backing budget")
        rejected(
            lambda: extent_case(m, 3, 1, 1, (1, 1, 1), 0, 1, short=True),
            "backing budget",
        )
        rejected(lambda: product_peak(0, 1), "positive product domain")
        narrow = extent_case(m, 3, 1, 1, (1, 1, 1), 0, 1, 8)[0]
        padded = extent_case(m, 3, 1, 1, (1, 1, 1), 0, 1, 256)[0]
        require(
            padded[7] > narrow[7] and padded[9] == narrow[9],
            "index-padding backing control",
        )
        require(padded[7] > narrow[8], "omitted index term is insufficient")
    return {
        "status": "PASS_SELECTED_EXTENT_COUNT_BACKING",
        "products": len(products),
        "product_sha256": digest(products),
        "extents": len(extents),
        "extent_sha256": digest(extents),
        "native_adds": actions,
        "controls": 4,
        "padding": {"narrow": narrow, "wide": padded},
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", action="store_true", help="explicitly regenerate RESULT.json"
    )
    args = parser.parse_args()
    result = run()
    path = PACKAGE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(json.loads(path.read_text()) == result, "exact replay receipt")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
