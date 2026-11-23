# Dyadic bases for the selected binary single-grade compiler

## 1. Claim and exact scope

There is an **alternate, completely specified choice of image/kernel bases**
for the selected binary raw word and the single-grade compiler of #7828 such
that every fixed pre-cover projector, complete basis, whole-job matcher and
inverse is defined over

\[
R=\mathbb Z[1/2].
\]

Every complete basis and matcher is invertible over R. Consequently every
fixed projector has the advertised split rank, and every whole-job matcher is
invertible with its stated conjugation identity, over **every**
\(\mathbb Z/q^w\mathbb Z\), for every odd prime q and every w >= 1. No additional
odd-prime exclusion is needed for this implementation of the finite compiler.
The retained quantitative condition \(q>2^{45}N^5\) is unchanged.

This refines an existence construction. It does **not** prove that an
unspecified predecessor's chosen rational bases or Gaussian pivots have only
dyadic denominators. The new carried/lattice bases may replace those choices;
the resulting route matrices need not be byte-for-byte equal to them. The
source scalar chronology, paid positions, target ranks, coupled port routes
and complete operator endpoints are preserved. Any numerical tables of route
constants must be generated and charged for the choices actually used.

Nor is a single prescribed nonzero minor a valid universal rank certificate.
The certificate below is a complete conjugating basis, equivalently a unit
determinantal ideal. Section 7 gives an exact counterexample to the stronger
fixed-minor claim.

The claim is about the selected binary word, not the complex word, a new
conditional multiplication exponent, or all possible compiler grammars. It
does not remove owned erasure, precision/tape services, physical route prices,
the quantitative cover/stock inequalities, or the growing outer fine-prime
and analytic recovery obligations.

### Source boundary

The immutable source data are the selected `paired-query-only-bit` native word,
caller and result at canonical commit
`e54523517d0f03e58352e647c403a5af3e525a57`. The selected word has 636 complete
frames and 111 main port chart pairs. Its independently audited interpretation
is #7840 at `adf2e0aa6777977a280ce50f8938f4a0f4f19b76`, Sections 2–4. The
compiler is #7828 at `03b572b3b9ab72c6ba67762e85e1630cda1daad5`, especially
`APPLICATION.md`, `product.py` and `schedule.py`. `ORIGINS.json` supplies exact
paths, Git blobs and SHA-256 values. The selected raw frames are kept distinct
from the new bases of their normalized nested differences.

