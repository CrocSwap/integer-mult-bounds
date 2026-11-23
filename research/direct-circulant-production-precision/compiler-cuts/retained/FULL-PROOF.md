# Full Toeplitz recursion with a polynomial conditioning envelope

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0.

## 1. Domain, result and predecessor scope

Let \(N=2^d\), and let \(T\in\mathbb Q(i)^{N\times N}\) be Toeplitz.
Write \(T_b=T[0:b,0:b]\). I assume
\[
\Lambda,Q\ge1,\qquad \|T\|_2\le\Lambda,\qquad
\|T_b^{-1}\|_2\le Q\quad(1\le b\le N).
\tag{1}
\]
The full inverse bound alone would not suffice: the Toeplitz matrix
\(\left[\begin{smallmatrix}0&1\\1&0\end{smallmatrix}\right]\) is invertible
but has a singular first section. I include it as an admission control.
I allow indefinite and non-Hermitian matrices satisfying (1).

I execute the retained `full_plan` on exactly \(N\) logical complex wires,
using the completed generator circuit and the same stored gates in reverse
for inversion. For input norm at most \(R\ge1\), incoming grid
\(F_0\in\mathbb Z_{\ge0}\) and target \(2^{-t}\), \(t\in\mathbb Z_{\ge1}\),
I prove forward and inverse error at most \(2^{-t}\)
with online widths
\[
O(F_0+t+\log N+\log\Lambda+\log Q+\log R).
\tag{2}
\]
The circuit has \(O(\log^4N)\) layers and \(O(N\log^4N)\) gates.
I give explicit constants below.

Vlado/PR1673 supplied the recursive compiler and displacement identities.
The retained `GAUGEFREE-INTERIORS.md`, Theorem 4.1, supplies a
conditioning-dependent guard of
\(O(\log N\log(2+\Lambda/\mu))\) for its accretive domain.
I use the scalar unit-LDU factors of legal completed-call sets to obtain
a joint polynomial envelope in dimension and conditioning. This
sharpens the sufficient guard's conditioning dependence under (1).
I leave the selected multiplication exponent unchanged.

ToikY's [PR4209](https://github.com/CrocSwap/integer-mult-bounds/pull/4209)
at `ccc33bfde8baadef7979fac81e28c0a6f6f278c4` supplies sharper local
Schur closure under a row/column near-identity majorant. I retain that
distinct credit. I do not infer its hypothesis from (1) or use its
sharper constants in the present allocation.

### Executable admission

`admission()` computes exact inverses of the same root's leading sections.
It returns \(\lambda_c,Q_c\), each at least one, using the maximum row
and column sums of \(|\Re z|+|\Im z|\). These bound the corresponding
operator norms and also support the executable component-envelope guards.
The verifier binds them to the unchanged root passed to `Full.plan()`.
That lower-level factory does not repeat the complete admission.

If (1) is supplied as operator-norm information, then
\[
\lambda_c\le\sqrt{2N}\Lambda,\qquad
Q_c\le\sqrt{2N}Q.
\tag{3}
\]
I use the executable envelopes in its explicit constants. The inflation
in (3) preserves (2). The written operator lemma below uses any valid
\(\Lambda,Q\); passing uninflated operator bounds directly to the
component-guarded factory need not satisfy its stronger guards.

Exact admission and Schur preparation are offline rational computations.
I do not equate their denominators with online data words or claim a
complete physical preparation/delivery tariff.

## 2. Contiguous descendants, shears and rank

The node on logical interval \([a,b)\) has reference matrix
\[
M_{a,b}=S(a,b)=T_b/T_a,
\]
with the empty prefix convention at \(a=0\). Its children are \(S(a,c)\)
and \(S(c,b)\), where \(c=(a+b)/2\), by the Schur quotient identity.
Consequently
\[
\|M_{a,b}\|\le U:=\Lambda+\Lambda^2Q,\qquad
\|M_{a,b}^{-1}\|\le Q.
\tag{4}
\]
The inverse is a principal block of \(T_b^{-1}\); the direct bound follows
from the Schur formula and restrictions of the original \(T\).

