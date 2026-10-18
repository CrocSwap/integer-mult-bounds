"""Replay the pinned caller with a census of cardinality tape symbols."""
import argparse
import ast
from contextlib import contextmanager
from hashlib import sha256
import importlib
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
MAX_FILES = 45
MAX_SOURCE_BYTES = 400_000
MAX_TRACKED_WRITES = 500_000_000
TAPE_CAP = 100
MAX_FIXTURE_SYMBOLS_PER_TAPE = 2048


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(root):
    """Check the proof's routine inventory against the authenticated syntax."""
    table = json.loads((HERE / "ROOTS.json").read_text())
    owned = table["owned_roots"]
    require(len(owned) == 19, "bounded count source groups")
    total = 0
    routines = 0
    for filename, limits in owned.items():
        require(len(limits) <= 8, "bounded routines per source group")
        tree = ast.parse((root / filename).read_text())
        functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                functions.update(node.name + "." + method.name for method in node.body
                                 if isinstance(method, ast.FunctionDef))
        require(set(limits) <= functions, "named count-owning routine: " + filename)
        for limit in limits.values():
            require(type(limit) is int and 1 <= limit <= 10, "positive root inventory bound")
            total += limit
            routines += 1
    require(total == table["owned_total"] == 92 and table["borrowed_roots"] == 6
            and table["participating_total"] == 98 and table["rounded_tape_cap"] == TAPE_CAP,
            "count-root arithmetic")
    return {"owned_roots": total, "borrowed_roots": 6, "tape_cap": TAPE_CAP,
            "routines": routines, "groups": len(owned)}


def unpack(destination, archive=None, manifest=None):
    manifest = manifest or json.loads((HERE / "SNAPSHOT.json").read_text())
    require(manifest["commit"] == "a53fdf4bcbe33c6732f0bec1badc8c023380f9d1", "caller pin")
    entries = manifest["files"]
    require(len(entries) == MAX_FILES, "snapshot file coverage")
    expected = {item["path"]: item for item in entries}
    require(len(expected) == MAX_FILES, "unique snapshot paths")
    observed = set()
    total = 0
    with tarfile.open(archive or HERE / "SOURCE.tar.gz", "r:gz") as source:
        for member in source:
            require(len(observed) < MAX_FILES, "bounded snapshot members")
            path = PurePosixPath(member.name)
            require(member.isfile() and str(path) == member.name and not path.is_absolute()
                    and ".." not in path.parts and member.name in expected,
                    "regular declared snapshot path")
            require(member.name not in observed, "duplicate snapshot member")
            total += member.size
            require(0 <= member.size <= MAX_SOURCE_BYTES and total <= MAX_SOURCE_BYTES,
                    "bounded snapshot bytes")
            data = source.extractfile(member).read()
            item = expected[member.name]
            require(len(data) == item["bytes"] and sha256(data).hexdigest() == item["sha256"],
                    "snapshot source digest: " + member.name)
            target = destination / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            require(target.write_bytes(data) == len(data), "complete source export")
            observed.add(member.name)
    require(observed == set(expected), "complete snapshot export")


@contextmanager
def sources():
    with tempfile.TemporaryDirectory(prefix="selected-count-storage-") as temporary:
        root = Path(temporary)
        unpack(root)
        original_path = sys.path[:]
        original_modules = set(sys.modules)
        source_names = {path.stem for path in root.rglob("*.py")} - {"verify"}
        require(not source_names.intersection(original_modules), "source module collision")
        sys.path[:0] = [str(root), str(root / "vendor")]
        try:
            yield root
        finally:
            sys.path[:] = original_path
            for name in set(sys.modules) - original_modules:
                module_file = getattr(sys.modules[name], "__file__", None)
                if module_file and Path(module_file).is_relative_to(root):
                    del sys.modules[name]


