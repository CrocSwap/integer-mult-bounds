# Exact cost 64 for masked root-star decoders on P112

This closes the assembly question in Aaron Wang / Navinor's
[PR1226](https://github.com/CrocSwap/integer-mult-bounds/pull/1226), at
`8b10989e4e45f0f9ce41004d7898a21a32f87e11`. Its averaged frame bound is
`784/13`; the joint frame constraints below force **64**, and the existing
coordinate decoder attains 64. The proof does not invoke pending rank-eight
rigidity claims, root-hyperplane classification, or a coefficient search.

## 1. Exact model and statement

Take the 120 real E8 root lines, represented by roots of squared norm two:
the lines of `(+/-1,+/-1,0,...,0)` and of
`(1/2)(+/-1,...,+/-1)` with an even number of minus signs. Let `F0` be the
eight mutually orthogonal lines represented by
`e_(2j)+e_(2j+1)` and `e_(2j)-e_(2j+1)`, for `j=0,1,2,3`.
The live set `L` is their 112-line complement.

Write `G_ij = <r_i,r_j>` and `N_ij = (G_ij+1) mod 2`. The required masked
entries are the diagonal and the orthogonal pairs (`N_ij=1`). An exact
masked decoder satisfies

```
sum_k d_k(i) t_k(j) = 2 G_ij whenever N_ij = 1.
```

Transpose is ordinary transpose. Coefficients may be arbitrary real or
complex numbers. The cost of a term is
`beta_k = rank_F2 N[R_k,A_k]`, where `R_k` and `A_k` are its **actual
nonzero supports**.

For each of the 120 normal lines `alpha`, define

```
C(alpha) = {i in L : <r_i,alpha> != 0},
N(alpha) = C(alpha) minus {alpha}, if alpha is live; otherwise C(alpha).
```

**Theorem.** Suppose each paid term's two supports each equal one of
these 240 listed supports. The decoder may have any finite number of paid
terms, and may additionally use arbitrary cost-zero terms. Then
`sum_k beta_k >= 64`. Equality is attained.

The repeated supports for the eight punctured normals are intentionally
retained in the 240-entry list. Arbitrary *subsets* of the listed supports
are not included. Nor does the theorem cover unions of stars, other
punctures, shared-copy pricing, or a different label pairing.

## 2. Finite geometric facts

Both checkers construct the root set and the pairing from their definitions;
neither imports a predecessor implementation or trusts its receipt.
The primary checker records a complete exact census in `CERTIFICATE.json`.

1. Every support-pair cost is 7, 8 or 9. Among the 57,600 ordered pairs,
   the counts are respectively 7,616, 37,440 and 12,544. Cost seven occurs
   **exactly** when both supports equal their self-trimmed versions and
   the normals have odd inner product. Consequently a cost-seven atom
   has at least one live normal: the eight punctured normals are mutually
   orthogonal.
2. There are 1,260 live orthogonal frames of eight lines. Every live line
   belongs to 90 of them. Every pair of distinct orthogonal live lines
   belongs to a live frame: 2,856 unordered pairs belong to ten frames
   and 448 belong to fifteen. These are all 3,304 orthogonal pairs.
3. A support `C(alpha)` meets every live frame. A support `N(alpha)` misses
   precisely the live frames containing `alpha`, with no misses if
   `alpha` is punctured.

Fact 3 also has a direct proof. If a live frame contains `alpha`, its other
seven lines are orthogonal to `alpha`, and the self-line has been removed.
Conversely, if a frame avoids `N(alpha)` and does not contain `alpha`, all
eight members would be orthogonal to the nonzero vector `alpha`, impossible
because the frame spans real eight-space. The same spanning argument
proves the assertion for `C(alpha)`.

The complete support-pair census establishes Fact 1 without assuming that
the arbitrary decoder coefficients are root-linear. The geometry concerns
supports only. Frame enumeration establishes Fact 2 by checking exact
integer dot products and counting every increasing eight-clique.

## 3. Nine pairwise odd root lines are impossible

Here is a short proof independent of the finite clique search. Suppose
nine roots `v_1,...,v_9` in rational eight-space have squared norm two and
all distinct-pair inner products odd (therefore `+1` or `-1`). Choose a
primitive integer dependence `sum_i c_i v_i=0`; one exists because there
are nine rational vectors in eight dimensions. Its coefficient vector
is not zero modulo two.

The Gram matrix modulo two is `J+I`, the 9-by-9 matrix with zeros on the
diagonal and ones elsewhere. Its kernel consists exactly of the constant
vectors: `x_i=sum_j x_j` for each `i`. Thus every `c_i` is odd. But

```
0 = (1/2) ||sum_i c_i v_i||^2
  = sum_i c_i^2 + sum_(i<j) c_i c_j <v_i,v_j>
  = 9 + 36 = 1  (mod 2),
```

a contradiction. This argument is about the real rational roots, even
when the decoder coefficients are complex.

As a separate finite check, the primary verifier enumerates all cliques
in the live nonorthogonality graph. The counts at sizes zero through
eight are
`1,112,2912,25088,88704,161280,145152,55296,4032`; there is no size-nine
clique. The independent verifier uses a quadratic form over F2 instead
of this clique search. It constructs root residues in a nondegenerate
eight-dimensional quadratic space, verifies every root has quadratic
value one, and checks the polar form against every root inner product.
Nine hypothetical pairwise-odd residues have Gram rank eight, hence span
the space. Their sum pairs to zero with every residue, so is zero, but
polarization gives its quadratic value as `9+36=1`, a contradiction.
The written integer-dependence argument above does not depend on either
finite computation being treated as a universal graph theorem.

## 4. Frame-rank demand and simultaneous misses

Restrict the masked identity to a live frame `F`. Its right side is
`4 I_8`, of rank eight over either real or complex scalars. Every paid
term contributes a rank-at-most-one outer product and contributes zero
if either support misses `F`. Thus **at least eight paid terms must meet
every live frame on both sides**.

A cost-zero term cannot help: its support-pair matrix `N[R,A]` is zero.
Every entry within a frame has `N_ij=1`, so its outer product vanishes
on the entire frame block. This also covers arbitrarily many free
singleton corrections on odd pairs.

For each cost-seven atom choose one live normal `a` supplied by Fact 1.
Fact 3 says that atom misses all 90 frames containing `a`. Suppose nine
cost-seven terms met every frame at least eight times. No frame could
be missed by two terms. Their chosen live normals would therefore be
distinct, because a repeated normal has a frame through it. They would
also be pairwise nonorthogonal, because Fact 2 supplies a frame through
any orthogonal pair. We would obtain nine pairwise odd root lines,
contradicting Section 3.

This proves the missing joint constraint. Average hit counts do not
detect it: an atom can meet 1,170 frames, as PR1226 correctly records,
while its omitted frames are incompatible with the other eight atoms.

## 5. Exhaustion by term count and sharpness

Let `m` count paid terms only. A hypothetical cost below 64 is impossible
in each case:

| Paid terms | Reason |
|---|---|
| `m <= 7` | A frame needs eight nonzero rank-one contributions. |
| `m = 8` | All eight must meet every frame. A cost-seven term misses a frame, so every term costs at least eight. |
| `m = 9` | Each costs at least seven; total below 64 forces all nine costs to be seven. Section 4 excludes this. |
| `m >= 10` | The total is at least `7m >= 70`. |

For sharpness, retain the known coordinate decoder indexed by `f in F0`:
`d_f(i)=t_f(i)=<r_i,f>`. Since `F0` is an orthogonal norm-two basis,

```
sum_(f in F0) <r_i,f><r_j,f> = 2<r_i,r_j>.
```

Its eight support pairs each have cost eight. Both checkers test the
complete all-pairs identity and the cost 64. Sharpness is credited to
the existing coordinate construction, not a new supplier.

## 6. Consequences and limits

The result upgrades PR1226's interval `[784/13,64]` to the exact minimum
64 for its stated root-star family, including mixed costs, arbitrary
term counts and arbitrary real or complex coefficients. In particular,
none of its nine-term cost-seven leads can be assembled into an exact
masked decoder. It does not establish a cost floor for general supports.

No physical word, new kappa, owner map, or supplier admission follows.
Extra centre reads, frame travel and dirty restoration were already
ignored in the favorable decoder budget; they cannot rescue the claimed
decoder-only saving within this model. All-size/compiler, realization,
hosting, precision/tape, analytic transfer and bit-interface obligations
remain unchecked and unchanged. This is a written scoped proof backed
by exact finite checks, not formal verification of integer multiplication.
