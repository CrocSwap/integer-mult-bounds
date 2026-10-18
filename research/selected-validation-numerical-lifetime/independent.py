#!/usr/bin/env python3
"""Independent integer/allocation model of pre-run numerical lifetimes.

This file imports no retained implementation.  Native integers determine the
arithmetic branches; explicit owned handles implement the source's allocation
order.  It is a finite check of the accompanying written invariant, not a formal
proof or an execution of the serialized program/directory implementation.
"""

import json
from dataclasses import dataclass
from math import gcd


def require(test, message):
    if not test:
        raise RuntimeError(message)


@dataclass
class Handle:
    serial: int
    value: int
    name: str


class Ledger:
    def __init__(self, bits, borrowed=0):
        self.bits = bits
        self.live = {}
        self.serial = 0
        self.peak = 0
        self.peak_event = None
        self.borrowed = [self.new(0, "borrowed") for _ in range(borrowed)]
        self.baseline = len(self.live)

    def new(self, value, name):
        require(0 <= value < 1 << self.bits, "word extent")
        word = Handle(self.serial, value, name)
        self.serial += 1
        self.live[word.serial] = word
        if len(self.live) > self.peak:
            self.peak = len(self.live)
            self.peak_event = name
        return word

    def release(self, *words):
        for word in words:
            require(self.live.pop(word.serial, None) is word, "unique live ownership")

    def copy(self, word, name="copy"):
        return self.new(word.value, name)

    def restore(self):
        require(set(self.live) == {w.serial for w in self.borrowed}, "entry ownership restored")


class IntegerArithmetic:
    def __init__(self, ledger):
        self.l = ledger

    def add(self, a, b, name="raw.add"):
        return self.l.new(a.value + b.value, name)

    def subtract(self, a, b, name="raw.subtract"):
        return self.l.new(a.value - b.value, name)

    def divide(self, a, b):
        require(0 < b.value < 1 << (self.l.bits - 1), "divisor margin")
        scan = self.l.copy(a, "divide.scan")
        quotient = self.l.new(0, "divide.quotient")
        remainder = self.l.new(0, "divide.remainder")
        for bit in reversed(range(self.l.bits)):
            shifted = self.l.new(2 * remainder.value + ((scan.value >> bit) & 1), "divide.shift")
            self.l.release(remainder)
            if shifted.value >= b.value:
                remainder = self.subtract(shifted, b, "divide.difference")
                self.l.release(shifted)
                quotient.value |= 1 << bit
            else:
                remainder = shifted
        self.l.release(scan)
        require((quotient.value, remainder.value) == divmod(a.value, b.value), "integer division")
        return quotient, remainder

    def small(self, a, multiplier):
        require(0 <= multiplier <= 128, "finite multiplier")
        result = self.l.new(0, "small.result")
        for bit in reversed(range(multiplier.bit_length())):
            doubled = self.add(result, result, "small.double")
            self.l.release(result)
            if (multiplier >> bit) & 1:
                result = self.add(doubled, a, "small.add")
                self.l.release(doubled)
            else:
                result = doubled
        return result


