# Exact displacement rank of a flattened Gaussian tensor

Base: `e54523517d0f03e58352e647c403a5af3e525a57`.

This is an all-size algebraic result about a specified exact representation.
It does not prove a multiplication runtime lower bound, discharge a retained
foundational assumption, or improve the selected conditional kappa.

## 1. Question and conventions

The one-dimensional inverse argument in
`research/capped-phase-fusion/SHALLOW-TOEPLITZ.md`, section 5, uses small ordinary
Toeplitz displacement rank to write an inverse as a short sum of products of
lower and upper triangular Toeplitz matrices. The Gaussian core in
`research/capped-fusion-t74-k554/outer/GAUGEFREE-INTERIORS.md`, section 2, is
Toeplitz after the specified normalization. A tempting grouped replacement is
to flatten a tensor of these cores into one ordinary Toeplitz-generator
representation. The theorem below gives the exact number of terms that this
particular replacement needs.

Indices start at zero. Let `Z_k` be the k-by-k strict lower shift, so
`(Z_k)_(i,j)=1` exactly when `i=j+1`. For a square matrix X define

\[
 D(X)=XZ-ZX,\qquad E(X)=X-ZXZ^{\mathsf T},
\]

using the shift of the same size. These are respectively the ordinary
Sylvester and Stein displacements; they are not tensor displacement operators.
Flatten `A tensor B` with the B index varying fastest. Every rank below is an
exact algebraic rank, not a numerical or approximate rank.

## 2. A general Kronecker--Toeplitz theorem

**Theorem 1.** Let A be an invertible m-by-m matrix over a field, m at least 1.
Let B be an n-by-n Toeplitz matrix, n at least 2, with
`B_(i,j)=b_(i-j)`. Put H=`A tensor B` and N=mn.

1. If `b_-1` is nonzero, then `rank D(H)=2m`.
2. If both `b_-1` and `b_1` are nonzero, then `rank E(H)=2m`.

No symmetry or invertibility assumption on B is required for these two
forward conclusions.

### 2.1 Sylvester displacement

If a row has fastest index greater than zero and a column has fastest index
less than n-1, the two entries of `HZ_N-Z_NH` agree by the Toeplitz identity.
Thus every nonzero entry lies in one of the m fastest-index-zero rows or one
of the m fastest-index-(n-1) columns. A matrix supported on r rows and s
columns has rank at most r+s, by splitting it into a matrix supported on those
rows and a matrix supported on those columns. Hence `rank D(H)<=2m`.

Select the rows and columns with fastest indices 0 and n-1, ordering all
index-zero rows/columns first. Set

\[
 R=b_{-1}I_m-b_{n-1}Z_m.
\]

The selected square minor is

\[
 \begin{pmatrix}
 RA&b_0(AZ_m-Z_mA)\\
 0&-AR
 \end{pmatrix}.
\]

Since R is lower triangular with diagonal `b_-1`, the determinant of this
2m-by-2m minor is

\[
 (-b_{-1}^2)^m\det(A)^2\ne0.
\]

This proves the first conclusion, including the boundary case n=2.

### 2.2 Stein displacement

An entry of `H-Z_NHZ_N^T` vanishes whenever both fastest indices are positive.
Its support is therefore contained in the union of the m fastest-index-zero
rows and columns, giving rank at most 2m. Select the rows and columns with
fastest indices 0 and 1. In the same grouped ordering the minor is

\[
 \begin{pmatrix}
 b_0(A-Z_mAZ_m^{\mathsf T})&RA\\
 AS&0
 \end{pmatrix},\quad
 S=b_1I_m-b_{-(n-1)}Z_m^{\mathsf T}.
\]

Exchanging the two block columns makes this block triangular, so its
determinant is

\[
 (-1)^m\det(RA)\det(AS)
 =(-b_{-1}b_1)^m\det(A)^2\ne0.
\]

This proves the second conclusion. The argument uses exact boundary entries,
not a genericity assertion.

## 3. Inverses and the role of persymmetry

If H is invertible, direct multiplication gives

\[
 D(H^{-1})=-H^{-1}D(H)H^{-1},
\]

so the Sylvester rank is unchanged without further assumptions.

For the Stein displacement one must first distinguish the shift orientation.
The two Schur complements of the block matrix

\[
 \begin{pmatrix}H&Z_N\\Z_N^{\mathsf T}&H^{-1}\end{pmatrix}
\]