At a split, write \(M=\left[\begin{smallmatrix}A&B\\C&D\end{smallmatrix}\right]\),
\(K=A^{-1}B\), \(L=CA^{-1}\). Let \(R_a\) select the coordinates
\([a,c)\) from \([0,c)\). The block inverse identities give
\[
K=R_aT_c^{-1}T[0:c,c:b],\qquad
L=T[c:b,0:c]T_c^{-1}R_a^T.
\]
Thus, with \(\chi=\Lambda Q\),
\[
\|K\|,\|L\|\le\chi.
\tag{5}
\]
The component-envelope versions follow under the executable admission.
The source computes \(L\) as `solve(A.T, C.T).T`. I preserve ordinary
transpose in this complex identity.

The retained `SHALLOW-TOEPLITZ.md`, Sections 4–6, gives commutator rank
at most \(2+\text{depth}\) for the Schur nodes. Its rectangular identities
bound the shear commutator ranks by \(2\,\text{depth}+5\) and
\(2\,\text{depth}+7\). Conversion to
\(E_X=X-ZXZ^T\) adds at most one rank. I use the uniform allowance
\[
r_*=2d+8.
\tag{6}
\]
The exact rational producer retains that rank; I do not use the numerical
source's floating SVD threshold as a universal rank argument.
The executable also checks exact generator rank against separate
elimination in its finite fixtures.

## 3. Uniform scalar-LDU bounds

Write \(M_J=\ell_J\delta_Ju_J\) for the scalar unit-LDU factors of a
contiguous descendant. All its leading sections are further \(S(a,c)\),
so (4) also applies during scalar elimination.
For \(A_k=M_J[0:k,0:k]\), the last row of
\(A_k^{-1}M_J[0:k,k:]\) is the corresponding unit-upper row tail.
The last column of \(M_J[k:,0:k]A_k^{-1}\) is the unit-lower column tail.
Each therefore has norm at most
\[
UQ=\chi+\chi^2\le2\chi^2.
\]
The Frobenius estimate therefore permits
\[
\|\ell_J\|,\|u_J\|\le W:=3N\chi^2.
\]
The pivot diagonal has norm at most \(U\) and inverse norm at most \(Q\).
From
\[
u_J^{-1}=M_J^{-1}\ell_J\delta_J,\qquad
\ell_J^{-1}=\delta_Ju_JM_J^{-1}
\]
I obtain
\[
\|\ell_J^{-1}\|,\|u_J^{-1}\|\le V:=6N\chi^4,
\tag{7}
\]
using \(QU\le2\chi^2\). A diagonal containing some completed pivots
and otherwise ones has direct and inverse norms at most \(2\chi^2\).

## 4. Exact downsets and the upper frontier

At an internal node \(v\), denote the upper and lower atomic calls by
\[
R_v=\begin{pmatrix}I&K_v\\0&I\end{pmatrix},\qquad
B_v=\begin{pmatrix}I&0\\L_v&I\end{pmatrix}.
\]
The source executes \(R_v\), its two child programs in parallel, then
\(B_v\). A leaf executes its scalar pivot.
The atomic partial order places \(R_v\) before both children and both
children before \(B_v\). Incomparable calls act on disjoint intervals
and commute. I count identity shears as calls even when they emit zero layers.

For a downset \(I\), let \(Q(I)\) be its product in any legal linearization.
At a node, the restricted downset is empty; or it contains \(R_v\) and
child downsets \(I_0,I_1\) but not \(B_v\); or it contains the whole node.
For an empty node set all three factors to identity. At a completed leaf
set them to \(I,d_i,I\). Otherwise define
\[
\begin{aligned}
\mathcal L(I)&=B_v^\epsilon
 \operatorname{diag}(\mathcal L(I_0),\mathcal L(I_1)),\\
\mathcal D(I)&=\operatorname{diag}(\mathcal D(I_0),\mathcal D(I_1)),\\
\mathcal U(I)&=\operatorname{diag}(\mathcal U(I_0),\mathcal U(I_1))R_v,
\end{aligned}
\tag{8}
\]
where \(\epsilon=1\) exactly when the lower call has completed.
Then both children are complete. Substituting the child identities gives
\[
\boxed{Q(I)=\mathcal L(I)\mathcal D(I)\mathcal U(I).}
\tag{9}
\]
This induction never commutes overlapping factors.

Uniqueness of scalar unit-LDU gives
\[
\ell_v=B_v\operatorname{diag}(\ell_{v0},\ell_{v1}),\quad
\delta_v=\operatorname{diag}(\delta_{v0},\delta_{v1}),\quad
u_v=\operatorname{diag}(u_{v0},u_{v1})R_v.
\]
Hence \(\mathcal L(I)\) is the direct sum of full lower factors on the
maximal completed subtrees, with identity elsewhere. The partial diagonal
contains completed pivots and otherwise ones.

