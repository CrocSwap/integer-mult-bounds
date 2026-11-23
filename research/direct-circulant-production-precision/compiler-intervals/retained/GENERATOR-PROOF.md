# Complete rounded bounded-generator circuits

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0.

## 1. Input, output and inherited generator identity

I consider a rational complex matrix \(T\) of dyadic size \(m=2^d\).
Let \(Z\) be the nilpotent lower shift and \(E=T-ZTZ^T\), with rank \(r\).
The target is the dirty shear
\[
S(T)(x,y)=(x,y+Tx)
\]
on exactly \(2m\) existing complex wires. I require no zero bank.
The input lies on an \(F_0\)-bit dyadic grid and has norm at most \(R\ge1\);
the requested output error is \(2^{-t}\), with integer \(t\ge1\).
I use a rational bound \(B_E\ge\|E\|_2\). The executable takes the maximum
of the row and column component sums, which bounds both induced norms.

I execute the frozen PR4198 rational producer. For each nonzero orthogonal
residual \(v_j\) of \(E\), it chooses a dyadic \(c_j\) with
\(\|v_j\|\le c_j<2\|v_j\|\), then emits
\[
g_j=v_j/c_j,\qquad
a_j=\frac{c_j}{v_j^*v_j}v_j^*E.
\]
The orthogonal projectors sum to the identity on the column space of \(E\).
Thus
\[
E=\sum_{j=1}^r g_ja_j,\quad
\|g_j\|\le1,\quad \|a_j\|<2B_E,\quad
T=\sum_{j=1}^r L(g_j)U(a_j).
\tag{1}
\]
The last identity follows by telescoping
\(T=\sum_{k=0}^{m-1}Z^kE(Z^T)^k\). The \(a_j\) are coefficient rows;
I apply no further conjugation.

I retain the producer's scale
\[
\Gamma_j=\min\{2^e:2^e\ge\max(1,2\ell(a_j))\},\quad
\ell(a)=\sum_k(|\Re a_k|+|\Im a_k|),
\]
and put \(P_j=I+U(a_j)/\Gamma_j\), \(G_j=\Gamma_jL(g_j)\).
Then \(P_j\) satisfies the component-l1 admission used in
[TRIANGLE-PROOF.md](TRIANGLE-PROOF.md), and
\(\|P_j\|\le3/2,\ \|P_j^{-1}\|\le2\).
The source realizes the upper triangular map by reversing its source wires.

I use the rational bounds
\[
\alpha=2rmB_E,\qquad K_G=2m+16mB_E.
\tag{2}
\]
Indeed \(\|L(g_j)U(a_j)\|\le2mB_E\), and
\[
\Gamma_j\sqrt m
 <2\sqrt m+8\sqrt2\,mB_E\le K_G.
\]
The scaled shear's coefficient component sum is at most
\(\sqrt2K_G<2K_G\). I budget the approximation of \(G_j\) itself;
approximating \(L(g_j)\) first and multiplying by an uncharged
\(\Gamma_j\) would not meet this contract.

## 2. Paired compensation and additive defects

I retain the source's four calls:
\[
P_j;\quad S(G_j);\quad P_j^{-1};\quad S(-G_j).
\tag{3}
\]
I compile \(\widehat P_j\) and reuse its exact stored inverse.
For the positive shear I use the certified FFT construction.
For its compensation I reuse the same unitary tables and negate the
stored spectral multipliers, preserving the source's cyclic-then-negacyclic
order. The two unrounded shear endpoints are exactly
\(S(\widehat G_j)\) and \(S(-\widehat G_j)\).

Negating a nearest-grid value gives a nearest-grid value of the negative
exact quantity, so this paired rule retains the same multiplier-error
bound. At half-grid ties it need not agree with independent rounding
toward positive infinity. The verifier includes that discrepancy as a
control. I do not replace the negative child with a reversed whole
positive-shear program.