class ModularArithmetic(IntegerArithmetic):
    def __init__(self, ledger, modulus, one):
        super().__init__(ledger)
        self.modulus, self.one = modulus, one

    def modadd(self, a, b):
        result = self.add(a, b, "modadd.sum")
        if result.value >= self.modulus.value:
            reduced = self.subtract(result, self.modulus, "modadd.reduce")
            self.l.release(result)
            return reduced
        return result

    def modsubtract(self, a, b):
        if a.value >= b.value:
            return self.subtract(a, b, "modsubtract.direct")
        larger = self.add(a, self.modulus, "modsubtract.larger")
        result = self.subtract(larger, b, "modsubtract.result")
        self.l.release(larger)
        return result

    def multiply(self, a, b):
        if not a.value or not b.value:
            return self.l.new(0, "multiply.zero")
        if a.value == 1:
            return self.l.copy(b, "multiply.unit")
        if b.value == 1:
            return self.l.copy(a, "multiply.unit")
        scan, result = self.l.copy(b, "multiply.scan"), self.l.new(0, "multiply.result")
        for bit in reversed(range(self.l.bits)):
            doubled = self.modadd(result, result)
            self.l.release(result)
            if (scan.value >> bit) & 1:
                result = self.modadd(doubled, a)
                self.l.release(doubled)
            else:
                result = doubled
        self.l.release(scan)
        return result

    def inverse(self, a):
        r0, r1 = self.l.copy(self.modulus), self.l.copy(a)
        t0, t1 = self.l.new(0, "inverse.t0"), self.l.copy(self.one)
        while r1.value:
            quotient, r2 = self.divide(r0, r1)
            if quotient.value >= self.modulus.value:
                reduced = self.subtract(quotient, self.modulus)
                self.l.release(quotient)
                quotient = reduced
            product = self.multiply(quotient, t1)
            t2 = self.modsubtract(t0, product)
            self.l.release(quotient, product, r0, t0)
            r0, r1, t0, t1 = r1, r2, t1, t2
        unit = r0.value == 1
        self.l.release(r0, r1, t1)
        if unit:
            require(t0.value == pow(a.value, -1, self.modulus.value), "integer inverse")
            return t0
        self.l.release(t0)
        return None


def seek(ledger, arithmetic, slot):
    """A scan at zero has two handles; a positive scan reaches three."""
    remaining, one = ledger.copy(slot, "seek.remaining"), ledger.new(1, "seek.one")
    while remaining.value:
        after = arithmetic.subtract(remaining, one, "seek.after")
        ledger.release(remaining)
        remaining = after
    ledger.release(remaining, one)


def validation_indices(root, events, borrowed=0, caller=8):
    """Each event is (kind, rank, half); root and all extents are native data."""
    ledger = Ledger(root.bit_length() + 1, borrowed)
    raw = IntegerArithmetic(ledger)
    outer = [ledger.new(0, "consumer.retained") for _ in range(caller)]
    one, sixty_four, two = (ledger.new(v, "callback.constant") for v in (1, 64, 2))
    root_size = ledger.new(root, "program.root_size")
    depth = ledger.new(len(events), "program.depth")
    current, count = ledger.copy(root_size), ledger.new(0, "program.count")
    for kind, rank, half in events:
        require(kind in (0, 1, 2) and 1 <= rank <= 42, "selected step")
        require(half in (0, 1) and (not half or kind == 2), "unit-only half")
        level = raw.add(count, one, "program.level")
        seek(ledger, raw, level)
        parent = ledger.new(current.value, "program.parent")
        factor = parent.value // 64
        child_value = rank * factor if kind == 0 else factor // 2 if half else factor
        require(0 < child_value < parent.value, "proper child")
        child = ledger.new(child_value, "program.child")
        f, remainder = raw.divide(parent, sixty_four)
        ledger.release(remainder)
        if kind == 0:
            expected = raw.small(f, rank)
        elif half:
            expected, remainder = raw.divide(f, two)
            ledger.release(remainder)
        else:
            expected = ledger.copy(f, "program.expected")
        require(expected.value == child.value, "child equality")
        ledger.release(expected)
        seek(ledger, raw, count)
        ledger.release(parent, f, current, count)
        current, count = child, level
    ledger.release(count)
    require(64 <= current.value < 128, "first internal width")
    after = raw.add(depth, one, "program.after")
    seek(ledger, raw, after)
    seek(ledger, raw, depth)
    seek(ledger, raw, after)
    ledger.release(after)
    require(len(ledger.live) - ledger.baseline == caller + 6, "six retained callback indices")
    ledger.release(root_size, depth, current, one, sixty_four, two)
    require(len(ledger.live) - ledger.baseline == caller, "caller boundary resident count")
    ledger.release(*outer)
    ledger.restore()
    return ledger.peak - ledger.baseline


