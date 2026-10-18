# Compatibility and finite integration proof

Alluri, with substantial OpenAI Codex assistance; Apache-2.0. The component
constructions and original proofs remain attributed in their retained packages.

## The D boundary, including arbitrary target and helper inputs

The original frame-zero prefix acts as `(x,y,s) -> (x,y+K s,s)` over F2.
PR694 chooses 201 disjoint helper transvections with product H. Each is an
involution and the disjoint factors commute, so H^-1 = H. Its middle matrix
is K H. The prefix H, middle additions K H, and suffix H restore all helper
inputs and implement the same complete D operator.

Apply PR713's target-row method to **K H**, not K. For its 56 disjoint target
transvections let P be their product, P^-1 = P. The combined execution is:

1. Helpers become H s; targets become P y.
2. Add `(P K H)(H s)` to the targets.
3. Restore targets with P and helpers with H.

The resulting targets are `P(P y + P K H H s) = y + K s`. Sources never change.
Every preparation, restoration and middle addition is counted. The verifier
reconstructs the matching from the transformed matrix and checks the full D
operator on all 660 columns using sets, independently of the producer's row
masks. It tests arbitrary targets as well as arbitrary helper dirt.

The literal old H2 condition excludes helper destinations and target reads in
D, so we do **not** label the actual new syntax H2-compliant. Instead we check
all original H1-H5 predicates and conclusions on the exact new A/B/C word
with the canonical old D, and then substitute the complete equal D operator.
The new D is wholly at frame zero, uses only targets/helpers already there,
restores every helper before A, and has no external read interleaved inside it.
This is the explicit semantic boundary required by PR686/694/713. Original
checkers and their rejection rules remain unchanged. Native common-frame,
source-owner and multistage checks additionally consume the actual new word.

## A/B substitutions and cleanup

PR691 replaces one phase-A quad by its complete equal map. PR670 and PR674,
composed by PR688, replace two disjoint phase-B windows. PR708 shares operands
in the final retained-total computation at FULL and restores every operand.
A subset of its disjoint pairs has the same restoration argument as the full
matching. Each substitution preserves the complete map on its boundary,
including arbitrary incoming helper data; composing them requires no assumption
that their incoming data are independent or clean. The integration checks
exact equality of the complete A operators, all scalar dirty-input columns,
and every physical register frame path.

B slices are replaced in descending original-index order. Literal inverse C
is rebuilt after the final A/B edit. Missing gates with correctly rebuilt
cleanup are negative controls, avoiding a test that only detects stale C.
The paid profile, nine copies, helper count and all original labels remain
unchanged. No change to the recursive exponent follows from fewer scalar ADDs.

## Compatibility includes precision

Naively composing all 27 PR708 pairs with the other edits needs 105 bits under
the inherited local signed-prefix formula `64 F^3 R^2`; its 18,370-ADD count
is therefore **rejected** under the existing strict bound `< 2^104`. All 27
leave-one-out variants also fail. A deterministic finite greedy pass evaluates
372 one-pair extensions, minimizing total additions then payload among valid
extensions. It retains 23 pairs, reaches 18,378 ADDs, and stops when none of the
four remaining pairs fits. No global or local optimum is claimed.

The resulting F=253149, R=4334338 give
`19505369118995241654063407203584 < 2^104`. Independent unchanged C++ replays
recompute both bounds on the exported instruction stream. The complete hosted
program must then be repriced; a local cap alone does not preserve its old
invoice. The global raw prefix rises from 189 to 196 bits and its charged
allocation from 192 to 256. The recomputed two-level coefficient bound rises
from 416 to 432 bits, still within the same charged 512 bits. Both are reported.
The unchanged invoice engines check the finite bill and identical paid profile.

## Complex lowering and its composition with PR681

PR696's source-copy Horner lowering and unit-coefficient shortcut preserve the
complete scalar macro boundary, including arbitrary incoming private work and
zero work on exit. Its primitive-state containment proof preserves the old
prefix envelope. The imported verifier checks all four selected CK/JP8 words,
all 716 data/helper columns and all encountered coefficients.

PR681 separately proves the full rational maps, frames, cleanup and four local
orientations for all fourteen raw factory windows. We freshly reconstruct both
raw words, then lower **each actual emitted scalar event** using PR696. The
rational primitive replay proves both full raw orientations; coefficients
encountered in these raw words get their own local containment checks. Count
and primitive-stream digest comparisons bind the emitted opt-in artifacts to
the streams that were replayed. No addition of independent headline savings
is used: combined raw forward primitives are 123768, not 118504.

These raw factory edits are not transported through selected provider recipes.
The selected complex results apply only the lowering; the separate raw result
applies both transformations. Non-scalar phase, climb and adapter events remain
literal. The emitted primitive artifacts contain one real-component stream;
reported complex primitive bills charge two components.

## Proof boundary

Exact finite identities, chronology, restored arbitrary dirt, emitted streams,
precision bounds, whole-owner placement and finite bit invoices are checked.
The old original H2 contract is retained for historical packages; this opt-in
integration supplies a sufficient semantic substitution argument.
The selected certificate and κ remain unchanged. The hosted price's cited
PR484 outer arithmetic is a historical control, not a new selected assembly.
All inherited all-size compiler, common-label/mutable-basis realization,
physical hosting, uniform precision/tape and analytic assumptions remain.
This is not a formal proof of the full multiplication theorem, a practical
runtime benchmark or a new exponent claim.