class Census:
    """Track occupied count symbols; LEFT markers are outside this category."""
    def __init__(self, limit=None):
        self.live = set()
        self.symbols = self.peak_symbols = self.peak_tapes = self.peak_single = 0
        self.writes = self.audits = 0
        self.limit = limit

    def audit(self):
        actual = sum(sum(value != 4 for value in tape.cells[1:]) for tape in self.live)
        require(actual == self.symbols, "independent count cell census")
        require(all(tape.occupied > 0 for tape in self.live), "nonempty live count tapes")
        self.audits += 1

    @contextmanager
    def install(self):
        records = importlib.import_module("records")
        modules = [importlib.import_module(name) for name in ("cardinality", "counts", "stream")]
        state = self

        class ObservedTape(records.Tape):
            def __init__(self):
                super().__init__()
                self.occupied = 0

            def write(self, symbol):
                previous = self.cells[self.head] if self.head < len(self.cells) else 4
                super().write(symbol)
                change = int(symbol != 4) - int(previous != 4)
                state.writes += 1
                if state.writes > MAX_TRACKED_WRITES:
                    raise ValueError("bounded fixture count writes")
                if change:
                    self.occupied += change
                    state.symbols += change
                    if self.occupied == 0:
                        state.live.remove(self)
                    elif self.occupied == 1 and change > 0:
                        state.live.add(self)
                    if change > 0:
                        require(len(state.live) <= TAPE_CAP
                                and self.occupied <= MAX_FIXTURE_SYMBOLS_PER_TAPE,
                                "bounded observed count inventory")
                        if state.symbols > state.peak_symbols:
                            state.peak_symbols = state.symbols
                        if len(state.live) > state.peak_tapes:
                            state.peak_tapes = len(state.live)
                        if self.occupied > state.peak_single:
                            state.peak_single = self.occupied
                        if state.limit is not None:
                            require(state.symbols <= state.limit, "count content budget exceeded")
                if state.writes % 32768 == 0:
                    state.audit()

        previous = [module.Tape for module in modules]
        for module in modules:
            module.Tape = ObservedTape
        try:
            yield
            self.audit()
        finally:
            for module, tape_type in zip(modules, previous):
                module.Tape = tape_type

    def result(self):
        return {"peak_symbols": self.peak_symbols, "peak_tapes": self.peak_tapes,
                "peak_single": self.peak_single, "count_writes": self.writes}


def padding_fixture(digits):
    Count = importlib.import_module("cardinal_counts").Count
    Counter = importlib.import_module("stream").Counter
    census = Census()
    with census.install():
        value = Count.literal((1 << digits) - 1)
        padded = value.marginal()
        counter = Counter(padded)
        census.audit()
        require(census.peak_single == digits + 2, "marginal and counter transient padding")
        require(counter.tape.cells[1:digits + 2] == bytes([1] * digits + [3]),
                "canonical copied countdown")
        counter.close()
        padded.close()
        value.close()
        require(census.symbols == 0 and not census.live, "count fixture erasure")
    return {"digits": digits, **census.result()}