For \(\|\widehat P_j-P_j\|,\|\widehat G_j-G_j\|\le\eta\le1/4\),
the exact stored-coefficient program has endpoint
\[
(x,y)\longmapsto(x,y+\widehat G_j(\widehat P_j-I)x).
\]
Write \(T_j=G_j(P_j-I)\) and
\(\widehat T_j=\widehat G_j(\widehat P_j-I)\). Then
\[
\|\widehat T_j-T_j\|
\le K_G\eta+(1/2+\eta)\eta\le(K_G+1)\eta.
\]
The completed terms restore the same source bank, so their endpoints
compose to \(S(\sum_j\widehat T_j)\). Consequently
\[
\boxed{\|\sum_j\widehat T_j-T\|\le
\Delta:=r(K_G+1)\eta.}
\tag{4}
\]
I need no generic product-of-perturbed-matrices bound across completed
generator terms. This additive estimate uses exact stored-coefficient
restoration; data-rounding errors receive a separate bound below.

## 3. Checkpoint prefixes and suffixes

Assume \(\Delta\le1\). Any preceding or remaining sum of approximate terms
has norm at most \(a_*=\alpha+1\).
For the current term write \(p=\widehat P_j\), \(h=\widehat G_j\),
\(A=\sum_{i<j}\widehat T_i\) and \(C=\sum_{i\ge j}\widehat T_i\).
We have \(\|p\|\le2\), \(\|p^{-1}\|\le4\) and
\(\|h\|\le k_*=K_G+1\).

Put \(\mathcal L(B,D)=\left[\begin{smallmatrix}B&0\\D&I\end{smallmatrix}\right]\).
The four prefixes ending at the current term's checkpoints are
\[
\mathcal L(p,A),\quad
\mathcal L(p,A+hp),\quad
S(A+hp),\quad S(A+h(p-I)).
\tag{5}
\]
The corresponding remaining suffixes are
\[
\mathcal L(p^{-1},Cp^{-1}),\quad
\mathcal L(p^{-1},Cp^{-1}-h),\quad
S(C-hp),\quad S(C-h(p-I)).
\tag{6}
\]
I obtain (6) by multiplying \(S(A+C)\) by the inverse of each prefix.
No matrices in this calculation need to commute.

Using
\[
\mathcal L(B,D)^{-1}=\mathcal L(B^{-1},-DB^{-1}),\quad
\|\mathcal L(B,D)\|\le\max(\|B\|,1)+\|D\|,
\]
I bound (5), (6) and their inverses by
\[
\boxed{\widehat C=4+4a_*+2k_*=10+4\alpha+2K_G.}
\tag{7}
\]
For example, the inverse of the second prefix has lower-left block
\(-Ap^{-1}-h\), and the inverse of the second suffix has block
\(-C+hp\). Their bounds contain no product of all previous shear norms.
For the fourth checkpoint I use the preceding and remaining *completed*
sum bounds \(a_*\).

## 4. Physical logical gates and one data grid

The triangular child's internal prefix/suffix and inverse bounds are
\(3200m^3\). For the scaled shear, the corresponding bound is
\(1+M+2v\le2+2K_G\), where \(M\le\sqrt2K_G\) and \(v\le1/2\).
Therefore I take
\[
H_0=\max(3200m^3,2+2K_G),\qquad
K_{\rm exec}=H_0\widehat C.
\tag{8}
\]
An unfinished child combines with a checkpoint prefix or suffix.
Thus \(K_{\rm exec}\) bounds complete-program physical gate prefixes,
suffixes and their inverses. An arbitrary segment has bound
\(K_{\rm exec}^2\).

The retained schedules give
\[
D=r(8d^2+32d+18),\qquad
G=rm(4d^2+24d+22)
\tag{9}
\]
as layer and gate upper bounds. I sum two triangular and two shear
children per generator. For \(r=0\), (1) gives \(T=0\) and I emit the
identity with no gates.

One layer rounds at most \(2m\) complex outputs. Nearest component
rounding contributes norm at most \(\sqrt m\,u\le m u\), with \(u=2^{-F}\).
Equations (4) and (8) imply
\[
\boxed{\|\widehat z-S(T)z_0\|
\le\Delta R+D K_{\rm exec}m u.}
\tag{10}
\]
The source restoration error is at most the second term because the
unrounded program restores that bank exactly. At intermediate states I use
\[
A=K_{\rm exec}R+D K_{\rm exec}^2m u.
\tag{11}
\]
I retain the larger arbitrary-segment factor in this amplitude bound.

