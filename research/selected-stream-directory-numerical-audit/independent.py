#!/usr/bin/env python3
"""Separate allocation-event oracle and rejecting-path witnesses.

This script does not import verify.py. It executes pinned source bytes without
bytecode caches, and compares literal allocations/frees with a plain-integer
lifetime model. This is a finite executable check, not a formal proof.
"""
from hashlib import sha256
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace


BASE = Path(__file__).resolve().parent
HASHES = {
    "words": "5c37f57708ba3131bdcb03139f9dbc29886bee44569c09cbba51b68f75acd7f9",
    "records": "0c9c4b23e998597fb877bb1a29da69ac869b68262abe635b162b4dba9c69b372",
    "stream": "c7dc7da5b00f27016982ada4c0416f8328568b00df16d97012f33d4b372d79b5",
    "cardinality": "505d5e560c5a507e6184edcc19a87cf1fed243eb34a5cb21fbe1e4fe017e7f22",
    "counts": "00b476dbda0e8cc99886bf794439e1cb9e775f435f599a3557e99321fe084069",
    "directory": "4270e370b2bfe38ef73aadcd97d1b3496b56bd582115d74331eb9e5ceb90bec7",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load_sources():
    for name, expected in HASHES.items():
        path = BASE / "vendor" / (name + ".py")
        data = path.read_bytes()
        require(sha256(data).hexdigest() == expected, "frozen source hash: " + name)
        module = ModuleType(name)
        module.__file__ = str(path)
        sys.modules[name] = module
        exec(compile(data, str(path), "exec"), module.__dict__)


load_sources()
from words import Arena, Ring, ZERO, ONE, RIGHT, BLANK
from records import Tape, append_finite, append_word, WORD_END, RECORD_END
from counts import Count
from stream import add_pass
from directory import produce


class ObservedArena(Arena):
    def __init__(self, bits):
        super().__init__(bits)
        self.active = False

    def begin(self):
        self.baseline = set(self.live)
        self.borrowed = {s: (bytes(self.words[s].cells), self.words[s].head)
                         for s in self.baseline}
        self.events = []
        self.peak = 0
        self.freed_borrowed = False
        self.active = True

    def event(self, delta):
        if self.active:
            self.events.append(delta)
            self.peak = max(self.peak, len(self.live - self.baseline))

    def zero(self):
        word = super().zero()
        self.event(1)
        return word

    def free(self, word):
        if self.active and word.slot in self.baseline:
            self.freed_borrowed = True
        super().free(word)
        self.event(-1)

    def restored(self):
        return (self.live == self.baseline and not self.freed_borrowed
                and all((bytes(self.words[s].cells), self.words[s].head) == state
                        for s, state in self.borrowed.items()))


class Life:
    """Independent, value-only allocation model: no Word or Tape operations."""
    def __init__(self):
        self.events = []
        self.live = self.peak = 0

    def new(self, value=0):
        self.events.append(1)
        self.live += 1
        self.peak = max(self.peak, self.live)
        return value

    def drop(self, *values):
        for _ in values:
            self.events.append(-1)
            self.live -= 1
            require(self.live >= 0, "model balanced ownership")

    def modular_add(self, a, b, modulus):
        total = self.new(a + b)
        if total >= modulus:
            result = self.new(total - modulus)
            self.drop(total)
            return result
        return total

    def multiply(self, a, b, modulus):
        if a == 0 or b == 0:
            return self.new(0)
        if a == 1 or b == 1:
            return self.new(a * b)
        scan, result = self.new(b), self.new(0)
        for bit in range(modulus.bit_length(), -1, -1):
            doubled = self.modular_add(result, result, modulus)
            self.drop(result)
            if (b >> bit) & 1:
                result = self.modular_add(doubled, a, modulus)
                self.drop(doubled)
            else:
                result = doubled
        self.drop(scan)
        require(result == a * b % modulus, "integer multiplication oracle")
        return result

    def stream(self, modulus, coefficients):
        for c in coefficients:
            coefficient, x = self.new(c), self.new(0)
            for x in range(modulus):
                offset = self.multiply(coefficient, x, modulus)
                leading = self.new(modulus - offset)
                self.drop(offset, leading)
            self.drop(x, coefficient)
        require(self.live == 0, "stream model final ownership")

    def divmod(self, numerator, denominator, bits):
        scan, quotient, remainder = self.new(numerator), self.new(0), self.new(0)
        for bit in reversed(range(bits)):
            shifted = self.new(2 * remainder + ((numerator >> bit) & 1))
            self.drop(remainder)
            if shifted >= denominator:
                remainder = self.new(shifted - denominator)
                self.drop(shifted)
            else:
                remainder = shifted
        self.drop(scan)
        return quotient, remainder

    def directory(self, modulus, q, dimension, old_fields, old_count):
        for _ in range(dimension * dimension):
            divisor, power = self.new(q), self.new(modulus)
            while power > 1:
                quotient, remainder = self.divmod(power, divisor, modulus.bit_length() + 1)
                self.drop(power, remainder)
                power //= q
            self.drop(divisor, power)
        for _ in range(old_count):
            for _ in range(old_fields * dimension * dimension):
                self.drop(self.new())
            digits = [self.new() for _ in range(dimension * dimension)]
            self.drop(*digits)
        require(self.live == 0, "directory model final ownership")


def ring_fixture(modulus):
    arena = ObservedArena(modulus.bit_length() + 1)
    ring = Ring(arena.input(modulus))
    arena.input(modulus - 1)  # unrelated borrowed resident, in common baseline
    index = ObservedArena(5)
    index.input(7)
    return arena, ring, index


def tape_fixture(bits):
    tape = Tape()
    for bit in bits:
        tape.append(bit)
    tape.rewind()
    return tape


def extent_fixture(value=1):
    plain = Count.literal(value)
    marginal = plain.marginal()
    plain.close()
    return marginal


def tape_state(tape):
    return bytes(tape.cells), tape.head


def stream_case(modulus, coefficients, bits=None, expect_success=True):
    arena, ring, index = ring_fixture(modulus)
    extents = [extent_fixture() for _ in range(3)]
    source = tape_fixture([0] * (modulus * modulus) if bits is None else bits)
    sources = [(source, tape_state(source))] + [(x.tape, tape_state(x.tape)) for x in extents]
    cursor = iter(coefficients)

    def callback():
        require(arena.live == arena.baseline, "no stream-owned Word during callback")
        return arena.input(next(cursor))

    arena.begin()
    index.begin()
    try:
        out, _ = add_pass(source, ring, *extents, callback)
    except ValueError as error:
        require(not expect_success, "unexpected stream rejection: " + str(error))
        return arena, str(error)
    require(expect_success, "expected stream rejection")
    require(arena.restored() and index.restored(), "stream entry residents restored")
    require(not index.events, "stream makes no index allocations")
    require(all(tape_state(tape) == state for tape, state in sources), "borrowed tapes restored")
    model = Life()
    model.stream(modulus, coefficients)
    require(arena.events == model.events, "literal/model stream allocation event equality")
    require(arena.peak == model.peak, "literal/model stream peak equality")
    require(arena.peak == (4 if max(coefficients) <= 1 else 6), "sharp stream classification")
    return arena, list(out.cells[1:])


def directory_case(q, modulus, dimension, old_fields, old_count, malformed=False):
    arena, ring, index = ring_fixture(modulus)
    cap = arena.input(modulus // q)
    context = SimpleNamespace(ring=ring, arena=arena, raw=ring.raw, q=q,
                              dimension=dimension, cap=cap,
                              codes=SimpleNamespace(bits=1, limit=1))
    old = Tape()
    for _ in range(old_count * old_fields):
        append_finite(old, 0, 1)
        for _ in range(dimension * dimension):
            if malformed:
                old.append(ZERO)
                old.append(WORD_END)
            else:
                word = arena.input(0)
                append_word(old, word)
                arena.free(word)
        old.append(RECORD_END)
    old.rewind()
    fields, count = Count.literal(old_fields), Count.literal(old_count)
    borrowed = [(x, tape_state(x)) for x in (old, fields.tape, count.tape)]
    arena.begin()
    index.begin()
    try:
        output, expected = produce(old, fields, count, 0, context)
    except ValueError as error:
        require(malformed, "unexpected directory rejection: " + str(error))
        return arena, str(error)
    require(not malformed, "expected malformed directory rejection")
    require(arena.restored() and index.restored(), "directory entry residents restored")
    require(not index.events, "directory makes no index allocations")
    require(all(tape_state(tape) == state for tape, state in borrowed), "directory borrowed tapes restored")
    model = Life()
    model.directory(modulus, q, dimension, old_fields, old_count)
    require(arena.events == model.events, "literal/model directory allocation event equality")
    require(arena.peak == model.peak == max(6, dimension * dimension), "sharp directory bound")
    require(output.head == expected.tape.head == 1, "output head restoration")
    expected.close()
    return arena, model


def callback_composition():
    results = []
    for residue_peak, index_peak in ((1, 0), (5, 2), (7, 4), (13, 1)):
        arena, ring, index = ring_fixture(3)
        extents = [extent_fixture() for _ in range(3)]
        source = tape_fixture([0] * 9)
        calls = []

        def callback():
            require(arena.live == arena.baseline and index.live == index.baseline,
                    "common numerical baseline at both callback entries")
            residues = [arena.input(2) for _ in range(residue_peak)]
            indices = [index.input(0) for _ in range(index_peak)]
            arena.free_many(*residues[1:])
            index.free_many(*indices)
            calls.append(True)
            return residues[0]

        arena.begin()
        index.begin()
        add_pass(source, ring, *extents, callback)
        require(len(calls) == 2, "two completed callback invocations")
        require(arena.peak == max(residue_peak, 6) and index.peak == index_peak,
                "max, not sum, callback composition")
        require(arena.restored() and index.restored(), "callback contract restoration")
        results.append([residue_peak, index_peak, arena.peak, index.peak])
    return results


def excess_lifetime_control():
    """A value-preserving extra temporary must fail the event oracle."""
    original = Ring.multiply

    def extra_word(self, a, b):
        temporary = self.arena.zero()
        try:
            return original(self, a, b)
        finally:
            self.arena.free(temporary)

    Ring.multiply = extra_word
    try:
        try:
            stream_case(3, (2, 2))
        except AssertionError as error:
            require(str(error) == "literal/model stream allocation event equality",
                    "extra-temporary control failed for the intended reason")
            return "rejected extra restored multiplication temporary"
        raise AssertionError("allocation event oracle accepted an extra temporary")
    finally:
        Ring.multiply = original


def main():
    cases = 0
    for modulus in range(2, 17):
        for coefficient in range(modulus):
            stream_case(modulus, (coefficient, coefficient))
            cases += 1
    directory_cases = [(2, 2, 1, 0, 1), (2, 4, 1, 1, 1),
                       (3, 3, 2, 1, 2), (3, 9, 2, 0, 1), (2, 2, 3, 1, 2)]
    for case in directory_cases:
        directory_case(*case)
    selected = Life()
    selected.directory(3, 3, 64, 0, 1)
    require(selected.peak == 4096, "selected-dimension symbolic peak")
    bad_coefficient, c_error = stream_case(3, (3,), expect_success=False)
    require(len(bad_coefficient.live - bad_coefficient.baseline) == 1,
            "invalid coefficient leaks its returned Word")
    short_input, s_error = stream_case(3, (2,), bits=[], expect_success=False)
    require(len(short_input.live - short_input.baseline) == 4,
            "short payload leaves coefficient/x/offset/leading live")
    bad_word, w_error = directory_case(2, 4, 1, 1, 1, malformed=True)
    require(len(bad_word.live - bad_word.baseline) == 1,
            "read_word rejection leaks its in-progress result")
    mismatch_witness = None
    for position in range(9):
        bits = [int(i == position) for i in range(9)]
        _, same = stream_case(3, (1, 1), bits=bits)
        _, different = stream_case(3, (1, 2), bits=bits)
        if same != different:
            mismatch_witness = {"input_one_position": position,
                                "equal_coefficients_output": same,
                                "unequal_coefficients_output": different}
            break
    require(mismatch_witness is not None, "coefficient equality is a semantic premise")
    print(json.dumps({
        "status": "PASS_INDEPENDENT_STREAM_DIRECTORY no_new_kappa",
        "stream_cases": cases,
        "stream_domain": "all 0 <= c < M, 2 <= M <= 16; before=middle=suffix=1; zero payload",
        "directory_cases_q_M_d_fields_count": directory_cases,
        "selected_d64_lifetime_model_peak": selected.peak,
        "callback_cases_R_I_actual_residues_actual_indices": callback_composition(),
        "event_oracle_negative_control": excess_lifetime_control(),
        "failure_witnesses": {"invalid_coefficient": [c_error, 1],
                              "short_payload": [s_error, 4],
                              "malformed_old_word": [w_error, 1]},
        "different_callback_values_accepted_witness": mismatch_witness,
        "proof_level": "finite exact source execution and independent lifetime model; no kernel proof",
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
