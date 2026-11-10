# The profile (1,1,0,2)/(1,1,1) is character-excluded

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, the seven-call count profile

```
(a,b,p,q,r,s,t) = (1,1,0,2,1,1,1)
```

admits no word. Every decomposition of its determinant residual by three nonzero symmetric rational rank-one matrices admits an additive character that detects two calls and four targets.

This is a scoped proof for that one profile. It is not a multiplication theorem, not a search, and not a certificate that changes the selected κ `781451/250000000`. The other seventeen three-frame census profiles, including the sign-flipped profile `(1,1,2,0)/(1,1,1)`, stay open. The settled profiles `(1,1,1,1)/(1,1,1)`, `(0,2,1,1)/(1,1,1)`, and `(2,0,1,1)/(1,1,1)` are not reproved.

The inequality "detected calls ≥ detected targets" is inherited from `research/bit-two-signed-frame-floor/PROOF.md`, Section 1, which records the PR2910 normalization. This file does not reprove it.

## 1. The determinant equation

Addresses are rational symmetric 2-by-2 matrices,

```
A = diag(1,0),  B = diag(0,1),
P = [[1,1],[1,1]]/2,  Q = [[1,-1],[-1,1]]/2,
```

with `A+B = P+Q = I`. A general element has coefficient vector `(a,b,c)` and matrix

```
[[a + c/2, c/2], [c/2, b + c/2]].
```

Its determinant is `ab + c(a+b)/2`. The matrix is nonzero and rank one exactly when that determinant vanishes and the vector is nonzero. For a primitive integer direction `u = (u1,u2)` and a nonzero rational scale `t`,

```
t uu^T = (t u1(u1-u2), t u2(u2-u1), 2 t u1 u2).
```

Every nonzero symmetric rational rank-one matrix arises this way.

The profile uses one `A`, one `B`, no `P`, two `Q`, and three added labels `R,S,T` once each. The PR2910 determinant identity gives

```
R + S + T = 4I - A - B - 2Q.
```

Since `Q = I - P` and `I = A+B`,

```
4I - A - B - 2Q = I + 2P.
```

In coefficients that is `H = (1,1,2)`, with matrix `[[2,1],[1,2]]`. Its determinant is `3`, so `H` has rank 2. A hypothetical word produces nonzero symmetric rational rank-one `R,S,T` with `R+S+T = H`.

One such solution is `A + B + 2P`. Section 7 excludes it by the same character that excludes every other solution. It is a witness of the test, not a census.

Let `B(x,y) = 2 x1 y1 - x1 y2 - x2 y1 + 2 x2 y2` and `q(x) = B(x,x) = 2(x1^2 - x1 x2 + x2^2)`. Let `δ(x,y) = x1 y2 - x2 y1`. If `n = (-u2,u1)`, then `n^T H n = q(u)`, because `J^T H J` is the adjugate `[[2,-1],[-1,2]]` for the rotation `J(u1,u2) = (-u2,u1)`. The forms `3 x1 y1 + x2 y2` and `x1 y1 + 3 x2 y2` are the adjoints of `diag(1,3)` and `diag(3,1)`. Neither is this `B`: here `q(1,0) = q(0,1) = 2` and `B((1,0),(0,1)) = -1`.

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

In family AB, `f(A)` and `f(B)` are odd and `f(P)` and `f(Q)` are even. In family PQ the four parities are reversed. The four targets `A+P`, `A+Q`, `B+P`, and `B+Q` all have odd `a+b` and odd `c`, so every integer shift makes all four targets odd under either family.

On this profile, a form that is even on `R`, `S`, and `T` detects the following old calls:

- Family AB detects the one `A` call and the one `B` call, and neither `Q` call.
- Family PQ detects both `Q` calls and the absent `P` call, hence two calls.

Either way that is two detected calls against four detected targets. The inherited inequality forbids the pattern. It remains to show that one of the two forms extends to a character of the label lattice with `f(R)`, `f(S)`, and `f(T)` even.

