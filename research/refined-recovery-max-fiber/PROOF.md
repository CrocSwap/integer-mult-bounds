# The maximum fiber equals the zero fiber near the Fourier main term

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

## Setting

All objects are those of Nick Petalas's
[PR6660](https://github.com/CrocSwap/integer-mult-bounds/pull/6660)
(`research/refined-recovery-longer-chains`, head
`b6de532eff668a7daf8f2f98668f97af5af41338`), built on CubeJerry's PR6327 and the
112×8 matrix M of #5444. R is nearest-integer rounding with half ties away from
zero, and Q(s) = {q : R((s+56q)/52) = q}. The chain is z_1 = K(2x),
z_(j+1) = K(U_j z_j), with fixed frames U_j ∈ G, and W_j = (U_(j−1)⋯U_1)^(−1).
C = ker_F2(M mod 2) is the self-dual [8,4,4] code.

We use PR6660 §2 without re-proving it. With s = Mᵀy, the preimages of y are in
bijection with integer chains

    q_t ∈ Q(s),  q_(t−1) ∈ Q(s + 56 q_t),  …,  q_1 ∈ Q(s + 56(q_2+⋯+q_t)),   (1)

taken per mode coordinate, that satisfy the parity condition

    Σ_j (W_j M mod 2) q̄_j = W_t y  (mod 2).                                  (2)

Let Φ(v) = Σ_j (W_j M mod 2) v_j on (F2^8)^t, and let H = ker Φ. Since every
W_j M kills C modulo 2, H = {v : (v_j + C)_j ∈ D}, where D is the dependency space
of [#6828](https://github.com/CrocSwap/integer-mult-bounds/pull/6828), and
|H| = 2^(4t + dim D).

**Definition.** Define ε₀ by

    |fiber(0)| = 2^(dim D − 4t) · 13^(8t) · (1 + ε₀).

The right side without ε₀ is the main Fourier term of §1. Section 1 shows ε₀ ≥ 0.

## Theorem

Let ε* = (1/13) / ((23/12)^8 − 1) = 429981696/1012453046605 ≈ 4.2469·10⁻⁴.
For every depth t and every frame sequence in G with ε₀ ≤ ε*,

    max_y |fiber(y)| = |fiber(0)|.

**Corollary (depth 27).**

    min_U max_y |fiber(y)| = (1 + 12ρ₂^25 + 3ρ₂^26) · F^27 ≈ 15.7897746 · F^27,

that is, exactly 696 tag bits.

*Proof of the corollary.* For every frame sequence, max_y ≥ |fiber(0)|. #6828
proves that the minimum depth-27 zero fiber over all frame sequences is the stated
value, and that its FRAMES27.json frames attain it with dim D = 4. For those
frames ε₀ = 5.4537·10⁻⁶ < ε*/75. The theorem then gives max_y = |fiber(0)| for
them, which matches the lower bound. verify.py computes ε₀ exactly from the
closed form.

## 1. Fourier form

For one coordinate k, let c_k(π) be the number of per-coordinate chains (1)
whose parity string (q_(t,k) mod 2, …, q_(1,k) mod 2) equals π ∈ F2^t. The
interval at each stage depends only on that coordinate's own history, so the set
of chains (1) is a product over the 8 coordinates.

Let v* be any solution of (2). The fiber of y is then the sum over the coset
v* + H:

    |fiber(y)| = Σ_{v ∈ v*+H} Π_k c_k(v_{·,k}).

Poisson summation gives

    |fiber(y)| = 2^(dim D − 4t) · Σ_{h ∈ H^⊥} (−1)^(h·v*) · Π_k Z_k(h_{·,k}),

where Z_k(b) = Σ_chains Π_j (−1)^(b_j q_j) for b ∈ F2^t. Here H^⊥ ⊆ C^t, by
self-duality. verify.py checks this identity exactly on six random t = 2
instances, with tie and non-tie coordinates and random D.

For y = 0 every box is [−6,6] − 14W (PR6327), so Z_k(b) = 13^(zeros of b) with
positive sign. Hence

    |fiber(0)| = 2^(dim D − 4t) · 13^(8t) · (1 + ε₀),
    ε₀ = Σ_{h ∈ H^⊥, h ≠ 0} 13^(−wt h) ≥ 0.

## 2. Lemma 1: boxes

For s ≢ 2 (mod 4) there are no ties, and Q(s) = {q : |s+4q| < 26}. Then
Q(s + 56W) = Q(s) − 14W: the box is 13 consecutive integers, shifted by an even
amount.

For s = 4x + 2 we have r := q + x ∈ [−6,5]. In addition:

* r = 6 is included iff x ≥ 7 (class U);
* r = −7 is included iff x ≤ −8 (class L);
* neither is included for −7 ≤ x ≤ 6 (class N, a 12-element box).

*Proof.* (s + 56q)/52 − q = (s + 4q)/52. A tie occurs at s + 4q = ±26. At
r = 6 the value is q + ½, which rounds to q iff q + ½ < 0, iff x ≥ 7. At r = −7
the value is q − ½, which rounds to q iff q ≥ 1, iff x ≤ −8.

Along a chain, s_j = s + 56W gives x_j = x + 14W. With W′ = W + q this gives

    x_(j−1) = −13 x_j + 14 r.

So x_j ≡ x (mod 2) at every stage, and q_j ≡ r_j + x (mod 2). verify.py checks
the box description for |s| ≤ 3000.

## 3. Lemma 2: per-coordinate signed chains

* **Non-tie coordinates.** By Lemma 1 the boxes do not depend on the history,
  so |Z(b)| = 13^(zeros b) exactly.
* **Tie coordinates.** If |x| ≥ 8, then |x′| ≥ 20 and the class alternates
  between U and L forever (§2 recursion). So for x ∉ [−8,7] the boxes are again
  fixed 13-intervals up to even shifts, and |Z(b)| = 13^(zeros b).
* **The sixteen states x ∈ [−8,7].** Z is a product of 10×10 transfer matrices,
  one family per parity of x:

      Z_x(b) = ± (T_(b_t) ⋯ T_(b_1) 𝟙)_x,

  on {x ∈ [−8,7] of one parity} ∪ {U, L}. The entry T_b[x][y] is
  Σ (−1)^(b r) over the r leading from x to class y. verify.py checks this
  against direct chain recursion for all |s| ≤ 150 and depth ≤ 4.

  Normalize the b = 0 steps by 13. Then the U and L entries stay ±1, and each
  small state has at most one small successor. So the reachable set of
  normalized vectors is described exactly by an interval for each small state,
  given the pair (v_U, v_L).

  verify.py exhibits a family of such intervals with endpoints on the 1/12
  grid. The family contains the starting vector 𝟙 and is exactly closed under
  T_0/13 and T_1. Hence, for **every** t and every b,

      |Z_x(b)| ≤ c_x · 13^(zeros b),    c_x ≤ 23/12,

  with c_x = 1 for x ∈ {−8, −7, 6, 7}. So c_x > 1 occurs only in class N.

  The bound 23/12 is essentially attained: at depth 27 the supremum for x = −6
  exceeds 1.9166.
  It also shows the naive majorant fails: Z_(−22)(1,0,1) = 24 > 13.

## 4. Lemma 3: chain counts

Z_x(0…0) is the total number of chains. Every box has at most 13 elements, and
class-N boxes have 12. So a coordinate in class N at stage t has
Z(0) ≤ 12·13^(t−1), and every coordinate has Z(0) ≤ 13^t.

## 5. Proof of the theorem

Fix y. Bound the χ = 0 term of §1 exactly, and every other term by absolute
values:

    |fiber(y)| ≤ 2^(dim D − 4t) [ Π_k Z_k(0) + Σ_{h≠0} Π_k c_k 13^(zeros h_{·,k}) ]
               ≤ 2^(dim D − 4t) 13^(8t) [ Π_k Z_k(0)/13^t + (Π_k c_k) ε₀ ].

There are two cases:

* **No coordinate has c_k > 1.** Then every c_k = 1, and the bracket is at
  most 1 + ε₀. So |fiber(y)| ≤ |fiber(0)|.
* **Some coordinate has c_k > 1.** By §3 that coordinate is in class N, so by
  §4 the first product is at most 12/13. Also Π c_k ≤ (23/12)^8. The bracket is
  therefore at most 12/13 + (23/12)^8 ε₀, which is ≤ 1 + ε₀ exactly when
  ε₀ ≤ ε*.

∎

For direct sums at t = 26, ε₀ = (16F/13^8)^26 − 1 ≈ 0.0128 > ε*. Those are
covered by PR6660's box lemma instead. verify.py records this as a control.

## Scope

Exact for the interface of PR6660:

* fixed known frames in G;
* one relative precision bit before the first call;
* unbounded exact integers;
* complete output access.

The corollary uses two premises:

* #6828's exact depth-27 minimum and its realization by FRAMES27.json;
* PR6660's chain bijection.

Both are open and unmerged, and this package does not replay them. It supplies
no codec, physical tag, caller or restoration cost. κ, the selected frontier and
its five assumptions are unchanged. No independent human or proof-kernel review
is claimed.
