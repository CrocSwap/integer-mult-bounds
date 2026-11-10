# Global central normalizers as ordinary programs

This is a scoped implementation and cost implication under the retained
monomial-movement, owned-storage and numerical interfaces. It does not prove
those interfaces or admit the complete construction of
CrocSwap/integer-mult-bounds#6902. **No new κ.**

## 1. Exact object and the tensor distinction

Let `q` be a nonzero binary vector on the fixed central nine axes, and let
`X_q` translate a complete array address by `q`. The retained exact Gaussian
gate is

\[
C_q=\tfrac{1+i}{2}I+\tfrac{1-i}{2}X_q,
\qquad C_q^2=X_q,\qquad C_q^4=I.
\]

These are the literal `C` and `cgate` conventions in the retained Clifford
engine. The root uses the central operator `Q_f=C_q^{\otimes f}` on `f`
columns, with every spectator coordinate fixed. The literal normalizer of
orientation `s∈{−1,+1}` is

\[
\Lambda_{s,f}=\tfrac{1+si}{2}I+
              \tfrac{1-si}{2}Q_f^2.
\tag{1}
\]

This definition and its scalar coefficients are outside tensor powers.
Consequently

\[
Q_f^2=X_q^{\otimes f}=X_{v_f},\quad
v_f=(q,\ldots,q),\quad
\Lambda_{s,f}=C_{v_f}^{s}.
\tag{2}
\]

Equation (2) does **not** identify this operation with `C_q^{⊗f}`.
For example, on two odd central characters, the latter normalizer convention
would give `i·i=−1`, whereas (1) gives `+1`. This difference is already
identified by the physical review of #6763 and the even-normalizer audit
#6735; it is credited background, not a newly discovered counterexample.

The contribution below is an ordinary implementation of (1), with the
non-tensorized coefficients retained, including its scratch, movement and
numerical costs at the literal #6902 caller.

## 2. A fixed ordinary lowering for every positive width

Write `a_s=(1+si)/2` and `b_s=(1−si)/2`. Let `A` be the current main field and
let `B` be one full owned scratch field of the same ambient shape. Execute:

1. Initialize `B` to zero under the owned-storage contract.
2. Copy `A` into `B`, implemented as `B += A`.
3. Apply the ordinary monomial translation `X_q^{⊗f}` to `B`.
4. Replace each current value of `A` by `a_s A+b_s B`.
5. Clear `B` under the owned-storage contract.

For arbitrary input `A`, the value at step 4 is exactly (1). No other
productive field is read or changed. Step 5 earns no output credit and
returns the scratch before the next caller event. The macro has no Gaussian
recursive child.

The required movement is a particularly simple instance of the retained
monomial interface. For every set coordinate `i` of `q`, execute the record
`NOT(i)`: flip that logical coordinate in **every** one of the `f` columns.
There are `weight(q)≤9` records, independently of `f`. This is precisely the
`NOT` record of the merged #5445 proof
`research/selected-monomial-tape-lift/PROOF.md`, not an arbitrary
width-dependent address permutation. The translated field has exactly the
same complete ambient rectangle as `A`; all external spectators are fixed.
The construction is valid also for a single column. No extra coordinate,
independent input, or scalar output target is introduced.

For completeness, the arithmetic at one address is explicit. If the current
values of `A` and translated `B` are `u+iv` and `r+it`, the new real and
imaginary parts are

\[
\frac{u-sv+r+st}{2},\qquad
\frac{v+su+t-sr}{2}.
\tag{3}
\]

Six real additions/subtractions and two halvings suffice. In the retained
scalar-pass units, initialization, copy and clear of the two components
contribute at most six more units. Thus sixteen scalar units are a
conservative charge. The translation is additional and is charged below.
Only a constant number of scalar temporary registers are required by (3).

## 3. Exact interface used, and what remains assumed

The proof invokes the following named contracts rather than inferring
permission from the absence of a restriction:

* `FINITE-PRECOMPILATION.md` §1 requires all-column words with uniform finite
  operation count, arbitrary complete data, explicitly initialized/erased
  owned storage, and permitted monomial address maps at every tensor width.
* Its §6 keeps the logical scalar program outside tensor powers and charges
  every initialization, scalar pass, movement and erasure. It permits a fixed
  number of owned fields with no productive credit.
* #5445 realizes `X_q^{⊗f}` by the fixed `NOT` record list above. Its tariff is
  the retained compact-control movement tariff, not a new unit-cost RAM
  lookup. In the actual layer domain it is
  `O(V((f log p)^τ+1))`, under the retained complete-control reservations and
  `f≤p`, `A=O(p)` hypotheses. The exact source proof and movement note are
  retained without modification.

The `1000` route units below are the **source program's finite accounting
allowance** per monomial map. They are not a claim that a physical tape route
takes 1000 machine steps. The tensor width, numerical payload and BIT movement
tariff are still charged by the inherited outer implementation. Nothing here
proves the movement proposition, its reserved-control implementation,
`owned_erasure`, the full precision/tape interface, the compiler theorem, or
analytic recovery.

The number of copies of this fixed macro in a precompiled finite word can be
enormous. It is nevertheless finite, known from that word, and enters its
scalar/routing/stock constants. The proof does not make those copies free.

## 4. Literal source-bound substitution for #6902

All counts below are recomputed from the retained word and caller at source
head `e4d42607f24d7a049b0fca329dc4c34882405c25`. The original files are retained
byte for byte, with Git blob and SHA256 pins in `RETAINED.json`.

