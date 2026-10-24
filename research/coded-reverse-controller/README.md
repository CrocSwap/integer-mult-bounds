# A consumer for the center-free coded native word: coded reverse stages, A⁻¹-mixed query shears

**Conditional construction with exact formal and arithmetic checks. No κ is promoted and no physical replay is claimed.**

PR #4929 removes the eight rank-8 owned-center children per FULL call (64 rank mass) but changes the main
endpoint to `Y ← Y + A X`, `A = I − RᵀR/4 = I − 14P`: symmetric, zero diagonal, eigenvalue 1 on 104 modes and −13 on 8.
Its open question is a caller that can use this code without spending the saving. This package gives one.

## The construction

In the query-thinned path controller every thick stage is a *reverse* call except the two end stages; all
even stages are forward query shears. Take

* every reverse stage = the center-free **backward** word (coupling `−A·Q`), no centers;
* **every** forward stage, including both ends, = a query-only shear whose source is first mixed by `A⁻¹ = I + (A−I)/13`
  (scalar adds into the owned copy `Z`; the 112 rank-one jobs are unchanged).

Then the reverse/forward coupling product is 1 on every mode, so the controller is the standard one in new variables:
`Coded = (A on x-roles) · Standard · (A⁻¹ on x-roles)`. Only the x-roles are converted, only at the controller boundary:
`×A` (dyadic) at the input, `×A⁻¹` (denominator 13) at the output. With thick stages = odd stages only, the invoice is
the published one with the center bill removed and p+1 query stages.

## What `verify.py` establishes (exact)

* `A = I − RᵀR/4` for the joint-query packet; `(A−I)(A+13I)=0`; `A⁻¹ = I+(A−I)/13`.
* The coded controller diagonalizes after thinning, for p = 3, 4, 5, 8, with **exactly the standard outputs**; the only new
  boundary denominator is 13. Controls: coded reverse with uncoded forward stages, coded forward end stages, and a wrong
  inverse code all fail to diagonalize.
* The identity `Coded = (A on x) · Standard · (A⁻¹ on x)` holds exactly as 448×448 matrices (p=2) with the real 112×112 code.
* Arithmetic (same moment model as the published invoice, which it reproduces to 13 digits): raw complex root
  **0.00793 (p=8), 0.00758 (p=19)** versus 0.0030218. At p=19 the three strict tail guards pass at C=0.0034
  (α=0.99579, γ=0.9638, δ=0.9516; p=8 fails δ). The repo's strict outer ledger (54 + 4 predicates) accepts every κ up to
  **0.0033999971** and first fails at 0.0034 only on `actual_bit_above_effective`. So the complex side stops binding and the
  BIT supplier (admitted 0.0034) caps κ at **+12.5%** over 0.0030217758 (+12.6% over 0.00302015).

## What is not established

1. **Physical admission of the three scalar mixings.** They are free scalar adds only if the mixed registers share a frame:
   the thin-stage sources are the X bank, whose exit frame is the same full frame for all ports (113 distinct main finals =
   112 Y hyperplanes + one shared full frame); the input conversion acts at the ground frame; the output conversion at the
   full frame. This bookkeeping is checked from the frame data but no physical phase/Clifford replay was run, and the community
   has flagged port-dependent charts for the *forward* word (which this design never uses as a thick stage).
2. **Denominator 13** (thin-stage mixing and output conversion): needs pricing (cf. the division-free Word-RAM transfer
   #4630). The design tolerates ~0.5 extra paid rank-one jobs per port per query stage and still exceeds +10%; it tolerates
   essentially no paid boundary conversions.
3. The complete compiler for the new invoice (ambient rank 153; the published tensor power 1024 / log power 1000 violates
   the shifted-capacity inequality at TESTED≈0.0034 and must be re-tuned, e.g. v ≤ 920), BIT-side hypotheses, hosting and precision.
4. No independent human or kernel review.

## Overlap

Same source word as #4929 and the same open question as the caller work in #4933 (Discussion #4930, which leaves the
negative-query banks as coded outputs and names an affordable decoder or recursive interface as the next theorem) and
#4932 (a standalone one-bank adapter needs 112 grade-two channels). This package takes the other branch: never decode the
reverse stages; conjugate the controller so only the x-roles at its boundary and the thin-stage sources are recoded.
Whether those recodings fit the scalar/monomial bill priced in #4933's PHYSICAL.md, and whether #4932's heterogeneous-entrance
bound reaches the thin-stage mixing, are exactly open question 1 below. The raw complex root 0.0076 agrees with the
~0.00765 planning estimate in #4933.

## Reproduce

```sh
python3.12 -B research/coded-reverse-controller/verify.py     # ~3 minutes, standard library only
```

Credit: Dugongue (#4929, the center-free coded word), Cinna Davis (#4694 center-free kernel; #4440 query thinning; #4470),
Cao Yifan (#4610), zxv, Jacob Alan Sussman and the retained lineage. The code, the controller engine and the outer ledger are
theirs; the delta is the coded/inverse-coded stage assignment, its exact diagonalization and the arithmetic above.

## Open next questions

See `TASK.json`: (1) a physical replay of the thin-stage mixing and the two boundary conversions at the actual frames;
(2) a priced implementation of ×1/13; (3) the compiler constants for ambient rank 153 and the full outer transfer.

AI assistance: derivation, scripts and package by Claude (Anthropic) under the author's direction; no independent human or kernel review.
