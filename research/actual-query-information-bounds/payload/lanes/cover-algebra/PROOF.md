# Routed centre projections

This note studies the centre-free scalar interface in the campaign's
`circuit-interface/INTERFACE.json`. The source commit is
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The source file hash is
`5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3`.
The route construction is in `temporal-reuse/verify_routes.py`.
These files are campaign evidence. This note does not replace their independent
native-map reviews.

## Result and scope

Let `J_0` be the 112-port scalar interface. Let `J_s` be the same interface
in any positive-stage swap chart. On an arbitrary full regular cover,

\[
\frac{\operatorname{rank}(J_s-J_0)}{|G|}\geq\frac{2912}{183}.
\]

Here `G` is any finite cover group that contains the route matrices, and the
group acts by right translation on its full regular representation. The bound
also holds on a disjoint union of regular orbits, with the same normalization.
The chart can use any orthonormal basis of each port's orthogonal complement.
Thus the bound does not depend on the particular chart basis in the selected
supplier.

Any linear subspace on which `J_s` and `J_0` agree has at least this
codimension. This excludes a lossless common-`J` restriction. The bound alone
does not exclude an encoding with new state, a new child invoice, or a new
controller.

The exact selected charts also fail scalar Temperley--Lieb, commutation, and
the braid relation for `J_0,J_s`. The first two failures hold for every chart
basis in the stated swap-chart class. The braid witness below is specific to
the selected chart.

## Source facts

Write `R` for the 8 by 112 centre matrix, `A=R^T R`, and

\[
P=A/56,\qquad J=I-14P.
\]

The supplied exact scalar map proves `R R^T=56I`. Thus `P` is an orthogonal
projection of rank 8. The independent calculation in `verify_algebra.py`
also checks these facts about all entries of `A`:

* Each diagonal entry is 4.
* There are 5,824 nonzero off-diagonal entries. Each is 2 or -2.
* If `A_qp` is nonzero and `q` is not `p`, the binary port vectors obey
  `q^T p=0`.

It follows that `tr(A^2)=56 tr(A)=25088` and `tr(A)=448`.

## Route matrices and distinct edge products

Work on `L` direct sum `E_s`, where `L` has binary dimension 9 and `E_s`
has binary dimension 8. Both use the dot product. A port has `q^T q=1`.
Let the columns of `B_q` be an orthonormal basis of `q`-perp. The swap chart
has matrix

\[
\rho_q=\begin{pmatrix}q q^T&B_q\\B_q^T&0\end{pmatrix},\qquad
B_q^TB_q=I_8,\quad B_qB_q^T=I_9+q q^T.
\]

It is an orthogonal involution. Different ports have different routes,
because the local block is `q q^T`.

For a nonzero off-diagonal entry `A_qp`, the local block of the product is

\[
(\rho_q\rho_p)_{LL}=B_q B_p^T.
\]

Its kernel is the line spanned by `p`; its image is `q`-perp. Over the
binary field a nonzero line has one nonzero vector. The matrix therefore
determines both `q` and `p`. Consequently all 5,824 ordered edge products
are distinct. None is the identity. The products at `q=p` are all the identity.
This proof uses no choice of the bases `B_q`.

The checker verifies the rank, kernel, and image of every selected edge
product as a binary 17 by 17 matrix. It also verifies all 3,136
star-transposition identities over all 112 ports and all pairs of positive
stages. Those identities give the stated `S_9` stage action. They do not
give relations between the projections below.

## Two exact trace moments

Use the involution on the real group algebra that sends each group element
to its inverse. Set

\[
D=\operatorname{diag}(\rho_q),\qquad Q=DPD.
\]

Both `P` and `Q` are self-adjoint projections. For a group-algebra matrix,
let `tau` be the sum of the identity coefficients on its diagonal. On a
full regular cover this is the ordinary trace divided by `|G|`.

Because the routes are distinct, only equal port indices contribute to the
identity coefficient in `P Q`. Hence

\[
\tau(P)=\tau(Q)=8,\qquad
\tau(PQ)=\frac{112\cdot4^2}{56^2}=\frac47.
\]

An identity term in `(P Q)^2` must satisfy
`rho_b rho_c = rho_a rho_d`, with `A_bc A_da` nonzero. The edge-product
lemma gives exactly two cases:

* Both products are the identity: `b=c` and `a=d`.
* Both products are nonidentity: `b=a`, `c=d`, and `b` is not `c`.

The resulting coefficient sum is