show that

\[
 \operatorname{rank}(H-Z_NHZ_N^{\mathsf T})
 =\operatorname{rank}(H^{-1}-Z_N^{\mathsf T}H^{-1}Z_N).
\]

The right side has the reverse shift. For a tensor of Toeplitz factors let J
be full coordinate reversal. Each Toeplitz factor satisfies `J B J=B^T`,
and full reversal is the tensor of the individual reversals. Consequently
`J H J=H^T`, and also `J H^-1 J=(H^-1)^T`. Since `J Z_N J=Z_N^T`, conjugating
`E(H^-1)` by J and transposing gives the reverse-shift displacement above.
These operations preserve rank. We have proved:

**Corollary 2.** If H is a tensor of invertible Toeplitz factors and its fastest
factor has nonzero adjacent offdiagonals, then the four ranks
`rank D(H)`, `rank E(H)`, `rank D(H^-1)`, and `rank E(H^-1)` all equal twice
the product of the other factor dimensions.

The same-shift inverse Stein conclusion here uses persymmetry. The arbitrary
A hypothesis of Theorem 1 is not, by itself, the proof of that conclusion.
Nor does this argument assert that an inverse Toeplitz matrix is Toeplitz.

## 4. Normalized shifted Gaussian sections

Write a normalized contiguous Gaussian section as

\[
 B_{ij}=q^{(i-j)^2}v^{i-j},\qquad 0<q<1,\quad v>0.
\]

This is the retained normalized kernel `exp(-gamma h^2+2 gamma s h)` with
`q=exp(-gamma)` and `v=exp(2 gamma s)`, up to transposition if the source uses
the opposite difference convention. The adjacent coefficients are `q/v`
and `qv`, both nonzero. This algebraic lemma allows every real shift s;
the caller's stricter shift, conditioning and precision premises remain
unchanged.

For completeness, this matrix is invertible without appealing to a finite
conditioning experiment. Factor it as left and right diagonal matrices
around the Vandermonde matrix `V_(i,j)=(q^(-2i))^j`, for
`0<=i,j<n`. The left diagonal has entries `q^(i^2)v^i` and the right diagonal
entries `q^(j^2)v^(-j)`. Its determinant simplifies to

\[
 \det B=\prod_{k=1}^{n-1}(1-q^{2k})^{n-k}>0.
\]

Indeed, each Vandermonde factor for i<j is
`q^(-2j)(1-q^(2(j-i)))`; its power of q cancels the two diagonal products.
The powers of v cancel as well.

**Corollary 3.** Let H be a tensor of g such sections with dimensions
`n_1,...,n_g>=2`, and let `T=product n_i`. In a lexicographic ordering with
factor f fastest, all four displacement ranks from Corollary 2 equal

\[
 \frac{2T}{n_f}.
\]

The minimum over permutations of the tensor axes is therefore
`2T/max_i n_i`. Equal factor dimensions B give `2 B^(g-1)`. For two-point
factors the rank is the full dimension `2^g` in every axis ordering.
Size-one factors can simply be removed. Nonzero scalar normalization of a
factor does not change any of these ranks.

This applies to the exact normalized Toeplitz cores. Diagonal gauges,
permutations, periodic tails, holes and rounded coefficient tables can change
ordinary displacement rank. No identification with the complete physical
Reference or a finite fixed-point source is being assumed.

There is also a direct conditional application to structure-preserving
rounding. If a truncated or rounded factor remains Toeplitz, is invertible,
and retains nonzero adjacent coefficients, Corollary 2 applies to that exact
table without any Gaussian formula. One sufficient admission test is an ideal
factor whose Hermitian part is at least `mu I`, a Toeplitz perturbation of
operator norm strictly below mu, and adjacent-coefficient errors strictly
below `min(q/v,qv)`. The perturbed Hermitian part remains positive definite,
and neither adjacent coefficient vanishes. A band truncation must retain
distance one. The retained source supplies a one-factor conditioning contract,
but this package does not silently certify its full precision choice or paid
diagonal conversion. Arbitrary perturbations need not preserve the rank
equality or the Toeplitz structure.

## 5. Exact minimum number of ordinary Toeplitz-generator terms

For vectors u,v of length T, let L(u) be lower triangular Toeplitz with first
column u, and U(v) upper triangular Toeplitz with first row v. Directly,

