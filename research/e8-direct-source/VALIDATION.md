# Reproduction and verification scope

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
PR647: `956bb581e7f97328e1b53baa5aca3d2490f2f607`.
Local checks on 2026-10-13 UTC, macOS arm64:

- Complete deterministic certificate on Python 3.9.6, 3.11.16 and 3.13.16.
- All 7088 independent live columns in each orientation, including arbitrary
  helper dirt, exact restoration and data endpoints.
- Every chronological frame move and scalar frame equality, all 3601 distinct
  local transition projectors, downward translations, and the final global
  rank-two projector's phase lowering.
- Exact scalar/child invoices and rational moment bounds. New slack at
  1/14100 exceeds 11/100; the old profile has strictly negative slack at
  that same value, certified with a moment lower bound.
- Seven mathematical negative controls, including early source access,
  missing dirty compensation/cleanup and an omitted center bill.
- Three tests on all three Python versions: 48 independent modular physical
  executions (12 characters, two fields, two directions), exact moment
  separation, and refusal of optimized execution before output creation.
- Selected-record integrity, source SHA256/Git blob authentication, workflow
  syntax, patch scope and whitespace checks.

The finite word is generated, not searched. The assignment seed 26 selects
source port 26 for adversarial read controls. Only this depth-one direct-source
rewrite was implemented; no exhaustive search or impossibility claim is made.
The complete recurrence and all retained interface assumptions are in PROOF.md.

The original PR647 package was freshly replayed during the immediately preceding
PR682 audit, at this exact unchanged source head; its full checker passed.
This contribution reuses that source evidence rather than repeating its unrelated
Fourier tests. The new construction and changed invoice are replayed fresh here.
The vendored phase/arithmetic utility code is reused openly; the primary checker
is not claimed to be a fully independent implementation of those utilities.
The modular physical interpreter is a separate arithmetic/phase execution check.

No full repository suite pass or formal proof is claimed. An earlier full
`make verify` attempt on the unchanged foundation stopped because the local
selected bit supplier requires unavailable Boost headers. The expensive suite
is not repeated for this isolated new package. Scoped Linux CI is provided and
its remote status is reported separately from local results.

Overlap was refreshed through PR692 (512 open PRs), including PR647's unchanged
head and empty comments. No pinned coordination issue existed. The local claim
records one result update. The earlier PR682 contribution checks the old tensor
profile; it does not implement this supplier rewrite. No existing repository
file, upstream source or selected certificate is changed.

Deterministic receipt SHA256: `c0fc7c08c5d707cdfb49693289d376a63dc148066ff9b25eb16a72cf95f46cc0`.
