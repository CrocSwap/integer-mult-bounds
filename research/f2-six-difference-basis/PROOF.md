# The difference basis of \(\mathbb{F}_2^6\) has order 14

Scoped census. No new κ. The selected conditional exponent stays
`60403/20000000`.

## Definition

Let \(G = \mathbb{F}_2^6\). A **difference basis** is a set \(P \subseteq G\) such
that

\[
\{x + y : x, y \in P,\ x \neq y\} = G \setminus \{0\}.
\]

These are the prefix differences of a source walk. In characteristic 2 the
sum of a vector with itself is zero, so only distinct pairs contribute a
nonzero mask. There are 63 nonzero masks.

## Counting

\(\binom{11}{2} = 55 < 63\), so no set of 11 or fewer points is a difference
basis. Every difference basis has at least 12 points.

## Normalization

Translation preserves differences, so a difference basis may be moved until
it contains 0. The remaining points must span \(G\): otherwise every
difference lies in a proper subspace and misses a coset. A spanning set
contains a basis. The linear map sending that basis to

\[
\{e_1, e_2, e_3, e_4, e_5, e_6\} = \{1, 2, 4, 8, 16, 32\}
\]

is a group automorphism, so it preserves the property of being a difference
basis. It is therefore enough to test sets that contain 0 and this basis.
The other points are chosen from the 57 nonzero non-basis vectors.

A set that does not span \(G\) has already been excluded. Its differences
meet at most 31 nonzero masks.

## Census

For each normalized set the nonzero pairwise sums of \(\{0\}\) together with
the chosen points are counted. The two implementations agree on every
normalized 12-point set. The 13- and 14-point rows are the compiled loop,
whose visit counts are the binomial coefficients and whose extremal
witnesses are recomputed by the Python coverage routine.

| \(|P|\) | normalized sets | full covers | maximum nonzero sums |
| ---: | ---: | ---: | ---: |
| 12 | \(\binom{57}{5} = 4{,}187{,}106\) | 0 | 57 |
| 13 | \(\binom{57}{6} = 36{,}288{,}252\) | 0 | 62 |
| 14 | \(\binom{57}{7} = 264{,}385{,}836\) | 53{,}340 | 63 |

One 12-point maximum is the nonzero set

\[
\{1, 2, 3, 4, 8, 16, 28, 32, 45, 54, 59\},
\]

which misses \(\{14, 15, 21, 23, 25, 26\}\). One 13-point maximum is

\[
\{1, 2, 3, 4, 5, 8, 16, 30, 32, 46, 54, 57\},
\]

which misses only \(63\). One 14-point basis, contained in the 53{,}340
normalized covers, is

\[
\{0, 1, 2, 3, 4, 5, 6, 8, 16, 24, 32, 40, 48, 63\}.
\]

Deleting any one of its nonzero points drops the cover. That deletion check
is special to this witness. The order is sharp because no 13-point set
covers, not because every 14-point set does.

## Consequence for the six-source connector

On the six-source connector, a closed source walk covers every nonzero mask
only when the set \(P\) of distinct prefix states is a difference basis.
Therefore \(|P| \ge 14\). A revisit makes \(|P|\) strictly smaller than the
length, which cannot help: a walk with a repeated prefix still needs 14
distinct prefixes, so its length is longer. Every covering closed walk is
simple and has length at least 14.

The predecessor's set-level query count is twice the number of nonzero masks
plus the number of prefixes. That count is at least

\[
2 \cdot 63 + 14 = 140
\]

and is not \(2 \cdot 63 + 12\). The explicit 14-point set shows that the
obstruction stops at 14. It does not supply a closed walk, a legal step
weight, or a priced connector program, so 140 is not shown to be attained.

## What is not claimed

No five-source leaf bill, no twelve-call profile with two triple edges, and
no change to the selected exponent. The positive control in \(\mathbb{F}_2^3\)
is only a check of the same predicate: the basis \(\{0, 1, 2, 4\}\) misses a
mask, and some 5-point set covers.