\[
 L(u)U(v)=\sum_{k=0}^{T-1}Z_T^k u v^{\mathsf T}(Z_T^{\mathsf T})^k,
 \qquad E(L(u)U(v))=uv^{\mathsf T}.
\]

Thus an exact representation of X as a sum of r products `L(u_l)U(v_l)`
implies `rank E(X)<=r`. Conversely, factor `E(X)` as a sum of exactly
`rank E(X)` rank-one matrices and apply the displayed finite sum. Telescoping,
using the fact that the T-th power of `Z_T` is zero, recovers X.

**Corollary 4.** The minimum number of ordinary lower-times-upper Toeplitz
generator terms for either the exact H or its inverse in Corollary 3 is
exactly `2T/n_f`. It is not merely an upper bound or a failure of one generator
construction.

This gives the precise missing representation obligation in a proposed
grouped use of the one-dimensional shallow Toeplitz inverse: rank one as a
tensor does not imply bounded ordinary shift-displacement rank after flattening.

## 6. Cost interpretation and exclusions

The exact term count prevents a direct constant-term transplant of that
ordinary generator formula to these grouped matrices. It does not turn an
upper bound on generator application cost into a lower bound on runtime.
Shared work, different generators, a tensor circuit, or another controller may
still exploit separability. Source generation, frame changes, gauges, movement,
precision, restoration and the other two transforms still need their full
cost accounts in any constructive replacement. No new complete kappa follows.

In particular, for two-point factors
`H=[[A,bA],[cA,A]]` has scalar-identity block shears bI and cI and middle
diagonal blocks A and `(1-bc)A`. A direct tensor circuit applies one local
factor per axis. This simple circuit coexists with full ordinary displacement
rank. The theorem is not a lower bound for the repository's recursive Full
compiler or for all grouped/separable circuits.

## 7. Failure controls and open next questions

The verifier deliberately checks these boundaries:

- With a zero adjacent offdiagonal, the formula can fail: an identity matrix
  has Sylvester rank zero and Stein rank one.
- Singular A need not give the asserted full minor rank.
- An axis shift such as `Z_m tensor I_n` is not the full lexicographic shift;
  for `A=I_m` its commutator is zero.
- Axis reorderings are not arbitrary coordinate permutations. For two equal
  symmetric two-point factors with q=1/2, Gray order `[0,1,3,2]` makes the
  matrix ordinary Toeplitz and reduces both ranks from four to two.
- A direct local-factor tensor circuit reproduces the matrix despite the
  large global rank.

Three concrete remaining questions are quantitative stability of these rank
minors under the retained rounding errors; source-faithful grouped algorithms
using multilevel structure instead of one ordinary displacement; and the effect
of the paid gauges, actual Reference and hole completion on that algorithm.
The first requires singular-value or inverse-minor bounds, not just nonzero
determinants. The latter two require the actual inherited source and complete
movement/precision budget. None is settled by this package.

## 8. Source context, novelty scope and credit

The source manifests pin the source sections and selected record. Relevant
predecessors include the Beatty-run inverse in
[CrocSwap/integer-mult-bounds#5566](https://github.com/CrocSwap/integer-mult-bounds/pull/5566),
the fine-grid Toeplitz inverse in
[CrocSwap/integer-mult-bounds#5571](https://github.com/CrocSwap/integer-mult-bounds/pull/5571),
the complete physical periodic inverse in
[CrocSwap/integer-mult-bounds#6905](https://github.com/CrocSwap/integer-mult-bounds/pull/6905),
and the retained shallow Toeplitz construction. Their cost and error results
remain their own; this package supplies the exact flattened representation
calculation and its limitations. The overlap search was bounded and does not
prove literature-wide novelty.

Classical background is Vadim Olshevsky, Ivan Oseledets and Eugene Tyrtyshnikov,
[*Tensor properties of multilevel Toeplitz and related matrices*](https://www2.math.uconn.edu/~olshevsky/papers/tenprop_revision2.pdf).
That work distinguishes tensor properties from one-dimensional displacement
structure. This package does not claim to introduce either concept.

Prepared for @CubeJerry with substantial OpenAI ChatGPT assistance. Two
independent derivations supplied the boundary-minor argument and its extension
from two-point factors to arbitrary Toeplitz sections. Exact finite checks are
failure controls for the written all-size proof, not a substitute for it.
Apache-2.0, retaining predecessor attribution.
