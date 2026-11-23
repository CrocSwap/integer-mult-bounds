"""Fixed, complete installations of the retimed binary and numerical suppliers."""

from dataclasses import dataclass
from fractions import Fraction as Q

BINARY_C = Q(4484997569314581, 2**60)
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


SELECTED_PRICE = Profile((5610,), 1024, Q(97,25000), Q(".00363005817"), 10**14)
SMALL = Profile((18400,), 1600, Q(97,25000), Q(".0038"), 10**14)
COMPACT = Profile((9100, 144000), 8500, Q(97,25000), Q(".00387992803556"), 10**14)
BALANCED = Profile((50900, 804000, 12800000), 19000, Q(39,10000), Q(".00389"), 10**14)
NEAR = Profile((3550000, 56200000, 888000000, 14100000000, 222000000000),
               19000, Q(39,10000), Q(".00389011528"), 10**17)
MATCHED = Profile((401000000, 6340000000, 101000000000, 1590000000000,
                   25100000000000, 396000000000000),
                  19000, Q(39,10000), Q(".0038901152865907"), 10**17)
RESOLUTION = Profile((5_698_204_041, 91_171_264_649, 1_458_740_234_375,
                      23_339_843_750_000, 373_437_500_000_000,
                      5_975_000_000_000_000, 95_600_000_000_000_000),
                     19_000, Q(39,10000), Q(".003890115286594445"), 10**21)
PROFILES = {"selected-price": SELECTED_PRICE, "small": SMALL, "compact": COMPACT,
            "balanced": BALANCED, "near": NEAR, "matched": MATCHED, "resolution": RESOLUTION}
