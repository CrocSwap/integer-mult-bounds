# Proof design and adversarial scope notes

**Source-only mathematical/Lean handoff.** This document explains the proof
represented by `TargetWriteFiniteImage.lean`; it is not a kernel-pass receipt.
The new executable proof source is the main deliverable. The existing prose
rank lemma is credited, not claimed anew.

## 1. Why a row certificate bounds the correct image

Write `D = I XOR P`. From the pinned PR1598 theorem, for a restoring word
with `m > 0` target writes, use exactly these concrete values:

- `G = retainedDonors y w`, the tail of the chronological **raw pre-gate**
  donor-occurrence list; `length G = m - 1`.
- `C r = reducedCoefficients y w r`, the actual reduced scanner mask for
  output row `r`; `length (C r) = length G`.
- `combination G (C r) = D r` for every output row `r`.

Those are conclusions of the existing theorem, not new assumptions on a
word. The reusable auxiliary factorization theorem accepts that exact-length
certificate, and the actual-word theorem discharges it from PR1598.

For a full arbitrary input `x : Fin n -> Bool`, define

```
q(v,x) = XOR_{c=0}^{n-1} (v(c) AND x(c)).
```

This is a scalar. `matrixAction D x` is the output vector whose coordinate
`r` is `q(D r,x)`. Define the donor measurement list

```
B_G(x) = [q(G[0],x), ..., q(G[k-1],x)],       k = length G.
```

Boolean distributivity, explicitly proved in the source, gives

```
q(combination G (C r), x)
  = XOR_{i=0}^{k-1} (C(r)[i] AND B_G(x)[i]).
```

The right side is the coordinate `r` of `decode C (B_G(x))`. Thus the actual
map factors as

```
(Fin n -> Bool)  -- B_G -->  k Boolean measurements  -- decode C --> (Fin n -> Bool)
```

with `matrixAction D = decode C o B_G`.

This is **not** an assertion that the output vector lies in the row span of
`D`, nor is `D` silently transposed. The intermediate vector consists of
scalar evaluations of its row generators. No row-rank/column-rank equality
is used. All columns, including the initial target column, occur in every
measurement definition.

The source also proves `matrixAction (identity n) x = x` for arbitrary `n`
and `x`, by splitting `List.finRange (n+1)` into coordinate zero and successor
coordinates. Consequently it proves the actual defect action equals
`x XOR (P*x)`. The zero-dimensional identity proof is vacuous; a word theorem
with a distinguished target never assumes an inhabitant of `Fin 0`.

## 2. A literal injection into a bounded finite ordinal

The executable list code is

```
code([]) = 0
code(b :: bs) = bitNumber(b) + 2*code(bs).
```

List induction proves `code(bs) < 2^(length bs)`. A second induction proves
that two lists of the **same length** with equal codes are equal. At the
cons step, a difference in the leading bits would equate an even integer
with an odd one; equal leading bits allow cancellation of the factor two.
The source uses ordinary `omega` proof production for these natural-number
arithmetic steps, not native evaluation of quantified examples.

For a fixed generator list, every measurement list has the same length `k`.
Therefore `inputCode G x : Fin (2^k)` has a proved bound, and equal input
codes imply equal measurement lists, hence equal actual outputs by the
factorization theorem.

An important direction issue remains: this does **not** mean equal outputs
have equal input codes. In general they do not. We therefore do not quotient
input codes by output equality or claim they are automatically well-defined
on the image.

Instead, the actual image type is

```
{ z : Row n // exists x : Row n, matrixAction D x = z }.
```

For each such output choose one witnessing input, using `Classical.choose`.
Its code is the image code. If two image codes are equal, the corresponding
chosen inputs have equal measurements, hence equal output vectors. Their
witness equations identify those vectors with the two original image
values. `Subtype.ext` then gives equality of the image elements. This is an
injection into `Fin (2^k)`, for **any** choices of the witnessing inputs.

Choice is an explicit foundational dependency, not a cardinality assumption,
computational oracle, or replacement for the actual row certificate. Only
this witness-selection step is noncomputable. The forward map, measurements,
decoder, and code of a supplied input are concrete executable functions.

Substitution of `k = m-1`, from the unchanged source theorem, gives the main
positive-case result. Natural-number exponentiation occurs in the actual
codomain `Fin (2^(m-1))`; it is not a newly named surrogate for conventional
rank.

## 3. Zero writes and exact hypotheses

The source theorem `zero_target_restored` gives `P = I` when the full raw
endpoint is identity and `targetCount = 0`. Consequently every defect row
is zero and every actual defect output is zero. Conversely, zero is an
actual output, witnessed by the zero input. This yields the exact singleton
image theorem and the constant injection into `Fin 1`.

The combined declaration `restored_image_bound` removes only the separate
positivity assumption by performing this explicit case split. Its exponent
uses natural subtraction, so `m=0` gives `2^(0-1)=2^0=1`. It does not try to
apply a positive-count donor-tail argument to an empty donor list.

