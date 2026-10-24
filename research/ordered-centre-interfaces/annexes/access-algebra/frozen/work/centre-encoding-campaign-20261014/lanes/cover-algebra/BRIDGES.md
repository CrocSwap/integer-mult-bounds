# Legal native bridges for routed centre operators

This note continues `PROOF.md`. It uses the same pinned centre matrix and
route charts. The global boundary frames are the frames supplied by the
selected controller and checked by `temporal-reuse/verify_routes.py` against
`DATA-PHASES.json`:

\[
X_q:F_{U_s},\qquad Y_q:F_{U_s}C_q^{-1},\qquad
U_s=L\oplus E_1\oplus\cdots\oplus E_s.
\]

Here `dim(L)=9`, each `dim(E_t)=8`, and `s=0,...,8`.
At the initial boundary, `X_q` has frame `C_q` and `Y_q` has frame zero.
This note checks bridges under these frame formulas. It does not repeat the
complete controller-frame derivation.

## Full frame conditions

Let

\[
\phi_{X,s}(x)=\sum_{i=0}^{8+8s}(e_i\cdot x)\pmod4,
\]

\[
\phi_{Y,s,q}(x)=\phi_{X,s}(x)-(q\cdot x)\pmod4.
\]

Each dot product in these phase formulas is its binary value, interpreted
as 0 or 1 before reduction modulo 4. The phase value is `i^phi`.
The polar matrices are the orthogonal projections onto `U_s` and

\[
H_s(q)=U_s\cap q^\perp,
\]

respectively. For an orthogonal right route `r`, a bridge from input port
`p` to output port `q` is legal up to an even linear phase exactly when

\[
\begin{array}{ll}
X:& rU_s=U_s,\\
Y:& rH_s(p)=H_s(q).
\end{array}
\]

Equality of the polar matrices is necessary. It is sufficient because two
quadratic phase forms with the same polar matrix differ by an even linear
form. The resulting translation must be applied; the polar condition alone
does not certify the phase.

The stronger pair of conditions `rU_s=U_s` and `rp=q` is sufficient for a
Y bridge. It is not necessary. In particular, the actual Y frame does not
distinguish its hole line from the other directions in its radical.

## A legal exchange with a future direction

Let `e` be a unit coordinate vector in a future block. The binary
transvection

\[
S_{q,e}=I+(q+e)(q+e)^T
\]

exchanges `q` and `e` and fixes `H_s(q)` pointwise. Thus it is Y-frame legal,
although it does not preserve `U_s` or the line `q`.

Every selected port has weight 3 or 7. Therefore
`phi_Y(q)=wt(q)-1=2 mod4`, whereas `phi_Y(e)=0`. The full phase defect is

\[
\phi_{Y,s,q}(S_{q,e}x)-\phi_{Y,s,q}(x)
=2(q+e)\cdot x\pmod4.
\]

The correction is exactly the translation vector `q+e`.
The checker verifies this identity as a full quadratic phase form for all
112 ports and all eight boundaries that have a future block. A controller
that forbids these bridges would impose a construction-specific restriction.

## Future Y access and past X access

Let `D_t=diag(rho_t(q))` and `K_t=D_t J D_t`, as operators on logical
content. The physical implementation of `D_t` below includes its phase
alignment. A bare cover permutation is not a substitute for that alignment.

If `s<t`, then

\[
\rho_t(p)H_s(p)=E_t\oplus E_1\oplus\cdots\oplus E_s.
\]

The right side is independent of the port. Thus `D_t` aligns all Y
registers to one common frame. At that common frame, any scalar matrix on
the 112 ports is legal. In particular, `J` and `J^{-1}` are legal as linear
maps there. Undoing the alignment gives `K_t` and `K_t^{-1}` on Y.

If `s>=t`, then every `rho_t(q)` preserves `U_s`. The same argument gives
`K_t` and `K_t^{-1}` on X. At the initial zero Y frame every `D_t` is legal
without a phase defect. Stage 0 has `D_0=I`.

There are explicit phase corrections for these two alignments. Write
`B_q` for the eight chart columns and set

\[
(\beta_q)_i=\frac{\operatorname{wt}((B_q)_i)-1}{2}\pmod2.
\]

Let `lift_t` put an eight-bit vector in `E_t`. Then

\[
\delta_Y(q,t)=q+\operatorname{lift}_t(\beta_q),\qquad s<t,
\]

\[
\delta_X(q,t)=B_q\beta_q+\operatorname{lift}_t(\beta_q),\qquad s\geq t.
\]

The formulas do not depend on `s` within the stated ranges. To prove them,
evaluate each phase on the orthonormal basis `[q,B_q]` and on `E_t`.
The Y phase has value 2 at `q`, has the stated chart-weight defects on the
eight other basis vectors, and is zero on the unused block. For X both
blocks are present; the two copies of the `q` defect cancel.

The checker compares every linear coefficient modulo 4 and every quadratic
coefficient. All 4,032 future Y cases and all 4,032 past X cases pass.

