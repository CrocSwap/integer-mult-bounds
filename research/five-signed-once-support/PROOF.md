# Five once-each rank-one frames do not meet the five-call endpoint

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Claim

In the PR2085/2112 formal register model, the shortest determinant equation that uses five new labels once each is

```
R + S + T + U + V = 4I.
```

It is the zero-old-call case: five paid calls and no call on `A`, `B`, `P`, or `Q`. Two statements are made about it.

1. **Exhaustive finite census of target support.** No five nonzero symmetric rational rank-one matrices summing to `4I` have all four targets as subset sums. The equation therefore admits no word. The domain is finite because a target-carrying subset has size 2 or 3, and every ordered 4-tuple of such subsets is solved exactly. This is a proof of that scoped support statement by complete case analysis. It is not a heuristic search, and it is not a hand classification into two degree patterns of the kind used for four calls.
2. **Parity-image witness, not a census.** The same sum, without the support requirement, has an explicit solution in five pairwise nonparallel primitive directions whose integral span has full parity image `F2^2`. The three-frame route does not apply to every five-frame solution. That witness is still not a word: the census already excludes it, and a direct character count on this one solution detects two calls and four targets.

Selected κ stays `781451/250000000`. Nothing here is a multiplication theorem, a statement about six or more added frames, or a statement about five added frames together with an old call. The census does not lower the eight-call minimum. It removes only this five-call equation.

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

trace `a+b+c`, and determinant `ab + c(a+b)/2`. The matrix is nonzero and rank one exactly when the vector is nonzero and the determinant is zero. Equivalently, the integer polynomial `2ab + c(a+b)` is zero.

The four targets and their coefficient vectors are

```
A+P = (1,0,1),   A+Q = (2,1,-1),
B+P = (0,1,1),   B+Q = (1,2,-1).
```

Each has trace 2 and determinant `1/2`. Their sum is `2A+2B+2P+2Q = 4I`, with coefficient vector `(4,4,0)` and determinant 16.

For a primitive integer direction `u = (u1,u2)` and a nonzero rational scale `s`,

```
s uu^T = s (u1(u1-u2), u2(u2-u1), 2 u1 u2).
```

Every nonzero symmetric rational rank-one matrix has this form. The parity image of an integral coefficient vector is

```
φ(a,b,c) = ((a+b) mod 2, c mod 2) in F2^2.
```

## 2. Only pairs and triples can carry a target

**Lemma 1.** Let `F1,...,F5` be nonzero symmetric rational rank-one matrices with sum `4I`. A subset sum equal to a target has size 2 or 3.

**Proof.** The empty sum is 0. A singleton has determinant 0, while each target has determinant `1/2`. The full sum is `4I`, with trace 8, while each target has trace 2. A four-element subset sums to a target `H` only if the omitted frame equals `4I-H`. For every target the matrix expansion gives

```
det(4I-H) = 16 - 4·tr(H) + det(H) = 16 - 8 + 1/2 = 17/2 ≠ 0,
```

and the coefficient formula for `(4-a,4-b,-c)` gives the same value. So `4I-H` is not rank one. The only remaining subset sizes are 2 and 3.

The four targets are distinct, so the four subsets are distinct. There are `C(5,2)+C(5,3) = 20` candidate subsets and `C(20,4)·4! = 116280` ordered 4-tuples. That list is the whole domain. It is not a sample of directions or scales.

## 3. The incidence system

Label the five frames by columns. For an ordered 4-tuple of subsets, let `M` be the 5-by-5 integer matrix whose first four rows are the subset indicators and whose last row is `(1,1,1,1,1)`. Target support and the sum `4I` are the three integer systems

```
M f_a = r_a,  M f_b = r_b,  M f_c = r_c,
```

where the right-hand sides are the corresponding coordinates of the four targets followed by `4`, `4`, or `0`. Any rational solution of the matrix equation is a candidate. It is a rank-one solution only if every column frame is nonzero and lies on the determinant cone.

`verify.py` decides every tuple by the Leibniz determinant of `M`, which is an integer. The sign convention is anchored by `det I_5 = 1` and by one 5-by-5 determinant computed by hand in Section 4.

- If `det M ≠ 0`, Cramer's rule supplies the unique rational solution. The program checks the matrix residual `M n = (det M) r` on every coordinate and rejects the tuple unless some frame is zero or off the cone.
- If `det M = 0`, exact rational row reduction is run twice, once with columns left to right and once right to left. An inconsistent augmented matrix removes the tuple. A consistent system of rank other than 4, or a rank-4 kernel with no zero coordinate, would be left unresolved and the program would fail. Neither occurs. Every remaining system has rank 4 and a kernel coordinate equal to zero, so the corresponding frame is constant on the whole affine line. That constant frame is off the cone, and the two elimination orders agree on its value.

