# Concurrent analytic improvement

The final overlap check read PR1025 at commit
`6ef2168ac90d42926bceb7ac9b2e029463800c76` on 2026-10-13.
Chafik Boukhalfa's [pinned proof](https://github.com/CrocSwap/integer-mult-bounds/blob/6ef2168ac90d42926bceb7ac9b2e029463800c76/research/averaged-cyclotomic-height/PROOF.md)
uses averaged cyclotomic coefficient heights to replace the inherited
circle exponent by

    d = 1 + 2ell + (r-1) phi(r) min(r,8ell^2).

Its precision corollary applies this bound to the retained PR862 and
PR977 clean-scratch estimates. It retains that solver's 40L record
interface. It does not supply a dirty-array circuit or a new inverse
execution. These are statements of that contribution's scope, not an
independent verification of its analytic theorem.

This package instead proves the effective-depth identity, nonlinear
error transfer, and inverse-preimage integer guard for the actual
PR985 target-dependent dirty word. It retains all structural recursion
and two-tape costs. Its explicit cubic budgets use the older pinned
analytic input. They remain sufficient; they are not a claim of the
best available analytic exponent or a minimum working width.

The theorem in Sections 4 and 5 of `PROOF.md` takes the margin and
common-operator subset bound as inputs. A later contribution can check
PR1025's analytic proof, substitute its exponents into this dirty
contract, derive new explicit integer and fractional inequalities,
and execute representative prepared kernels at those widths. This
package does not claim that combined result. No new dependency or
changed budget was added after the source freeze.

## PR985 accounting successor

PR985 advanced to `da1cdf8ed4ac9b1b8378dfec73f77ff4e81a4f70` during
verification. The coordinator reports that this successor applies the same
two read-once validation corrections and retains the mathematical receipt.
Its public head was checked on 2026-10-13 at 17:11 UTC.

This package intentionally retains the exact consumed predecessor,
`9df42a99dd8497b6e7d46cd2507bb89071372640`, in `vendor/pr985/`. The
derived solver contains the two read-once corrections and its separate
effective-depth admission. The independent array observer rejects the old
double-read behavior. No moving dependency was imported after verification.
