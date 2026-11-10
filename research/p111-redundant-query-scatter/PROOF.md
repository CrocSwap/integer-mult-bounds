# A retained four-centre query cannot sparsify this scatter

This scoped proof was produced by Nick Petalas. Work over the rational
numbers. The same proof holds over the real or complex numbers. It concerns
direct scalar ADD coefficients, with arbitrary coefficients permitted.

Let c be an arbitrary vector of eight independent centre values in the order
`(60,61,63,224,31,240,23,256)`. Put J=`{61,63,31,256}` and

```text
q = (c61+c63+c31+c256)/2.
```

Let S be the 112-by-8 matrix of the pinned PR1525 word's `cut` array. We
ask for matrices B with nine columns such that

```text
B (c,q) = S c    for every c.
```

All eight old readouts are retained. Only their use in this direct scatter
is being optimized. The price of B is its number of nonzero entries. Each
entry denotes one scaled ADD to the corresponding arbitrary dirty output.
No sharing, intermediate accumulator, target mixing or basis change is
included in this price model. Readout acquisition and frames are not free
physical operations merely because the algebra grants their availability.

## Every exact correction and its cost

Fix a row a of S. If the coefficient of q in its replacement row is t,
coefficient comparison on the eight independent centre variables forces

```text
b_j = a_j-t/2 for j in J,
b_j = a_j     for j outside J.
```

Conversely these coefficients work for every t. This describes every exact
row, without a finite coefficient restriction. In particular no independent
correction freedom is omitted by the following optimization.

Let z be the number of zero entries of a on J. If t is nonzero, all z of
these entries become nonzero, the query adds one nonzero entry, and the only
cancellations are entries with a_j=t/2. If m(t/2) counts those entries, the
exact increase in row support is

```text
1+z-m(t/2).
```

The finite source census below finds at most two nonzero entries on J in
every row. Thus z>=2 and m(t/2)<=2. Every nonzero query coefficient strictly
increases that row's support, by at least one. A query-free row is forced
to equal a. Since the rows have independent coefficients, the unique
minimum-support B is `[S | 0]`, of support 176.

If at least one query coefficient must be nonzero, support is at least 177.
Equality is possible exactly by activating one row with z=2 and two equal
nonzero coefficients a_j=t/2, and leaving every other row unchanged. This
also characterizes every matrix attaining 177.

## Complete finite census and attainment

Every coefficient of S is 0 or plus/minus 1/4. The checker classifies every
row by its entries on J. The counts and minimum nonzero-query penalties are:

| Entries on J | Rows | Minimum increase |
|---|---:|---:|
| Four zeros | 40 | 5 |
| One nonzero | 56 | 3 |
| Two equal nonzeros | 8 | 1 |
| Two opposite nonzeros | 8 | 2 |

For each of the eight equal-pair rows, choose t twice the common coefficient.
The two original nonzero entries disappear, the two previously zero entries
become their negatives, and q adds one term. This gives an exact 177-entry
matrix. The replay reports all eight receiver IDs, and emits one attaining
row's receiver and coefficient. The finite arithmetic census supplies the
source-specific premise; the argument above supplies the quantifier over
every rational coefficient and every exact direct-scatter matrix.

An independent checker enumerates all 512 subsets of the nine readouts for
each of the 112 rows. It uses exact integer elimination for rational span
membership, without the frequency formula. With q present, a nonzero query
coefficient exists if q is dependent on the selected centres, or, when it
is independent, if a is absent from the selected-centre span. This also
handles zero rows, where query use requires compensating centre terms.
All 57,344 support-subset cases give the same two per-row minima.

## Dirty values and the precise obstruction

The matrix identity holds for arbitrary c. Therefore it holds for every
possible prior linear or nonlinear dependence of c on original inputs and
dirty workspace. Adding B(c,q) to arbitrary outputs preserves precisely the
same dirty dependence as adding Sc. No original dirty coefficient has been
discarded, specialized to zero or claimed compensated. The direct ADD program
reads c and q without changing them. Reversing its ADD signs restores the
outputs exactly. This is an algebraic restoration statement.

The lower bound requires exact equality for every independent centre vector.
Restricted-value inputs or a caller that needs a different output are other
contracts. Shared arithmetic can compute a direct matrix more cheaply than
its nonzero count, so this is not an ADD-circuit lower bound. Multiple new
queries, changed source bases and changing the scatter itself are outside
scope. In particular this result does not reject PR1525's whole research
direction or reprove PR6640's different eight-readout price check.

The two-zero premise matters. A row with coefficient 1/4 on all four query
centres has four old terms and equals q/2, which has one. The replay includes
this changed-premise positive control.
