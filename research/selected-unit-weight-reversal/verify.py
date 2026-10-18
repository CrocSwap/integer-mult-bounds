#!/usr/bin/env python3
"""Run the q=3 macro machine at the unit root's weights and compare with C_n.

The published GL2(F3) controller compiles weights (2, 1). The depth-zero unit
ROOT evaluates to weight 1 at every body coordinate. This run installs that
pair and checks the column map. It does not change kappa.
"""

import hashlib
import inspect
import json
from pathlib import Path
import tarfile
import textwrap

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
INTERCHANGE = ROOT / "research/physical-ordinary-interchange"
ARCHIVE = INTERCHANGE / "inputs/pr2809.tar"
MACHINE = "macro_local_checks.py"
DESTINATION = "inputs/pr2753/check_runtime.py"
Q = 3
N = 2
GAP = 1
BODY = 64
MARKER = (
    "PASS_SELECTED_UNIT_WEIGHT_REVERSAL q=3 n=2 gap=1 body=64 "
    "addresses=15552 reversal=Cn weighted_disagreements=72 no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_SELECTED_UNIT_WEIGHT_REVERSAL " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def column_reversal(address, n=N, modulus=Q, gap=GAP, suffix=1):
    """Swap the two atom blocks and reverse each block. Gap and suffix stay."""
    address, scalar = divmod(address, suffix)
    block = modulus ** n
    address, tail = divmod(address, block)
    address, gap_index = divmod(address, gap)
    outer, head = divmod(address, block)

    def digits(value):
        found = [0] * n
        for index in range(n - 1, -1, -1):
            value, found[index] = divmod(value, modulus)
        return found

    def pack(values):
        packed = 0
        for value in values:
            packed = modulus * packed + value
        return packed

    new_head = list(reversed(digits(tail)))
    new_tail = list(reversed(digits(head)))
    return ((((outer * block + pack(new_head)) * gap + gap_index) * block + pack(new_tail)) * suffix + scalar)


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "certificates/selected-result.json",
        "research/bit2234-stock-threshold/README.md",
        "research/physical-ordinary-interchange/ordinary.py",
        "research/physical-ordinary-interchange/inputs/pr2809.tar",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    ordinary = (INTERCHANGE / "ordinary.py").read_text(encoding="utf-8")
    require("for word in (size, ring.one, depth):" in ordinary, "unit ROOT triple changed")
    require('size, depth = indices.load(plan["body"]), indices.zero()' in ordinary,
            "fitted call no longer forces depth zero")
    with tarfile.open(ARCHIVE, "r:") as tar:
        machine = tar.extractfile(MACHINE).read().decode("utf-8")
        destination = tar.extractfile(DESTINATION).read().decode("utf-8")
    for needle in (
        "value = (2, 1)[finite_word(request.coordinate, 2)]",
        "incoming = model.Incoming(context, indices, (2, 1))",
        "size, depth = indices.input(2), indices.zero()",
        "source, directory, program = Tape(), Tape(), Tape()",
        "counts = [Count.literal(value) for value in (1, 192, 1, gap_size, 1)]",
    ):
        require(needle in machine, "GL2 machine no longer states " + needle)
    require("def destination(address,n,modulus,weights,gap=1,suffix=1,active=None):" in destination,
            "column-map oracle changed")
    return machine


def unit_root_weights():
    import sys
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
    size_count, modulus_count = Count.literal(BODY), Count.literal(Q)

    def forbidden(*_args, **_kwargs):
        raise ValueError("fixture-only word operation during the unit-root read")

    comparisons = []
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
        callback = Callback(ring, indices, program, fields, specifications,
                            binding.ambient, allow_fallback=True, leaf=True)
        try:
            for coordinate_value in range(BODY):
                coordinate = indices.literal(coordinate_value)
                coefficient = callback.weight(coordinate)
                comparisons.append(ring.raw.compare(coefficient, ring.one))
                arena.free(coefficient)
                indices.free(coordinate)
            root_size, root_unit, root_depth = program.root()
            require(callback.raw.compare(root_size, size) == 0, "root size drifted")
            require(ring.raw.compare(root_unit, ring.one) == 0, "root unit drifted")
            require(callback.depth.zero(), "root depth drifted")
            indices.free_many(root_size, root_depth)
            arena.free(root_unit)
        finally:
            callback.close()
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
                "unit-root banks were not erased")
    size_count.close()
    modulus_count.close()
    require(comparisons == [0] * BODY, "a unit-root coordinate was not 1")


def install_unit_weights(module, obj, name):
    source = textwrap.dedent(inspect.getsource(obj)).replace("(2, 1)", "(1, 1)")
    require("(2, 1)" not in source, name + " still names the weighted pair")
    require("(1, 1)" in source, name + " lost the unit pair")
    namespace = {}
    exec(source, module.__dict__, namespace)
    return namespace[name]


def evaluate():
    authenticate()
    unit_root_weights()
    from check_runtime import destination
    block = Q ** N
    columns = block * GAP * block
    reversal = [column_reversal(address) for address in range(columns)]
    require(reversal == [destination(address, N, Q, (1, 1), GAP) for address in range(columns)],
            "unit weights are not the position reversal")
    require(all(destination(destination(address, N, Q, (1, 1), GAP), N, Q, (1, 1), GAP) == address
                for address in range(columns)),
            "unit-weight map is not an involution")
    disagreements = sum(destination(address, N, Q, (2, 1), GAP) != reversal[address] for address in range(columns))
    require(disagreements == 72, "weighted pair disagreement count changed")

    import macro_local_checks as machine
    machine.compile_binding = install_unit_weights(machine, machine.compile_binding, "compile_binding")
    machine.Binding.incoming = install_unit_weights(machine, machine.Binding.incoming, "incoming")
    machine.run = install_unit_weights(machine, machine.run, "run")
    result = machine.run(gap_size=GAP)
    require(result["gap"] == GAP and result["addresses"] == 192 * columns, "machine shape changed")
    require(result["instructions"] == 25415, "unit-weight instruction count changed")
    require(result["residuals"] == {"MOVE": 192, "COPY": 96, "IDLE": 384}, "residual census changed")
    require(result["private_copy_oracles"] == 96, "private COPY census changed")
    return {
        "q": Q,
        "modulus": Q,
        "body": BODY,
        "root": [BODY, 1, 0],
        "unit_coordinates": BODY,
        "machine_n": N,
        "machine_weights": [1, 1],
        "gap": GAP,
        "rows": 192,
        "addresses": result["addresses"],
        "row_columns": columns,
        "reversal_matches": columns,
        "weighted_disagreements": disagreements,
        "instructions": result["instructions"],
        "residuals": {"COPY": 96, "IDLE": 384, "MOVE": 192},
        "private_copy_oracles": 96,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
