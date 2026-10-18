# A source-bound adapter fusion attempt

This attempts the single-complex-supplier repair on actual emitted source
operators. The result is negative for the concrete compilers below. It is
not a lower bound on arbitrary supplier constructions or globally fused
Clifford programs.

## Exact segment and inherited source

At commit `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, the file
`research/involutive-walsh-lift/evidence/WALSH-RETARGET-NATIVE.json.gz`
contains 2,896 native recipes and two literal 24,767-event local programs.
It is the emitted retarget of the selected historical local word, with the
same native ranks and scalar gates. Its exact operator and arbitrary-input
proofs are in that package's `NATIVE-PROOF.md` and `review_native.py`.

We select the entire canonical-frame interior between the `A` and
`exit_adapters` phase markers, source events 8107 through 17217 inclusive.
Each orientation has 9,111 events: 3,486 persistent climbs, eight centre
children, 5,613 scalar gates and four phase markers. There are no external
adapter or helper-normalizer events inside this chosen segment.
The exact native child inventory is

    {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8},

with rank mass 5,586. Every child occurrence is resolved by its exact
`(old frame, new frame, rank)` key to an emitted left/right monomial recipe.
The program uses 704 persistent and eight private scalar registers.

This scope includes the literal scalar chronology, rather than adding a
generic adapter allowance to a rank histogram. Initial and final canonical
layouts are preserved. External endpoint normalization, helper hosting,
global charts, idle work, scalar guards and the complete supplier are not
part of this segment.

## A concrete Fourier-only address compiler

A monomial factor is `P_A D`, where A is an affine binary address map and
D is its exact quadratic diagonal phase. These diagonal phases can be
evaluated on the indicated current addresses. Conjugating them through a
known affine map changes their exact quadratic formula; it does not make
them commute unchanged. The phase completion is proved algebraically
below; the executable synthesizes and replays affine maps and does not
materialize the completed phase program. These phases add no recursive
Fourier children. Their scalar scan and precision invoice remains an
explicit whole-supplier obligation.

For each actual 9-by-9 invertible linear matrix, the compiler constructs
four exact alternatives: column elimination, row-grouped LU elimination,
and reversals of those algorithms applied to the inverse matrix. A dense
rectangular block shear also receives its direct two-transform candidate.
It chooses the least target-weighted cost among these valid finite words;
this choice uses floating-point scores only to select a valid program,
never to certify its endpoint or a strict moment.

Each resulting binary row operation is checked on the complete matrix.
Consecutive shears are merged whenever their combined target set is
disjoint from every participating control. The merged rectangular shear
costs two Fourier children of rank equal to the number of targets, using
the exact identity in the main README. Each coordinate swap costs three
rank-two children using `(H_2 D)^3`. A translation on t selected coordinate
slots costs two rank-t native C children, since `C_t^2=X_all`.

These operations are generalized children on the specified selected axis
subsets. The count is favorable to this attempted repair: an all-size
physical compiler accepting those subsets without an additional gather
has not been supplied here. Every such child still has rank at most nine,
strictly below the selected ambient parent rank 73.

## Fusion through the actual scalar word

Three legal implementations of the segment are compared.

1. **Literal:** implement each emitted left and right adapter independently.
2. **Deferred, then flush:** maintain a pending affine address map per
   register; compose successive adapters, commute translations through
   native C children, and flush layouts before an incompatible scalar ADD.
3. **Deferred, relative alignment:** retain the same pending maps, but align
   one ADD operand to the other's current physical layout using a single
   relative affine map. Evaluate both directions with the concrete compiler
   and choose the cheaper one. Common-layout ADDs need no address operation.

The invariant is `desired register value = P_pending(stored value)`.
For an edge `P_L C_r P_R`, first implement the linear part of
`P_R P_pending`. Its translation commutes with every coordinate C factor,
so it is pushed into the new pending left map. Diagonal phases are
conjugated at their proper positions. For scalar ADD, the relative map
`P_target^-1 P_source` transforms the stored source into the target layout;
the opposite choice transforms the target instead. Both identities are
checked as exact affine maps at every occurrence.

Here is the phase placement explicitly. Write the full edge as
`(P_L D_l) C_r (P_R D_q)`, with constant phases included in the
quadratic Z4 functions `l,q`. For incoming pending affine map T, write
`R T(x)=M x+b`. In execution order on the stored array, apply

    D_(q composed with T), P_M, C_r, D_(l composed with X_b),

then leave pending map `L composed with X_b`. This follows exactly from
`D_q P_T=P_T D_(q composed with T)`,
`P_(RT)=X_b P_M`, and `C_r X_b=X_b C_r`.
It retains both constant phases as well as linear and quadratic terms.
The phase formulas are a proved completion of the affine replay, not an
independently emitted or verified scalar/phase ledger.

Scalar multiplication commutes with pending maps. COPY makes the target
inherit the source's pending map. CLEAR resets the private value and its
pending map. All remaining pending maps are actually returned at the end.
With that phase completion, fusion preserves the complete segment on
arbitrary values, including dirty helpers. It does not depend on values
being zero or tensor-separable.

## Result and its limits

The initial run gave these exact rank masses and diagnostic target moments
at `a=1/9`, normalized by `m=73` and `W/N=896/9`:

| Orientation | Literal | Deferred, flush | Deferred, relative alignment |
|---|---:|---:|---:|
| Forward rank mass | 294,446 | 259,814 | 239,648 |
| Backward rank mass | 294,574 | 259,942 | 232,198 |
| Forward target moment | 60.5071 | 54.0229 | 49.1179 |
| Backward target moment | 60.5311 | 54.0454 | 47.6197 |

`ADAPTER-RESULT.json` is authoritative for the current direct-block-shear
compiler as well. It records the complete combined child profile, exact
rank masses, operation counts, source hash and address-charge-schedule
digest (`program_sha256`) for every orientation and strategy. That digest
covers charged affine maps and their chosen words, not scalar coefficients
or diagonal phases; the source hash separately binds those original inputs.
The bare source interior itself already
fails at the 0.1 target; this compiler adds much more work than the
available budget. External/global work has not been charged.

Failure of each concrete compiled profile is exact: for `0<t<=1`,
`t^(8/9)>=t`, so its target moment is at least

    rank_mass / (73 * 896/9).

Every reported rational floor exceeds one by a large margin. The decimal
moments are only descriptive, and no floating calculation determines the
failure conclusion.

There is a more informative **restricted boundary obstruction**. After
relative-layout fusion, the backward word still has 5,619 nonidentity
linear adapter boundaries before final layout returns. If each of these
maps is independently synthesized on one array from nonzero diagonal
phases and native Fourier calls, it needs at least two nonzero-rank calls:
zero calls give a diagonal operator, while one Fourier call, with any
nonzero diagonal wrappers, has at least two nonzero entries in every row
and cannot be a permutation. Thus even granting every call the minimum
rank one and waiving every translation and endpoint return, these
adapter boundaries alone exceed the entire rank budget.

This last exclusion is deliberately narrow. It does not allow auxiliary
arrays, linear combinations of saved transforms, crossing a native child
boundary during fusion, or a changed physical frame assignment throughout
the scalar network. Those possibilities require a new program and are
not ruled out. It does establish that replacing Gaussian elimination by
a better independent diagonal-plus-Fourier synthesizer at the same
boundaries cannot repair this attempted recursion.

The next meaningful single-supplier attempt must therefore change the
global frame/compiler structure or provide a new finite word with far
fewer such boundaries. Merely compressing each existing address map is
insufficient in this restricted implementation model.

## Replay

    python3 -I -B research/kappa01-outer-repair/adapter_fusion.py

The verifier uses explicit requirements, also under `-O`, and authenticates
its exact source object. No predecessor or selected record is modified.
The inherited native recipes and Walsh-retarget proof are credited to the
`involutive-walsh-lift` package. This new finite compiler investigation used
OpenAI assistance, is Apache-2.0, and has no independent human review.
