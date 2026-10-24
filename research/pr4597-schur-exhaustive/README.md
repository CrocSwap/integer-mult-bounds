# Exhaustive check of #4597's block Schur commutator bound on all commuting pairs

**Task:** independent-moment (independent check). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## The claim

petalas's #4597 (head `dfeb8ca7`) concerns commuting P and Q over a field whose leading d×d blocks A and B are invertible. It proves that the Schur complements S and Z satisfy

- **the identity** [S, Z] = XV − UY;
- **the bound** rank [S, Z] ≤ min(2d, n−d);
- **the equality criterion:** rank 2d exactly when [X U] and [V; −Y] both have rank 2d.

Its finite corroboration covers the polynomial families (P, P²) and one GL₄(F₂) orbit.

## What is checked here

This package covers **every commuting pair** in M₃(F₂), M₃(F₃) and M₄(F₂), and every split 1 ≤ d < n with A and B invertible. Nothing is imported from #4597.

- **Enumeration.** Pairs are generated as Q in the centralizer of P, a nullspace computed here.
- **Symmetry reduction.** P runs over orbit representatives under simultaneous block-diagonal conjugation by GL_d × GL_{n−d}. This preserves every quantity checked. Results are weighted by orbit size.
- **Totals.** The weights recover the exact number of commuting pairs: 7,456, 809,433 and 2,526,976 respectively.

## Results

The identity, the bound and the equality criterion hold for **every** admitted pair.

| domain | d | bound | admitted pairs | rank 0 / 1 / 2 | idempotent pairs, max rank |
|---|---|---|---|---|---|
| M₃(F₂) | 1 | 2 | 1,864 | 1,684 / 132 / 48 | 1 |
| M₃(F₂) | 2 | 1 | 1,104 | 1,104 / 0 / 0 | 0 |
| M₃(F₃) | 1 | 2 | 359,748 | 237,060 / 64,512 / 58,176 | 1 |
| M₃(F₃) | 2 | 1 | 267,840 | all 0 | 0 |
| M₄(F₂) | 1 | 2 | 631,744 | 428,128 / 140,112 / 63,504 | 1 |
| M₄(F₂) | 2 | 2 | 336,096 | 275,256 / 30,168 / 30,672 | 1 |
| M₄(F₂) | 3 | 1 | 241,248 | all 0 | 0 |

- **The bound is attained.** General commuting pairs reach min(2d, n−d) whenever it is at least 2: M₃ at d = 1 over F₂ and F₃, and M₄(F₂) at d = 1 and 2.
- **When n − d = 1**, the commutator always vanishes, as it must for a 1×1 commutator.
- **Finding, relevant to #4597's open question 2.** **Commuting idempotent pairs never exceed rank 1** in these exhaustive domains: F₂ with n = 3, 4 and F₃ with n = 3. The 2d bound is therefore not attained by binary or ternary projectors at these sizes, even where general commuting pairs attain it.
- **Positive control.** Over F₅, #4597's sharpness field, the verifier exhibits a commuting idempotent pair in M₃ with commutator rank 2 = 2d at d = 1. So the gap depends on the field, not on the code.

## Verify

```text
python3 -B research/pr4597-schur-exhaustive/verify.py
```

The check takes about 80 s and uses the standard library only.

## Limitations

- **Sizes.** Coverage is exhaustive only at n ≤ 4 over F₂ and n = 3 over F₃. This corroborates the written proof but does not replace it.
- **The idempotent finding** is an exhaustive statement at these sizes. It is not a theorem for larger n.

## Open next questions

- **Binary projectors.** Do commuting binary idempotent pairs reach commutator rank 2d at a larger n, or is there a field-dependent bound below 2d for F₂ and F₃? First step: enumerate commuting idempotent pairs in M₅(F₂) and M₆(F₂) directly, as simultaneously diagonalizable pairs M·diag·M⁻¹, with d = 1 and 2.

Credit: petalas (Nick Petalas) for #4597 and #4278. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
