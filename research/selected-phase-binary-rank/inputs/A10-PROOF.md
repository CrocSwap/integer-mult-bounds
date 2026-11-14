# Pointwise arbitrary-order rank at the retained narrow-core widths

**Scoped exact theorem; no new kappa.** Canonical base:
`e54523517d0f03e58352e647c403a5af3e525a57`.
The immediate mathematical predecessor is
[085b30f8e036f69421d5953d0993ac4974ec3f24](https://github.com/CubeJerry/integer-mult-bounds/commit/085b30f8e036f69421d5953d0993ac4974ec3f24),
whose exact proof is retained as `inputs/A9-PROOF.md`.

## 1. Statement and precise interface

Let g>=1, N=2^g, let s_1,...,s_g be distinct odd primes, t_i positive
integer powers of two, and alpha a common positive integer. Define

\[
 q_i=\exp(-\pi\alpha^2t_i/s_i),\qquad
 H=\bigotimes_{i=1}^g\begin{pmatrix}1&q_i\\q_i&1\end{pmatrix},
 \qquad R_N=2\left\lceil\frac{N+3}{5}\right\rceil,
 \qquad r=\min\{R_N,s_{\min}-1\}.
 \tag{1}
\]

Here s_min=min_i s_i. Both entries in the minimum are even. Let Z be the
N-by-N nilpotent lower shift, Z_(j+1,j)=1, with no cyclic wrap, and write
E(A)=A−ZAZ^T.

**Theorem 1.** For every simultaneous row/column permutation P,

\[
 \operatorname{rank}E(PHP^T)\ge r,\qquad
 \operatorname{rank}E(PH^{-1}P^T)\ge r.                       \tag{2}
\]

This is pointwise for every tuple satisfying (1); it has no unspecified
generic exception. The full predecessor bound R_N holds when R_N<s_min,
with the simpler sufficient condition N<s_min. No coprimality condition
between alpha and any s_i is needed.

The tensor is the **exact unshifted normalized two-point narrow core**.
Section 5 binds its widths to the retained source and states the limits of
that identification. The theorem asserts no Stein-rank bound for a shifted,
chirped, periodic, rounded or larger matrix merely because that matrix
contains, or is similar to, this core.

## 2. Every smaller even degree has a unit coefficient certificate

The predecessor proves the following statement for indeterminates Q_i and
any ordered list of the binary vertices. Some nonzero XOR mask v has a
translation-matching Stein matrix E(P_v) with a principal minor of even
size r_v>=R_N and determinant ±1. After removing two adjacent vertices
from every alternating cycle, its induced signed graph is a disjoint union
of even paths. The open path and all retained edges have weights ±1.
The same principal Gaussian minor has coefficient ±1 at `(Q^v)^r_v`, where
Q^v=product_(i:v_i=1) Q_i. Its proof is retained and credited, rather than
replaced by finite examples.

**Lemma 2 (even trimming).** For every even integer k with 0<=k<=r_v,
there is a principal subminor of E(P_v) of size k and determinant ±1.
For k>0, the corresponding Gaussian minor is a nonzero integer polynomial
in Q_1,...,Q_g, of individual degree at most k.

**Proof.** Orient each retained path from an endpoint. Its length in
vertices is 2a_j for an integer a_j>=1. Choose integers 0<=b_j<=a_j whose
sum is k/2, for example greedily. Retain the first 2b_j vertices of path j.
There are no edges between distinct paths, and each retained nonempty
component is again an even path. An even-path adjacency determinant has
one perfect matching; expansion gives determinant ±1. Empty components
contribute the empty determinant 1. Thus the resulting minor is ±1.

Every binary Gaussian entry is a squarefree monomial Q^w; each Stein entry
is a difference of at most two such monomials. A size-k determinant has
individual degree at most k. To obtain exponent k on every variable selected
by v and exponent zero on every other variable, each of its k chosen entry
monomials must be Q^v. The coefficient of `(Q^v)^k` is therefore precisely
the retained minor of E(P_v), namely ±1. This proves noncancellation, even
in characteristic 2. The pointwise specialization below is over the reals.

These are principal minors of the full matrix E(H). We do not replace them
by E of a compressed principal submatrix of H, which would change Z.

For Theorem 1, take k=r. Since r_v>=R_N>=r, the result is a nonzero integer
polynomial f_P satisfying

    degree_(Q_i) f_P <= r < s_i for every i.                    (3)

We specialize each order's size-r minor separately. Specializing the
predecessor's product over all N! orders would violate this degree guard.

## 3. CRT separation and the transcendental base

The separation fact is slightly more general than the source prime case.

**Lemma 3.** Let m_i>=2 be pairwise coprime integers and let u_i be positive
integers coprime to m_i. Put M=product_i m_i and e_i=u_i M/m_i. Then the map

    (a_1,...,a_g) -> sum_i a_i e_i

is injective on the integer box 0<=a_i<m_i.

**Proof.** If the weighted sums for a and b agree, reduce their difference
modulo m_k. Every term except k is divisible by m_k, leaving
`(a_k-b_k)u_k(M/m_k)=0 mod m_k`. Both u_k and M/m_k are invertible modulo
m_k, so a_k=b_k modulo m_k. Their difference has absolute value below m_k,
hence a_k=b_k. This holds for every k.

Consequently substitution Q_i=z^e_i sends any nonzero polynomial over Q
whose individual degrees are below m_i to a nonzero univariate polynomial
in z: its nonzero monomials cannot merge. This is a bounded-degree statement,
not unrestricted algebraic independence.

For (1), let S=product_i s_i and use

\[
 z=\exp(-\pi\alpha^2/S),\qquad e_i=t_iS/s_i,\qquad q_i=z^{e_i}.
 \tag{4}
\]

The e_i are positive integers. Distinct primes are pairwise coprime and odd
primes are coprime to powers of two, so Lemma 3 applies. The common alpha
is inside z, rather than each e_i; no condition gcd(alpha,s_i)=1 is needed.

**Classical transcendence input.** The Gelfond-Schneider theorem states that
an algebraic base different from 0 and 1 raised to an algebraic irrational
power is transcendental, with a specified value of its complex logarithm.
Choose base -1, logarithm i*pi, and exponent i alpha^2/S. That exponent is
algebraic, nonzero and nonreal, hence irrational. Its specified power is
exactly z in (4). Therefore z is transcendental.

The primary historical source is A. Gelfond, *Sur le septieme probleme de
Hilbert*, Bulletin de l'Academie des Sciences de l'URSS (1934), no. 4,
623-634, especially the logarithm-ratio theorem on p. 628; the official
[record and full text](https://www.mathnet.ru/eng/im4924) were read.
Schneider's independent 1934 proof retains its classical credit. This
package cites the theorem; it does not re-prove or numerically verify it.

By (3), Lemma 3 makes f_P(z^e_1,...,z^e_g) a nonzero integer polynomial in
z. It cannot vanish at a transcendental number. Thus the size-r minor of
E(PHP^T) is nonzero. This proves the first inequality in (2) for each P,
and therefore for all P at the same declared source tuple.

## 4. Inverses and the exact dense-generator consequence

Every factor of H has eigenvalues 1±q_i>0, so H is positive definite and
invertible. For any invertible matrix A, the two Schur-complement rank
expressions of the block matrix [[A,Z],[Z^T,A^-1]] give
`rank E(A)=rank(A^-1−Z^T A^-1 Z)`. Apply this identity to A^-1. With J the
reversal permutation, JZJ=Z^T, and hence

    rank E(A^-1) = rank E(JAJ).                               (5)

Reversal is another allowed vertex order. The pointwise forward result
proves the inverse result, without a persymmetry premise.

For ordinary lower/upper triangular Toeplitz factors L(u),U(v),
E(L(u)U(v))=uv^T. An exact sum of k such products needs k>=rank E(A).
Every order of the forward or inverse core therefore needs at least r
terms. Separately storing both full length-N vectors of each term requires
at least 2Nr scalar slots in that specified format.

That count is not a general space/time or multiplication lower bound. It
leaves shared, implicit, compressed, sparse and tensor generators, other
displacement operators and algorithms open. It supplies no finite-bit
representation of exact transcendental coefficients. Approximation and
coefficient production need separate error and cost arguments.

## 5. Exact retained source identification and exclusions

The byte-pinned sources are `inputs/FINE-PRIME-PADDING.md` and
`inputs/GAUGEFREE-INTERIORS.md`, retained from
`research/native-kappa-30201655/modern-sources/` at the canonical base.
DEPENDENCIES.json records their blobs, SHA256 hashes and exact provenance.

FINE-PRIME section 1 supplies the eventually admissible distinct odd source
primes, dyadic target sides `t_i in {r_source,r_source/2}`, and

    (1−2 eta_p)t_i < s_i <= (1−eta_p)t_i,
    eta_p=1/(4p^2), rho_i=t_i/s_i=1+theta_i.                   (6)

Its prime-existence argument is credited source work, not re-proved by this
package. Section 2 sets the common legal integer

    alpha=ceil(sqrt((4/pi) log(16p))),  a=pi alpha^2.           (7)

GAUGEFREE section 2, Lemma 2.2, gives the narrow factor on a constant-offset
cell stretch. On one axis, write rho=1+theta, h=j−i, tau_i=i−m, and
beta_i=beta_0+theta tau_i. Its exact identity is

    N_ij = exp(a theta(tau_i^2−tau_j^2))
           exp(−a rho h^2−2a beta_0 h).                     (8)

Here tau denotes a centered coordinate; the dyadic target side in (6)
remains a different quantity. The normalized shifted Toeplitz kernel is

    G'_s(h)=exp(−gamma h^2+2gamma s h),
    gamma=a rho, s=−beta_0/rho, G'_s(0)=1.                  (9)

For the source convention h=j−i, put D_xx=exp(−2gamma s x). Then the
matrix in (9) equals D H0 D^-1, where H0_xy=exp(−gamma(y−x)^2).
The remaining factor in (8) is the separate chirp similarity. Thus its
unshifted normalized two-point core on coordinates x=0,1 is exactly
[[1,exp(−gamma)],[exp(−gamma),1]], with gamma=pi alpha^2 t_i/s_i.
Tensoring selected distinct original axes identifies (1) with those exact
core widths. A translation of the two local coordinates does not change
the unshifted differences.

This is an algebraic identification of a normalized core. The actual
shifted kernel and its physical chirp are not silently replaced by that
core, and neither diagonal conjugation is free. Ordinary Stein rank is
not invariant under diagonal similarity. For q_1=q_2=1/2 in the Gray
order [0,1,3,2], the unshifted four-point kernel has Stein rank 2. With
D=diag(1,2,3,4), the determinant of E(D H D^-1) is -3/512, so its rank
is 4. Reversing the similarity decreases it again. This exact general
noninvariance control is not a counterexample in the distinct-prime
source family. No similarity-invariance theorem is used.

The ideal core differs from the finite stored kernel: the source truncates
and rounds entries and retains additional setup/weight conventions.
Transcendence gives exact nonzero minors only, not a magnitude lower bound
or a Cp-bit tolerance. This package makes no comparison with those rounded
pages, no precision-production claim and no claim that an actual caller
materializes this dense format. It also excludes periodic aliases, cross-cell
entries, identity holes, rectangular or mismatched index sets, and any claim
that a rank floor for a two-point section transfers to the full section's
ordinary Stein matrix. Deleting vertices changes the one-step shift.

## 6. Honest comparison with the source group scale

FINE-PRIME section 1 states d=Theta(p^epsilon), fixed 0<epsilon<1,
log r_source=Theta(p/d), and target sides r_source or r_source/2. From (6),
for every group of distinct original axes,

    s_min=Theta(r_source),
    log s_min=Theta(p^(1−epsilon)).                           (10)

The exact pointwise bound is r=min(R_(2^g),s_min−1), not automatically a
linear bound for every group size. If `g=o(p^(1−epsilon))`, then
2^g<s_min eventually, and r=R_(2^g). At comparable scales the constants
matter; the exact condition R_(2^g)<s_min governs. For group schedules
`g=Theta(p^beta)` with beta>1−epsilon, the cap is eventually active and

    r=s_min−1=exp(Theta(p^(1−epsilon))).                       (11)

This is superpolynomial in p but is not linear in N=2^g. If beta<1−epsilon,
the full predecessor linear floor holds eventually. The equality case is
not classified without its constants.

The stated dense-format storage lower bound is 2Nr scalar slots, hence
Omega(N^2) when the full floor holds and N exp(Theta(p^(1−epsilon))) in
(11). These are counts for the stated exact binary core. They are not a
cost comparison for a larger source tile or a complete supplier. Generator
construction, source access, transport, gauge application, finite precision,
restoration and recursive children all remain to be paid in an algorithm.

## 7. Evidence, necessary guards and remaining obligations

The standard-library verifier authenticates the three retained inputs,
enumerates exact exponent boxes, constructs trimmed even-path minors and
checks their coefficient certificates, then specializes polynomial
dictionaries by exact integer exponents. It evaluates no floating
exponential and uses no numerical transcendence oracle. The written proof
supplies universal quantifiers; Gelfond-Schneider is an explicit input.

The controls preserve these distinctions. For primes 3,5 with equal dyadic
target 8, Q_1^3−Q_2^5 vanishes after substitution: its degrees reach the
respective thresholds. For noncoprime odd denominators 9,27 with equal
dyadic target, Q_1−Q_2^3 vanishes below both thresholds. For denominators
3,5 and nonunit numerators 3,5, Q_1=Q_2. Thus distinct denominators and
unrestricted degrees cannot replace the stated CRT premises.

A common alpha divisible by a source prime is still valid because it is
absorbed in the common base. Alpha=0 is excluded. An algebraic surrogate
for z can be a root of a nonzero specialized polynomial: distinct exponent
support alone is not transcendental nonvanishing. Arbitrary vertex deletion
can destroy a path minor; the stated even-prefix trimming is needed.
Compressing H before forming E changes the shift. The similarity example
in section 5 and coarse-rounding controls also block unjustified transfer.

The pointwise specialization is the contribution. Gelfond-Schneider, CRT,
path determinants and Schur complements are classical. The predecessor
supplies the all-order matching/counting theorem. Fine-prime existence,
legal width and source normalization are credited source work; predecessor
scientific suites are not replayed as this package's deliverable.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The lead proposed the specialization; the worker removed the unnecessary
alpha coprimality guard, derived the trimming/source argument and wrote
the primary checks; separate review checked the critical obligations.
Separate AI review is not human or formal-kernel certification.

All five selected assumptions remain. A source-specific quantitative margin
or a valid rank theorem for the actual shifted/rounded matrix is still
needed. Neither follows from transcendence. An algorithm must price setup,
coefficient access, transport, precision, gauges, restoration and recursive
children. No selected-frontier change or multiplication theorem is supplied.
