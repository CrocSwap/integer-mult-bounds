"""Generate the chronological grades of the dilated numerical source."""

from collections import Counter
from fractions import Fraction
from functools import cache

SCALES = (1, 79)
SPLITS = 1008
HALF = Fraction(1, 2)


class Grades:
    """Use the fixed role segments for each copy and each chronological split."""

    def __init__(self, ports, splits=0):
        self.ports = ports
        self.splits = splits
        raw = Counter()
        counts = {}
        for prefix, entries in ports.segments:
            key = id(entries)
            if key not in counts:
                ranks = (p.rank for p in entries) if prefix is None else (r for _, r in entries)
                counts[key] = Counter(ranks)
            raw.update(counts[key])
        if raw[1] < splits:
            raise ValueError("The base copy has too few rank-one loans")
        self.histogram = Counter()
        for scale in SCALES:
            for rank, count in raw.items():
                self.histogram[scale * rank] += count
        if splits:
            self.histogram[1] -= splits
            self.histogram[HALF] += 2 * splits

    def __len__(self):
        return len(SCALES) * len(self.ports) + self.splits

    def __iter__(self):
        for scale in SCALES:
            remaining = self.splits if scale == 1 else 0
            for rank in self.ports.ranks():
                if remaining and rank == 1:
                    yield HALF
                    yield HALF
                    remaining -= 1
                else:
                    yield scale * rank


@cache
def numerical_source():
    from upstream import HERE, install
    _, _, _, source = install()
    from clock_ports import clock_word
    from installations import GAUSSIAN_C
    from strong_complex import artifacts
    from unpowered_price import certify

    atlas = artifacts(source / "research/grade14-native-realization", HERE / "inputs")
    word = clock_word(atlas)
    targets, paid = Grades(word.targets), Grades(word.paid, SPLITS)
    margin, cells = certify(GAUSSIAN_C, (targets.histogram, paid.histogram))
    if cells is None or margin <= 0:
        raise ArithmeticError("The numerical source cannot pay its physical loans")
    return atlas, word, targets, paid, cells


@cache
def numerical_recipe(rank_log):
    from installations import GAUSSIAN_C
    from transport import Recipe

    _, word, targets, paid, cells = numerical_source()
    return Recipe(rank_log, max(SCALES) * word.ambient, targets, paid, cells, GAUSSIAN_C)
