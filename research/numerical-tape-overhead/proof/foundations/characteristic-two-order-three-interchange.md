# Order-three closure for physical interchange in characteristic two

Status: **new fixed-parameter physical construction, proof under independent
review**. It combines the power-of-two label geometry with finite full-rate
repair over characteristic two. It does not claim a stronger final overhead
function; the generic scalar module is explicitly retained.

The new point is an exact two-by-two group identity. It makes the spectral
converters short words in the same order-three transform being repaired.
This avoids assuming a cheap implementation of a spatial low-rank residual.

Sources: OpenAI `math@3344da59991ed94f9ba711217b29c1d760badfa6`, Fourier
`build/repair.tex` for integral interpolation, matrix roots and Hermite
repair; tape `build/interchange.tex` for physical endpoint routing and
comparison scans. The new characteristic-two geometry is proved in
[characteristic-two-label-geometry.md](characteristic-two-label-geometry.md); finite batch composition extends
[batch-contraction-repair.md](batch-contraction-repair.md) and [physical-reflection-family.md](physical-reflection-family.md).

## 1. Exact matrices over four elements

Let `F4=F2[omega]/(omega^2+omega+1)`, so `omega^3=1` and `omega!=1`.
On a two-element orbit ordered by the smaller/larger address, set

\[
 Q=\begin{pmatrix}0&1\\1&0\end{pmatrix},\quad
 C=\begin{pmatrix}0&1\\1&1\end{pmatrix},\quad
 D=\begin{pmatrix}\omega&0\\0&\omega^2\end{pmatrix}.
\]

Direct multiplication gives `C^3=D^3=I` and

\[
 S=DCDC=\begin{pmatrix}1&1\\\omega&\omega^2\end{pmatrix},\qquad
 T=C^{-1}D^{-1}C^{-1}D^{-1}
   =\begin{pmatrix}\omega^2&1\\\omega&1\end{pmatrix}.       \tag{O3-1}
\]
\[
 TS=ST=I,\qquad TCS=D,\qquad
 Q=CDC^{-1}D^{-1}CD.                                    \tag{O3-2}
\]

On every equal-field fixed point, define **all** of `Q,C,D,S,T` to be
the identity. Then every displayed identity remains valid. Matrices are
written in algebraic product order; an implementation applies the
rightmost factor first.

For `m` disjoint pairs of fields, use subscripts `j` for these operators
and put `F=prod_j C_j`, `Delta=prod_j D_j`. Operators at different indices
commute, so (O3-1)--(O3-2) imply

\[
 \mathcal S=\prod_jS_j=\Delta F\Delta F,\qquad
 \mathcal T=\mathcal S^{-1}=F^{-1}\Delta^{-1}F^{-1}\Delta^{-1},
                                                               \tag{O3-3}
\]
\[
 \prod_jQ_j=F\Delta F^{-1}\Delta^{-1}F\Delta.             \tag{O3-4}
\]

The forward spectral converter is `mathcal T`, and the inverse is
`mathcal S`. Each uses **two** transforms `F` or `F^-1` and pointwise
diagonals. Both simultaneously diagonalize the queries `C_j` and `C_j^-1`.
Their spectral exponents are `k_j=0` at equality, `1` at the smaller member,
and `2` at the larger member. For inverse queries replace `k_j` by `-k_j`
modulo three. All three choices are realizable on every positive-width
field pair. These are exact finite-field statements, not numerical gates.

## 2. Every order-three pencil retains the shared swap cost

Let `L_j=1_{H_j>N_j}` and `U_j=1_{H_j<N_j}` be ordinary pointwise
projections, zero on equal fields. Then

\[
 C_j=Q_j+L_j,\qquad C_j^2=Q_j+U_j.                       \tag{O3-5}
\]

Consequently a source `ell=3` pencil has the exact decomposition

\[
 A_0+\sum_j(A_{j1}C_j+A_{j2}C_j^2)
 =A_0+\sum_j(A_{j1}+A_{j2})Q_j
        +\sum_j(A_{j1}L_j+A_{j2}U_j).                  \tag{O3-6}
\]

The first part uses one shared-swap pencil over the new characteristic-two
labels. The last sum is computed separately in the original physical
layout, retaining the input as needed. Its comparisons have the source's
actual linear-volume implementation: a fixed earlier `H_j` splits the
complete `N_j`-and-suffix fiber into three consecutive runs. Fixed-point
diagonals and `Delta` use the same scans. They cost `C_template V`, with
the finite parameter dependence retained. No address-dependent mask is
silently moved through an endpoint coordinate change.

## 3. Integral constant-tail prediction in characteristic two

Use the source theorem with query order `ell=3`, independently for targets
`F` and `F^-1`. At each spectral tuple, shifts `beta in (Z/3Z)^m` make the
ordinary shifted digits independent and uniform in `{0,1,2}`. Their count
has mean `m`. Choose

\[
 B=3\lceil\sqrt m\rceil,\qquad u=m-B,\qquad v=m+B.
\]

