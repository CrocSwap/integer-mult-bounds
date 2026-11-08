# A literal banded forward action through a nilpotent lift

This package implements one supplied real band-matrix action on encoded RHS
columns. Its finite source is a Schur matrix of the **broad** current rational
Reference. It does not implement a whole broad Gaussian word, a union router,
an outer multiplication algorithm, or a new selected exponent. **No new κ.**

The elementary lift, Strassen identity and generic Gaussian conditioning are
not new claims. The contribution is the complete fixed-role zero/interleave,
existing physical inverse-page call, projection and restoration transaction;
its source-bound dyadic page preparation; and its explicit full bill.

## 1. Exact function and input contract

Let F be an n-by-n real rational matrix, n>0, with half-band v and at most s
nonzero coefficients per row. Let Γ≥||F||∞. In particular s≤2v+1. F may be
singular. Let b be dyadic with b≥2v+1. The producer checks the exact interleaved
support **before** coefficient rounding: a tiny out-of-band coefficient cannot
silently turn an invalid source into a valid one by disappearing on the grid.

For r>0 real RHS columns, put

    J = ceil(r/b), K0 = ceil(n/b), K = ceil(2n/b),
    N0 = K0 b, N1 = K b.

The source has J batches, each N0 rows by b columns in row-major order. A word
is the retained width-w two's-complement, least-significant-bit-first encoding
of its numerator on the 2^-P grid. P<w. Rows at least n and columns at least r
are zero. The output has exactly this same padded layout. Pairing real columns
as real and imaginary components gives the complex-l1 contract below; an odd
last real column is also permitted.

All five source tapes (input and four coefficient banks) are distinct and
outside the complete owned closure. Metadata ports may alias each other, but
not data ports or owned tapes. Every port begins at its left-marker origin.
`run` returns one protected output; `consume` must erase it before the next
call. Moving the returned head does not remove this obligation.

The four coefficient banks having the prescribed source/lift semantics is an
**admission premise**, established by the authenticated preparer and its source
receipt. The online caller checks port ownership, encoded geometry, binary
extents and padding; it does not authenticate the mathematical values of
arbitrary supplied coefficient banks.

## 2. Interleaving and exact prepared-page equality

For each i interleave a fresh zero target at position 2i and the source value
at 2i+1. Define

\[
 N_{2i,2j+1}=-F_{ij},\qquad N_{kl}=0\text{ otherwise}.
\]

Its half-band is at most 2v+1. Target rows and source columns are disjoint, so
any product of two matrices with this mask vanishes. Split N into strictly
lower, diagonal and strictly upper **blocks** N_L,N_D,N_U. Then

\[
 L=I+N_L,\quad U=I+N_D+N_U,\quad
 LU=I+N,\quad (LU)^{-1}=I-N.                                \tag{1}
\]

In particular `(I+N)^-1(0,x)=(Fx,x)`. At b covering the band, L and U are block
bidiagonal. L's diagonal inverse blocks are I, while U's are I−N_D. These
blocks have positive unit no-pivot elimination pivots: every nonidentity
entry goes from a source column to a target row, and no second such entry can
follow it. Inverting these blocks never requires F to be invertible.

Let τ be componentwise real truncation toward zero at P fractional bits.
Setup first computes `Fhat=τ(F)` exactly, constructs the corresponding dyadic
factors, serializes them as exact retained Matrix objects, and **executes
unchanged physical `prepare_pages`**. This produces exactly the same bytes as
preparing the unrounded exact-F factors and rounding their final pages:

* Preceding-block pages contain only signed entries of F, and τ(−x)=−τ(x).
* Every inverse diagonal block is I minus its masked block. The mask has zero
  scalar diagonal, so no truncation of `1+x` occurs. Identity and zero entries
  remain exact, and off-diagonal entries again commute with τ and sign.
* Padding by identity and reversal are permutations of this same identity.

Thus pre-rounding changes the setup height without changing the inherited
online rounded function. The source's `expected_pages` is an observer only;
its values are never supplied to the physical consumer. The independent
checker instead inverts exact diagonal blocks, computes both page routes and
compares each to the actual physical page words.

## 3. Literal transaction, restoration and fixed owners

