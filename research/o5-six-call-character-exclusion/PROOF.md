# The six-call orbit O5 is character-excluded

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, assume the two premises in Section 1. Let the old counts `(a,b,p,q)` be one of

```
(0,1,1,1),  (1,0,1,1),  (1,1,0,1),  (1,1,1,0)
```

and let three added labels each be used once. Then there is no word. Every decomposition of the residual into three nonzero symmetric rational rank-one matrices admits an additive character that detects two calls and four targets.

These four profiles are the orbit O5 of PR #7128. The representative `(0,1,1,1)/(1,1,1)` has residual `diag(3,2)`. The argument is written for the coordinate swap `(1,0,1,1)`, whose residual is `diag(2,3)` and whose quadratic form is `3 x1^2 + 2 x2^2`, and Section 8 carries it back.

Evidence class: **proof**, for these four profiles and these hypotheses only. It is not a multiplication theorem, not a search, and not a change to the selected κ `363005817/100000000000`. Rational solutions of the matrix equation exist. The obstruction is the character. Orbits O3 and O4, and every decomposition with four or more added frames, stay open. The excluded orbit O2 is not redone.

The literal parity-image conclusion of PR #7035 does not transfer. Section 6 records where the 2-adic estimate stops being strict, and gives a decomposition whose parity image contains `(1,1)`. The exclusion uses a different pair of the same triple.

## 1. Premises and the residual

Addresses are rational symmetric 2-by-2 matrices,

```
A = diag(1,0),  B = diag(0,1),
P = [[1,1],[1,1]]/2,  Q = [[1,-1],[-1,1]]/2,
```

with `A+B = P+Q = I`. A general element has coefficient vector `(a,b,c)` and matrix

```
[[a + c/2, c/2], [c/2, b + c/2]].
```

Its determinant is `ab + c(a+b)/2`. For a primitive integer direction `u = (u1,u2)` and a nonzero rational scale `t`,

```
t uu^T = (t u1(u1-u2), t u2(u2-u1), 2 t u1 u2).
```

Every nonzero symmetric rational rank-one matrix arises this way.

Two premises are cited and not reproved. They are the determinant identity and the first-order character inequality in `research/bit-two-signed-frame-floor/PROOF.md`, Section 1, which records the PR2910 normalization used by PR #6190. That file writes the determinant identity for two added labels. The same counting, with three added labels each used once, is the form used by the merged all-old-once exclusion and by the open three-frame papers. This note uses it in that form.

- **(P1)** The labels of a word with old counts `(a,b,p,q)` and three added labels once each satisfy `R+S+T = 4I - aA - bB - pP - qQ`.
- **(P2)** For those labels, every additive character detects at least as many calls as targets.

For `(a,b,p,q) = (1,0,1,1)`,

```
4I - A - P - Q = 3I - A = 2A + 3B = diag(2,3).
```

Write `H* = diag(2,3)`, with coefficient vector `(2,3,0)` and determinant `6`. Let `n(u) = (-u2, u1)`,

```
q(u) = n(u)^T H* n(u) = 3 u1^2 + 2 u2^2,  B(x,y) = 3 x1 y1 + 2 x2 y2.
```

The form `3 x1^2 + x2^2` of PR #7035 belongs to `diag(1,3)`. Replacing the coefficient of `x2^2` by `2` is the form of this residual. The coordinate swap of Section 8 sends `H*` to `diag(3,2)` and `(1,0,1,1)` to the named profile `(0,1,1,1)`.

A hypothetical word produces nonzero symmetric rational rank-one `R,S,T` with `R+S+T = H*`. One such decomposition is `3P + 3Q - A`. The character below rules out every such triple, so it rules out every triple a word could produce.

For an integral coefficient vector write

```
φ_AB = (a+b) mod 2,  φ_PQ = c mod 2,  φ = (φ_AB, φ_PQ).
```

**Family AB.** Integers `p,s,t` give `f(a,b,c) = (1+2p)a + (1+2s)b + 2t c`.