The independent check in
`../interface-proof/BRIDGE-OPERATOR-REVIEW.json` binds these formulas to the
actual supplier. It checks all 1,008 entry and exit vectors in the pinned
`DATA-PHASES.json` and all 32,256 owner routes in `GLOBAL-TEMPLATE.json.gz`.
It also checks the full phases by Fourier-character evaluation on zero,
single-coordinate, and two-coordinate inputs. The actual local shear is
exactly `D_t L(J) D_t` or `D_t U(-J^T) D_t` in these boundary gauges. Thus
the bridge and the supplier use the same logical `K_t`; no additional
phase conjugation remains. The independent check rejects omitted X or Y
translations and the wrong Y route/translation order for all 112 ports.

### Factorized implementation and open costs

To apply one of these encoded matrices, use this sequence:

1. Apply the portwise cover permutation `D_t` and its listed phase correction.
2. Apply `J` or `J^{-1}` to the 112 registers in the common frame.
3. Undo the phase correction and the portwise permutation.

The common-frame scalar step needs only one private accumulator. The rows
`r_k` of `R` are pairwise orthogonal, so the eight rank-one updates commute.
For each row, form `z=r_k v`, scale it by `1/4`, and subtract `r_k^T z`
from `v`. Clear the accumulator before and after each row. The product of
these updates is exactly `J`. For `J^{-1}`, use `1/52` instead of `1/4`.
The previous row updates do not change the dot product for the current row.

This needs 896 unit-coefficient ADDs, eight quarter scales, and sixteen
CLEARs. The dyadic real-primitive bound is 7,232. The inverse also needs
eight complex divisions by 13. The checker verifies both scalar maps on
all 113 input columns, including arbitrary initial private state. The maps
leave unrelated borrowed state unchanged and end with zero private state.
The `interface_proof` worker supplied this one-accumulator factorization
and its primitive invoice during independent review.

This is an operator construction, not an admitted compiler program. The
new source accesses, cover permutations, phase translations, private-array
hosting, and all scalar costs still require a concrete lowering. In
particular, `1/52` is not dyadic. The current dyadic primitive invoice does
not by itself price the inverse. A controller must either supply the
required arithmetic lowering or carry its scale and account for final
normalization. The existence of a rank-zero phase bridge does not make its
array permutation or scalar work free.

## A fixed port bijection can change a backward transfer

The nonzero off-diagonal graph of `J` is 52-regular and bipartite when one
copy of its port set is used on each side. It has a perfect matching. The
checker records an explicit bijection `q=pi(p)` with `J_pi(p),p` nonzero.

Define a post-call X bridge by

\[
(B_X)_{p,\pi(p)}=\rho_t(p)\rho_t(\pi(p)).
\]

This is a fixed bijection of port-cover addresses. It preserves `U_t`, so
it is X-frame legal after stage `t`, with the computed linear correction.
Direct multiplication gives

\[
(B_XK_t)_{p,p}=J_{\pi(p),p}=\pm\tfrac12.
\]

Thus a backward off-diagonal native transfer can become a diagonal logical
transfer. This invalidates an obstruction that assumes every bridge
preserves the port label or fixes every completed external block.
It does not remove the other entries of `B_XK_t`.

The same bridge on Y fails the polar condition. It sends the old hole to a
unit vector in `E_t`, orthogonal to the new local port. The two rank-one
hole projectors have a difference of rank 2. The checker verifies this for
all 896 matching bridges over eight stages.

## A single forward edge has a different constraint

For a forward stage `t>=1`, write `U_prev=L+E_1+...+E_(t-1)`.
If `J_qp` is nonzero, then `p` and `q` are orthogonal. Set
`g=rho_t(q)rho_t(p)`. One has

\[
gU_{prev}=q^\perp\text{ in }L
\;\oplus\;E_1\oplus\cdots\oplus E_{t-1}
\;\oplus\;\langle\rho_t(q)p\rangle
\subseteq H_t(q).
\]

Legal pre-X and post-Y bridges preserve this inclusion. An identity
same-port transfer does not have this property, because `U_prev` contains
the target hole. Hence one forward off-diagonal edge cannot be converted
to the identity transfer by legal endpoint bridges alone. This is a
single-edge statement. It does not exclude multi-call controller paths.

## Endpoint test for the current full-stage residual

At the final boundary the rank-zero Y algebra is the line-preserving group
algebra: a group term `g` from port `p` to port `q` must satisfy `gp=q`.
This algebra is closed under composition. The same condition makes
`C_q g C_p^{-1}` have zero polar defect.

The controller worker is studying the residual

\[
E=K_8K_7^{-1}K_6K_5^{-1}\cdots K_1^{-1}K_0.
\]

