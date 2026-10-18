#!/usr/bin/env python3
"""Execute B1's depth-zero unit ROOT at one odd prime and record what it does.

The callback is the production selected-coefficient parser. This does not run
the macro machine, invent a padded-row reversal, or change kappa.
"""

import ast
import hashlib
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
INTERCHANGE = ROOT / "research/physical-ordinary-interchange"
ARCHIVE = INTERCHANGE / "inputs/pr2809.tar"
CONTROLLER = "inputs/pr2753/predecessor/vendor/controller.py"
SELECTED_CHECK = "macro_selected_checks.py"
Q = 3
MODULUS = 3
BODY = 64
MARKER = (
    "PASS_SELECTED_ODD_PRIME_UNIT_ROOT q=3 modulus=3 body=64 "
    "unit_coordinates=64 root=64,1,0 no_step reverse_unreachable "
    "pointwise_restoration=false no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_SELECTED_ODD_PRIME_UNIT_ROOT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "certificates/selected-result.json",
        "research/bit2234-stock-threshold/README.md",
        "research/physical-ordinary-interchange/ordinary.py",
        "research/physical-ordinary-interchange/check_root.py",
        "research/physical-ordinary-interchange/check_engine.py",
        "research/physical-ordinary-interchange/check_binary.py",
        "research/physical-ordinary-interchange/inputs/pr2809.tar",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    ordinary = (INTERCHANGE / "ordinary.py").read_text(encoding="utf-8")
    root_check = (INTERCHANGE / "check_root.py").read_text(encoding="utf-8")
    engine = (INTERCHANGE / "check_engine.py").read_text(encoding="utf-8")
    binary = (INTERCHANGE / "check_binary.py").read_text(encoding="utf-8")
    for needle in (
        "for word in (size, ring.one, depth):",
        "size, depth = indices.load(plan[\"body\"]), indices.zero()",
        "borrowed_count(rows)",
    ):
        require(needle in ordinary, "ordinary call site no longer states " + needle)
    require("coordinate = indices.zero()" in root_check, "odd-prime root check lost its single coordinate")
    require("return Ordinary(2, binding, topology, (program,), capacity=128, fixture_index_floor=64)" in engine,
            "pointwise engine is no longer the q=2 fixture")
    require("lambda: dict(fits=False)" in binary and "for q in (2, 3, 5):" in binary,
            "odd-prime binary cases no longer skip the reversed callee")
    with tarfile.open(ARCHIVE, "r:") as tar:
        controller = tar.extractfile(CONTROLLER).read()
        selected = tar.extractfile(SELECTED_CHECK).read().decode("utf-8")
    require("(256, 2, 1)" in selected, "selected extended root triple changed")
    require("changed = bytes(1 - bit for bit in reversed(initial))" in selected,
            "selected odd-prime check no longer writes its own child body")
    return controller


def level_zero_test(test):
    return (isinstance(test, ast.Call) and isinstance(test.func, ast.Attribute)
            and test.func.attr == "zero" and not test.args
            and isinstance(test.func.value, ast.Name) and test.func.value.id == "level")


def zero_level_facts(source):
    """The depth-zero arm returns the root unit and does not read reverse."""
    if isinstance(source, str):
        source = source.encode("utf-8")
    weight = next((node for node in ast.walk(ast.parse(source))
                   if isinstance(node, ast.FunctionDef) and node.name == "weight"), None)
    require(weight is not None, "controller weight function missing")
    require([item.arg for item in weight.args.args] == ["self", "index"],
            "weight acquired a row or depth argument")
    branches = [node for node in ast.walk(weight) if isinstance(node, ast.If) and level_zero_test(node.test)]
    require(len(branches) == 1, "expected one level.zero arm in weight")
    branch = branches[0]
    names = set()
    attributes = set()
    for statement in branch.body:
        for node in ast.walk(statement):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                attributes.add(node.attr)
    require(isinstance(branch.body[-1], ast.Continue), "depth-zero arm falls through")
    require("reverse" not in names and "step" not in names, "depth-zero arm reads reverse or a step")
    require("root_unit" in attributes, "depth-zero arm does not return the root unit")
    reverse_sites = [node for node in ast.walk(weight)
                     if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "reverse"]
    require(len(reverse_sites) == 1, "expected one reverse flag outside the depth-zero arm")
    require(all(site not in ast.walk(statement) for statement in branch.body for site in reverse_sites),
            "reverse flag sits inside the depth-zero arm")
    return {"arguments": ["self", "index"], "returns": "root_unit", "reverse_unreachable": True}


def evaluate(controller):
    facts = zero_level_facts(controller)
    sys.path.insert(0, str(INTERCHANGE))
    import source
    source.activate()
    from unittest.mock import patch
    from cardinal_counts import Count
    from catalogue import Catalogue, Specifications
    from check_support import no_decode
    from controller import Callback
    from macro_binding import SelectedBinding
    from ordinary import unit_program
    from physical_words import PhysicalArena, PhysicalWord
    from records import Fields
    from scratch_pool import ScratchPool
    from session import sealed_constructors
    from words import BLANK, Ring, Word

    catalogue = Catalogue(Q)
    specifications = Specifications(catalogue)
    binding = SelectedBinding(specifications)
    arena, indices = PhysicalArena(128), PhysicalArena(128)
    pool = ScratchPool(64)
    size_count, modulus_count = Count.literal(BODY), Count.literal(MODULUS)

    def forbidden(*_args, **_kwargs):
        raise ValueError("fixture-only word operation during the odd-prime unit root")

    comparisons = []
    rejected = None
    with no_decode(), sealed_constructors(), pool.install(), \
            patch.object(Word, "__init__", forbidden), \
            patch.object(PhysicalWord, "inspect", forbidden):
        arena.prepare(modulus_count)
        indices.prepare(size_count)
        modulus = arena.load(modulus_count)
        size, depth = indices.load(size_count), indices.zero()
        ring = Ring(modulus)
        program = unit_program(indices, ring, size, depth, catalogue.codes.bits)
        fields = Fields(indices, arena, catalogue.codes.bits)
        saved = bytes(program.tape.physical.cells)
        callback = Callback(ring, indices, program, fields, specifications,
                            binding.ambient, allow_fallback=True, leaf=True)
        try:
            for coordinate_value in range(BODY):
                coordinate = indices.literal(coordinate_value)
                coefficient = callback.weight(coordinate)
                comparisons.append(ring.raw.compare(coefficient, ring.one))
                arena.free(coefficient)
                indices.free(coordinate)
            coordinate = indices.literal(BODY)
            try:
                callback.weight(coordinate)
            except ValueError as error:
                rejected = str(error)
            else:
                fail("coordinate outside the body was accepted")
            finally:
                indices.free(coordinate)
            root_size, root_unit, root_depth = program.root()
            require(callback.raw.compare(root_size, size) == 0, "root size is not the 64-atom body")
            require(ring.raw.compare(root_unit, ring.one) == 0, "root unit is not the ring one")
            require(callback.raw.compare(root_depth, depth) == 0 and callback.depth.zero(),
                    "root depth is not zero")
            indices.free_many(root_size, root_depth)
            arena.free(root_unit)
        finally:
            callback.close()
        require(bytes(program.tape.physical.cells) == saved and program.tape.head == 1,
                "weight evaluation rewrote the ROOT record")
        program.tape.clear()
        fields.tape.clear()
        ring.close()
        arena.free(modulus)
        indices.free_many(size, depth)
        pool.empty()
        arena.erase_owned()
        indices.erase_owned()
        require(all(all(bit == BLANK for bit in word.cells)
                    for bank in (arena, indices) for word in (*bank.words, bank.template)),
                "odd-prime root numerical erasure")
    size_count.close()
    modulus_count.close()
    require(comparisons == [0] * BODY, "a body coordinate was not the ring unit")
    require(rejected == "requested generated coordinate", "out-of-range rejection changed: " + str(rejected))
    require(facts["reverse_unreachable"], "depth-zero reverse fact was dropped")
    return {
        "q": Q,
        "modulus": MODULUS,
        "body": BODY,
        "depth": 0,
        "root": [BODY, 1, 0],
        "unit_coordinates": BODY,
        "out_of_range_rejected": True,
        "step_records": 0,
        "weight_arguments": facts["arguments"],
        "reverse_unreachable": True,
        "selected_extended_root": [256, 2, 1],
        "pointwise_restoration": False,
        "no_new_kappa": True,
        "controls_rejected": 1,
        "peak_scratch": pool.peak,
    }


def main():
    controller = authenticate()
    observed = evaluate(controller)
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
