# One nullity-7 class has thin rank sum at least 8 over every field of characteristic 2

No new kappa. The selected frontier stays κ = 781451/250000000.

## Statement

On the g=3, d=2 paired-star full-call contract, full calls are the twelve F₂ orthogonal resolutions and each stage contributes exactly its two halves. A word is one of the 12³ × 720 orders. Two thin maps sit in two distinct gaps. Their matrices satisfy an F₂-linear system, so over any extension of F₂ the solution set is the scalar extension of an F₂-affine space.

Let the lexicographically first consistent gap pair of F₂-nullity 7 be the class below. Lex order is stage resolutions (c₀, c₁, c₂), then the heap order of the six-call permutation used by `research/paired-star-two-thin-rank/search.c`, then the gap pair. The parameters are resolutions 0, 0, 3, permutation index 4, and gaps 2 and 5. Resolution 0 has (A, B) bits (1, 0). Resolution 3 has (A, B) bits (1, 6). Chronological order, rightmost factor first, is calls 1, 2, 0, 3, 4, 5.

**Theorem.** Let F be any field of characteristic 2. Every point of this affine class, with coefficients in F, has rank(Zg) + rank(Zh) at least 8. In particular the class has no point of total rank 6 or 7 over F₈ = F₂[x]/(x³ + x + 1). The bound is attained by two F₂ points, of ranks (4, 4) and (6, 2).

The theorem is one affine class. It is not a statement about the other 1,745 classes, about F₈ points outside this scalar extension, or about three thin maps. A failed search is not the argument: the rank bound is the case analysis in the next sections. The F₈ enumeration in `search.c` and `verify.py` is an exhaustive finite check that the same minimum is 8 on all 8⁷ points, and that the two implementations agree.

## The matrices

Zh = Zg + D for the fixed rank-4 star D of the F₄ census, with rows `54 a8 01 02 01 02 01 02` in little-endian bits. The seven F₂ generators each add the same field coefficient to one entry of both matrices. Writing c₀, …, c₆ for those coefficients,

```text
Zg = c6  0  1  0  1  0  0  0
      0 c6  0  1  0  1  0  0
      1  0 c0  0  0  0  0  0
      0  1  0 c1 c2  0  0  0
      1  0  0 c3 c4  0  0  0
      0  1  0  0  0 c5  0  0
      0  0  0  0  0  0 c6  0
      0  0  0  0  0  0  0 c6

Zh = c6  0  0  0  0  0  1  0
      0 c6  0  0  0  0  0  1
      0  0 c0  0  0  0  0  0
      0  0  0 c1 c2  0  0  0
      0  0  0 c3 c4  0  0  0
      0  0  0  0  0 c5  0  0
      1  0  0  0  0  0 c6  0
      0  1  0  0  0  0  0 c6
```

Rows and columns are indexed from 0. The zero-coefficient point is an F₂ solution of the endpoint equations, and each generator is in the kernel, so every F-linear combination is a solution. The seven free coordinates are independent, so distinct coefficient tuples are distinct points. Over a finite field of order q there are exactly q⁷ points.

## Rank of Zh

The rows of Zh use disjoint sets of columns:

- rows {0, 1, 6, 7} use columns {0, 1, 6, 7};
- row 2 uses column 2;
- rows {3, 4} use columns {3, 4};
- row 5 uses column 5.

Rank therefore adds. The middle pieces contribute 1 when c₀ ≠ 0, the rank of

```text
M = c1 c2
    c3 c4
```

and 1 when c₅ ≠ 0. On the ordered basis (0, 1, 6, 7) the corner is

```text
A = c6 I    I
    I     c6 I
```

with I the 2×2 identity. For (x, y) in F² ⊕ F²,

```text
A(x, y) = (c6 x + y, x + c6 y).
```

A kernel vector satisfies y = c6 x and (1 + c6²) x = 0. In characteristic 2, 1 + c6² = (1 + c6)², so c6 ≠ 1 forces x = y = 0 and rank(A) = 4. If c6 = 1 then A(x, y) = (x + y, x + y), whose image has dimension 2, and rank(A) = 2.

