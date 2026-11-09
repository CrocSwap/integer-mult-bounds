"""The actual remaining Gaussian diagonal, on full original target axes.

This is a new explicit Diagonal-event producer, not a FullRoot execution.
All preparation is input-independent and paid; online payloads stay on tapes.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import prod


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceiling(value):
    value = Q(value)
    return -(-value.numerator // value.denominator)


def ceil_log2(value):
    value = Q(value)
    need(value > 0, "positive radius")
    k = value.numerator.bit_length() - value.denominator.bit_length()
    power = Q(1 << k) if k >= 0 else Q(1, 1 << -k)
    return k + int(power < value)


def upper_grid(lower, upper, bits):
    """One-ulp approximation to A in [lower,upper] intersect [0,1]."""
    need(type(bits) is int and bits >= 1 and Q(0) <= lower <= upper
         and lower <= 1 and upper - lower <= Q(1, 1 << bits),
         "positive coefficient enclosure with one-ulp width")
    return min(1 << bits, (upper.numerator << bits) // upper.denominator)


@dataclass(frozen=True)
class Layout:
    lengths: tuple
    selected: tuple

    def __post_init__(self):
        need(type(self.lengths) is tuple and self.lengths
             and all(type(x) is int and x >= 1 for x in self.lengths),
             "positive original dyadic axis widths")
        need(type(self.selected) is tuple and self.selected and len(set(self.selected)) == len(self.selected)
             and all(type(x) is int and 0 <= x < len(self.lengths) for x in self.selected),
             "distinct original source axes in low-first packed order")

    @property
    def n(self):
        return sum(self.lengths)

    @property
    def h(self):
        return sum(self.lengths[a] for a in self.selected)

    @property
    def positions(self):
        starts = tuple(sum(self.lengths[:a]) for a in range(len(self.lengths)))
        return tuple(starts[a] + j for a in self.selected for j in range(self.lengths[a]))

    @property
    def gather(self):
        # Complete the selected source-to-low-target bijection on its union.
        source, target = self.positions, tuple(range(self.h))
        mapping = dict(zip(source, target))
        mapping.update(zip(sorted(set(target) - set(source)), sorted(set(source) - set(target))))
        return {a: b for a, b in mapping.items() if a != b}

    @property
    def inverse(self):
        return {b: a for a, b in self.gather.items()}

    def coordinates(self, packed_index):
        need(type(packed_index) is int and 0 <= packed_index < 1 << self.h,
             "full original group period index")
        values = []
        for a in self.selected:
            values.append(packed_index & ((1 << self.lengths[a]) - 1))
            packed_index >>= self.lengths[a]
        return tuple(values)


class RemainingProgram:
    """Bind the same References/u_i and emit one original Diagonal event.

    Caller supplies the original Core normalizer exponents, and the completed
    source normalization K. No further 2^-U is applied by the codec.
    """
    def __init__(self, Reference, references, normalizer_bits, layout, completed_bits,
                 bits, radius, Diagonal):
        self.Reference, self.references, self.normalizer_bits = Reference, tuple(references), tuple(normalizer_bits)
        self.layout, self.completed_bits, self.Diagonal = layout, completed_bits, Diagonal
        need(len(self.references) == len(layout.selected) == len(self.normalizer_bits),
             "same source-axis and original normalizer family")
        need(type(completed_bits) is int and completed_bits >= 0
             and type(bits) is int and bits >= 1 and type(radius) is int and radius >= 1,
             "integer completed normalization, grid, and actual-state radius")
        need(all(type(u) is int and u >= 0 for u in self.normalizer_bits), "original dyadic normalizer exponents")
        self.U, self.radius = sum(self.normalizer_bits), radius
        self.bound = sum(Q(ref.spec.alpha ** 2, 4) for ref in self.references)
        self.length = ceiling(8 * self.bound)
        need(completed_bits - self.U >= self.length, "funded actual remaining-diagonal contraction")
        self.bits = self.incoming = bits
        self.array_bits, self.axis_bits, self.axes = layout.n, layout.h, 1
        self.coarse_bits = layout.n - layout.h
        self.radius_bits = ceil_log2(radius) + (layout.n + 1) // 2
        self.data_width = bits + self.radius_bits + 2
        self.factor_width = self.cache_width = bits + 2
        self.temporary_width = 2 * self.data_width + 3
        self.stages, self.h_count, self.diagonal_count = 1, 0, 1
        self.reference_seal = self.source_seal()
        scale = Q(1, 1 << (completed_bits - self.U))
        self.receipts, page = [], []
        for index in range(1 << layout.h):
            coordinates = layout.coordinates(index)
            exponent = Q(0)
            for ref, k in zip(self.references, coordinates):
                source = ref.source_at.get(k)
                if source is not None:
                    exponent += ref.spec.alpha ** 2 * ref.betas[source] ** 2
            box = self.references[0].exp.relative(exponent, self.bound, bits + 4)
            need(box["lower"] > 0, "positive retained Gaussian enclosure")
            lower, upper = scale / box["upper"], scale / box["lower"]
            value = upper_grid(lower, upper, bits)
            page.append((value, 0))
            self.receipts.append(dict(coordinates=coordinates, exponent=exponent, lower=lower,
                                      upper=upper, value=value, precision=box["precision"],
                                      working_bits=box["working_bits"]))
        self.page = tuple(page)
        self.receipts = tuple(self.receipts)
        self.page_seal = sha256(repr(self.page).encode()).hexdigest()
        self.allocation_seal = self.allocation()
        self.validate()

    def source_seal(self):
        rows = []
        for a, ref, u in zip(self.layout.selected, self.references, self.normalizer_bits):
            need(type(ref) is self.Reference and ref.target_size == 1 << self.layout.lengths[a],
                 "same actual Reference and full original target axis")
            need(ref.narrow_gap > 0 and (1 << u) * ref.narrow_gap >= 1,
                 "same admitted narrow inverse normalizer")
            spec = {key: getattr(ref.spec, key) for key in ref.spec.__dataclass_fields__}
            need(sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest() == ref.description_hash,
                 "unchanged immutable reference specification")
            S, e, N = ref.spec.source_size, ref.spec.excess, ref.target_size
            need(N == S + e, "unchanged original target period")
            source_map = []
            for k in range(N):
                j = ref.source_at.get(k)
                candidate = (2 * S * k + N) // (2 * N)
                phi = (2 * e * candidate + S) // (2 * S)
                expected = candidate if 0 <= candidate < S and candidate + phi == k else None
                need(j == expected, "literal original selected-coordinate map")
                if j is not None:
                    beta = Q(e * j, S) - (2 * e * j + S) // (2 * S)
                    need(ref.betas[j] == beta and abs(beta) <= Q(1, 2), "literal original beta")
                source_map.append(j)
            rows.append((id(ref), ref.description_hash, u, tuple(source_map)))
        return tuple(rows)

    def allocation(self):
        names = ("normalizer_bits", "layout", "completed_bits", "U", "radius", "bound", "length",
                 "bits", "incoming", "array_bits", "axis_bits", "axes", "coarse_bits", "radius_bits",
                 "data_width", "factor_width", "cache_width", "temporary_width", "stages", "h_count",
                 "diagonal_count")
        return tuple(getattr(self, name) for name in names)

    def validate(self):
        need(self.allocation() == self.allocation_seal, "unchanged complete remaining-diagonal allocation")
        need(self.source_seal() == self.reference_seal, "unchanged same-reference source binding")
        need(sha256(repr(self.page).encode()).hexdigest() == self.page_seal,
             "unchanged certified remaining coefficient period")
        need(len(self.page) == 1 << self.layout.h and
             all(type(a) is int and 0 <= a <= 1 << self.bits and b == 0 for a, b in self.page),
             "contractive real common-grid coefficient page")

    def events(self):
        self.validate()
        # Full original spectator pages are explicitly emitted and paid.
        pages = ((self.page,),) * (1 << self.coarse_bits)
        yield self.Diagonal(0, self.coarse_bits, self.axis_bits, 1, self.bits, self.data_width,
                            self.factor_width, self.cache_width, self.temporary_width, pages)

    def record(self):
        return dict(original_axis_bits=self.layout.lengths, selected_axes=self.layout.selected,
                    full_group_bits=self.layout.h, records=1 << self.layout.n, U=self.U,
                    completed_bits=self.completed_bits, grid=self.bits, radius=self.radius,
                    radius_bits=self.radius_bits, data_width=self.data_width,
                    coefficient_stock=len(self.page), original_description_hashes=
                    [r.description_hash for r in self.references], page_sha256=self.page_seal)
