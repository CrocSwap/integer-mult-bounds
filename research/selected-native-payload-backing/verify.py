"""Exact retained payload arrays of source-pinned native primitives."""
import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import sys
import types
import weakref

PACKAGE = Path(__file__).resolve().parent
MODULES = ("words", "records", "stream", "cardinality", "bitstream", "linear_sign")
EXPORTS = {"sources/" + name + ".py" for name in MODULES} | {
    "sources/PR2697-NOTICE.md", "sources/PR2753-README.md",
    "sources/PR2882-PROOF.md", "sources/PR2566-PROOF.md",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(package=PACKAGE):
    exports = json.loads((package / "SOURCES.json").read_text())["exports"]
    require(len(exports) == len(EXPORTS), "complete source export inventory")
    require({row["export"] for row in exports} == EXPORTS, "source export names")
    for row in exports:
        path = package / row["export"]
        require(path.is_file() and not path.is_symlink(), "regular source export")
        payload = path.read_bytes()
        blob = b"blob " + str(len(payload)).encode() + b"\0" + payload
        require(hashlib.sha256(payload).hexdigest() == row["sha256"],
                "source SHA256 mismatch: " + row["export"])
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                "source Git blob mismatch: " + row["export"])
    return len(exports)


class Observer:
    """Weak references observe source lifetimes without retaining scratch."""
    def __init__(self):
        self.references = []
        self.peak = 0
        self.witness = []
        self.cleared_retained = False

    def sample(self):
        live = [tape for ref in self.references if (tape := ref()) is not None]
        sizes = sorted(len(tape.cells) for tape in live)
        total = sum(sizes)
        if total > self.peak:
            self.peak, self.witness = total, sizes
        return sizes

    def tape_class(self, original):
        observer = self

        class ObservedTape(original):
            def __init__(self):
                super().__init__()
                code = sys._getframe(1).f_code
                filename = Path(code.co_filename).name
                self.payload = (filename in ("bitstream.py", "linear_sign.py")
                                or filename == "stream.py" and code.co_name == "add_pass")
                if self.payload:
                    observer.references.append(weakref.ref(self))
                    observer.sample()

            def write(self, symbol):
                super().write(symbol)
                if self.payload:
                    observer.sample()

            def clear(self):
                super().clear()
                if self.payload:
                    observer.cleared_retained |= len(self.cells) > 1
                    observer.sample()

        return ObservedTape


@contextmanager
def sources(observer):
    authenticate()
    require(not any(name in sys.modules for name in MODULES), "source module preloaded")
    loaded = {}
    try:
        for name in MODULES:
            path = PACKAGE / "sources" / (name + ".py")
            module = types.ModuleType(name)
            module.__file__ = str(path)
            sys.modules[name] = loaded[name] = module
            # Authenticated source, bypassing source-adjacent bytecode caches.
            exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
            if name == "records":
                module.Tape = observer.tape_class(module.Tape)
        yield loaded
    finally:
        for name in loaded:
            del sys.modules[name]


def payload_peak(kind, q, w, volume):
    require(kind in ("add", "swap", "sign", "linear_sign"), "known primitive")
    require(all(type(x) is int and x > 0 for x in (q, w, volume)), "positive exact parameters")
    require(q >= 3 and q % 2 == 1, "odd radix at least three")
    atoms = 2 if kind in ("add", "swap") else 1
    require(volume % (q ** (w * atoms)) == 0, "complete primitive fibre")
    if kind == "add":
        return 2 * volume + 3
    if kind == "linear_sign":
        return volume + 1
    if kind == "swap":
        return 2 * volume + q * q + 1 if w == 1 else 3 * volume + q * q + 2
    return 3 * volume + 4 if w == 1 else 3 * volume + q + 2


def composed_bound(n, fibre, source, directory, prefix, private):
    values = (n, fibre, source, directory, prefix, private)
    require(all(type(x) is int and x > 0 for x in values), "positive exact composition inputs")
    require(source >= n * fibre + 1 and prefix >= 2, "complete source and prefix")
    require(directory >= 1 + n * (prefix - 1), "complete prefix directory")
    require(private >= fibre + 1, "private allowance includes the returned result")
    structural = source + (2 * n + 1) * fibre + 4 + directory + 2 * prefix + max(prefix, fibre)
    interior = source + 2 * n * fibre + 3 + directory + 2 * prefix + private
    return max(structural, interior)


def margin(modules, value):
    words = modules["words"]
    arena = words.Arena(max(2, value.bit_length() + 1), capacity=64)
    return arena, arena.input(value)


