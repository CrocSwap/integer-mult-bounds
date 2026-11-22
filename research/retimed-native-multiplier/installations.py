"""Fixed, complete installations of the retimed binary and numerical suppliers."""

from dataclasses import dataclass
from fractions import Fraction as Q

BINARY_C = Q(4484997569314581, 2**60)
GAUSSIAN_C = Q(4085, 2**20)


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


COMPACT = Profile((33000, 380000), 13000, Q(97,25000), Q(".00387992803556"), 10**14)
SMALL = Profile((48000,), 3000, Q(97,25000), Q(".0038"), 10**14)
BALANCED = Profile((90000, 1800000, 36000000), 36000, Q(39,10000), Q(".00389"), 10**14)
NEAR = Profile((20000000,300000000,4000000000,40000000000,600000000000),
               36000,Q(39,10000),Q(".00389011528"),10**17)
MATCHED = Profile((650000000,10500000000,168000000000,2700000000000,
                   43000000000000,1050000000000000),
                  36000,Q(39,10000),Q(".0038901152865907"),10**17)
PROFILES = {"small": SMALL, "compact": COMPACT, "balanced": BALANCED,
            "near": NEAR, "matched": MATCHED}