Hoeffding gives an outside-window fraction at most
`2 exp(-B^2/(2m))<=2 exp(-9/2)<1/32`. For the strict last inequality,
`exp(3/2)>1+3/2+(3/2)^2/2+(3/2)^3/6>4`, so `exp(9/2)>64`.
The source **integral multivariate** predictor has degree at most
`D_pred=2B=O(sqrt m)`. Let `b_pred` be the least power of three at least
`max(2,D_pred)`; it is at most three times that maximum.

The generic matrix-root representation evaluates it in `b_pred` pencil
stages on a full batch of independent rows. Keep every shift with equal
multiplicity and duplicate by 32 to obtain a row count `R` divisible by
32. Use the inflated defect budget `s=R/32`. Hermite repair uses
`ell+2=5` predictor applications and two conversion phases of `2s=R/16`
rows. Both targets have the same scalar construction with query powers
interchanged. Their tables use the appropriate signed exponent tuple.

One common finite scalar algebra suffices. Start with
`R3=Z[1/3,omega]`, choose a primitive `3^a`-th root `eta` of order at least
`R`, with `eta^(3^(a-1))=omega`, and include the needed matrix-root power.
The source node differences are units because `Phi_(3^b)(1)=3`.
Specialize to characteristic two, where three is a unit and `omega`
generates `F4`. This gives a finite free algebra `E` over `F4`; every
node, pencil and finite table is defined in this one algebra. No new
extension is taken at a later recursion level.

There is no ordinary-count division by a factorial and no attempt to use
characteristic-zero low-rank transfers. The large generic matrix-root
dimension is retained. In this characteristic the Hermite polynomial happens
to simplify to `g(y)=y^4`. This permits the additional reduction below,
which uses only two predictor applications.

### Four-element discrepancy repair

The scalar polynomial `P_beta` has coefficients in `F4`; the larger
cyclotomic algebra is needed only for its full-rate evaluation and the
check nodes. All predictor eigenvalues `p_i` and target eigenvalues `z`
belong to `F4`. Hence `p_i^4=p_i` and, as a diagonalized operator, `P^4=P`.
The source Hermite factor is `D_z(y)=(y-z)^2`, because
`g(y)-z=(y-z)^4`. Recover `e_i=(p_i-z) Xhat_i` on the known outside-window
set and choose the lift with `Zhat_i=(p_i-z)^2 e_i` there. Output

\[
 PX+PZ+FZ.                                             \tag{O3-6a}
\]

Its error is `(p_i-z)(Xhat_i+Zhat_i)`. A zero gap gives zero error. A
nonzero gap has cube one in `F4`, so `Zhat_i=Xhat_i`. Outside the exception
set the gap is zero. This also handles outside-window rows made correct
by specialization. Only `PX` and `PZ` are evaluated. Nonzero gaps remain
units in the common extension algebra.

## 4. Finite full-rate contraction with four child phases

Let `N_lab` be the number of labels, `W0=R N_lab`, and let `R_route(m)`
bound the shared-pencil calls per independent input stream. Put

\[
 a_m=2b_{\rm pred}R_{\rm route}(m).
\]

For total depth `h`, start with `W_h=W0 16^h` independent `E`-valued
streams, in labeled base batches. A repair node for either `F` or `F^-1`
has four recursive child phases: two `F^-1` transforms implementing its
forward converter and two `F` transforms implementing its inverse
converter, with the pointwise `Delta` factors in their actual word order.
Each child phase has exactly one sixteenth of the parent's rows. Regroup
within each label across parent batches, as in the reflection construction,
then restore the batch roles after each child returns.

The spectral table is produced after the complete forward word and before
the inverse word. These phases are sequential and can be data dependent.
At depth `h`, evaluate `F` or `F^-1` directly: (O3-5) needs one copied
field swap per index, hence at most `m` calls per stream.

Correctness on arbitrary inputs in `E` and induction over the finite depth
give, for either target, the call bound

\[
 {\sigma_h\over W_h}
 \le a_m\sum_{t=0}^{h-1}4^{-t}+m4^{-h}
 \le{4\over3}a_m+m4^{-h}.                               \tag{O3-7}
\]

Indeed the four children each have row fraction `1/16`, giving total mass
`1/4`. Their own targets are precisely the transforms in (O3-3); no
same-size circular invocation remains at the finite leaves. Row correlations
created by checks do not affect correctness of a full-rate linear identity.

Use the three transforms in (O3-4) sequentially on this same batch. Their
combined target is the main swap product, with

\[
 {\sigma_{Q,h}\over W_h}
 \le8b_{\rm pred}R_{\rm route}(m)+3m4^{-h}.              \tag{O3-8}
\]

For `h=ceil(log2(m)/4)`,

\[
 W_h\le16W0m,\qquad
 {\sigma_{Q,h}\over W_h}
       =O(\sqrt m\,(R_{\rm route}(m)+1)).               \tag{O3-9}
\]

Every original input row receives its own exact swap product. No initial
zero workspace is counted as an independently transformed input.

## 5. Physical recursion, occupied reserves, and space

The characteristic-two geometry supplies, for `d=2^r`, `q=2^t` and
`h_lab=2d-1`,

