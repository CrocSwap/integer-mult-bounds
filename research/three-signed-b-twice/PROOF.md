# The profile (0,2,1,1)/(1,1,1) is character-excluded

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, the seven-call count profile

```
(a,b,p,q,r,s,t) = (0,2,1,1,1,1,1)
```

admits no word. Every decomposition of the determinant residual by three nonzero symmetric rational rank-one matrices admits an additive character that detects two calls and four targets.

This is a scoped proof for that one profile. It is not a multiplication theorem, not a search, and not a certificate that changes the selected κ `781451/250000000`. The other nineteen three-frame census profiles, and every decomposition with four or more added frames, stay open. The settled all-old-once profile `(1,1,1,1)/(1,1,1)` is not reproved.

The inequality "detected calls ≥ detected targets" is inherited from `research/bit-two-signed-frame-floor/PROOF.md`, Section 1, which records the PR2910 normalization. This file does not reprove it.

## 1. The determinant equation

Addresses are rational symmetric 2-by-2 matrices,

```
A = diag(1,0),  B = diag(0,1),
P = [[1,1],[1,1]]/2,  Q = [[1,-1],[-1,1]]/2,
```

with `A+B = P+Q = I`. A general element of the rational span has coefficient vector `(a,b,c)` and matrix

```
[[a + c/2, c/2], [c/2, b + c/2]].
```

Its determinant is `ab + c(a+b)/2`. The matrix is nonzero and rank one exactly when that determinant vanishes and the vector is nonzero. For a primitive integer direction `u = (u1,u2)` and a nonzero rational scale `t`,

```
t uu^T = (t u1(u1-u2), t u2(u2-u1), 2 t u1 u2).
```

Every nonzero symmetric rational rank-one matrix arises this way.

The profile uses two `B` calls, one `P` call, one `Q` call, and three added labels `R,S,T` once each. No `A` call is used. The PR2910 determinant identity gives

```
R + S + T = 4I - 2B - P - Q.
```

Since `P+Q = I` and `I = A+B`,

```
4I - 2B - P - Q = 3I - 2B = 3A + B = diag(3,1).
```

Write `H = 3A+B`, with coefficient vector `(3,1,0)`. A hypothetical word produces nonzero symmetric rational rank-one `R,S,T` satisfying `R+S+T = H`. Target support is not required for the exclusion below: the character already rules out every such triple, so it rules out every triple that a word could produce.

Let `B(x,y) = x1 y1 + 3 x2 y2` and `q(x) = B(x,x) = x1^2 + 3 x2^2`. Let `δ(x,y) = x1 y2 - x2 y1`.

## 2. Two character shapes

For an integral coefficient vector `N = (a,b,c)` write

```
φ_AB(N) = (a+b) mod 2,  φ_PQ(N) = c mod 2.
```

**Family AB.** Integers `p,s,t` give

```
f(a,b,c) = (1+2p)a + (1+2s)b + (2t)c.
```

**Family PQ.** Integers `p,s,t` give

```
f(a,b,c) = (2p)a + (2s)b + (1+2t)c.
```

In family AB, `f(A)` and `f(B)` are odd and `f(P)` and `f(Q)` are even. In family PQ, `f(A)` and `f(B)` are even and `f(P)` and `f(Q)` are odd. Either evaluation is immediate from `Q = A+B-P`.

The four targets are `A+P = (1,0,1)`, `A+Q = (2,1,-1)`, `B+P = (0,1,1)`, and `B+Q = (1,2,-1)`. Substituting the forms shows that every integer shift `(p,s,t)` makes all four targets odd. Thus either character detects four targets.

On this profile the same forms detect the following old calls when they vanish on `R,S,T`:

- Family AB detects the two `B` calls and no `A` call, because `a = 0` and `b = 2`.
- Family PQ detects the one `P` call and the one `Q` call.

Either way that is two detected calls. The inherited inequality forbids two detected calls against four detected targets. It remains only to show that one of the two forms extends to a character of the label lattice with `f(R)`, `f(S)`, and `f(T)` even.