def validation_residues(q, exponent, unit, borrowed=0):
    modulus_value = q ** exponent
    require(exponent >= 1 and gcd(unit, modulus_value) == 1, "unit prime-power fixture")
    ledger = Ledger(modulus_value.bit_length() + 1, borrowed)
    modulus, one = ledger.new(modulus_value, "entry.modulus"), ledger.new(1, "entry.one")
    entry = len(ledger.live)
    arithmetic = ModularArithmetic(ledger, modulus, one)
    divisor = ledger.new(q, "context.q")
    cap, remainder = arithmetic.divide(modulus, divisor)
    require(remainder.value == 0 and cap.value > 0, "high cap")
    ledger.release(remainder)
    test = ledger.copy(cap, "context.test")
    while test.value > 1:
        quotient, remainder = arithmetic.divide(test, divisor)
        require(remainder.value == 0, "prime-power reduction")
        ledger.release(test, remainder)
        test = quotient
    ledger.release(test, divisor)
    root_unit = ledger.new(unit, "program.root_unit")
    inverse = arithmetic.inverse(root_unit)
    require(inverse is not None, "root unit")
    ledger.release(inverse)
    require(len(ledger.live) == entry + 2, "two retained callback residues")
    ledger.release(root_unit, cap, modulus, one)
    ledger.restore()
    return ledger.peak - entry


def closed_formula(events):
    if not events:
        return 18
    return 23 if any(half for _kind, _rank, half in events) else 22


def run_checks():
    index_cases = 0
    observed = set()
    # Backward construction produces actual legal extents for every legal final
    # width, all three step types, and half steps in every position up to depth8.
    for final in range(64, 128):
        sequences = [()]
        for depth in range(1, 9):
            sequences.append(((2, 1, 0),) * depth)
            sequences.append(((1, 42, 0),) * depth)
            for half_position in range(depth):
                sequences.append(tuple((2, 1, int(i == half_position)) for i in range(depth)))
        for events in sequences:
            root = final
            for _kind, _rank, half in reversed(events):
                root *= 128 if half else 64
            peak = validation_indices(root, events, borrowed=3)
            require(peak == closed_formula(events), "index lifetime formula")
            observed.add(peak)
            index_cases += 1
    # Cover the good-rank times_small branches for all42 allowed ranks; keep
    # exactly those one-step extents ending in the selected internal interval.
    for rank in range(1, 43):
        for factor in range(1, 128):
            if not 64 <= rank * factor < 128:
                continue
            for remainder in (0, 1, 63):
                peak = validation_indices(64 * factor + remainder, ((0, rank, 0),))
                require(peak == 22, "good-rank branch")
                index_cases += 1
    residue_cases = 0
    residue_peak = 0
    for q in (2, 3, 5, 7, 11):
        for exponent in range(1, 4):
            modulus = q ** exponent
            for unit in range(1, modulus):
                if gcd(unit, modulus) != 1:
                    continue
                peak = validation_residues(q, exponent, unit, borrowed=5)
                require(peak <= 12, "residue lifetime bound")
                residue_peak = max(residue_peak, peak)
                residue_cases += 1
    require(observed == {18, 22, 23}, "all index classes attained")
    require(validation_residues(5, 1, 2) == residue_peak == 12, "residue sharp fixture")
    return {
        "checker_kind": "independent integer and explicit ownership event model",
        "index_cases": index_cases,
        "index_extra_peaks": sorted(observed),
        "residue_cases": residue_cases,
        "callback_residue_extra_peak": residue_peak,
        "selected_whole_initialization_residue_bound": 4096,
        "depth_domain": "0 through8; one half step at every possible position; unhalved unit/pair chains",
        "width_domain": "all final widths64 through127; canonical root extents constructed backward",
        "residue_domain": "q in[2,3,5,7,11], exponent1 through3, every root unit",
        "proof_status": "finite independent check; all-parameter written derivation in INDEPENDENT.md; no kernel proof",
    }


if __name__ == "__main__":
    print(json.dumps(run_checks(), indent=2, sort_keys=True))
