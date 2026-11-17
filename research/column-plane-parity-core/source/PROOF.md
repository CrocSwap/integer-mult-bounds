# Column-column plane orbits

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

No new κ is claimed. The selected frontier stays
`363005817/100000000000`. This note does not reprove the dimension bound
of #7139, and it does not classify the normal-normal or mixed geometries.

Evidence classes, kept separate:

- The single-plane normal form is a proof for every width.
- The weight-(2,2,2) count is an exhaustive finite census. The domain is
  finite because every such plane has support size 3, the pair support
  has size 6, 7, or 8, and every plane on a 3-set is the even-weight
  code. The completeness argument is the case split in Section 4 together
  with the labeled counts matched in Section 5.
- The unrestricted minimum-weight-at-least-2 count is a proof that there
  are infinitely many orbits, by an explicit family. It is not a census
  of a finite list of normal forms, and it is not a search.

## 1. Statement

Work over F2. A **column plane** is a pair (c, T) where c is a coordinate
and T is a 2-dimensional space of vectors with coordinate c equal to 0,
every nonzero vector of T having Hamming weight at least 2. Its image
space is span(e_c)+T, which is 3-dimensional because e_c is not in T.

A **column-column pair** is two column planes (c, T) and (d, S) with
c ≠ d and

```text
(span(e_c)+T) ∩ (span(e_d)+S) = 0.
```

A coordinate permutation acts by permuting the basis. Two pairs are
equivalent when some permutation carries one ordered pair of planes onto
the other, columns included. Support size means the number of coordinates
that appear in c, d, T, or S.

**Theorem A.** Coordinate-permutation orbits of a single column plane are
in bijection with sorted triples of nonnegative integers α ≤ β ≤ γ
satisfying α+β ≥ 2. The three nonzero weights are α+γ, β+γ, and α+β.
There are infinitely many such orbits.

**Theorem B.** There are exactly five orbits of column-column pairs in
which every nonzero vector of each plane has weight 2. Representatives,
with columns c, d and supports A, B, are

| orbit | support | crosses | A ∩ B | representative |
| --- | ---: | ---: | ---: | --- |
| mutual cross | 6 | 2 | empty | c=0, d=1, A={1,2,3}, B={0,4,5} |
| hooked overlap | 6 | 1 | one coordinate | c=0, d=1, A={1,2,3}, B={2,4,5} |
| one-sided placement | 7 | 1 | empty | c=0, d=1, A={1,2,3}, B={4,5,6} |
| shared foot | 7 | 0 | one coordinate | c=0, d=1, A={2,3,4}, B={2,5,6} |
| printed disjoint | 8 | 0 | empty | c=0, d=1, A={2,3,4}, B={5,6,7} |

A cross is a column that lies in the other plane's support. The one-sided
placement is pool B of #7221. The printed disjoint pair is the
column-column witness of #7138 Section 6 and #7139 Section 9. The
invariants (support size, number of crosses, |A ∩ B|) separate the five
rows, so no two rows are equivalent.

**Theorem C.** Dropping the weight-2 restriction, and requiring only
minimum weight at least 2, produces infinitely many orbits. One infinite
family is the printed disjoint pair with 2k extra coordinates, k =
0, 1, 2, ..., each extra pair duplicating coordinate 2 of that
representative. The resulting support sizes are 8+2k. Pool W of #7221 is
a further orbit, of support size 9, whose heavier plane has weights
2, 2, 4 and does not arise by that duplication.

## 2. One column plane

Let (c, T) be a column plane. The three nonzero vectors of T are a, b,
and a+b. Every coordinate other than c lies in one of four classes: in a
and a+b but not b; in b and a+b but not a; in a and b but not a+b; or in
none of them. Coordinate c itself is in none of them. Let α, β, γ be the
sizes of the first three classes, and sort them so that α ≤ β ≤ γ.

Each used coordinate contributes 2 to the sum of the three weights, so
that sum is 2(α+β+γ). The individual weights are

```text
wt(a) = α+γ,  wt(b) = β+γ,  wt(a+b) = α+β.
```

Minimum weight at least 2 is exactly α+β ≥ 2, α+γ ≥ 2, and β+γ ≥ 2.
Under α ≤ β ≤ γ the last two inequalities follow from the first.

Conversely, any such triple is realized by placing α, β, γ fresh
coordinates in the three classes and taking the two vectors that cut out
those classes. The column is one further coordinate. A permutation can
move the column to 0 and each class to an interval. Renaming a, b, a+b
sorts the triple, and GL(2, F2) induces every permutation of the three
nonzero vectors. Two planes therefore lie in the same orbit exactly when
their sorted triples agree.