For the upper frontier, stop at a node whose upper call has not completed;
otherwise descend to its two children. Retain singleton leaves.
The resulting intervals partition the coordinates. With
\(U_{\mathcal F}=\bigoplus_{v\in\mathcal F}u_v\), induction gives
\[
u_{\rm root}=U_{\mathcal F}\mathcal U(I),\qquad
\mathcal U(I)=U_{\mathcal F}^{-1}u_{\rm root}.
\tag{10}
\]
At an unvisited node the identity is \(u_v=u_vI\); at a visited node,
substitute the two child identities and multiply by \(R_v\).

Equations (7)–(10) bound the lower factor and its inverse by \(V\),
the partial diagonal and its inverse by \(2\chi^2\), and the upper
factor and its inverse by \(VW\). Thus
\[
\boxed{\|Q(I)\|,\|Q(I)^{-1}\|
\le216N^3\chi^{12}<\mathcal B:=256N^3\chi^{12}.}
\tag{11}
\]
I use a fixed number of polynomial factors, rather than multiplying
conditioning factors through the recursion depth.

## 5. Approximate atomic calls and physical cuts

There are \(J=3N-2\) atomic calls: two shears per internal node and one
scalar per leaf. Approximate each by operator error at most \(\eta\).
For any legal linearization, set
\[
G_j=Q_j^{-1}(\widehat A_j-A_j)Q_{j-1},\qquad
\theta=J\mathcal B^2\eta.
\]
The downset bound (11) applies to its prefixes.
If \(\theta\le1/4\), the product of \(I+G_j\), or its inverse, has norm
below two and distance from identity at most \(2\theta\).
Using \(\Lambda,Q\le\mathcal B\), I obtain
\[
\|\widehat T-T\|,\|\widehat T^{-1}-T^{-1}\|
\le e:=2J\mathcal B^3\eta.
\tag{12}
\]
Completed approximate prefixes and inverse prefixes have norm at most
\(2\mathcal B\). Remaining suffixes and inverse suffixes have norm at most
\(2L_0\mathcal B\), where \(L_0=\max(1,\Lambda,Q)\).
I apply the exact LDU identities to the ideal calls, not to the
approximate endpoints.

At a physical gate cut, completed calls form a downset \(I\).
Started but unfinished calls form a pairwise incomparable set \(A\):
the source finishes an upper call before starting its descendants and
finishes those descendants before its lower call. Active supports are
therefore disjoint, even when sibling ranks and lengths differ.

Write each active stored endpoint as \(\widehat A_a=T_aF_a\), with executed
prefix \(F_a\) and remaining suffix \(T_a\). A completed call executed
after an active call began must act on a disjoint subtree, so I may commute
only that disjoint work. I obtain the exact identities
\[
C_{\rm prefix}=(\bigoplus_{a\in A}F_a\oplus I)\widehat Q(I),\qquad
C_{\rm suffix}=\widehat Q_{\rm remaining}
                    (\bigoplus_{a\in A}T_a\oplus I).
\tag{13}
\]
The set \(I\cup A\) is also a downset, so I may order \(I\), then \(A\),
then the remaining calls in the suffix argument.
A direct sum contributes the largest fragment norm. I do not require
aligned child macro boundaries. A zero-layer identity completes at its
position in the source schedule and contributes no active fragment.

## 6. Child, scalar and data bounds

The component envelope used by a shear's exact producer satisfies
\(B_E\le4N\chi\): its displacement norm is at most \(2\chi\), and a
component row/column sum is at most \(\sqrt{2m}\) times that norm.
Substituting \(m\le N\), \(r\le r_*\), \(B_E\le4N\chi\) in
[GENERATOR-PROOF.md](GENERATOR-PROOF.md), put
\[
\alpha_*=8r_*N^2\chi,\quad K_{G,*}=2N+64N^2\chi,
\]
\[
H_*=\max(3200N^3,2+2K_{G,*})(10+4\alpha_*+2K_{G,*}).
\]
The generator's radius-one allocation supplies an unrounded operator
defect. I discard its local data grid and execute the flattened full
program on one global grid.