The label lattice is `Λ = Z^3 + ZR + ZS`. It contains `T = H - R - S` because `H` lies in `Z^3`. Here `φ(H) = (0,0)`: both `a+b = 2` and `c = 2` are even. Consequently both families are even on `H` for every integer shift.

## 3. Extension from a vanishing coordinate

Let `U = ZR + ZS` and let `W = U ∩ Z^3`. Let `θ` be `(a+b)/2` in the AB case and `c/2` in the PQ case.

**Lemma 1.** Suppose `φ_AB` is identically zero on `W`. Then some AB form is an integer on `Λ` and is even on `R` and on `S`. The same holds for a PQ form when `φ_PQ` vanishes on `W`.

**Proof.** If `kR + lS = 0` in `Q^3`, then `k θ(R) + l θ(S) = 0`. On one primitive line, `θ` is proportional to the scale. Two nonparallel frames are linearly independent, because

```
det(c uu^T + d vv^T) = c d δ(u,v)^2
```

is nonzero when both scales and `δ(u,v)` are nonzero. Thus

```
ψ(kR+lS) = -(k θ(R) + l θ(S)) mod Z
```

is a homomorphism `U → Q/Z`, and the hypothesis says that `ψ` vanishes on `W`.

Let `d` be twice the least common multiple of the denominators of the coordinates of `R` and `S`. An integer vector `X` satisfies `X·R ≡ -θ(R)` and `X·S ≡ -θ(S)` modulo `Z` exactly when the same congruences hold after clearing `d`. A target in `(Z/dZ)^2` lies in the image of `X ↦ (X·(dR), X·(dS))` if and only if every integer pair `(k,l)` that kills the image also kills the target. Such a pair has `kR+lS ∈ Z^3`, and the target condition is the hypothesis. Hence some `X = (p,s,t)` exists. The corresponding form is even on `R` and on `S` and integer-valued on `Λ`.

**Lemma 2.** Either extension of Lemma 1 is even on `T` as well.

**Proof.** Both families are even on `H`, as recorded in Section 2. Then `f(T) = f(H) - f(R) - f(S)` is even.

The image of `φ = (φ_AB, φ_PQ)` on `W` is a subspace of `F2^2`. If it does not contain `(1,1)`, it cannot contain both `(1,0)` and `(0,1)`, so at least one coordinate functional vanishes. Lemmas 1 and 2 then supply a character, and Section 2 gives the forbidden count `2 < 4`.

Because `φ(H) = (0,0)`, an integral combination `kR + lS + mT` lies in `Z^3` only when `(k-m)R + (l-m)S` does, and the two combinations have the same image. The third frame does not enlarge the image of a pair.

## 4. One primitive line never has image (1,1)

**Lemma 3.** Let `u` be a primitive integer vector and let `t` be rational. If `t uu^T` lies in `Z^3`, then its `φ`-image is not `(1,1)`. An axial `u` forces the `P`-coefficient even and the scale `t` itself to be an integer. A diagonal `u` forces `a+b` even.

Axial means that exactly one coordinate is odd. Diagonal means that both are odd. Every primitive vector is one of these two kinds.

**Proof.** Write `Δ = u1 - u2`. The coefficient vector is `(t u1 Δ, -t u2 Δ, 2 t u1 u2)`. Since `gcd(u1,u2) = 1`, one has `gcd(Δ,u1) = gcd(Δ,u2) = 1`.

Suppose `u` is horizontal, so `u1` is odd, `u2` is even, and `Δ` is odd. Integrality of the first and third coordinates gives `Δ | 2 u2 a` after eliminating `t`, where `a` is the first coefficient. Thus `Δ | a`, because `Δ` is coprime to `2` and to `u2`. Writing `a = Δ a1` produces `t = a1/u1`. The second coefficient is then an integer multiple of `Δ/u1` times `u2`. Coprimality of `u1` with both `Δ` and `u2` forces `u1 | a1`, so `t` is an integer. The third coefficient `2 t u1 u2` is divisible by the even integer `u2`. The vertical case is the same argument with the two diagonal entries exchanged.