The triples (1, 1, 1), (0, 2, 2), (0, 2, 3), ... are infinitely many, so
there are infinitely many single-plane orbits. The triple (1, 1, 1) is
the weight triple (2, 2, 2). The triple (0, 2, 2) is the weight triple
(2, 2, 4), which is the heavier plane of pool W.

## 3. Image intersection

Let R be the set of coordinates other than c and d, and let π forget
coordinates c and d.

The kernel of π on T is T ∩ span(e_d), because every vector of T already
has coordinate c equal to 0. A nonzero vector in that kernel would be
e_d, of weight 1, which T does not contain. Thus π is injective on T and
on S, and both images are 2-dimensional.

If a vector lies in both image spaces, write it as α e_c + t = β e_d + s.
Applying π gives π(t) = π(s). Trivial intersection of the projected
planes forces π(t) = π(s) = 0, hence t = s = 0, and then α = β = 0.

Conversely, π(t) = π(s) means t+s is supported on {c, d}. Since t has no
c-coordinate and s has no d-coordinate,

```text
s_c e_c + t = t_d e_d + s,
```

and the common value lies in both image spaces. It is zero only when
t = 0. Thus the image spaces meet only at 0 exactly when π(T) and π(S)
do.

## 4. The weight-(2, 2, 2) case split

Assume every nonzero vector of T and of S has weight 2. Section 2 gives
the triple (1, 1, 1), so each plane has support size 3. The three
nonzero vectors are the three weight-2 vectors on that 3-set, and they
are exactly the nonzero vectors of the even-weight code on the 3-set.
The plane is therefore that code. Write A = supp(T) and B = supp(S).
Then c is not in A and d is not in B.

The support of the pair is {c, d} ∪ A ∪ B. Its size is at most 8, when
the eight labels are distinct, and the case split below shows it is at
least 6. Every orbit therefore meets a configuration on 6, 7, or 8
coordinates in which every coordinate is used. Widths outside that range
add no orbits.

**No crosses.** Suppose d is not in A and c is not in B. Then A and B
both lie in R, π is the identity on each plane, and the intersection
condition is T ∩ S = 0.

If |A ∩ B| = 3, then A = B and T = S. If |A ∩ B| = 2, the two codes share
the weight-2 vector on the common pair. Both subcases fail.

If |A ∩ B| = 1, a common vector would be supported on that one
coordinate. The weight-1 vector on it is not in the even-weight code, so
T ∩ S = 0. The support size is 2+5 = 7. Any two such pairs are equivalent:
two external columns, one shared foot, and two private coordinates on
each side. This is the shared-foot row.

If |A ∩ B| = 0, the supports are disjoint, so the intersection is zero.
The support size is 8. This is the printed disjoint row: the two 3-sets
and the two columns are eight distinct coordinates.

**One cross.** Suppose d is in A and c is not in B. The symmetric
situation, c in B and d not in A, is the same orbit after swapping the
two planes. Write A = {d, p, q}. The even-weight vectors are
e_d+e_p, e_d+e_q, and e_p+e_q. Their projections to R are e_p, e_q, and
e_p+e_q, so π(T) is the full coordinate plane on {p, q}. Since c is not
in B and d is not in B, the support B lies in R and π(S) = S.

A nonzero even-weight vector on B lies in span(e_p, e_q) exactly when its
two support coordinates are {p, q}, that is, when {p, q} ⊂ B. The
intersection is trivial exactly when |B ∩ {p, q}| is 0 or 1.

If the intersection with {p, q} is empty, B is a 3-set disjoint from
{c, d, p, q}. The support size is 7. This is the one-sided placement,
pool B of #7221: one plane contains the other column, and the remaining
supports are disjoint.

If the intersection with {p, q} has size 1, B consists of that shared
coordinate and two further coordinates outside {c, d, p, q}. The support
size is 6. Swapping p and q is an automorphism of the even-weight code
that fixes d, so the choice of which foot is shared does not create a
second orbit. This is the hooked-overlap row.

**Two crosses.** Suppose d is in A and c is in B. Write A = {d, p, q}
and B = {c, r, s}. As above, π(T) is the full plane on {p, q} and π(S)
is the full plane on {r, s}. Those planes meet only at 0 exactly when
{p, q} and {r, s} are disjoint. The support is then the six coordinates
{c, d, p, q, r, s}. This is the mutual-cross row. An overlapping choice
of {p, q} and {r, s} has nontrivial intersection and is excluded.

These five combinatorial types are the rows of Theorem B. The triple
(support size, number of crosses, |A ∩ B|) is preserved by coordinate
permutation, and the five triples (6, 2, 0), (6, 1, 1), (7, 1, 0),
(7, 0, 1), and (8, 0, 0) are distinct. The rows are five orbits.