The label lattice is `Λ = Z^3 + ZR + ZS`. It contains `T` because `T = H-R-S` and `H` lies in `Z^3`. A form above is integer-valued on `Z^3`. It descends to a character `Λ → F2` once it is integer-valued on `Λ` and even on `2Λ`, which is automatic for an integer-valued homomorphism into `Z` read modulo 2.

## 3. Extension from a vanishing coordinate

Let `U = ZR + ZS` and let `W = U ∩ Z^3`. Let `θ` be `(a+b)/2` in the AB case and `c/2` in the PQ case.

**Lemma 1.** Suppose `φ_AB` is identically zero on `W`. Then some AB form is an integer on `Λ` and is even on `R` and on `S`. The same holds for a PQ form when `φ_PQ` vanishes on `W`.

**Proof.** If `kR + lS = 0` in `Q^3`, then `k θ(R) + l θ(S) = 0`. Indeed `θ` is linear, and on a single primitive line it is proportional to the scale: the AB value of `t uu^T` is `t(u1-u2)^2/2` and the PQ value is `t u1 u2`. Two parallel frames are scales of one matrix, so a linear dependence of the frames is a linear dependence of the scales. Two nonparallel frames are linearly independent, because a primitive direction has a nonzero perpendicular and the determinant formula

```
det(c uu^T + d vv^T) = c d δ(u,v)^2
```

is nonzero when both scales and `δ(u,v)` are nonzero. Thus

```
ψ(kR+lS) = -(k θ(R) + l θ(S)) mod Z
```

is a well-defined homomorphism `U → Q/Z`. The hypothesis says that `ψ` vanishes on `W`.

Let `d` be twice the least common multiple of the denominators of the coordinates of `R` and `S`. Then `dR`, `dS`, `dθ(R)`, and `dθ(S)` are integers. An integer vector `X` satisfies `X·R ≡ -θ(R)` and `X·S ≡ -θ(S)` modulo `Z` exactly when

```
X·(dR) ≡ -d θ(R),  X·(dS) ≡ -d θ(S)  (mod d).
```

A target in `(Z/dZ)^2` lies in the image of `X ↦ (X·(dR), X·(dS))` if and only if every integer pair `(k,l)` that kills the image also kills the target. Such a pair has `kR+lS ∈ Z^3`, and the target condition is then `kθ(R)+lθ(S) ∈ Z`, which is the hypothesis. Hence some `X = (p,s,t)` exists. The corresponding form satisfies `f(R) ∈ 2Z` and `f(S) ∈ 2Z`, and it is integer-valued on `Λ = Z^3 + U`.

**Lemma 2.** Either extension of Lemma 1 is even on `T` as well.

**Proof.** The AB form takes the value `(1+2p)·3 + (1+2s)·1 = 4 + even` on `H = (3,1,0)`, and the PQ form takes `2p·3 + 2s·1`, which is even. Thus `f(H)` is even. Then `f(T) = f(H) - f(R) - f(S)` is even.

Consequently, once either coordinate functional vanishes on `W`, the profile's calls and targets give the forbidden count `2 < 4`.

The image of `φ = (φ_AB, φ_PQ)` on `W` is a subspace of `F2^2`. If it does not contain `(1,1)`, it cannot contain both `(1,0)` and `(0,1)`, so at least one coordinate functional vanishes. The rest of the argument shows that `(1,1)` never occurs.

## 4. One primitive line never has image (1,1)

**Lemma 3.** Let `u` be a primitive integer vector and let `t` be rational. If `t uu^T` lies in `Z^3`, then its `φ`-image is not `(1,1)`. An axial `u` forces the `P`-coefficient even and the scale `t` itself to be an integer. A diagonal `u` forces `a+b` even.

Axial means that exactly one coordinate is odd. Diagonal means that both are odd. Every primitive vector is one of these two kinds. Horizontal means `(odd, even)` and vertical means `(even, odd)`.

**Proof.** Write `Δ = u1-u2`. The coefficient vector is

```
(t u1 Δ, -t u2 Δ, 2 t u1 u2).
```

