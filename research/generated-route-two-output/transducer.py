"""Two-pass bounded-state low-digit and dyadic-carry production.

The streaming core never assembles an input integer. The convenience adapters
and the independent oracle in check.py may do so. This is a finite-register
controller specification, not an executed literal tape instruction graph.
Prepared for Jerry Chen / CubeJerry with OpenAI assistance. Apache-2.0.
"""
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Callable, Iterable, Sequence


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass
class Observer:
    """Unbounded diagnostic counters, external to finite controller state."""
    first_rows: int = 0
    second_rows: int = 0
    flush_rows: int = 0
    input_symbols: int = 0
    output_symbols: int = 0
    quotient_updates: int = 0
    comparison_updates: int = 0
    largest_signed_state: int = 0


@dataclass(frozen=True)
class Column:
    """Fixed coefficients sum a_i*x_i divided by D=2**s."""
    numerators: tuple[int, ...]
    denominator_exponent: int
    lower: int = field(init=False)
    upper: int = field(init=False)
    positive: int = field(init=False)
    thresholds: tuple[int, ...] = field(init=False)
    inverse_residues: tuple[int, ...] = field(init=False)

    def __post_init__(self) -> None:
        need(1 <= len(self.numerators) <= 2, 'one or two input channels required')
        need(self.denominator_exponent >= 0, 'nonnegative denominator exponent')
        lo = sum(min(x, 0) for x in self.numerators)
        hi = sum(max(x, 0) for x in self.numerators)
        upper = max(0, hi - 1)
        d = 1 << self.denominator_exponent
        inv = tuple(pow(r, -1, d) if r % 2 else 0 for r in range(d)) if d > 1 else (0,)
        object.__setattr__(self, 'lower', lo)
        object.__setattr__(self, 'positive', hi)
        object.__setattr__(self, 'upper', upper)
        object.__setattr__(self, 'thresholds', tuple(range(lo + 1, upper + 1)))
        object.__setattr__(self, 'inverse_residues', inv)

    @property
    def denominator(self) -> int:
        return 1 << self.denominator_exponent

    @property
    def carry_bounds(self) -> tuple[int, int]:
        return self.lower - self.denominator + 1, self.upper

    def state_bits(self) -> int:
        """Sufficient explicit product-state encoding, not a minimality claim."""
        total = 0
        for j in self.thresholds:
            lo, hi = self.lower - max(j, 0), self.positive - min(j, 0)
            total += (hi - lo).bit_length()
        # comparisons, numerator/radix residues, saturated phase and end flags
        return (total + len(self.numerators) + 2 * self.denominator_exponent
                + max(self.denominator_exponent, 2).bit_length() + 3)


def first_pass(column: Column, rows: Iterable[Sequence[int]], obs: Observer) -> int:
    """Return the bounded integer c with canonical y=(sum a*x-c*q)/D."""
    states = [0] * len(column.thresholds)
    comparisons = [0] * len(column.numerators)
    numerator_residue = radix_residue = phase = 0
    seen = False
    at_least_two = False
    last_radix = 0
    d = column.denominator
    for row in rows:
        need(len(row) == len(column.numerators) + 1, 'input channel count')
        need(all(bit in (0, 1) for bit in row), 'binary input row')
        bits, radix = row[:-1], row[-1]
        if not seen:
            need(radix == 1, 'radix must be odd')
        else:
            at_least_two = True
        seen, last_radix = True, radix
        digit = sum(a * bit for a, bit in zip(column.numerators, bits))
        for index, j in enumerate(column.thresholds):
            states[index] = (states[index] + digit - j * radix) // 2
            lo = column.lower - max(j, 0)
            hi = column.positive - min(j, 0)
            need(lo <= states[index] <= hi, 'quotient state escaped invariant')
        for index, bit in enumerate(bits):
            comparisons[index] = (comparisons[index] + bit - radix) // 2
            need(comparisons[index] in (-1, 0), 'input comparison state escaped')
        if phase < column.denominator_exponent:
            numerator_residue = (numerator_residue + (digit << phase)) % d
            radix_residue = (radix_residue + (radix << phase)) % d
            phase += 1
        obs.first_rows += 1
        obs.input_symbols += len(row)
        obs.quotient_updates += len(states)
        obs.comparison_updates += len(comparisons)
        obs.largest_signed_state = max(obs.largest_signed_state, *(abs(x) for x in states), 0)
    need(seen and at_least_two and last_radix == 1, 'canonical odd radix at least three')
    need(all(x == -1 for x in comparisons), 'low digit outside canonical radix')
    # If the radix has fewer than s bits, the absent high input bits are zero.
    # The stored residues are already complete; no extra input pass is needed.
    inverse = column.inverse_residues[radix_residue]
    residue = (numerator_residue * inverse) % d
    quotient = column.lower + sum(x >= 0 for x in states)
    carry = quotient - ((quotient - residue) % d)
    lo, hi = column.carry_bounds
    need(lo <= carry <= hi, 'terminal carry escaped envelope')
    return carry


