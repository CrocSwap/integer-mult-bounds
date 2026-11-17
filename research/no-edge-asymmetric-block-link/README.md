# A nonsymmetric link between two binary projector blocks

A rank-one idempotent with different image and covector supports joins two
fixed normal-form triples over F2 at width eight. Their complete pool contains
seven projectors, spans a five-dimensional off-diagonal pattern space with
no matrix unit, and acts irreducibly on its seven-dimensional joint image.
This scoped construction answers Open next question 3 of #7281.

## Proof

For a pattern space $P$, its complete pool consists of all rank-one
idempotents $ab^T$ with $b^T a=1$ and nonzero $\mathrm{off}(ab^T)$
in $P$. Here $\mathrm{off}$ clears the diagonal.

On coordinates 0, 1, 2, take $u=e_1+e_2$, $v=e_0+e_2$ and
$o=e_0+e_1+e_2$, with projectors $uv^T,\ vu^T,\ oo^T$. Repeat
on coordinates 3, 4, 5 by shifting the indices by three. Write $H$
for the off-diagonal span of the six projectors. We use the complete-pool
calculation for $H$ in #7281, Section 5, which identifies those six
projectors. Each block's off-diagonal patterns have weights
3, 3 and 6, with the first two disjoint and summing to the third. Hence
$H$ has dimension four and every nonzero element has weight at least
three.

Adjoin the link $L=xy^T$ with

$$
x=e_2+e_5+e_6,\qquad y=e_2+e_5+e_6+e_7.
$$

The overlap of their supports has size three, so $y^T x=1$.
Write $p=\mathrm{off}(L)$ and $P=H+\langle p\rangle$. Every nonzero
entry of $p$ lies outside the two internal block squares, and $p$
has nine entries. It follows that $P$ has dimension five, contains
no matrix unit, and every pattern in $p+H$ has the same row and
column at coordinate 6 as $p$.

**The link is the only projector above $p+H$.** Any lift $ab^T$ of a
pattern in $p+H$ has a nonzero off-diagonal row and column at 6.
The row forces $a_6=1$ and $b_j=y_j$ for $j\ne6$. The column
forces $b_6=1$ and $a_i=x_i$ for $i\ne6$. This fixes
$a=x,\ b=y$. Together with the pool of $H$, this identifies all seven
projectors. Six have images forming a basis on coordinates 0 through 5.
The link adds $e_6$ modulo that block span, so the joint image is
$V=\mathrm{span}(e_0,\ldots,e_6)$.

**The action on $V$ is irreducible.** Each block's three covectors are
dual to its three images, and all six covectors evaluate to 1 on $x$.
The link covector $y$ evaluates to 1 on each block image because each
image contains its block's hub. If a nonzero invariant subspace contains
a vector hit by $y$, it contains $x$, then all six block images and
thus all of $V$. Otherwise $y$ vanishes on the subspace and it
contains no block image. Invariance forces every block covector to
vanish there too. Their common kernel in $V$ is $\langle e_6\rangle$,
and $y^T e_6=1$, so this case gives the zero subspace.

The new covector uses coordinate 7 outside $V$. This gives an
asymmetric link in the coordinate model of #7281. The action on the
image has the same covector-image incidence as its square-link family,
since the additional covector bit vanishes on $V$.

## Evidence and scope

The verifier scans all 32,640 rank-one idempotents at width eight for
membership in this one pattern space. It checks its 31 nonzero patterns
and all 127 nonzero starting vectors in the joint image. The span of
the projector orbit of each starting vector is the joint image, which
checks irreducibility by direct iteration. Two controls delete the link
or remove its matched fresh covector bit.

From the repository root, with CPython 3.12 and the standard library:

```sh
python3.12 -I -B -W error -X dev research/no-edge-asymmetric-block-link/verify.py
python3.12 -I -O -B -W error -X dev research/no-edge-asymmetric-block-link/verify.py
python3.12 -B scripts/research_package.py --package research/no-edge-asymmetric-block-link
python3.12 -B scripts/check_research_commit.py --package research/no-edge-asymmetric-block-link --check-source-history
```

The direct verifier prints `PASS_NO_EDGE_ASYMMETRIC_BLOCK_LINK` with
`patterns=31 idempotents=32640 pool=7 image_dimension=7 spanning_orbits=127 controls=2`.

This is a side result on the binary pattern pools used in BIT relation
arguments. It answers an existence question with the two blocks fixed.
Classifying other nonsymmetric extensions, bounding arbitrary
five-dimensional pattern spaces, and realizing the pool by a paid word
remain open here. No new κ or supplier admission is claimed. No predecessor
verifier, selected scientific replay, Lean or Docker run is required by the
standalone check. Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Can one classify the nonsymmetric links on these blocks at arbitrary width?
Such a classification would separate links that merely change coordinate
supports from links that change incidence on the joint image. First fix a
nonzero fresh row and column and derive the constraints on the two block
restrictions. The present proof uses row and column 6 at the same coordinate,
so extensions without a shared fresh bit require a separate argument.

## Credit

This contribution was produced by Nick Petalas. Credit unpaidmoon for the
two-block model and square-link question in [#7281](https://github.com/CrocSwap/integer-mult-bounds/pull/7281),
the fresh-size-one construction in [#7237](https://github.com/CrocSwap/integer-mult-bounds/pull/7237),
and the normal-form triple and its lineage in [#6921](https://github.com/CrocSwap/integer-mult-bounds/pull/6921).
The complete-pool calculation in #7281 uses Nick Petalas's off-diagonal
fiber lemma from [#5921](https://github.com/CrocSwap/integer-mult-bounds/pull/5921).
The cited [proof for #7281](https://github.com/unpaidmoon/integer-mult-bounds/blob/0cd5324c41490b856d0e94daa8b011683fc153f6/research/no-edge-dim5-fresh-link/PROOF.md)
has SHA-256 `8b182a2dfe649d56af2efe0d6bfaa033a80b479cbbedd4c7fdbe4840daf7ea24`.
It is a mathematical reference. The verifier has no external source input.
The Git-provenance pins in [SOURCES.json](SOURCES.json) bind the task
catalogue and selected record at the base. Apache-2.0.
