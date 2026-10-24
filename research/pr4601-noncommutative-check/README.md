# Literal check of #4601 on a noncommutative local algebra

**Task:** independent-moment (independent check). **Base:** canonical main `f626db5c`. **No κ is claimed.**

## The claim

petalas's #4601 (head `4b2322fc`) concerns finite products R of local K-algebras, with **no commutativity assumed**, and invertible 2×2 targets M in the two-role alphabet. The alphabet has paid factors I + u yᵀ (u ∈ R², y ∈ K²) and free maps in GL₂(K) anywhere. #4601 proves

```text
cost_R(M) ≤ 2  ⇔  cost_D(M̄) ≤ 2,      cost_R(M) = max(δ_R(M), cost_D(M̄)),     D = R/J.
```

Its census covers the commutative dual numbers (F₂[e]/e²)^k only.

## What is checked here

Costs are computed **literally from the definition**. There is no pivot test and nothing is imported.

- **Cost sets.** cost ≤ c means M lies in S_c, where S₀ = GL₂(K) and S_c = S_{c−1} · P · GL₂(K).
- **Right cosets suffice.** Conjugation by GL₂(K) permutes the paid factors: g P(u,y) g⁻¹ = P(gu, g⁻ᵀy). So only right-coset representatives of S_{c−1} need to be multiplied.
- **Invertible factors suffice.** M₂ of a finite ring is Dedekind-finite, so non-invertible factors can never appear in an invertible product.
- **Invertibility test.** A matrix is invertible exactly when v ↦ xv is injective on R².
- **Residue costs** are computed the same way over D.

Each ring is checked on every invertible target (k = 1):

| ring R (K) | D | invertible targets | cost 0/1/2/3 | targets where δ raises the cost above the residue cost |
|---|---|---|---|---|
| **F₄[e; Frobenius]/e² (F₂), noncommutative** | F₄ | 46,080 | 6 / 1,710 / 44,364 / 0 | 23,130 |
| F₂[x]/x³ (F₂) | F₂ | 1,536 | 6 / 270 / 1,260 / 0 | 1,530 |
| F₃[e]/e² (F₃) | F₃ | 3,888 | 48 / 1,536 / 2,304 / 0 | 3,840 |
| F₂[e]/e² (F₂), control | F₂ | 96 | **6 / 54 / 36 / 0** | 90 |

The noncommutative ring has multiplication (a + be)(c + de) = ac + (ad + bc²)e. The verifier checks that it is local, that its non-units form a two-sided ideal, and that it is genuinely noncommutative: ω·e ≠ e·ω.

## Results

- **#4601's formula holds on every target of every ring,** including the noncommutative one. So does the two-factor invariance cost_R ≤ 2 ⇔ cost_D ≤ 2.
- **Control.** The F₂[e]/e² histogram reproduces #4601's published k = 1 histogram [6, 54, 36, 0], from independent code.
- **Failure control.** The residue cost alone is wrong on many targets in each ring, as the last column shows. The δ term is therefore needed.

## Verify

```text
python3 -B research/pr4601-noncommutative-check/verify.py
```

The check takes about 4 s and uses the standard library only.

## Limitations

- **One component only.** Cost-three targets need k ≥ q + 1 components, and none arise here. So this package checks the radical-invariance and δ parts of the formula, including the noncommutative case, but not the three-factor regime. #4601's own (F₂[e]/e²)³ census covers that regime in the commutative case.
- **Not claimed.** A supplier or κ.

## Open next questions

- **Noncommutative three-factor regime.** Check it with T₄³ or a smaller noncommutative local algebra over F₂ with k = 3. First step: find the smallest noncommutative local F₂-algebra (order 16 is the candidate). Its k = 3 product has about 10¹⁴ targets, so a symmetry-reduced census is needed.

Credit: petalas (Nick Petalas) for #4601; ToikY (#4334), #4276 and Wentao Li (#4099) for the alphabet and its predecessor results. Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
