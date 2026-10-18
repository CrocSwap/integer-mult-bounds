# Six coordinate-sensitive simplex exclusions

## Statement and geometric premises

Use the pinned P112 root representatives `r_t` and binary labels `ell(t)`.
Over any characteristic-zero field `K`, define

```
C = {c_h : c_h(t) = <r_t,h>, h in K^8},
w(q) = rank_F2 {ell(t) : q(t) != 0}.
```

For each `b=6,7,8`, no `b+4` independent pieces spanning `T` can satisfy
`dim(T intersect C) >= b` if their weights are bounded by either

```
3,5,5,5,6^b   or   4,4,5,5,6^b.
```

Here `6^b` means `b` pieces of weight at most six. These are six named
profiles in the pinned TWOSIDE `(b,t)=(6,4),(7,4),(8,4)` residues. This
statement does not assert that those entire cells, C5 or the decoder floor
are settled.

The retained [root-simplex proof](vendor/ROOT-SIMPLEX-PROOF.md) and
[larger-simplex proof](vendor/LARGER-SIMPLEX-PROOF.md) supply these premises:

- A support of binary weight `w=3,4,5,6` has at most `4,8,12,20` live lines.
- The evaluation code `C` has dimension eight and minimum support size 53.
- Every nonzero codeword with support below 70 is proportional to a root
  codeword.
- For an affine root simplex with `n` vertices, each live coordinate meets
  at most `M_n=max(2n-3,floor(n^2/4))` edge supports.

The replay reconstructs all roots and labels, all 4,097,782 five/six-flat
kernels, 960 simple reflections and 7,140 root planes. The written
geometric argument uses the standard Weyl-chamber theorem. Every six-node
parabolic has at most 36 root lines. Of the eight seven-node parabolics,
only the 63-line E7 system can contain 43 perpendicular live roots, and
its normal is a root. Root directions have live supports 53 or 56.
The same argument gives distance 53.

For a field-valued direction, the rational roots perpendicular to it have
rank at most seven. If at least 43 live roots are perpendicular, their rank
cannot be at most six, by taking a generic real normal and using the
36-line bound. Their rational kernel is thus one-dimensional. This extends
the root classification to `K`. The root-plane argument below also extends
by solving a nonsingular rational coordinate minor. The executable checks
the finite premises, not the Weyl-chamber theorem or a formal proof kernel.

## Quotient normalization

Choose the three small pieces of weights `3,5,5` in the first profile, or
`4,4,5` in the second. Let `S` be the union of their supports. Both give
`|S|<=28`. The remaining pieces `q_0,...,q_b` have weights `5,6^b`, so

```
U = sum_i |supp(q_i)| <= 12+20b.
```

Put `D=T intersect C` and consider `lambda:T -> T/D`. Its dimension is at
most four. The three small pieces together with any `q_i` have support at
most `28+20=48<53`. Their images are independent, since a dependence would
produce a nonzero codeword supported on fewer than 53 lines. Therefore
`dim(T/D)=4`, and modulo the three small images every `q_i` has a nonzero
image in a one-dimensional quotient.

Rescale the `q_i` to have the same image there. Supports and piece
independence are unchanged. There are small-piece combinations `a_i` with

```
c_0=0,   c_i=q_i-q_0-a_i in D, i=1,...,b.
```

The `c_i` are independent, by their distinct unit coefficients on the
independent pieces `q_1,...,q_b`. Every edge `c_i-c_j` is nonzero and has
support at most `28+20+20=68<70`. Every edge is a root direction.

Injectivity of `h -> c_h` gives independent `h_i` with `c_i=c_{h_i}`.
The root-plane property forces a common scalar `z` and signed roots
`alpha_i` with `h_i=z alpha_i` and `<alpha_i,alpha_j>=1` for distinct
indices, after normalizing squared root norm to two. Thus the `n=b+1`
vertices form an affine root simplex. This is the same quotient and
root-simplex step as PR3170; no new independence premise is assumed.

## New coordinate count

For any `n` scalar values with exactly `k` nonzero entries, the number `F`
of unequal unordered pairs satisfies

```
F <= k(n-k) + k(k-1)/2 <= (n-2)k + 1.
```

The first bound counts all zero/nonzero pairs and, favorably, every pair
of nonzero entries. Subtracting the middle expression from the last gives
`(k-1)(k-2)/2`, which is nonnegative for every integer `k>=0`. The additive
one cannot be dropped: two distinct nonzero values and `n-2` zeros give
`F=2n-3`. This inequality needs no root or ordering assumption on the
values. The replay separately checks all 142,139 equality patterns of six
through nine values together with a distinguished zero.

At a coordinate outside `S`, the edge evaluations are `q_i(t)-q_j(t)`.
Apply this inequality there and sum. Inside `S`, use the root-simplex
coordinate cap `M_n`. With `L=112` live coordinates and `E=n(n-1)/2` edges,

```
53E <= M_n |S| + (n-2)U + (112-|S|)
     = 112 + (M_n-1)|S| + (n-2)U.
```

All coefficients of the support upper bounds are nonnegative. Substitution
therefore only weakens the contradiction:

| b | n | M_n | S cap | U cap | Required incidences | Upper bound | Margin |
|---|---|---|---|---|---|---|---|
| 6 | 7 | 12 | 28 | 132 | 1113 | 1080 | 33 |
| 7 | 8 | 16 | 28 | 152 | 1484 | 1444 | 40 |
| 8 | 9 | 20 | 28 | 172 | 1908 | 1848 | 60 |

Each row applies to both profiles. All six are impossible over `K`.

The older count `53E <= M_n |S|+(n-1)U` gives margins `-15,-28,-28`
and does not exclude them. The six-vertex specialization of the new count
is PR3169's `795<=112+8s+4U`; that predecessor is credited, not claimed as
new here. The advance is its larger-simplex generalization and these six
applications.

## Source residue and overlap boundary

The unchanged original `bk2b.py` reproduces the 24-cell source table.
An independent transcription checks the six profiles against the original
69,154,251 survivors. The historical source filters are inherited; this
package proves a direct conditional piece theorem, not their completeness.

Every weight-certified four-piece quotient basis is checked by exhaustive
two-six-flat packing with paid cuts. The smallest deletion allowance
certified from these weight capacities alone is sixteen for all profiles.
A nonbasis rank-four anchor is absent in the first profile; for the second
its smallest certified allowance is twenty. The pinned eight/ten-deletion
bounds and twelve-deletion/rank-four-anchor theorem therefore do not certify
these cases by that weight-only route. These allowances are not lower
bounds on actual deletion sets. Support overlaps may reduce the actual
cost, and other geometric covers or proofs are not excluded.
PR3170's `2,5^3,6^b`, PR3169's `(5,5)` profiles and PR3171's `4,5^9`
independence result are distinct. No complete current residue count is
claimed after combining all pending work.
