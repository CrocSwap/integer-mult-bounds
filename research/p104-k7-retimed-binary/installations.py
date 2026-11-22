"""Fixed, complete installations of the retimed binary and numerical suppliers."""

from dataclasses import dataclass
from fractions import Fraction as Q

BINARY_C = Q(4391986206293, 2**50)
GAUSSIAN_C = Q(2092819, 2**29)


@dataclass(frozen=True)
class Profile:
    rank_logs: tuple
    complex_log: int
    eta: Q
    kappa: Q
    positive_stop_denominator: int

    @property
    def ordinary(self):
        return self.kappa + Q(5, self.positive_stop_denominator)


SELECTED_PRICE = Profile((5610,), 1024, Q(97, 25000), Q(".00363005817"), 10**14)
SMALL = Profile((18400,), 1600, Q(97, 25000), Q(".0038"), 10**14)
COMPACT = Profile((9100, 144000), 8500, Q(97, 25000), Q(".00387992803556"), 10**14)
CONSERVATIVE_36K = Profile((60_000, 960_000), 36_000, Q(39, 10000), Q(".003893947"), 10**14)
COMPACT_1M = Profile((60_000, 960_000), 1_000_000, Q(39, 10000), Q(".003898026"), 10**17)
EXTENDED_10M = Profile((60_000, 960_000), 10_000_000, Q(39, 10000), Q(".003898163"), 10**18)
EXTENDED = Profile((60_000, 960_000), 20_000_000, Q(39, 10000), Q(".003898171"), 10**18)

PROFILES = {
    "selected-price": SELECTED_PRICE,
    "small": SMALL,
    "compact": COMPACT,
    "conservative-36k": CONSERVATIVE_36K,
    "compact-1m": COMPACT_1M,
    "extended-10m": EXTENDED_10M,
    "extended": EXTENDED,
}
