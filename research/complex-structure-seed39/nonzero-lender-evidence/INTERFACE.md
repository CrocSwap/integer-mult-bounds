# Nonzero-lender correction interface

Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
Apache-2.0. This builds on Cinna Davis's PR2226 anticipatory borrowing, Sagar
Thakrar's PR2339 extension, and Jeremy Kothe's PR2269 emitter and native audit.
Base: `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`; PR2339 source head:
`bf1742aee4d855efb8bbd44a8419eddb33a679e5`; PR2269:
`b479fc5567bc09ab9185bffe89b62594f36d74e5`. Assignment seed39, helper644.

This note separates a legal correction interface from the existence of a
complete useful alias. It does not certify a new supplier or κ. The local
census and any later candidate must be evaluated separately.

## Positive flag-compatible early prelude

The revised interface avoids the immediate-handoff frame obstruction by
moving four existing target rank1 climbs before A. Independently checked
exact data are:

```
source33 entrance S = [138]
source33 retirement U = [266,138,75,30]
raised target frame T = [30]
handoff E = [504,30,95,20] = span([486,65,20,10])
G columns = [1,2,4,32,50,128,124,60,474]
```

G maps the flag `S⊂U` to `T⊂E`. After the ordinary entry adapters, raise
Y135, Y146, Y162 and Y220 from0 to T, warp source33 from S to T, add the
coefficients `(+1/2, −1/2, +1/2, +1/2)` respectively, and inverse-warp source33
back to S. These are exactly the target-precondition transport of final
correction `−K_G X33` at Y162 and `+K_G X33` at Y220. This source is still
its initial X33 input at this early point. The separate later lender
restoration operation remains required before the helper644 handoff.

All four targets' first touches in the pinned ext80 words are at T, and
all later target frames contain T. Their four rank1 calls are moved earlier,
not removed or added. The target levels at the center cut change from0 to T.
Centers9,92,224,240 contain T and each still serves other targets at0, so each
copy path changes `8→0` to `8→1→0`. The exact local copy-profile change is
`+4 H7 +4 H1 −4 H8`, with rank mass0. This may still worsen recursive cost:
equal rank mass is not equal recursive cost, and global pricing must include
the full profile.

Run the independent check:

```
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/check_flag_prelude.py
```

Expected: `PASS_INDEPENDENT_FLAG_PRELUDE_INTERFACE_NOT_NATIVE_ADMISSION`.
`FLAG-PRELUDE-INDEPENDENT.json` records all512 exact columns for the prelude
and handoff products (both nominated and canonical literal handoff bases),
source restoration, and the inverse-transpose two-register macro on512
source plus512 target columns. Wrong target line, omitted G and wrong inverse
scalar phase controls fail on all512 columns. Source SHA256 pins come from
the immutable PR2339 acquisition receipt.

This is positive evidence for a concrete interface, not a complete
construction. The chronological prelude must be represented in the actual
native program, with its target climbs, literal warp bases and new target
levels; the later source-restoration add must enter inverse cleanup. Whole
forward/dual replay, exact new paid profile, recursive labels, prefix/row
bounds, owner geometry and outer admission remain required. Neither original
monotone-frame checks nor initial-correction guards have been weakened here.

## A free read must match the actual frames

Write a logical register value as `z` and its physical value at frame `S` as
`A_S z`. A correction `y += c K_G z` into a target at frame `T` uses physical
operator `A_T K_G A_S^{-1}`. Its recursive rank is

```
r = dim(T) + dim(G S) - 2 dim(T ∩ G S).
```

Here the finite Clifford frame of `U` has Lagrangian
`L_U = {(x,x+p): x∈U, p∈U⊥}`. The exact symplectic action of `K_G` takes
`L_S` to `L_(G S)`. The intersection of `L_T` and `L_(G S)` has dimension
`h − dim(T) − dim(G S) + 2 dim(T∩G S)`, giving the displayed rank. Thus a
single correction is free exactly when `T=G S`. Equal dimensions alone or
containment alone is insufficient. This argument concerns Fourier rank;
actual scalar phases still require the native exact operator check.

The canonical emitter chooses handoff `E` as the first `dim(U)` basis vectors
of the helper's first-use frame `F1`. A different `E⊆F1` of the same dimension
is algebraically possible, provided the exact `G(U)=E` product is checked and
all later frames remain nested. For helper644 the observed first-use frame
has dimension4; any rank4 handoff therefore has the uniquely forced subspace
`E=F1`, regardless of the basis used to write it.

The proposed end-cleanup free shortcut fails this test. Actual target ends
are the distinct hyperplanes `port_i⊥` (dimension8), while an ordinary lender
restored by FULL cleanup is at dimension9. Because `G(FULL)=FULL`, each such
read has rank1. Targets are not at FULL. A cold restored helper instead has
a private zero buffer in FULL cleanup; that buffer is not its dirty input.
The actual ordinary lender is restored in place by inverse-reverse cleanup;
there is no separately copied dirty register available for free access.

## Delaying a correction requires target transport

Both pinned ext80 words have136 target-to-target additions and56 target
scales in the preconditioner, and136 target-to-target additions and56 target
scales in B. Their total target-only linear map is the identity. A, the
center COPY cut, restoration and cleanup have no target-to-target mixing.
Non-target registers do not read targets.