[Selected binary source](https://github.com/CrocSwap/integer-mult-bounds/tree/e54523517d0f03e58352e647c403a5af3e525a57/research/paired-query-only-bit)
· [#7840 native proof](https://github.com/CubeJerry/integer-mult-bounds/blob/adf2e0aa6777977a280ce50f8938f4a0f4f19b76/research/selected-native-four-premise-specialization/PROOF.md)
· [#7828 source application](https://github.com/aliromman/integer-mult-bounds/blob/03b572b3b9ab72c6ba67762e85e1630cda1daad5/research/single-grade-rank-compiler/APPLICATION.md).

## 2. A constructive localization lemma

Let S be a finite set of primes, let \(R_S=\mathbb Z[S^{-1}]\), and let
\(P\in M_n(R_S)\) satisfy \(P^2=P\). There is an effectively constructible
matrix \(B\in\operatorname{GL}_n(R_S)\) such that

\[
B^{-1}PB=E_r:=\operatorname{diag}(I_r,0),
\qquad r=\operatorname{rank}_{\mathbb Q}P.
\tag{1}
\]

**Construction.** Choose a positive integer s whose prime divisors lie in S
such that sP is integral. Then s(I-P) is also integral. Using only unimodular
integer column operations, obtain a basis X of the integer column lattice of
sP and a basis Y of the integer column lattice of s(I-P). Set

\[
B=[X\;Y].
\tag{2}
\]

The two rational column spaces are respectively the image and kernel of P.
They are complementary, with dimensions r and n-r, so B is square and
nonsingular. Also PX=X and PY=0, proving (1).

The lattice \(L=\operatorname{im}_{\mathbb Z}(sP)+
\operatorname{im}_{\mathbb Z}(s(I-P))\) has basis B. Since

\[
sI=sP+s(I-P),\qquad s\mathbb Z^n\subseteq L\subseteq\mathbb Z^n,
\]

its index satisfies

\[
|\det B|=[\mathbb Z^n:L]\mid s^n.
\tag{3}
\]

Thus det B is a unit of \(R_S\), and the adjugate formula gives
\(B^{-1}\in M_n(R_S)\). This controls **both summands**. A basis for the image
alone would not establish an invertible complete matcher.

The column-lattice algorithm is elementary. In a remaining row, combine two
entries a,b with integers u,v satisfying ua+vb=gcd(a,b)>0. On their two
columns apply

\[
\begin{pmatrix}u&-b/g\\v&a/g\end{pmatrix},\qquad g=\gcd(a,b).
\]

This integer matrix has determinant one, replaces the two entries by g,0,
and does not change the column lattice. Repeating clears the row, and the
next step acts only on remaining columns. Column exchanges and sign changes
also have determinant +/-1. At termination the nonzero echelon columns form
a basis of the original column lattice; the other columns are zero. Integer
Euclidean algorithms terminate, so this is a finite construction. No rational
Gaussian pivot is assumed to be a unit of \(R_S\).

`localized.py` implements this construction and retains the unimodular
transformation check internally. The written index argument is universal;
the exact finite matrix checks below corroborate its use on the selected data.

### Nested differences

If P,Q are idempotents over \(R_S\) and PQ=QP=Q, then

\[
(P-Q)^2=P-Q.
\]

Hence the same construction normalizes the exact difference P-Q. Its image
is \(\operatorname{im}P\cap\ker Q\), and its kernel is
\(\operatorname{im}Q\oplus\ker P\). These identities follow either by
decomposing x as Qx+(P-Q)x+(I-P)x or by applying the three pairwise
annihilating idempotents. The normalized child is the **difference**, not the
larger source projector, and its kernel includes the smaller image.

The same argument handles a further nested difference of generated
idempotents. For the specific compiler below, coordinate splits carry a
compatible basis directly, so fresh lattice reduction at generated nodes is
unnecessary.

## 3. Bind the fixed selected native catalogue

For each raw frame the source stores integral rows B and A. Its complete
column basis is \(G=[B^t\;A^t]\), and its projector is

\[
P=G E_r G^{-1}.
\]

The source check reconstructs all 636 matrices and checks their inverses,
self-adjoint idempotence and determinants with exact rational arithmetic.
An independent fraction-free Bareiss determinant check agrees. The complete
determinant census is:

| determinant | number of raw frame bases |
| ---: | ---: |
| -64 | 32 |
| -16 | 76 |
| -4 | 103 |
| -1 | 12 |
| 1 | 16 |
| 4 | 223 |
| 16 | 174 |

Thus G and G inverse lie in GL_8(R). For each of the 111 actual port charts,
the stored \(U_i=[u_i\;B_i]\) has determinant +/-1 or +/-4. The checker verifies
its stored inverse and the **exact** two projector equalities

\[
U_iE_1U_i^{-1}=P_{\mathrm{input}(i)},\qquad
U_i(I-E_1)U_i^{-1}=P_{\mathrm{output}(i)}.
\tag{4}
\]

There are 2,871 raw MOVE occurrences, 2,374 distinct directed MOVE pairs,
and 437 complete helper endpoint pairs. Their union has 2,380 pairs. For
each pair the exact smaller and larger projectors satisfy PQ=QP=Q. The
513 distinct differences have clearing denominators only 1,2,4. Applying
Section 2 produces complete bases with determinants powers of two; both
the image and the full kernel are checked. In this particular construction
the largest basis entry has four magnitude bits and the largest absolute
determinant is 2^14. These finite bounds are not needed by the theorem.

This normalization is a real extra step: **307** of those pairs have a
difference projector that is not an existing raw frame projector. For
example, the difference of frames 270 and 2 has no matching raw frame in
the catalogue. Looking up one of the 636 raw G matrices would not suffice.
`integral_split_basis` constructs the missing full basis instead.

The 134 physical axes consist of the central eight-space and eighteen
fresh seven-spaces. The actual stage route is

\[
S_{i,s}=(U_i\oplus I)\,\Pi_s\,(U_i^{-1}\oplus I),
\tag{5}
\]

where the permutation exchanges the seven central body coordinates with the
fresh stage space. This is in GL_134(R). The checker verifies its essential
15-dimensional block for all 111 ports: the route is an involution, fixes
the exact head in (4), and exchanges the complete body with the fresh
seven-space. The other 119 axes are fixed. The same block is placed at each
of the eighteen stages.

Both members of each coupled X_i,Y_i pair retain the **same** route (5).
Replacing internal normalizers does not authorize separate routes through
that coupled scalar contact. The selected caller's 38 target patterns are
an optional head, with coefficient 0 or 1, plus a set of disjoint fresh
stage spaces. Each is therefore a coordinate projector in the complete
basis \(U_i\oplus I_{126}\), with a permutation putting its image first.
The raw helper endpoints, nested paid requests and these complete caller
targets have thus all acquired complete bases over R before the single-grade
compiler is applied.

## 4. Carry bases through the exact compiler syntax

Use a **tagged projector** (P,B,r), meaning the full identity (1), as the
normalization interface. The following operations preserve that interface
over any localization \(R_S\).

1. **Conjugation.** For T in GL_n(\(R_S\)), the conjugated projector TPT^-1
   carries basis TB and the same rank. Products and inverse route symbols
   remain in GL_n(\(R_S\)).
2. **Direct sum.** For two tagged projectors, start from B directsum C and
   permute its columns so both image blocks precede both kernel blocks.
   The result normalizes P directsum Q with rank r+s. Add an identity basis
   for any unused exterior coordinates, with projector zero there.
3. **Kronecker product.** Use B tensor C, then permute the columns indexed
   by (image,image) first. The projector P tensor Q has rank rs. In
   particular P tensor I_c has rank rc and basis B tensor I_c.
4. **Whole-coordinate placement.** A complete coordinate permutation Pi
   carries a basis to Pi B; an embedded local basis is first extended by
   identity on all spectators. Every inverse placement is retained.
5. **Image split.** Let J be any ordered subset of {0,...,r-1}. Put
   P_J=B E_J B^-1. Let Pi_J move exactly J first, keeping **all** remaining
   n-|J| coordinates, and put B_J=B Pi_J. Then
   \(B_J^{-1}P_JB_J=E_{|J|}\). The kernel includes every unselected image
   direction as well as the old kernel. Disjoint subsets give pairwise
   annihilating projectors whose sum is P when they partition its image.
   Nested differences are the difference of their coordinate subsets in
   that same carried basis.

The determinant formulas are

\[
\det(B\oplus C)=\det B\det C,
\quad
\det(B\otimes C)=(\det B)^{\dim C}(\det C)^{\dim B},
\quad \det\Pi=\pm1.
\]

They are units of \(R_S\). No submatrix is inverted to normalize a split.

The source also embeds a route S on a restricted column sector E. This is
the **specific** guarded sum

\[
L_E(S)=S\otimes E+I\otimes(I-E),\qquad E^2=E.
\tag{6}
\]

The identities E(I-E)=(I-E)E=0 give

\[
L_E(S)L_E(T)=L_E(ST),\qquad L_E(S)^{-1}=L_E(S^{-1}).
\]

If E has a carried basis and rank k, conjugating by that basis and shuffling
coordinates makes (6) a direct sum of k copies of S and identity blocks.
Its determinant is (det S)^k, a unit. A change of ambient basis conjugates
this same construction. Arbitrary sums of invertible matrices are not part
of the closure assertion.

### Literal source-to-operation map

| Pinned source location | Added operation | Complete basis rule |
| --- | --- | --- |
| `product.compose` | Suspend distinct outer callbacks; place each normalized paid axis tuple | Complete coordinate permutation; keep outer adapter active |
| `product.compose` target/paid rank products | Tensor product of independent target axes | Kronecker product and image-first shuffle |
| `product.specialize` | Zero roles for unselected target tuples; retain all source paid positions | Same source projectors; no new inverse or rank witness |
| `product.specialize` request slices | Consecutive slices of normalized `axes` | Image split in the carried basis; all complement columns retained |
| `schedule.complete_order` | Active coordinates followed by every unused coordinate | A full permutation, never a rectangular minor |
| `schedule.expand` | Tile placement, recursively completed native requests, one-axis tails and inverse return | Placement, image split and rank-one coordinate projector |
| `APPLICATION.md`, binary embedding | Multiplicity, identity extension, changed basis and restricted sectors | Kronecker/direct sum/conjugation and (6) |

The two literal Python sources do not choose rational Gaussian pivots. Their
callback yields `(owner, axes)` only after a raw request is normalized. This
proof supplies compatible normalized bases at that callback boundary, then
follows exactly the complete placement and slicing operations above.

Structural induction on that finite source syntax proves that every tagged
projector and route remains in the stated localization. This is a universal
proof over finite generated words; the enormous selected word is not
materialized by the finite checker. It is also not a claim of a natural,
coordinate-free basis choice for an untagged projector. The lattice algorithm
chooses a basis once, and later operations carry that choice coherently.

## 5. Match both summands and reduce at every odd prime power

For two n-dimensional tagged projectors (P,B_P,r),(Q,B_Q,r), set

\[
S=B_PB_Q^{-1}.
\]

Then S and S^-1 belong to GL_n(\(R_S\)), and

\[
SQS^{-1}=P,\qquad S(I-Q)S^{-1}=I-P.
\tag{7}
\]

This proves the complete whole-job matching identity on arbitrary data,
including spectators, not merely on a chosen image subspace.

For any prime q outside S and any w>=1 there is a ring homomorphism
\(R_S\to\mathbb Z/q^w\mathbb Z\). Applying it to all matrix identities gives
the same inverse and the same (1) and (7). Thus the reduced image and kernel
are free summands with their advertised ranks at every width. For the selected
source S={2}. This proves the all-odd-prime conclusion without extrapolating
from any finite list of moduli.

All (r+1)-minors of P vanish, and its r-minors generate the unit ideal over
\(R_S\). One way to see the latter is Cauchy–Binet applied to
\(B^{-1}PB=E_r\): the unit r-minor of E_r is an \(R_S\)-linear combination
of the r-minors of P. This is the appropriate rank-witness semantics.
The complete conjugating pair (B,B^-1) is a smaller structural certificate
than expanding every minor and its Bezout coefficients.

In the delayed-cover interpretation, (7) gives

\[
(gS)Q(gS)^{-1}=gPg^{-1}.
\]

Right multiplication by S is a bijection of the full cover group at every
width. Coupled raw pairs still use their one common route; independent
completed compiler roles may have different matchers. The common weight
and chronological ownership conditions are inherited unchanged from the
source proofs. This argument supplies the arithmetic premise of that route;
it does not make a dense physical address map free.

## 6. Physical factorization and the ordered-shear boundary

The source #7840 Section 4 permits full GL elimination with q-unit pivots,
charging ordinary swaps to implement upper updates. After choosing q, an
invertible remaining Schur block has a unit pivot modulo q. The physical
factorization may therefore be chosen for that q; it need not reuse a
preselected rational pivot list. This supports the all-odd-prime conclusion
for the exact source route, with its existing count bounds.

There is also a q-independent algebraic factorization of any GL_n(R) matrix
into elementary dyadic additions, row exchanges and dyadic-unit scalings.
To construct it, multiply by a power of two to clear denominators. The gcd
of its first integer column divides its determinant, which is a power of
two. Unimodular Euclidean row operations reduce that column to a signed
power of two, a unit of R. Normalize and clear with dyadic coefficients,
then recurse on the remaining invertible block. This shows that even a
fixed factor list *can* avoid odd exclusions. It is an optional algebraic
construction, not an assertion that its number of elementary operations
obeys the source's `2N^3` route bound. Using it physically would require
recounting the finite constants. The source q-dependent unit-pivot route is
sufficient here.

This distinction is essential in view of Nick Petalas's #6201 at
`7f150965d4836ae29bac98df8c25785428deddb1`. That proof characterizes a more
restricted **lower / partial-permutation / lower** ordered matrix-shear
route using all northeast rank profiles. Even a determinant-one matrix
\(\left(\begin{smallmatrix}1&3\\0&1\end{smallmatrix}\right)\) has a failure of
that restricted route over Z/9. Its result does not contradict the full GL
route with paid swaps used by #7840. Our conclusion must not be substituted
for its northeast-profile condition in a tariff that only permits the
restricted ordered route.

[#6201 exact proof](https://github.com/petalas/integer-mult-bounds/blob/7f150965d4836ae29bac98df8c25785428deddb1/research/ordered-shear-admissible-primes/PROOF.md).

## 7. Negative controls and finite evidence

Let

\[
G=\begin{pmatrix}2&3\\3&5\end{pmatrix},\quad \det G=1,
\qquad
P=GE_1G^{-1}=\begin{pmatrix}10&-6\\15&-9\end{pmatrix}.
\]

This projector has split rank one at every prime. None of its entries is a
unit of Z[1/2]. In particular the fixed witness P_11=10 vanishes modulo 5,
although P_12=-6 does not. The relation 10+(-9)=1 certifies that its entries
generate the unit ideal. Hence a rule excluding every prime that divides
one chosen nonzero rank minor can introduce spurious odd exclusions even
for a unimodular complete basis. This is a generic exact negative control,
not a claim that the selected compiler literally generates this 2x2 matrix.

Similarly, a prescribed Gaussian pivot can fail while the complete matrix
remains invertible. The determinant-one matrix
\(\left(\begin{smallmatrix}3&1\\2&1\end{smallmatrix}\right)\) has a nonunit
upper-left pivot at q=3, but exchanging its two rows exposes a unit pivot.
Neither example is an obstruction to the carried-basis construction.

The independent checker authenticates the retained source bytes, rebuilds
all 636 frame projectors and 111 port charts, and constructs all 513 actual
nested-difference bases. It uses a second determinant algorithm and checks
3,078 complete image/kernel conjugations over moduli 3,9,5,25,7,49. It also
checks 1,026 source-derived coordinate splits, 513 equal-rank whole-job
matchers, all 111 essential stage-route blocks, and 36 complete placements
using the literal pinned `complete_order` function. A nonorthogonal sector
checks formula (6), while a non-idempotent sector makes its proposed inverse
fail. Invalid rank matches, duplicate coordinates and a non-idempotent
projector are rejected.

A bounded search through the actual 513 differences found no odd determinant
in the simpler basis formed by lexicographically chosen independent columns
of P and I-P. No universal claim is inferred from that observation; the
lattice-index proof is what establishes the general prime control.

## 8. Consequence and remaining work

For this alternate selected binary compiler, choose any odd prime
\(q>2^{45}N^5\). The choice no longer needs a list of additional forbidden
odd primes from generated full bases, whole-job matchers or rank certificates.
Existence and effective search for such a fixed prime are elementary; no
least-prime estimate or numerical selected q is supplied.

The old instruction to avoid the complete generated list remains a sound
conservative rule for arbitrary basis choices. The present refinement
replaces the relevant choices by an explicit localized implementation. It
reduces one finite-cover arithmetic obligation and does not discharge the
whole native or compiler theorem. In particular:

- the native scalar identities, owner/erasure contract, common-weight support
  and exact raw boundary semantics still come from their separate sources;
- finite logical compilation and well-founded runtime recursion remain the
  independently proved compiler obligations;
- every complete right route, its inverse, its low-type work, high-column
  work and full-volume movement retains its physical charge;
- changed explicit route matrices require consistent finite descriptor and
  setup constants, even though ranks and scalar chronology are unchanged;
- the quantitative large-cover inequality and all outer precision, stock,
  tape and analytic recovery conditions are unchanged.

The natural next step is independent review of the source-to-tagged-syntax
map, particularly the coupled raw route, the complement of a nested
difference, and the restricted-sector embedding. This package is local
review-ready evidence, not a published admission or formal proof-kernel
certificate.
