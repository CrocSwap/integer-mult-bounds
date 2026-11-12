# Exact balanced optimum at coefficient height one

All ranks in this note are over the rationals. Let

```text
D = {M in Mat_2(Z) : every entry belongs to {-1,0,1}}.
```

A balanced rank-distance biclique of order r consists of two r-element
subsets E and O of D. Distinct matrices in the same part have difference
rank two; every cross-part difference has rank one.

**Result.** The maximum r is exactly six. The lower bound has a written
construction. The upper bound is an exact finite enumeration with two
implementations and the coverage argument below. No formal-kernel acceptance
of that finite computation is claimed.

## Six-by-six construction

Write q(a,b)=a^2+ab+b^2 and take

```text
S = {(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)}.
E(a,b) = [[a,b],[-a-b,a]]
O(a,b) = [[a,b],[b,-a-b]]       for (a,b) in S.
```

Every point in S satisfies q=1 and every displayed entry is in {-1,0,1}.
The determinant identities are

```text
det(E(a,b)-E(u,v)) =  q(a-u,b-v)
det(O(a,b)-O(u,v)) = -q(a-u,b-v)
det(E(a,b)-O(u,v)) =  q(a,b)-q(u,v) = 0.
```

The identity `4q(a,b)=(2a+b)^2+3b^2` proves strict positivity away from
zero over Q. Thus distinct same-part differences have rank two. The parts
are disjoint because E has determinant one and O has determinant minus one.
Consequently every cross difference is nonzero and singular, with rank one.

For the actual shear frames

```text
Phi(M) = [[I_2,M],[0,I_2]],
```

we have `Phi(M)Phi(N)=Phi(M+N)` and
`rank(Phi(M)-Phi(N))=rank(M-N)`. Hence these twelve commuting integral
four-by-four frames have the rank-distance metric K_(6,6).

## Upper bound by a complete finite certificate

For every unordered triple {A,B,C} of distinct matrices in D whose three
pairwise differences have rank two, count

```text
N(A,B,C) = #{X in D : rank(X-A)=rank(X-B)=rank(X-C)=1}.
```

The enumeration gives the following complete distribution.

| N(A,B,C) | Number of triples |
|---:|---:|
| 0 | 1,480 |
| 1 | 4,368 |
| 2 | 9,624 |
| 3 | 5,760 |
| 4 | 2,096 |
| 6 | 160 |

There are 23,488 such triples. In particular each has at most six common
rank-one contacts. A purported K_(7,7) contains three matrices in its first
part, while all seven matrices of its second part would be contacts of that
triple. This contradicts the certified ceiling six. Any larger balanced
biclique contains a K_(7,7), so it is excluded as well.

This upper certificate does not assume that the contacts themselves have
pairwise rank-two differences. Its relaxation is sufficient for the ceiling.

## Why both enumerations cover the domain

`verify.py` creates exactly the 3^4=81 lexicographically ordered matrices.
For every ordered matrix pair, it computes rank from its determinant and
whether the difference is zero. It visits each of the binomial(81,3)=85,320
unordered triples once. Rank-two adjacency selects the admissible triples;
intersection of three 81-bit rank-one neighbor sets counts their contacts.
It checks the complete histogram and emits a hash of every retained triple
and its full contact bitset, in order.

`ceiling.py` imports no scientific code from the first verifier. It derives
all pair ranks by exact Fraction Gaussian elimination. Two matrices with
the same first row cannot have rank-two difference. An admissible triple
therefore uses three distinct first rows among the nine possible rows.
For each of the binomial(9,3) choices, it tries all 9^3 second-row choices,
giving 61,236 candidates. Sorting first rows gives every admissible triple
exactly once, even though this ordering differs from the first enumeration.
For each accepted triple it scans all 81 matrices and tests the three
contact ranks individually. It recovers the same complete histogram.
It also checks all 144 ordered differences of the twelve four-by-four
shear frames by Fraction elimination, covering attainment directly.

The first verifier rejects a missing witness matrix, duplicates, a height
violation, Boolean or noninteger entries, a malformed shape, overlapping
parts, a same-part rank-one change, and missing/repeated domain vertices.
The second verifier checks elimination on zero, singular, nonsingular,
pivot-swap and rational fixtures. All acceptance checks remain enabled under
optimized Python.

## Scope

This is an exact finite result for D, with a rational construction proof.
It does not bound larger coefficient heights, rational entries of bounded
denominator, different matrix orders, or other fields. The elementary
determinant and rank arguments are classical. No literature-priority claim
is made for them. The new claim is the specified height-one optimum and
its twelve-matrix attaining configuration.