\[
\begin{split}
\tau((PQ)^2)
&=\frac{16}{56^4}
  \left(\sum_{a,b}A_{ab}^2+\sum_{a\ne b}A_{ab}^2\right)\\
&=\frac{16(25088+23296)}{56^4}=\frac{27}{343}.
\end{split}
\]

This argument works in the full group algebra. It does not evaluate the
cover at a phase value or identify two different group elements.

## Rank bound and the equality subspace

Set `M=P-Q`. Cyclicity of `tau` and the projection identities give

\[
\tau(M^2)=16-2\tau(PQ)=\frac{104}{7},
\]

\[
\tau(M^4)=16-4\tau(PQ)+2\tau((PQ)^2)=\frac{4758}{343}.
\]

Let the nonzero real eigenvalues of `M` on the full regular cover be
`lambda_1,...,lambda_r`. Cauchy--Schwarz gives

\[
(\operatorname{tr}M^2)^2\le r\operatorname{tr}M^4.
\]

After division by the cover size,

\[
\frac{\operatorname{rank}M}{|G|}
\geq\frac{(104/7)^2}{4758/343}=\frac{2912}{183}.
\]

Since `J_s-J_0=-14(Q-P)`, the same rank bound holds for the routed
interfaces. It is additive on independent copies. A code on which these
two interfaces agree must lie in the kernel of their difference, so its
codimension is at least this rank.

One can also express the result as a bound on common centre information.
The normalized dimension of `im(P)` intersect `im(Q)` is at most `8/183`.
To see this, apply the nonnegative polynomial
`(t-13/196)^2/(1-13/196)^2` to `PQP` on `im(P)`. Each eigenvalue 1
contributes 1. The two trace moments give an upper bound `8/183`.

## Exact failures of smaller algebras

Use port index 0, whose binary label is 11, and port index 1, whose label
is 19. Let `g=rho_0 rho_1`. The edge-product lemma gives

\[
[g](PQP)_{00}=\frac{16}{56^3}=\frac1{10976}.
\]

Every scalar multiple of `P` has zero coefficient at this nonidentity
element. Therefore `P Q P=lambda P` fails for every scalar `lambda`.
This is a formal group-algebra counterexample.

At the same group element,

\[
[g](PQ-QP)_{00}=-\frac4{56^2}=-\frac1{784}.
\]

This failure also holds for every allowed chart basis. Indeed the first
term uses products `rho_i rho_0` and the second uses `rho_0 rho_i`.
On the nonzero off-diagonal support these ordered products are distinct.

For the selected chart, the checker gives a further group element with
coefficient `1/21952` in `(PQP-QPQ)_{00}`. Both `P` and `Q` have the same
diagonal entry, so the braid difference

\[
J_0J_1J_0-J_1J_0J_1
=14\cdot13(P-Q)-14^3(PQP-QPQ)
\]

has coefficient `-1/8` at this entry. Its full binary matrix is in
`ALGEBRA.json`.

The optional sixth-moment calculation retains every group coefficient of
`(R D R^T)^3`. It gives

\[
\tau((PQ)^3)=\frac{1609241}{120472576}.
\]

There are 314,608 contributing walks and 302,910 distinct group elements.
The exact coefficient sums give the stronger selected-chart codimension
bound `5763805736/360389295`. This stronger bound is not needed for the
basis-independent result. It has not yet received an independent replay.

## Reproduction and open next questions

From the workspace root, run:

```sh
python3 -I -B work/centre-encoding-campaign-20261014/lanes/cover-algebra/verify_algebra.py --interface work/centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json --out work/centre-encoding-campaign-20261014/lanes/cover-algebra/ALGEBRA.json --sixth-moment
```

The printed result is `PASS_EXACT_ROUTED_PROJECTION_ALGEBRA`.
The calculation uses one CPU and exact integer or rational arithmetic.

The next controller question is whether a word that revisits a physical
stage can use these larger algebras at a favourable full cost. A word that
uses each fresh external stage only once has a separate support obstruction:
an off-diagonal edge in stage `s` cannot fix `E_s` pointwise. Other stages
do fix `E_s` pointwise. The `encoded_controller` worker is checking the
bridge alphabet and the native-frame obligations for that argument.

The rank theorem also leaves encodings that add state or change recursive
children open. The `source_domain` worker is applying the bound to the
unchanged-child invoice. That application requires its own dimension count.

This work used AI assistance. It builds on the selected supplier and on the
campaign's centre-free interface and route calculations. It makes no supplier
admission or multiplication-exponent claim.
