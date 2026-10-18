# One free rectangle cannot improve a single P112 coordinate term

This is a scoped COPY-cost obstruction, with exact finite geometric premises.
It concerns the fixed PR717 P112 model and arbitrary complex coefficients with
ordinary transpose. It is neither a supplier construction nor a multiplication
theorem. Arham Tahir, with substantial OpenAI Codex assistance; Apache-2.0.

## Model and statement

Let `R` be the 112 live E8 root lines after removing the standard orthogonal
eight-frame, in the model pinned by SOURCES.json. Write `X` for its 112 by 8
coordinate matrix, with entries in `{0,1,-1}` and `XX^T = 2G`.
The binary label pairing is

`B_ij = (G_ij + 1) mod 2`.

It is one on the diagonal and on orthogonal root pairs, and zero on odd pairs.
For supports `A,C`, write `rho(A,C) = rank_F2 B[A,C]`. A scalar outer-product
term `d t^T` costs `rho(supp(d),supp(t))`; coefficients determine supports,
but they are not reduced modulo two. This is the separate-term copy-rank
convention of PR717/PR968, granted as the algebraic objective here.

Choose any original coordinate column `x = X[:,k]`, with support `C`.
Let `u,v` be arbitrary complex vectors such that

`B[supp(u),supp(v)] = 0`.

Thus `uv^T` costs zero and vanishes on every constrained even entry. Adding
it to `XX^T` gives a valid masked decoder. Its entries on odd pairs may change.
Neither vector must be root-linear; their supports may be arbitrary subsets.
Zero vectors are allowed.

For arbitrary `M in GL(2,C)`, replace the two factors by

`[d1,d2] = [x,u] M`, `[t1,t2] = [x,v] M^(-T)`.

**Theorem.** The replacement costs satisfy

`rho(supp(d1),supp(t1)) + rho(supp(d2),supp(t2)) >= 8`.

The other seven coordinate terms each cost eight, so the entire decoder has
COPY cost at least 64. Equality is attained by `M=I`, including a genuinely
rank-nine masked decoder obtained from an odd singleton correction.

For nonzero `u,v`, if both products of original-coordinate coefficients are
nonzero, each replacement costs at least six; their sum is at least twelve.
This lower bound of twelve is not asserted sharp.

## Exact finite premises

The nine-dimensional binary label space has a nondegenerate symmetric form.
For each of the eight coordinate stars `C`:

1. `|C|=56`; its labels span an eight-dimensional space `H`.
2. `rho(C,C)=8`, so the form restricted to `H` is nondegenerate.
3. For every live root `j`, the subset
   `E(C,j) = {i in C : B_ij=1}` has label span dimension **seven**.

`verify.py` reconstructs the doubled Euclidean roots independently and binds
all 12,544 binary pairings and coordinate columns to the pinned PR845/PR717
geometry. It checks all 896 slices and records a seven-row basis for each.
The dimensions and all support masks are stored in CERTIFICATE.json.
The distinct replay `independent_check.py` uses the predecessor's explicit
nine-bit labels and a different binary elimination direction.

The cross-pair census checks all 100,352 ordered pairs of slices within one
coordinate star. Their pairing rank is at least six. Some have rank exactly
six: neither an eight-dimensional slice nor a seven-rank cross-pair bound is
available. The quantified proof below needs only premises 1–3, rather than
assuming the exhaustive slice pairs enumerate arbitrary free rectangles.

No hyperplane-flat classification, global masked rigidity, or pending PR
theorem is required for these finite premises.

## Dense survivor lemma

Put `U=supp(u)` and `V=supp(v)`, and suppose both are nonempty.
The free-rectangle condition implies, for any `j in V` and `i in U`,

`E(C,j) subset C minus U`, `E(C,i) subset C minus V`.

Both survivor label spaces therefore have dimension at least seven and are
subspaces of the same eight-dimensional nondegenerate space `H`.
For subspaces `A,Z` of `H`,

`rank(pairing A x Z) >= dim(A)+dim(Z)-dim(H)`.

Indeed, the kernel on `A` is `A intersect Z^perp`, whose dimension is at most
`8-dim(Z)`. Consequently

`rho(C minus U,C minus V) >= 6`.

This applies to every free rectangle, regardless of its cardinality,
coefficients, or whether it is maximal.

## Factor-change cases

Write `M=[[a,b],[c,d]]`, with `Delta=ad-bc != 0`. Then

`d1=ax+cu`, `d2=bx+du`,
`t1=(dx-bv)/Delta`, `t2=(-cx+av)/Delta`.

These preserve `d1 t1^T + d2 t2^T = xx^T+uv^T` identically.

**Two nonzero original-coordinate products.** If `ad != 0` and `bc != 0`,
each left support contains `C minus U` and each right support contains
`C minus V`. For nonempty `U,V`, the survivor lemma and rank monotonicity give
at least six for each term, hence at least twelve in total.

**Exactly one nonzero original-coordinate product.** At least one of `ad,bc`
is nonzero because their difference is `Delta`. When exactly one is nonzero,
we may swap the two output terms and/or transpose the whole factorization to
reduce to `b=0`, `a,d != 0`. These operations preserve all costs: `B` is
symmetric, and term order does not enter the objective. If `c=0`, the original
coordinate term remains and already costs eight. Suppose `c != 0`.
Let `A=supp(ax+cu)`. The first right support is exactly `C`. The second left
support is exactly `U`, and its right support contains `C minus V`.
Since `C subset A union U`, vertical stacking and rank subadditivity give

`8 = rho(C,C) <= rho(A,C)+rho(U,C)`.

The columns in `V` of the pairing on `U` are zero, so
`rho(U,C)=rho(U,C minus V)`. The two actual term costs dominate the two ranks
on the right. Their sum is at least eight.

**Zero outer-product boundary.** If `u=0`, every left factor is a multiple of
`x`. Discard the terms with zero left factor. The right supports of the
remaining terms cover `C`: on a row where `x` is nonzero, the identity
`sum d_l t_l^T = xx^T` forces at least one active right factor to be nonzero
at every column in `C`. Horizontal concatenation of these pairing submatrices
therefore gives total cost at least `rho(C,C)=8`. If `v=0`, transpose this
argument. This branch is essential: a dense `M` can have costs `(8,0)` when
the free outer product is zero. It must not be subjected to the twelve bound.

All cases prove the theorem over C. The finite Q(i) fixtures check the
ordinary-transpose formula and boundary handling; they do not replace this
quantified argument.

## Optimistic COPY moment screen

For any retained saving parameter `0<=a<1`, put `q=1-a in (0,1]`.
If `r1+r2>=8`, then

`r1^q+r2^q >= (r1+r2)^q >= 8^q`, with `0^q=0`.

Thus, with the same width, role normalization and common multiplicity for
these COPY children, the replacement cannot improve the COPY contribution
to the recursive moment, even granting all additional preparation, gathering,
frames and restoration zero expense. The unchanged seven copies cancel in
this comparison. This is an optimistic screen for this replacement only.
It does not price a new owner layout, changes in other children or denominators,
shared copies, other helper contracts, or an entire physical supplier.

## Limits and next step

Only one original coordinate term is mixed. Composing several such changes
can leave this family after the first step, so the theorem cannot be iterated
to assert a global local-search barrier. Mixing two or more original terms,
multiple independent free corrections, other punctures or support alphabets,
and nonseparate COPY accounting remain open. In particular, rank-nine masked
decoders and their complete cost optimization remain open in general.
The named next experiment and its blocker are in README.md/TASK.json.
