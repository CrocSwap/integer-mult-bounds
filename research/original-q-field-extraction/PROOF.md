# Actual full-field original-q extraction

Prepared for @CubeJerry with substantial OpenAI assistance. **No new kappa.**
This is one physical boundary lemma for `analytic_recovery`; it is not a
Gaussian approximation theorem or a complete multiplication caller.

## 1. Frozen source and exact missing boundary

The canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
`research/unconditional-batched-crt/GAUSSIAN.md`, “Complete-array calls and
q-image layout,” already states the increasing tensor-image scan. That
mathematical observation is prior work. Its required layout has the coarse
and low-bit gather undone before extraction; this package does not make a
gathered microbox field into an original-coordinate field for free.

`research/unconditional-batched-crt/PROOF.md`, “Sizes,” fixes axis zero as
the fastest coordinate, dyadic target periods, nominal `p0=6b`, and
`n_addr=log2(T)=Theta(p0)`. Its eventual fine family has
`s_i<t_i<2s_i` and `T/2<S<T`. The extractor only needs the per-axis strict
inequalities, not the stronger product comparison or primality.

The public normalized recovery package at
`1ab10aa78c4b27345c76806d1d32c7b9de481219` explicitly requires compact
original-order S fields. Its current external common-grid compression
carrier has two sign-magnitude components of `q+3` bits, a `#` record
separator, and a `2^-q` grid. Its zero-drop codec and native `q+3` to
`q+2` carrier are separate, paid operations. We implement the full padded
T-to-compact-S selection **before** that codec, with exactly this external
carrier and no numerical change.

Canonical `physical-gaussian-tensor/tensor_windows.py::CoreAssembly`
concatenates already-compressed contiguous source cores, removes their
capacity padding, and restores a source row's target-period padding.
It does not select the tensor q-image from a completed augmented inverse
on all T original target coordinates. Local C selection/D normalization
from CrocSwap/integer-mult-bounds#3851 is credited, not rediscovered.

## 2. The admitted ports and uniform theorem

Let `D>=1`, `q>=1`, and let a prepared native Count packet contain
`D,(ell_i,s_i)_{i=0}^{D-1}` in axis-zero-first order. Each Count is the
unchanged canonical binary Count encoding, least significant bit first.
Require integer `ell_i>=1`, `t_i=2^ell_i`, and `s_i<t_i<2s_i`.
Write

\[
 n_{\rm addr}=\sum_i\ell_i,\quad T=2^{n_{\rm addr}},\quad
 S=\prod_i s_i,\qquad
 Q_i(j)=\left\lfloor {t_i j\over s_i}+{1\over2}\right\rfloor.
\]

The caller binds this packet to the **original** periods used by its
Reference/normalization operators, not a core side, phase-run width, a
reordered group, or a gathered address. The complete external input has
T records, each exactly `2(q+3)` bits and `#`, in original target order
with axis zero fastest. `^` and `!` are the B-tape boundary markers.
The input, the prepared descriptor packet and the working-grid Count are
borrowed ports; they are distinct from the owner's fixed private stock.
They enter at their data origins (the B input may instead stand on its
left sentinel). Arbitrary initial head displacement is not free: if
allowed, add the total entry-to-origin movement `J_entry` to the time
bill. The owner starts with fresh private stock and retains the same
immutable parameters on every reuse.

**Theorem.** `Extract.run` preserves the input and its origin, and returns
exactly S records in source order. The record for source coordinate
`j=(j_0,...,j_{D-1})` is the unchanged input record at

\[
 A(j)=\sum_{i=0}^{D-1}Q_i(j_i)2^{\sum_{k<i}\ell_k}.
\]

The output is protected until `consume`. The owner can then be reused;
it regenerates active coordinate state from the same immutable initial
packet. It consumes the **entire** T-record field, including a possible
tail after the last selected address. Nonselected records may contain
arbitrary valid framed bits. No zero-hole premise is needed.

The theorem assumes the retained sequential Tape/Count semantics and
properly source-bound prepared ports. It does not certify Gaussian
headers, a full production transform, or the repository's complete
compiler/erasure/native framework assumptions.

## 3. Exact per-axis successor, including endpoints

Put `e=t-s`, so `0<e<s`. For `0<=j<s` define

\[
 r_j=(2ej+s)\bmod 2s,\qquad
 c_j=j+\left\lfloor {2ej+s\over2s}\right\rfloor=Q(j).
\]

Initially `(j,r,c)=(0,s,0)`. On a nonterminal increment form
`r'=r+2e`, which is nonnegative and strictly below `4s`. If `r'>=2s`,
subtract `2s` once and increment `c` by two; otherwise increment it by
one. This is exactly `next_axis`. Since `0<e<s`, at most one subtraction
is necessary. At source wrap `j+1=s`, the state resets to `(0,s,0)` and
passes a carry to the next axis. The formula at the unused `j=s` would
give `(r,c)=(s,t)`, consistent with that wrap.

