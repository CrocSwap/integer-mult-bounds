# Exact stage views in every dimension 9+8T

The actual D25 and D73 DATA routes are instances of one exact formula.
The formula works for every positive integer T in dimension \(D=9+8T\).
It retains the actual root chart of each of the 112 ports. It gives the
complete payload phase and the regular-cover owner map.

This result supplies the stage boundary identities needed to carry the
same local nine-dimensional service to later stages. It does not make
the routed response constant. It does not supply a complete caller,
a new recursive host, a finite map cost, or an exponent.

## Root quadratic refinement

Fix an actual port with intrinsic unit vector q. The root chart is the
pinned orthonormal basis

\[
B=(q,b_1,\ldots,b_8)
\]

of the first nine coordinates. Its q has Hamming weight 3 or 7.
For any unit vector v, define

\[
\beta(v)=\frac{|v|-1}{2}\pmod 2.
\]

Put \(\beta_j=\beta(b_j)\) and

\[
\delta_0=q+\sum_{j=1}^{8}\beta_jb_j.
\tag{1}
\]

The coefficient of q is one because its weight is 3 or 7.
Let \(C_v\) be the exact line transform with Fourier multiplier
\(i^{v\cdot z}\). Let \(X_v=C_v^2\) be the translation by v.
All these operators commute. If \(F_0\) is FULL on the root axes, then

\[
Q\prod_{j=1}^{8}C_{b_j}=X_{\delta_0}F_0,\qquad Q=C_q.
\tag{2}
\]

To prove (2), compare the Z4 functions
\(\sum_{v\in B}(v\cdot z)\) and \(|z|\). Their difference has zero
quadratic part modulo four because B is orthonormal. Its linear part
is even. Evaluate it at each basis vector \(v\in B\): the value is
\(1-|v|=2\beta(v)\pmod4\). Thus the difference is
\(2\delta_0\cdot z\). This proves the full phase, including its sign.

## The route and its two translations

Let \(E_s=(e_{s,1},\ldots,e_{s,8})\) be the fresh coordinate block for
stage s, where \(1\leq s\leq T\). Define \(\rho_s\) to exchange
\(b_j\) with \(e_{s,j}\), for each j, and to fix q and all other fresh
blocks. This is an orthogonal involution. An explicit matrix is

\[
\rho_s=I+\sum_{j=1}^{8}
 (b_j+e_{s,j})(b_j+e_{s,j})^{\mathsf T}.
\tag{3}
\]

The eight vectors in the sum are isotropic and pairwise orthogonal.
Equation (3) therefore has the stated action on the complete
orthonormal basis.

The two physical translations are

\[
\delta_{\rm in}(s)=\rho_s\delta_0
 =q+\sum_j\beta_je_{s,j},\qquad
\delta_{\rm out}(s)=\delta_0+\rho_s\delta_0.
\tag{4}
\]

Let \(P_{\rho_s}\) be the payload address permutation. The entry map is
\(V_{\rm in}=X_{\delta_{\rm in}}P_{\rho_s}\). Its equivalent order is
\(P_{\rho_s}X_{\delta_0}\). The exit map is
\(V_{\rm out}=X_{\delta_{\rm out}}P_{\rho_s}\).
The exit translation is fixed by \(\rho_s\), so the exit map is its
own inverse.

## Adjacent-stage identities

Let \(F_\ell\) be FULL on the root and fresh blocks 1 through \(\ell\).
Let \(F_{{\rm ext},s}\) be FULL on fresh blocks 1 through s.
The exact adjacent identities are

\[
\begin{aligned}
V_{\rm in}(s)F_{s-1}
 &=F_{{\rm ext},s}\,Q\,P_{\rho_s},\\
V_{\rm in}(s)F_{s-1}q
 &=F_{{\rm ext},s}\,P_{\rho_s},\\
V_{\rm out}(s)F_s
 &=F_sP_{\rho_s},\\
V_{\rm out}(s)F_sq
 &=F_sqP_{\rho_s}.
\end{aligned}
\tag{5}
\]