Every word retains the original `Gate` distinct-endpoint constraint. Repeated
raw donors are retained as repeated occurrences. Target-source gates are
allowed and remain in chronological projection. Full raw restoration is
an equality of the full matrix, not a helper-block equality or a clean-target
specialization. Extra dirty registers are unrestricted and unbounded.

## 4. Small controls and what they actually establish

The source adds eight formal fixture declarations. They await compilation,
like the universal theorems. The separate Python tests were actually run;
those logs are supplemental and cannot certify Lean elaboration.

**Orientation:** the imported three-register commutator fixture has defect
`E_(b,a)`. On input `e_a` the actual output is `e_b`. Transposition instead
makes the tested `b` output bit zero. The formal positive and negative
fixtures evaluate this same action.

**Dirty target:** for the imported two-register feedback word
`(y+=a; a+=y)^3`, the defect is `E_(a,y)`. It maps `e_y` to `e_a`, while zero
input maps to zero. These inputs agree on the sole helper coordinate. Any
implementation that silently cleans or deletes the target input loses the
observed output.

**Noncanonical measurements:** in that same word the actual retained donors
are `[e_y, e_a XOR e_y]`. Zero input and `e_a` both have zero defect output,
but their measurement lists are `[false,false]` and `[false,true]`, with
codes 0 and 2. The fixture demonstrates why witness selection, rather than
an unjustified quotient of input codes, matters.

**Length:** `[]` and `[false]` share code zero. The equal-length hypothesis in
the binary-code injectivity theorem is essential and is explicitly present.
All actual measurement lists, and all source coefficient lists used in the
bridge, carry the appropriate length equalities.

**Zero writes:** the nonempty word `[a+=y; a+=y]` restores the full raw matrix
without a target write. The formal fixture uses the universal singleton-image
theorem. The Python controls additionally check repeated donor occurrences,
a one-register empty word, extra dirty spectators, and retained-gate order.

The finite factorization tests range only over `0<=n,k<=2`, independently of
any word search. They test the new row-to-image algebra and coding on all
such small generator/mask choices. They are not an exhaustive treatment of
all words or a substitute for any quantified theorem.

## 5. Boundaries deliberately not crossed

No `Fintype.card`, vector-space dimension, conventional finite-field rank,
row-rank/column-rank theorem, or comparison of numeric dimension APIs is
formalized. The exact supported formulation is the displayed finite-ordinal
injection. Its elementary set-theoretic interpretation is an upper bound on
the number of distinct actual outputs, but no additional library-equivalence
theorem is advertised.

The optional three-cycle necessity corollary is left open in this successor.
There is no formalized helper-cycle specification, no resulting three-write
lower bound here, no five-register reduction, no BFS, no 13-gate optimality,
and no supplier/frontier/kappa/geometry/multiplication result.

Mathematically, the bridge described above resolves the row/action orientation
obstacle without dimension machinery. Mechanically, source acceptance in the
operator's exact installed Lean remains the outstanding validation step.
If elaboration fails, preserve and return the first exact diagnostic and
source hash; do not relabel the unaccepted source a kernel theorem.

## 6. Attribution and source pins

All artifact work here is AI-assisted formalization, not independent human
review. Credit Andrey Mas and substantial GPT-6 Pro assistance for the written
lemma and concrete execution theorem; separate Codex coordination and local
verification are not recast as mathematical proof development. This successor
was developed through this ChatGPT conversation at the requested setting,
without independent backend-model attestation. Preserve the precursor
credits Gareth Davidson / @bitplane PR1420 and @woklerx PR1105.

- PR1598 dependency, head `96ef13e9c0aada8730ace8624fde2de1e3ddb1b9`:
  https://github.com/CrocSwap/integer-mult-bounds/blob/96ef13e9c0aada8730ace8624fde2de1e3ddb1b9/research/target-write-row-certificate/TargetWriteCertificate.lean
- PR1546 written source, section 2, commit `0980a7c266532b42ccda3d77bf61b5cf18be9054`:
  https://github.com/CrocSwap/integer-mult-bounds/blob/0980a7c266532b42ccda3d77bf61b5cf18be9054/research/projected-three-cycle-minimum/proof.md
- PR1420: `d19a944897714f2ecae72720b7dafc3e256f2f8d`; mathematical commit
  `dc6ba012c92470ea830e3b0ff2dab28fbd8126d8`.
- Public coordination was supplied by the operator; nothing was posted here:
  https://github.com/CrocSwap/integer-mult-bounds/discussions/1548#discussioncomment-18915295
- Pinned Lean core API consulted for `List.finRange` and its successor split:
  https://github.com/leanprover/lean4/blob/d024af099ca4bf2c86f649261ebf59565dc8c622/src/Init/Data/List/FinRange.lean
- Pinned Lean core API consulted for `Fin.cases`, successor injectivity, and
  Boolean/natural-number lemmas:
  https://github.com/leanprover/lean4/tree/d024af099ca4bf2c86f649261ebf59565dc8c622/src/Init

These references identify source lineage/API consultation, not independent
replay of the repository or verification of historical search claims.

SPDX-License-Identifier: Apache-2.0
