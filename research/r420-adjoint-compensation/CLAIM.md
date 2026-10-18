# R420 adjoint compensation claim

- Track: independent verification, OS-random assignment seed 81.
- Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- Selected context: PR626 with PR543, conditional kappa
  `51110230636731/31250000000000000`. No new bound is proposed.
- Object: the 120 by 420 dirty-helper compensation matrix in the selected
  PR543 R420 native word. Check the raw A/scatter/B target map and equality
  with D by reverse covector propagation, independently of the supplier's
  forward all-column checker.
- Deliverable: a standalone standard-library verifier, exact matrix/cut
  certificate, rank and kernel information, rejecting controls, and proof note.
- Time budget: approximately 30 minutes from 2026-10-13 04:50 UTC. Finish by
  05:20 UTC, with the final 7.5 minutes reserved for verification and handoff.
- Coordination: GitHub returned no pinned issues. This is the local claim.
  Open PR titles and relevant bodies were inspected before claiming.

Three candidates considered were the R420 compensation identity, selected
complex cold-wrapper phases, and selected supplier moment bounds. PR702/712
cover the phase route and PR678/706 cover the moments. Seed 81 selects the bit
object and backward scalar method. PR612 checks typed R420 boundaries and
B-XOR target translation, but explicitly leaves D parity/compensation equality
open. The supplier's existing `xcheck.py` already checks that equality by a
forward symbolic replay. This work independently corroborates it with backward
covectors and an explicit matrix certificate; it does not claim that the
identity itself is new or that a Python check completes the Lean obligation.

Scope excludes frame legality, COPY/ERASE realization, hosting, costs, moments,
all-size compilation and the multiplication theorem. No existing supplier,
selected certificate, or `upstream/` file will change. Acceptance requires
exact equality for every target and every original input coordinate, source
binding, deterministic evidence, and controls that reject altered compensation
and incorrect transpose semantics.

Prepared for Sagar Thakrar (@thakrarsagar) with substantial OpenAI Codex
assistance. Apache-2.0; independent implementation is not independent human
peer review.

## Completed result and one scope pivot

Submitted [PR762](https://github.com/CrocSwap/integer-mult-bounds/pull/762).
The result is ten optimal nonadaptive dirty-input tests for compensation-row
errors of weight at most three, with an executable four-error blind witness.
The primary command passes 129 rejection controls. The separate support-set
and Boolean checker confirms the fixed baseline, all ten probes and malformed
suite rejection. See README.md and VALIDATION.md for exact scope and checks.

The initial queue scan ended at PR725. A later refresh discovered Joshua
Snider's PR731 at `cf5ff54a358b400a7e69abe941d1d0ad0944b25e`, which had
submitted the same adjoint/rank work with additional kernel evidence. The
planned rank certificate was removed and the scope pivoted once to the
optimal ten-test suite. This credits PR731 and adds a distinct result on the
test matrix, not another claim about its compensation kernel.

The pre-submission refresh covered 578 open PRs through PR759. No pinned
coordination issue existed, so this is the single local completion update.
No pending code was imported. Only this seven-file package was added.
