"""Stream Gaussian phases with at most one coefficient half in scratch.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
The affine/compact composition follows Jose Manuel's retained PR2250 code.
"""
from pathlib import Path
import sys
SOURCE = Path(__file__).resolve().parents[1] / "selected-complex-compact-adapters"
sys.path.insert(0, str(SOURCE))
from streams import Tape, need, copy, digit_permutation, flip_digit
from compact import Compact, execute
from monomial import tensor_phase, binary_word


def phase_pass(source, layout, recipe, f, K, rho, coefficient_bits, inverse=False):
    need(coefficient_bits >= 2 and layout.record_bits % (2 * coefficient_bits) == 0,
         "Gaussian record extent")
    need(len(source.data) == layout.records * layout.record_bits, "complete record rectangle")
    source.rewind()
    out, real = Tape(source.meter), Tape(source.meter)
    def emit(tape, negative):
        if not negative:
            copy(tape, out, coefficient_bits)
        else:
            carry = 1
            for _ in range(coefficient_bits):
                value = 1 - tape.read(1)[0] + carry
                out.write(bytes((value & 1,)))
                carry = value >> 1
    for index in range(layout.records):
        phase = tensor_phase(recipe, layout.decode(index), f, K, rho)
        if inverse:
            phase = -phase % 4
        source.meter.control_evaluations += 1
        for _ in range(layout.record_bits // (2 * coefficient_bits)):
            if phase % 2 == 0:
                emit(source, phase == 2)
                emit(source, phase == 2)
            else:
                copy(source, real, coefficient_bits)
                emit(source, phase == 1)
                real.rewind()
                emit(real, phase == 3)
                real.finish(); real.erase()
    source.finish(); source.erase(); out.rewind()
    need(not real.data and real.head == 0, "phase scratch not retired")
    return out


def execute_monomial(source, layout, recipe, f, K, G, rho, coefficient_bits, inverse=False):
    """Use the unchanged affine word and compact operations with this phase pass."""
    need(f >= 1, "positive tensor width")
    word = binary_word(recipe)
    if not inverse:
        source = phase_pass(source, layout, recipe, f, K, rho, coefficient_bits)
    for kind, i, k in reversed(word) if inverse else word:
        target = "v" + str(i)
        control = None if kind == "flip" else "v" + str(k)
        if f > 1:
            source = execute(source, layout, Compact(f-1, K, G, rho, control, target,
                             False if control is None else k > i))
        elif control is None:
            source = flip_digit(source, layout.bits, layout.position(target, rho), layout.record_bits)
        else:
            a, b = layout.position(control, rho), layout.position(target, rho)
            mapping = (0, 1, 3, 2) if a < b else (0, 3, 2, 1)
            source = digit_permutation(source, layout.bits, min(a,b), max(a,b), layout.record_bits, mapping)
    if inverse:
        source = phase_pass(source, layout, recipe, f, K, rho, coefficient_bits, True)
    return source