Suppose `u` is diagonal. Then `Δ` is even. The sum of the first two coefficients is `t Δ^2`. If `Δ = 0`, that sum is `0`. If `Δ ≠ 0` and the sum were an odd integer, then `v2(t) ≤ -2`, and the third coefficient `2 t u1 u2` would have valuation at most `-1`, because both direction coordinates are odd, so it would not be an integer.

**Corollary.** If two of `R,S,T` are rational multiples of one primitive `uu^T`, then one coordinate functional vanishes on their `W`. Lemmas 1 and 2 supply a character.

Three parallel directions cannot occur: their sum would have rank at most 1, while `det H = 3`. If exactly two directions are parallel, order those two as `R` and `S`. The corollary applies, whether or not the third direction is orthogonal to them.

## 5. Scales for three directions

**Lemma 4.** Let `α,β,γ` be odd integers with `α+β ≡ 0 (mod 4)`. Then `αβ - γ^2 ≡ 2 or 6 (mod 8)`.

**Proof.** The statement depends only on residues modulo 8. There are exactly 32 eligible classes. `verify.py` evaluates all 32. Odd squares are `1 (mod 8)`, and writing `β = 4t - α` leaves `4tα - 2 (mod 8)`.

**Lemma 5.** For every primitive integer vector `u`, `v2(q(u)) = 1`.

**Proof.** Modulo 2, squares equal the bits and `-1 ≡ 1`, so

```
x1^2 - x1 x2 + x2^2 ≡ x1 + x1 x2 + x2 (mod 2).
```

The right side is `1` for each of the three primitive classes `(1,0)`, `(0,1)`, and `(1,1)`, and those classes exhaust primitive vectors. Thus the parenthesis is odd and `q(u) = 2 · (odd)` has valuation exactly 1.

**Proposition 6.** Let `u,v,w` be pairwise nonparallel primitive integer vectors, and suppose

```
c_u uu^T + c_v vv^T + c_w ww^T = H
```

with all three scales nonzero. Then

```
c_u = B(v,w) / (δ(u,v) δ(u,w)),
```

and the cyclic formulas hold for `c_v` and `c_w`. In particular `B(v,w)`, `B(w,u)`, and `B(u,v)` are nonzero.

**Proof.** Evaluating the quadratic form on the perpendicular `n = (-u2,u1)` gives

```
c_v δ(u,v)^2 + c_w δ(u,w)^2 = q(u),
```

because `n·v = δ(u,v)` and `n^T H n = q(u)`. The cyclic analogues complete a linear system whose coefficient matrix has determinant `2 δ(u,v)^2 δ(u,w)^2 δ(v,w)^2 ≠ 0`, so the scales are unique. Substituting the cyclic expressions produces the bracket

```
δ(u,w) B(u,v) - δ(u,v) B(u,w) - q(u) δ(v,w).
```

This bracket vanishes for every symmetric bilinear form on a 2-dimensional space. If `ℓ(y) = B(u,y)`, the vector identity `δ(u,w) v - δ(u,v) w = δ(v,w) u` gives `δ(u,w) ℓ(v) - δ(u,v) ℓ(w) = q(u) δ(v,w)` after applying `ℓ`, since `ℓ(u) = q(u)`. `verify.py` expands the same polynomial for this particular `B` and finds no monomial.

## 6. The parity image avoids (1,1)

Let `R = c_u uu^T` and `S = c_v vv^T` be two of the three frames in Proposition 6, and suppose `N = kR + lS` lies in `Z^3` with `φ(N) = (1,1)`. Write `α = 2a+c`, `β = 2b+c`, and `γ = c`. All three are odd, and `α+β = 2(a+b+c) ≡ 0 (mod 4)`. Lemma 4 gives `v2(αβ-γ^2) = 1`.