def destination(address, atoms, modulus, weights, gap, active=None):
    address, tail = divmod(address, modulus ** atoms)
    address, intervening = divmod(address, gap)
    outer, head = divmod(address, modulus ** atoms)
    h = [head // modulus ** (atoms - 1 - i) % modulus for i in range(atoms)]
    t = [tail // modulus ** (atoms - 1 - i) % modulus for i in range(atoms)]
    changed_h, changed_t = h[:], t[:]
    for i in range(atoms) if active is None else active:
        changed_h[i] = weights[i] * t[atoms - 1 - i] % modulus
        changed_t[atoms - 1 - i] = pow(weights[i], -1, modulus) * h[i] % modulus
    new_head = new_tail = 0
    for a, b in zip(changed_h, changed_t):
        new_head = modulus * new_head + a
        new_tail = modulus * new_tail + b
    return ((outer * modulus ** atoms + new_head) * gap + intervening) * modulus ** atoms + new_tail


def node_fixture():
    model = importlib.import_module("model")
    words = importlib.import_module("words")
    Count = importlib.import_module("cardinal_counts").Count
    Context = importlib.import_module("directory").Context
    Node = importlib.import_module("node").Node
    Tape = importlib.import_module("records").Tape
    census = Census()
    with census.install():
        catalogue = model.Catalogue()
        topology = model.Topology(catalogue)
        arena, indices = words.Arena(3), words.Arena(8)
        modulus = arena.input(3)
        ring = words.Ring(modulus)
        context = Context(ring, catalogue.codes)
        size, depth = indices.input(2), indices.input(0)
        incoming = model.Incoming(context, indices, (2, 1))
        consumer = model.Consumer(context, indices, object(), size, depth, catalogue, incoming)
        evaluator = Node(context, indices, object(), size, depth, topology, consumer, incoming)
        old = Tape()
        parameters = [Count.literal(value) for value in (1, 192, 1, 1, 1)]
        volume = 192 * 81
        source = Tape()
        original = bytes(((i * 13) ^ (i >> 3) ^ (i >> 7) ^ 0x53) & 1 for i in range(volume))
        for value in original:
            source.append(value)
        source.rewind()
        baseline = census.symbols
        output = evaluator.run(source, old, *parameters)
        census.audit()
        require(census.symbols == baseline and len(census.live) == 6,
                "all owned node count work erased")
        observed = bytes(output.cells[1:])
        require(len(observed) == volume, "complete node output extent")
        for row in range(192):
            for address in range(81):
                target = row * 81 + destination(address, 2, 3, (2, 1), 1)
                require(observed[target] == original[row * 81 + address], "independent node bit endpoint")
        require(bytes(source.cells[1:]) == original and source.head == output.head == old.head == 1,
                "borrowed payload and head restoration")
        require(consumer.calls == {"MOVE": 192, "COPY": 96, "IDLE": 384}
                and consumer.children["enter"] == consumer.children["return"] == 5712,
                "complete local, idle and leaf coverage")
        result = {"volume": volume, "B": max(volume.bit_length(), indices.bits),
                  "borrowed_count_symbols": baseline, "output_sha256": sha256(observed).hexdigest(),
                  "children": dict(consumer.children), "residuals": dict(consumer.calls), **census.result()}
        source.clear()
        output.clear()
        incoming.close()
        for value in parameters:
            value.close()
        context.close()
        require(census.symbols == 0 and not census.live, "all count content erased")
        ring.close()
        arena.free(modulus)
        indices.free_many(size, depth)
        require(not arena.live and not indices.live, "numerical fixture cleanup")
    require(result["peak_tapes"] <= TAPE_CAP and result["peak_single"] <= result["B"] + 2,
            "source-derived count storage envelope")
    return result


def peel_fixture():
    model = importlib.import_module("model")
    words = importlib.import_module("words")
    Count = importlib.import_module("cardinal_counts").Count
    Context = importlib.import_module("directory").Context
    Tape = importlib.import_module("records").Tape
    peel = importlib.import_module("peel")
    census = Census()
    with census.install():
        arena, indices = words.Arena(3), words.Arena(8)
        modulus = arena.input(3)
        ring = words.Ring(modulus)
        context = Context(ring, model.Catalogue().codes)
        size, depth = indices.input(3), indices.input(0)
        incoming = model.Incoming(context, indices, (1, 2, 2))
        old, source = Tape(), Tape()
        parameters = [Count.literal(1) for _ in range(5)]
        original = bytes(((i * 7) ^ (i >> 2) ^ 0x35) & 1 for i in range(729))
        for value in original:
            source.append(value)
        source.rewind()
        baseline = census.symbols
        output = peel.run(source, context, indices, size, depth, object(), old,
                          *parameters, incoming)
        census.audit()
        require(census.symbols == baseline and len(census.live) == 6, "peel count erasure")
        observed = bytes(output.cells[1:])
        require(len(observed) == 729, "complete peel extent")
        for address in range(729):
            target = destination(address, 3, 3, (1, 2, 2), 1, active=(2,))
            require(observed[target] == original[address], "original-offset peel endpoint")
        require(bytes(source.cells[1:]) == original and source.head == output.head == old.head == 1,
                "peel borrowed input and head restoration")
        result = {"volume": 729, "B": 10, **census.result()}
        source.clear()
        output.clear()
        incoming.close()
        for value in parameters:
            value.close()
        context.close()
        require(census.symbols == 0 and not census.live, "all peel count content erased")
        ring.close()
        arena.free(modulus)
        indices.free_many(size, depth)
        require(not arena.live and not indices.live, "peel numerical cleanup")
    require(result["peak_tapes"] <= TAPE_CAP and result["peak_single"] <= result["B"] + 2,
            "peel count storage envelope")
    return result


def controls():
    Count = importlib.import_module("cardinal_counts").Count
    cases = []
    census = Census(limit=9)
    try:
        with census.install():
            Count.literal(255)
    except ValueError as error:
        require(str(error) == "count content budget exceeded", "specific underbudget rejection")
        cases.append("literal-constructor-temporary-budget")
    else:
        raise ValueError("underbudget count fixture accepted")
    census = Census()
    with census.install():
        value = Count.literal(7)
        value.tape.cells[1] = 4
        try:
            census.audit()
        except ValueError as error:
            require(str(error) == "independent count cell census", "specific observer bypass rejection")
            cases.append("direct-cell-observer-bypass")
        else:
            raise ValueError("observer bypass accepted")
        value.tape.cells[1] = 1
        value.close()
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    with sources() as root:
        result = {"inventory": inventory(root),
                  "padding": [padding_fixture(bits) for bits in (1, 2, 8, 64, 257, 1025)],
                  "controls": controls(), "peel": peel_fixture()}
        if not args.quick:
            result["node"] = node_fixture()
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        if args.quick:
            expected.pop("node")
        require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
                "exact typed count-storage receipt")
        print("PASS_SELECTED_NODE_COUNT_STORAGE" + (" quick" if args.quick else " full"))


if __name__ == "__main__":
    main()
