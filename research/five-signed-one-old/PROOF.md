# Five frames plus one old projector meet support only by splitting 2I

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, fix one old projector `E` in `{A,B,P,Q}` and five nonzero symmetric rational rank-one matrices. For the once-each equation

```
R + S + T + U + V = 4I - E
```

target support holds if and only if, up to order, three of the five matrices are the three old projectors other than `E` and the other two are a rational rank-one splitting of `2I`.

Every integral solution of that form fails the inherited `P`-coefficient character: exactly two of the six labels have odd `P`-coefficient, and all four targets do. Those solutions are not words. A non-integral splitting is a support solution and is not, by itself, a word.

Selected κ stays `781451/250000000`. Nothing here is a multiplication theorem, a κ change, or a lowering of the eight-call minimum. Six added frames with no old call, four added frames plus an old call, and two or more old calls stay outside this equation.

The determinant identity `sum of paid addresses = 4I` and the necessary condition "each target exponent is a subset sum of the paid labels" are inherited from `research/bit-two-signed-frame-floor/PROOF.md`, Section 1. The character inequality in that same section is inherited and is not reproved. This file does not reprove them.

## 1. Setup

Addresses are rational symmetric 2-by-2 matrices. Write

```
A = diag(1,0),  B = diag(0,1),
P = [[1,1],[1,1]]/2,  Q = [[1,-1],[-1,1]]/2.
```

A coefficient vector `(a,b,c)` means `aA + bB + cP`. The matrix is nonzero and rank one exactly when the vector is nonzero and `2ab + c(a+b) = 0`. The old projectors are

```
A = (1,0,0),  B = (0,1,0),  P = (0,0,1),  Q = (1,1,-1).
```

Each has trace 1. Opposite pairs sum to `I = (1,1,0)`:

```
A + B = P + Q = I,    A + B + P + Q = 2I = (2,2,0).
```

The four targets are

```
A+P = (1,0,1),  A+Q = (2,1,-1),  B+P = (0,1,1),  B+Q = (1,2,-1).
```

Each has trace 2 and determinant `1/2`. Their sum is `4I = (4,4,0)`. For `E` as above, `4I-E` has trace 7. Write `E⊥` for the opposite of `E` and `{G,G⊥}` for the other opposite pair. The three projectors other than `E` are exactly `{E⊥,G,G⊥}`, and they sum to `2I-E`.

## 2. Which subset sizes can be targets

The six paid labels are the five frames and `E`. They sum to `4I`.

**Lemma 1.** A subset sum equal to a target has size 2, 3, or 4.

The empty sum is 0. A singleton has determinant 0, while each target has determinant `1/2`. The full sum has trace 8, while each target has trace 2. A five-element subset sums to a target `H` only if the omitted label equals `4I-H`. The same expansion used for five frames with no old call gives

```
det(4I-H) = 16 - 4·tr(H) + det(H) = 17/2 ≠ 0,
```

so `4I-H` is not rank one. The only remaining sizes are 2, 3, and 4.

There are `C(6,2)+C(6,3)+C(6,4) = 50` such subsets. The four targets are distinct, so the four subsets are distinct. The support domain is the `C(50,4) = 230300` unordered 4-tuples, each with `4! = 24` assignments of the targets and with each of the four choices of `E`. That list is the whole domain left by Lemma 1. It is not a sample of directions or scales.

## 3. The construction

**Theorem 2.** Let `X` and `2I-X` both be nonzero and rank one. For each projector `E`, the five matrices `{E⊥, G, G⊥, X, 2I-X}` sum to `4I-E`, and the four subsets

```
{E⊥,G},  {E⊥,G⊥},  {E,G},  {E,G⊥}
```

are the four targets in some order.

The three complementary projectors sum to `2I-E`, so the five matrices sum to `4I-E`. The four displayed pairs are subset sums of the six labels, and direct addition shows they are the four targets:

| `E` | Frozen frames | The four pair sums |
|---|---|---|
| `A` | `B,P,Q` | `B+P, B+Q, A+P, A+Q` |
| `B` | `A,P,Q` | `A+P, A+Q, B+P, B+Q` |
| `P` | `A,B,Q` | `A+Q, B+Q, A+P, B+P` |
| `Q` | `A,B,P` | `A+P, B+P, A+Q, B+Q` |

The pairs `A+B` and `P+Q` equal `I`, which is not a target, and they are not used. The two summands of `2I` do not appear in these subsets, so every splitting works. In particular `2I-E` itself is not rank one for any projector `E`, so neither free frame is `E`.