The doubled matrix `[[α,γ],[γ,β]]` equals `σ uu^T + τ vv^T`, where `σ = 2 k c_u` and `τ = 2 l c_v`. Entry comparison gives, whenever the relevant first coordinates and `δ = δ(u,v)` are nonzero,

```
σ = G / (u1 δ),  τ = -H_ / (v1 δ),
αβ - γ^2 = -G H_ / (u1 v1),
```

with `G = α v2 - γ v1` and `H_ = α u2 - γ u1`. Hence `v2(G H_) = 1 + v2(u1) + v2(v1)`.

If a direction is axial, the corresponding linear form is odd: the odd coordinate contributes an odd term and the even coordinate an even term. If the direction is diagonal, the form is a difference of two odd integers and is even.

**Axis case.** Suppose `u1 = 0`. Primitivity gives `u = (0,ε)` with `ε = ±1`, and `q(u) = 2`. Nonparallelism forces `v1 ≠ 0` and `w1 ≠ 0`. The scale formulas collapse to

```
c_u = B(v,w) / (v1 w1),  c_v = (2 w2 - w1) / (v1 δ(v,w)).
```

Both signs `ε = ±1` give the same expressions: the factors of `ε` in `B(w,u)` and in `δ(v,u)` cancel, and `δ(u,v) δ(u,w) = v1 w1`. The doubled matrix has `α = τ v1^2` and `γ = τ v1 v2`. Oddness of `α` forces `v1` odd and `v2(τ) = 0`, and then oddness of `γ` forces `v2` odd. Thus `v` is diagonal. Also `l ≠ 0`: otherwise `N` would be a multiple of `uu^T`, which Lemma 3 forbids. Equating the two formulas for `c_v` gives

```
(v1 w2 - v2 w1) α = 2 l v1 (2 w2 - w1).
```

The coefficient of `w1` on the rearranged equation is `2 l v1 - α v2`, which is even minus odd, hence odd and nonzero. If `w2 = 0`, that equation forces `w1 = 0`, which is impossible. Thus `w2 ≠ 0`, and

```
w1 = v1 w2 (4l - α) / (2 l v1 - α v2).
```

Here `4l - α` is even minus odd, hence odd and nonzero, so `w1 ≠ 0` as well. Substituting `r = w2/w1` into `c_u = 2 - r - v2/v1 + 2 v2 r / v1` and clearing the denominator `v1^2 (4l-α)` produces the numerator identity

```
(2 v1 - v2) v1 (4l - α) + (2 l v1 - α v2)(2 v2 - v1)
  = 2(-α Q + 3 l v1^2),
```

where `Q = v1^2 - v1 v2 + v2^2`. Thus

```
c_u = 2(-α Q + 3 l v1^2) / (v1^2 (4l - α)).
```

`verify.py` expands this six-factor polynomial and finds that the two sides agree. The relation `αβ-γ^2 = σ α`, coming from `α = τ v1^2` and `αβ-γ^2 = σ τ v1^2`, rearranges `k c_u = (αβ-γ^2)/(2α)` into

```
v1^2 (4l - α)(αβ - γ^2) + 4 α k (α Q - 3 l v1^2) = 0.
```

The factor `4` is `2` from `σ = 2 k c_u` times the `2` in the numerator of `c_u`. It is not the constant `6` of the `diag(1,3)` axis equation. `verify.py` checks that this display is the cleared scale condition.

Under the oddness hypotheses, `v1` is odd, `4l-α` is odd, and `αβ-γ^2` has valuation exactly 1, so the first summand has valuation exactly 1. The second summand is divisible by `4`, so its valuation is at least 2. Their sum cannot be zero. Therefore `u1 ≠ 0`. Exchanging the two summands gives `v1 ≠ 0`.

**Cramer case.** Both first coordinates are nonzero, and `δ ≠ 0`. The entry comparison above gives `v2(G H_) = 1 + v2(u1) + v2(v1)`.

