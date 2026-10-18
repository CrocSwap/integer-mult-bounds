# Exact minimum eight for the fixed order-four target

This is a computer-assisted finite theorem in an explicitly changed register
model. It is not a theorem about unrestricted integer-multiplication algorithms.

## 1. Alphabet, target and scalar normalization

Let `G=GL_3(F2)`, `R=F2[G]`, and

\[
 h=\begin{pmatrix}0&1&0\\0&0&1\\1&1&1\end{pmatrix}.
\]

There are exactly two scalar register roles. The target in `M_2(R)` is
`T=diag([h],[h])`; equality of every formal coefficient is required. A free
operation is any `B in GL_2(F2)`, using the identity group label. A paid unit is

\[
 D_N(g)=I+([g]+1)N,\qquad
 g=I+E_{ij},\ i\ne j,\qquad
 N=uv^T,\quad u,v\in\mathbb F_2^2,\quad v^Tu=1.
\]

No address operation is free. There are no extra roles, clean-only input
promises, copies or erasures. Each paid occurrence costs one, including undo.
For each of the three nonzero `u`, exactly two `v` satisfy `v^Tu=1`; these
are precisely the six rank-one binary idempotents.

Moving scalar basis changes to one end conjugates `N`, preserving the complete
six-projector alphabet. Augmentation `[g] -> 1` maps all paid units and `T` to
`I`. Therefore the remaining scalar matrix must be `I`. Every legal circuit
with `k` paid calls is a product of `k` of the 36 specified units. This argument
is the normalization used in Gareth Davidson's PR #1333, credited here.

## 2. The natural relaxation is sufficient for exclusion

The natural representation extends linearly to an algebra homomorphism
`rho: F2[G] -> M_3(F2)`. On the two-register space, reorder coordinates with
address coordinate first. A paid unit becomes

\[
 \rho_2(D_N(I+E_{ij}))=I_6+E_{ij}\otimes N,
 \qquad \rho_2(T)=h\otimes I_2.
\]

Every such six-dimensional matrix is an involution, since `E_ij^2=0`.
Consequently, if no word of length at most seven reaches `h tensor I_2` in
this matrix alphabet, no formal word of those lengths reaches `T`.
No injectivity of `rho` is needed for this implication.

In fact `rho` is not injective even when augmented data are retained. Write
`q=[1]+[h]+[h^2]+[h^3]`. Since `h` has order four, `q` is a nonzero formal
element. Direct exact matrix addition gives
`I+h+h^2+h^3=0`, and its augmentation is also zero. Thus replacing an
off-diagonal zero of `T` by `q` preserves its natural image and augmentation
but changes the formal endpoint. This is an explicit checker control, not a
claim that the perturbed endpoint is attainable by a shorter legal word.

## 3. Complete finite lower-bound certificate

Breadth-first traversal starts at `I_6`. At each depth, expand **every** state
in the previous new layer by **all 36** generators. Deduplicate only by exact
matrix equality, retaining each state at its shortest distance. By induction,
these are precisely the distance layers; a state seen earlier can use the
same future suffix and therefore need not be re-expanded at a greater depth.
All arithmetic is over `F2`; no floating-point or probabilistic hash comparison
is used for membership or cross-implementation equality.

The verified layer cardinalities through depth four are

\[
 (1,36,816,14694,225528),
\]

and the total directed expansion count is
`36*(1+36+816+14694)=559692`. Let `B_d` be the union of layers through `d`
and `U=h tensor I_2`. The certificate checks

\[
 \#\{p\in B_3 : pU^{-1}\in B_4\}=0.\tag{1}
\]

Every word of length at most seven can be split as `U=A B`, with `A` of
length at most four and `B` of length at most three. Taking `p=B` gives
`p U^-1=A^-1 in B_4`, because the generators are involutions. Conversely a
meet gives `U=(pU^-1)^-1 p`, of length at most seven. Thus (1) is a complete
exclusion, not a heuristic search. It includes all shorter and odd lengths.

The independent implementation enumerates scalar projectors from all 16
binary 2x2 matrices and uses dense 6x6 row tuples, register-major coordinates
and right multiplication. Its full layer sets equal the primary packed-row
left-product sets after coordinate conversion. Independently, it tests
`U p^-1 in B_4` for every `p in B_3`, computing inverses by binary Gaussian
elimination. This second test also has zero meets. Layer SHA256 values serve
only as deterministic receipts; acceptance compares the actual complete sets.

## 4. Attained formal upper bound and direct length

In chronological order, the four address gates are

\[
 (i,j)=(1,0),(0,1),(2,1),(1,2),\qquad x_i\leftarrow x_i+x_j.
\]

Their successive row-bitmask matrices are
`(1,2,4) -> (1,3,4) -> (2,3,4) -> (2,3,7) -> (2,4,7)`.
Thus the final address map is `h`. The exact direct Cayley census has distance
layers `1,6,24,51,60,24,2`, totaling
`(8-1)(8-2)(8-4)=168=|GL_3(F2)|`, and places `h` at distance four.
A separate enumeration of all 512 binary matrices, keeping rank three,
agrees on every direct distance. Also `h^4=I`, `h^2!=I` and `rank(h-I)=2`.

For every scalar idempotent `N` and group labels `a,b`, expansion gives
`D_N(a)D_N(b)=D_N(ab)`. Apply the four chronological gates with `N=E_00`,
then the same four with `N=E_11`. The result is exactly `diag([h],[h])`.
Each role receives four paid calls; the other role is fixed during those
four calls. There are eight total calls, no other roles, no scalar basis
changes and no leftover restoration operation. The identity is in the formal
algebra, so it holds on every module and for arbitrary input values in both roles.

The coefficient-bitset implementation checks all four formal matrix entries.
A separate set-based implementation acts on all 336 basis vectors of the
faithful left regular module. This representation is faithful because an
algebra element acting on the identity basis element recovers that element;
the register-matrix extension is faithful for the same reason column by column.
Together with Section 3, the minimum is exactly eight.

## 5. Scope and attribution

The finite exclusion fixes two scalar registers and the six coordinate-CNOT
labels. It proves neither the same lower bound with extra restored dirty
registers nor an unrestricted direct-sum theorem. If rank-two scalar
projectors were charged one unit, the same four address gates would apply to
both roles in four units; that is a different alphabet and an explicit scope
control. Allowing arbitrary rank-one address maps also changes the problem.

No rational-address source is reduced modulo two. No physical bit supplier,
all-size compiler, common-label realization, hosting, precision/tape,
analytic transfer, selected cold replay or Lean theorem is established.
The code-disjoint implementations were prepared in the same session, without
an independent human proof review.

This account's PR #1414 posed the higher-dimensional follow-up to Gareth
Davidson (@bitplane)'s PR #1333. The surrounding abelian register lineage is
credited to eumemic, Ali Romman and David Govea. No predecessor implementation
is imported, and no broad literature-priority claim is made.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
