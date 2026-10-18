"""Independent integer oracles for encoded selection and template creation."""
from pathlib import Path
import json
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import source
source.activate()
from cardinal_counts import Count
from check_support import no_decode
import encoded
from physical_words import PhysicalArena, PhysicalWord
from scratch_pool import ScratchPool
from session import sealed_constructors
from words import BLANK, RIGHT, need


def decode(count):
    data = count.tape.cells if hasattr(count.tape, "cells") else count.tape.physical.cells
    digits = []
    for bit in data[1:]:
        if bit == RIGHT:
            break
        digits.append(bit)
    return sum(bit << index for index, bit in enumerate(digits))


def run():
    pool = ScratchPool(64)
    arithmetic = roots = 0
    for a in range(24):
        for b in range(1, 24):
            left, right = Count.literal(a), Count.literal(b)
            with no_decode(), sealed_constructors(), pool.install():
                need(encoded.compare(left, right) == ((a > b) - (a < b)), "count order")
                quotient, remainder = encoded.divide(left, right)
                need((decode(quotient), decode(remainder)) == divmod(a, b), "binary long division")
                quotient.close()
                remainder.close()
                if a >= b:
                    difference = encoded.subtract(left, right)
                    need(decode(difference) == a-b, "exact count subtraction")
                    difference.close()
                pool.empty()
            left.close()
            right.close()
            arithmetic += 1
    for value in (1, 2, 63, 64, 311310, 311311, 1000000):
        original = Count.literal(value)
        with no_decode(), sealed_constructors(), pool.install():
            width = encoded.atom_width(original)
            observed = decode(width)
            need((observed-1)**10000 < value**17 <= observed**10000,
                 "exact selected ceiling power")
            width.close()
            pool.empty()
        original.close()
        roots += 1
    selections = []
    profile = encoded.Profile(dimension=2, child_rank=1, row_factor=6)
    for q, value in ((2, 1), (2, 2), (2, 32), (2, 127), (2, 512), (3, 512)):
        original = Count.literal(value)
        with no_decode(), sealed_constructors(), pool.install():
            plan = encoded.select(original, q, profile)
            observed = {key: item if key == "fits" else decode(item) for key, item in plan.items()}
            width = observed["width"]
            cursor, depth = value, 0
            while cursor >= 2:
                cursor //= 2
                depth += 1
            order = (q*q-1)*(q*q-q)
            stock = (6*order*q**(4*(width-1)))**depth
            rows, borrowed = 1, 0
            while rows < stock:
                rows *= q
                borrowed += 1
            need((observed["stock"], observed["depth"], observed["rows"], observed["borrowed"])
                 == (stock, depth, rows, borrowed), "encoded stock and minimal borrowing")
            if 2*borrowed < value:
                need((observed["body"], observed["remainder"])
                     == divmod(value-borrowed, width), "body and remainder")
                need(observed["fits"] == (observed["body"] >= 2), "body fit guard")
            else:
                need(not observed["fits"], "strict borrowing fit guard")
            for key, item in plan.items():
                if key != "fits":
                    item.close()
            pool.empty()
            selections.append(observed)
        original.close()
    templates = []
    def forbidden(*_args, **_kwargs):
        raise ValueError("decoded physical word")
    for value in (1, 2, 8, 65, 2**80+13):
        maximum = Count.literal(value)
        bank = PhysicalArena(4)
        with no_decode(), sealed_constructors(), patch.object(PhysicalWord, "inspect", forbidden):
            bank.prepare(maximum)
            word = bank.load(maximum)
            need(list(word.cells[1:-1]) == [(value >> bit) & 1 for bit in range(value.bit_length()+1)],
                 "exact scanned word template and high zero margin")
            copied = bank.copy(word)
            need(bytes(copied.cells) == bytes(word.cells), "retained Arena operations on physical roles")
            bank.free_many(copied, word)
            bank.erase_owned()
            need(all(all(bit == BLANK for bit in item.cells) for item in (*bank.words, bank.template)),
                 "complete owned numerical erasure")
        maximum.close()
        templates.append(value.bit_length()+1)
    return dict(arithmetic_cases=arithmetic, selected_roots=roots, selections=selections,
                template_bits=templates, peak_setup_leases=pool.peak)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
    print("PASS_ENCODED_ORDINARY_SETUP")