Since `gcd(u1,u2) = 1`, one has `gcd(Δ,u1) = gcd(u2,u1) = 1` and `gcd(Δ,u2) = 1`.

Suppose `u` is horizontal, so `u1` is odd, `u2` is even, and `Δ` is odd. Integrality of the first and third coordinates gives `Δ | 2 u2 a` after eliminating `t`, where `a` is the first coefficient. Thus `Δ | a`, because `Δ` is coprime to `2` and to `u2`. Writing `a = Δ a1` produces `t = a1/u1`. The second coefficient is then an integer multiple of `Δ/u1` times `u2`. Coprimality of `u1` with both `Δ` and `u2` forces `u1 | a1`, so `t` is an integer. The third coefficient `2 t u1 u2` is divisible by the even integer `u2`.

The vertical case is the same argument with the two diagonal entries exchanged: the odd coordinate is now the second one, and the third coefficient is divisible by the even first coordinate.

Suppose `u` is diagonal. Then `Δ` is even. If `Δ = 0`, the direction is parallel to `(1,1)` and the sum of the first two coefficients is `0`, which is even. If `Δ ≠ 0`, then `v2(Δ^2) ≥ 2`. That sum is `t Δ^2`. If it were an odd integer, then `v2(t) ≤ -2`. The third coefficient `2 t u1 u2` would have valuation `1+v2(t) ≤ -1`, because both direction coordinates are odd, and would not be an integer.

**Corollary.** If `R` and `S` are rational multiples of one primitive `uu^T`, then one coordinate functional vanishes on `W`. Lemmas 1 and 2 supply a character, and the profile is excluded.

Three parallel directions cannot occur: their sum would have rank at most 1, while `H = diag(3,1)` has rank 2. If exactly two directions are parallel, order the frames so that those two are `R` and `S`. The corollary applies.

## 5. Scales for three directions

**Lemma 4.** Let `α,β,γ` be odd integers with `α+β ≡ 0 (mod 4)`. Then `αβ - γ^2 ≡ 2 or 6 (mod 8)`.

**Proof.** The statement depends only on residues modulo 8. There are exactly 32 eligible classes: each of `α,β,γ` lies in `{1,3,5,7}`, and `α+β ≡ 0 (mod 4)`. `verify.py` evaluates all 32. This finite check is the whole lemma, because every eligible integer triple reduces to one class. The same expansion used for the all-old-once profile explains the count: odd squares are `1 (mod 8)`, and writing `β = 4t-α` leaves `4tα - 2 (mod 8)`.

**Proposition 5.** Let `u,v,w` be pairwise nonparallel primitive integer vectors, and suppose

```
c_u uu^T + c_v vv^T + c_w ww^T = H
```

with all three scales nonzero. Then

```
c_u = B(v,w) / (δ(u,v) δ(u,w)),
```

and the cyclic formulas hold for `c_v` and `c_w`. In particular `B(v,w)`, `B(w,u)`, and `B(u,v)` are nonzero.

**Proof.** The three matrices `uu^T`, `vv^T`, and `ww^T` are linearly independent. The same perpendicular evaluation used for `2I` gives the system

```
c_v δ(u,v)^2 + c_w δ(u,w)^2 = q(u)
```

and its cyclic analogues. The coefficient matrix has determinant `2 δ(u,v)^2 δ(u,w)^2 δ(v,w)^2 ≠ 0`, so the scales are unique. It is therefore enough to check the displayed formula. Substituting the cyclic expressions produces the bracket

```
δ(u,w) B(u,v) - δ(u,v) B(u,w) - q(u) δ(v,w).
```

Expanding in the six coordinates, the terms `±3 u1 u2 v2 w2` and `± u1 u2 v1 w1` cancel, and the rest factors as `q(u) δ(v,w)`. The bracket is identically zero. `verify.py` expands the same polynomial and finds no monomial. The cyclic brackets are the same identity with the variables permuted.

## 6. The parity image avoids (1,1)

