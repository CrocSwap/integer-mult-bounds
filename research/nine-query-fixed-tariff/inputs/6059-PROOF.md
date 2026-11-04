# Exact readout frontier for partitioned independent walks

The result is a scoped theorem in the five-source abstract model of Wentao Li's
[PR #2779](https://github.com/CrocSwap/integer-mult-bounds/pull/2779), using
Nick Petalas's extension to arbitrary labels and any number of walks in
[PR #6036](https://github.com/CrocSwap/integer-mult-bounds/pull/6036).
It supplies no physical supplier or new kappa. The proof is elementary counting;
the bounded finite checks corroborate it rather than replace an unbounded step.

## 1. Model and theorem

A restored walk is a slot list

```
w = (s_0, ..., s_(n-1)),    s_0 = 0,    s_i in F2^5,
```

whose closed completion has no zero edge: consecutive labels differ, including
the last label and the initial zero. Labels may repeat at nonadjacent slots,
and zero may be revisited. Necessarily n >= 2. Its even-subset table e_w(x)
is the minimum cardinality of a subset of slots whose XOR is x and whose
cardinality is even, or infinity if there is no such subset. In particular
e_w(0)=0 by the empty subset.

For k >= 2 independent walks of lengths n_1,...,n_k, let Q=sum_i n_i and
define the cost of a mask x by the min-plus XOR convolution

```
c(x) = min { sum_i e_(w_i)(x_i) : x_1 XOR ... XOR x_k = x }.
```

A family covers if every x in F2^5 has finite cost. Its readout is
R=sum_(x != 0) c(x). For k=2 this is PR #2779's two-port model; the k>=3
extension is the one explicitly defined in PR #6036.

**Theorem.** No covering family exists at Q<7. For every integer Q>=7 the
minimum readout over all covering families, all walk counts k>=2 and all
permitted label repetitions is

| Q | Minimum R |
|---:|---:|
| 7 | 112 |
| 8 | 92 |
| 9 | 80 |
| 10 | 72 |
| 11 | 66 |
| >=12 | 62 |

The first three values are retained predecessor results. The new ingredients
are sharp pair-difference bounds for eight and nine points in F2^5, which
settle the open Q=10 and Q=11 cases, and an explicit saturation construction
with a valid padding rule for every Q>=12.

## 2. Even-subset costs and difference sets

For a support set A in F2^5 write

```
D(A) = { a XOR b : a,b in A, a != b }.
```

The table lemma of PR #6036 also follows directly from the definition.
An arbitrary subset of slots has the same XOR after toggling slot 0, so an
even subset exists precisely for the masks in the span of the walk labels.
For a nonzero mask every finite cost is an even integer at least two, and
cost two is equivalent to membership in D(A). Repeated labels do not change
this equivalence: two equal labels produce zero, not a new nonzero difference.

Consequently, if P is the union of all walk difference sets, exactly the masks
in P have combined cost two. Every other nonzero mask of a covering family
costs at least four. Thus

```
R >= 124 - 2|P|,    R >= 62.                                  (1)
```

These are lower bounds: the masks outside P need not all have cost four.
Attaining families below are checked with their full even-subset tables.

Coverage is equivalent to the sum of the walk spans being F2^5. Since each
walk starts with zero, its span has dimension at most n_i-1. Therefore

```
5 <= sum_i (n_i-1) = Q-k <= Q-2,                              (2)
```

which proves the nonexistence statement for Q<7.

## 3. Two sharp finite-geometry bounds, proved without a census

**Lemma 1.** If A is a subset of F2^5 with at most eight points, then
|D(A)|<=25.

**Proof.** It suffices to consider eight distinct points: smaller sets can
be enlarged to size eight, and enlargement cannot remove a difference.
Write A={a_1,...,a_8}. The kernel over F2 of the matrix whose columns are
(1,a_i) in F2^6 has dimension at least two. Choose a two-dimensional subspace
C of this kernel. Every nonzero vector of C has even weight, and its weight
cannot be two because the points a_i are distinct. Thus its three nonzero
vectors have weights at least four.

At each coordinate, either every vector of C is zero or exactly two vectors
are one. The sum of the three nonzero weights is therefore at most 2*8=16.
They cannot all have weight at least six. There is a weight-four vector, or
four distinct points whose XOR is zero.

Those four points produce three different pairings into equal-difference
pairs. The three corresponding nonzero differences are distinct. Among the
C(8,2)=28 unordered pairs, there are therefore at least three excess
occurrences beyond the first occurrence of each difference. Hence
|D(A)|<=28-3=25. QED.

**Lemma 2.** If A is a subset of F2^5 with at most nine points, then
|D(A)|<=28.

**Proof.** Again enlarge to nine distinct points if needed. The same
six-row matrix now has a kernel of dimension at least three. Choose a
three-dimensional subspace C of the kernel. Its seven nonzero vectors
have even weights at least four, and their total weight is at most 4*9=36.
If at most two had weight four, the total would be at least
2*4+5*6=38. Thus A has at least three distinct four-point subsets with
zero XOR.

For each nonzero d let m_d be the number of unordered pairs from A with
difference d. Two distinct pairs with the same difference cannot share a
point. If N_4 is the number of zero-XOR four-point subsets, double counting
the three pairings of each such subset gives

```
sum_(d != 0) C(m_d,2) = 3 N_4 >= 9.                          (3)
```

If every m_d<=2, then C(m_d,2)=max(m_d-1,0). Since sum_d m_d=36,
equation (3) gives 36-|D(A)|>=9, and in fact |D(A)|<=27.

Otherwise one difference b occurs in at least three pairs. Take six points
B from three of these disjoint pairs. They form three cosets of the
two-element subgroup {0,b}. Their internal differences consist of b and
at most two differences for each pair of distinct cosets. Hence

```
|D(B)| <= 1 + 2*C(3,2) = 7.
```

The remaining set C=A\B has three points. There are at most 6*3=18
cross differences and at most C(3,2)=3 differences inside C. Every
difference of A belongs to one of these three classes, so
|D(A)|<=7+18+3=28. QED.

Both bounds are sharp. The supports

```
A8 = {0,1,2,4,8,16,30,31},
A9 = {0,1,2,4,8,16,29,30,31}
```

have respectively 25 and 28 differences, with integers denoting their
five-bit vectors. These claims are small direct XOR checks. The verifier
also corroborates the bounds by normalizing a full-rank support to contain
{0,1,2,4,8,16} and enumerating the C(26,2)=325 or C(26,3)=2600 possible
extra-point sets. Supports of rank at most four have at most 15 nonzero
differences. This normalization is independent of the kernel-weight proof.

## 4. The Q=7,8,9 predecessor cases

At Q=7, (2) forces k=2, with lengths (2,5) or (3,4), up to interchange.
The five noninitial slot labels must be linearly independent. Thus their
two walk spans form a direct sum of dimensions d_1=n_1-1 and d_2=n_2-1,
with d_1+d_2=5 and each d_i>=1. Every mask has a unique expression using
these five labels. In a given walk, if that expression uses h noninitial
slots, the even-subset cost is h when h is even and h+1 when h is odd,
because the only possible adjustment is to include slot 0.

Summed over all 32 masks, the selected-label contribution is 32*5/2=80.
For each of the two nonempty blocks, exactly half of its coefficient vectors
have odd weight, contributing 16 more. The zero mask contributes zero.
Therefore every covering Q=7 family has R=80+16+16=112. Independent basis
labels give valid restored walks, so the bound is attained. This rederives
the PR #2779 value in the arbitrary-label scope of PR #6036.

For general lengths, |D(A_i)|<=C(n_i,2), so (1) implies

```
R >= 124 - 2 sum_i C(n_i,2).
```

For fixed Q with n_i>=2 and k>=2, moving slots from a smaller part to a
largest part can only increase the sum of these binomial coefficients.
Its maximum is 1+C(Q-2,2), at the two-part partition (2,Q-2).
This is PR #6036's pair-sum bound. It gives R>=92 at Q=8 and R>=80 at Q=9.
The same predecessor supplies attaining valid walks:

```
Q=8: (0,10), (0,22,5,31,24,20),
Q=9: (0,3),  (0,18,1,5,11,20,27).
```

The present verifier recomputes their complete readout tables as calibration
fixtures. Their origin and the established values remain credited to PR #6036.

## 5. The exact Q=10 and Q=11 minima

The preceding geometry bounds apply to supports of walks, regardless of
repetition or slot order. The union of difference sets is bounded by the
sum of their sizes; overlap can only make the union smaller.

For two walks the complete lists of length partitions and resulting bounds
on |P| are:

| Q | Lengths | Bound on size of P |
|---:|:---|---:|
| 10 | (2,8) | 1+25=26 |
| 10 | (3,7) | 3+21=24 |
| 10 | (4,6) | 6+15=21 |
| 10 | (5,5) | 10+10=20 |
| 11 | (2,9) | 1+28=29 |
| 11 | (3,8) | 3+25=28 |
| 11 | (4,7) | 6+21=27 |
| 11 | (5,6) | 10+15=25 |

For k>=3, convexity bounds sum_i C(n_i,2) by
C(Q-2k+2,2)+(k-1). For feasible k>=3 this is at most its k=3 value:
17 at Q=10 and 23 at Q=11. These are smaller than 26 and 29 respectively.
This treats every walk count and every permitted repetition pattern.

Equation (1) therefore gives

```
Q=10: R >= 124-2*26 = 72,
Q=11: R >= 124-2*29 = 66.
```

The following explicit families attain these bounds:

```
Q=10: (0,7), (0,1,2,4,8,16,30,31),
Q=11: (0,7), (0,1,2,4,8,16,29,30,31).
```

Each closed walk has nonzero edges because its slots are distinct. Their
long walks contain all five basis vectors, so both families cover.
Direct enumeration of their even subsets and XOR convolution gives
26 masks of cost two and five of cost four at Q=10, and 29 masks of
cost two and two of cost four at Q=11. Thus R=72 and R=66 respectively.

## 6. Saturation at every Q>=12

At Q=12 take

```
(0,1), (0,1,2,4,8,16,3,5,6,31).
```

The ten-point long support has all 31 nonzero differences. This finite
identity is checked by direct XOR enumeration. Thus every nonzero mask
can be read with cost two, attaining the universal floor R=62.

To increase Q by one, choose any edge (a,b) of the long walk and insert
an existing support label c distinct from both a and b. There is such a
label because the support has ten points. Both new edges (a,c),(c,b)
are nonzero. The initial zero and the closed completion are retained,
and the support is unchanged. In particular its 31 differences remain.
Repeat this operation for any desired number of added slots. This proves
attainment at every integer Q>=12, including both parities. Adjacent
duplication of a label would create a zero edge and is not the padding rule.

## 7. Tariff consequence and scope

In the retained abstract tariff T=38Q+2R+2X with X>=0, the exact readout
frontier gives the following lower bounds, without claiming that X=0 is
attainable together with the readout minimum:

| Q | Lower bound on T |
|---:|---:|
| 7 | 490 |
| 8 | 488 |
| 9 | 502 |
| 10 | 524 |
| 11 | 550 |
| >=12 | 38Q+124>=580 |

Hence every covering partitioned independent-walk family in this model has
T>=488, strictly above the six-query endpoint tariff 436. This is a consistency
corollary, not a new tariff obstruction: it already follows by combining
PR #6036's exact Q=7 value with its older readout floors. It does not identify
the exact minimum of T: path cost X and its possible tradeoff with readout remain.

The theorem concerns the five-source alphabet, independent restored walks,
and the stated even-subset/min-plus billing rule. It does not cover same-walk,
transfer-coupled, shared-dirt or changed-output contracts. No native supplier,
compiler, precision, stock, restoration implementation or outer multiplication
transfer is supplied or priced by this abstract result. No selected-frontier
change, proof-kernel acceptance or independent human review is claimed.

## Credit

The model and two-port readout rule are due to Wentao Li, PR #2779, building
on Arham Tahir's PR1898 and the lineage retained in those packages. Nick
Petalas, PR #6036, supplies the arbitrary-label and multiple-walk scope,
pair-sum floor, prior exact Q=7,8,9 conclusions and Q=8,9 witnesses, and
the open questions resolved here. New geometry proof, exact frontier completion
and verification were prepared by **apoursh**, with substantial OpenAI Codex
assistance, including independent subagent derivation and checking.
Apache-2.0.
