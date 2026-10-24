# Cache tree identities and the selected center intersection bound

## Frames and actual paid ranks

Let a field have \(2^n\) binary-address positions. A Clifford frame F has
exact unitary operator \(G_F\). Set
\(L_0=\{(0,z):z\in\mathbb F_2^n\}\) and
\(\Lambda_F=F^{-1}L_0\), using the induced binary symplectic action.
For the actual transport \(G_B G_A^{-1}\), its Fourier rank is

\[
r(A,B)=n-\dim(\Lambda_A\cap\Lambda_B).
\tag{1}
\]

Indeed its B block measures the dimension outside \(L_0\) of
\(BA^{-1}L_0\). Its kernel is the intersection of \(L_0\) with that
image. Pulling the intersection back through B gives (1).
Phases and monomial factors do not change this rank, but must still be
implemented. This rank is an integer metric on Lagrangian charts; different
Cliffords with the same chart can have distance zero and nontrivial paid
ordinary monomial work.

For the repository's canonical subspace frame \(C_U\), direct substitution
gives

\[
\Lambda(U)=\{(x,x+z):x\in U,\ z\in U^\perp\}.
\]

Consequently
\(r(U,V)=\dim U+\dim V-2\dim(U\cap V)\), including non-nested pairs.
`primitive.py` independently checks this against exact lowered Clifford
operators for every pair of the 16 subspaces of \(\mathbb F_2^3\), including
all input columns and absolute phase. The binary chart formula is the
algebraic statement; these finite tests check its convention in the retained
implementation.

## A cache is a snapshot with a representation

Fix a logical column x. At each cache node v maintain physical value
\(z_v=G_vx\). An owned child w is created by copying \(z_v\), then applying
the fully paid transport \(G_wG_v^{-1}\). Thus

\[
G_wG_v^{-1}z_v=G_wx.
\tag{2}
\]

Induction proves the invariant on any typed-copy tree. At a terminal,
\(y_i\leftarrow y_i+\alpha_i z_i\) supplies precisely the requested
contribution. Internal caches carry no productive-owner credit. Leaves can
be processed in their original order using a reusable owned field if the
retained parent cache remains unchanged.

The logical snapshot is an operator row on the independent caller inputs.
For a cached row R, a later required row S may use the cache when
\(S=qR\) for an explicitly known scalar q, by changing the ADD coefficient.
Writes to the original owner are harmless only when this row relation still
holds. The invariant concerns expressions, not register identifiers. In a
longer caller the row algebra must include all address operators, coefficients
and phases; the small scalar-row control here is not such a caller analysis.

Let the desired main endpoint be
\((x,y_1,y_2)\mapsto(x,y_1+A_1x,y_2+A_2x)\).
Its raw inverse transpose is

\[
(x,y_1,y_2)\mapsto
(x-A_1^Ty_1-A_2^Ty_2,y_1,y_2).
\tag{3}
\]

Since G is unitary, \(G^T=\overline G^{-1}\). Reversing the fanout into a
gather therefore uses conjugate transports in the reversed directions.
`dual_program` implements (3), not a forward move with a reversed name.
The inverse transpose is of the main endpoint; owned CLEARs make the full
scratch-inclusive map noninvertible. Arbitrary owned entries are erased under
the retained owned-erasure contract and both owned fields leave zero.

Equations (2) and (3) hold for arbitrary field columns. Lifting each block by
\(I_b\otimes G\) proves the same identities with b idle positions, and block
composition proves arbitrary repetitions. Tensoring address operators does
not merge owner roles or turn their sum into independent output credit.
This is an all-width algebraic identity under the retained Gaussian and
owned-erasure primitives. A bit-cost implementation still needs those
primitives' precision, storage, normalizer and tape contracts.

## A sharp three terminal example

Take \(U=0\), \(V_1=\langle1,2\rangle\),
\(V_2=\langle1,4\rangle\). The three terminals have pairwise distance 2.
Their shared line \(M=\langle1\rangle\) has distance 1 to each.
Copy x to owned Z and move U to M; copy Z to owned W, move M to V1,
ADD to Y1 and clear W; repeat for V2; clear Z. The program has three
rank-1 moves and the ordinary passes recorded in RESULT.json.

For \(0<s\leq1\), the minimum recursive moment over typed-copy cache trees
connecting these terminals is exactly

\[
\min\{2\,2^s,3\}.
\tag{4}
\]