## 5. Explicit allocation and widths

For \(r\ge1\), choose
\[
s=t+\left\lceil\log_2(4(r+1)(K_G+1)(R+1))\right\rceil,\quad \eta=2^{-s}.
\]
Let \(B_m=100m^3\), \(q_m=2d+1\), and
\[
\ell=s+\lceil\log_2(8q_mB_m^3)\rceil,\qquad
\overline M=\max(6,2K_G).
\]
I apply the triangular allocation with target \(2^{-s}\) and radius one,
using its unrounded operator bound. I then raise its phase and multiplier
precisions to the common values
\[
\begin{aligned}
P&=\max\{\ell+\lceil\log_2(48(d+1))\rceil,\
          s+\lceil\log_2(32(d+1)(\overline M+1))\rceil\},\\
S&=\max(\ell+2,s+4),\\
F&=\max\{F_0,\ t+\lceil\log_2(2D K_{\rm exec}m)\rceil\}.
\end{aligned}
\tag{12}
\]
Higher \(P,S\) only reduce the child defects; leaf precision stays \(\ell\).
I use no child-specific data grids. I flatten the complete program and
round its data on the single \(F\)-grid.

The triangle operator defect is at most \(\eta\).
The scaled shear defect satisfies
\(4(d+1)M2^{-P}+2^{1-S}\le\eta\).
Equations (4) and (12) give
\(\Delta R<2^{-t}/4\) and \(D K_{\rm exec}m2^{-F}\le2^{-t}/2\).
Thus (10) is below the requested target.
For \(r=0\), the executable replaces the zero logarithm argument by one;
the defect and rounding terms remain zero.

I include the scaled multipliers in the common coefficient bound:
\[
C_{\rm bits}=\max\{4P+24,\ S+\lceil\log_2(\overline M+2)\rceil+2,\
                         2\ell+16\}.
\]
The last term covers the exact reciprocals of stored triangular leaves.
With \(I=\max(1,\lceil\log_2\max(1,A)\rceil)+2\), I use signed
grid-record width \(F+I\) and temporary allowance
\[
2F+8C_{\rm bits}+2I+32.
\tag{13}
\]
Since \(r\le m\), these online widths are
\[
O(F_0+t+\log m+\log(1+B_E)+\log R).
\]
If the caller supplies \(r=O(\log N)\) and \(m\le N\), (9) gives
\(O(\log^3N)\) logical depth. I do not prove that caller's rank premise
through this finite replay.

## 6. Source binding, evidence and limits

I retain PR4198's exact producer bytes and original identity in
`vendor/STEIN-PROVENANCE.json`. The sibling PR commit is not an ancestor
of this PR; I pin the retained local bytes through their archive commit.
The new proof above rederives the generator identities and norm bounds
needed here. I reference PR4198's separate preprocessing proof for context;
I do not claim a new complete setup or physical-delivery bound.

I execute the original exact Schur walk with one collection hook,
preserving its assertions. I run it in the producer's exact-complex type
cohort, then convert through rational real/imaginary fields.
I extract the literal seven-statement generator macro, including source
reversal and the same `transform` object for inverse execution.
I replace the former exact matrix callbacks with actual certified gates.

The verifier reconstructs both Stein identities, checks the full circuit
against a separately assembled matrix \(S(T)\), and measures rounded
dirty-bank errors and canonical widths. Exact dense matrices remain
checker oracles outside the online representation claim. Finite
Frobenius checks corroborate consequences of the written operator proof;
they do not independently establish its sharp norm bounds.

I credit Vlado Vojdanovski/PR1673 for the generator/compiler identity,
Schur producer and retained schedule; Chafik Boukhalfa/PR628 for certified
phases; Cinna Davis for the later caller; and the classical structured-matrix
and Gram-Schmidt lineage. Internal agents belong to the author process.
Full Toeplitz/Gaussian recursion, physical coefficient setup/delivery,
fixed-tape costs and independent mathematical acceptance remain open.