Thus rank(Zh) = rank(A) + 1_{c₀ ≠ 0} + rank(M) + 1_{c₅ ≠ 0}, which is at least 4 when c6 ≠ 1 and at least 2 when c6 = 1.

## Rank of Zg

Columns 6 and 7 of Zg are zero except the diagonal entries c6, and rows 6 and 7 are zero on columns 0 through 5. If c6 ≠ 0 those two rows contribute 2, and

```text
rank(Zg) = rank(N) + 2,
```

where N is the leading 6×6 block. If c6 = 0 then rows 6 and 7 vanish and rank(Zg) = rank(N). The first two rows of N are

```text
(c6, 0, 1, 0, 1, 0),    (0, c6, 0, 1, 0, 1).
```

They are independent whenever c6 ≠ 0, so rank(N) ≥ 2 and rank(Zg) ≥ 4.

## The three cases

If c6 is neither 0 nor 1, then rank(Zh) ≥ 4 and rank(Zg) ≥ 4.

If c6 = 0, then rank(Zh) ≥ 4. The four rows

```text
(0, 0, 1, 0, 1, 0),
(0, 0, 0, 1, 0, 1),
(1, 0, c0, 0, 0, 0),
(0, 1, 0, c1, c2, 0)
```

of N have, on columns (0, 1, 2, 3), the minor

```text
0 0 1 0
0 0 0 1
1 0 c0 0
0 1 0 c1
```

Swap row 0 with row 2, then row 1 with row 3. The result is triangular with ones on the diagonal, so the minor equals 1 over any commutative ring. Those four rows are independent, rank(N) ≥ 4, and rank(Zg) ≥ 4.

If c6 = 1, then rank(Zg) = rank(N) + 2 and rank(Zh) = 2 + δ₀ + rank(M) + δ₅, where δ₀ = 1_{c₀ ≠ 0} and δ₅ = 1_{c₅ ≠ 0}. The first two rows of N are independent and pivot in columns 0 and 1. Clearing those columns from the other four rows leaves the vectors, in coordinates (2, 3, 4, 5),

```text
v2 = (1 + c0, 0, 1, 0),
v4 = (1, c3, 1 + c4, 0),
v3 = (0, 1 + c1, c2, 1),
v5 = (0, 1, 0, 1 + c5).
```

So rank(N) = 2 + rank(R) for R the span of these four vectors, and

```text
rank(Zg) + rank(Zh) = rank(R) + 6 + δ₀ + rank(M) + δ₅.
```

It is enough that rank(R) + δ₀ + rank(M) + δ₅ ≥ 2. Set a = 1 + c₀. If a ≠ 0, the first vector and v5's pivot (0, 1, 0, 1 + c₅), which has a 1 in the second coordinate, are two independent pivots after elimination, so rank(R) ≥ 2. If a = 0, then c₀ = 1, so δ₀ = 1, and the first vector is (0, 0, 1, 0) ≠ 0, so rank(R) ≥ 1. Either way the extra terms are at least 2.

Every value of c6 falls into one of the three cases. The sum is at least 8.

## Attainment

All seven coefficients zero gives rank 4 and rank 4. The single coefficient c6 = 1, with the others zero, gives rank 6 and rank 2. Both points have entries in F₂. The F₈ census below finds no other point of sum 8, and none of sum less than 8.

## What was enumerated

F₈ has 8⁷ = 2,097,152 points in this class. Both the C enumerator and the independent Python enumerator report minimum rank sum 8, with 2 points at sum 8 and none below. The same loop over the 4⁷ F₄ points also has minimum 8. That finite census is not the proof for an arbitrary characteristic-2 field. It checks the displayed matrices, including the block formula for rank(Zh), on one finite field.

Deleting the constant ones in Zg drops the zero-coefficient point to rank sum 4. Those ones are part of the solved class; the deleted matrix is only a failure control.

## What this does not decide

The other affine classes on this contract, including every class the F₄ census left unresolved, are untouched. So are F₁₆ and larger fields outside this one scalar extension, three or more thin maps, and a stage with three or more full calls. No point found here changes κ.