def second_pass(column: Column, carry: int, rows: Iterable[Sequence[int]],
                obs: Observer) -> tuple[int, ...]:
    """Emit the B zero-padded bits of the new low digit, LSB first."""
    lo, hi = column.carry_bounds
    need(lo <= carry <= hi, 'invalid carry code')
    state = phase = 0
    out: list[int] = []
    lower = column.lower - max(carry, 0)
    upper = column.positive - min(carry, 0)

    def tick(digit: int, radix: int) -> None:
        nonlocal state, phase
        total = state + digit - carry * radix
        bit = total % 2
        state = total // 2
        need(lower <= state <= upper, 'output state escaped invariant')
        if phase < column.denominator_exponent:
            need(bit == 0, 'discarded denominator bit is nonzero')
            phase += 1
        else:
            out.append(bit)
            obs.output_symbols += 1
        obs.largest_signed_state = max(obs.largest_signed_state, abs(state))

    for row in rows:
        need(len(row) == len(column.numerators) + 1, 'second-pass channel count')
        need(all(bit in (0, 1) for bit in row), 'second-pass binary row')
        tick(sum(a * bit for a, bit in zip(column.numerators, row[:-1])), row[-1])
        obs.second_rows += 1
        obs.input_symbols += len(row)
    for _ in range(column.denominator_exponent):
        tick(0, 0)
        obs.flush_rows += 1
    need(state == 0, 'final output carry is nonzero')
    return tuple(out)


def produce(column: Column, row_factory: Callable[[], Iterable[Sequence[int]]],
            observer: Observer | None = None) -> tuple[tuple[int, ...], int, Observer]:
    """Inputs must be the same read-only channels on both traversals."""
    obs = Observer() if observer is None else observer
    carry = first_pass(column, row_factory(), obs)
    bits = second_pass(column, carry, row_factory(), obs)
    return bits, carry, obs


def integer_rows(values: Sequence[int], q: int) -> Callable[[], Iterable[tuple[int, ...]]]:
    """Convenience fixture/adapter; excluded from finite-control state theorem."""
    need(q > 0, 'positive fixture radix')
    width = q.bit_length()
    need(all(0 <= x < (1 << width) for x in values), 'fixture value exceeds supplied channel width')
    return lambda: (tuple((x >> k) & 1 for x in (*values, q)) for k in range(width))


def from_bits(bits: Iterable[int]) -> int:
    return sum(bit << k for k, bit in enumerate(bits))


def invert_word(word: Sequence[Sequence]) -> list[tuple]:
    result = []
    for op in reversed(word):
        if op[0] == 'swap':
            result.append(tuple(op))
        elif op[0] == 'add':
            result.append(('add', op[1], op[2], str(-Fraction(op[3]))))
        elif op[0] == 'scale':
            result.append(('scale', op[1], str(1 / Fraction(op[2]))))
        else:
            raise ValueError('unknown opcode')
    return result


def word_envelope(word: Sequence[Sequence]) -> dict[str, int]:
    product = 1
    exponent = 0
    arithmetic = 0
    for op in word:
        if op[0] == 'swap':
            continue
        coefficient = Fraction(op[3] if op[0] == 'add' else op[2])
        d, a = coefficient.denominator, coefficient.numerator
        need(d.bit_count() == 1, 'non-dyadic coefficient')
        need(op[0] != 'scale' or (a and abs(a).bit_count() == 1), 'nonunit dyadic scale')
        product *= d + abs(a) if op[0] == 'add' else max(d, abs(a))
        exponent += d.bit_length() - 1
        arithmetic += 1
    return dict(denominator_exponent=exponent, product_bound=product,
                signed_work_bits=product.bit_length() + 4, arithmetic_ops=arithmetic)


def evaluate_row(word: Sequence[Sequence], low: Sequence[int], q: int,
                 observer: Observer | None = None) -> dict:
    """Produce a whole-word low row and exact fused dyadic carry.

    Only per-atom low digits enter the two-pass controller. Fused carry registers
    use separately charged exact integer arithmetic; they are not finite control.
    """
    need(q >= 3 and q % 2 == 1, 'odd radix at least three')
    need(all(0 <= x < q for x in low), 'canonical low row')
    n = len(low)
    values = list(low)
    numerators = [0] * n
    exponent = 0
    obs = Observer() if observer is None else observer
    envelope = word_envelope(word)
    limit = 1 << (envelope['signed_work_bits'] - 1)
    observed_peak = 0
    for op in word:
        kind, i = op[:2]
        need(0 <= i < n, 'target index')
        if kind == 'swap':
            j = op[2]
            need(0 <= j < n and i != j, 'swap index')
            values[i], values[j] = values[j], values[i]
            numerators[i], numerators[j] = numerators[j], numerators[i]
            continue
        need(kind in ('add', 'scale'), 'unknown arithmetic operation')
        coefficient = Fraction(op[3] if kind == 'add' else op[2])
        a, d = coefficient.numerator, coefficient.denominator
        s = d.bit_length() - 1
        if kind == 'add':
            j = op[2]
            need(0 <= j < n and i != j, 'addition index')
            column = Column((d, a), s)
            inputs = (values[i], values[j])
        else:
            column = Column((a,), s)
            inputs = (values[i],)
        output_bits, carry, _ = produce(column, integer_rows(inputs, q), obs)
        updated = [x << s for x in numerators]
        term = carry << exponent
        if kind == 'add':
            partial = updated[i] + a * numerators[j]
        else:
            partial = a * numerators[i]
        updated[i] = partial + term
        for x in (*updated, partial, term):
            need(-limit <= x < limit, 'fused integer register overflow')
            observed_peak = max(observed_peak, abs(x))
        values[i] = from_bits(output_bits)
        numerators = updated
        exponent += s
    need(exponent == envelope['denominator_exponent'], 'denominator ledger mismatch')
    return dict(low=values, carry_numerators=numerators, denominator_exponent=exponent,
                envelope=envelope, peak_integer_magnitude=observed_peak)