Let `R = c_u uu^T` and `S = c_v vv^T` be two of the three frames in Proposition 5, and suppose `N = kR + lS` lies in `Z^3` with `φ(N) = (1,1)`. Write `α = 2a+c`, `β = 2b+c`, and `γ = c` for the coefficient vector of `N`. All three are odd, and `α+β = 2(a+b+c) ≡ 0 (mod 4)` because `a+b` and `c` are both odd. Lemma 4 gives `v2(αβ-γ^2) = 1`. The doubled matrix is `[[α,γ],[γ,β]]`.

**Axis case.** Suppose `u1 = 0`. Primitivity gives `u = (0,ε)` with `ε = ±1`. Nonparallelism forces `v1 ≠ 0` and `w1 ≠ 0`. The scale formulas collapse to

```
c_u = 1 + 3 v2 w2 / (v1 w1),  c_v = 3 w2 / (δ(v,w) v1).
```

The doubled matrix has `α = τ v1^2` and `γ = τ v1 v2`, where `τ = 2 l c_v`. Oddness of `α` forces `v1` and `τ` to be odd, and then oddness of `γ` forces `v2` odd. Thus `v` is diagonal. Also `gcd(v1,v2) = 1`, so `v1` divides `α`, and `τ = α / v1^2` has valuation 0.

The identity `αβ-γ^2 = σ τ v1^2` with `σ = 2 k c_u` gives `v2(σ) = 1`. Equating the two formulas for `c_v` gives

```
δ(v,w) = 6 l v1 w2 / α.
```

The right side vanishes only if `w2 = 0` or `l = 0`. The second would make `N` a multiple of `uu^T`, which Lemma 3 forbids. The first makes `w` horizontal, so `δ(v,w) = ∓ v2 ≠ 0`. Thus `w2 ≠ 0`, and solving for `w1` gives

```
w1 = v1 w2 (α - 6l) / (α v2).
```

The same doubled-matrix identity gives `k c_u = (αβ-γ^2)/(2α)`. Substituting `c_u` and then `w1` produces

```
(α-6l) v1^2 (αβ-γ^2 - 2α k) = 6 α^2 k v2^2.
```

Here `α`, `v1`, and `v2` are odd, so `α-6l` is odd. The right side has valuation `1 + v2(k)`.

If `v2(k) ≥ 1`, the left bracket has valuation 1, because `αβ-γ^2` has valuation 1 and `2αk` has valuation at least 2. The left side then has valuation 1 and the right side has valuation at least 2.

If `v2(k) = 0`, both `αβ-γ^2` and `2αk` are congruent to `2` or `6` modulo 8, by Lemma 4 and the oddness of `α` and `k`. Their difference is congruent to `0` or `4` modulo 8, so its valuation is at least 2. The right side is nonzero and has valuation 1.

Both alternatives contradict the equation. Therefore `u1 ≠ 0`. Exchanging the two summands gives `v1 ≠ 0`.

**Cramer case.** Both first coordinates are nonzero, and `δ = δ(u,v) ≠ 0`. Set `G = α v2 - γ v1` and `H_ = α u2 - γ u1`. Entry comparison gives

```
σ = G / (u1 δ),  τ = -H_ / (v1 δ),
αβ - γ^2 = -G H_ / (u1 v1),
```

where `σ = 2 k c_u` and `τ = 2 l c_v`. Hence

```
v2(G H_) = 1 + v2(u1) + v2(v1),
```

with valuations taken on absolute values. If `u` is axial then `H_` is odd: the odd coordinate of `u` contributes an odd term and the even coordinate an even term. The same holds for `G` when `v` is axial. If the direction is diagonal, the corresponding linear form is a difference of odd integers and is even.

Both directions axial, and both directions diagonal, are then impossible. Two horizontal directions would require valuation 1 while both forms are odd. Two vertical directions would require valuation at least 3 while both forms are odd. One horizontal and one vertical direction would require valuation at least 2 while both forms are odd. Two diagonal directions would require valuation 1 while both forms are even. The only remaining possibility is one axial direction and one diagonal direction. Different parity classes make `δ` odd.

