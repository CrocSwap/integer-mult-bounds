# Sharp rank-five joint incidence in an E8 A2 fiber

Let R be the full 120 E8 root-line labels in the exact simple-root convention
of the pinned `geometry.py`. A root with integral simple-root coordinates
c has label `(1,c mod2)` in F2^9. The leading coordinate is the low bit.
Let A be any 27-line nonzero projective evaluation fiber of an A2 root plane.
For any binary linear space V of dimension at most five, define

```
m = |R intersect V|,     j = |A intersect V|.
```

**Theorem.** `m+j <=20`. Equality is attained. In particular every piece
whose support has binary rank at most five has total support plus its
singleton support in one such fiber at most 20. This improves the sufficient
bound 21 used by Nick Petalas's PR3257. It holds before the frame puncture
and any common cut. Taking subsets preserves the inequality.

This is a binary support lemma. Coefficients, characteristic-zero code
lifting, normalization of an arbitrary code plane, actual callers and the
complete decoder/supplier are separate questions. No shortening threshold,
physical invoice, selected frontier change or kappa follows here alone.

## Exact geometric binding

Put `G_ij = dot(s_i,s_j)/4` for the doubled simple roots s_i and define

```
q(x) = sum_i x_i + sum_(i<j) G_ij*x_i*x_j modulo2.
B(x,y) = q(x+y)+q(x)+q(y).
```

The norm identity gives `q(c mod2)=norm(sum_i c_i*s_i)^2/8 modulo2`.
The executable binds all 120 distinct root residues to precisely the 120
vectors with q=1, all 112 existing live labels, polar nondegeneracy and the
positive ambient Gauss sum `sum_x (-1)^q(x)=16`.

For **every** large A2 fiber A, write W=span(A). The replay checks the
following on all 3,360 distinct fibers from all 1,120 A2 planes.

- W has dimension seven, and R intersect W has 28 labels.
- The leading-one section of W is an affine six-space H.
- The restriction f of q to H has nondegenerate polar form and
  `sum_(x in H) (-1)^f(x)=+8`.

Completeness of the plane inventory does not require a Weyl transitivity
assumption. Every A2 plane has two nonorthogonal root lines; their unique
third line is their appropriately signed sum. The replay constructs each
plane from all 7,140 root-line pairs and partitions all 120 lines by their
exact two evaluations. Each plane has three 27-line fibers, three singleton
fibers and one 36-line zero fiber. It finds 3,360 distinct large fibers.

These are finite model-binding premises, checked exhaustively with exact
integers. The argument below proves the bound for all support spaces V,
including those outside W. It does not enumerate the 3,309,747 ambient
five-spaces. A separate implementation rebuilds the roots and labels and
checks the canonical extremal closures by five-label bases.

## A signed affine restriction lemma

Consider any affine quadratic function f on F2^n with nondegenerate polar
form B and positive Gauss sum `G=2^(n/2)`. Constants and linear terms in f
are allowed. Set `q_0(x)=f(x)+f(0)`. For a k-dimensional linear space L,
let R_0=L intersect L-perp be its polar radical, of dimension t. On an
affine translate a+L, put `S=sum_(x in L) (-1)^f(a+x)`.

Polarization and cancellation of nonzero linear characters give

```
S^2 = 2^k * sum_(h in R_0) (-1)^(q_0(h)+B(a,h)).
```

The radical character is linear. If nonzero, S=0. Otherwise
`|S|=2^((k+t)/2)`. Also `t<=n-k`, since the ambient polar form is
nondegenerate. The restriction polar rank k-t is even.

The sign matters when `k+t=n`. In that case L=R_0-perp. Set
`g(x)=q_0(x)+B(a,x)`. The zero radical character says g vanishes on R_0.
Every coset x+R_0 outside L has zero signed g-sum. Hence the sum of
`(-1)^g` over the ambient space equals its sum over L. Translation by a
and multiplication by `(-1)^f(a)` then give

```
S = sum_ambient (-1)^f(x) = +G.
```

The number of f=1 points is `(2^k-S)/2`.

## Two consequences

First recall the global rank-five capacity 12 of PR3269. A leading-one
rank-five label space has an affine section of dimension at most four
in the ambient q-space of dimension eight. Extend smaller sections to
affine four-spaces. At k=4 the possible polar ranks are 0,2,4. Rank 0 is
balanced, with eight ones, or has the positive extreme S=16, with zero
ones. Rank 2 gives at most 12 ones, and rank 4 at most 10. Thus every such
V has `m<=12`. This is the signed character-sum proof of PR3269, recalled
here so the present package has no pending executable or proof dependency.

Now apply the same lemma inside H of dimension six and Gauss sum +8.
For an affine four-space in H, t<=2. The polar rank is 2 or 4. At rank 2,
t=2 and k+t=6, so the restriction is balanced with eight ones or has
S=+8 with four ones. At rank 4, `|S|=4`, giving at most 10 ones. Therefore
**every affine four-space in H contains at most ten roots**. Smaller
affine spaces extend to four-spaces in H and satisfy the same bound.

The positive sign is essential. On F2^6 the nondegenerate function
`x0*x1+x2*x3+x4*x5+x4+x5` has Gauss sum -8. Its four-space x1=x3=0
contains 12 ones. The controls construct this counterexample explicitly.
Nondegeneracy alone would not prove the ten-point bound.

## Split the ambient support space

If V is contained in W, its leading-one section has affine dimension at
most four inside H. The preceding consequence gives `m<=10`. Since
A is a subset of R, `j<=m<=10`, so `m+j<=20`.

If V is not contained in W, `dim(V intersect W)<=4`. The leading-coordinate
functional either vanishes there, giving j=0, or its leading-one section
has at most `2^(4-1)=8` points. Thus `j<=8`. Combine this with global
`m<=12` to obtain `m+j<=20` again. This second case covers ambient
five-spaces that are not generated by fiber labels.

For an actual support T with span V, both its total support and its
singleton sites are subsets of R intersect V and A intersect V. The same
upper bound applies without requiring T to fill its binary closure.
A singleton projective fiber has j<=1 and m<=12, so it also satisfies 20.
Zero coefficient columns contribute no singleton sites.

## Attainment and limits

RESULT.json records a literal ten-label subset in the canonical 27-line
fiber. Its labels span a five-space, and its full E8 closure is precisely
those ten labels. Thus m=j=10. The canonical census checks all 2,667
five-spaces inside W and finds 216 such equality spaces. The separate
five-label reconstruction finds the same 216 equality closures.

The theorem is sharp for the full E8 configuration. Restricting to the
fixed P112 gives the same upper bound; no P112 sharpness claim is needed.
The proof is written mathematics with exact finite model binding. It is
not proof-kernel formalization or independent human review. Other code
planes, higher support ranks, physical port encodings, Weyl/chamber
normalization, shortening thresholds and full multiplication remain
outside this result.

Credit Nick Petalas's PR3257 at 1499da8f88c4d0293fe3ae443d0c7fec80f0e2d7
for the incidence 21 obligation, and PR3269 at
 ebe02d33157dc6c6d3b35df204e4a39242b7429e for the signed global 12 proof.
David Arias's retained quadratic model and the root-simplex/E8/P112 lineage,
including joaqcoo, and DreamingOfClouds's PR3154 motivation, retain credit.
No frozen predecessor is changed.
