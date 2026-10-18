# The coordinate component of the P112 masked eight-term decoder space

This is a statement about a finite algebraic decoder model. Its exact rank
premises are checked by this package. The differential and topological
arguments below are written mathematics, not proof-assistant verification.
There is no new physical supplier or multiplication exponent.

## 1. Object and statement

Use the P112 root lines and deleted orthogonal frame from the PR717/PR968
geometry. The live roots have squared norm two. Put

\[
Y_{ik}=\langle r_i,f_k\rangle,\qquad K=YY^T=2G.
\]

Here `Y` is a `112 x 8` integer matrix with entries in `{0,-1,1}`,
`Y^T Y = 56 I_8`, and every diagonal entry of `K` is four. Its
off-diagonal entries are zero or `+/-2`. The transpose is ordinary
transpose, including when coefficients are complex.

Let `E` consist of all diagonal positions and all off-diagonal positions
where `K_ij=0`. There are 6,720 ordered positions in `E`. These are the
even-Gram entries. The complementary off-diagonal graph has an edge
`{i,j}` when `K_ij=+/-2`; it is connected, with 2,912 edges and degree 52
at every vertex. Both facts are finite checks, not assumptions about an
arbitrary root configuration.

For `F=R` or `C`, define the masked solution space

\[
Z_F=\{(D,T)\in F^{112\times8}\times F^{112\times8}:
                (DT^T)_{ij}=K_{ij}\text{ for }(i,j)\in E\}.
\]

No conditions are imposed on odd-Gram entries. Factors have eight columns;
the definition initially permits deficient column rank. Define the orbit

\[
O_F=\{(SYA,S^{-1}YA^{-T}):
       A\in\operatorname{GL}_8(F),\quad
       S=\operatorname{diag}(s_0,\ldots,s_{111}),\quad s_i\ne0\}.
\tag{1}
\]

**Theorem.** `O_F` is open and closed in `Z_F` in the ordinary Euclidean
topology. Over `C`, it is the connected component of `(Y,Y)`. Over either
field, every continuous path in `Z_F` beginning at `(Y,Y)` remains in
`O_F`. In particular its factors retain rank eight throughout the path.

Under the inherited separate-term pairing-rank copy cost, every point in
`O_F` has cost at least 64. This cost conclusion invokes the predecessor
all-pairs eight-term floor and its stated hypotheses.

The theorem does not classify other components of `Z_F`. In particular it
does not say that every masked eight-term decoder has cost at least 64.
Nine or more columns, a changing mask or label set, and physical programs
outside the separate-term cost model are outside the statement.

## 2. The exact tangent certificate

The defining equations are polynomial. At `(D,T)=(Y,Y)`, their derivative
on a perturbation `(U,V)` is

\[
(U Y^T+Y V^T)_{ij}=0\qquad ((i,j)\in E).
\tag{2}
\]

The resulting integer Jacobian has 6,720 rows and 1,792 columns. The
primary implementation proves rank at least **1,617** by elimination
over `F_101`: a nonzero minor modulo 101 is a nonzero integer minor,
hence also a nonzero minor over `Q`, `R`, and `C`. This is a rank lower
bound in characteristic zero, not an assumption that modular rank always
equals rational rank.

Differentiate (1) at `S=I`, `A=I`. With a diagonal perturbation
`diag(a)` and an arbitrary `8 x 8` matrix `H`, the resulting directions are

\[
U=\operatorname{diag}(a)Y+YH,\qquad
V=-\operatorname{diag}(a)Y-YH^T.
\tag{3}
\]

There are 176 displayed generators: 112 choices of a unit coordinate in
`a` and 64 matrix units in `H`. Every generator satisfies (2) as an exact
integer identity. For the row-scaling generators the product derivative
is `diag(a)K-K diag(a)`, which vanishes at every constrained entry.
Gauge generators have zero product derivative at every entry.

The generator matrix has rank **175** modulo 101. It therefore supplies
175 independent null directions over characteristic zero. Conversely its
176 columns have the explicit relation `a_i=-1` for every `i`, `H=I`.
Consequently their characteristic-zero rank is exactly 175. Equation (2)
has nullity at least 175, so its rank is at most `1792-175=1617`.
Together with the Jacobian minor this proves

\[
\ker J_{(Y,Y)}=T_{(Y,Y)}O_F,\qquad
\dim_F\ker J_{(Y,Y)}=175.
\tag{4}
\]

The independent implementation separates `U+V` and `U-V` and works over
`F_3`. The symmetric equations have rank 868 on 896 variables; the
antisymmetric equations have rank 749 on 896 variables. Their sum is
again 1,617. Division by two is legitimate over `F_3` and in
characteristic zero. This second computation checks the same tangent
claim by a different matrix construction.

## 3. Tangent equality implies an open orbit here

Tangent equality alone should not be described as global rigidity. The
following local argument is needed before taking any global consequence.

Choose 1,617 defining equations whose differentials are independent at
`(Y,Y)`. The real or complex implicit function theorem gives a
175-dimensional smooth local manifold `M` cut out by these selected
equations. The full solution set `Z_F` is contained in `M` locally.

The orbit map (1) takes its values in `Z_F`: its product is `SKS^{-1}`,
which preserves the diagonal entries and all prescribed zero entries.
Normalize the orbit parameters by `s_0=1`. This removes one parameter
without changing the orbit, since a common scalar in `S` can be absorbed
in `A`. The derivative on this 175-dimensional parameter slice is
injective: the full parameter derivative has the one-dimensional kernel
identified above, and its nonzero vectors have `a_0 != 0`.

Thus the orbit map from that slice to `M` has an invertible derivative.
The inverse function theorem makes its image a neighborhood of `(Y,Y)`
inside `M`. Since the image lies in `Z_F`, the full masked solution set
and the orbit coincide in a neighborhood of `(Y,Y)`.

