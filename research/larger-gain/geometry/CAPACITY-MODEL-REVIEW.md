# Independent review of the current-alphabet capacity ceiling

The model in [capacity_ceiling.py](../patterns/capacity_ceiling.py) is a valid
relaxation of the pinned PR564 whole-owner packing problem. The exact dual
in [CURRENT-ALPHABET-EXACT-CEILING.json](../patterns/CURRENT-ALPHABET-EXACT-CEILING.json)
passed the standard-library verifier with both independent rational moment
engines. This review separately checked the mathematical interpretation of
its variables and objective, not just the verifier's return value.

The 144 `(replica, child)` windows give 48 rank-eight windows and 32 windows
of each rank 16, 32 and 48. There are 112 port owners per window, so the
capacity equalities use respectively 5376, 3584, 3584 and 3584 physical bins.
Every legal literal arrangement supplies one integer pattern per bin;
enumerating all nonnegative counts of widths 4, 5, 8 and 9 below that bin's
capacity covers every such arrangement. The remaining axes are charged as
one child. Splitting a remainder could only increase its concave moment cost.

For a cold provider with `p = 0, 4, 8` promotions, the complete helper
inventory is `(p, 56-p, 157, 291)` at widths `(4, 5, 8, 9)`, totaling 504
helpers. Its paid local profile is fully included. The difference between
local paid rank mass and residual width mass is always

```text
2 * 112 * (9-1) + 64 = 1856.
```

The four width-balance equalities therefore account for every helper exactly
once. The provider-count equality imposes 72 complete invocations. Allowing
fractional counts and discarding chronology, active-data conflicts and
same-call owner uniqueness enlarges the feasible set. It cannot incorrectly
exclude a legal packing in the stated family. The resulting total rank mass
is always `sum(capacity * bins) + 72*1856 = 520704`.

At positive rate `b`, define

```text
c_b(r) = r * ((73/r)^b - 1) / b,   c_b(0) = 0.
```

The native complex moment is below one precisely when
`b * sum(c_b(r) * H[r]) < 2560`, since `73*7168 - 520704 = 2560`.
The verifier computes rigorous **lower** bounds on every LP objective
coefficient. A dual feasible against these smaller coefficients is also
feasible against the true costs. Its objective times `b` strictly exceeds
2560, proving rejection for every relaxed solution.

Both engines verified all 548 dual column inequalities at
`b = 0.001595676284575998624255`, the next supplier grid point above PR564.
The exact relaxed primal reproduces PR564's full histogram. Its alternate
provider mixture of 56 eight-pivot plus 16 zero-pivot calls has the same
total 448 promotions as the actual 55/eight, 2/four, 15/zero mixture; local
profiles and inventories depend affinely on that total. No extra source
provider is being assumed.

The nominal kappa upper bound is less than
`0.001593134158181640233288`, excluding the next `10^-18` kappa grid point.
This supports **optimality on the certified grids in this fixed family**.
One-rate dual verification should not be described as an exact symbolic
identity between the unknown real optimum and the real root.

Finite cloned controllers normalize to the same fractional model because
all capacities, provider counts, live stock and rank mass scale together.
Changed scalar words, entrance frames, cuts, width alphabets, pending-factor
capacities, ambient dimension, decoder or recurrence are outside the reviewed
claim. In particular, the earlier [free-concentration ceiling](PACKING-CEILING.json)
is valid but substantially weaker: it ignores indivisible helper widths.

Verification run:

```sh
python3 research/larger-gain/patterns/capacity_ceiling.py \
  --verify research/larger-gain/patterns/CURRENT-ALPHABET-EXACT-CEILING.json
```

Result: `PASS_EXACT_CAPACITY_PATTERN_UPPER_BOUND`.
