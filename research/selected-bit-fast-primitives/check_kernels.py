"""Complete-field affine oracles for the literal high-field primitives."""
from pathlib import Path
import json
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_sources
stage_sources.activate()
from cardinal_counts import Count
from check_support import no_decode
import kernels
from physical_words import PhysicalArena, PhysicalWord
from provenance import Provenance
from records import Tape
from scratch_pool import ScratchPool
from session import sealed_constructors
from words import BLANK, Ring, Word, need


def body(tape):
    physical = getattr(tape, "physical", tape)
    return bytes(physical.cells[1:]).rstrip(bytes([BLANK]))


def run():
    result = []
    for modulus_value in (3, 5, 9, 25):
        bank, pool = PhysicalArena(64), ScratchPool(64)
        maximum = Count.literal(modulus_value)
        bank.prepare(maximum)
        modulus = bank.load(maximum)
        ring = Ring(modulus)
        before, suffix = Count.literal(2), Count.literal(3)
        length = 6*modulus_value
        source = Tape()
        for address in range(length):
            source.append((address*11 ^ address//3 ^ 5) & 1)
        source.rewind()
        initial = body(source)
        observer = Provenance(length)
        observer.mark(source)
        def forbidden(*_args, **_kwargs):
            raise ValueError("fixture-only word operation")
        with no_decode(), sealed_constructors(), pool.install(), observer.installed(), \
                patch.object(Word, "__init__", forbidden), patch.object(PhysicalWord, "inspect", forbidden):
            operations = (("double", 2), ("half", pow(2,-1,modulus_value)), ("negate", -1))
            for name, coefficient in operations:
                output = (kernels.negated(source, ring, 3, before, suffix) if name == "negate" else
                          kernels.doubled(source, ring, before, suffix, pool.acquire, name == "half"))
                expected, masks = bytearray(length), [0]*length
                for address, bit in enumerate(initial):
                    block, tail = divmod(address, 3)
                    prefix, value = divmod(block, modulus_value)
                    target = (prefix*modulus_value+(coefficient*value)%modulus_value)*3+tail
                    expected[target], masks[target] = bit, 1 << address
                need(body(output) == expected and observer.masks(output.physical, length) == tuple(masks),
                     "complete pure high scaling endpoint")
                output.clear()
                pool.empty()
                result.append(dict(modulus=modulus_value, operation=name, columns=length))
            for amount in (-4, -1, 1, 4):
                output = kernels.translated(source, ring, 3, before, suffix, amount)
                expected, masks = bytearray(length), [0]*length
                for address, bit in enumerate(initial):
                    block, tail = divmod(address, 3)
                    prefix, value = divmod(block, modulus_value)
                    target = (prefix*modulus_value+(value+amount)%modulus_value)*3+tail
                    expected[target], masks[target] = bit, 1 << address
                need(body(output) == expected and observer.masks(output.physical, length) == tuple(masks),
                     "complete bounded high carry endpoint")
                output.clear()
                pool.empty()
                result.append(dict(modulus=modulus_value, operation=amount, columns=length))
            need(body(source) == initial and source.head == 1, "borrowed primitive input preserved")
        ring.close()
        bank.free(modulus)
        bank.erase_owned()
        source.clear()
        for count in (maximum, before, suffix):
            count.close()
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
    print("PASS_HIGH_AFFINE_KERNELS")