One integral solution for `E=B` is

```
A, P, Q, 2A, 2B.
```

One pairwise nonparallel solution, still for `E=B`, uses the splitting in Section 4 at `t=2`:

```
A, P, Q, (-2/5, 4/5, 8/5), (12/5, 6/5, -8/5).
```

The directions are `(1,0)`, `(1,1)`, `(1,-1)`, `(1,2)`, and `(2,-1)`, at scales `1`, `1/2`, `1/2`, `2/5`, and `2/5`. No two are parallel. Both solutions meet support. Neither is claimed to be a word.

## 4. Every splitting of 2I

**Lemma 3.** For a symmetric matrix `X=(a,b,c)`,

```
Q(2I-X) - Q(X) = 4(2 - a - b - c),
```

where `Q=2ab+c(a+b)`. Thus `X` and `2I-X` are both rank one if and only if `X` is nonzero and rank one and has trace 2. The partner is then automatically nonzero, because `2I` is not rank one.

The identity is the polynomial expansion checked by `verify.py`. If both quadrics vanish, the trace equals 2. Conversely, trace 2 and `Q(X)=0` force `Q(2I-X)=0`.

On the trace-2 slice, `b=2-c-a` and `Q(X)=0` become a quadratic in `a` whose discriminant is `4-c^2`. For an integer vector, `c` is an integer. If `|c|≥3`, then `c^2≥9>4`, so the discriminant is negative. Inside `-2≤c≤2` the discriminant is a square only for `c=0,±2`, and the only nonzero rank-one solutions are

```
2A=(2,0,0),  2B=(0,2,0),  2P=(0,0,2),  2Q=(2,2,-2).
```

They form the two pairs `{2A,2B}` and `{2P,2Q}`. Every coordinate `c` in these four vectors is even.

For every rational `t`, 

```
X(t) = ( 2(1-t)/(1+t^2),  2t(t-1)/(1+t^2),  4t/(1+t^2) )
```

has trace 2 and lies on the cone, and `X(0)=2A`, `X(1)=2P`. The partner of `2B` is `2A`, which is the missing point of this chart. The verifier checks the formula at `t=0,1,2,3,1/2,5`. These are infinitely many distinct splittings; the trace-2 cone is the full set.

## 5. Integral solutions are not words

**Theorem 4.** Every integral support solution of the equation fails the inherited `P`-coefficient test, so it is not a word.

By Theorem 5 below, an integral support solution has the multiset in Theorem 2 with an integral splitting. Section 4 lists those splittings, and both frames have even `c`. The six labels are the four projectors together with that pair. Among `A,B,P,Q`, only `P` and `Q` have odd `c`. Exactly two calls are detected. All four targets have odd `c`. The inherited inequality forbids a word. The addresses lie in the old lattice `ZA+ZB+ZP`, so the character is the ordinary `P`-coefficient modulo 2. The inequality itself is not reproved.

The same count does not apply to a non-integral splitting. Section 4's `t=2` witness has denominator 5. It meets support and is not claimed to survive, or to fail, every character.

## 6. No other support solution exists

**Theorem 5.** Every rational rank-one solution with target support is one of the solutions in Theorem 2.

The proof is the case division of the domain in Section 2. `verify.py` decides every tuple. The hand arguments are the twin obstruction and the trace obstruction. The other branches are finite and are exhausted by the program.

### Duplicate frame rows

Two distinct subsets can impose the same row on the five unknown frames only when one is `S` and the other is `S∪{E}`. Their equations say `E=H2-H1` for two distinct targets. The twelve differences are

```
A+Q-(A+P) = (1,1,-2),     A+P-(A+Q) = (-1,-1,2),
B+P-(A+P) = (-1,1,0),     A+P-(B+P) = (1,-1,0),
B+Q-(A+P) = (0,2,-2),     A+P-(B+Q) = (0,-2,2),
B+Q-(A+Q) = (-1,1,0),     A+Q-(B+Q) = (1,-1,0),
B+P-(A+Q) = (-2,0,2),     A+Q-(B+P) = (2,0,-2),
B+Q-(B+P) = (1,1,-2),     B+P-(B+Q) = (-1,-1,2).
```

None equals `A=(1,0,0)`, `B=(0,1,0)`, `P=(0,0,1)`, or `Q=(1,1,-1)`. There are 22370 such 4-tuples. Each is inconsistent for every projector and every target assignment.