The caller has 2492 events, 40 roles, 104 ports, 124 `LAMBDA` events and six
thin `QUERY` events. Its 124×104 normalizer uses require **12,896** translated
scratch passes. Charging each a full source monomial allowance of 1000 adds
**12,896,000** finite route units. This pays each use separately; there is no
cross-port or cross-event fusion.

The exact scalar count of the caller, retaining the predecessor's sixteen
units per normalizer, is 36,304 per port. Including every new translation
gives

\[
104(36304+124\cdot1000)=16,671,616
 <32\cdot40\cdot104\cdot2492=331,735,040.
\]

Thus the expanded actual caller fits the existing caller overcount. A second,
deliberately more conservative check charges the translations **again** on
top of the entire existing reviewed raw bound:

\[
971,071,328+12,896,000=983,967,328<10^9.
\]

The remaining margin is **16,032,672**. The original raw figure is rebuilt
from the literal native scalar events, routes, helper normalizers, caller
envelope, thin queries, output maps and idle/query adapters. It is not copied
from the README. These are finite ordinary constants; the paid Gaussian and
productive-target histograms have zero delta. No κ improvement follows from
this lowering alone.

### Scratch capacity and chronology

The source allocation reserves one `('query_scratch',0)` bank disjoint from
all public inputs and native owned fields. Thin `QUERY` events are atomic
macros and return their scratch before continuing. Process ports sequentially
inside each `LAMBDA`; steps 1–5 finish before the next port or caller event.
The same bank can therefore be reused for all 12,896 normalizer lifetimes,
with no simultaneous `QUERY` or native invocation. Its full-field capacity
already serves the query at this ambient rank. There is no aliasing with a
main/helper input, no new productive credit, and no new owned slot. The
literal native peak is 30; the expanded caller peak stays `max(30,1)=30`.

This is an explicit allocation for the expanded program. The original JSON
does not already contain its INIT/COPY/translation/clear micro-events. A
consumer may lower `LAMBDA` by this macro while preserving the original JSON
as frozen evidence.

## 5. Numerical residuals and width

COPY is an addition into the current initialized bank, not an operation that
magically replaces a dirty numerical residue. Let the incoming real-coordinate
sup error of `A` be `E`. Let initialization, copy and the translation produce
combined real-coordinate error at most `D` in the scratch relative to its
copy of the current `A`. Let the final arithmetic in (3) add real-coordinate
error at most `R`. The real matrix of (1) has row absolute sum two, and that
of `b_s X_{v_f}` has row absolute sum one. Hence

\[
E_{\rm out}\le 2E+D+R.
\tag{4}
\]

If these errors are tracked individually, replace `D` by their sum with the
appropriate norm-one routing factors. Clearing `B` after use does not remove
its already-propagated contribution to `A`. Any residual left at that clear
belongs to the next initialization's contract. The numerical controls include
an actual nonzero residual whose effect would be lost by an assignment-style
COPY implementation.

The unrounded combinations use only signs, additions and a final half. For
inputs and scratch of component magnitude at most `M`, the integer sum before
the half has magnitude at most `4M`; two extra magnitude bits, with one
additional safe guard bit, suffice for this local arithmetic. The exact
denominator increases by at most one bit. A rounding grid may be applied to
the final halves; rounding error is included in `R`. Translations preserve
the grid and magnitude under the retained monomial implementation.

The source caller charges height eight per `LAMBDA`, which exceeds this
local growth/denominator allowance. Retaining that envelope and the
conservative raw constant above is sufficient for its **same conditional
precision argument**. This does not rederive the caller's global precision
format or claim a rounded complete multiplier has been executed.

## 6. Independent check and scope

`verify.py` executes the scratch/NOT lowering on complete small basis domains,
one dense actual nine-axis width-two array, and sampled routes for all 104
literal ports at widths one, two and three. It authenticates the retained
sources and rebuilds the complete ordinary budget and scratch lifetime count.

`independent.py` was written by the same research agent as `verify.py`, using
a distinct algorithm and code; it is not a separate human or agent review.
It imports no primary or predecessor scientific code. It
recovers the spatial kernel from all Fourier characters on every nonzero
direction in binary dimensions one through six. Character orthogonality
gives the two coefficients in (2) and zero elsewhere. Separately it proves
the finite coefficient identities in `Q(i)[Q]/(Q^4−1)` and checks the real
pair matrices and residual norms. The mathematical all-width claim is the
written argument in §§1–3; finite tests corroborate it and distinguish the
wrong tensor convention.

The source controls mutate a retained byte, a Git-blob pin, and a source
path in disposable copies. They verify that the source authenticator rejects
byte corruption, mismatched Git provenance, symlinks and missing inputs.
The lead researcher separately reviewed the algebraic lowering and its
fixed `NOT` record allowance against the pinned source contracts.

No scalar/native word search, changed root, new κ, five-assumption discharge,
fixed-tape execution, BIT admission, all-column native admission or overall
supplier acceptance is claimed. The extra owned-ascent hypothesis of #6902
is outside this package.

## Credit

DreamingOfClouds (#6902 and #6833) supplied the caller and review question;
zxv (#6726) supplied the normalization/caller lineage. Chris R / Clear1nsight
and @CubeJerry's #6763 physical review supply the exact total-Q convention,
query scratch allocation and scalar allowance; #6735 is credited for the
even-normalizer query-floor context. Matarener's #5445 supplies the fixed
monomial record realization, following Cao Yifan / intqwq, Cinna Davis,
icekylinx, Ali Romman, Jacob Alan Sussman and the retained compiler/native
lineage. Prepared for Jerry Chen / @CubeJerry with substantial OpenAI Codex
assistance. Apache-2.0; no independent human or proof-kernel acceptance.
