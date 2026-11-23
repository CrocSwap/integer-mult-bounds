"""Represent a split address projector by a frame program and an ordered mask."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import chain

from ternary_frames import covered_factors, residue
from vendor.cover import elementary_swap, rotate, scale_records, target_pass


def inverse_word(word):
    for op, i, *args in reversed(word):
        if op == "scale":
            yield op, i, 1 / Fraction(args[0])
        elif op == "add":
            yield op, i, args[0], -args[1]
        else:
            yield op, i, args[0]


def coordinate_word(word, index):
    for op, i, *args in word:
        if op == "scale":
            yield op, index(i), args[0]
        elif op == "add":
            yield op, index(i), index(args[0]), args[1]
        else:
            yield op, index(i), index(args[0])


def apply_row(word, values, modulus):
    row = list(values)
    for op, i, *args in word:
        if op == "scale":
            row[i] = row[i] * residue(args[0], modulus) % modulus
        elif op == "add":
            j, coefficient = args
            row[i] = (row[i] + row[j] * residue(coefficient, modulus)) % modulus
        else:
            j = args[0]
            row[i], row[j] = row[j], row[i]
    return row


def move_cover(records, low, word, digits, swap=elementary_swap):
    """Route one entire low packet by the elementary word, with its high carries."""
    n, side = len(low), 3 ** (digits - 1)
    low = [list(row) for row in low]
    data = list(records)
    if len(data) != side ** (n * n):
        raise ValueError("The matcher needs the complete high matrix fibre")
    for op, t, *args in word:
        for i, row in enumerate(low):
            target = i * n + t
            if op == "swap":
                j = args[0]
                row[t], row[j] = row[j], row[t]
                if side > 1:
                    data = swap(data, 3, digits - 1, n * n, target, i * n + j)
                continue
            if op == "scale":
                coefficient = Fraction(args[0])
                value = row[t] * coefficient
            else:
                j, coefficient = args
                value = row[t] + row[j] * coefficient
            row[t] = residue(value, 3)
            if side == 1:
                continue
            offset = residue((Fraction(value) - row[t]) / 3, side)
            if op == "scale":
                def scaled(_prefix, slots):
                    return rotate(scale_records(slots, coefficient), offset)
                data = target_pass(data, side, n * n, target, scaled)
            else:
                source = i * n + j
                backwards = source > target
                if backwards:
                    data = swap(data, 3, digits - 1, n * n, source, target)
                    source, target = target, source
                factor = residue(coefficient, side)
                def added(prefix, slots):
                    return rotate(slots, factor * prefix[source] + offset)
                data = target_pass(data, side, n * n, target, added)
                if backwards:
                    data = swap(data, 3, digits - 1, n * n, source, target)
    return low, data


@dataclass(frozen=True)
class Frame:
    size: int
    word: tuple
    mask: tuple

    def embed(self, size, indices):
        """Place the whole basis and fill the exterior with identity coordinates."""
        return Frame(size, tuple(coordinate_word(self.word, indices.__getitem__)),
                     tuple(indices[i] for i in self.mask))

    def parts(self, cutoff):
        """Partition the active coordinates in the stipulated order."""
        if cutoff < 1:
            raise ValueError("The positive cutoff must be at least one")
        return [Frame(self.size, self.word, self.mask[i:i + cutoff])
                for i in range(0, len(self.mask), cutoff)]

    def complement(self):
        selected = set(self.mask)
        return Frame(self.size, self.word, tuple(i for i in range(self.size) if i not in selected))

    def tensor(self, other):
        """Emit the two lifted factors in F tensor G. Account for every copy."""
        n, m = self.size, other.size
        first = chain.from_iterable(coordinate_word(self.word, range(j, n * m, m).__getitem__)
                                    for j in range(m))
        second = chain.from_iterable(coordinate_word(other.word, range(i * m, (i + 1) * m).__getitem__)
                                     for i in range(n))
        return Frame(n * m, tuple(chain(first, second)), tuple(i * m + j for i in self.mask for j in other.mask))

    def matcher_to(self, target):
        """Return S such that P S=S Q using full coordinate permutations."""
        if self.size != target.size or len(self.mask) != len(target.mask):
            raise ValueError("Matching requires equal width and rank")
        n = self.size
        source_at = list(range(n))
        position = list(range(n))
        alignment = dict(zip(target.mask + target.complement().mask,
                             self.mask + self.complement().mask, strict=True))
        swaps = []
        for dst in range(n):
            src = position[alignment[dst]]
            if src != dst:
                x, y = source_at[dst], source_at[src]
                source_at[dst], source_at[src] = y, x
                position[x], position[y] = src, dst
                swaps.append(("swap", dst, src))
        return tuple(chain(self.word, swaps, inverse_word(target.word)))

    def project(self, row, modulus):
        local = apply_row(self.word, row, modulus)
        selected = set(self.mask)
        return apply_row(tuple(inverse_word(self.word)),
                         [x if i in selected else 0 for i, x in enumerate(local)], modulus)

    def covered_line(self, cover_row, digits):
        """Generate native factors from a word, then place them at the full g."""
        if len(self.mask) != 1:
            raise ValueError("A terminal leaf must have rank one")
        modulus = 3**digits
        e = [int(i == self.mask[0]) for i in range(self.size)]
        dual = []
        for op, i, *args in reversed(self.word):
            if op == "add":
                dual.append((op, args[0], i, args[1]))
            else:
                dual.append((op, i, *args))
        u = apply_row(dual, e, modulus)
        v = apply_row(tuple(inverse_word(self.word)), e, modulus)
        return covered_factors((u, v), cover_row, digits)