**Family PQ.** Integers `p,s,t` give `f(a,b,c) = 2p a + 2s b + (1+2t)c`.

On `Z^3`, an AB form is congruent to `a+b` and a PQ form is congruent to `c`. The four targets are `A+P = (1,0,1)`, `A+Q = (2,1,-1)`, `B+P = (0,1,1)`, and `B+Q = (1,2,-1)`. Each has odd `a+b` and odd `c`, so every form in either family is odd on all four targets and detects four targets.

On the profile `(1,0,1,1)`, an AB form detects the one `A` call and no `B`, `P`, or `Q` call. A PQ form detects the one `P` call and the one `Q` call. The same arithmetic on the named profile `(0,1,1,1)` detects the one `B` call in family AB and the two calls `P` and `Q` in family PQ.

The label lattice is `Λ = Z^3 + ZR + ZS`. It contains `T` because `T = H* - R - S`.

## 2. Extension

Let `U = ZR + ZS` and `W = U ∩ Z^3`. Let `θ` be `(a+b)/2` in the AB case and `c/2` in the PQ case. Both are linear forms on coefficient vectors.

**Lemma 1.** Suppose `φ_AB` vanishes on `W`. Then some AB form is an integer on `Λ` and is even on `R` and on `S`, whether or not `R` and `S` lie on the same line. The same holds for a PQ form when `φ_PQ` vanishes on `W`.

**Proof.** On one primitive line, `θ_AB(t uu^T) = t(u1-u2)^2/2` and `θ_PQ(t uu^T) = t u1 u2`, so `θ` is proportional to the scale. A linear dependence of two frames on that line is a linear dependence of the scales, and `θ` respects it. If the frames are nonparallel, they are linearly independent, because

```
det(c uu^T + d vv^T) = c d δ(u,v)^2
```

with `δ(u,v) = u1 v2 - u2 v1`. Thus

```
ψ(kR+lS) = -(k θ(R) + l θ(S)) mod Z
```

is a well-defined homomorphism `U → Q/Z`. Vanishing of `φ` on `W` means `θ(W) ⊂ Z`, so `ψ` vanishes on `W`.

Let `d` be twice the least common multiple of the denominators of the coordinates of `R` and `S`. Then `dR`, `dS`, `dθ(R)`, and `dθ(S)` are integers. An integer vector `X` satisfies `X·R ≡ -θ(R)` and `X·S ≡ -θ(S)` modulo `Z` exactly when

```
X·(dR) ≡ -d θ(R),  X·(dS) ≡ -d θ(S)  (mod d).
```

A target in `(Z/dZ)^2` lies in the image of `X ↦ (X·(dR), X·(dS))` if and only if every integer pair `(k,l)` that kills the image also kills the target. Such a pair has `kR+lS ∈ Z^3`, and the target condition is then `kθ(R)+lθ(S) ∈ Z`, which is the vanishing of `ψ` on `W`. Hence some `X = (p,s,t)` exists. The corresponding form is even on `R` and on `S` and integer-valued on `Λ`. ∎

**Lemma 2.** On this residual, the AB extension of Lemma 1 is odd on `T`, and the PQ extension is even on `T`. Either one detects two calls and four targets on the profile `(1,0,1,1)`.

**Proof.** Every AB form takes the value `(1+2p)·2 + (1+2s)·3 = 5 + even` on `H* = (2,3,0)`, which is odd. Every PQ form takes an even value there. Thus an AB form that is even on `R` and on `S` is odd on `T = H*-R-S`, and a PQ form that is even on `R` and on `S` is even on `T`.

The AB character detects the one `A` call and the one frame `T`, hence two calls, and all four targets. The PQ character detects the `P` call and the `Q` call, and no frame, hence two calls, and all four targets. Premise (P2) forbids either pattern. ∎