### Rank 3

A matrix with all 4-by-4 minors zero has rank at most 3. Every one of the 2450 such matrices has rank exactly 3. Its left kernel is two-dimensional, and both kernel vectors annihilate the rows. For every projector and every target assignment, one of those vectors misses the right-hand side. No rank-3 system is consistent. No rank below 3 occurs.

### Rank 4 with no frozen frame

The remaining singular matrices have rank 4, so the adjugate has rank 1 and supplies the left and right kernels. On 3840 matrices the right kernel has no zero coordinate. Every primitive left kernel has the shape with two `+1` entries among the four subset rows, zeroes elsewhere there, and `-1` on the total row. The six shapes and their counts are

| Left kernel | Count |
|---|---:|
| `(1,0,0,1,-1)` | 800 |
| `(0,1,0,1,-1)` | 640 |
| `(0,1,1,0,-1)` | 640 |
| `(1,0,1,0,-1)` | 640 |
| `(0,0,1,1,-1)` | 560 |
| `(1,1,0,0,-1)` | 560 |

Thus two subset rows sum to the total row. The corresponding right-hand sides would satisfy

```
(H_p - ε_p E) + (H_q - ε_q E) = 4I - E,
```

where each `ε` is 0 or 1. The left trace is `4-(ε_p+ε_q)`, hence 2, 3, or 4. The right trace is 7. The system is inconsistent for every projector and every target assignment.

### One frozen frame

On 27840 matrices the right kernel has exactly one zero. That frame is constant on the solution line. Of the systems that are consistent, 16320 freeze a frame that is zero or off the cone, so the whole line fails. The other 960 freeze a rank-one frame. For those, if one moving frame `X` lies on the cone, each of the other three moving frames lies on the cone only if a fixed linear form in `X` vanishes. The verifier solves those three linear forms. None of the 960 systems has a rank-one solution.

### Three frozen frames

On 53400 matrices the right kernel has exactly three zeroes. The two nonzero kernel coefficients sum to zero, so the sum of the two moving frames is constant on each solution space. Of the consistent systems, 28560 freeze a frame off the cone. The other 240, sixty for each projector `E`, freeze exactly the three complementary projectors, and the moving sum is `2I`. Substituting `2A` and `2B` satisfies every equation of each of these 240 systems. Because the moving sum is invariant, every rank-one point of each system is a splitting of `2I`. The 240 systems are in bijection with the ways to place those three projectors into five positions, `4·P(5,3)=240`.

### Invertible systems

The other 120400 matrices are invertible. Cramer's rule, with the cofactor matrix checked against `M·adj(M)=det(M)I` on every one of them, produces a unique rational solution for each of the `120400·24·4 = 11558400` right-hand sides. Every solution has a zero frame or a frame off the cone.

One of those matrices is the incidence matrix of subsets `{0,1}`, `{0,2}`, `{1,2}`, `{0,3}`, with no `E` bit. Its determinant is `-2`, by the same integer row reduction already recorded for this matrix in the five-call note, and again by the cofactor routine here. For `E=A` and the targets in the order `A+P,A+Q,B+P,B+Q`, the unique frames are

```
(3/2, 0, -1/2),  (-1/2, 0, 3/2),  (1/2, 1, -1/2),
(-1/2, 2, -1/2),  (2, 1, 0).
```

Their quadrics are `-3/4`, `-3/4`, `1/4`, `-11/4`, and `4`. This is one invertible case, not a substitute for the census. The same solver recovers the `t=2` witness from the subset sums of these four masks, and it stops recovering that witness if the total row is shifted by `A`.

## 7. What was not proved

The census is exhaustive for this one equation. It is not a search over a bounded box of directions. A support solution is not a legal word: the factors still have to multiply to the target in the group algebra. Theorem 4 excludes only the integral solutions. Discussion #2091 and the fixed fifth address `R=(1,1/2)` are a different alphabet; this note does not revisit that word search and does not contradict its eight-call conclusion, because no word is exhibited here.

## Open next questions

Can one rational splitting of `2I` make the length-6 support solution into a word? A word would lower the eight-call minimum. The integral pairs `{2A,2B}` and `{2P,2Q}` already fail the `P`-coefficient test. The first unchecked point on the same chart is `t=2`, whose frames are displayed in Section 3. Passing that character would still not be a word: support and the first-order count are necessary, not sufficient.
