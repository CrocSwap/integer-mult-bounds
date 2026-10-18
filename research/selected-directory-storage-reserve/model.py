"""Exact directory extent and a numerical large-q storage certificate.

The serialized field formula is credited to PR2590. New material: its
uniform numerical payload allowance under the declared caller premises.
ywz65 with OpenAI Codex assistance. Apache-2.0.
"""
from math import prod

REQUEST_CAP = 28278
CELL_SHIFT = 130


def need(ok, message):
    if not ok:
        raise ValueError(message)


def integer(value, minimum, name):
    need(type(value) is int and value >= minimum, name)


def code_bits(q, dimension, requests):
    integer(q, 3, "integer radix at least three")
    integer(dimension, 1, "positive dimension")
    integer(requests, 1, "positive vocabulary")
    need(dimension <= 64, "dimension at most 64")
    order = prod(q**dimension-q**k for k in range(dimension))
    return (2*requests*order-1).bit_length()


def field_cells(q, dimension, width, requests):
    integer(width, 1, "positive width")
    bits = code_bits(q, dimension, requests)
    word_bits = (q**width).bit_length()+1
    return bits + dimension*dimension*(word_bits+1)+2


def directory_cells(q, dimension, width, frozen, old_positions, requests):
    integer(frozen, 0, "nonnegative frozen depth")
    integer(old_positions, 1, "positive old physical multiplicity")
    field = field_cells(q, dimension, width, requests)
    high_count = q**(dimension*dimension*(width-1))
    return 1+old_positions*high_count*(frozen+1)*field


def reserve(q, dimension, width, frozen, requests, body_dimension=1,
            fibre_bits=None, compiled_bits=None):
    """Certificate arithmetic, not a runtime allocator or primality test.

    It never constructs the huge high cube or its cardinality. The leading
    LEFT cell is absorbed using CH>=1; the returned bound holds for every C.
    """
    integer(q, 1 << 80, "large-q threshold")
    integer(width, 1, "positive width")
    integer(frozen, 0, "nonnegative frozen depth")
    integer(body_dimension, 1, "positive complete body dimension")
    integer(requests, 1, "positive vocabulary")
    need(requests <= REQUEST_CAP, "frozen vocabulary cap")
    need(17*(frozen+1) <= 20051*width, "root-derived depth envelope")
    bits = code_bits(q, dimension, requests)
    if compiled_bits is not None:
        need(type(compiled_bits) is int and compiled_bits == bits,
             "canonical minimal compiled code width")
    minimum_fibre = q**(2*body_dimension*width)
    if fibre_bits is not None:
        integer(fibre_bits, 1, "positive fibre extent")
        need(fibre_bits >= minimum_fibre, "complete body fibre")
    per_record = 1+(frozen+1)*field_cells(q, dimension, width, requests)
    # Finite cross-check of each returned certificate. The all-input argument
    # is the uniform inequality chain in PROOF.md, not this assertion alone.
    need((per_record << CELL_SHIFT) < minimum_fibre,
         "strict numerical directory allowance")
    return {"q_bits": q.bit_length(), "code_bits": bits,
            "word_bits": (q**width).bit_length()+1,
            "field_cells": field_cells(q, dimension, width, requests),
            "per_prefix_upper_cells": per_record,
            "directory_cell_shift": CELL_SHIFT,
            "four_bit_encoding_shift": CELL_SHIFT-2,
            "five_directory_cell_shift": CELL_SHIFT-3,
            "five_four_bit_encoding_shift": CELL_SHIFT-5}