The image of `φ` on `W` is a subgroup of `F2^2`. If it does not contain `(1,1)`, it cannot contain both `(1,0)` and `(0,1)`, so at least one coordinate functional vanishes. Lemmas 1 and 2 then exclude the decomposition. Call a pair of frames **safe** when no vector of its `W` has image `(1,1)`.

## 3. One line never has image (1,1)

**Lemma 3.** Let `u` be a primitive integer vector and let `t` be rational. If `t uu^T` lies in `Z^3`, then its `φ`-image is not `(1,1)`. An axial `u` forces the off-diagonal coefficient to be even, and forces `t` itself to be an integer. A diagonal `u` forces `a+b` even.

Axial means that exactly one coordinate of `u` is odd. Diagonal means that both are odd. Horizontal means `(odd, even)` and vertical means `(even, odd)`. The axis is the vertical line through `(0,1)`.

**Proof.** The coefficient vector is `(t u1 Δ, -t u2 Δ, 2 t u1 u2)` with `Δ = u1-u2`. Since `gcd(u1,u2) = 1`, one has `gcd(Δ,u1) = gcd(Δ,u2) = 1`.

If `u` is horizontal, then `Δ` is odd and coprime to `u2`. Integrality of the first coefficient and the relation `c = 2 a u2/Δ` force `Δ` to divide `a`, and then coprimality forces `t` to be an integer. The third coefficient is divisible by the even integer `u2`. The vertical case exchanges the diagonal entries. This is the argument of PR #7035, Lemma 3, and it does not use `H*`.

If `u` is diagonal, then `Δ` is even and `a+b = t Δ^2`. A nonzero even `Δ` has `v2(Δ^2) ≥ 2`. An odd value of `a+b` would force `v2(t) ≤ -2`, and then `c = 2 t u1 u2` would have valuation `1+v2(t) ≤ -1` because both direction coordinates are odd. ∎

**Corollary.** If `R` and `S` lie on one primitive line, their pair is safe. If all three frames lie on one line, their sum has rank at most 1, while `det H* = 6`. So a decomposition uses either two lines or three.

## 4. Scales

**Proposition 4.** Let `u,v,w` be pairwise nonparallel primitive integer vectors, and suppose

```
c_u uu^T + c_v vv^T + c_w ww^T = H*
```

with all three scales nonzero. Then

```
c_u = B(v,w) / (δ(u,v) δ(u,w)),
```

and the cyclic formulas hold for `c_v` and `c_w`. In particular `B(v,w)`, `B(w,u)`, and `B(u,v)` are nonzero.

**Proof.** Evaluating the quadratic form on `n(u)` gives

```
c_v δ(u,v)^2 + c_w δ(u,w)^2 = q(u).
```

The cyclic equations complete a linear system. Its coefficient matrix has determinant `2 δ(u,v)^2 δ(u,w)^2 δ(v,w)^2 ≠ 0`, so the scales are unique. The displayed formula satisfies the system because the bracket

```
δ(u,w) B(u,v) - δ(u,v) B(u,w) - q(u) δ(v,w)
```

is the zero polynomial. `verify.py` expands that polynomial in six variables and finds no monomial. The same expansion with the coefficient `1` in place of `2` is the bracket of PR #7035; the two polynomials are not the same. ∎

## 5. Pairs that cannot carry (1,1)

Let `N = kR + lS` lie in `Z^3` with `φ(N) = (1,1)`. Write `α = 2a+c`, `β = 2b+c`, and `γ = c`. All three are odd, and `α+β = 2(a+b+c)` is divisible by 4 because `a+b` and `c` are both odd. The next lemma is the one from PR #7035. It does not use the residual.

**Lemma 5.** If `α,β,γ` are odd and `α+β ≡ 0 (mod 4)`, then `αβ-γ^2 ≡ 2 or 6 (mod 8)`, so `v2(αβ-γ^2) = 1`.

`verify.py` evaluates the 32 residue classes. Odd squares are `1 (mod 8)`, and `β = 4t-α` leaves `αβ-γ^2 ≡ 4tα - 2 (mod 8)`.