Every `Q(j)` is an integer in `[0,t)`, and successive coordinates differ
by one or two. The nearest-integer convention is part of the source
contract; replacing initial remainder `s` by zero produces the floor
map and changes selected values. We do not claim a tie-breaking control
inside this dyadic domain: exact half ties are absent when
`s<t=2^ell<2s`.

## 4. One packed successor and one full scan

The active state holds five Counts per axis `(ell,s,j,r,c)`, on **one**
sequential tape, in axis-zero-first order. Its successor reads every
record once and writes a new state to the other tape. A single Boolean
carry records whether the source odometer has wrapped through lower
axes; after the first nonwrapping axis, remaining records are copied.
The last source coordinate is never advanced, so a complete carry past
the highest axis is rejected as an internal contract violation.

The new target address is built while reading that same state: append
exactly `ell_i` least-significant-first bits of `c_i`, zero-extending its
canonical Count, then append the next axis's bits. This is the binary
expansion of A(j). No stride products, coordinate list or random access
are stored. The single temporary address is normalized using the actual
Count normalizer. Coordinate-width checks reject any overflowing state.

The tensor-image addresses strictly increase in source order. Within
one axis this follows from its increasing Q. At a carry, the increase
in the first changed higher-axis digit is at least its target stride,
while the total possible decrease of all lower target digits is less
than that stride. Therefore equality with the next target address can
occur exactly once in a full target scan.

The scan maintains an encoded `Counter(S)` and actual `indices(T)`.
It starts with address zero, copies a matching complete record, and
advances the packed state only when an additional source record remains.
All intervening target records are validated and skipped. Induction on
the source ordinal proves the theorem; the final extent check requires
both the exhausted S clock and the actual end marker after exactly T
records. A compact S-field supplied as the input is rejected.

## 5. Exact norm, grid, scale and consumer join

Let C be the coordinate selection above and use the component-l1 maximum
norm `||x||_*=max_a(|Re x_a|+|Im x_a|)`. Exact bit preservation gives
`C_hat(x)=C(x)` for every valid encoded payload, with no rounding loss,
no frame-dependent rescaling and no extra Gaussian normalizer. Also
`||Cx-Cy||_*<=||x-y||_*`, and the maximum Euclidean coordinate radius
cannot increase. A production caller can consequently carry its full
field error and actual reached radius through this boundary unchanged.

This statement does **not** infer a half-disk from arbitrary q+3 words.
The public normalized-recovery carrier requires its already-proved
actual half-disk premise. Once present, the retained zero-drop codec
uses exactly S output records; the later q+2 narrowing is justified by
that radius, not by extraction. Canonical sign/negative-zero conventions
are inherited from the producer and preserved bit-for-bit; this
extractor checks framing, not numerical source admission.

The Gaussian restoration remains the same `Gamma=K_f+K_c`; the two S
factors and three Gamma occurrences in the public deferred recovery
remain unchanged. The downstream encoded S descriptor must equal the
product authenticated by this preparation. It may be copied from that
metadata or independently recomputed from the same bound packet, with
the corresponding Count-copy/product cost paid. No new CRT address
permutation or host-decoded cardinality is supplied here.

## 6. Preparation, fixed inventory, cleanup and complete costs

Preparation reads the borrowed packet, constructs each `2^ell_i`,
checks both strict guards, computes `n_addr` by actual Count additions
and S by actual `Count.product`, and constructs T as `2^n_addr`.
It serializes its own immutable metadata and initial axis state. Thus
neither T nor S is a free clock. The descriptor packet and q must
already exist on native tapes; source production/binding remains a
caller obligation. Their complete encoded lengths and the cost to
copy/read them are included below. There is no claim that a Python
shape tuple is an encoded production producer; such tuples occur only
in the test fixture.

The owner allocates 160 native scratch tapes, four fixed native tapes
(metadata, initial state and two active states), and one B output tape.
All variable-length objects are represented by cells on this fixed
stock. Runtime arithmetic is inside the unchanged sealed constructor /
OuterScope discipline. Fixed tuples of two or five temporary Count
handles are not variable-size coordinate storage. The input and the
two borrowed descriptor tapes are protected external ports. Counts
close every lease before `pool.empty`, and native scratch markers are
erased at macro return. On run success or rejection, active state is
erased, both immutable metadata heads are restored, the borrowed input
head is restored, and unprotected failed output is erased. `consume`
erases the successful owned output; `close` erases prepared stock.
Backing is retained and charged even after cell erasure. Let
`H_borrowed` be the sum of **complete retained capacities**, including
erased historical tails, of the input and the two borrowed descriptor
tapes. Their live extents alone do not bound this quantity. Private
stock is freshly allocated by the constructor; on every later call it
has the same immutable parameters and its historical widths remain
bounded by the bounds below.

