# Distinct nondegenerate lines in a three-dimensional space

Let `F` be any field and let `B` be a nondegenerate symmetric bilinear form
on `F^3`. Choose finitely many distinct lines `E_i`, each nondegenerate for
`B`. Permit a scalar decoder's off-diagonal fitting entry only when the two
complete lines are orthogonal.

Two distinct lines span dimension two. Their common perpendicular space
has dimension one, so they have at most one common orthogonal line among
the chosen ports. Consequently the undirected orthogonality graph is
`C4`-free, including for indefinite symmetric forms and in characteristic
two whenever the stated nondegeneracy hypotheses hold.

The coefficient field matters. For fitting matrices **over the complex
numbers**, the source-derived rank lemma in [the parent audit](README.md)
therefore gives `rank_C(M)>V/4`. It does not require a positive-definite
label form or a symmetric fitting matrix.

Suppose the native accounting uses `h=3,k=1`, each scalar query carries one
total, and its tariff is the rank over `F` of the pairing between the
complete source and reader support spans. Zero-tariff terms can be deleted
without changing the fitting conditions. The remaining number of queries
exceeds `V/4`, and each has integer tariff at least one. Keeping the separate
public legs of the three-stage model forces

```
M(1/9) > 3*(2/7)^(8/9) + (3/8)*(1/7)^(8/9)
        = 1.051658213344872081... > 1.
```

This is the already verified parent-package gate; no new numerical
approximation or enumeration is needed. A restriction-of-scalars model
with `h=3k` has the same conclusion if every nonzero support pairing tariff
is at least `k`, as proved there for full finite-field lines.

This is a conditional obstruction in the stated **complex scalar decoder**
model. The graph fact holds over any label field, but the fitting-rank proof
uses complex absolute values, positive scaling and a Hermitian Gram matrix.
It therefore does **not** imply the same rank lower bound for fitting
coefficients over `F2`, including binary bit decoders on indefinite rational
label geometries. Repeated copies of one geometric line also require a new
argument: the distinct-line hypothesis is essential to the common-neighbor
bound. A different tariff or a query serving several independent totals
changes the stated native model.
