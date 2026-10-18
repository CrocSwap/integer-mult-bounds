# One-slack workspace compression in the UT4 model

**Uniform scoped theorem; no new construction or kappa.** The new result is
workspace compression near the retained call lower bound. It uses the span
and quotient lemmas of @ToikY's [PR1662](https://github.com/CrocSwap/integer-mult-bounds/pull/1662),
pinned at `01cc02b164ecc4f9d84df3f56a1fe65b88daf390`.

## Model and normalization

All scalar coefficients and ranks are over F2. Let `G=UT4(F2)`, with
`a=I+E12`, `b=I+E23`, `c=I+E34`, and central `z=I+E14`.
Work in the full formal algebra `R=F2[G]`. For every finite `r>=w>=2`, a
paid factor is `D_N(g)=I_r+([g]+1)N`, where `g in {a,b,c}` and
`N=x y^T` for nonzero binary r-vectors x,y. Idempotent and nilpotent
rank-one couplings are both admitted. Count every paid occurrence at unit cost.
The required endpoint is `T=I_r+([z]+1)P`, `P=diag(I_w,0)`.
Every role has arbitrary input; the extra r-w roles must be restored exactly.

Scalar GL_r(F2) maps may be free. Move them to one end by conjugating paid
couplings, which preserves their nonzero rank one and their labels. Augmentation
`[g]->1` sends every paid factor and T to identity, so the remaining free map
is identity. We therefore analyze a normalized paid word without changing its
count or endpoint. There are no other free address operations, clean workspace,
higher-rank paid couplings, COPY or ERASE. All equalities below are formal
operator equalities, not agreement only on inputs with zero extra roles.

## Retained span premises

For label g, let X_g collect its column vectors and Y_g its row vectors:
X_g is r by n_g and Y_g is n_g by r. Write u_g=rank(X_g), v_g=rank(Y_g).
The first-order coefficient gives `X_g Y_g=0`, hence `n_g>=u_g+v_g`.
The fixed degree-three quotient used in PR1662 is

`Q=F2<a,b,c>/(a^2,b^2,c^2,ac-ca,all monomials of degree>=4)`.

Here a,b,c are augmentation variables: group generators map to 1+a,1+b,1+c,
and z maps to `1+abc+acb+bac+cba`. The unchanged pinned quotient implementation
replays all 4096 group products and 4913 basis associativity triples. This is
a fixed-group homomorphism certificate; it does not enumerate r,w or word lengths.
Each of these four target coefficients is P. Ordered scalar expansion gives:

| Coefficient | Target containment forced by its first/last scalar factor |
|---|---|
| abc | im(P) contained in im(X_a); row(P) contained in row(Y_c) |
| cba | im(P) contained in im(X_c); row(P) contained in row(Y_a) |
| bac, combining BAC and BCA | im(P) contained in im(X_b) |
| acb, combining ACB and CAB | row(P) contained in row(Y_b) |

No scalar matrices are commuted when the address monomials combine.
Consequently all six ranks are at least w. To recall the stronger middle bound,
number b factors and let A_j be the sum of preceding a couplings and C_j the
sum of following c couplings. Set X=X_b, Y=Y_b, `U=[A_j x_j]`, and let V
have rows `y_j^T C_j`. The B, AB, BC and ABC coefficients give
`XY=UY=XV=0`, `UV=P`. The last map factors through `ker(X)/im(Y)`, of dimension
`n_b-u_b-v_b`; therefore `n_b>=w+u_b+v_b`. These are inherited premises.

## New one-slack theorem

For every normalized legal word of length L with endpoint T, if `L<=7w+1`,
there is a legal word on exactly w roles with endpoint `[z]I_w` and length
at most L. More precisely, all normalized couplings share at least one orientation:

`N P=N for every factor`, or `P N=N for every factor`.

**Proof.** Summing the retained per-letter inequalities gives

`L=n_a+n_b+n_c >= w+sum_g(u_g+v_g) >= 7w`.

All ranks are integers. Thus their total excess over w is at most one.
At most one of the six spans can have dimension w+1; every other span has
dimension w and, by containment, equals the corresponding target span.
If the exceptional span is a column span, every row span equals row(P).
Thus each y satisfies `y^T P=y^T`, giving `N P=N` for every factor.
If it is a row span, every column span equals im(P), giving `P N=N`.
If no span is exceptional, both conclusions hold. The orientation is common
to the whole word, not chosen separately at each factor.

Split roles as the active w roles followed by the extra r-w roles. In the
first case each paid factor is block lower triangular; in the second it is
block upper triangular. On either common block-triangular algebra, projection
pi to the active corner is multiplicative, including over the noncommutative
ring R: the discarded cross-block product is zero. Therefore
`pi(product D_N(g))=product pi(D_N(g))=pi(T)=[z]I_w`.
Each projected coupling is the outer product of the active components of x,y,
so it has rank one or zero. Retain the former and discard zero identity factors.
This produces the claimed legal word. Each label count can only decrease;
no new preparation, inverse or restoration factor is introduced. This proves
the theorem for arbitrary extra-role inputs, using the full endpoint premise.

## Two-target optimum is independent of workspace

Let C_r be the minimum unit paid count for two targets and r>=2 roles.
Embedding a two-role word gives `C_r<=C_2`. The retained lower bound gives
`C_r>=14`, and `(abcb)^2=z` on each target gives `C_2<=16`.
If `C_r<C_2`, then `C_r<=15`; the new theorem compresses such an optimal
r-role word to two roles, implying `C_2<=C_r`, a contradiction. Hence

`C_r=C_2 in {14,15,16} for every finite r>=2`.

This does not decide which value occurs or provide a 14/15-call construction.
It does not claim that every 16-call word compresses. Optimal weighted tariffs
are outside this corollary: a cheaper weighted word may have more than 15 calls.
Physical/compiler/hosting, precision/tape, analytic transfer and proof-kernel
verification remain outside this formal-model theorem; the selected frontier is unchanged.

Credit @ToikY/PR1662 for the UT4 span and quotient machinery, steph4n-gh/PR1573
for the UT3 all-register rank method, Arham Tahir/PR1589 for nilpotent couplings,
and Hanson Sun (@bbMisk)/PR1607 for mixed-target coefficient spans. Their
retained source lineage remains credited. Prepared for @ToikY with substantial
OpenAI Codex assistance. Separate AI checks are not independent human review.
New work is Apache-2.0.
