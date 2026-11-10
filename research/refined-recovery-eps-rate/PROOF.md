# The second-order term of the refined-recovery optimum decays at 4 to 14.8 bits per stage

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

## Setting and premises

The objects are those of Nick Petalas's
[PR6660](https://github.com/CrocSwap/integer-mult-bounds/pull/6660) (head
`b6de532e`). Let V = red₂(ker_ℤ Mᵀ) be the 104-dimensional space containing
every image N_j (PR6660 (c)), and let μ = M mod 2 on Q = F2^8/C. For a frame
sequence define

    S(U) = Σ_{χ ∈ V^, χ≠0} Π_j 13^(−wt h_j(χ)),   h_j(χ) = χ∘φ_j ∈ C.

By Poisson summation ([#6849](https://github.com/CrocSwap/integer-mult-bounds/pull/6849) §1),

    |fiber(0)| = 2^(−104) · 13^(8t) · (1 + S(U))

for every frame sequence. S < 1 forces rank 104, because a deficient rank adds
1 for each χ vanishing on the span. Then S equals the ε₀ of
[#6848](https://github.com/CrocSwap/integer-mult-bounds/pull/6848). Hence

    OPT(t) = 2^(−104) 13^(8t) (1 + ε_t),   ε_t := min_U S(U),

whenever some U has S(U) ≤ ε* ≈ 4.25·10⁻⁴. In that case #6848 gives
max_y = |fiber(0)| for that U. For every other U the max fiber is at least
|fiber(0)|.

## Theorem

Let q = 16F/13^8 / 16 = (1 + 14·13^(−4) + 13^(−8))/16. For every t ≥ 29,

    (2^104 − 1) · 13^(−4t·2^104/(2^104−1))  ≤  ε_t  ≤  E_t := (2^104 − 16) q^t + 14·13^(−4t) + 13^(−8t).

So −log₂ ε_t / t lies between 4 − log₂(16F/13^8) = 3.9993 and 4·log₂13 = 14.8018,
asymptotically. At t = 29, E_t = 2.48·10⁻⁴. #6850's periodic construction gives
a decay of 13^(−4/26) per stage, about 0.57 bits per stage; this improves it to
4 bits per stage.

## Upper bound: random frames, exact first moment

Use PR6660's frame family W_j = I + V_jE, where V_j has four integer columns
with MᵀV_j = 0 and E V_j = 0, and W_1 = I. Modulo 2 this gives
φ_j = μ + ψ_j with ψ_j = V_j ∘ η, where η = E M mod 2 is an isomorphism
Q → F2^4. The column space R′ (the mod-2 reductions of the integer kernel of
Mᵀ on rows ∉ E) has dimension 100, and V = im μ ⊕ R′. verify.py computes both
from the pinned M. So ψ_2, …, ψ_t range over **all** linear maps Q → R′.

Draw them independently and uniformly, and write χ = (χ₁, χ₂) ∈ (im μ)^ × R′^.

* **χ₂ ≠ 0.** h_j = χ₁∘μ + χ₂∘ψ_j is uniform on C and independent for j ≥ 2,
  with E[13^(−wt h)] = q. Stage 1 contributes 13^(−wt χ₁∘μ). Summing over χ₁
  gives (2^100 − 1)·16q·q^(t−1).
* **χ₂ = 0, χ₁ ≠ 0.** h_j = χ₁∘μ for every j. These are the 15 nonzero words of C
  (14 of weight 4, one of weight 8).

Hence E[S] = E_t exactly, and some choice has S ≤ E_t. By Markov's inequality,
at least half of all choices have S ≤ 2E_t.

verify.py checks the identity E[S] = formula exactly by full enumeration in toy
dimensions dim R′ ∈ {1, 2} and t ≤ 4, using the real code C and the real η.

## Lower bound: Jensen, all frames

For each j, χ ↦ h_j(χ) is a linear surjection V^ → C, since φ_j is injective.
So every word of C is hit 2^100 times, and

    Σ_χ Σ_j wt h_j(χ) = t · 2^100 · Σ_{h∈C} wt h = 4t · 2^104.

Since x ↦ 13^(−x) is convex, Jensen over the 2^104 − 1 nonzero χ gives the
lower bound. verify.py checks the weight identity and the bound on random toy
instances.

## Consequences

* OPT(t) = 2^(−104) 13^(8t) (1 + ε_t) with ε_t ≤ 2.48·10⁻⁴·16^(−(t−29))·(1.0005)^(t−29).
* "Most" frames of the family are near-optimal: half of them are within 2E_t.
* Pinning the exact rate needs either better codes than random ones or a
  linear-programming lower bound on S.

## Scope

The premises are cited and not replayed here:

* PR6660's dimension cap and frame family;
* #6848's max-fiber theorem;
* #6849's Poisson identity.

All three are open and unmerged. The package supplies no codec, physical tag,
caller or restoration cost. κ, the selected frontier and its five assumptions are
unchanged. No independent human or proof-kernel review is claimed.
