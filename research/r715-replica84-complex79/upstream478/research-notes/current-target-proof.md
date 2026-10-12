# PR473 target interval factors

Pinned source: PR473 commit 6095681095a1caeedb9b7ad3ab31ac6a0cb81221; canonical source SHA-256 cb12976c73d1570bb16d87786ae93d23e607dd9f1aa48abf1eae08247a1b9439.

The first layer applies fourteen disjoint target-donor interval factors. During each interval let the original receiver increment be U and donor increment V. Setup receiver += donor; replacing the receiver increment by U+V; and recovery receiver += donor returns the receiver to its exact original value, since (u+d)+(U+V)+(d+V)=u+U over F2. This holds for arbitrary initial values of every register. The donor is restored trivially because it is never written. Each selected factor removes one common helper increment and adds two target reads. The remaining word, including all helper operations and hosting interface fields, is identical.

The changed target paths are checked against the pinned rational frame geometry. Every visited frame contains its predecessor, and every integer-clean operand support lies in its frame. The portable checker audits all 955 independent binary dirty columns, exact rational frame ranks, and rejects each of 28 separate setup/recovery omission mutants. These finite audits do not replace the root's native signed/formal-column compilation audit.

The exact local paid-rank delta is {1:-14,4:-14,5:+14}. For every exponent 0<a<1, strict subadditivity gives 5^a < 1+4^a, so the changed recursive moment is strictly smaller at fixed rank mass. This is a sufficient exact moment improvement; the outer kappa is obtained only by the retained full assembly and its paid scalar bill. There are 28 additional scalar target reads.

Selection: SELECTION473.json. Constructor: D:/proof/research/kappa-next-tensor-20261011/scheduling/schur_constructor.py. Candidate: F:/proof/kappa-round-next-20261011/scheduling/first-layer/word.json; SHA-256 e2ab3c0c4f25e78f96f14a548a795adaefda5bacbb01cd0ea61950f029aadf63.

Priority: this is a new checked selection on PR473, using an inherited target-prefix/interval technique. It is not evidence of a globally new algebraic method. A second one-donor layer returned zero positive nominees. A separate bounded two-donor interval search is recorded independently.

## Bounded extension screen results

1. A further one-donor interval layer enumerated 157,002 intervals,120 legal paths,zero positive nominees.
2. General two-donor intervals enumerated22,697,181 intervals,440 legal paths,zero positive nominees. The implemented sufficient identity replaces receiver increments U with U+V1+V2, wraps by receiver += donor1+donor2 at common setup/recovery frames, and leaves both donors unchanged. Its failure to improve this instance does not disprove other multi-target basis constructions.
3. Shared-donor two-receiver blocks checked28 candidate pairs with exact complete-word replay. All28 were legal; none improved the paid moment. This checks whether merging the donor's chronological frame path beats pricing the factors separately.

The final deliverable should retain the positive14-factor selection and record the two broader mechanisms as tested research, not achieved gains. Source-only structural analogue: Mathlib/LinearAlgebra/Matrix/SchurComplement.lean, Matrix.fromBlocks_eq_of_invertible11 (the Unicode subscript spelling in Lean), gives block LDU elimination. Mathproof/Meta/TISLTransvectionWord20260908.lean commutator3 gives the elementary three-index transvection identity. Neither was freshly kernel replayed in this round, and neither substitutes for the actual finite word and cost audits.