Let `n=n_addr`. Each packed state and all setup products have O(n)
bits, since `sum log2 s_i<n`, `r_i<2s_i`, and `c_i<t_i`.
The actual unchanged Count product has a safe schoolbook bound
O(n^2) per axis; with `D<=n/2`, complete setup is

\[
 O(n^3+\log(q+1))\text{ steps},\qquad O(n+\log(q+1))
 \text{ private preparation backing}.
\]

This deliberately loose polynomial setup bound includes serialized
headers, all products, source scans, copies, remainders, and immutable
initialization. It does not stand for a sublinear hidden table producer.

For one successor, all encoded additions, subtractions, comparisons,
power-of-two construction, record copies, coordinate-bit emission and
state erasure cost O(n). `indices` uses the actual ripple increment and
canonical countdown; over k iterations their total ripple work is O(k)
plus initialization/closing width. In particular the loops over an
axis's ell bits and over a payload record's `2(q+3)` bits do not pay an
additional logarithm on every bit. In the literal retained runtime,
`Lease.clear` invokes `Tape.clear`, which stops at the first blank after
the current live body; it does not traverse allocated historical
capacity. A former longer body is erased once when that former lease
closes. A later shorter Count sees only blank cells beyond its new
body, and is not charged the old width at every payload bit.
`ScratchPool.empty` inspects each of the fixed 160 origins and adjacent
markers, not their historical tails. `ScratchPool.acquire` scans only
that fixed slot inventory. Full T-index/address comparison
costs O(n) per record; rebuilding all packed coordinates costs O(n)
only on the S selected records. There are no per-axis complete-field
passes. Including both endpoint rewinds, successful output consumption,
active-state erasure, metadata accesses and retained capacity gives

\[
 \boxed{\operatorname{time}=O(n^3+\log(q+1)+T(q+n)),\qquad
 \operatorname{backing}=O(H_{\rm borrowed}+Sq+n+\log(q+1)).}
\]

The backing bill includes all borrowed historical capacity and the
simultaneous owned S output. Under the additional bounded-history
admission `H_borrowed=O(Tq+n+log(q+1))`, it simplifies to
`O(Tq+n+log(q+1))`. A currently short well-formed field does not imply
this admission. The native fixture explicitly includes formerly larger
borrowed fields to expose the difference. Erasure of the producer's full T field after this
borrow ends is an additional O(Tq) caller charge, already of the same
displayed order; it is not performed destructively by this owner.
No hidden `D*n` stride array or `D*T` sweep is used.

For the retained fine family, `n=Theta(p0)` and the public working-grid
allocation has `q=Theta(p0)` (source-specific eventual tests still
apply). The polynomial setup is eventually absorbed by T, yielding
O(Tp0) time for **this boundary**; total backing is
O(Tp0+H_borrowed), hence O(Tp0) only under the stated bounded-history
admission. This does not lower the slow
Broad reference's Omega(Tp0 log T) invoice, admit a production Fourier
implementation, or improve the complete multiplication exponent.

## 7. Verification and precise remaining work

`python -B research/original-q-field-extraction/verify.py` authenticates
eight complete canonical inputs and three public retained files. It
checks 32,385 independent exact scalar coordinates, including full
period endpoints, and detects 15,808 wrong-floor coordinates. Genuine
native Count execution uses one-, two- and three-axis fields with
`(T,S)=(4,3),(32,15),(256,105)`. The oracle independently enumerates
source tuples and uses the direct rational-floor formula; it does not
call `next_axis` or reuse the program's address-concatenation routine.

The fixture supplies nonzero, unrelated hole values; checks exact output,
reuse, borrowed descriptors, immutable stock, origins, erased active
state and a formerly larger borrowed field with retained capacity; and rejects short/extra/compact inputs, malformed framing,
aliasing, pending return, invalid source guards and truncated descriptors.
Wrong nearest convention, wrong axis order and contiguous-pad-only
controls produce different address sequences. `python -O` must produce
the same result; assertions are not the acceptance mechanism.

These are bounded implementation witnesses and failure detection, not
a proof by finite enumeration. Sections 2–6 supply the uniform invariant
and complete invoice. Remaining prerequisites are actual production
full-field delivery in this exact original coordinate order, the input
error/radius/source contracts, the unchanged downstream codec/recovery,
CRT/carry completion and all inherited five framework obligations.