Equating the Cramer formulas with Proposition 5 gives the linear system

```
2 k u1 B(v,w) = G δ(u,w),  2 l v1 B(u,w) = H_ δ(v,w).
```

In coordinates `(w1,w2)` the coefficient matrix is

```
| 2 k u1 v1 + G u2    6 k u1 v2 - G u1 |
| 2 l u1 v1 + H_ v2   6 l v1 u2 - H_ v1 |.
```

Its determinant expands to

```
δ G H_ + 2 l G v1 q(u) - 2 k H_ u1 q(v) - 12 k l u1 v1 δ.
```

The grouping is the one checked as a polynomial identity in `verify.py`: the `G H_` terms produce `δ G H_`, the `k H_` terms produce `-2 k H_ u1 q(v)`, the `G l` terms produce `2 l G v1 q(u)`, and the `k l` terms produce `-12 k l u1 v1 δ`. The existing direction `w` is a nontrivial kernel vector, so this determinant is zero.

A diagonal primitive vector has `q ≡ 4 (mod 8)`, because both squares are `1 (mod 8)`. Thus its quadratic valuation is exactly 2. An axial primitive vector has odd `q`: the odd coordinate contributes an odd square and the even coordinate an even term. Thus its quadratic valuation is 0.

Suppose `u` is axial and `v` is diagonal. Then `v2(H_) = 0`, `v1` is odd, and `v2(G) = 1+v2(u1)`. The constant term has valuation exactly `1+v2(u1)`, and it is nonzero. The `l` term has valuation at least `2+v2(u1)`, the `k` term at least `3+v2(u1)`, and the `kl` term at least `2+v2(u1)`. Each is strictly larger than the constant valuation, whether or not `k` or `l` is divisible by 2. The determinant therefore has valuation `1+v2(u1)` and is not zero.

Suppose `u` is diagonal and `v` is axial. Then `v2(G) = 0` and `v2(H_) = 1+v2(v1)`, while `v2(q(u)) = 2` and `v2(q(v)) = 0`. The constant term has valuation `1+v2(v1)`. The `l` term has valuation at least `3+v2(v1)`, the `k` term at least `2+v2(v1)`, and the `kl` term at least `2+v2(v1)`. Again the constant term is strictly smaller, so the determinant is nonzero.

This contradiction shows that no vector of `W` has image `(1,1)`.

The third frame does not enlarge the image. Because `T = H-R-S` and `φ(H) = (0,0)`, an integral combination `kR+lS+mT` lies in `Z^3` only when `(k-m)R+(l-m)S` does, and the two combinations have the same image under `φ`.

## 7. Conclusion

**Theorem.** The profile `(0,2,1,1,1,1,1)` admits no word in the PR2085/2112 model.

**Proof.** A hypothetical word would give rank-one `R,S,T` with `R+S+T = 3A+B`. If two directions are parallel, Section 4 supplies a character. If all three directions are distinct, Section 6 shows that the parity image of `W` avoids `(1,1)`, so one coordinate functional vanishes, and Lemmas 1 and 2 supply a character. In both situations the character detects two calls and four targets. The inherited inequality forbids that pattern.

The explicit forms found for the fixtures in `verify.py` are witnesses of the extension. The finite fixture list, the single-line box, and the valuation-arithmetic checks are not this theorem. Sections 4 through 6 are. Lemma 4 and the two polynomial identities are exhaustive finite or exact-expansion arguments, as recorded in Section 5 and in the verifier.

## Open next questions

Nineteen three-frame count profiles from the census in discussion comment 19377345 remain open, including the twelve siblings of this profile such as `(2,0,1,1)/(1,1,1)`. A useful first step for `(2,0,1,1)` is to repeat the scale formula with the bilinear form `3 x1 y1 + x2 y2`, because the residual there is `diag(1,3)` rather than `diag(3,1)`. The constants 3, 6, and 12 in this file belong to `3A+B` and are not claimed for another residual.

Four or more added signed rank-one frames are also open. This argument stops at three summands.