`action.py` uses one BandedAction owner, a fixed pool of 128 local roles, a
dilated tape, an output tape and the unchanged FastBoundaryPages child. Its
complete constructor closure is 2,788 physical roles. Tape constructors are
sealed throughout online execution. Count values, loop indices and record
dimensions remain encoded; the online program never decodes a matrix size,
payload word, coefficient or numerical answer into a host integer.

The wrapper scans each input batch. For each real row it writes b zero words
and copies the b source words. It validates and discards the input's row pad,
then writes only the necessary N1−2n lifted row pad. It does not double N0
blindly: when n is ragged, `ceil(2n/b)` and `2 ceil(n/b)` can differ.

It suspends its local scratch scope around **one complete** child call with
dimensions `(2n,r,b,w,P)`. The child retains its full batch/row ceiling invoice
and unchanged exact-product-then-rounding ABI. The wrapper projects each even
row and compares every recovered odd-row bit with the original borrowed source
row. It checks all lifted padding, restores the original row padding, consumes
the child, and rewinds every input/page/metadata port.

Successful return protects the complete output until consume. All other owned
roles are erased, with left markers released; consume also erases output.
Exception cleanup consumes any child return, clears partial dilation/output,
closes the pool, releases markers and restores every borrowed port. Tests
include a truncated coupling after a completed matrix child, so this assertion
is not based only on preflight failures.

The largest local live set has eleven persistent Count descriptors, at most
three nested iterator/copy activations, and bounded arithmetic temporaries.
The same fixed helper implementations used by the retained wrapper fit a
conservative 64-local-role envelope, below the 128 available roles. Child
execution suspends that local pool rather than borrowing its remaining roles.
No dimension-dependent Python stack, list of tapes or recursively live owner
is created by `run`.

The underlying Tape clear scans the **live prefix to the first blank**. Every
call clears that prefix before shorter reuse, leaving its already blank
historical suffix intact. Retained backing remains part of space; it is not
rescanned merely because a later call is short. The same owner executes a
larger singular case followed by a one-row/one-column call, and every retained
cell is checked blank afterward. Copying, comparison, zero creation, rewind,
projection and erasure are all charged.

## 4. Error and scalar range

Assume the actual input maximum complex-l1 norm is at most R≥1 and the input is
already on the common grid. This is a mathematical admission promise, not an
unimplemented modulus-check claim. Earlier grid conversion belongs to the
caller. Put h=2^-P. The quantized source satisfies

\[
 \|\widehat F-F\|_\infty\le sh,\qquad
 \|\widehat F\|_\infty\le\Gamma.
\]

Throughout both physical passes, source rows stay exact. Target errors are
never read as sources of a nonidentity coefficient. Each target is assembled
from three disjoint sets of original source columns: lower-block, upper-block
and same-block contributions. The lower inverse page is identity and adds no
effective rounding. There are at most three effective scalar truncations, or
six ulps for a complex pair. Therefore

\[
 \|\widehat y-Fx\|_*\le(sR+6)2^{-P}.                       \tag{2}
\]

This need not equal a single completed-dot truncation of Fx. The independent
oracle forms those three disjoint dot sums directly rather than copying the
block-solver recurrence. It also compares the returned values with the original
unrounded F.

Inward rounding cannot increase a partial absolute row-sum budget. Since each
coefficient appears in exactly one of the three sets, stored targets have
magnitude at most ΓR and sources at most R. This includes complete residuals
and solved states; it avoids multiplying a `(1+Γ)` factor once per block.
A sufficient target-q allocation is

\[
 P\ge\max(P_{\rm in},q+\lceil\log_2(sR+6)\rceil+1),\qquad
 w\ge P+2+\lceil\log_2(\max(1,\Gamma)(R+1))\rceil,           \tag{3}
\]

with metadata widths separately charged. Exact root products and recursive
Strassen scratch do not remain masked. They use the retained general guards
`U=w+ell+2`, `V=2w+4ell+4`, and exact returned width `2w+ell+2`, where
`ell=log₂b`. These are not replaced by the smaller stored-state bound.

