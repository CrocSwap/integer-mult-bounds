# Higher prime powers do not enlarge this column alphabet

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

**Theorem.** Let q>=5 be prime and let a,b>=1. Let H have q+3 rows,
at least four pairwise orthogonal columns, and entries in the group
of roots `mu_m`, where `m=3^a q^b`. Row and column phases from mu_m
change H into a matrix with entries in `mu_(3q)`.

Equivalently, every two-by-two multiplicative cross ratio of H lies
in mu_(3q). The explicit double dephasing is

```text
H'_rj = H_rj conjugate(H_r0) conjugate(H_0j) H_00.
```

The theorem says that every entry of H' lies in the smaller alphabet.
It preserves all column inner products and their norms.

**Corollary.** The maximum number of pairwise orthogonal eight-entry
columns over `mu_(3^a 5^b)` is exactly four for every a,b>=1. This follows
from the complete fifteenth-root capacity proof in
[PR #7769](https://github.com/CrocSwap/integer-mult-bounds/pull/7769).
Its [attaining matrix and exhaustive certificate](https://github.com/aliromman/integer-mult-bounds/blob/6dbe6e9503f26189833d5ef213aee708679835f2/research/fifteenth-root-column-capacity/PROOF.md)
remain unchanged and replay here. Four columns attain the bound in
every larger alphabet because mu_15 is a subgroup.

This is an exact alphabet theorem, not a physical supplier. No new
kappa or change to the selected frontier follows.

## 1. Pairwise zero sums have only two cycles

The classical two-prime result of
[T. Y. Lam and K. H. Leung, Corollary 3.4](https://arxiv.org/pdf/math/9511209#page=8)
states that minimal positive zero sums over mu_m are rotated prime
cycles. Decompose any positive zero sum into such minimal sums.
For a zero sum of length q+3, the only nonnegative solution of
`3u+qv=q+3` is u=v=1. Thus each pair of orthogonal columns gives
exactly one rotated 3-cycle and one rotated q-cycle, as a multiset.

Two consequences are needed. First, each of those cycles lies inside
one coset of mu_(3q) in mu_m. Its coset has multiplicity three or q;
if the two cosets coincide, all q+3 terms lie in that one coset.
Second, a single root has multiplicity at most two in the zero sum.
Each individual prime cycle has no repeated root, so their union
cannot contain a root three times.

This use of the classical theorem is explicit. The new argument below
concerns simultaneous columns; the cycle classification is not claimed
as new theory.

## 2. Every nonconstant quotient column uses the same three rows

Multiply rows to make the first column constant one. Work in the
additive quotient group

```text
K = mu_m / mu_(3q).
```

Its order is `3^(a-1) q^(b-1)`, which is odd. By Section 1, each column's
quotient entries are either constant or have two values with counts
three and q. A column phase makes the value on q rows zero. A
nonconstant column then has the form `t 1_S`, where t is nonzero in K
and S is a three-row subset. A constant column can be made identically
zero in the quotient.

Suppose two nonconstant columns have different subsets S,T. Put
`k=|S intersection T|`, so k is 0,1 or 2. Their quotient difference has
these values and multiplicities before coincident values are combined:

| Row region | Quotient value | Multiplicity |
| --- | --- | --- |
| Outside S and T | 0 | q-3+k |
| S only | t | 3-k |
| T only | -u | 3-k |
| Intersection | t-u | k |

Here t,u are nonzero. If k>0, the only possible equalities between the
four values are t=u or t=-u. These cannot both hold in an odd-order
group. At least three distinct values therefore remain, contrary to
Section 1.

If k=0, there are three occupied values unless t=-u. In that exceptional
case there are two, with multiplicities q-3 and six. They cannot be
three and q for a prime q>=5: that equality would require q=6. Nor
is the quotient difference constant. This is again impossible.

Thus all nonconstant quotient columns have one common three-row subset
S. Every quotient column is `t_j 1_S`, allowing t_j=0 for the constant
columns. If no nonconstant quotient column exists, column phases
already place every entry in mu_(3q), and the theorem follows.

## 3. An essential higher phase permits at most three columns

Assume that a nonconstant quotient column exists. The first column has
t_j=0, so there are at least two distinct quotient values among columns.
Partition the columns by t_j.

For columns in different parts, their quotient difference has value
`t_j-t_k` on S and zero on the other q rows. The two cycles in their
inner product must therefore be supported separately: the 3-cycle is
on S and the q-cycle is on its complement. In particular, their
restrictions to S are orthogonal in C^3.

Now take two columns x,y in the same part, and choose a column z from
a different part. The three coordinate ratios x/z form a rotated
3-cycle, and so do y/z. After their scalar factors are removed, each
is a permutation of `(1,omega,omega^2)`. Up to scalar, such permutations
lie on only two lines:

```text
span(1,omega,omega^2),   span(1,omega^2,omega).
```

These lines are orthogonal. Multiplication by the unit-modulus entries
of z preserves this conclusion. Therefore x and y restricted to S are
either proportional or orthogonal.

They cannot be proportional. If they were, the three terms of their
inner product on S would be exactly the same root. The complete
q+3-term zero sum would then contain that root at least three times,
contrary to Section 1. Hence x and y are also orthogonal on S.

All column restrictions to S are consequently pairwise orthogonal
nonzero vectors in C^3. There can be at most three columns. This
contradicts the hypothesis of at least four and proves the theorem.

## 4. The four-column threshold is sharp

Suppose m>3q and write eta for a primitive m-th root, omega for a
primitive cube root and zeta for a primitive q-th root. The following
(q+3)-by-3 matrix has columns indexed by j=0,1,2:

```text
first three rows: H_rj = eta^j omega^(rj),       r=0,1,2,
last q rows:      H_rj = zeta^(rj),             r=0,...,q-1.
```

Any two columns are orthogonal on each block separately. Their
nonzero index differences are one or two, so both geometric sums
vanish. All column norms squared are q+3.

Use the first row of each block and columns zero and one. Their
multiplicative cross ratio is eta, which is not in mu_(3q).
Cross ratios are unchanged by row and column phases. Thus this
three-column matrix cannot descend to the smaller alphabet, even
if arbitrary unit-modulus row and column phases are permitted.
This gives a uniform counterexample to a three-column version of
the theorem. The requirement of four columns is substantive.

## Evidence and limits

The complete source capacity verifier runs unchanged, including its
full 95-vertex extension graph, triangle exclusion, attaining matrix
and nested predecessor checks. All 28 retained files are authenticated.
The new checker uses only exact integers and cyclotomic polynomial
reduction. It checks:

- 10,272 canonical intersection/group cases and 173,600 full subset-pair
  cases for the quotient collision lemma. A composite-q=6 pattern
  exhibits the excluded multiplicities three and six.
- All prime-cycle pairs in alphabets of orders 15,45,75,225 and
  21,63,147,441: 14,400 pairs. Their quotient counts and maximum root
  multiplicity agree with the proof. This is the complete cycle-pair
  family in those alphabets, not an exhaustive search of arbitrary
  root multisets without the classical theorem.
- Every normalized three-root zero sum in these eight alphabets, by
  exact basis lookup. Each alphabet has exactly the two displayed
  normalized Fourier triples. All line-pair inner products agree.
- The explicit three-column matrices and their nontrivial higher-phase
  cross ratios, plus four-column attainment over each 3/5 alphabet.
  Full row/column phase changes dephase exactly to the source matrix.
  In total, 200 exact Gram entries are checked.

The all-prime/all-power statement is a written proof using the cited
classical theorem. The finite checks do not enumerate all matrices or
replace that theorem. The source capacity result remains a finite
certificate rather than a formal proof-kernel artifact. Other row counts,
a third prime divisor, approximate orthogonality, full equivalence
classification, native preparation and complete caller prices remain
outside the result. No selected cold replay, Lean, Docker, independent
human acceptance or formal-kernel acceptance is claimed. All five
framework assumptions and the selected frontier remain unchanged.
