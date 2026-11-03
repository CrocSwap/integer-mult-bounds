"""Exact finite-menu batching. Counts describe whole compatible invocations."""

from dataclasses import dataclass
from math import gcd, lcm


@dataclass(frozen=True)
class Batch:
    widths: tuple[int, ...]
    multiplicity: int

    def __post_init__(self) -> None:
        if not isinstance(self.widths, tuple) or not 1 <= len(self.widths) <= 8:
            raise ValueError("a menu must be a tuple of one through eight widths")
        if any(type(w) is not int or not 1 <= w <= 64 for w in self.widths):
            raise ValueError("widths must be integers in 1..64")
        if tuple(sorted(set(self.widths))) != self.widths:
            raise ValueError("widths must be strictly increasing")
        if type(self.multiplicity) is not int or not 1 <= self.multiplicity <= 4096:
            raise ValueError("multiplicity must be an integer in 1..4096")


@dataclass(frozen=True)
class Residues:
    widths: tuple[int, ...]
    divisor: int
    modulus: int
    minima: tuple[int, ...]
    witnesses: tuple[tuple[int, ...], ...]
    conductor: int


@dataclass(frozen=True)
class Schedule:
    replication: int
    divisibility_step: int
    scan_bound: int
    partitions: tuple[tuple[int, ...], ...]
    tables: tuple[Residues, ...]


def residue_minima(widths: tuple[int, ...]) -> Residues:
    """Return the Apéry minima and attaining coefficient vectors."""
    Batch(widths, 1)
    divisor = gcd(*widths)
    coins = tuple(w // divisor for w in widths)
    modulus = coins[0]
    distances: list[int | None] = [None] * modulus
    witnesses = [(0,) * len(coins) for _ in range(modulus)]
    settled = [False] * modulus
    distances[0] = 0
    for _ in range(modulus):
        eligible = [r for r in range(modulus) if not settled[r]
                    and distances[r] is not None]
        if not eligible:
            raise ArithmeticError("normalized menu failed to reach every residue")
        r = min(eligible, key=lambda i: (distances[i], i))
        distance = distances[r]
        if distance is None:
            raise ArithmeticError("selected an unreachable residue")
        settled[r] = True
        for index, coin in enumerate(coins):
            target = (r + coin) % modulus
            candidate = distance + coin
            if distances[target] is None or candidate < distances[target]:
                distances[target] = candidate
                counts = list(witnesses[r])
                counts[index] += 1
                witnesses[target] = tuple(counts)
    minima = tuple(d for d in distances if d is not None)
    if len(minima) != modulus or max(minima) > (modulus - 1) * max(coins):
        raise ArithmeticError("residue-distance bound failed")
    return Residues(widths, divisor, modulus, minima, tuple(witnesses),
                    max(minima) - modulus + 1)


def partition(table: Residues, total: int) -> tuple[int, ...] | None:
    """Partition total using a table returned by residue_minima."""
    if type(total) is not int or not 0 <= total < 2**80:
        raise ValueError("total must be a nonnegative integer below 2^80")
    if total % table.divisor:
        return None
    normalized = total // table.divisor
    residue = normalized % table.modulus
    if normalized < table.minima[residue]:
        return None
    counts = list(table.witnesses[residue])
    counts[0] += (normalized - table.minima[residue]) // table.modulus
    result = tuple(counts)
    if sum(c * w for c, w in zip(result, table.widths)) != total:
        raise ArithmeticError("invocation partition has the wrong total")
    return result


def least_replication(batches: tuple[Batch, ...]) -> Schedule:
    """Return the least positive common replication, without pooling cuts."""
    if not isinstance(batches, tuple) or not 1 <= len(batches) <= 8:
        raise ValueError("supply one through eight chronological batches")
    if any(not isinstance(batch, Batch) for batch in batches):
        raise ValueError("every batch must have a validated Batch contract")
    tables = tuple(residue_minima(batch.widths) for batch in batches)
    step = lcm(*(table.divisor // gcd(table.divisor, batch.multiplicity)
                 for table, batch in zip(tables, batches)))
    rates = tuple(step * batch.multiplicity // table.divisor
                  for batch, table in zip(batches, tables))
    bound = max(1, *(max(0, table.conductor + rate - 1) // rate
                     for table, rate in zip(tables, rates)))
    if not 1 <= bound <= 3969 or step >= 2**48:
        raise ArithmeticError("declared finite search capacity failed")
    for multiplier in range(1, bound + 1):
        replication = step * multiplier
        partitions = tuple(partition(table, replication * batch.multiplicity)
                           for batch, table in zip(batches, tables))
        if all(counts is not None for counts in partitions):
            return Schedule(replication, step, bound,
                            tuple(c for c in partitions if c is not None), tables)
    raise ArithmeticError("conductor bound did not supply a feasible schedule")
