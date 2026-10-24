# Exact support distance of the eight source queries

Every nonzero scalar combination of the eight rows of the actual
query matrix `R` uses at least 53 of the 112 source ports. This bound
is exact. Each of the 112 old-root coefficient directions attains it.

This gives a restriction on shared snapshot proposals. On the valid
input family `X=JY`, with all helper and private inputs zero, each
snapshot in an actual frame of rank at least two uses at most 20
source ports. Thus a nonzero query cannot be a combination of only
two such snapshot fields. More generally, a `k`-dimensional query
space needs at least `k+2` such fields in one common span. A full
eight-query span therefore needs at least ten fields. This is a
field-count bound, not a native-cost bound for a general shared
network.

## The quartet structure

The pinned matrix has 14 groups of eight columns. Each group has one
four-coordinate support. Within that support, the columns give all
16 sign vectors modulo multiplication by minus one. The certificate
checks this fact directly from `INTERFACE.json`; it does not assume
an E8 classification.

Let `a` be a nonzero complex row of length eight. Fix one quartet,
and let `t` be the number of nonzero entries of `a` on it. The eight
column evaluations are the signed sums on that quartet, modulo sign.
Their number of nonzero values is at least

```text
t:                 0  1  2  3  4
nonzero values:    0  8  4  6  5
```

Here is a short proof of this table. First project the nonzero
complex coefficients onto a real line that gives no zero coefficient.
A complex zero sum is still a zero sum after this projection. Change
the signs of the coefficients so that all projected coefficients are
positive. The sign patterns in one quartet are closed under this
change.

Subsets of positive coefficients with a fixed sum form an antichain:
one cannot be a proper subset of another. A permutation gives a
maximal chain of subsets, and an antichain meets it at most once.
Counting the permutations through each subset gives

\[
\sum_{S\text{ in the antichain}}
  \binom{t}{|S|}^{-1}\leq1.
\]

Thus there are at most `binomial(t,floor(t/2))` zero sign patterns.
The zero patterns occur in opposite pairs. For `t=1,2,3,4`, their
counts are therefore at most `0,2,2,6`. Each zero coefficient on the
quartet doubles the number of full sign patterns. Division by two
then identifies opposite full patterns. This gives the displayed
table.

For each of the 255 possible nonempty coefficient supports, add the
14 quartet bounds. The exact minima at each support size are

| Nonzero coefficients in `a` | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lower bound for support of `aR` | 56 | 76 | 78 | 53 | 73 | 75 | 77 | 70 |

The smallest bound is 53. The checker also evaluates `aR` exactly
when `a` is any actual column of `R`. Each of these 112 choices has
support 53. The lower bound and its attainment prove the claimed
minimum. The table gives lower bounds at each coefficient support
size; no separate attainment claim is made for its other entries.

## Consequence for a shared span

The independent snapshot support theorem says that a snapshot at
frame `U`, on the input family above, uses only ports perpendicular
to `U`. The certificate checks all actual frame bases. Every frame
of rank at least two permits at most 20 ports. The maximum counts
at ranks two through eight are `20,10,8,8,4,2,1`.

Let `w_1,...,w_m` be independent reduced snapshot rows of this type.
Suppose their span contains a `k`-dimensional subspace of the query
row space. Each query has a unique coefficient row in this basis.
The resulting length-`m` linear code has minimum nonzero Hamming
weight at least three: a combination of at most two birth rows has
support at most 40, while a nonzero query has support at least 53.
Delete any two code coordinates. The deletion is injective, so

\[
k\leq m-2.
\]

If the original birth rows are dependent, first keep a basis from
them. The same bound applies and hence also bounds their original
count. This excludes a four-birth-field, three-query merge of this
type, even if the query basis is changed. It also gives the bound of
ten fields for all eight queries.

The same support count holds for nonzero operator coefficients on
the query rows. Apply a linear functional to the coefficient
operators that does not kill all of them. Every zero port operator
remains zero, and the scalar support bound applies. For payload
fields of dimension `d`, the coefficient code then has dimension
`kd` and block distance at least three. Deleting two field blocks
gives `kd <= (m-2)d`. This extension still requires each birth field
to have source-port support at most 20. It does not allow new source
reads to enter without counting their fields.

## Verification and scope

Run:

```text
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/history-encoding/check_query_support_distance.py
```

The result is `PASS_EXACT_QUERY_SUPPORT_MINIMUM_53`, saved in
`QUERY-SUPPORT-DISTANCE.json`. The checker reads the pinned query
matrix and frame table. It checks all quartet sign patterns, all 255
coefficient supports, all 112 attaining directions, and all actual
frame support counts. A duplicate sign-pattern control and an
excessive quartet-bound control both fail.

This proof inherits the independent exact snapshot support review.
It does not repeat the 712-input core replay. It does not prove a
64-rank lower bound, or an optimal field count for a network with
several merge levels. A new observation at a later frame can add
information; shared paid edges can also change the cost. A positive
circuit still needs time order, phases, arbitrary-state cleanup,
private lifetimes, and complete native and scalar costs.
