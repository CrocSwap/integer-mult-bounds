"""The selected coefficient parser accepts the encoded unweighted ROOT."""
from pathlib import Path
import json
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source
source.activate()
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
from words import BLANK, Ring, Word, need


def run():
    catalogue = Catalogue(3)
    specifications = Specifications(catalogue)
    binding = SelectedBinding(specifications)
    results = []
    for size_value, modulus_value in ((64, 3), (128, 3), (256, 9)):
        arena, indices = PhysicalArena(128), PhysicalArena(128)
        pool = ScratchPool(64)
        size_count, modulus_count = Count.literal(size_value), Count.literal(modulus_value)
        def forbidden(*_args, **_kwargs):
            raise ValueError("fixture-only word operation in selected ROOT setup")
        with no_decode(), sealed_constructors(), pool.install(), \
                patch.object(Word, "__init__", forbidden), patch.object(PhysicalWord, "inspect", forbidden):
            arena.prepare(modulus_count)
            indices.prepare(size_count)
            modulus, size, depth = arena.load(modulus_count), indices.load(size_count), indices.zero()
            ring = Ring(modulus)
            program = unit_program(indices, ring, size, depth, catalogue.codes.bits)
            fields = Fields(indices, arena, catalogue.codes.bits)
            saved = bytes(program.tape.physical.cells)
            callback = Callback(ring, indices, program, fields, specifications,
                                binding.ambient, allow_fallback=True, leaf=True)
            coordinate = indices.zero()
            try:
                coefficient = callback.weight(coordinate)
                need(ring.raw.compare(coefficient, ring.one) == 0,
                     "actual selected unweighted incoming root coefficient")
                need(callback.raw.compare(callback.final_size, size) == 0 and callback.depth.zero(),
                     "actual selected root width and zero history")
                arena.free(coefficient)
            finally:
                callback.close()
                indices.free(coordinate)
            need(bytes(program.tape.physical.cells) == saved and program.tape.head == 1,
                 "selected evaluation preserves the emitted ROOT")
            program.tape.clear()
            fields.tape.clear()
            ring.close()
            arena.free(modulus)
            indices.free_many(size, depth)
            pool.empty()
            arena.erase_owned()
            indices.erase_owned()
            need(all(all(bit == BLANK for bit in word.cells)
                     for bank in (arena, indices) for word in (*bank.words, bank.template)),
                 "selected root numerical erasure")
        size_count.close()
        modulus_count.close()
        results.append(dict(size=size_value, modulus=modulus_value, coefficient=1,
                            peak_scratch=pool.peak))
    return results


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
    print("PASS_SELECTED_UNIT_ROOT_SETUP")
