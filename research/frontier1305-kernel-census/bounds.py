"""bounds.py: true-moment bounds for each priced candidate, from PR #1186 revision 2's Pricer(interval=True).

The stored fields do not depend on the platform:
  realized_delta_units  bounds of (H_candidate - H_base) . T(b) from the engines' exact per-rank bounds (exactly 0 for an
                        unchanged profile);
  gain_certified        the upper end of realized_delta_units is negative;
  max_gain_units_ceil   rigorous: no frame assignment of the candidate program has a per-call moment at b below the base
                        word's surrogate-optimal frames by more than this (exact rational value rounded UP to 1e-6 units);
  interval_width_units_ceil  width of the candidate's own true-moment interval, rounded up likewise.
One unit is 2^-40 of the per-call moment (frames.Costs)."""
import math
from fractions import Fraction as Q
GRID = 10 ** 6
def up(x):
    n = math.ceil(Q(x) * GRID); assert n >= 0
    return f"{n // GRID}.{n % GRID:06d}"
def pricer(H):
    class Pricer(H.Pricer):
        def compare(self, profile, iv):
            out = super().compare(profile, iv); unit = 1 << self.costs.unit_bits
            gain = max(Q(0), self.base_interval['upper'] - iv['lower']) * unit
            return dict(realized_delta_units=list(out['realized_delta_units']), gain_certified=out['gain_certified'],
                        max_gain_units_ceil=up(gain), interval_width_units_ceil=up((iv['upper'] - iv['lower']) * unit))
    return Pricer
