"""Install two weighted rank streams and materialize real labels at an active calendar."""

from collections import Counter
from fractions import Fraction as Q
from functools import cache
from typed_transport import NativeType, TypedPlan

WEIGHTS = (1, 90)
SCALES = (1, 2)
SPLITS = 1008


class GradeVariant:
    def __init__(self, ports, raw, scale, splits):
        self.ports, self.scale, self.splits = ports, scale, splits
        self.histogram = Counter({scale * r: n for r, n in raw.items()})
        if splits:
            if not (scale == 1 and raw[1] >= splits):
                raise ValueError("A fixed split lacks a physical rank-one loan")
            self.histogram[1] -= splits
            self.histogram[Q(1, 2)] += 2 * splits

    def __iter__(self):
        left = self.splits
        for r in self.ports.ranks():
            if r == 1 and left:
                left -= 1
                yield Q(1, 2)
                yield Q(1, 2)
            else:
                yield self.scale * r

    def __len__(self):
        return len(self.ports) + self.splits


class WeightedGrades:
    def __init__(self, ports, splits=0):
        raw = Counter()
        counts = {}
        for prefix, entries in ports.segments:
            key = id(entries)
            if key not in counts:
                counts[key] = (
                    Counter(p.rank for p in entries)
                    if prefix is None
                    else Counter(r for _, r in entries)
                )
            raw.update(counts[key])
        self.variants = (
            GradeVariant(ports, raw, 1, splits),
            GradeVariant(ports, raw, 2, 0),
        )
        self.histogram = Counter()
        for w, var in zip(WEIGHTS, self.variants, strict=True):
            for r, n in var.histogram.items():
                self.histogram[r] += w * n


@cache
def numerical_source():
    from upstream import HERE, install
    from strong_complex import artifacts
    from clock_ports import clock_word
    from installations import GAUSSIAN_C
    from unpowered_price import certify

    _, _, _, source = install()
    atlas = artifacts(source / "research/grade14-native-realization", HERE / "inputs")
    word = clock_word(atlas)
    targets, paid = WeightedGrades(word.targets), WeightedGrades(word.paid, SPLITS)
    margin, cells = certify(GAUSSIAN_C, (targets.histogram, paid.histogram))
    if cells is None or margin <= 0:
        raise ArithmeticError("The two native types cannot fund their real loans")
    return atlas, word, targets, paid, cells


class WeightedRecipe:
    def __init__(self, rank_log, ambient, targets, paid, cells, trial):
        if rank_log < 1024:
            raise ValueError("The complete numerical schedule requires H at least 1024")
        self.rank_log, self.ambient, self.targets, self.paid = (
            rank_log,
            ambient,
            targets,
            paid,
        )
        self.cells, self.trial, self.width_log = cells, trial, 92 * rank_log

    @property
    def width(self):
        return 1 << self.width_log

    def types(self):
        return tuple(
            NativeType(tuple(t), tuple(p), w)
            for t, p, w in zip(
                self.targets.variants, self.paid.variants, WEIGHTS, strict=True
            )
        )

    def typed_cells(self):
        shares = {}
        for (r, k), p in self.cells.items():
            for a, src in enumerate(self.paid.variants):
                if r not in src.histogram:
                    continue
                for b, dst in enumerate(self.targets.variants):
                    if k not in dst.histogram:
                        continue
                    shares[a, r, b, k] = (
                        p * WEIGHTS[b] * dst.histogram[k] / self.targets.histogram[k]
                    )
        return shares

    def open(self):
        types, shares = self.types(), self.typed_cells()
        M = 1 << self.rank_log
        return TypedPlan(
            M,
            types,
            shares,
            1 - self.trial,
            32768,
            2 * (M // (2048 * self.ambient)),
            M**6,
            M**82,
            M**2,
            width=self.width,
            delay_base=1 << 19,
        )


@cache
def numerical_recipe(rank_log):
    from installations import GAUSSIAN_C

    _, word, targets, paid, cells = numerical_source()
    return WeightedRecipe(rank_log, 2 * word.ambient, targets, paid, cells, GAUSSIAN_C)