For the first identity, conjugate (2) by \(P_{\rho_s}\).
The eight root-complement line factors become the fresh block s.
The other completed fresh blocks are fixed. The entry translation
in (4) cancels the translated factor in (2).
The second identity follows because \(\rho_s q=q\) and \(Qq=I\).

For the third identity, the factors from both the root and fresh
block s are present. Exchanging these factors changes FULL by precisely
\(X_{\delta_0+\rho_s\delta_0}\), which the exit map cancels.
The fourth identity follows again from \(\rho_s q=q\).

All remaining coordinates are spectators. None of these arguments
depends on T or on the number of preceding completed blocks.

The same proof gives the complete access cones. A FULL field at level
\(\ell\geq s\) admits the stage-s exit map. A hole field \(F_\ell q\)
at level \(\ell<s\) admits the stage-s entry map into the common
exterior on fresh blocks \(1,\ldots,\ell,s\). The corresponding
FULL input has one additional intrinsic Q line.

## Owner cover and physical fields

Use the regular cover \(O(D,2)\). For a body label d and port p, its
owner is \(h=d\rho_{s,p}\). Right multiplication by the fixed
orthogonal matrix is a bijection. Thus each field's owner assignment
is a permutation of the complete cover. Equation (5) includes the
payload map on that owner change; it is one field/address map.

This proof permits a complete-cover barrier between local events or
between a local service and a routed query. It does not permit two
different stages' bodies to be identified without their maps.
In particular, a scalar matrix E in each current body lifts to
\(\Gamma_s^{-1}E\Gamma_s\), where
\(\Gamma_s=\operatorname{diag}(P_{\rho_{s,p}})\). These global operators
can differ with s.

## Consequence for a retained reader

The forward and inverse-adjoint reader services have current local
boundaries \(\operatorname{diag}(Q,Z)\) and
\(\operatorname{diag}(F_9,F_9G_R)\), with
\(Z=\operatorname{diag}(Q_P,I_R)\) and
\(G_R=\operatorname{diag}(I_P,q_R)\).
Equation (5) supplies those same boundaries at every stage t.
For any earlier reader label \(s<t\), the old FULL views are legal at
the completed level t.

Consequently the reversible-source query

```text
current A_t on X
past L_s query into selected Y
current A_t on X
```

and its same-chronology inverse-adjoint use the same local words and
the same number of views at every \(0\leq s<t\leq T\). For s=0,
the past route is the identity. This statement keeps the old reader
label separate from the physical entry level \(t-1\).

The exact logical maps remain the ordered maps from the frozen service,
with \(D_{s,t}[P,*]=L_sA_t\) and \(D_{s,t}[R,*]=(A_t)_R\).
No commutation between \(L_s\) and \(A_t\) is used.
The native profile, scalar count, and number of map calls do not change
under this dimension extension. The actual map size and its finite cost
still depend on D. The frozen finite replay covers the three D25 pairs;
the general extension follows from (5) and the unchanged local word.

## Source binding and checks

The checker emits the actual root chart and the three translation
formulas for each port. It compares all 224 nonzero-stage D25 records
and all 1,792 D73 side records with the pinned source payloads.
It checks the full Z4 identities in dimensions 17, 25, 33, 73, and 137.
The first four cases check all access-cone levels. The last checks
every adjacent stage. Omitting either required translation fails.

The arbitrary-T statement is the proof above, not an inference from
these finite tests. Run `check_views.py --output <new-directory>` in
normal Python and in `python3 -O`; both payload and receipt must be
byte equal.

The root charts, D25 records, and D73 records come from the actual
supplier access calculations. The retained-reader consequence uses
the complete forward service and its emitted inverse-adjoint. All
source hashes are explicit in the payload. This work uses AI assistance
and exact finite-field and Z4 computation.

No PR or publication is authorized. Before any future PR description,
read `/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