To prove the lower bound, remove nonterminal leaves and suppress degree-two
vertices. Suppression does not increase moment: the metric triangle
inequality and \((a+b)^s\leq a^s+b^s\) allow replacement of a path by
one direct edge. Contract zero-rank edges for this rank-only argument.
A reduced tree connecting three terminals is either a path through one
terminal or a three-edge tree with one nonterminal junction. The former
costs \(2\,2^s\). In the latter all three positive integer edge ranks are
at least 1, hence the cost is at least 3. These bounds apply to arbitrary
Clifford intermediate charts. The separate transfers and the shared line
attain them. Ordinary monomial costs are outside this rank-only optimum.

At \(s=1-0.00302015\), the frozen gain is
\(2\,2^s-3=0.9916351247756209043\ldots\).
The exact rational interval engine certifies its positive sign and the
negative sign after charging one more H1. In fact the repaired saving is
\(4(2^{-\kappa}-1)<0\) for every \(\kappa>0\).
At \(s=1/2\) the separate
transfers win. This sign reversal is a useful control on treating rank mass
as a sufficient cost statistic.

If Z is already a caller-supplied observation \(C_Mx\), omit its creation
and final erasure. One owned W then suffices for two marginal H1 moves.
Z is returned unchanged. Its relation to x and all costs outside the module
are preconditions; the module does not manufacture that observation.

## Intersection loss bounds any typed tree

For a rooted tree of n-dimensional charts, in parent-before-child order let
\(I_k=\bigcap_{v\leq k}\Lambda_v\). When child w of p is added,
\(I_{k-1}\subseteq\Lambda_p\), so the quotient map injects

\[
I_{k-1}/(I_{k-1}\cap\Lambda_w)
\hookrightarrow
\Lambda_p/(\Lambda_p\cap\Lambda_w).
\]

The lost dimension is at most \(r(p,w)\). Summing proves

\[
\sum_e r_e\geq n-\dim\!\bigcap_v\Lambda_v.
\tag{5}
\]

Matarener's nested path argument is the predecessor of this proof. The
extension uses the actual inverse-image Clifford chart and permits branching
and arbitrary intermediate Lagrangians. For \(0<s\leq1\), subadditivity gives
\(\sum_e r_e^s\geq(\sum_e r_e)^s\).

For canonical terminal frames \(U_i\), set \(I=\bigcap_iU_i\) and
\(J=\sum_iU_i\). The explicit chart formula gives

\[
\dim\bigcap_i\Lambda(U_i)=\dim I+n-\dim J.
\tag{6}
\]

Adding arbitrary intermediate vertices can only shrink that intersection.

## Application to all selected center blocks

Keep #4470's chronological scalar demand, coefficients, fixed warps and helper
boundaries. Persistent L roles retain the original monotone subspace-frame
rules. Every source/target scalar contact is in a common canonical frame.
The predecessor's interval propagation forces a source frame R to contain
\(A=\operatorname{Low}(\mathrm{source})\), and every target frame Fi to
lie in \(B_i=\operatorname{Up}(\mathrm{target}_i)\).

Allow the owned payload to travel along arbitrary Clifford intermediates and
to branch by typed copies. It carries the same specified snapshot; combining
independent payloads is outside this contract. From (5) and (6), its rank mass
is at least

\[
\begin{aligned}
\dim(R+\sum_iF_i)-\dim(R\cap\bigcap_iF_i)
&\geq\dim R-\dim(R\cap\bigcap_iB_i)\\
&\geq\dim A-\dim(A\cap\bigcap_iB_i).
\end{aligned}
\tag{7}
\]

The last inequality is the injection
\(A/(A\cap X)\hookrightarrow R/(R\cap X)\).
For a dual gather, apply the same argument to the transposed typed-copy tree
with conjugate charts; intersection dimensions and edge ranks are preserved.

`center.py` rebuilds the selected local word, recovers paid profile
`{1:2237,2:388,3:494,4:147,5:36,8:8}` in both orientations, and propagates
all original contact intervals. For all eight blocks in each orientation,
it finds \(\dim A=8\) and \(A\cap\bigcap_{i=1}^{22}B_i=0\).
Thus every such tree pays rank mass at least 8 and moment at least \(8^s\).
The existing single H8 attains the bound. The actual terminal-chart
intersection independently gives the same loss eight.

This closes the predecessor's stated non-nested-C question under unchanged
persistent/contact constraints. It does not cover changed cross-frame contact
interfaces, changed scalar graphs or helper boundaries, new observations, or
general circuits mixing independent payloads. Such changes alter the premises
of (7). In particular the bound must not be transferred unchanged to the
split-contact or paid-history continuations.