def expected_origin(kind, q, w, before, middle, suffix, coefficient):
    modulus = q ** w
    if kind in ("sign", "linear_sign"):
        return [(u * modulus + (-x) % modulus) * suffix + s
                for u in range(before) for x in range(modulus) for s in range(suffix)]
    # The ADD layout is [before][source x][middle][target y][suffix].
    return [((((u * modulus + (y if kind == "swap" else x)) * middle + g) * modulus
              + (x if kind == "swap" else (y - coefficient * x) % modulus)) * suffix + s)
            for u in range(before) for x in range(modulus) for g in range(middle)
            for y in range(modulus) for s in range(suffix)]


def execute_case(kind, q, w, before, middle, suffix, plane=None):
    require(kind in ("add", "swap", "sign", "linear_sign"), "fixture primitive")
    require(type(q) is int and q in (3, 5), "fixture radix")
    require(type(w) is int and 1 <= w <= 3, "fixture digit bound")
    require(all(type(x) is int and 1 <= x <= 2 for x in (before, middle, suffix)),
            "fixture spectator bound")
    observer = Observer()
    with sources(observer) as modules:
        words, records = modules["words"], modules["records"]
        modulus = q ** w
        arena, modulus_word = margin(modules, modulus)
        ring = words.Ring(modulus_word)
        extents = [margin(modules, value) for value in (before, middle, suffix)]
        pre, gap, tail = [word for _, word in extents]
        coefficient = modulus - 1
        volume = before * modulus * suffix
        if kind in ("add", "swap"):
            volume *= modulus * middle
        require(volume <= 5000, "bounded fixture volume")
        origin = expected_origin(kind, q, w, before, middle, suffix, coefficient)
        require(len(origin) == volume, "complete origin oracle")
        data = [((i * 17 + i // 3) % 7) % 2 if plane is None else (i >> plane) & 1
                for i in range(volume)]
        source = records.Tape()
        for bit in data:
            source.append(bit)
        source.rewind()
        saved = bytes(source.cells)
        if kind == "add":
            output, _traffic = modules["stream"].add_pass(
                source, ring, pre, gap, tail, lambda: arena.literal(coefficient))
        elif kind == "swap":
            output = modules["bitstream"].atom_swap(source, ring, q, pre, gap, tail)
        else:
            module = modules["linear_sign" if kind == "linear_sign" else "bitstream"]
            output = module.sign_address(source, ring, q, pre, tail)
        require(list(output.cells[1:]) == [data[i] for i in origin], "complete payload permutation")
        require(bytes(source.cells) == saved and source.head == output.head == 1,
                "borrowed source and both heads restored")
        require(output is not source and len(output.cells) == volume + 1, "fresh complete output")
        expected = payload_peak(kind, q, w, volume)
        require(observer.peak == expected, "exact private payload peak")
        require(observer.sample() == [volume + 1], "only owned result remains at return")
        require(arena.live == {modulus_word.slot, ring.one.slot}, "numerical temporaries released")
        for (owner, word), value in zip(extents, (before, middle, suffix)):
            require(word.head == 1 and word.inspect() == value, "extent restored")
            owner.free(word)
        ring.close()
        arena.free(modulus_word)
        return {"kind": kind, "q": q, "w": w, "before": before, "middle": middle,
                "suffix": suffix, "volume": volume, "peak": expected,
                "witness_sizes": observer.witness, "cleared_retained": observer.cleared_retained}


def run():
    exports = authenticate()
    cases = []
    for kind in ("add", "swap", "sign", "linear_sign"):
        for q, w in ((3, 1), (3, 2), (3, 3), (5, 1), (5, 2)):
            for before, middle, suffix in ((1, 1, 1), (2, 1, 1), (1, 2, 2)):
                cases.append(execute_case(kind, q, w, before, middle, suffix))
    # Complete origin-bit bases in these small macro domains, not random samples.
    origin_planes = 0
    for kind in ("add", "swap", "sign", "linear_sign"):
        volume = 9 if kind in ("sign", "linear_sign") else 81
        for plane in range((volume - 1).bit_length()):
            execute_case(kind, 3, 2, 1, 1, 1, plane)
            origin_planes += 1
    require(any(row["cleared_retained"] for row in cases), "cleared backing witnessed")
    return {"status": "PASS_NATIVE_PAYLOAD_BACKING", "exports": exports,
            "fixtures": len(cases), "origin_bit_planes": origin_planes, "cases": cases,
            "scope": "Payload bytearray lengths only; counters and numerical words excluded. No supplier or kappa claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt, refusing overwrite")
    args = parser.parse_args()
    result = run()
    if args.write:
        with args.write.open("x") as output:
            output.write(json.dumps(result, indent=2) + "\n")
    else:
        stored = json.loads((PACKAGE / "RESULT.json").read_text())
        require(json.dumps(result, sort_keys=True) == json.dumps(stored, sort_keys=True),
                "receipt differs from source execution")
    print(json.dumps({k: v for k, v in result.items() if k != "cases"}, sort_keys=True))


if __name__ == "__main__":
    main()
