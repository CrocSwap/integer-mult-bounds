# Projector refinement of #4597's block Schur commutator bound

**Task:** independent-moment (original successor result, a partial answer to #4597's open question 2). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## Background

petalas's #4597 (head `dfeb8ca7`, open) proves the following for commuting P, Q with invertible leading d×d blocks:

- the Schur complements satisfy rank [S, Z] ≤ min(2d, n−d);
- S and Z are idempotent when P and Q are;
- the bound is sharp over F₅.

Its open question 2 asks for sharp bounds for projectors over a fixed field, especially F₂.

## Results

### 1. Parity theorem (written proof below; any field)

If S and Z are idempotent of odd size, then [S, Z] is singular. Hence, for commuting idempotent P and Q,

```text
rank [S,Z] ≤ min(2d, 2⌊(n−d)/2⌋).
```

This is strictly smaller than #4597's bound exactly when n−d is odd and n−d ≤ 2d. Example: n = 5, d = 2, where the bound drops from 3 to 2. The refinement needs idempotence. A general commuting pair over F₂ at n = 5, d = 2 reaches rank 3.

### 2. Minimal dimensions for sharpness at small fields

All "max" values in this table are exhaustive over every commuting idempotent pair. Every "rank" entry is an explicit verified witness.

| field | d = 1, target rank 2 | d = 2 |
|---|---|---|
| F₅ | reached at n = 3 | rank 2 at n = 5, which equals the refined bound |
| F₃ | n = 3: max 1; **first at n = 4** | — |
| F₂ | n = 3, 4: max 1; **first at n = 5** | n = 4: max 1; rank 2 at n = 5 (refined bound); **rank 4 = 2d at n = 6** |

So the refined bound is attained over F₂ at (n, d) = (5, 1), (5, 2) and (6, 2). Over very small fields, attaining it needs more room than over F₅.

## Proof of the parity theorem

**Setup.** Let A = F̄⟨s, z⟩/(s² − s, z² − z), and let u = (s − z)². Then u is central:

```text
su = s − szs = us,  and similarly for z.
```

**Small quotients.** On a simple A-module M, u acts as a scalar λ by Schur's lemma, so M is a module over A/(u − λ). In that quotient:

- szs = (1 − λ)s and zsz = (1 − λ)z;
- sz + zs = s + z − λ.

So the quotient is spanned by 1, s, z and sz, and has dimension at most 4. By Jacobson density, End(M) is a quotient of it. Hence dim M ≤ 2.

**One-dimensional factors.** On a 1-dimensional module, s and z act as scalars, so c = sz − zs acts as 0.

**Conclusion.** Let V = F̄^k with idempotents S and Z. Then C = [S, Z] lies in the image of A and preserves a composition series of V, so det C is the product of its determinants on the composition factors. If C is invertible, no factor is 1-dimensional. Every factor then has dimension 2, so k is even. Finally, apply this to the idempotent Schur complements S and Z, which have size n−d. ∎

The verifier also checks:

- the centrality of u on every idempotent pair in M₃(F₂) and M₃(F₃);
- singularity on every idempotent pair in those algebras, whether or not the pair commutes;
- singularity on 3,000 random idempotent pairs each in M₅(F₂), M₅(F₃) and M₅(F₅).

## Verify

```text
python3 -B research/schur-projector-refinement/verify.py
```

The check takes about 50 s and uses the standard library only.

## Limitations

- **Minimal dimensions** are established only where an exhaustive negative is shown: n ≤ 4 over F₂ and n = 3 over F₃. Larger cells have witnesses only.
- **Not settled.** A closed-form sharp bound for every field and every (n, d). For instance, it is open whether F₂ reaches 2d for every d once n is large enough. Fixed projector ranks are not separated.
- **Not claimed.** A header density, caller, supplier or κ.

## Open next questions

- **Binary sharpness for all d.** Is min(2d, 2⌊(n−d)/2⌋) attained over F₂ for every d once n ≥ 3d? First step: tensor the n = 5, d = 1 binary witness with I_d, following #4597's tensor construction, and test whether the Schur structure survives.

Credit: petalas (Nick Petalas) for #4597 and #4278. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
