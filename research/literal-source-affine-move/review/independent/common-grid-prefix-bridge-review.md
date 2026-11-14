# Cross-review: common-grid prefix bridge

## Pins and conclusion

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.

- Retained premise: `docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md`, Git blob `3dd1af2285e597676725e85ad4f65e7ad326d695`, SHA-256 `4501502c2ceb9759b20372435fe4beb51082c5a5e2910c1fd5dbe6edca415055`.
- Reviewed application: `root-work/common-grid-prefix-bridge/PROOF-DRAFT.md` (local proposal; no external source substituted).

**Conclusion: the complete-prefix closure argument is valid under its retained full-root hypotheses.** No new precision theorem or actual producer theorem follows. One partial-memory sentence should be read narrowly, as specified below.

## Why the closure is licensed by #7000 §5

The retained §5 ideal row has the form

`y = sum_nu c_nu U_nu x_nu`,

where each `U_nu` acts on the same complete `D`-bit root factor and has the retained Gaussian-dyadic Clifford form. Its numerator-grid and component-magnitude bounds are uniform over that Clifford class, for the source-specific coefficients, complete input rows and exterior unfinished-context debt fixed by the section.

Let `V_j` be a completed mathematical prefix acting as one exact Clifford on an injectively selected subset of those same `D` root coordinates, with identity on every other root coordinate. Then

`V_j y = sum_nu c_nu (V_j U_nu) x_nu`.

The class is closed under multiplication. `V_j` changes neither `c_nu`, `x_nu`, the outer ROW fiber nor any exterior coefficient/context. The product still acts on the same complete root factor, so the uniform §5 estimate applies without adding a new per-gate denominator or magnitude debt. This includes an arbitrary fixed finite number of complete prefixes; no bound is obtained by multiplying a per-gate error term.

The source operations cited in the draft fit this mathematical class: CNOT, affine X, S, CZ and Gaussian-unit phase are Clifford operations; the positive central matrix

`C = 1/2 [[1+i,1-i],[1-i,1+i]] = H S H`

is itself a Gaussian-dyadic Clifford. A coordinate reordering is allowed only if it is a bijective relabeling of the entire retained factor; projecting away a complementary root coordinate, mixing an external control into the root operation, or replacing the row by an arbitrary rational isometry would invalidate this application.

Thus the assertion that each **completed exact C-prefix output** is on the retained grid and inside the same signed `W` range is redundant, conditional on the actual row already satisfying every #7000 §5 source-specific premise.

## Partial-memory limit

The theorem controls the complete vectors `V_j y`; it does not make a fine-grained physical instruction prefix a Clifford image. A buffer during an in-place scan may mix old and new addresses. The draft's “completed component values” statement is valid only when each cited value is a fully assembled numerical component already committed from either the preceding or next complete prefix.

It does not cover partially written component words, add/divide accumulators, partially updated descriptor encodings, or any helper scratch. Those may lie outside the endpoint row invariant and must be bounded by the relevant literal helper and widened-scratch proofs. I recommend making “fully assembled and committed” explicit next to “at each position”; the later scratch caveat is necessary and must remain.

## What remains conditional

The bridge does not produce the row/view/header or prove that a particular selected source packet lies in the §5 admissible class. A valid actual producer must still establish the complete-root representation, common grid, source coefficients/debt, owner/header, cutoff and physical entry promises. Paid packing/unpacking, B1 routing, initialization/erasure, literal helper costs, history and nonleaf tariff remain separate. This is a premise-reuse lemma only; it proves no selected framework assumption by itself.
