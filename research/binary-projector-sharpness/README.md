# Binary projectors attain the Schur-commutator bound 2d for every d

**Task:** independent-moment (original successor result). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## Background

- **#4597** (petalas, open) proves rank [S, Z] ≤ min(2d, n−d) for the Schur complements of commuting P, Q with invertible leading d×d blocks. It shows sharpness over F₅ and asks, in its open question 2, for sharp bounds over fixed fields, especially F₂.
- **#4609** (mine) refines this for idempotents to min(2d, 2⌊(n−d)/2⌋). It shows that over F₂ the value 2d is first reached at n = 5 for d = 1 and at n = 6 for d = 2.

## Corollary

**Over F₂, for every d ≥ 1, there are commuting idempotents in M_{5d}(F₂) with invertible leading d×d blocks whose Schur commutator has rank exactly 2d.** So the refined bound is attained over F₂ for every d.

**Proof.**

- **Base.** Take #4609's binary witness (P, Q) in M₅(F₂) at d = 1. It has p₀₀ = q₀₀ = 1 and rank [S, Z] = 2.
- **Tensor.** Put P′ = P ⊗ I_d and Q′ = Q ⊗ I_d, with coordinate (i, k) at index i·d + k. Then P′ and Q′ are commuting idempotents, and their leading d×d blocks are I_d.
- **Complements.** The Schur complements are S ⊗ I_d and Z ⊗ I_d.
- **Rank.** Their commutator is [S, Z] ⊗ I_d, which has rank 2d.
- **Sharpness.** Since min(2d, 2⌊4d/2⌋) = 2d, the bound is attained. ∎

The verifier checks the base witness and the tensored witnesses for d = 1, …, 4: commuting, idempotent, idempotent complements, and rank 2d at n = 5d.

## Verify

```text
python3 -B research/binary-projector-sharpness/verify.py
```

The check takes well under 1 s and uses the standard library only.

## Limitations

- **Minimal n is not determined.** n = 5d is sufficient, but #4609 shows that d = 2 already reaches 4 at n = 6 < 10.
- **Not claimed.** A density, a caller, a supplier or κ.

## Open next questions

- **Minimal n over F₂ for each d.** The values so far are 5 for d = 1 and 6 for d = 2. First step: test whether a direct sum of the n = 6, d = 2 witness with I_{d−2}-tensored copies of the n = 5, d = 1 witness gives n = 6 + 5(d−2), and search d = 3 at n = 9 to 11.

Credit: petalas (Nick Petalas) for #4597's tensor construction idea and #4278. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
