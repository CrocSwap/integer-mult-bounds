# Five binary full-guard events lie below the product of their marginals

Ryanson Jonathan, with Claude Code (Claude Opus 5.5) assistance. Apache-2.0. This is successor work to petalas's
#4275, which supplies the character law, and #4599, which settles k = 4. It follows the same method.

## Statement

**Setting.**

- U_1, …, U_5 are pairwise orthogonal rank-one idempotents on F_2^m, with m ≥ 5.
- P_t = I − U_t, and G is uniform on GL_m(F_2).
- E_t is the event that every leading principal minor of G P_t G⁻¹, of orders 1 to m−1, is nonzero.
- n = m − 1, X = 2^m, s_m = 3ⁿ/((X−1)2ⁿ), and ρ_m = Pr(E_1 ∩ … ∩ E_5)/s_m⁵.

**Theorem.** For every m ≥ 5,

```text
Pr(E_1 ∩ … ∩ E_5) < s_m^5,     1 − ρ_m = 20 (7/9)^n + O((19/21)^n (7/9)^n).
```

This answers k = 5 of Open next question 2 in #4275. The claim is a scoped counting proof with an exact finite
component. No negative association is asserted for other functions, other event families or k ≥ 6.

## 1. Reduction to a walk

A basis change takes U_t to e_t e_tᵀ. This only permutes headers, so it does not change any probability.

**The guard as a sum.** Let g_t be column t of G and h_t row t of G⁻¹. Then G P_t G⁻¹ = I − g_t h_tᵀ, and by the
matrix determinant lemma its order-j leading minor is

```text
1 − Σ_{i≤j} h_t[i] g_t[i].
```

**Headers as pairs.** Let x_i be the first five coordinates of row i of G, and y_i the first five coordinates of
column i of G⁻¹. Write A_j = Σ_{i≤j} y_i x_iᵀ for the prefix sums. Then every guard passes exactly when A_1, …, A_n
all have zero diagonal. Two facts follow:

- each increment y_i x_iᵀ with i ≤ n has disjoint factor supports;
- A_m = YX = I_5, so the last increment is I_5 − A_n. This has unit diagonal and rank at most one, so it is J and
  its pair is forced to be all ones. Hence A_n = E := J − I_5.

**Counting headers.** Each pair (X, Y) with YX = I_5 extends to exactly |GL_{m−5}| headers, because the remaining
columns of G form an ordered basis of ker Y. Let D_n(E) be the number of ordered sequences of n factor pairs with
disjoint supports whose rank-one increments sum to E. Then

```text
Pr(E_1 ∩ … ∩ E_5) = D_n(E) |GL_{m−5}| / |GL_m| = D_n(E) / (2^{5n−20} (X−1)(X−2)(X−4)(X−8)(X−16)).
```

**The ratio.** Put N_n = 2^20 D_n(E). Then

```text
ρ_m = (N_n / 243^n) · H(X),     H(X) = (X−1)^4 / ((X−2)(X−4)(X−8)(X−16)) > 1.        (1)
```

## 2. The signed spectrum

The increments live in the group of zero-diagonal 5×5 binary matrices, F_2^20. Let w be the weight of each element,
meaning the number of disjoint-support pairs that produce it. Its total is 3⁵ = 243, of which the zero matrix has
weight 63; there are 181 distinct increments. Let ŵ be the Walsh–Hadamard transform. Then

```text
N_n = Σ_c (−1)^{|c|} ŵ(c)^n,
```

because the character c evaluated at E is (−1)^{|c|}. The verifier computes ŵ exactly on all 2^20 characters and
collects N_n = Σ_z b_z zⁿ. The result has 62 bases, all of them positive. The leading terms are

```text
N_n = 243^n − 20·189^n + 60·171^n − 40·165^n + … ,    Σ_{z<189} |b_z| = 1,048,555,   max_{z<189} z = 171.     (2)
```

This agrees with #4275's description of the second eigenvalue: 7·3^{k−2} = 189, with sign −1 and multiplicity
k(k−1) = 20.

**Cross-checks of the table.** These do not use characters.

- **Direct counts.** Meet-in-the-middle convolution gives D_n(E) for n = 4, 5 and 6, and 2^20 D_n(E) equals
  Σ_z b_z zⁿ in each case. In particular D_4(E) = 0.
- **m = 6.** The formula gives exactly 2,880 complete headers. This matches #4598 and my independent recount in #4605.
- **Marginal law.** At k = 1 the same reduction reproduces the marginal s_m.
- **Brute force.** The reduction matches a brute force from the leading-minor definition over GL_3 and GL_4, for
  k = 1, 3 and 4.
- **Failure control.** Changing one multiplicity by one unit is detected.

## 3. Large dimensions (n ≥ 117)

Put x = (7/9)ⁿ. The bases below 189 satisfy |R_n| ≤ 1,048,555·171ⁿ. Since 1,048,555·171^117 ≤ 9·189^117 and
171/189 < 1, every n ≥ 117 gives

```text
N_n / 243^n ≤ 1 − 20x + 9x = 1 − 11x.                                   (3)
```

**Bounding H.** The numerator minus the denominator of H is 26X³ − 274X² + 956X − 1023. This is at most 26X³ for
X ≥ 4. For X ≥ 32 the denominator is at least (15/16)(7/8)(3/4)(1/2)X⁴ = (315/1024)X⁴. Since 26·1024 < 85·315,

```text
H(X) − 1 < 85/X = 42.5/2^n ≤ x     (85·9^117 ≤ 2·14^117, then monotone).   (4)
```

**Conclusion.** Also 11·7^117 < 9^117, so 1 − 11x > 0. N_n ≥ 0 because it counts sequences, so (1), (3) and (4)
give

```text
ρ_m ≤ (1 − 11x)(1 + x) = 1 − 10x − 11x² < 1     for every m ≥ 118.
```

## 4. Remaining dimensions (5 ≤ m ≤ 118)

The verifier checks the strict rational inequality Pr(E_1 ∩ … ∩ E_5) < s_m⁵ exactly at each of these 114
dimensions.

- **m = 5:** the joint probability is 0.
- **m = 6:** it is 2,880/|GL_6|, and ρ_6 ≈ 0.0056.
- **m = 7:** it is 39/225,763,328.

## 5. Leading deficit

By (2), N_n/243ⁿ = 1 − 20x + O((171/243)ⁿ), and 171/243 = (19/21)(7/9). By (4), H = 1 + O(2⁻ⁿ), and 1/2 < 171/243.
Multiplying the two gives the asserted deficit. The computed ratio (1−ρ_m)/x is 18.97 at m = 40, 19.98 at m = 80 and
19.9995 at m = 118.

## Scope

**Covered.** Exactly five fixed, pairwise orthogonal rank-one requests over F_2, with complete headers weighted
equally.

**Not settled.** k ≥ 6, odd characteristic, restricted header families and nonorthogonal kernels.

**Not claimed.**

- A physical saving: producer, header selection, emission, dispatch, dirty restoration, stock and precision are
  all unpriced.
- A supplier or a new κ.
- Formal proof-kernel review.
