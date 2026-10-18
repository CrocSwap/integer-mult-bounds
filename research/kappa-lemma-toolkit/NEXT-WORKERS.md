# Applying the library to the newly reviewed frontier

The 2026-10-15 03:17:29 UTC snapshot includes PR #2279. These are sufficient
applications of existing proved interfaces, not claims that other PRs have
already been formalized or independently validated by this package.

## T74 anticipatory borrowing: PR #2269

[PR #2269](https://github.com/CrocSwap/integer-mult-bounds/pull/2269) reports
conditional kappa approximately 0.0016962471390584742, crediting Cinna Davis's
PR #2226 anticipatory borrowing. Its T74 supplier differs from this package's
T73 owner witness. Preserve that distinction when reusing the following APIs.

- Instantiate `rational_upper_certificate` with the actual nonnegative paid
  counts, real analytic weights and pointwise rational upper enclosures from
  that supplier. Use its own normalization and strict budget; the theorem
  proves the real weighted-sum bound from those sufficient inputs.
- Use `admission_with_reserve` when a changed profile's certified saving must
  pay an additional setup or stock reserve. All added and removed children,
  including changed bad-residue costs, belong in that actual inventory.
- Use `bootstrap_target_of_power_bound` for a concrete fixed-depth bootstrap
  after binding its initial rate, recurrence parameter and target. The
  31-stage witness here does not certify the different 39-stage calculation
  reported in #2269.
- Use `step_monomial_natural`, `framed_add_decode` and
  `framed_dirty_relay_restoration` to prove the phase, separate source/target
  frame and dirty-restoration algebra of a proposed alias. Literal owner
  chronology, nonoverlap, cost and complete restoration still require the
  actual new physical witness. A T73-to-T74 change is not an owner transport
  proved by these theorems.

For further profile concentration, `admission_of_batch_concentration` provides
a universal sufficient moment comparison. A proposed transfer must also have
a valid physical realization, and transfers sharing a bin must be accounted
for as the actual final profile rather than independent simultaneous moves.

## Borrowed-source Gray fanout: PR #2271

[PR #2271](https://github.com/CrocSwap/integer-mult-bounds/pull/2271) gives a
closed mask walk with arbitrary source values and a 13-versus-21 row-XOR bill.
The next useful formal result is a closed-walk invariant: after each source
transition the anchor holds its original value plus the current mask, each
target write adds its intended linear form, and the final anchor is restored.
`framed_add_decode` and `framedKernel_comp` supply the frame-sensitive ADD
algebra, also over characteristic two. The desired source contribution in
the Gray anchor must be retained; the dirty-relay theorem cancels a nuisance
dirty offset and by itself does not prove this 13-step tour. Its row-XOR bill
also remains separate from physical hosting and tape execution charges.

## Scope of the other new PRs

PR #2273's static read-set analysis reinforces the distinction between source
provenance and mathematical validation. This package separately replays its
literal chart, family and chronological owner checks. Our theorem library does
not certify the static analyzer. The root-code/CR2 claims in #2272, #2274 and
#2277, the exact scatter optimum in #2279 and the cache optimization in #2276
are different results. In particular no unrestricted odd-geometry decoder
floor withdrawn in #2277 is an assumption of this library.