## 5. Labeled counts

The same split counts the labeled pairs on a fixed width in which every
coordinate is used. These counts are the size of the census domain, not
a second list of orbits.

On 8 coordinates the only surviving type is the printed one. Choose the
ordered columns in 8·7 ways and the 3-set A in C(6, 3) ways; B is the
complement. The count is 8·7·20 = 1120.

On 6 coordinates the mutual-cross type contributes 6·5·C(4, 2) = 180:
the complement of the two-foot set is forced. Each one-cross orientation
contributes 6·5·C(4, 2)·2 = 360, and the two orientations are disjoint,
so the one-cross contribution is 720. The width-6 total is 900.

On 7 coordinates the one-sided type contributes 7·6·C(5, 2) = 420 in each
orientation, hence 840. The shared-foot type contributes 7·6·C(5, 3)·3
= 1260: choose A, then choose which point of A is the shared foot, and
the other two points of B are forced. The width-7 total is 2100.

Widths 5 and 9 contribute 0. Five coordinates cannot hold support size
at least 6. Nine coordinates cannot all be used when the support has
size at most 8.

`verify.py` enumerates every ordered pair of columns and every pair of
3-sets on widths 5 through 9, keeps the configurations whose image
spaces are 3-dimensional, meet only at 0, and use every coordinate, and
checks that the surviving invariants and the labeled counts are exactly
the ones above. A configuration in an excluded subcase, such as
|A ∩ B| = 2 with no cross, is built and checked to have nontrivial
intersection. That is the exhaustive census. The case split is what
shows that every weight-(2, 2, 2) pair appears in it.

## 6. Infinitely many orbits in the wider family

Start from the printed representative and, for each integer k ≥ 0, add
2k fresh coordinates. For each i = 0, ..., k-1 the two coordinates
8+2i and 9+2i lie in exactly the vectors of T that contain coordinate 2,
and in no vector of S. The new nonzero vectors of T are

```text
e2+e3+E,  e2+e4+E,  e3+e4,
```

where E is the sum of the 2k fresh basis vectors. The first two weights
are 2+2k, counting coordinate 2, coordinate 3 or 4, and the fresh
coordinates. The third weight is 2. For k = 0 this is the printed plane.
For every k ≥ 0 the minimum weight is 2. The three vectors sum to zero,
and any two of them are independent, so the plane is still 2-dimensional. The second
plane is unchanged. Neither support contains the other column. The two
R-supports are disjoint, so Section 3 gives trivial image intersection.
The support size is 8+2k.

Different values of k have different support sizes, which coordinate
permutation preserves. The family therefore meets infinitely many
orbits. This is an explicit infinite family, not a claim that these are
all the orbits.

Pool W, from #7221 Section 3, is the pair

```text
T = span(e1+e2, e3+e4) at column 0,
S = span(e6+e7, e6+e8) at column 5.
```

Its weights are (2, 2, 4) and (2, 2, 2), its support size is 9, and the
R-supports {1, 2, 3, 4} and {6, 7, 8} are disjoint, so the image
intersection is zero. It is not one of the five rows. It is also not a
member of the doubling family: the weight-2 vector e1+e2 is supported
on exactly the two coordinates of one type, so deleting those two
coordinates kills that vector and the plane collapses to a line. The
doubling family, read backwards, only deletes a duplicated coordinate
when a weight-2 core remains.

## 7. What this does and does not claim

Theorem A is the single-plane classification. Theorem B is the
exhaustive census of the weight-(2, 2, 2) pairs. Theorem C shows that
the minimum-weight-at-least-2 problem, which is the question asked in
#7221, has infinitely many orbits. Pools W and B are two of them, and
the printed complementary weight-(2, 2, 2) pair is a third. The five-row
list is the full set of orbits in which both planes have weights
(2, 2, 2). It is not a full set of normal forms for every
minimum-weight-at-least-2 pair.

The normal-normal geometry and the mixed geometry of #7139 Section 7
are not classified here. No word is priced. The selected κ and its five
framework assumptions are unchanged.

## Open next questions

1. After deleting, in pairs, every coordinate that duplicates another
   coordinate in both planes, which orbits still have minimum weight at
   least 2 and both planes of dimension 2? The doubling family reduces
   to the printed row. Pool W collapses instead, so it is a different
   kind of orbit. The first deletion to try is one repeated type in a
   plane whose three type counts are positive.

2. Is every dimension-6 pool built from two normal-form triples, or
   from one normal-form triple and one column triple, a coordinate
   permutation of the witness printed in #7139? That is question 2 of
   #7221. The column-column census does not decide it.
