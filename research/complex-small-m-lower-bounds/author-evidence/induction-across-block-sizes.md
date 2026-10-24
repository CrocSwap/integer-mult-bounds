> **Working note, kept as written.** An AI agent wrote this on the evening of 13 October 2026 (the induction track
> of the proofs round), and it is the written argument behind the bound of 2.9447 moves per array at every block from
> 4 on. Private paths were replaced by public ones (listed below) and nothing else was changed. No person has checked
> it. Two AI skeptics then read it: one went through every step by hand, the other recomputed every number with its
> own code. Neither found an error in the bounds of section 4. Their reports are in
> [induction-across-block-sizes-skeptics.md](induction-across-block-sizes-skeptics.md), and they asked for these
> corrections, which the note below does not contain:
>
> - **Proposition 7(c) is false as stated.** "General tensor products: at most 2 × the best" fails for families whose
>   dimension varies from frame to frame: at block 2 two cut families give 28/13 times the better factor. It holds
>   for families of constant dimension, which includes every certificate and every projection, pullback or sum of
>   one.
> - **"No growth" says more than was proved.** What is proved is that each single operation (projection, pullback,
>   direct sum, tensor product of certificate families) stays within a fixed factor of the ratio it starts from, so
>   a computation at block m0 fed through them certifies at most about 2·m0 at any block size. Small rises do
>   happen: the perfect block-2 family goes from 2 to 2.2 higher up, and the block-3 hook from 2.636 at block 4 to
>   2.653 at block 5. Combinations such as tensor products of several pullbacks are not covered.
> - **The corollary of Theorem 4 needs one more sentence.** It checks that the profile built from the lower bounds
>   for f_2, f_3, f_4 is nondecreasing, not the true profile. That is enough, because every T_m and every R_r grows
>   with each f_s, while ā_1 depends only on f_1, which is exact.
> - **κ_m = 2 − 2^(1−m)** is checked exactly up to block 40 (the second skeptic) and argued beyond.
>
> **Since then.** Fact B calls f_2 ≥ 48,576 and f_3 ≥ 68,320 "certified mod-p lower bounds", but no certificate
> for them was stored until 23 October 2026. Now one is, checked on all 16 characters, in
> `../programs/hook-certificates-blocks-2-to-6/`, next to the 5,412 × 5,412 minor behind f_4 ≥ 86,592. Maximilian
> Lutz checked section 4 independently with his own code, and proved the two domination inequalities for every k
> ([#4643](https://github.com/CrocSwap/integer-mult-bounds/pull/4643)).
>
> **Names of my working notes used below, and where to read them here.**
>
> | In the note | Here |
> |---|---|
> | Theorem R (`w-bounds` section 2) | section 1.1 of [the README](../README.md); proved in Lean in `../programs/lean-block2-block3/` |
> | the Averaging Lemma and the triangle inequality (`w-bounds` section 3) | Lemma 2 of [two-arrays.md](../../../notes/network-coding/two-arrays.md), written there at block 3; its proof uses only that the letter group carries every ordered pair of frames to every other pair at the same distance, which Fact A gives at every m. The triangle inequality δ(U,W) ≤ δ(U,V) + δ(V,W) holds because intersecting Y_U ∩ Y_V with Y_W removes at most δ(V,W) dimensions. |
> | `engine_m.py` and its outputs (v-b56-methods) | `../programs/engine-bounds-blocks-5-and-6/fact-a/` and `../data/engine-bounds-blocks-5-and-6/fact-a/` |
> | the exact table of N_r(s) (b56-methods, v-b56-methods) | `../data/engine-bounds-blocks-5-and-6/exact-projection-table/` |
> | the earlier engine-game bounds (b56-note, b56-methods: 2.665, 2.641, 35/17, …) | `../data/certificate-ceilings/out_numbers.txt` |
> | b56-compute, v-b56-compute (the block-4 hook values) | `../data/block4-hook/`; the skeptic's own check is `fcheck.py` below |
> | w-bounds section 5.4 (certificates A to E) | certificate A (the label permutation module) is the function `A` of `../../existence-routes/programs/boosters/certlib.py`; the others are not published |
> | the programs and outputs named in the note | `../programs/engine-bounds-blocks-5-and-6/` and `../data/engine-bounds-blocks-5-and-6/` |

# Induction across block sizes (pf-induction)

Proofs round, 13 October 2026, evening. One agent; no skeptic has read this yet. Nothing posted. Labels: [proved] (full proof here), [computed] (exact arithmetic, script named), [argued], [guess]. Everything is "given Theorem R" (`w-bounds` section 2) and holds in the **engine game** unless it says otherwise.

## What came out

1. **A finite computation at block 4 now bounds every block size** [proved + computed]. Carrying the block-4 hook (k = 8) up by the projection recursion gives, in the engine game, at least **2.9447 moves per array at every block size m ≥ 4**, with exact values 834241/278850 = 2.99172 at block 5 and 1188222/399685 = 2.97290 at block 6. The previous engine-game bounds were 2.665 (block 5) and 2.641 (block 6). The saving left open drops from 0.391 to 0.319 at block 5, and from 0.458 to 0.392 at block 6. At every m it is at most ln(m/2.9447)/ln m. (Theorem 4.)
2. **The bound does not grow. No induction of the projection kind can make it grow** [proved]. Projection from a block-m0 family never exceeds (its best profile ratio) × (2^(m0+1)+1)/(2^(m0+1)−2), at any m. From block 4 that is at most 4.4 even for a perfect block-4 family, and 3.47 for the hook. Pullbacks along arbitrary maps (equivariant or not) gain at most a factor κ_m = 2 − 2^(1−m) < 2. Direct sums never beat their best part. Tensor products of certificate families never beat their best factor. (Theorems 5 and 6, Proposition 7.)
3. **The question has a clean dichotomy** [proved]. The best engine-game Theorem-R bound L*_m is subadditive: L*_(a+b) ≤ L*_a + L*_b. So L*_m/m converges to λ* = inf L*_m/m. Either λ* > 0, in which case ε_m is bounded and the method's bounds grow linearly (savings → 0), or λ* = 0 and ε_m → ∞. No finite computation at small m, fed through any of the inductions above, can decide which: they all stay within a factor of about 2 of the base block. (Lemma 1, section 9.)
4. **Coordinate families are capped below 2 at every block size** [proved for m ≤ 12; argued for all m]. A family spanned by basis vectors chosen per frame (any permutation module) certifies at most κ_m = 2 − 2^(1−m) moves per array. This is attained by the point cut, and explains certificates A to E of w-bounds 5.4 (1.75 = κ_3). (Theorem 6.)
5. **One array always needs m moves** [proved, 6 lines]. A one-array unit cannot use fewer than m moves at block m, at engine prices too. So "1 in 3" at blocks 5 and 6 is excluded. (Proposition 8.)
6. **Units embed, and so do the bounds** [proved]. True costs satisfy μ_(m+1)(W) ≤ μ_m(W) + W and μ_(a+b) ≤ μ_a + μ_b, which mirrors the subadditivity of L*. (Lemma 1(d).)

**What this does not settle.** Whether any Theorem-R certificate in the engine game can certify more than 4 per array at large m is still open. The answer is "no" for every construction built by induction from small blocks: projections and other pullbacks, sums, tensors, and coordinate families. A "yes" needs a global object, a family of subspaces on the whole dual polar graph with average edge excess ε_m = o(m). Section 9 says what such an object must look like.

---

## 0. Setting

- **Frames.** At block m, frames are the Lagrangians of F_2^(2m), with the form x·z′ + x′·z. Distance is d(U,V) = m − dim(U∩V). This is the dual polar graph DSp(2m,2): diameter m, valency 2(2^m − 1). L_0 is the diagonal-Pauli frame {(0|z)}.
- **Families.** A family Y gives each frame U a subspace Y_U of one vector space over a field of characteristic 0. Put δ(U,V) = dim Y_U − dim(Y_U ∩ Y_V). ā_r is the mean of δ over ordered pairs at distance r. The profile ratios are R_r = ā_r/ā_1, and the top ratio is T(Y) = R_m. A family is **distance-determined** when δ(U,V) depends only on d(U,V).
- **L\*_m** is the supremum of T(Y) over all families at block m: the best moves-per-array bound that Theorem R can give in the engine game. ε_m = m/L_m − 1 (b56-note).

**Fact A (letters at every m)** [proved; matrices at m = 3, 4, 5 in `../data/engine-bounds-blocks-5-and-6/fact-a/out_engine_m*.txt`]. The letters are those typed from the Lean source in `../programs/engine-bounds-blocks-5-and-6/fact-a/engine_m.py`: shift X^z, dir z = ((1+i)/2)·I + ((1−i)/2)·X^z, address maps for G in GL(m,2), and phaseMat z c = diag(i^((z·x) xor c)). Their frame actions are as follows:
- The address maps act as diag(A, A^−T), which gives all of GL(m,2).
- phaseMat z c acts as the transvection along (0|z). With D = diag(i^[z·x]), D X^a D^−1 = X^a if z·a = 0, and = i·X^a Z^z (up to the fixed sign convention) if z·a = 1. That is (a|b) ↦ (a|b + (z·a)z). Sums of zz^T give every symmetric matrix over F_2, for example [[0,1],[1,0]] = (e1+e2)(e1+e2)^T + e1e1^T + e2e2^T. So the free letters give the whole stabiliser P of L_0, and they fix L_0.
- dir z is the transvection along (z|0). A block dir z_1⋯dir z_j acts as [[I,T],[0,I]] with T = Σ z_i z_i^T, so it moves L_0 to distance rank T ≤ j. The kernel has T = I, which is distance m (opposite).

P acts transitively on each sphere around L_0. By Witt's theorem every pair of Lagrangians at distance d has a symplectic basis e, f with U = ⟨e⟩ and V = ⟨e_1..e_(m−d), f_(m−d+1)..f_m⟩. Since rank-d blocks reach distance d, the letter group Γ is transitive on frames. Its image contains P, so |image| ≥ |frames|·|P| = |Sp(2m,2)|, so the image is Sp(2m,2), which is distance-transitive. These are exactly the hypotheses of the Averaging Lemma (w-bounds section 3) at every m. Hence for every family, moves ≥ W·ā_m/ā_1, using ā_j ≤ j·ā_1 for a block of rank j.

**Fact B (certificates are distance-determined families)** [proved]. Let (V, N) be a certificate with N kept by the free group B. The kernel of Γ → Sp(2m,2) consists of the Paulis and the scalars ±1, ±i. The Paulis are in B: the X^z are shifts, and the Z^z are squares of phaseMat. If cI ∈ Γ, then c ∈ Q(i) and c^n = det(cI) is a product of letter determinants, each a power of i, since the letters have eigenvalues in {±1, ±i}. So c is a root of unity in Q(i), that is ±1 or ±i, and i = phaseMat 0 1 ∈ B. So B is the whole preimage of P = Stab(L_0). Hence Y_U := gN, for any g with gL_0 = U, is well defined. Its δ(U,V) = f(g_U^−1 g_V) is constant on each B-double coset, that is, on each distance. So δ = f_d with f_d = f(any block of rank d). The block-4 hook has f_1 = 27456 (exact, proved closed form), f_2 ≥ 48576, f_3 ≥ 68320 and f_4 ≥ 86592 (certified mod-p lower bounds: `../data/block4-hook/out_rank2_blocks.txt`, `out_m4_hook8_G.txt`; upheld by v-b56-compute).

## 1. Lemma 1: profiles, residues, subadditivity, units

(a) [proved] For every family and every r, s with r+s ≤ m: ā_(r+s) ≤ ā_r + ā_s.
*Proof.* Take U, W at distance r+s and a frame V on a geodesic, at distance r from U and s from W. Then δ(U,W) ≤ δ(U,V) + δ(V,W) (w-bounds section 3). Average over a uniformly random pair (U,W) and a uniformly random such V. By distance-transitivity, (U,V) is a uniform pair at distance r and (V,W) a uniform pair at distance s. ∎

(b) [proved] **Residue restriction.** For every family at block m and every r ≤ m: R_r ≤ L\*_r.
*Proof.* The frames containing a fixed isotropic I of dimension m−r form a copy of DSp(2r,2), via U ↦ U/I in I^⊥/I, and distances are preserved. Restricted to it, Y is a block-r family. Average over I. Pairs (U,V) in a residue at distance s ≤ r are uniform among all pairs at distance s, by transitivity. So the averaged residue family has the profile ā_1..ā_r of Y, and its top ratio R_r is at most L\*_r. A direct sum over all I has the averaged profile. ∎

(c) [proved] **Subadditivity.** L\*_(a+b) ≤ L\*_a + L\*_b. Hence (Fekete) L\*_m/m → λ\* = inf_m L\*_m/m. ε_m is bounded if and only if λ\* > 0.
*Proof.* By (a), ā_(a+b) ≤ ā_a + ā_b. By (b), this is at most (L\*_a + L\*_b)·ā_1. Fekete's lemma applies to the subadditive sequence L\*_m. ε_m = m/L\*_m − 1 is bounded if and only if L\*_m ≥ cm for some c > 0. ∎

(d) [proved, given Fact A's letter list] **Units embed.** Let μ_m(W) be the fewest paid moves of a correct block-m word for W live arrays. Then μ_(m+1)(W) ≤ μ_m(W) + W and μ_(a+b)(W) ≤ μ_a(W) + μ_b(W).
*Proof.* The map g ↦ g ⊗ I_2 on the last address bit sends block-m letters to block-(m+1) letters of the same kind and rank: dir z ↦ dir (z,0), shift and phase likewise, and the address map G ↦ G ⊕ id. It is a group homomorphism, so it maps formal identities to formal identities. The block-(m+1) kernel is (K_m ⊗ I)·dir e_(m+1). So run the lifted word, then one direction per live array. Likewise K_(a+b) = (K_a ⊗ I)(I ⊗ K_b): run the two lifted words one after the other. ∎
(c) is the certificate-side mirror of (d). Neither gives growth.

## 2. Lemma 2: the projection counts, closed form [proved; computed check]

For a point p, π_p(U) = (U∩p^⊥ + p)/p ∈ Lag(p^⊥/p). For L, M at distance r, put H = L∩M, of dimension m−r, so that L+M = H^⊥. The number N_r(s) of nonzero p with d(π_pL, π_pM) = s is:

| s | N_r(s) | which p |
|---|---|---|
| r | (2^(m−r) − 1) + (4^m − 2^(m+r)) | p ∈ H, or p ∉ L+M |
| r−1 | 2(2^m − 2^(m−r)) + (2^r − 1)·2^(r−1)·2^(m−r) | p ∈ (L∪M) \ H; or p = l+m′ with ⟨l,m′⟩ = 1 |
| r−2 | (2^r − 1)(2^(r−1) − 1)·2^(m−r) | p = l+m′ (l ∈ L\H, m′ ∈ M\H) with ⟨l,m′⟩ = 0 |

*Proof.* Upstairs, π_pL ∩ π_pM = {a + εp = b + ε′p : a ∈ L∩p^⊥, b ∈ M∩p^⊥}, so a = b or a + b = p.
- (i) If p ∈ H, the intersection is H, so s = r.
- (ii) If p ∉ L+M, then a + b = p is impossible. The intersection is (H∩p^⊥) + ⟨p⟩, of dimension m−r, so s = r.
- (iii) If p ∈ L\H, then π_pL = L/p, and the intersection is H + ⟨p⟩, so s = r−1. The case p ∈ M\H is symmetric.
- (iv) Otherwise p = l + m′. Here ⟨h,p⟩ = 0 for h ∈ H, and for a = l + h we get ⟨a,p⟩ = ⟨l,m′⟩, which does not depend on the decomposition. If it is 0, the intersection is H + ⟨l, p⟩ and s = r−2. If it is 1, the intersection is H + ⟨p⟩ and s = r−1.

The pairing L/H × M/H → F_2 is perfect. So, counting the nonzero pairs (l̄, m̄′), (2^r−1)(2^(r−1)−1) have pairing 0 and (2^r−1)·2^(r−1) have pairing 1, and each pair gives 2^(m−r) points p. ∎

[computed, `nrs.py` → `out_nrs.txt`] The formula agrees with all 20 exact (m,r) rows of b56-methods/v-b56-methods (m = 2..6) and with 23 fresh brute-force counts on random symplectic frames (m = 2..5). There were 0 mismatches.

## 3. Theorem 3: the projection recursion as a Markov chain [proved]

Let f_0 = 0, f_1, …, f_(m0) be the profile of a distance-determined block-m0 family. For k > m0 put Y^(k)_U = ⊕_p Y^(k−1)(ι_p π_p U), summed over the nonzero points p, where each ι_p is a fixed symplectic identification p^⊥/p ≅ F_2^(2k−2).

**Claim 1.** ā^(k)_r = Σ_s N^(k)_r(s)·ā^(k−1)_s (b56-methods). *Proof.* Fix p. Stab(p) maps onto Sp(p^⊥/p), π_p is equivariant, and the uniform law on pairs at distance r is invariant. So, given s, the pair (π_pU, π_pV) is uniform among pairs at distance s, and E[δ | s] = ā^(k−1)_s. Summing P(d_p = s) over p gives E[#{p : d_p = s}] = N_r(s), by Lemma 2. ∎

**Claim 2.** Write P_k = 4^k − 1. Let D_m, D_(m−1), …, D_(m0) be the Markov chain on distances with step law N^(k)_r(s)/P_k from block k to block k−1, in which 0 is absorbing. Then ā^(m)_r = (Π_(k=m0+1..m) P_k)·E[f_(D_(m0)) | D_m = r]. In particular ā^(m)_1 = (Π P_k)·f_1·S_m with S_m = Π_(k=m0+1..m) A_1(k)/P_k, where A_1(k) = 4^k − 3·2^(k−1) − 1. *Proof.* Induction on m, using Claim 1. From distance 1 the chain stays at 1 with probability A_1(k)/P_k or falls to 0. ∎

So T_m = E[f_(D_(m0)) | D_m = m] / (f_1·S_m).

## 4. Theorem 4: a bound for every block size from block 4 [proved + computed]

Let J_k = k − D_k be the **deficit**. An opposite pair starts at J_m = 0. One step at block k from deficit j (distance r = k−j ≥ 1) goes as follows: down to j−1 with probability A_r/P_k; stay at j with probability B_r/P_k; up to j+1 with probability C_r/P_k. Here A, B, C are the three rows of Lemma 2. From distance 0 the chain always goes down.

**Domination** [proved]. For all k ≥ 1 and 0 ≤ j < k:
- C_r ≤ 2^(−j−1)·P_k. Indeed C_r = 2^(2k−j−1) − 3·2^(k−1) + 2^j and 2^(−j−1)P_k = 2^(2k−j−1) − 2^(−j−1), so the claim reduces to 2^j + 2^(−j−1) ≤ 3·2^(k−1), which holds for j ≤ k−1.
- For j ≥ 1, A_r ≥ (1 − 2^(−j))·P_k, because the difference is 2^j − 2^(−j) ≥ 0. [exact check for k ≤ 80 in `tail.py`: 0 violations]

Let J\* be the homogeneous birth-death chain with up-probability 2^(−j−1) and down-probability 1 − 2^(−j) (j ≥ 1), and at j = 0 up 1/2, stay 1/2. It is stochastically monotone, since p_up(j) + p_down(j+1) = 1. The real chain is dominated by it step by step: P(next ≥ j+1) ≤ p\*_up and P(next ≥ j) ≤ 1 − p\*_down. Hence, starting both at 0, J_t ≤_st J\*_t. A monotone chain started at its bottom state increases stochastically to its stationary law. So J_t ≤_st π\*, where by detailed balance π\*(j+1)/π\*(j) = 1/(2^(j+1) − 1). That is, π\* ∝ 1, 1, 1/3, 1/21, 1/315, …, with normaliser 2.3842310290.

**Theorem 4.** Fix M > m0. Suppose the block-M profile r ↦ R^(M)_r (with R_0 = 0) is nondecreasing. Then for every m ≥ M:

T_m ≥ c\*_M := Σ_j π\*(j)·R^(M)_(M−j)   (terms with M−j ≤ 0 count as 0).

*Proof.* Condition on J_M. Then E[f_(D_(m0)) | J_m = 0] = Σ_j P(J_M = j)·h(j), with h(j) = ā^(M)_(M−j)/Π_(k≤M)P_k = R^(M)_(M−j)·f_1·S_M by Claim 2 at block M. So T_m = (S_M/S_m)·Σ_j P(J_M = j)·R^(M)_(M−j). Here S_M/S_m ≥ 1 because every factor is ≤ 1. Since j ↦ R^(M)_(M−j) is nonincreasing and J_M ≤_st π\* (the chain from block m down to M is dominated), the sum is at least Σ_j π\*(j)·R^(M)_(M−j). ∎

**Corollary (block-4 hook)** [computed, `tail.py` → `out_tail.txt`, exact integers and fractions; normaliser of π\* bounded from above]. The base profile is (27456, 48576, 68320, 86592). All of its entries are certified lower bounds, and f_1 is exact, so every T_m below is a certified lower bound.
- T_5 = 834241/278850 = 2.991720, T_6 = 1188222/399685 = 2.972896, T_7 = 2361819/799370 = 2.954600.
- T_m decreases to 2.944709234 by m = 60.
- The block-60 profile is nondecreasing, and c\*_60 = 2.944709234120998, equal to the exact top at m = 60.

Hence, in the engine game, **every unit at block m ≥ 5 uses at least 2.9447·W moves**, and block 4 keeps 41/13. The block-5 and block-6 values are exact rationals. Cross-checks: the same code reproduces b56-methods' 29/11, 9486/3575 and 405993/153725 from the block-3 hook, and 35/17, … from the perfect block-2 family (`out_induct.txt`).

| Block | Old engine-game bound (b56-note) | New | Saving left open, old → new | Units now excluded (moves, engine game) |
|---|---|---|---|---|
| 5 | 2.665 | 2.99172 (exact fraction) | 0.391 → 0.319 | 3 in 8, 4 in 11, and every W in 3W−1 with W ≤ 120 |
| 6 | 2.641 | 2.97290 (exact fraction) | 0.458 → 0.392 | 3 in 8, 4 in 11, 5 in 14, and every W in 3W−1 with W ≤ 36 |
| m ≥ 7 | none | 2.9447 | 1 − ln 2.9447/ln m | — |

Engine prices [computed, indicative: they need f_j from above for j ≥ 2, which mod-p ranks do not give; `out_prices.txt`]. The engine-priced caps are 0.713 (block 5; hooks gave 0.83) and 0.796 (block 6; hooks 0.91). From block 7 on they exceed 0.9, because f_(m−1)/f_m → 1: rank-(m−1) blocks are priced almost as a whole array. The bounds hold in the engine game only, as do all projection bounds (Toffoli letters do not act on frames).

## 5. Theorem 5: projection cannot grow [proved]

For every base profile and every m > m0:

T_m ≤ (max_s f_s / f_1) / S_∞(m0),   with S_∞(m0) = Π_(k>m0) A_1(k)/P_k = 2(2^(m0) − 1)/(2^(m0+1) + 1).

*Proof.* E[f_(D_(m0))] ≤ max_s f_s and S_m ≥ S_∞. For the product, write x = 2^k. Then A_1/P_k = (x−2)(2x+1)/(2(x−1)(x+1)), and both factors telescope: Π (2^k − 2)/(2^k − 1) → (2^(m0) − 1)/2^(m0) and Π (2^(k+1) + 1)/(2(2^k + 1)) → 2^(m0+1)/(2^(m0+1) + 1). ∎ [computed: S_∞ = 2/3, 14/17, 10/11 for m0 = 2, 3, 4, agreeing with the 400-term product]

Every family has max_s f_s/f_1 ≤ m0 by Lemma 1(a). So **projection from block m0 never certifies more than m0·(2^(m0+1)+1)/(2^(m0+1)−2)**, at any block size: 3, 3.643, 4.4, 5.24 for m0 = 2, 3, 4, 5. Even a perfect block-4 family (which does not exist in characteristic 0) would give at most 4.4. The block-4 hook gives at most 3.469, and in fact converges to 2.9447.

**Why** [proved by Lemma 2]. An edge survives a point projection with probability 1 − 3·2^(k−1)/P_k ≈ 1 − 3·2^(−k−1), but an opposite pair loses a step of distance with probability (2^(k−1)−1)/(2^k+1) ≈ 1/2, every time. The deficit settles at π\*, near 0.42/0.42/0.14 on deficits 0/1/2. So the projected top ratio is a fixed weighted sum of the base's top ratios. For the block-4 hook the limit is 0.491·R_4 + 0.460·R_3 + 0.134·R_2 + 0.014·R_1 = 2.944709 [computed, `checks.py` → `out_checks.txt`: the exact law of the block-4 distance of an opposite pair projected down from block 60 is 0.446/0.418/0.122/0.013 on 4/3/2/1, divided by S_60]. That is why R_3 = 2.49 of the hook matters almost as much as R_4 = 3.15. A block-4 certificate with a better R_3 would raise the bound for every m.

## 6. Theorem 6: cuts, coordinate families and pullbacks along any map

**κ_m** := the largest P_m(cut)/P_1(cut) over the nontrivial cuts S of DSp(2m,2), where P_d(cut) is the probability that a uniform pair at distance d is separated. For a 0/1 function, P_d = ½·E_d|1_S(U) − 1_S(V)|² = Σ_θ (1 − u_d(θ))·‖f_θ‖² (spectral decomposition of the distance-regular graph). So κ_m ≤ max_(θ≠k) (1 − u_m(θ))/(1 − u_1(θ)).

[proved for m = 2..12 by exact computation, `cutceil.py` → `out_cutceil.txt`] I used the intersection array b_i = 2^(i+1)(2^(m−i) − 1) and c_i = 2^i − 1, which agrees with the sphere sizes of engine_m.py at m = 3, 4, 5. All m+1 eigenvalues were found as exact integer roots. The maximum is **κ_m = 2 − 2^(1−m)** (3/2, 7/4, 15/8, …), at the eigenvalue 2^m − 3. It is attained by the point cut {U : v ∈ U}: brute force at m = 2, 3 gives exactly 3/2 and 7/4, and the general count is in section 9. [argued for m > 12: the same eigenvalue maximises; a closed-form check of the q-Krawtchouk cosines is the missing step]

**Consequences** [proved, for every m with κ_m as above].
- (i) A **coordinate family**, with Y_U = span{e_x : x ∈ S(U)} for one fixed basis, has δ(U,V) = |S(U) \ S(V)| = Σ_x [x ∈ S(U), x ∉ S(V)]. This is a sum of directed cuts, so its ratio is ≤ κ_m < 2. This covers every permutation-module certificate. w-bounds 5.4's certificate A has ratio exactly 7/4 = κ_3; B (2W) is a quotient, not a coordinate family.
- (ii) **Pullbacks along arbitrary maps.** Let φ: Lag(2m,2) → Lag(2m′,2) be any map, and F′ a distance-determined family with 0 < f′_1 ≤ f′_s ≤ f′_max (s ≥ 1). Then Y_U = F′(φU) has ratio ≤ (f′_max/f′_1)·κ_m. *Proof.* The numerator is ≤ f′_max·q_m and the denominator ≥ f′_1·q_1, where q_d = P_d(φU ≠ φV) = Σ_fibres C P_d(U ∈ C, V ∉ C) is a sum of directed cuts, so q_m/q_1 ≤ κ_m. ∎
- So any pullback induction from a block-m′ certificate family gives at most 2·(its ratio) ≤ 2m′ at any block size. The equivariant point projection gives the sharper factor of Theorem 5.

## 7. Proposition 7: sums and tensor products [proved]

- (a) **Direct sums:** ā_r adds, so T(F ⊕ G) is a mediant, at most max(T(F), T(G)).
- (b) **Tensor products of distance-determined families** (every certificate family, by Fact B): T(F_1 ⊗ ⋯ ⊗ F_k) ≤ max_i T(F_i).
  - *Proof.* With D_i = dim and x_i = δ_i/D_i, we have δ_⊗/ΠD_i = 1 − Π(1 − x_i). On edges x_i = e_i, a constant, and on opposite pairs x_i = t_i ≤ min(1, R·e_i), with R = max T(F_i). Put g(ρ) = 1 − Π(1 − min(1, ρe_i)). Each factor is nonnegative, nonincreasing and convex in ρ, and a product of such functions is convex ((uv)″ = u″v + 2u′v′ + uv″ ≥ 0). So g is concave, and g(0) = 0. Hence g(R) ≤ R·g(1) for R ≥ 1. The numerator 1 − Π(1 − t_i) is at most g(R), and the denominator is g(1). So the top ratio is ≤ R. ∎
- (c) **General tensor products:** T(F ⊗ G) ≤ 2·max(T(F), T(G)), because x + y − xy ≥ (x+y)/2.

## 8. Proposition 8: one array needs m moves, at any price [proved]

Expand a correct word multilinearly. Every term of the final content of live register 1 comes from a history, which is a sequence of letters applied to y_1, and its group element is the product of those letters. The coefficient of [K]y_1 is 1, so some history has product K. Along it, d(ℓgL_0, L_0) ≤ d(gL_0, L_0) + d(ℓL_0, L_0) (because d(ℓgL_0, ℓL_0) = d(gL_0, L_0)). That step adds 0 for a free letter (Fact A) and at most j for a block of rank j. K is at distance m, so the paid blocks on that history, which are distinct steps of the word, have total rank ≥ m. Their engine price is Σ(j_i/m)^z ≥ Σ j_i/m ≥ 1 for z ≤ 1. ∎ So "1 in 3" (blocks 5 and 6, b56-note) is excluded, and a saving needs W ≥ 2 with shared paid steps.

## 9. The question asked, and checks against the exact table

- **Growth theorem from induction: impossible** [proved, sections 5 to 7]. The inductions named in the brief have these limits:
  - Projection (point and isotropic) gains at most a factor (2^(m0+1)+1)/(2^(m0+1)−2), and for the hook it converges to a weighted mean of its top ratios.
  - Pullbacks along any maps gain at most a factor < 2.
  - Sums and tensor products of certificate families gain nothing.
  - Lifting units only gives μ_(m+1) ≤ μ_m + 1.

  So no theorem of the form "block-m bound ⇒ larger block-(m+1) bound" exists inside this toolbox. A finite computation at block m0 caps what these inductions can certify at about 2·m0 at most. They do give a uniform bound for every m, which is Theorem 4.
- **No-go for the whole method (≤ 4 for every certificate): not proved.** It holds for every certificate that is coordinate (< 2), projected or pulled back from small blocks (< 2·base), a sum or a tensor of those, a hook (< 4, b56) or a Venn set (< 4, b56). The general case is exactly the λ\* dichotomy of Lemma 1(c). λ\* > 0 needs a family whose average edge excess ε_m stays bounded.
  - In such a family, the triangle inequality must be nearly tight along most geodesics. Equivalently, Y_U ∩ Y_W ⊂ Y_V must hold for most frames V between U and W.
  - Then on the copy of the subspace lattice of L inside the graph (A ↦ A + (A^⊥ ∩ M) for M opposite L; distance = dim(A+B) − dim(A∩B), an isometric embedding), A ↦ Y_L ∩ Y_(F_A) must be close to a lattice representation of PG(m−1,2) in characteristic 0. That is the Fano obstruction (Theorem F), now needed in every rank-3 residue at once.
  - [guess] I expect λ\* = 0 (ε_m → ∞), because the clean part of every known family (the pair frames of the perfect lift) has density → 0. Turning this into a proof needs a quantitative, characteristic-dependent rank inequality on PG(m−1,2) configurations whose violation count grows with m. I did not find one.
- **Checks at m = 2..6** [computed]:
  - The N_r(s) closed form equals the exact table (section 2).
  - The recursion reproduces b56-methods' bounds exactly (35/17, 400/187, 26319/12155, 228354/104533; 29/11, 9486/3575, 405993/153725).
  - κ_2 = 3/2 < 2 = L_2, so block 2 needs a non-coordinate family (the perfect lift). κ_3 = 7/4 equals certificate A of w-bounds 5.4.
  - New m = 5, 6 values: 2.99172 ≥ widened 31/14 and 2.97290 ≥ 63/31, consistent since engine bounds must dominate widened ones.
  - Lemma 1 on the new families [computed, `out_checks.txt`]: block-5 profile 1, 1.737, 2.359, 2.806, 2.992 and block-6 profile 1, 1.723, 2.306, 2.694, 2.865, 2.973. Both are nondecreasing and satisfy R_(r+s) ≤ R_r + R_s and R_r ≤ r. So does the base block-4 profile (lower bounds) 1, 1.769, 2.488, 3.154.
  - ε_5 = 5/2.99172 − 1 = 0.671 and ε_6 = 1.018. Ruling out a saving of 0.1 needs 0.175 and 0.196 (b56-note).
- **Point cut count (for Theorem 6):** P_m(cut) = 2/(2^m+1) and P_1(cut) = 2·(1/(2^m+1))·2^(m−1)/(2^m−1), so the ratio is (2^m−1)/2^(m−1) = 2 − 2^(1−m). The count: of the 2(2^m−1) neighbours of U ∋ v, 2^m are reached through hyperplanes H ∌ v, and those neighbours do not contain v.

## Files (`../programs/engine-bounds-blocks-5-and-6/`, outputs in `../data/engine-bounds-blocks-5-and-6/`)

- `nrs.py`, `nrs_closed.py` → `out_nrs.txt`: Lemma 2 and its checks.
- `induct.py` → `out_induct.txt`: the recursion from three bases, with and without the triangle improvement (identical values).
- `tail.py` → `out_tail.txt`: domination inequalities, π\*, c\*, the all-m bound, S_∞ and the no-growth ceilings.
- `cutceil.py` → `out_cutceil.txt`: κ_m for m = 2..12, with a brute-force check at m = 2, 3.
- `prices.py` → `out_prices.txt`: indicative engine-price caps.
- `checks.py` → `out_checks.txt`: Lemma 1 on the projected profiles, and the limiting deficit law.
- `RUNLOG.txt`, `STATUS.txt` (in my private archive).

All runs went through a memory guard, each under 15 s and 100 MB.
