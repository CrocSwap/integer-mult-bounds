# Local sprint claim

- Track: independent verification; OS-random seed **80**.
- Base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`.
- Object: the selected #741 backward local scalar endpoint, including all
  728 native and eight arbitrary private-center input columns.
- Method: independent modular matrix replay over pairwise coprime odd
  Fermat-number moduli, with exact dyadic denominator and positive-envelope
  bounds proving deterministic reconstruction. No primality assumption.
- Deliverable: read-only exact certificate, bound proof and adversarial
  controls that defeat modular replay without its height guard.
- Expected finish: 06:50 UTC, 2026-10-13; hard stop before 06:54 UTC.

Three candidates: (0) dual-annihilator frame checks, overlapping #777;
(1) cyclic-resultant CRT, overlapping #668; (2) bounded modular endpoint
reconstruction. Seed `80 % 3 = 2` chose the third; even parity selects the
backward orientation. This is a different arithmetic implementation of an
already accepted finite endpoint, not a new construction or theorem claim.

Read current contribution instructions, selected #741/#589 certificate,
construction/provenance and maintainer review, PR ledger and earlier negative
results. Inspected open PR metadata through #830 and modular/CRT-related
claims. #668 concerns cyclic resultants, not this endpoint; #777 concerns
frame geometry. No pinned sprint issue exists, so this is the local claim.

Ryan Haines (@Ryan-Haines), with substantial OpenAI Codex assistance.
Apache-2.0. Result and handoff will be recorded once after verification.

## Result and handoff

Completed: [PR #835](https://github.com/CrocSwap/integer-mult-bounds/pull/835).
All 736 input columns pass exact reconstruction using two coprime odd
moduli. The endpoint denominator bound is 19 and the scaled residual bound
is 1582669748628115714804285440; the modulus product exceeds twice this.
Seven controls reject, including a mutant invisible to both modular replays
but rejected by the height guard. Windows normal/optimized, Linux, Ruff and
whitespace checks pass. No new kappa; only the backward scalar projection.

Final overlap scan through #834 at 06:51 UTC found no equivalent endpoint
reconstruction. No pinned coordination issue exists. This is the single
result update to the local claim. Initial research commit: `6b0b090`.
The workspace also retains `sw4-crt-s80.patch` and `sw4-crt-HANDOFF.txt`
with the final commit, patch hash and reproduction command. Full sprint
handoff is in `SPRINT-HANDOFF.txt`. Work ends before the requested cutoff.
