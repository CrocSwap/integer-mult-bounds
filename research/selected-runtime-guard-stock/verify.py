#!/usr/bin/env python3
"""Exact stock for the current recursive NODE guards, not both old formats."""
import argparse
import importlib
import json
import math
import sys
import tempfile
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "research/selected-bit-recursive-caller/predecessor/"
Q = 9475
W = 28416
SOURCE_DIGEST = "1fb24116c79ad1f5c7c9ff6531c63e7c1d547ebf0326cbbc8e06b0709fe73aa3"
MODULES = {
    "cardinal_counts": "cardinal_counts.py",
    "fresh_rows": "fresh_rows.py",
    **{name: "vendor/" + name + ".py" for name in (
        "bitstream", "cardinality", "counts", "directory", "matrices",
        "oracle", "records", "routes", "stream", "words")},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(root=ROOT):
    raw = (HERE / "SOURCES.json").read_bytes()
    require(sha256(raw).hexdigest() == SOURCE_DIGEST, "source manifest changed")
    manifest = json.loads(raw)
    files = manifest["files"]
    require(len(files) <= 32, "bounded source inventory")
    for row in files:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        require(path.is_file() and not path.is_symlink(), "regular source input")
        require(path.stat().st_size <= 1_000_000, "bounded source file")
        require(sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "source mismatch: " + row["path"])
    return manifest


def depth(width):
    require(type(width) is int and 0 <= width < 2**256, "bounded width")
    for result in range(1024):
        if width < 64:
            return result
        width = 42 * (width // 64)
    raise ValueError("depth budget exceeded")


def reserve(packet, compatibility, levels):
    require(type(packet) is int and 1 <= packet <= 2**32, "packet domain")
    require(type(compatibility) is int and 1 <= compatibility <= 2**16,
            "compatibility domain")
    require(type(levels) is int and 0 <= levels <= 64, "level domain")
    return 1 if levels == 0 else compatibility * packet**levels


def guard_chain(rows, packet, compatibility, levels):
    """Independent integer model of quotient followed by the local Q guard."""
    require(type(rows) is int and 1 <= rows <= 2**4096, "chain rows")
    _ = reserve(packet, compatibility, levels)  # Validate the bounded model parameters.
    for _ in range(levels):
        rows, remainder = divmod(rows, packet)
        if remainder or rows == 0 or rows % compatibility:
            return False
    return True


def arithmetic():
    require(math.lcm(W, 28425) == W * Q == 269241600, "selected lcm")
    require(2**17 * 42**28 < 64**28, "depth rate certificate")
    require(W < 2**15 and Q < 2**14, "packet logarithm constants")
    decisions = 0
    for packet in range(1, 6):
        for compatibility in range(1, 8):
            for levels in range(4):
                stock = reserve(packet, compatibility, levels)
                for rows in range(1, 2 * stock + 2):
                    require(guard_chain(rows, packet, compatibility, levels)
                            == (rows % stock == 0), "exact guard divisor")
                    decisions += 1
    thresholds = [64]
    for _ in range(31):
        thresholds.append(64 * ((thresholds[-1] + 41) // 42))
    for level, boundary in enumerate(thresholds, 1):
        require(depth(boundary) == level and depth(boundary - 1) == level - 1,
                "inverse depth boundary")
    widths = 8192
    table = [0] * widths
    children = 0
    for width in range(64, widths):
        columns = width // 64
        table[width] = 1 + table[42 * columns]
        for child in [rank * columns for rank in range(1, 43)] + [columns // 2]:
            require(table[child] <= table[width] - 1, "child depth")
            children += 1
    return {"divisor_decisions": decisions, "depth_boundaries": len(thresholds),
            "child_depth_checks": children, "widths": widths}


def source_contract(root=ROOT):
    logical = (root / "research/selected-bit-recursive-caller/node.py").read_text()
    physical = (root / "research/selected-bit-physical-caller/macro_machine.py").read_text()
    binding = (root / "research/selected-bit-physical-caller/macro_binding.py").read_text()
    require('stock.divide_small(self.stock_multiple)==0' in logical,
            "logical local compatibility guard")
    require('child_stock=unused,child_before=before' in logical,
            "logical separate child stock")
    require('stock.divide_small(self.binding.stock_multiple) == 0' in physical,
            "physical local compatibility guard")
    require('self.tape("unused")' in physical, "physical child capsule stock")
    require('cutoff, stock_multiple, child_mode = 64, 9475, 0' in binding,
            "selected physical compatibility constant")
    require('def check_stock(self, runtime):\n        pass' in binding,
            "no additional selected residual stock check")
    for filename in ("fresh_rows.py", "cardinal_counts.py"):
        physical_copy = root / "research/selected-bit-physical-caller/inputs/pr2753/predecessor" / filename
        require((root / PREFIX / filename).read_bytes() == physical_copy.read_bytes(),
                "physical/logical shared row implementation")
    return 8


def check_module_locations(root):
    for name, suffix in MODULES.items():
        actual = Path(sys.modules[name].__file__).resolve()
        require(actual == (root / PREFIX / suffix).resolve(), "module binding: " + name)


def literal_case(modules, dimension, atom_width, families, compatibility):
    fresh, counts, words = modules
    low = math.prod(3**dimension - 3**i for i in range(dimension))
    packet = families * low * 3**(dimension**2 * (atom_width - 1))
    arena = words.Arena((3**atom_width).bit_length() + 1)
    modulus = arena.input(3**atom_width)
    ring = words.Ring(modulus)
    context = SimpleNamespace(codes=SimpleNamespace(size=low), dimension=dimension,
                              ring=ring, q=3)
    owned = []
    try:
        current = counts.Count.literal(compatibility * packet**2)
        owned.append(current)
        for _ in range(2):
            current = fresh.quotient(current, context, families)
            owned.append(current)
            check = counts.Count(current)
            try:
                require(check.divide_small(compatibility) == 0, "literal local Q guard")
            finally:
                check.close()
        expected = counts.Count.literal(compatibility)
        owned.append(expected)
        require(current.equals(expected), "literal final quotient")
        rejected = literal_failures(fresh, counts.Count, context, families,
                                    compatibility, packet)
        return {"dimension": dimension, "atom_width": atom_width, "q": 3,
                "families": families, "compatibility": compatibility,
                "depth": 2, "old_to_new_stock_ratio": compatibility,
                "row_bits": (compatibility * packet**2).bit_length(),
                "rejected_controls": rejected}
    finally:
        for value in owned:
            value.close()
        ring.close()
        arena.free(modulus)
        require(not arena.live, "literal probe numerical cleanup")


def literal_failures(fresh, count_type, context, families, compatibility, packet):
    candidates = (packet**2, compatibility * packet,
                  compatibility * packet**2 - 1)
    for rows in candidates:
        owned = [count_type.literal(rows)]
        failed = False
        try:
            for _ in range(2):
                value = fresh.quotient(owned[-1], context, families)
                owned.append(value)
                check = count_type(value)
                try:
                    require(check.divide_small(compatibility) == 0,
                            "literal local Q guard")
                finally:
                    check.close()
        except ValueError as error:
            require(str(error) in (
                "complete fresh family factor", "complete fresh GL low factor",
                "complete fresh high factor", "nonempty unused row quotient",
                "literal local Q guard"), "unexpected literal probe failure: " + str(error))
            failed = True
        finally:
            for value in owned:
                value.close()
        require(failed, "literal insufficient stock was accepted")
    return len(candidates)


def runtime_probes(root=ROOT):
    predecessor = root / PREFIX
    old_path, old_cache = sys.path[:], sys.pycache_prefix
    old_bytecode = sys.dont_write_bytecode
    try:
        with tempfile.TemporaryDirectory(prefix="guard-stock-bytecode-") as cache:
            sys.pycache_prefix = cache
            sys.dont_write_bytecode = True
            sys.path[:0] = [str(predecessor), str(predecessor / "vendor")]
            for name in MODULES:
                _ = importlib.import_module(name)  # Materialize the fixed authenticated closure.
            fresh, counts, words = (sys.modules[name] for name in (
                "fresh_rows", "cardinal_counts", "words"))
            check_module_locations(root)
            modules = (fresh, counts, words)
            return [literal_case(modules, *case) for case in (
                (64, 1, W, Q), (2, 1, 4, 5), (2, 2, 4, 5))]
    finally:
        sys.path[:] = old_path
        sys.pycache_prefix = old_cache
        sys.dont_write_bytecode = old_bytecode


def result():
    _ = authenticate()  # Validation must complete before any predecessor import.
    return {"status": "PASS_RUNTIME_GUARD_STOCK", "arithmetic": arithmetic(),
            "source_checks": source_contract(), "literal_probes": runtime_probes(),
            "scope": "NODE guards only; old dual depth-D format not admitted"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-to", type=Path)
    args = parser.parse_args()
    observed = result()
    encoded = json.dumps(observed, indent=2, sort_keys=True) + "\n"
    if args.emit_to is not None:
        with args.emit_to.open("x", encoding="utf-8") as output:
            require(output.write(encoded) == len(encoded), "complete explicit receipt write")
    else:
        stored = json.loads((HERE / "RESULT.json").read_bytes())
        require(json.dumps(stored, indent=2, sort_keys=True) + "\n" == encoded,
                "required stored receipt mismatch")
    print("PASS_RUNTIME_GUARD_STOCK selected_Q=9475 depth2_factor=9475 "
          "literal_probes=3 rejected_controls=9 no_new_kappa")


if __name__ == "__main__":
    main()