Let the doubled matrix of `N` be `[[α,γ],[γ,β]] = σ uu^T + τ vv^T`, where `σ = 2 k c_u` and `τ = 2 l c_v`. Entry comparison gives the polynomial identities

```
G = α v2 - γ v1 = σ u1 δ,  H_ = α u2 - γ u1 = -τ v1 δ,
αβ - γ^2 = σ τ δ^2 = -G H_ / (u1 v1),
```

whenever `u1`, `v1`, and `δ = δ(u,v)` are nonzero. `verify.py` expands these identities. Consequently

```
v2(G H_) = 1 + v2(u1) + v2(v1).
```

Since `α` and `γ` are odd, `G ≡ u1+u2 (mod 2)` and `H_ ≡ v1+v2 (mod 2)`. An axial direction makes its linear form odd. A diagonal direction makes it even.

**Proposition 6.** A pair of nonparallel frames has no integral combination of image `(1,1)` in any of these situations.

1. Both directions are diagonal.
2. Both are horizontal.
3. Both are vertical and neither is the axis.
4. One is horizontal, one is vertical, and the vertical one is not the axis.
5. One is the axis and the other is not diagonal.
6. One is the axis, the other is diagonal, and the third direction of the decomposition is not diagonal.

**Proof of (1)–(4).** Both first coordinates are nonzero, so the valuation formula applies. In (1) the required valuation is `1`, while both forms are even, so the product has valuation at least `2`. In (2) the required valuation is `1`, while both forms are odd. In (3) each first coordinate has valuation at least `1`, so the required valuation is at least `3`, while both forms are odd. In (4) the required valuation is at least `2`, while both forms are odd. ∎

The quadratic form is not used here. These four exclusions are the part of the PR #7035 case split that survives. The part that does not survive is the mixed axial-diagonal estimate and the axis estimate. Both used a strict inequality that the coefficient `2` removes. The Cramer determinant of the `(w1,w2)` system is recorded in `verify.py`: its `kl` coefficient is `24`, where PR #7035 had `12`, and `q` is the new form. That identity is not an input of Proposition 6. The witness in Section 6 shows why a mixed pair can carry `(1,1)`.

**Proof of (5) and (6).** Suppose the axis frame is `R = c_u uu^T` with `u = (0,ε)`, `ε = ±1`, and `S = c_v vv^T` contributes to a vector of image `(1,1)`. The top-left entry of the doubled matrix is `α = τ v1^2` and the off-diagonal entry is `γ = τ v1 v2`. Oddness of `α` forces `v1` and `τ` to be odd, and oddness of `γ` then forces `v2` to be odd. So `v` is diagonal. This is (5): a non-diagonal partner is impossible.

The scale formulas collapse to

```
c_u = 3 + 2 v2 w2 / (v1 w1),  c_v = 2 w2 / (δ(v,w) v1).
```

`verify.py` compares these with Proposition 4 on every primitive pair of coordinates at most `4`. From `τ = 2 l c_v` and `τ = α/v1^2`,

```
δ(v,w) = 4 l v1 w2 / α.
```

The case `l = 0` makes `N` a multiple of the axis frame, which Lemma 3 forbids. The case `w2 = 0` makes `w` horizontal, so `δ(v,w) = ∓ v2 ≠ 0`, while the right side vanishes. Thus

```
w1 = v1 w2 (α - 4l) / (α v2).
```

Here `α`, `v1`, and `v2` are odd, and `α-4l` is odd. The primitive direction of `w` has two odd coordinates, so `w` is diagonal. This is (6).

The factor `4` is the product of the `2` in `τ = 2 l c_v` and the `2` in the numerator of `c_v`. For `diag(1,3)` that numerator was `1` and the gap in the cleared equation was strict. The cleared equation here is the polynomial identity

```
(α-4l) v1^2 (αβ-γ^2 - 6α k) = 4 α^2 k v2^2,
```