For a desired final target correction vector `d`, insertion at time `t`
requires `M_after(t)c=d`, where `M_after(t)` is the remaining target-only
matrix. Equivalently, moving an initial correction vector through a prefix
requires multiplying it by that prefix's target matrix. Checking only the
sign or scalar gain of one target misses the mixing terms.

The center COPY cut writes `Y += c center` with a source independent of Y,
so target correction translations commute through its logical action. The
physical copy path still requires the existing target frame and paid center
COPY calls. Moving a correction does not remove these calls.

A read of the original dirty input is legal only when the source actually
has that logical value, or when the full changed source row is included in
the exact compensation equation. A binary frame equality says nothing about
that scalar row condition.

## Dynamic correction at the handoff

Let the lender's complete free-operator row immediately before handoff be
`R`, including every variable and every operator word. The handoff makes
its row `K_G R` and changes its frame from `U` to `E`. Immediately afterward,
a scalar addition `target += c lender` is free when the target's current
frame is exactly `E`. This uses the already executed handoff; it needs no
extra warp or inverse warp.

Such a correction is valid when the final residual equals the target-suffix
transport of the inserted vector of `c K_G R` terms. Pristineness of `R` is
not necessary for this more general equation. An omitted nonzero term in R,
a correction copied from a pristine-lender experiment, or an untransported
target coefficient is not sufficient evidence.

Because the new correction writes only targets, the non-target history is
unchanged. Its inverse-reverse cleanup still restores the non-target inputs.
If a new source-restoration scalar operation is inserted before the handoff,
that operation must also be present, with its inverse, in the recorded
non-target cleanup history. Backward/dual replay must be checked separately:
it reads targets and updates the lender, even though the forward correction
does not.

Any early target climb to E must be legal relative to both its current and
future frames and must be included in the recursive profile. The existing
native schema does not yet encode a chronological correction event; a
validated new emitted program and independent native replay are still
required. A successful scalar diagnostic alone is not native admission.

## Explicit paid entrance round trip

There is also a mathematically explicit fallback when a lender really is
available and pristine. For a dimension-one entrance frame S:

1. Apply `A_S^{-1}` to the source (one rank1 recursive child).
2. Apply monomial `K_G`, add its value to all frame-zero correction targets,
   and apply `K_G^{-1}` to restore the source's zero-frame logical value.
3. Apply `A_S` to restore its original entrance representation (one rank1
   recursive child).

This uses the source itself and no private buffer; source restoration is
exact on arbitrary inputs. It costs `2 H_1` per distinct such source, in
addition to every later original call. It does not solve the separate
problem of finding or restoring an eligible lender.

The practical placement is after existing entry adapters and before A,
while all targets are still at frame0. Nonzero entrants require their
residual pre-wrapper before physical use. If the original correction was
specified before the preconditioner, its target coefficient vector must be
multiplied by that preconditioner before insertion here. Placing it before
its residual pre-wrapper would violate the actual native interface.

The current native checker accepts monotone ordinary climbs only. A paid
round trip requires an explicit descent primitive, both recursive labels and
orientations, the corresponding ascent, exact recursive profile accounting,
and new native validation. It is not implemented by removing a frame guard.
In fixed nine-stage accounting, the extra two units of local mass increase
`mass − helper_width` by2 and reduce the available deficit by `666×2=1332`;
the apparent local helper saving must not hide this expense.

## Reproducible independent checks

```
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/check_interface.py
```

Expected:
`PASS_INDEPENDENT_INTERFACE_CONDITIONS_NO_CANDIDATE_NO_NEW_KAPPA`.
The checker imports no predecessor implementation. It verifies all112
independent target columns of both words; their COPY source/target
separation; actual frame maps for all80 warps in each word; and rank1 for
all8960 FULL-lender/target combinations in each word. It also checks an
illustrative paid round trip on all512 complex coordinate columns using
Gaussian integers and a shared power-of-two denominator. Its test source
frame `[30]` is helper644's entrance frame and its G is one actual nontrivial
pinned warp; this is an interface illustration, not a nominated viable alias.

Negative controls reject omission of the descent, omission of the inverse
warp, reversal of the correction sign, and moving a correction across the
target preconditioner without transporting its coefficients. Source hashes
and exact failed-column counts are recorded in `INTERFACE-CHECK.json`.
Neither this finite check nor the rank calculation establishes the full
recursive theorem, a hosted supplier, an outer bound, or a new κ.


## Independent check of the immediate-handoff negative screen

```
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/check_dynamic_interface.py
```

Expected: `PASS_INDEPENDENT_DYNAMIC_FACTOR_SUFFIX_FRAMES_NO_FREE_HANDOFF`.
All44 recorded source-row/residual factorizations pass; the checker
independently reconstructs target suffixes and literal target frames from
the pinned canonical words and witness schedules. At immediate handoff the
four required target writes each have physical rank4 relative to E. Mutations
removing a residual column, changing a transported coefficient, or forging a
target frame are rejected. The source rows and residuals themselves are
reported diagnostic inputs, not independently regenerated by this checker;
its receipt makes that scope explicit. This finite immediate-slot result
does not exclude the flag-compatible early prelude above.


The subsequent four-alias implementation has separate exact operator and
compiler-interface checks in `COMPILER-REVIEW.md` and
`FOUR-OPERATORS-INDEPENDENT.json`. Its operators differ from the original
single-helper illustration above; use their actual pinned G records rather
than copying the illustrative G into the four-alias word.
