# An overlap floor for refined recovery chains at depth t ≥ 27

Prepared for apoursh with substantial Anthropic Claude assistance. Apache-2.0.

## Setting

All objects are those of Nick Petalas's
[PR6660](https://github.com/CrocSwap/integer-mult-bounds/pull/6660)
(`research/refined-recovery-longer-chains`, head
`b6de532eff668a7daf8f2f98668f97af5af41338`). That package builds on CubeJerry's
PR6327 and uses the 112×8 matrix M of #5444 from
`research/precision-state-frontier/FIXTURE.json`. The chain is z_1 = K(2x),
z_(j+1) = K(U_j z_j), with fixed frames U_j ∈ G = {U ∈ GL_112(ℤ) : MᵀU = Mᵀ}.
The code C = ker_F2(M mod 2) is the self-dual [8,4,4] code, and
F = W_C(13,1)/16 = 51,008,161.

PR6660 proves that the optimal worst-case fiber is exactly F^t for t ≤ 26 and
strictly larger for t ≥ 27. Its open question 1 asks for the exact optimum at
t ≥ 27, and its suggested first step is to minimize the zero-fiber kernel
formula over overlap patterns. This note bounds that minimum from below for
**every** overlap pattern and every t ≥ 27, and pins it at t = 27.

We use two results from PR6660 and do not re-prove them:

* **(Z) Zero fiber, its §5.** With N_j = im_F2(W_j M mod 2),

      |fiber(0)| = Σ_{u ∈ ker} Π_j 7^(8−wt u_j) 6^(wt u_j),
      ker = {(u_1,…,u_t) ∈ (F2^8)^t : Σ_j W_j M u_j ≡ 0 (mod 2)}.

* **(c) Dimension cap, its §6.** Every N_j lies in one fixed binary space of
  dimension at most 104.

## 1. Coset form of the zero fiber

Since W_j M kills C modulo 2, membership in ker depends only on the cosets
a_j = u_j + C ∈ Q := F2^8/C ≅ F2^4. Grouping (Z) by cosets gives

    |fiber(0)| = Σ_{a ∈ D} Π_j S(a_j),   S(a) = Σ_{u ∈ a} 7^(8−wt u) 6^(wt u),

where D = {(a_j) ∈ Q^t : Σ_j φ_j(a_j) = 0} and φ_j : Q → N_j is the induced
isomorphism. By (c), dim D = 4t − dim(N_1+⋯+N_t) ≥ 4t − 104.

verify.py computes the 16 coset sums exactly from C, which it derives from M:

* S(C) = F;
* S(a) = 50,983,170 on the 8 odd-weight cosets;
* S(a) = 50,979,600 on the 7 nonzero even-weight cosets.

The even-weight cosets together with C form a plane E ⊂ Q of dimension 3. Write
ρ(a) = S(a)/F, so ρ(0) = 1, ρ = ρ₁ = 50983170/F off E, and ρ = ρ₂ = 50979600/F
on E∖0. Then 0 < ρ₂ < ρ₁ < 1, and

    |fiber(0)| = F^t · Σ_{a ∈ D} Π_j ρ(a_j).                              (1)

## 2. Theorem

Let μ_d be the minimum of Π_{x ∈ F2^d∖0} ρ(ℓx) over all linear maps
ℓ : F2^d → Q. For t ≥ 27, every frame sequence, and every 1 ≤ d ≤ 4t − 104,

    |fiber(0)| ≥ F^t · (1 + (2^d − 1) · μ_d^(t/(2^d − 1))).               (2)

For d ≥ 3, μ_d = ρ₂^(2^d − 2^(d−3)), attained exactly by the rank-3 maps onto E.
Also μ_1 = ρ₂ and μ_2 = ρ₂³. Hence the optimal maximum fiber
min_U max_y |fiber(y)| is at least the right side of (2). It is at most
A_t = (13^(8t) + 14·13^(4t) + 1)/16, the identity-frame value of PR6327 (U_j = I is
a valid frame).

*Proof.* Choose a d-dimensional subspace D′ ⊆ D, possible since dim D ≥ d.
Parametrize it by an injective linear map x ↦ (ℓ_1x,…,ℓ_tx) from F2^d. Every
term of (1) is positive, so

    Σ_{a∈D} Π_j ρ(a_j) ≥ Σ_{x ∈ F2^d} P(x),   P(x) = Π_j ρ(ℓ_j x).

The term x = 0 equals 1. By AM–GM over the 2^d − 1 nonzero x,

    Σ_{x≠0} P(x) ≥ (2^d − 1) (Π_{x≠0} P(x))^(1/(2^d−1))
                 = (2^d − 1) (Π_j Π_{x≠0} ρ(ℓ_j x))^(1/(2^d−1))
                 ≥ (2^d − 1) μ_d^(t/(2^d−1)).

*Value of μ_d.* Let ℓ have rank k and image I. Then ℓ hits each point of I
exactly 2^(d−k) times on F2^d, so Π_{x≠0} ρ(ℓx) = (Π_{a∈I∖0} ρ(a))^(2^(d−k)).
verify.py evaluates this exactly for all 67 subspaces I of Q and every d ≤ 8.
In each case the minimum is I = E with k = 3. The general form follows from two
facts verify.py checks exactly: ρ₂ < ρ₁ < 1 and ρ₂⁷ < ρ₁⁸.

* If k ≤ 3, the product has 2^d − 2^(d−k) ≤ 2^d − 2^(d−3) factors, each at
  least ρ₂ and at most 1. So it is at least ρ₂^(2^d − 2^(d−3)), with equality
  exactly for I = E.
* If k = 4, so I = Q, the product is (ρ₁⁸ρ₂⁷)^(2^(d−4)), which exceeds
  ρ₂^(14·2^(d−4)) = ρ₂^(2^d − 2^(d−3)) because ρ₂⁷ < ρ₁⁸. ∎

The perhaps surprising fact ρ₂⁷ < ρ₁⁸, with a ratio 1 − 1.18·10⁻⁷, means a stage
map that collapses a line onto E beats an injective one. A naive analysis that
uses only injective maps gets the constant wrong in the seventh significant digit.

## 3. Depth 27

At t = 27 we have d ≤ 4, and d = 4 is best. Then μ_4 = ρ₂^14 and (2) reads

    |fiber(0)| ≥ F^27 · (1 + 15 ρ₂^(126/5)) ≥ (49343/3125) F^27 = 15.78976 F^27.

verify.py certifies the rational floor by checking ((L−1)/15)^15 ≤ μ_4^27
exactly. A control confirms that L + 15·10⁻⁶ fails. So every mode-preserving
frame sequence at depth 27 needs a tag of **at least 696 bits**, compared with
⌈27 log₂ F⌉ = 692 for a hypothetical direct sum, as at t ≤ 26. The identity
frame needs ⌈log₂ A_27⌉ = 796 bits.

**Near-attainment by an abstract pattern.** Take ℓ_1,…,ℓ_27 : F2^4 → Q of rank 3
onto E. Their kernels cover 12 nonzero points twice and 3 points once, so they
meet trivially and the map is injective. This pattern gives
Σ_x P(x) = 1 + 12ρ₂^25 + 3ρ₂^26 = 15.789775 (exact rational in verify.py). It
exceeds the floor by less than 10⁻⁴.

**Realization by actual frames.** FRAMES27.json gives integer blocks V_1 = 0,
V_2, …, V_27 with MᵀV_j = 0 and E V_j = 0, where E is the rows 0, 1, 2, 4 as in
#6660. With W_j = I + V_j E and U_j = I + (V_j − V_(j+1))E, these are
mode-preserving frames, by the same algebra as #6660 §6. verify.py does not
trust their derivation. From the committed integers it checks:

* MᵀV_j = 0 and E V_j = 0;
* the 27 binary images W_jM span exactly 104 dimensions;
* the dependency space D is 4-dimensional and lies in E^27;
* Σ_{a∈D} Π_j ρ(a_j) equals 1 + 12ρ₂^25 + 3ρ₂^26 exactly.

Hence, at depth 27,

    15.78976 F^27 ≤ min over frame sequences of |fiber(0)| ≤ 15.789775 F^27.

**How the frames are built** (`build_frames.py`, deterministic):
1. Realizable images are graphs N = {μ(a) + ψ(a)}, where μ is M mod 2 and ψ is
   any map into R′. Here R′ is the mod-2 reduction of {v ∈ ℤ^112 : Mᵀv = 0,
   v_E = 0}. It has dimension 100 and complements im M; the script finds a ℤ-basis
   by unimodular column reduction.
2. A relation Σ_j φ_j(a_j) = 0 therefore splits into Σ_j a_j = 0 and
   Σ_j ψ_j(a_j) = 0.
3. Choose rank-3 maps ℓ_j onto E with Σ_j ℓ_j = 0 and kernels covering 12 lines
   twice and 3 lines once.
4. Choose ψ_1 = 0 and ψ_2, …, ψ_22 at random. Solve Σ_j ψ_j ℓ_j = 0 for the last
   five maps, adding a random homogeneous part. Seed 20 gives full rank 104.

A direct-sum prefix of 26 stages cannot work, because it would force the 27th
coordinate map to be injective. These frames avoid such a prefix.

## 3½. The exact minimum zero fiber at depth 27

**Theorem.** Over all mode-preserving frame sequences at t = 27,

    min |fiber(0)| = (1 + 12ρ₂^25 + 3ρ₂^26) · F^27 = 15.7897746… · F^27,

and FRAMES27.json attains it.

*Proof.*

1. **Reduction to dimension 4.** By (c), dim D ≥ 4. Every term of (1) is
   positive, so any 4-dimensional subspace D′ ⊆ D gives a smaller or equal
   sum. It therefore suffices to minimize Σ_{x∈F2^4} Π_j ρ(ℓ_j x) over all
   27-tuples of linear maps ℓ_j : F2^4 → Q. Allowing non-injective joint maps
   only enlarges the set minimized over; the minimizer found below is
   injective and realized.
2. **Map types.** ρ(ℓx) depends only on whether ℓx is 0, in E∖0, or outside E.
   verify.py evaluates all 65,536 maps: the per-map product over the 15 nonzero
   x takes 8 values. The smallest is ρ₂^14, for a rank-3 map onto E. The next is
   ρ₁⁸ρ₂⁷, for an injective map. All others are at least 1.00056·ρ₂^14.
3. **Few injective maps.** With only maps onto E (kernel a line, value 1 there,
   ρ₂ elsewhere) and q ≤ 7 injective maps (value ρ₂ on a hyperplane, ρ₁ off it),
   verify.py enumerates every multiset of q hyperplanes exactly. For each it
   places the 27 − q kernel lines optimally; the cost is separable and convex,
   so greedy placement is optimal. The minimum is at q = 0, with kernels on 12
   lines twice and 3 lines once. The value is 1 + 12ρ₂^25 + 3ρ₂^26.
4. **Everything else.** By AM–GM, Σ_{x≠0} ≥ 15·(Π of per-map products)^(1/15).
   This lower bound already exceeds the q = 0 value whenever q ≥ 8, and whenever
   any map has neither of the two smallest types. These comparisons are exact
   rational checks.
5. **Realization.** The §3 frames realize this pattern exactly. ∎

So for zero outputs the depth-27 question is closed: the minimum is
⌈log₂((1 + 12ρ₂^25 + 3ρ₂^26)F^27)⌉ = 696 bits. Whether the maximum fiber of the
optimal frames exceeds their zero fiber is still open; if it does not, this is
the depth-27 optimum.

## 4. Larger depth

RESULT.json lists t = 27,…,40 with the best d ≤ 8. For 28 ≤ t ≤ 40, taking d = 8
already gives |fiber(0)| > 251·F^t. That is about 8 more tag bits than
⌈t log₂ F⌉; RESULT.json records the certified bit count for each t.
Larger d, up to 4t − 104, gives larger bounds, which the table does not
evaluate. Asymptotically, d = 4t − 104 gives roughly 16^(t−26) ρ₂^(7t/8) F^t.

## Scope

This is a lower bound for the zero fiber, and hence for the optimal maximum
fiber, of PR6660's exact interface: fixed known frames in G, one precision bit,
unbounded integers and full output access. At t = 27 the minimum zero fiber is determined exactly and attained by explicit
frames. The maximum fiber of those frames, and hence the exact optimum, remain
open. It supplies no codec, physical tag, caller or restoration
cost. κ, the selected frontier and its five assumptions are unchanged.
PR6660's theorems (Z) and (c) are cited premises at its pinned head, not
replayed; that PR is open at the time of writing. The written proof is
author-checked with exact finite corroboration, and no independent human or
proof-kernel review is claimed.