checked by expansion in `verify.py`. If `v2(k) ≥ 1`, the left side has valuation `1` and the right side has valuation at least `3`, because `v2(6αk) ≥ 2` while `v2(αβ-γ^2) = 1`, and `α-4l` and `v1` are odd. That subcase is impossible. If `v2(k) = 0`, both sides can have valuation `2`: the right side is `4` times odd integers, and `αβ-γ^2 - 6αk` is a difference of two integers each congruent to `2` or `6` modulo `8`. There is no contradiction. The determinant `6` is what puts the extra factor of `2` on the right side. The structural conclusion used above does not need this valuation split. The split is the redone 2-adic step, and it stops exactly on the odd-`k` axis case. ∎

## 6. A pair can carry (1,1)

The statement "no pair carries `(1,1)`" is false for this residual. Take the directions `(-5,1)`, `(-3,4)`, and `(-1,1)` at scales `1/4`, `1`, and `-53/4`. Proposition 4 gives three nonzero rank-one frames summing to `H*`. The combination

```
2·(scale 1/4 on (-5,1)) + 1·(scale 1 on (-3,4)) = (36, 31, -29)
```

has `a+b = 67` and `c = -29`, so its image is `(1,1)`. The first and third directions are diagonal, so Proposition 6(1) says that pair is safe. The AB form `a+b+2c` is even on those two frames and odd on the horizontal frame. It detects two calls and four targets.

The same phenomenon occurs on the axis. The directions `(0,1)`, `(-5,3)`, and `(-3,5)` at scales `5`, `1/8`, and `-1/8` sum to `H*`. The combination of the axis frame with coefficient `1` and the first diagonal frame with coefficient `4` is `(20, 17, -15)`, of image `(1,1)`. The coefficient of the axis frame is odd, which is the subcase the valuation split does not forbid. The two diagonal frames form a safe pair, and the AB form `a+b` is even on both and odd on the axis frame.

`verify.py` checks both witnesses in exact arithmetic, including the sums, the ranks, the images, and the call counts.

## 7. Every decomposition has a safe pair

**Proposition 7.** Every decomposition of `H*` into three nonzero symmetric rational rank-one matrices has a safe pair.

**Proof.** If two frames lie on one line, the corollary of Lemma 3 says that pair is safe.

Now suppose the three directions are pairwise nonparallel. At most one of them is the axis, because `(0,1)` and `(0,-1)` are the same line.

- If at least two directions are diagonal, their pair is safe by Proposition 6(1).
- If none is diagonal, then each is horizontal or vertical. Any pair is then one of Proposition 6(2), 6(3), 6(4), or 6(5): a vertical partner of the axis is not diagonal, and a vertical non-axis direction has nonzero first coordinate.
- If exactly one is diagonal and there is no axis, the other two form a pair of type horizontal-horizontal, vertical-vertical, or horizontal-vertical, with no axis. That pair is safe by Proposition 6(2), 6(3), or 6(4).
- If exactly one is diagonal and one direction is the axis, the third direction is not diagonal. The axis-diagonal pair is safe by Proposition 6(6). The axis paired with the third direction is safe by Proposition 6(5).

`verify.py` enumerates the four direction types and checks that every triple with at most one axis falls under one of these bullets. That enumeration is a check of the case list, not a substitute for Proposition 6. ∎

**Theorem 8.** The profile `(1,0,1,1)/(1,1,1)` admits no word.

**Proof.** A word would give a decomposition of `H*` by (P1). Proposition 7 supplies a safe pair. One coordinate functional vanishes on that pair, so Lemma 1 supplies an AB or PQ form even on the pair, and Lemma 2 says that form detects two calls and four targets. Premise (P2) forbids it. ∎

Sections 2 through 7 are the argument. The two witnesses in Section 6 show that the character can come from a pair other than a pair that carries `(1,1)`. The finite boxes in `verify.py` corroborate Lemma 3 and the collapsed axis scales. They are not this theorem.

