# The second-order term of the refined-recovery optimum decays at exactly 4·log₂13 bits per stage

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

## Setting

We use the notation of [#6851](https://github.com/CrocSwap/integer-mult-bounds/pull/6851)
and its predecessors. OPT(t) = 2^(−104)·13^(8t)·(1+ε_t), where ε_t = min_U S(U)
and

    S(U) = Σ_{χ ∈ V^, χ ≠ 0} 13^(−W(χ)),   W(χ) = Σ_j wt h_j(χ),   h_j(χ) = χ∘φ_j ∈ C.

#6851 proved the following:

* **Jensen.** ε_t ≥ (2^104−1)·13^(−4t·2^104/(2^104−1)) for every frame
  sequence.
* **First moment.** ε_t ≤ E_t, which decays at about 4 bits per stage.

It left the exact rate open, somewhere between 4.0 and 14.8 bits per stage.

## Theorem

    lim_{t→∞} −log₂ ε_t / t = 4·log₂13 = 14.8018…

Quantitatively, ε_t ≤ (2^104 − 1)·13^(−w_t) for the certified values w_t below.
It is valid whenever w_t > 0.

| t | 60 | 100 | 200 | 400 | 1000 |
|---|---:|---:|---:|---:|---:|
| w_t | 80 | 200 | 532 | 1236 | 3444 |
| w_t / t | 1.33 | 2.00 | 2.66 | 3.09 | 3.44 |
| log₂ upper bound on ε_t | −192 | −636 | −1865 | −4470 | −12640 |
| log₂ Jensen lower bound | −784 | −1376 | −2856 | −5817 | −14698 |

## Proof

**The upper rate is at least 4·log₂13.** This uses PR6660's frame family, as in
#6851: φ_j = μ + ψ_j with ψ_1 = 0 and ψ_2, …, ψ_t uniform and independent.

* **χ with a nonzero R′-component** (2^104 − 16 of them). Here h_2, …, h_t are
  independent and uniform on C. Write X for the weight of a uniform word of C:
  it is 0 with probability 1/16, 4 with probability 14/16 and 8 with
  probability 1/16. For 0 < r ≤ 1, Markov's inequality applied to r^W gives

      P(W(χ) < w) ≤ r^(−w) · m(r)^(t−1),   m(r) = E[r^X] = (1 + 14r⁴ + r⁸)/16.

* **The other 15 χ.** Their W is 4t or 8t, which is at least w whenever w ≤ 4t.

If (2^104 − 16)·r^(−w)·m(r)^(t−1) < 1, a union bound shows that some choice of
the ψ_j has W(χ) ≥ w for every χ ≠ 0. That choice has S ≤ (2^104 − 1)·13^(−w).
verify.py certifies the largest such w (a multiple of 4) with exact rational r
for each tabulated t.

For the limit, fix c < 4. Then f(λ) = λc + log m(e^(−λ)) has f(0) = 0 and
f′(0) = c − E[X] = c − 4 < 0. So some r = e^(−λ) < 1 gives r^(−c)·m(r) < 1. Then
(2^104−16)·r^(−ct)·m(r)^(t−1) → 0, so w = 4⌊ct/4⌋ is admissible for all large t,
and liminf −log₂ε_t/t ≥ c·log₂13. verify.py exhibits exact certificates r for
c = 3, 3.5, 3.9 and 3.99. As a control, no r works at c = 4, because
r^(−4)·m(r) ≥ 1 by AM–GM.

**The lower rate is at most 4·log₂13.** This is #6851's Jensen bound.

Each frame sequence in the table has S below #6848's threshold, so its max fiber
equals its zero fiber. The bound therefore controls OPT(t) itself. ∎

## Interpretation

Every nonzero character must accumulate total weight close to the average 4t.
A random member of PR6660's frame family achieves this, because W(χ) is a sum of
independent weights. #6851's first-moment rate of 4 bits per stage came from
rare characters with W ≈ 0. Rare means probability about 16^(−t) each; the union
bound removes them once t is large enough. The convergence of w_t/t to 4 is slow:
it is 3.44 at t = 1000.

## Scope

The premises are cited and not replayed here:

* PR6660's frame family and dimension cap;
* #6848's max-fiber theorem;
* #6849's and #6851's Poisson and Jensen statements.

All of these are open and unmerged. The upper bound is existential. The package
supplies no codec, physical tag, caller or restoration cost. κ, the selected
frontier and its five assumptions are unchanged. No independent human or
proof-kernel review is claimed.
