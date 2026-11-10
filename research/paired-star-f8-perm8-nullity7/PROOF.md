# The next nullity-7 class has thin rank sum at least 8

No new kappa. The selected frontier stays κ = 781451/250000000.

## Statement

On the g=3, d=2 paired-star full-call contract, full calls are the twelve F₂ orthogonal resolutions and each stage contributes exactly its two halves. A word is one of the 12³ × 720 orders. Two thin maps sit in two distinct gaps. Their matrices satisfy an F₂-linear system, so over any extension of F₂ the solution set is the scalar extension of an F₂-affine space.

Lex order is stage resolutions (c₀, c₁, c₂), then the heap order of the six-call permutation used by `research/paired-star-two-thin-rank/search.c`, then the gap pair. The lexicographically first consistent gap pair of F₂-nullity 7 is resolutions (0, 0, 3), permutation index 4, and gaps 2 and 5. That class is the one settled by the open argument in PR #7028, which records F₈ checksum 6631801623909619557.

The next nullity-7 system in the same order is permutation index 5, calls 2, 1, 0, 3, 4, 5, with the same gaps. Its reduced basis is identical, so it is the same affine class. The next system with a different reduced basis is the class below.

**Class.** Resolutions (0, 0, 3), permutation index 8, and gaps 2 and 5. Resolution 0 has (A, B) bits (1, 0). Resolution 3 has (A, B) bits (1, 6). Chronological order, rightmost factor first, is calls 0, 3, 1, 2, 4, 5. Nullity is 7. This is not the settled class: the permutation index is 8 rather than 4, the call order is 0, 3, 1, 2, 4, 5 rather than 1, 2, 0, 3, 4, 5, and the free support below is different. The settled support matcher returns false on this basis.

**Theorem.** Let F be any field of characteristic 2. Every point of this affine class, with coefficients in F, has rank(Zg) + rank(Zh) at least 8. In particular the class has no point of total rank 6 or 7 over F₈ = F₂[x]/(x³ + x + 1). The bound is attained by two F₂ points, of ranks (4, 4) and (6, 2).

The theorem is one affine class. It is not a statement about the other affine classes, about three thin maps, or about a stage with three or more full calls. The rank bound is the case analysis below. The F₈ enumeration is an exhaustive finite check that the same minimum is 8 on all 8⁷ points, and that the two implementations agree. A failed search is not the argument.

## The matrices

Zh = Zg + D for the fixed rank-4 star D, with rows `54 a8 01 02 01 02 01 02` in little-endian bits. The same relation holds for the settled class. The supports of the seven generators do not. Writing c₀, …, c₆ for the coefficients of this class,

```text
Zg = c6  0  1  0  1  0  0  0
      0 c6  0  1  0  1  0  0
      1  0 c0  0  0 c1  0  0
      0  1  0 c2  0  0  0  0
      1  0  0  0 c3  0  0  0
      0  1 c4  0  0 c5  0  0
      0  0  0  0  0  0 c6  0
      0  0  0  0  0  0  0 c6

Zh = c6  0  0  0  0  0  1  0
      0 c6  0  0  0  0  0  1
      0  0 c0  0  0 c1  0  0
      0  0  0 c2  0  0  0  0
      0  0  0  0 c3  0  0  0
      0  0 c4  0  0 c5  0  0
      1  0  0  0  0  0 c6  0
      0  1  0  0  0  0  0 c6
```

Rows and columns are indexed from 0. The zero-coefficient point is an F₂ solution of the endpoint equations, and each generator is in the kernel, so every F-linear combination is a solution. The seven masks are independent over F₂: c₀, c₁, c₂, c₃, c₄, c₅, and c₆ each have a private coordinate, namely (2,2), (2,5), (3,3), (4,4), (5,2), (5,5), and (0,0). Distinct coefficient tuples are distinct points. Over a finite field of order q there are exactly q⁷ points.

The settled class uses a 2×2 block on rows {3, 4} and columns {3, 4}, with c₅ alone at (5,5). This class does not. Rows 2 and 5 share columns {2, 5}, and rows 3 and 4 are separate diagonal entries. The column partition of PR #7028 does not describe these rows.

## Rank of Zh

The rows of Zh use disjoint sets of columns:

- rows {0, 1, 6, 7} use columns {0, 1, 6, 7};
- rows {2, 5} use columns {2, 5};
- row 3 uses column 3;
- row 4 uses column 4.

Rank therefore adds. The singleton rows contribute 1 when c₂ ≠ 0 and 1 when c₃ ≠ 0. Rows {2, 5} contribute the rank of

```text
M = c0 c1
    c4 c5
```

On the ordered basis (0, 1, 6, 7) the corner is

```text
A = c6 I    I
    I     c6 I
```

with I the 2×2 identity. The same block appears in the settled class. For (x, y) in F² ⊕ F²,

```text
A(x, y) = (c6 x + y, x + c6 y).
```

A kernel vector satisfies y = c6 x and (1 + c6²) x = 0. In characteristic 2, 1 + c6² = (1 + c6)², so c6 ≠ 1 forces x = y = 0 and rank(A) = 4. If c6 = 1 then A(x, y) = (x + y, x + y), whose image has dimension 2, and rank(A) = 2.