Both directions axial, and both directions diagonal, are impossible. Two horizontal directions would require valuation 1 while both forms are odd. Two vertical directions would require valuation at least 3 while both forms are odd. One horizontal and one vertical direction would require valuation at least 2 while both forms are odd. Two diagonal directions would require valuation 1 while both forms are even. The only remaining possibility is one axial direction and one diagonal direction. Different parity classes make `δ` odd: an axial-diagonal cross product is odd minus even, or even minus odd.

Equating the Cramer formulas with Proposition 6 gives

```
2 k u1 B(v,w) = G δ(u,w),  2 l v1 B(u,w) = H_ δ(v,w).
```

In coordinates `(w1,w2)` the coefficient matrix is

```
| 2 k u1 (2 v1 - v2) + G u2    2 k u1 (2 v2 - v1) - G u1 |
| 2 l v1 (2 u1 - u2) + H_ v2   2 l v1 (2 u2 - u1) - H_ v1 |.
```

Its determinant expands to

```
δ G H_ + 2 l G v1 q(u) - 2 k H_ u1 q(v) - 12 k l u1 v1 δ,
```

with this residual's `q`. `verify.py` expands both polynomials and finds that they agree. The existing direction `w` is a nontrivial kernel vector, so the determinant is zero.

Suppose `u` is axial and `v` is diagonal. Then `v2(H_) = 0`, `v1` is odd, `v2(δ) = 0`, and `v2(G) = 1 + v2(u1)`. The constant term has valuation exactly `1 + v2(u1)`. The `l` term has valuation at least `3 + v2(u1)`, because it carries a factor `2`, the factor `G`, and `q(u)` of valuation 1. The `k` term has valuation at least `2 + v2(u1)`, from the factor `2` and `q(v)`. The `kl` term has valuation at least `2 + v2(u1)`, from the factor `12`. Each is strictly larger than the constant valuation, whether or not `k` or `l` is divisible by 2. The determinant is nonzero.

Suppose `u` is diagonal and `v` is axial. Then `v2(G) = 0` and `v2(H_) = 1 + v2(v1)`. The constant term has valuation `1 + v2(v1)`. The `l` term has valuation at least `2 + v2(v1)`, the `k` term at least `3 + v2(v1)`, and the `kl` term at least `2 + v2(v1)`. Again the constant term is strictly smaller.

This contradiction shows that no vector of `W` has image `(1,1)`.

## 7. Conclusion

**Theorem.** The profile `(1,1,0,2,1,1,1)` admits no word in the PR2085/2112 model.

**Proof.** A hypothetical word would give rank-one `R,S,T` with `R+S+T = I+2P`. If two directions are parallel, Section 4 supplies a character. If all three directions are distinct, Section 6 shows that the parity image of every pair avoids `(1,1)`, so one coordinate functional vanishes, and Lemmas 1 and 2 supply a character. In both situations the character detects two calls and four targets. The inherited inequality forbids that pattern.

The explicit rational solution `A+B+2P` is the fixture `rational-rank-one`. Its PQ character, the unshifted form `f(a,b,c) = c`, is even on all three frames, odd on both `Q` calls, and odd on all four targets. The finite fixture list, the single-line box, the axis-reduction box, and the residue checks are not this theorem. Sections 4 through 6 are. Lemma 4, Lemma 5, and the polynomial identities are exhaustive finite or exact-expansion arguments.

## Open next questions

Seventeen three-frame count profiles from the census in discussion comment 19377345 remain open. This file settles only `(1,1,0,2)/(1,1,1)`. The sign-flipped tuple `(1,1,2,0)/(1,1,1)` has residual `[[2,-1],[-1,2]]` and is not implied by the calculation above. A useful first step for any one of the seventeen is to read that printed tuple, write its own determinant residual, and test one rational rank-one solution with that residual's bilinear form. The form in Section 1 does not transfer.

Four or more added frames are outside this three-summand argument.
