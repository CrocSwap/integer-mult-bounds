"""Construct exact two-row fanout optima for comparable finite-ring demands.

The theorem is in PROOF.md and covers arbitrary rings and positive real
prices. This executable uses explicit finite rings and positive rational
prices. Krzysztof Wójt, substantial OpenAI Codex assistance; Apache-2.0.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable


@dataclass(frozen=True)
class Ring:
    name: str
    size: int
    zero: int
    one: int
    add: Callable[[int, int], int]
    mul: Callable[[int, int], int]
    neg: Callable[[int], int]

    def element(self, value: int) -> int:
        if type(value) is not int or not 0 <= value < self.size:
            raise ValueError("coefficient is not a canonical ring element")
        return value

    def quotient(self, target: int, parent: int) -> int | None:
        """Return r with target = r * parent, never parent * r."""
        self.element(target)
        self.element(parent)
        return next((r for r in range(self.size)
                     if self.mul(r, parent) == target), None)


def modular_ring(modulus: int) -> Ring:
    if type(modulus) is not int or modulus < 2:
        raise ValueError("modulus must be an integer at least two")
    return Ring(f"Z/{modulus}", modulus, 0, 1,
                lambda a, b: (a + b) % modulus,
                lambda a, b: (a * b) % modulus,
                lambda a: -a % modulus)


def binary_matrix_ring() -> Ring:
    """M_2(F_2), row-major bits, used to expose left/right order."""
    def product(a: int, b: int) -> int:
        result = 0
        for i in range(2):
            for j in range(2):
                entry = 0
                for k in range(2):
                    entry ^= ((a >> (2*i+k)) & 1) & ((b >> (2*k+j)) & 1)
                result |= entry << (2*i+j)
        return result
    return Ring("M2(F2)", 16, 0, 9, lambda a, b: a ^ b, product, lambda a: a)


def binary_dual_ring() -> Ring:
    """F_2[e]/e^2; a + b*e is encoded by a + 2*b."""
    def product(a: int, b: int) -> int:
        constant = (a & 1) & (b & 1)
        linear = (((a >> 1) & (b & 1)) ^ ((a & 1) & (b >> 1))) << 1
        return constant | linear
    return Ring("F2[e]/e^2", 4, 0, 1, lambda a, b: a ^ b, product, lambda a: a)


@dataclass(frozen=True)
class Prices:
    source: tuple[Fraction, Fraction]
    add: tuple[Fraction, Fraction]

    def __post_init__(self) -> None:
        for pair in (self.source, self.add):
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise ValueError("prices must be two-element tuples")
            if any(type(x) not in (int, Fraction) or x <= 0 for x in pair):
                raise ValueError("prices must be positive exact rationals")


@dataclass(frozen=True)
class Gate:
    kind: str
    dst: int
    coefficient: int


@dataclass(frozen=True)
class Plan:
    name: str
    price: Fraction
    word: tuple[Gate, ...]


def word_price(word: tuple[Gate, ...], prices: Prices) -> Fraction:
    total = Fraction(0)
    for gate in word:
        if type(gate.dst) is not int or gate.dst not in (0, 1):
            raise ValueError("gate destination must be 0 or 1")
        if gate.kind == "source":
            total += prices.source[gate.dst]
        elif gate.kind == "add":
            total += prices.add[gate.dst]
        else:
            raise ValueError("unknown gate kind")
    return total


def inverse(word: tuple[Gate, ...], ring: Ring) -> tuple[Gate, ...]:
    return tuple(Gate(g.kind, g.dst, ring.neg(ring.element(g.coefficient)))
                 for g in reversed(word))


def demand_quotients(ring: Ring, demand: tuple[int, int]) -> tuple[int | None, ...]:
    if not isinstance(demand, tuple) or len(demand) != 2:
        raise ValueError("demand must be a pair")
    for element in demand:
        ring.element(element)
    ratios = (ring.quotient(demand[1], demand[0]),
              ring.quotient(demand[0], demand[1]))
    if all(r is None for r in ratios):
        raise ValueError("incomparable principal left ideals are outside scope")
    return ratios


def lower_envelope(ring: Ring, demand: tuple[int, int], prices: Prices) -> Fraction:
    """The five-term theorem, independently of the chosen attaining word."""
    ratios = demand_quotients(ring, demand)
    values = [sum((prices.source[i] for i in (0, 1)
                   if demand[i] != ring.zero), Fraction(0))]
    for i in (0, 1):
        j = 1-i
        if demand[j] == ring.zero:
            single = prices.source[i]
        elif ratios[i] is not None:
            single = prices.source[i] + 2*prices.add[j]
        else:
            single = prices.source[i] + 2*(prices.add[i] + prices.add[j])
        values.extend((single, 2*prices.source[i] + 2*prices.add[j]))
    return min(values)


def candidates(ring: Ring, demand: tuple[int, int], prices: Prices) -> tuple[Plan, ...]:
    ratios = demand_quotients(ring, demand)
    plans = []

    def retain(name: str, gates: list[Gate]) -> None:
        word = tuple(g for g in gates if g.coefficient != ring.zero)
        plans.append(Plan(name, word_price(word, prices), word))

    retain("direct", [Gate("source", i, demand[i]) for i in (0, 1)])
    for i in (0, 1):
        j = 1-i
        retain(f"repeat-{i}", [
            Gate("add", j, ring.neg(ring.one)), Gate("source", i, demand[j]),
            Gate("add", j, ring.one),
            Gate("source", i, ring.add(demand[i], ring.neg(demand[j]))),
        ])
        ratio = ratios[i]
        if ratio is not None:
            retain(f"transport-{i}", [Gate("add", j, ring.neg(ratio)),
                   Gate("source", i, demand[i]), Gate("add", j, ratio)])
        reverse_ratio = ratios[j]
        if reverse_ratio is not None:
            last = ring.add(reverse_ratio, ring.neg(ring.one))
            retain(f"mix-{i}", [
                Gate("add", i, ring.neg(last)), Gate("add", j, ring.neg(ring.one)),
                Gate("source", i, demand[j]), Gate("add", j, ring.one),
                Gate("add", i, last),
            ])
    return tuple(plans)


def optimal_plan(ring: Ring, demand: tuple[int, int], prices: Prices) -> Plan:
    best = min(candidates(ring, demand, prices),
               key=lambda plan: (plan.price, len(plan.word), plan.name))
    if best.price != lower_envelope(ring, demand, prices):
        raise RuntimeError("attaining word disagrees with the proved lower envelope")
    return best


def execute(ring: Ring, word: tuple[Gate, ...], initial: tuple[int, int, int]) -> tuple[int, ...]:
    if not isinstance(initial, tuple) or len(initial) != 3:
        raise ValueError("state must contain two rows and the preserved source")
    state = [ring.element(value) for value in initial]
    for gate in word:
        if type(gate.dst) is not int or gate.dst not in (0, 1):
            raise ValueError("gate destination must be 0 or 1")
        coefficient = ring.element(gate.coefficient)
        if gate.kind not in ("source", "add"):
            raise ValueError("unknown gate kind")
        src = 2 if gate.kind == "source" else 1-gate.dst
        state[gate.dst] = ring.add(state[gate.dst], ring.mul(coefficient, state[src]))
    return tuple(state)
