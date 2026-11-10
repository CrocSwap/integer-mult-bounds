# Four once-each rank-one frames do not meet the four-call endpoint

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, the shortest determinant equation that uses four new labels once each is

```
R + S + T + U = 4I.
```

It is the zero-old-call case: four paid calls and no call on `A`, `B`, `P`, or `Q`. Two statements are proved about it.

1. **Support proof.** No choice of four nonzero symmetric rational rank-one matrices satisfies target support for this equation. The equation therefore admits no word. This does not lower the eight-call minimum, and it does not speak about five, six, or seven calls.
2. **Parity-image witness, not a census.** The same equation has an explicit rational solution whose integral span has full parity image `F2^2`. The three-frame route, "the image misses `(1,1)`, so an AB or PQ form kills every added frame," does not apply to every four-frame solution. That witness is still character-excluded by a direct count, and it is not a word.

Selected κ stays `781451/250000000`. Nothing here is a multiplication theorem, a search failure presented as nonexistence, or a statement about five or more added frames.

The determinant identity `sum of paid addresses = 4I` and the necessary condition "each target exponent is a subset sum of the paid labels" are inherited from the normalization recorded in `research/bit-two-signed-frame-floor/PROOF.md`, Section 1 (itself from PR2910 and PR6190). This file does not reprove them.

## 1. Setup

Addresses are rational symmetric 2-by-2 matrices. Write

```
A = diag(1,0),  B = diag(0,1),
P = [[1,1],[1,1]]/2,  Q = [[1,-1],[-1,1]]/2.
```

A coefficient vector `(a,b,c)` means `aA + bB + cP`, with matrix

```
[[a + c/2, c/2], [c/2, b + c/2]],
```

trace `a+b+c`, and determinant `ab + c(a+b)/2`. The matrix is nonzero and rank one exactly when the vector is nonzero and the determinant is zero.

The four targets and their coefficient vectors are

```
A+P = (1,0,1),   A+Q = (2,1,-1),
B+P = (0,1,1),   B+Q = (1,2,-1).
```

Each has trace 2 and determinant `1/2`. Their sum is `2A+2B+2P+2Q = 4I`, with coefficient vector `(4,4,0)`.

For a primitive integer direction `u = (u1,u2)` and a nonzero rational scale `s`,

```
s uu^T = s (u1(u1-u2), u2(u2-u1), 2 u1 u2).
```

Every nonzero symmetric rational rank-one matrix has this form. The parity image of an integral coefficient vector is

```
φ(a,b,c) = ((a+b) mod 2, c mod 2) in F2^2.
```

## 2. Only pairs can carry a target

**Lemma 1.** Let `F1,F2,F3,F4` be nonzero symmetric rational rank-one matrices with sum `4I`. A subset sum equal to a target has size exactly 2.

**Proof.** The empty sum is 0. A singleton has determinant 0, while each target has determinant `1/2`. The full sum is `4I`, with trace 8, while each target has trace 2. A three-element subset sums to a target `H` only if the omitted frame equals `4I-H`. For every target,

```
det(4I-H) = 16 - 4·tr(H) + det(H) = 16 - 8 + 1/2 = 17/2 ≠ 0,
```

so `4I-H` is not rank one. The only remaining subsets are the pairs.

## 3. The fifteen pair patterns

There are six unordered pairs among four calls and `C(6,4) = 15` ways to choose four of them. Each target would have to be a different pair, because the four targets are distinct. `verify.py` enumerates all 15 graphs. Their sorted degree sequences are only

```
(2,2,2,2)  three times,  and  (3,2,2,1)  twelve times.
```

That enumeration is exhaustive for the pair patterns. It is not a search over directions or scales.

**Theorem 2.** No four nonzero symmetric rational rank-one matrices summing to `4I` have all four targets as subset sums.

**Proof.** By Lemma 1 every target is a pair sum, so some four-edge graph as above has its four edge sums equal to the four targets. The sum of those edge sums is therefore `4I`.

If every degree is 2, the edge sum is twice the sum of the four frames, hence `2·4I = 8I`. Then `8I = 4I`, which is false.

If the degrees are 3, 2, 2, and 1, label the degree-3 call `F` and the unique edge disjoint from `F` by `X+Y`. The fourth call is `Z`. The edge sum is

```
3F + 2X + 2Y + Z.
```

Subtracting the total sum `F+X+Y+Z = 4I` gives the matrix identity

```
2F + X + Y = 0.
```

The edge `X+Y` equals some target `H`, so `F = -H/2`. Then

```
det(F) = det(-H/2) = (1/4)·det(H) = 1/8 ≠ 0,
```

so `F` is not rank one.

Both patterns contradict the rank-one hypothesis. Therefore target support fails for every solution of the equation, and the equation admits no word.

The direct eight-call word, two old labels on each target, is untouched. Theorem 2 removes only the four-call equation.

## 4. A full parity image

**Witness.** The directions and scales

```
(0,1) at -3,   (1,-1) at 5/2,   (1,1) at 1/2,   (1,2) at 1
```

give the integral frames

```
R = (0,-3,0),  S = (5,5,-5),  T = (0,0,1),  U = (-1,2,4).
```

Their sum is `(4,4,0)`. Each determinant is 0 and each vector is nonzero, so each frame is rank one. The integer combinations

```
R = (0,-3,0),   S = (5,5,-5),   S+U = (4,7,-1)
```

have parity images `(1,0)`, `(0,1)`, and `(1,1)`. The zero combination has image `(0,0)`. The parity image of the integral span is all of `F2^2`.

In particular neither coordinate functional vanishes on that span. No integer form of shape `(odd,odd,even)` or `(even,even,odd)` is even on all four frames: the first shape reduces to `a+b` modulo 2, and `R` has `a+b` odd; the second reduces to `c` modulo 2, and `S` has `c` odd. The three-frame extension, which needs one of those shapes to kill every added frame, does not apply to this solution.

This is one explicit solution. It is not an enumeration of all four-direction solutions, and a full parity image is not a word.

## 5. The witness still fails a direct character count

The same witness is excluded by the inherited call-versus-target inequality, without killing every frame. Reduce the coefficient of `P` modulo 2. All four targets have odd `P`-coefficient, so all four are detected. Among the frames, only `S` and `T` have odd `P`-coefficient, so two calls are detected. Two calls against four targets is forbidden.

Theorem 2 already excludes the witness as a word. Section 5 records that evading the vanishing test is not the same as surviving every first-order character. The witness also fails support, as Theorem 2 requires: none of its fifteen nonempty subset sums equals a target. That fifteen-line check is a check of one solution, not the proof.

## Open next questions

Lengths 5, 6, and 7 with four added labels, and every decomposition with five or more added frames, are untouched. One extra old call changes both the residual and the allowed subset sizes, so Theorem 2 does not apply. A solution whose parity image is full can still fail a character that detects only some of the new frames.