\[
 R_{\rm route}(m)
   =O(D_{\rm route}(1+\lambda)(1+mr_*/N_{\rm lab})),
\]

with the explicit rank, incidence and dimension bounds in the companion
note. Its rational endpoint maps are valid over a separately chosen odd
address radix. All nonrecursive comparisons, row maps, copies, regroupings
and pointwise `Delta` factors are actual fixed-parameter linear-volume
operations, not free arithmetic on randomly addressed records.

During finite repair a child has `1/16` of its parent data volume. Park the
other arrays and run one child at a time. Parked volumes are at most
`16V/15` times the finite base workspace coefficient; siblings and the
three final word factors reuse their marked regions. The same alphabet `E`
is used by every recursive field-swap call. The complete final target is
`prod Q_j`, with coefficients in `F2`. Expanding the **completed** program
in an `F2` basis of `E` therefore transforms every basis component's
independent input correctly. Intermediate `F` transforms do not need to
act componentwise over `F2`. The dimension and arithmetic of `E` remain
part of its physical binary encoding and finite compiler coefficient.

For the source spatial recursion let `a_route=D_route-2`. Choose the
address prime above `W_h` and all required units; the first digit supplies
the main labeled batches at stream-volume ratio at most `2/W_h`. After
the main program returns, merge and clear its arrays before performing
the `2a_route` full-volume reserve calls. With
`f=floor((e-1)/(m+2a_route))`, the actual recurrence is

\[
 T(e)\le C_{\rm template}
   +(2\sigma_{Q,h}/W_h+2a_{\rm route})T(f).              \tag{O3-10}
\]

Depth-first spatial parking has the source's geometric-volume bound; the
full-volume reserve calls keep only a descriptor. Occupied reserves are
restored exactly. Hence this is a fixed finite-alphabet, fixed-tape physical
component with linear visited cells for each fixed parameter choice.

Choosing the distance parameter between
`(log m/log log(m+2))^(1/3)` and twice that value gives

\[
 {\sigma_{Q,h}\over W_h}
 \le\sqrt m\,2^{O((\log m)^{2/3}(\log\log(m+2))^{1/3})},
\]

while the reserve dimension is `m^o(1)`. Thus every fixed interchange
exponent above `1/2` can be reached using this alternative characteristic-two
program. Its end-to-end finite constants must still be bounded and compiled
before a growing-parameter overhead claim is made.

## 6. Scope and next question

The construction supplies both the formerly missing characteristic-two
shared-pencil geometry and an exact semisimple repair closure. It does not
apply the source odd-characteristic sum/difference converter in
characteristic two. It also does not assume that a low-rank matrix on
spatial coordinates can be applied cheaply on tapes.

The remaining large quantity is the **full-rate multivariate predictor
module**. With degree `O(sqrt m)` in the individual order-three query
powers, the generic source construction still has a large tensor module.
Its size, the cyclotomic algebra, all tables, numeric address scalings and
the common space coefficient are retained. No better whole-input `H(n)`
bound is inferred just from fixing the data characteristic or removing a
square-root logarithm from the local call count.

Credits: source integral interpolation, generalized matrix roots, Hermite
repair and physical endpoint routing; B's power-of-two-distance labels and
finite group-word closure; Jerry Chen (@CubeJerry); AI-assisted discovery
and exact finite verification during the 2026-11-25 session.

## 7. Exact finite verification

[verify_order_three_interchange.py](https://github.com/CubeJerry/integer-mult-bounds/blob/a2a17b61d943676c757e0bbfaef3f4fae03ab8e5/research/moonshot-overhead-program/routes/B/verify_order_three_interchange.py) and
`order-three-interchange-verification.json` verify the finite identities
using integer polynomial arithmetic in characteristic two. The four-element
matrices are embedded into `F_256` for sufficiently many distinct check nodes.
No floating-point numbers occur.

The checks include the exact group words, 390 unit differences in
`F2[Y]/Phi_(3^a)(Y)` for `a=1,2,3`, all-basis physical orbit identities
including fixed points, the one-shared-pencil decomposition, and all 3456
shift/frequency cases for the toy predictor. Label-preserving gather/scatter
is checked with three labels. Both positive and inverse targets pass
one- and two-level full-rate Hermite unrollings. The largest has 19683
independent input rows and 1259712 field entries. The final three-transform
word returns the actual whole-field swap on 1458 independent rows.

Negative controls reject a wrong group word, failure to keep equal-field
points unchanged, wrong check order, an omitted intermediate diagonal,
wrong-label inverse returns, omission of repair, and starting an inverse
phase before the spectral table is ready. The numerical mismatch counts
are retained in the JSON result.

The toy uses three queries, 27 shifts, window `[1,5]`, and two exceptional
rows, giving phase fraction `4/27` and total child mass `16/27`. It tests
the finite composition at that exact rational fraction. The proof's chosen
fraction `1/16` and mass `1/4` are checked separately by exact ledgers.
Predictors in the verifier use direct spectral converters. Consequently
these checks do not implement the generic Clifford module, source physical
routing, or a complete Turing machine. Those claims rely on the stated
source interfaces and the proof above.
