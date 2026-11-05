"""Exact, whole-invocation prices for independent chronological cuts.

SHIN09-git with OpenAI Codex assistance. Apache-2.0.
"""
from dataclasses import dataclass
from fractions import Fraction
from heapq import heappop, heappush
from math import gcd, lcm


@dataclass(frozen=True)
class Label:
    loss: Fraction
    size: int
    counts: tuple[int, ...]


def residue_table(widths, losses, modulus):
    """Least (loss, total width) labels and one attaining count vector."""
    labels = [None] * modulus
    labels[0] = Label(Fraction(0), 0, (0,) * len(widths))
    queue = [(Fraction(0), 0, 0)]
    while queue:
        loss, size, r = heappop(queue)
        current = labels[r]
        if (loss, size) != (current.loss, current.size):
            continue
        for i, (width, charge) in enumerate(zip(widths, losses, strict=True)):
            s = (r + width) % modulus
            value = (loss + charge, size + width)
            old = labels[s]
            if old is None or value < (old.loss, old.size):
                counts = list(current.counts)
                counts[i] += 1
                labels[s] = Label(*value, tuple(counts))
                heappush(queue, (*value, s))
    return labels


def exact_prefix(widths, prices, stop):
    """Amount-ordered optimum with a last-invocation witness."""
    bills = [Fraction(0)] + [None] * stop
    last = [None] * (stop + 1)
    for n in range(1, stop + 1):
        for i, w in enumerate(widths):
            if w <= n and bills[n-w] is not None:
                price = bills[n-w] + prices[i]
                if bills[n] is None or price < bills[n]:
                    bills[n], last[n] = price, i
    return bills, last


class Menu:
    def __init__(self, programs):
        rows = tuple(programs)
        if not rows or any(type(w) is not int or w <= 0 for w, _ in rows):
            raise ValueError("widths must be positive integers")
        if any(isinstance(c, bool) or not isinstance(c, (int, Fraction)) or c <= 0
               for _, c in rows):
            raise ValueError("prices must be positive exact rationals")
        rows = sorted(rows)
        self.widths = tuple(w for w, _ in rows)
        if len(set(self.widths)) != len(rows):
            raise ValueError("widths must be distinct")
        self.g = gcd(*self.widths)
        self.prices = tuple(Fraction(c) for _, c in rows)
        self.density = min(c / w for w, c in zip(self.widths, self.prices, strict=True))
        self.losses = tuple(c - w * self.density for w, c in zip(self.widths, self.prices, strict=True))
        self.best = tuple(i for i, loss in enumerate(self.losses) if loss == 0)
        cheap = tuple(self.widths[i] for i in self.best)
        self.h = gcd(*cheap)
        self.labels = residue_table(self.widths, self.losses, self.h)
        normalized = tuple(w // self.h for w in cheap)
        self.apery = residue_table(normalized, (0,) * len(cheap), normalized[0])
        self.conductor = max(item.size for item in self.apery) - normalized[0] + 1
        self.threshold = max(item.size for item in self.labels if item is not None) + self.h * self.conductor
        self.anchor = cheap[0]
        self.refined = (self.labels if self.anchor == self.h else
                        residue_table(self.widths, self.losses, self.anchor))

    def cheap_counts(self, n):
        if n < 0 or n % self.h:
            return None
        z = n // self.h
        m = len(self.apery)
        label = self.apery[z % m]
        if z < label.size:
            return None
        counts = [0] * len(self.widths)
        for i, k in zip(self.best, label.counts, strict=True):
            counts[i] = k
        counts[self.best[0]] += (z - label.size) // m
        return counts

    def optimum(self, n, prefix=None):
        """Return (exact price, aligned invocation counts), or None for a hole."""
        if type(n) is not int or n < 0:
            raise ValueError("target must be a nonnegative integer")
        label = self.refined[n % self.anchor]
        if label is None:
            return None
        if n >= label.size:
            counts = list(label.counts)
            counts[self.best[0]] += (n - label.size) // self.anchor
            return self.density * n + label.loss, tuple(counts)
        bills, last = prefix if prefix is not None else exact_prefix(self.widths, self.prices, n)
        if bills[n] is None:
            return None
        counts = [0] * len(self.widths)
        remaining = n
        while remaining:
            i = last[remaining]
            counts[i] += 1
            remaining -= self.widths[i]
        return bills[n], tuple(counts)


def validate_cuts(cuts, parent):
    if (not cuts or type(parent) is not int or parent <= 0 or
            any(type(q) is not int or q <= 0 for q, _ in cuts)):
        raise ValueError("positive parent and cut multiplicities required")


def period_and_floor(cuts, parent=1):
    """The least eventual excess period, floor bill per unit and first floor."""
    validate_cuts(cuts, parent)
    period = lcm(*(m.h // gcd(m.h, q) for q, m in cuts))
    floor = sum(q * m.density for q, m in cuts) / parent
    # One cheapest program at each cut supplies a common positive witness.
    cheap = [(q, m.widths[m.best[0]]) for q, m in cuts]
    upper = lcm(*(w // gcd(w, q) for q, w in cheap))
    guaranteed = max(1, max((m.h*m.conductor + q - 1) // q for q, m in cuts))
    upper = min(upper, ((guaranteed + period - 1) // period) * period)
    for a in range(period, upper + 1, period):
        if all(m.cheap_counts(a*q) is not None for q, m in cuts):
            return period, floor, a
    raise ArithmeticError("single-width floor witness missing")


def first_periodic_replication(cuts):
    """Earliest positive replication from which the excess is periodic."""
    validate_cuts(cuts, 1)
    accessible = lcm(*(m.g // gcd(m.g, q) for q, m in cuts))
    last_bad = 0
    for q, menu in cuts:
        step = q * accessible
        classes = menu.anchor // gcd(menu.anchor, step)
        for u in range(classes):
            s = (step * u) % menu.anchor
            limit = (menu.refined[s].size - 1) // step
            last_t = limit - (limit - u) % classes
            last_bad = max(last_bad, accessible * last_t)
    return last_bad + 1


def frontier(cuts, parent=1):
    period, floor, first = period_and_floor(cuts, parent)
    prefixes = [exact_prefix(m.widths, m.prices, min(q*first, max(0, m.threshold-1)))
                for q, m in cuts]
    records = []
    for a in range(1, first + 1):
        bills = [m.optimum(a*q, prefix) for (q, m), prefix in zip(cuts, prefixes, strict=True)]
        if any(bill is None for bill in bills):
            continue
        price = sum(bill[0] for bill in bills) / (parent*a)
        if not records or price < records[-1][1]:
            records.append((a, price, [bill[1] for bill in bills]))
    return period, floor, records