A scalar pivot has \(1/Q\le|a|\le U\). I round it at \(s\) bits,
with \(\eta=2^{-s}\le1/(2Q)\), and invert the same stored value.
Then \(|\widehat a|\ge1/(2Q)\), its direct norm is at most \(U+1\),
and its inverse norm is at most \(2Q\).
Consequently
\[
\mathcal H=\max(H_*,U+1,2Q),\qquad
K_{\rm phys}=2L_0\mathcal B\mathcal H
\tag{14}
\]
bounds physical prefixes, suffixes and their inverses.
An arbitrary segment needs the conservative bound \(K_{\rm phys}^2\).

The unchanged source schedule permits
\[
D_*=1+2dr_*(8d^2+32d+18),\qquad
G_*=N[1+dr_*(4d^2+24d+22)].
\tag{15}
\]
I sum two generator calls per level and the \(N\) scalar leaves; parallel
siblings contribute their maximum depth.
Choose
\[
s=t+\lceil\log_2(4J\mathcal B^3(R+1))\rceil,\quad
F=\max(F_0,t+\lceil\log_2(2D_*K_{\rm phys}N)\rceil).
\tag{16}
\]
These choices ensure the perturbation and scalar margins above.
One layer's rounding error is at most \(N2^{-F}\). Thus either direction
has error at most
\[
eR+D_*K_{\rm phys}N2^{-F}\le2^{-t},
\tag{17}
\]
and intermediate amplitude at most
\[
A=K_{\rm phys}R+D_*K_{\rm phys}^2N2^{-F}.
\tag{18}
\]
The inverse direction uses the exact stored inverse program on its own
input satisfying the same \(R,F_0\) contract. I claim no exact rounded
forward/inverse round trip.

If \(\widehat a=(a+ib)/2^s\) is a scalar leaf, its reciprocal
\(2^s(a-ib)/(a^2+b^2)\) has component height at most
\(2s+2\lceil\log_2(U+2)\rceil+8\).
I take the maximum of this bound and the generator children's declared
coefficient bounds, all fixed before online execution.
With \(I=\max(1,\lceil\log_2\max(1,A)\rceil)+2\), signed grid words fit
\(F+I\) bits and constant-size gate temporaries fit
\[
2F+8C_{\rm bits}+2I+32.
\]
The constants in (6), (11), (14) and (15) are polynomial in \(N,\Lambda,Q\).
The child precision formulas and (16) therefore give (2), including the
executable envelope inflation (3).

## 7. Source binding, finite evidence and limits

I authenticate and execute the unmodified `full_plan`, `parallel` and
`inverse` ASTs. I supply exact rational matrix slicing, ordinary transpose,
solve, subtraction and multiplication; wrap recursive calls only to
record their exact reference matrices; and bind `lowdisp_shear` to the
completed generator program. I preserve source assertions in its
dependencies under optimized Python.

The verifier checks direct full matrices and separate inverse references,
exact stored inversion, leading-section bounds, scalar-LDU identities,
legal downsets and upper-frontier identities. It enumerates all downsets
through size four and checks source-timed downsets on larger fixtures.
Selected physical cuts compare both identities in (13), including
simultaneous nonempty active fragments. Timing checks explicitly cover
unequal sibling lengths and zero-layer calls.

I test indefinite and half-shift Gaussian matrices, complex inputs,
small and large scalar pivots, reversed wire labels, a nonzero 512-bit
incoming fixture and a size-16 identity with zero-layer shear calls.
The finite Frobenius inequalities include the dimension factor \(N\);
they corroborate consequences of the written operator proof rather than
independently establish its sharper bounds.
Exact dense matrices remain checker oracles outside the online
representation claim. Observed heights describe completed rational
components rather than exhaustive `Fraction` internals.

I preserve the earlier FFT, triangular and generator receipts and the
fixed-head scope of James Reed's finite budget/source-seal audit at
`fdcdc269`. That audit excludes gate replay and universal-proof acceptance.
I credit Vlado Vojdanovski/PR1673 and the retained gauge-free source lineage
for the original recursive, displacement and conditioning arguments;
Chafik Boukhalfa/PR628 for certified phases; Cinna Davis for the later caller;
ToikY for the distinct same-rho Schur theorem; and classical LU/Schur methods.
Internal agents belong to the author process.

Complete Gaussian assembly, physical coefficient setup/delivery, fixed-tape
costs and independent mathematical acceptance remain open.
