# Explicit near-optimal refined-recovery frames at depths 28–30

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

## Statement

FRAMES28.json, FRAMES29.json and FRAMES30.json give explicit integer frame
sequences in PR6660's family W_j = I + V_jE, with W_1 = I. For each of them,
verify.py checks four things exactly:

* MᵀV_j = 0 and E V_j = 0, so every U_j = W_(j+1)^(−1) W_j lies in G;
* the binary images of W_j M have total rank 104, so dim D = 4t − 104;
* S = 2^104·|fiber(0)|/13^(8t) − 1, computed by enumerating all of D (2^8, 2^12
  and 2^16 elements);
* the Poisson identity |fiber(0)| = F^t Σ_{a∈D} Π ρ(a_j) = 2^(−104) 13^(8t) (1+S),
  in exact rationals.

| t | S (exact, rounded) | previous bound on ε_t | improvement |
|---|---:|---:|---:|
| 28 | 2.7245·10⁻⁷ | θ = 5.454·10⁻⁶ (#6850, explicit) | 20× |
| 29 | 5.0073·10⁻⁹ | E₂₉ = 2.476·10⁻⁴ (#6851, existential) | 4.9·10⁴× |
| 30 | 5.0460·10⁻¹² | E₃₀ = 1.548·10⁻⁵ (#6851, existential) | 3.1·10⁶× |

Every S is far below [#6848](https://github.com/CrocSwap/integer-mult-bounds/pull/6848)'s
threshold ε* ≈ 4.25·10⁻⁴. So each sequence has max_y |fiber(y)| = |fiber(0)|.
Combined with [#6849](https://github.com/CrocSwap/integer-mult-bounds/pull/6849)'s
lower bound, this gives

    2^(−104)·13^(8t) ≤ OPT(t) ≤ 2^(−104)·13^(8t)·(1 + S_t),   t = 28, 29, 30,

**attained by explicit frames**.

## How the frames were found

Write φ_j = μ + ψ_j. Here ψ_j sends the four η-basis vectors to elements of R′,
the mod-2 span of the 100 integer kernel vectors of Mᵀ that vanish on E. The
search started from uniform random ψ_j, which is #6851's ensemble. It then ran a
greedy local search, replacing one column at a time and keeping a change when
the exact objective decreased and the rank stayed 104. The frame files record
each column as a subset of the integer kernel basis, which verify.py recomputes.
verify.py does not trust the search; it certifies the stated properties from
the integers alone.

## Why the values drop so fast

S is the weighted count Σ_{χ≠0} 13^(−W(χ)). Random frames leave about 2^(104−4t)
characters with very small total weight W. Local search removes them, and the
remaining minimum-weight characters dominate. The observed decay from t = 28 to
30 is about 5.8 and then 10 bits per stage. That is already past #6851's
existential rate of 4 bits per stage, heading toward #6852's asymptotic
4·log₂13 ≈ 14.8 bits per stage.

## Scope

These are upper bounds by explicit construction. The exact minimum of S at
t ≥ 28 remains open; the lower bound is still the main term. The premises are
cited and not replayed here:

* PR6660's frame family and dimension cap;
* #6848's max-fiber theorem;
* #6849's Poisson identity.

All three are open and unmerged. The package supplies no codec, physical tag,
caller or restoration cost. κ, the selected frontier and its five assumptions are
unchanged. No independent human or proof-kernel review is claimed.