The cone test uses the integer numerator `2ab+c(a+b)`. A zero numerator with a nonzero vector would have been reported as a hit. There is no hit.

## 4. A worked invertible tuple

Take the subsets of column indices

```
{0,1}, {0,2}, {1,2}, {0,3},
```

with indicators `(1,1,0,0,0)`, `(1,0,1,0,0)`, `(0,1,1,0,0)`, and `(1,0,0,1,0)`. Row reduction of the incidence matrix, subtracting the first row from the later rows that begin with 1 and then expanding, gives determinant `-2`. The same value is what the Leibniz routine returns. Cramer's rule produces the unique frames

```
(3/2, 0, -1/2),  (-1/2, 0, 3/2),  (1/2, 1, -1/2),
(-1/2, 2, -1/2),  (3, 1, 0).
```

Their integer numerators `2ab+c(a+b)`, cleared of the common denominator, are nonzero. This tuple is one invertible case. It is not a substitute for the census.

## 5. A worked rank-4 tuple

Take the subsets

```
{0,1}, {0,2}, {1,3}, {2,3}.
```

Adding the first subset equation to the fourth, and the second to the third, gives the same relation

```
F0+F1+F2+F3 = (A+P)+(B+Q) = 2I = (2,2,0),
```

because both pairings of targets sum to `2I`. The total-sum equation then freezes the omitted frame:

```
F4 = 4I - 2I = 2I = (2,2,0).
```

The determinant of `2I` is 4, so `F4` is not rank one. The kernel may still move `F0,F1,F2,F3`. It cannot move `F4`, and one non-rank-one frame excludes the whole line. One point on the line is

```
(2,1,-1),  (-1,-1,2),  (0,0,0),  (1,2,-1),  (2,2,0).
```

Direct addition checks the four subset equations and the total sum. The zero third frame is an artifact of this parameter value, not a second frozen frame. The program records the frozen value `2I` for the tuple.

## 6. Census

The program classifies all 116280 tuples.

| Class | Count | Rank-one support |
|---|---:|---|
| Invertible, unique rational solution off the cone | 71040 | none |
| Inconsistent augmented matrix | 44520 | none |
| Consistent rank 4, one frame frozen off the cone | 720 | none |

The 720 frozen frames take only the six values

```
±2I = ±(2,2,0),   ±(A-B) = ±(1,-1,0),   ±(P-Q) = ±(1,1,-2),
```

each for 120 tuples. Their determinants are `4` or `-1`. No consistent system of rank below 4 occurs, and no rank-4 kernel lacks a zero coordinate. Those are checked assertions, not omitted branches.

Therefore no rational rank-one solution has target support. By the inherited subset-sum necessity, the equation admits no word. The direct eight-call word, two old labels on each target, is untouched.

## 7. A full parity image

**Witness.** The directions and scales

```
(-1,1) at 1,  (0,1) at -1,  (1,0) at 3,  (1,1) at -1/2,  (1,3) at 1/2
```

give the integral frames

```
(2,2,-2),  (0,-1,0),  (3,0,0),  (0,0,-1),  (-1,3,3).
```

Their sum is `(4,4,0)`. Each determinant is 0 and each vector is nonzero. The five directions are pairwise nonparallel. The integer combinations

```
(0,-1,0),  (0,0,-1),  (0,-1,-1)
```

have parity images `(1,0)`, `(0,1)`, and `(1,1)`. The parity image of the integral span is all of `F2^2`.

No integer form of shape `(odd,odd,even)` or `(even,even,odd)` is even on all five frames. The three-frame extension, which needs one of those shapes to kill every added frame, does not apply to this solution.

This is one explicit solution of the sum. It is not an enumeration of all five-direction solutions. A full parity image is not a word, and Section 6 already excludes this witness as a support solution: none of its 31 nonempty subset sums equals a target.

## 8. The witness still fails a direct character count

Reduce the coefficient of `P` modulo 2. All four targets have odd `P`-coefficient. Among the five frames, only `(0,0,-1)` and `(-1,3,3)` have odd `P`-coefficient, so two calls are detected. Two calls against four targets is forbidden by the inherited inequality. The inequality is not reproved here. Section 8 records that evading the vanishing test is not the same as surviving every first-order character, for this one solution. It is not a character theorem for every five-frame solution of the sum.

## Open next questions

Six once-each added frames, and every five-frame equation whose residual is not `4I`, are untouched. One extra old call changes both the residual and the allowed subset sizes, so Lemma 1 does not apply. A solution whose parity image is full can still fail a character that detects only some of the new frames.