For the actual broad source `F=D-C A^-1 B`, the source's retained admission
`E_M Qideal≤1/2` and row/column bounds give `||A^-1||≤2Qideal` and
`Γ=3+18Qideal`. No broad F inverse or broad row gap is needed. The finite fixture
instead computes and reports the exact inverse norm of its small A and exact
norm of F. It makes no arbitrary-cap or ideal-Gaussian claim.

Only with `q,P_in,log R,log Γ=O(p)` do scalar widths become O(p). Tensor use
also needs the accumulated `g log(1+Γ)` guard funded. Under the particular
capped broad source conditioning in GAUSSIAN.md, Γ is polynomial in p and
`g=p^beta`, beta<1, gives an o(p) guard. An arbitrary fixed Reference does not
automatically satisfy those premises. Neither the other broad shears nor that
whole-source composition is implemented here.

## 5. Complete online ceiling and space invoice

With K,J from section 1, exactly

\[
 Q_{\rm prod}=2(2K-1)J
\]

matrix products occur, each with `7^ell` actual scalar children. Write
`omega=log₂7`, `Lambda=1+ell+ceil(log₂(w+2))`, and let M(u) be the complete bit
cost of the inherited independent scalar-word product at width u. Retain

\[
 Q_{\rm prod}\,O\!\left(b^\omega[
 M(w+\ell+2)+(2w+4\ell+4)\Lambda^3]\right)                  \tag{4}
\]

for all matrix arithmetic and its quadrant/parked-frame movement. The inherited
caller adds

\[
 O\!\left(KJb^2[w+\log(2n+r+2)+\ell+1]\Lambda^3\right).    \tag{5}
\]

Here `h=ceil(log₂(2n+r+2))` is retained explicitly. This wrapper calls the child
once with the **global r**, so exponentially many lines do not give
`h=O(log p)` merely because n and b are polynomial in p. The primitive claims
no production boundary margin obtained by dropping h. A later streaming wrapper
could call local b-column transactions, or a complete outer proof could fund
the displayed global-column overhead; neither substitution is made here.

The wrapper's input/output extent is `I=J K0 b²w`; the dilation extent is
`D=J K b²w≤2I`. All copying, inserted zeros, source-row comparisons, projection,
clears and rewinds cost O(I+D), plus `O(J N0 log(n+2))` for the explicit row
comparisons and a fixed polynomial in the encoded startup dimensions. The
encoded outer `indices(J)` loop uses amortized binary increment/decrement;
there is no repeated scan of a log r counter for every payload bit. Keeping
the startup polynomial separately is safe, and these terms are absorbed by
(5) in the usual sufficiently large admitted regime.

The output and dilated buffers store **all r columns**, not merely one b-column
batch. Current storage is their complete I+D bits, the inherited child storage,
input/page banks, descriptors and all previously retained backing extents.
Live-prefix erasure prevents an extra old-high-water rescan tariff, but does
not remove historical extents from the space count. The long-to-short receipt
records that those extents remain allocated and erased. The physical role
count is constant, while the number of occupied/retained cells is not.

When both `2n≥b` and `r≥b`, the product count in (4) simplifies to
`O(nr b^(omega−2))`. In general retain

\[
 O(nr b^{\omega-2}+(n+r)b^{\omega-1}+b^\omega).
\]

With b=O(W), this has the desired band exponent; it is not by itself a global
supplier or multiplication bound. Headers, field exposure and page-key grouping
are outside this already-packed input ABI. There is no hidden tensor-sized
integer argument charged at a scalar width.

## 6. Separately paid source and page setup

The setup is independent of online payloads. The finite source takes entries
of the authenticated current **broad** Reference on `[16,20)`, validates the
original phase-pure interior `{1,2}`, and computes its exact rational Schur F
on `{0,3}`. This is an explicit admitted partition, not a claim that the
production carve selects that interior. The independent source oracle obtains
F by inverting the J-principal block of the full original Q inverse, using
pivoted triangular elimination/back-substitution instead of the producer's
interior inverse. It explicitly distinguishes substitution of the narrow Q.

For a general supplied rational F let H_F bound its input numerator/denominator
heights. Pre-rounding costs `O(n²(H_F+P)^3)` by conservative elementary rational
division, including complete input reads. After that, the factor coefficients
have height `H=O(P+log(Γ+1)+log(n+b+2)+1)`. Unit-pivot nilpotent block elimination
has no products of two nonidentity coefficients; its reduced intermediate
entries and inverse pages remain in the same height envelope. All physical
Matrix get/set scans, support checks, counter arithmetic, serialization and
exact block inversions are paid by, for example,