For any allowed fixed `S,A`, the transformation

\[
(D,T)\longmapsto(SDA,S^{-1}TA^{-T})
\]

is an invertible map of `Z_F` onto itself. It carries `(Y,Y)` to the
corresponding orbit point. The same local conclusion therefore holds at
every point of `O_F`, proving that `O_F` is open in `Z_F`.

## 4. The orbit is closed, including against loss of factor rank

Let a sequence of orbit points converge in the ambient factor space:

\[
(S_nYA_n,S_n^{-1}YA_n^{-T})\longrightarrow(D,T).
\]

Normalize each `S_n` by `s_{n,0}=1`, absorbing the common scalar into
`A_n`. Put `M_n=S_n K S_n^{-1}`. Continuity of multiplication gives
`M_n -> M=DT^T`.

For each edge `{i,j}` of the connected odd-Gram graph,

\[
(M_n)_{ij}(M_n)_{ji}=K_{ij}K_{ji}=4.
\tag{5}
\]

Both limiting entries are finite, and their product is four. Neither
limiting entry can be zero. Fix a spanning tree rooted at vertex zero.
For its oriented edge `i -> j`,

\[
\frac{s_{n,i}}{s_{n,j}}=\frac{(M_n)_{ij}}{K_{ij}}.
\]

Products of these ratios along the tree recover each normalized
`s_{n,i}`. Every factor has a finite nonzero limit, so
`S_n -> S` for an invertible diagonal matrix `S`. Passing to the limit
in `M_n=S_nKS_n^{-1}` gives

\[
DT^T=SKS^{-1},\qquad\operatorname{rank}(DT^T)=8.
\tag{6}
\]

In particular both `D` and `T` have rank eight. To recover the factor
gauge without assuming that the original sequence of gauges was bounded,
use the explicit left inverse `L=Y^T/56`, so `LY=I`. Then

\[
A_n=L S_n^{-1}(S_nYA_n)\longrightarrow A=L S^{-1}D.
\]

The limiting identity `D=SYA` and rank eight of `D` force `A` to be
invertible. Inversion is continuous near an invertible matrix, so the
second factor also converges to `S^{-1}YA^{-T}`. The limiting pair is
therefore a point of `O_F`.

This proves that `O_F` is closed in the entire ambient factor space,
and hence in `Z_F`. In particular a finite limit cannot escape through
a deficient-rank factor. Connectedness of the odd-Gram graph and the
nonzero reverse-edge products in (5) are essential to this argument.

## 5. Components and continuous searches

The orbit is both open and closed in `Z_F`. The image of a continuous
path from the connected interval `[0,1]` cannot meet both it and its
complement. Thus every exact masked eight-term path beginning at the
coordinate decoder stays in the orbit, however far its parameters travel.

Over `C`, both `GL_8(C)` and `(C^*)^112` are connected. Their product maps
continuously onto `O_C`, so the orbit is connected. Together with being
open and closed, this identifies it as the connected component of the
coordinate decoder. No connectedness assertion about the entire real
orbit is needed for the path conclusion over `R`.

This statement concerns continuous paths of exact solutions. A discrete
search can jump to another component, and an approximate path can leave
the exact constraint set. Neither is excluded.

## 6. Copy-cost consequence and its limits

For columns `d,t`, the predecessor cost is the binary rank of the label
pairing restricted to `supp(d) x supp(t)`, denoted `beta(d,t)`. The
eight-term cost is `sum_k beta(D[:,k],T[:,k])`.

Take an orbit point in (1). Removing the nonzero row scalings gives

\[
\widehat D=YA,\qquad \widehat T=YA^{-T},\qquad
\widehat D\widehat T^T=YY^T=2G
\]

on **all** entries. The complex-coefficient extension of the predecessor
eight-term all-pairs theorem applies to P112, the puncture of eight frame
lines. Its lower bound is `max(72-8,56)=64`. The real case is included.

Gauge transformations can change column supports; we do not assert
otherwise. The all-pairs theorem handles those gauge-dependent supports.
The remaining multiplication of each row by a nonzero `s_i` or `s_i^-1`
preserves the support of every individual column exactly. The masked
orbit point therefore has the same copy cost as its all-pairs decoder,
and its cost is at least 64.

The inherited all-pairs proof uses its stated hyperplane-flat
classification premise and label-cost convention. This package does not
replace that proof or establish a new physical interpretation of `beta`.

A cost floor in a sufficiently small neighborhood of `(Y,Y)` alone would
follow from persistence of the original nonzero entries, even without a
Jacobian computation. The new conclusion here is the complete orbit
classification of the coordinate component and the consequent restriction
on entire continuous paths, including paths along which supports change.

The result does not settle disconnected masked solutions, overcomplete
decoders, several interacting totals, or the cost of producing and
restoring physical helper states. No claimed improvement has been priced,
admitted by a native supplier checker, or composed into the selected
recurrence. The selected frontier and its inherited all-size/compiler,
common-label/mutable-source, hosting, precision/tape, analytic-transfer,
and bit-interface obligations remain unchanged.

## Attribution and assistance

The P112 geometry and decoder model are inherited from DreamingOfClouds'
PR717 and the PR968 model pinned in `SOURCES.json`. The coordinate cost 64
belongs to Joel Pulikkan's PR620 and
its predecessors. The eight-term all-pairs floor is supplied by
`complex-frame-pair-decoders`, with its complex extension in
`complex-decoder-field-extension-seed44` (PR1077). The new contribution
is the masked Jacobian/orbit certificate and the component argument above.
This proof was prepared with substantial OpenAI Codex assistance; separate
AI implementation and review are not independent human peer review.
New material is under the repository's Apache-2.0 license.