Thus rank(Zh) = rank(A) + rank(M) + 1_{c₂ ≠ 0} + 1_{c₃ ≠ 0}, which is at least 4 when c6 ≠ 1 and at least 2 when c6 = 1.

## Rank of Zg

Columns 6 and 7 of Zg are zero except the diagonal entries c6, and rows 6 and 7 are zero on columns 0 through 5. If c6 ≠ 0 those two rows contribute 2, and rank(Zg) = rank(N) + 2, where N is the leading 6×6 block. The first two rows of N have, on columns (2, 3), the identity

```text
1 0
0 1
```

so they are independent for every value of c6. If c6 ≠ 0, then rank(N) ≥ 2 and rank(Zg) ≥ 4.

## The three cases

If c6 is neither 0 nor 1, then rank(Zh) ≥ 4 and rank(Zg) ≥ 4.

If c6 = 0, then rank(Zh) ≥ 4. The four rows

```text
(0, 0, 1, 0, 1, 0),
(0, 0, 0, 1, 0, 1),
(1, 0, c0, 0, 0, c1),
(0, 1, 0, c2, 0, 0)
```

of N have, on columns (0, 1, 2, 3), the minor

```text
0 0 1 0
0 0 0 1
1 0 c0 0
0 1 0 c2
```

The entry c1 lies in column 5, so it does not meet this minor. Swap row 0 with row 2, then row 1 with row 3. The result is triangular with ones on the diagonal, so the minor equals 1 over any commutative ring. Those four rows are independent, rank(N) ≥ 4, and rank(Zg) ≥ 4.

If c6 = 1, then rank(Zg) = rank(N) + 2 and rank(Zh) ≥ 2. The first two rows of N are (1, 0, 1, 0, 1, 0) and (0, 1, 0, 1, 0, 1). They pivot in columns 0 and 1. Clearing those columns from the other four rows leaves, in coordinates (2, 3, 4, 5),

```text
v2 = (1 + c0, 0, 1, c1),
v3 = (0, 1 + c2, 0, 1),
v4 = (1, 0, 1 + c3, 0),
v5 = (c4, 1, 0, 1 + c5).
```

So rank(N) = 2 + rank(R) for R the span of these four vectors, and

```text
rank(Zg) + rank(Zh) ≥ rank(R) + 6.
```

It is enough that rank(R) ≥ 2. If c0 ≠ 1, then v2 = (a, 0, 1, c1) with a = 1 + c0 ≠ 0, and v3 = (0, 1 + c2, 0, 1). The last coordinate of v3 is 1, so v3 ≠ 0. A relation λ v2 + μ v3 = 0 forces λ a = 0, hence λ = 0, and then μ = 0. If c0 = 1, then v2 = (0, 0, 1, c1) ≠ 0 and v4 = (1, 0, 1 + c3, 0) ≠ 0. A relation λ v2 + μ v4 = 0 forces μ = 0 from the first coordinate and then λ = 0 from the third. Either way rank(R) ≥ 2.

Every value of c6 falls into one of the three cases. The sum is at least 8.

## Attainment

All seven coefficients zero gives rank 4 and rank 4. The single coefficient c6 = 1, with the others zero, gives rank 6 and rank 2. Both points have entries in F₂. The F₈ census below finds no other point of sum 8, and none of sum less than 8.

## What was enumerated

F₈ has 8⁷ = 2,097,152 points in this class. Both the C enumerator and the independent Python enumerator report minimum rank sum 8, with 2 points at sum 8 and none below. The equality points are the two F₂ points above. The histogram of rank sums 0 through 16 is

```text
0,0,0,0,0,0,0,0,2,0,1194,3306,42661,192405,414638,545106,897840
```

and the checksum is 3440682239519878741. That checksum is not the checksum of the settled class. On every one of these points, Gaussian elimination of Zh agrees with the block formula in the rank section. The Python checker also repeats the c6 = 1 row reduction on all 8⁶ tuples of (c₀, …, c₅) and checks the two-vector independence used above.

That finite census is not the proof for an arbitrary characteristic-2 field. It checks the displayed matrices, including the block formula for rank(Zh), on one finite field. The case analysis is what covers every field of characteristic 2. Characteristic not 2 is outside the argument: the identity 1 + c6² = (1 + c6)² uses characteristic 2.

Deleting the constant ones in Zg drops the zero-coefficient point to rank sum 4. Those ones are part of the solved class; the deleted matrix is only a failure control.

The scan that names the class is finite and stops at this word. It rejects any consistent system of nullity less than 7 earlier in lex order, and it rejects any earlier nullity-7 system whose reduced basis is neither the settled basis nor this one. It does not enumerate the words after permutation 8. Those words are outside the claim.

## What this does not decide

Later affine classes on this contract remain open, including every class the F₄ census left unresolved and every nullity-8 class. So do F₁₆ and larger fields outside this one scalar extension, three or more thin maps, and a stage with three or more full calls. No point found here changes κ.