\[
 C_{\rm setup}\le C_F+O(n^2(H_F+P)^3+(n+b+2)^6H^4).          \tag{6}
\]

Here C_F is the complete cost of producing the exact source F, not a free entry
oracle. Host setup indexing can be simulated by full sequential scans of its
finite matrices within this deliberately loose polynomial. The actual dyadic
physical `prepare_pages` actions are separately metered in the receipt.

For the current source, C_F includes canonical interval generation, exact
coordinate arithmetic, original reference weights/cuts, and rational Schur
formation. Those algorithms have polynomial bit cost in their numerical
precision, period and coefficient-height parameters. In the intended
`period=2^O(ell)` and polynomial-p setup regime this permits
`C_F=2^O(ell)poly(p)`; the generic theorem always retains C_F explicitly.
Any numerical admission radius supplied as a rational requires its full
numerator/denominator description charge, not only log of its value.

Fresh setup storage includes dense serialized factors of O(n²H) bits, source
matrices of O(n²H_F), interval caches and page banks of
`2(2K−1)b²w` bits. Historical source caches and physical tape backing remain
charged unless a fresh/cleared namespace is used. Across repeated calls the
same pages can be reused without recomputing F or its coefficients per RHS.
No global catalogue amortization is asserted by this component.

## 7. Evidence, provenance and limits

The registered normal/optimized verifier executes three cases on one owner:
the actual broad-reference Schur, a signed nongrid singular tridiagonal matrix,
and a smaller one-row zero matrix. The singular matrix is

\[
 \tfrac13\begin{pmatrix}1&-1&0\\-1&2&-1\\0&-1&1\end{pmatrix}.
\]

Its constant vector is in the kernel and a 2-by-2 minor is nonzero, so its rank
is exactly two. It has both lower and upper lifted block couplings at b4. The
tests include partial input rows/RHS columns, exact page commutation, a tiny
out-of-band coefficient before rounding, source/page and inactive-owned aliases,
pending returns and failure after a completed matrix child. Every data/page/
descriptor head, dirty spectator and owned backing cell is checked. The
independent output oracle uses three disjoint integer dot sums; it also checks
the exact original-F error and every padded output bit.

Each receipt's `transaction_actions` includes `run`, the subsequent physical
scan moving the returned head to its end, the attempted rejected pending
reentry, and `consume`. It is not a claimed count of core `run` alone. Host
fixture construction and external exact observers are separate; actual factor
serialization/page preparation and initial payload packing have their own
metered fields.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Retained
`seven_product.py` and `fast_boundary.py` are unchanged bytes from public fork
commit `f821cba68f44048e70e78afb75603ed4dde99f11`, with source paths/hashes in
SOURCES.json. The canonical actual page/Matrix runtime is from
CrocSwap/integer-mult-bounds#5059 and its pinned physical scalar-word cohort.
CrocSwap/integer-mult-bounds#481 already proposed batched Gaussian arithmetic
and a written conditional tape tariff; it is closed/unmerged. Merged
CrocSwap/integer-mult-bounds#4205 already proves the shared finite-core broad
word/error interface at its host arithmetic boundary. We do not republish
either generic theorem. This package supplies the specified physical forward
primitive and preserves their remaining outer obligations.

Credit the retained construction authors, Jose Manuel's shared reference/core
integration, Mason Hale's interval arithmetic, Vlado Vojdanovski's Gaussian
and block work, the physical scalar-word contributors, and the independently
credited exact seven-product package. Prepared for `@CubeJerry` with substantial
OpenAI Codex assistance. A separate source-aware AI researcher supplied the
independent original-matrix/page/three-sum oracle. Apache-2.0. No human or proof
assistant acceptance is claimed by the finite checks.

Open next question: can the actual broad union-window caller pay its original
coupling shear, header transport, source catalogue and current-grid conversion
around this primitive? A first step is one frozen page key and complete
rounded chronological transaction. No such full caller, complete Gaussian
word, outer CRT/FFT assembly or discharge of the selected five assumptions is
part of this result.
