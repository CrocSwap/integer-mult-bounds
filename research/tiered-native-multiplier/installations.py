"""Select both complete native stages from the signed controller's public width."""

from dataclasses import dataclass
from fractions import Fraction as Q

BINARY_C = Q(4391986206293, 2**50)
GAUSSIAN_C = Q(2143194013, 2**39)


@dataclass(frozen=True)
class Profile:
    rank_logs: tuple
    complex_log: int
    kappa: Q
    eta: Q = Q(39, 10000)
    positive_stop_denominator: int = 10**18

    @property
    def ordinary(self):
        return self.kappa + Q(5, self.positive_stop_denominator)


ENTRY = Profile((3000, 3080), 1024, Q(".00345"))
TERMINAL = Profile((35327, 559005), 680000, Q(".0038982"))
PROFILES = {"entry": ENTRY, "terminal": TERMINAL}


def activation(profile):
    from linear_geometry import connected_exponent
    from staged_carriers import entrance_logs

    return connected_exponent(entrance_logs(profile.rank_logs)[-1], profile.complex_log)


def at_public(public):
    """The magnitude scan and square-side selector have already computed public."""
    return TERMINAL if public.bit_length() > activation(TERMINAL) else ENTRY