In fact, the same conclusion holds for every chronological product of
`K_t` and `K_t^{-1}` that contains at least one `K_t`, with the stages
increasing from right to left. The identity coefficient of `K_t^{-1}`
is `12/13`, and each remaining term has the support of `K_t`.
Before the first off-diagonal term in a product path, the carried initial
port is the current port. At stage 0, an off-diagonal term leaves that
vector in the new port's orthogonal complement, since `J_qp` is supported
only on `p dot q=0`. At a positive stage `t`, the first off-diagonal term
sends that vector into `E_t`, hence into `H_t(q)`.

Each subsequent term at stage `u>t` maps
`H_(u-1)(p)` to `H_(u-1)(q)`: the two route charts map these spaces to the
same space `E_u + E_1 + ... + E_(u-1)`. An identity term also preserves
this property. Each factor `K_t` has zero port diagonal, so at least one
off-diagonal term must occur in every product path. Therefore every
surviving entry of any such product satisfies `q dot (gp)=0`. No such
entry can satisfy `gp=q`. This includes both orientations of the
alternating normalization word.

Consequently this residual is outside the final Y rank-zero algebra. Every
nonzero group entry of `C_q E C_p^{-1}` has polar defect rank 2. This does
not prove that two complete rank-one endpoint boundaries are the cheapest
repair. A factored or encoded repair may cost less and remains a research
target. The actual controller word and its full cost are separate obligations.
The statement does not cover arbitrary inserted routers that mix future
blocks or products whose stage order decreases.

### A stronger statement for arbitrary port support

The restriction can be proved without the binary-orthogonal support of
`J`. Consider any chronological product

\[
E=(D_m A_m D_m)\cdots(D_1 A_1 D_1)A_0,
\]

where each `A_s` is a scalar port matrix and the block `E_s` is new at stage
`s`. Port labels may repeat. Use the same chart for each occurrence of the
same physical label. On a product path, let `p` and `q` be the input and
output labels of a stage, and let `v` be the carried image of the original
source line before that stage. The vector `v` has no component in `E_s`.
Set `h=p dot v_local`. For `g=rho_s(q)rho_s(p)`, the block formula gives

\[
(gv)_{E_s}=h B_q^T p,\qquad q\cdot(gv)=(q\cdot p)h.
\]

Every later stage fixes `E_s` pointwise. A final line-preserving path must
therefore have zero new external component at each stage and final hole
coefficient one. The hole coefficient cannot change from zero to one under
the displayed recurrence. Thus it is one at every stage, and
`B_q^T p=0`. Since `ker(B_q^T)=span(q)`, this implies `p=q` at every
positive stage. Each such route is the identity. The stage-zero label must
also equal the original label to give the final source line.

Consequently the line-preserving part of `E` is exactly the product of the
within-label blocks of the scalar matrices. With distinct labels it is

\[
\operatorname{diag}_p\left(\prod_{s=0}^m (A_s)_{pp}\right)
\]

at the identity cover element. This is a statement about a chronological
product. It is not a homomorphism on arbitrary words in the routed algebra.

For the 120-port completion with its eight distinct centre-normal labels,
the line-preserving part of `M_8...M_0` is exactly
`diag(0_112,13^9 I_8)`. With arbitrary choices of eight additional labels,
at least 104 of the original labels remain singletons. Their diagonal is
zero, so their entire input columns have no line-preserving component in
this normalization word. A duplicate label is allowed by the local native
interface; it does not remove this count.

There is a further statement that does not require a zero diagonal. Let
the last scalar matrix split as `A_m=A_same+A_change`, according to whether
its input and output physical labels agree. Let `H` be the cover subgroup
that fixes `E_m` pointwise. Every term of the earlier invertible product
`P` and its inverse lies in `H`. The routed `A_same` is supported at the
identity, whereas every routed `A_change` term is outside `H`. Therefore
the two products have disjoint `H` and non-`H` support. The second product
cannot be zero if `A_change` is nonzero, since `P` is invertible.

For such a last changing term from `p` to `q`,

\[
g^{-1}q=\rho_m(p)q
\]

has a nonzero `E_m` component. No earlier route sends an initial local line
to this vector, because earlier routes preserve `U_(m-1)`. Hence every
surviving coefficient in that second product fails line preservation. Any
nontrivial last label-changing factor leaves a nonfree endpoint component.
This argument was checked independently with the controller worker. It
does not give a lower bound on the cost of a final repair.

## Reproduction

From the workspace root, run:

```sh
python3 -B work/centre-encoding-campaign-20261014/lanes/cover-algebra/verify_bridges.py --interface work/centre-encoding-campaign-20261014/lanes/circuit-interface/INTERFACE.json --out work/centre-encoding-campaign-20261014/lanes/cover-algebra/BRIDGES.json
```

The output is `PASS_EXACT_NATIVE_BRIDGE_PHASES`. The code uses exact integer
phase forms, binary matrix operations, and rational matrix coefficients.
It does not certify a complete supplier or a multiplication exponent.

Open work includes a cheaper residual decoder, legal movement of the
post-X factors on idle bank roles, and full lowering of the new scalar
access pattern. This work used AI assistance and builds on the selected
supplier and the campaign's interface, route, and controller calculations.
