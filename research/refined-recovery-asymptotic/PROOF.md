# Refined recovery past depth 26: the optimum is asymptotically exact

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

## Setting and premises

The objects are those of Nick Petalas's
[PR6660](https://github.com/CrocSwap/integer-mult-bounds/pull/6660) (head
`b6de532e`). OPT(t) = min_U max_y |fiber(y)|, and α = 8·log₂13. The following
premises are cited and not replayed:

* **(P1) PR6660 (c).** All binary images N_j lie in one space V of dimension at
  most 104. Its FRAMES.json gives 26 frames whose images form a direct sum, so
  together they span all of V and dim V = 104.
* **(P2) [#6828](https://github.com/CrocSwap/integer-mult-bounds/pull/6828).**
  FRAMES27 has rank 104, and its zero fiber equals (1+12ρ₂^25+3ρ₂^26)F^27.
* **(P3) [#6848](https://github.com/CrocSwap/integer-mult-bounds/pull/6848).**
  If ε₀ ≤ ε* ≈ 4.25·10⁻⁴, then max_y |fiber(y)| = |fiber(0)|.
* **(P4) [#6849](https://github.com/CrocSwap/integer-mult-bounds/pull/6849).**
  Every frame sequence has |fiber(0)| ≥ 13^(8t)/2^104. For rank 104,
  |fiber(0)| = 2^(−104) 13^(8t) (1+ε₀) with ε₀ = Σ_{χ∈V^∖0} Π_j 13^(−wt h_j(χ)).

## Theorem

Let θ = ε₀(FRAMES27) = 5.4537·10⁻⁶. For every t ≥ 27,

    1  ≤  OPT(t) · 2^104 / 13^(8t)  ≤  1 + θ · 13^(−4⌊(t−27)/26⌋).

In particular, OPT(t)·2^104/13^(8t) → 1 exponentially fast. Moreover the
minimum tag is

    ⌈log₂ OPT(t)⌉ = ⌈8t·log₂13⌉ − 104   for every t ≥ 27.

This removes every sparse exception left by #6849, including t = 584,977.

## Proof

**Frames.** Take FRAMES27 for stages 1–27. Then append #6660's 26 direct-sum
frames, cycled. Each U_j ∈ G, because G is a group containing every W_j. The
rank stays 104 by (P1).

**Decay.** Fix χ ∈ V^∖0. In each complete cycle, χ is nonzero on some N_j,
because those images span V. There h_j(χ) is a nonzero word of C and has weight
at least 4. So every term of ε₀ gains a factor of at most 13^(−4) per complete
cycle, and no term grows. Hence ε₀(t) ≤ θ·13^(−4m) with m = ⌊(t−27)/26⌋.

Since ε₀(t) ≤ θ < ε*, (P3) gives max_y = |fiber(0)|. Then (P4) gives both
bounds. verify.py checks the decay claim exactly on eight random small instances.

**Tag bits.** The tag is undetermined only if 1 − {tα} < log₂(1+ε₀(t)) ≤ 2ε₀(t).

* For 27 ≤ t ≤ 1500, verify.py decides this exactly with big integers.
* For t > 1500, 2ε₀(t) ≤ 10^(−254.8).

The continued fraction of α = [29; 1, 1, 1, 1, 10, …] is computed to 700
digits. It gives convergents with q_414 of 200 digits, q_415 ≥ 10^200 and
‖q_414 α‖ ≈ 10^(−202). By the best-approximation property, every 0 < t < q_415
has ‖tα‖ ≥ ‖q_414 α‖ > 10^(−254.8). So no t in (1500, 10^200) is ambiguous.

For t ≥ 10^200 we use Laurent–Mignotte–Nesterenko (J. Number Theory 55
(1995) 285–321), Corollary 2. Here D = 1, α₁ = 2, α₂ = 13, log A₁ = 1 and
log A₂ = log 13. With b₁ = k and b₂ = 8t we have b′ = k/log 13 + 8t ≤ 20t. The
bound gives

    log|8t·log 13 − k·log 2| ≥ −24.34·(log(20t) + 0.14)²·log 13.

At t = 10^200 the right side is about −1.34·10⁷. The window's logarithm is
≤ log(2θ) − 4·log 13·⌊(t−27)/26⌋ ≈ −4·10^199. That side falls linearly in t, while
the right side falls only polylogarithmically, so the window stays below ‖tα‖
for every t ≥ 10^200. The margin is so large, a factor of 10^6 in the exponent
and far more, that any constant of this type would do. ∎

## Scope

Exact for the PR6660 interface:

* fixed known frames in G;
* one relative precision bit before the first call;
* unbounded exact integers;
* complete output access.

Premises (P1)–(P4) are open and unmerged, and are not replayed here. For
t ≥ 10^200 the LMN bound is cited, not formalized; the margin is enormous. The package supplies no
codec, physical tag, caller or restoration cost. κ, the selected frontier and its
five assumptions are unchanged. No independent human or proof-kernel review is
claimed.