## 8. Transport to the named profile and to O5

Define three linear maps on a symmetric matrix with entries `(x,y,z)` by

```
s(x,y,z) = (x, -y, z),
t(x,y,z) = (z, y, x),
h(x,y,z) = ((x+2y+z)/2, (x-z)/2, (x-2y+z)/2).
```

These are the generators used by PR #7128. Each is an involution, fixes `I`, and preserves the determinant: `s` and `t` are congruences by monomial matrices of determinant `±1`, and `h(M) = W M W^T/2` with `W = [[1,1],[1,-1]]`, `det W = -2`, so the determinant is multiplied by `(det W)^2/4 = 1`. A nonzero symmetric matrix has rank one exactly when its determinant vanishes, and each map is bijective, so rank-one matrices are preserved. On labels,

```
s: P ↔ Q,   t: A ↔ B,   h: A ↔ P and B ↔ Q.
```

For a profile `π` and a generator `g`, define `(gπ)(gX) = π(X)`. Then `g` sends the residual of `π` to the residual of `gπ`, because `g` fixes `I` and permutes the old labels. In particular `t` exchanges `diag(2,3)` and `diag(3,2)`, and exchanges `(1,0,1,1)` and `(0,1,1,1)`.

**Lemma 9.** If `g` is a composite of `s`, `t`, and `h`, and `F` is a decomposition of `(π,(1,1,1))`, then `gF` is a decomposition of `(gπ,(1,1,1))` with the same character table. Thus `(π,(1,1,1))` is character-excluded exactly when `(gπ,(1,1,1))` is.

**Proof.** Each generator is a bijective linear map, fixes `I`, preserves rank one, and permutes the old labels, so a composite does as well. The frames of `gF` remain nonzero and rank one, and `g` sends the residual of `π` to the residual of `gπ`. A character `χ` of the source lattice pushes to `χ' = χ ∘ g^{-1}` on the image lattice. Then `χ'(gX) = χ(X)` for every old label and every frame, and the profile identity `(gπ)(gX) = π(X)` makes the detected call counts equal. The four targets are permuted. ∎

Applying the words `id`, `t`, `h`, and `sh` to `(1,0,1,1)` produces

```
(1,0,1,1),  (0,1,1,1),  (1,1,1,0),  (1,1,0,1).
```

Theorem 8 and Lemma 9 exclude all four. These are the four profiles of O5 in PR #7128. On `(1,1,0,1)` and `(1,1,1,0)` the AB form detects two old calls and the PQ form detects one; the transport carries the strict inequality without a second 2-adic analysis.

`verify.py` checks the label rules, the equality `t(diag(2,3)) = diag(3,2)`, the orbit, and the character table of `3P+3Q-A` after every word in the group generated by `s`, `t`, and `h`. That group has eight elements. The table check on one decomposition is a witness of Lemma 9, not the lemma.

## 9. What this does not prove

- It does not reprove premises (P1) and (P2).
- It does not settle O3 or O4. PR #7128 gives an explicit decomposition of each on which every character detects at least as many calls as targets.
- It does not treat four or more added frames.
- The witnesses and the coordinate boxes are not a classification of rational decompositions.
- No selected-frontier quantity moves. The selected κ stays `363005817/100000000000`.

## Open next questions

The two questions left open by PR #7128, and not used here, are the natural continuations.

1. Does every decomposition of `(2,1,1,0)/(1,1,1)` fail a character or fail target support? PR #7128 gives the character survivor `-B + (5/2)Q + (1/4)(1,3)(1,3)^T`. A useful first step is to describe the decompositions that pass every character, starting from the lattice `Z^3 + Z(1/2,1/2,1/2)` of that witness. The character test alone cannot close the orbit.
2. The same question for `(0,1,1,1)/(1,1,2)`, where the witness `(1/2)B + (1/2)(2,1)(2,1)^T + 2Q` passes every character and fails target support.

Four or more added frames are a different equation. They are not given a profile here.
