# Causal splitting in the shared four-main native word

This proves source-specific helper splits using Ali Romman's mechanism from
CrocSwap/integer-mult-bounds#5599 and the witnessed prefix/suffix implementation
retained by @CubeJerry in CrocSwap/integer-mult-bounds#6805. The new source is
CrocSwap/integer-mult-bounds#6902 at
`e4d42607f24d7a049b0fca329dc4c34882405c25`.

The result is conditional on that source's computational contracts, including
owned ascent and ideal owned erasure. An owned value is never credited as an
independent productive input. Each split allocates a fresh public input and
proves its independence.

## 1. Exact cut obligation

Conjugate each live stream by its current canonical frame chart. A legal MOVE
preserves its normalized coordinate, while ADD and SCALE act over the dyadic
rationals. INIT and CLEAR are the inherited zero projections on owned fields.
Let (P) be the prefix before a cut and (S) the suffix. Public inputs are
arbitrary independent vectors; owned fields start at zero. The endpoint (E=SP)
is identity on helpers and has, at every port,

\[
 X=x,\qquad Y=x+y,\qquad X_2=x_2-y_2,\qquad Y_2=y_2.
\]

All owned final rows are zero. A witness supplies row vectors (a,c), column
vectors (b,d), a helper label (p), and an intermediate frame (F), with

\[
 aP=c,\qquad Sb=d,\qquad ab=cd=1.
\]

The support of (a,b), together with (p), consists of fields currently at
(F). The support of (c,d) consists solely of public helpers sharing initial
frame (U) and final frame (V). All four main sets are excluded. The strict
subspace inclusions are (U\subsetneq F\subsetneq V).

These are full prefix and suffix equations. A pure helper row alone is
insufficient: the suffix direction must exclude effects on every other public
output and every owned final row. `split.py:check_cut` evaluates the equations
over the rationals, including COPY, INIT and CLEAR semantics.

## 2. Splitting lemma

Checked elementary dyadic bases (B_0,B_F) satisfy

\[
 e_p^TB_0=c,\quad B_0d=e_p,
 \qquad e_p^TB_F=a,\quad B_Fb=e_p.
\]

(B_0) acts on the common-boundary public helper group and is identity on all
other fields. (B_F) acts on coframed live fields, possibly including owned
fields. The construction uses the two unit pairings; every emitted coefficient
and inverse scaling is checked against the permitted dyadic alphabet.
Set

\[
 C=B_FPB_0^{-1},\qquad D=B_0SB_F^{-1}.
\]

Then (e_p^TC=e_p^T), (De_p=e_p), and (DC=E), because (B_0) commutes with
the identity helper block of (E). The cut's (p)-coordinate equals the old
arbitrary input (x_p). Every other final row is insensitive to that cut
coordinate. The (p)-th final row equals the cut value plus a function of the
remaining cut coordinates; this latter function vanishes on every old input
since (DC=E).

Retire the old (p)-field at (F), and introduce a new independent public field
(z) at (F). Use (z) in place of (p) throughout the suffix. All other
outputs stay unchanged, the successor output is (z) at (V), and the retired
field returns (x_p) at (F). Thus one arbitrary-input job (U\to V) becomes
two independent jobs (U\to F) and (F\to V).

The emitted sequence is (B_0^{-1}), the old prefix, (B_F), (B_F^{-1}) using
the successor, the old suffix using that successor, and (B_0) at (V).
Every owned label is shifted upward when a fresh public label is inserted.
No alias is allowed. The proof permits zero projections in the old program:
it uses (aP=c) and (Sb=d), not invertibility of (P,S). Only the explicitly
constructed bases must be invertible.

The first 46 steps preserve the historical basis rule. Later entries name
`dyadic-unit-v1`: if the direction contains a dyadic unit, move that coordinate
to the pivot, normalize it, and clear the other column entries by dyadic ADDs.
If the resulting matrix is $P$, then $Pb=e_p$ and $(aP^{-1})_p=ab=1$.
Updating only pivot row by the other entries of $aP^{-1}$ gives the required
$B$. Every SCALE is a dyadic unit; each emitted ADD and its cost is checked.
Choosing an available unit avoids a forbidden reciprocal such as $-2/3$.
This does not decide every dyadic basis-realizability question.

Twenty cuts also retime 48 single MOVEs inside contact-free windows. No other
operation in a window reads or writes its retimed field. The exact chart
operators telescope as $T_VT_F^{-1}T_FT_U^{-1}=T_VT_U^{-1}$, with all signs
and phases. The prepared prefix and suffix receive the same full cut checks.
The emitted word has exactly the original paid operator multiset.

COPY requires more than a formal overwrite matrix. Full replay proves every
COPY destination is zero on all arbitrary public inputs. The separate cut
audit checks that the new arbitrary-input perturbation also has zero
destination at every later COPY. Thus COPY is the admitted ADD into an owned
zero field; an unknown value is never overwritten by this argument.

## 3. The live owned field in the first witness

The first witness uses (p=93), (U=3) (dimension zero), (F=240) (dimension
four), and (V=127) (dimension nine). Its middle vectors are

\[
 a=e_{93}^T+\tfrac12e_{86}^T+4e_{1107}^T-\tfrac12e_{1386}^T,
 \qquad b=e_{93}.
\]

Label 1386 is a **currently live owned field** in the original source. Exact
prefix evaluation gives

\[
 c=e_{93}^T+\tfrac32e_{1005}^T+4e_{1107}^T-e_{256}^T-4e_{338}^T
   +\tfrac12e_{351}^T+e_{370}^T-\tfrac12e_{681}^T,
 \qquad d=e_{93}.
\]

Every label in (c,d) is an original public helper with the same zero-to-nine
boundary. Both pairings are one. The owned value is only used inside an
invertible basis operation at its live frame. Here (b=e_{93}), so the middle
basis reads the owned field without writing it. The new credited field is
public label 1375, whose input at frame 240 is arbitrary and independent.
Original owned label 1386 is shifted to 1387; it is neither this new public
input nor a credited target.

Later witnesses receive the same full checks even when their middle supports
differ. Exact endpoint replay checks every fresh input column, every old output,
and owned return under the inherited erasure semantics. There is no inference
of productive credit merely from a pure row or an empty-looking owned field.

## 4. Physical maps and tensor widths

Every common-frame scalar basis operation is ordinary stream work. Its scalar
coefficient is applied once to the whole stream, outside the tensor power.
Entry and exit corrections are legal because their supports share (U,V).

The first split's helper endpoints are the literal signed chart changes
`chart(3).adjoint().then(chart(240))` and
`chart(240).adjoint().then(chart(127))`, of ranks four and five.
`native_physical.py` asks the retained Clifford compiler for each factorization,
then checks its signed Pauli action and absolute phase with a separate exact
Gaussian-dyadic interpreter. A phase-only mutation must fail. The same checker
covers every paid MOVE and every helper boundary pair in its selected scope.

The finite nine-column identities lift using the inherited ordinary monomial
and column-uniform frame implementation. Frame factors tensor with their
proper global phases; the external dyadic coefficients stay outside that
tensor power. These are explicit inherited compiler contracts. A finite
stream replay alone is not a proof of the complete machine model.

All four main initial and final charts are fixed explicitly to the source.
A scalar endpoint check by itself could miss a changed second-main chart;
the new checker rejects precisely that mutation.

## 5. Complete invoice and independent fields

The 68-split construction adds 68 public fields and 3,182 scalar events.
It changes no paid operator or paid rank coefficient; 48 MOVE occurrences
are retimed. Each split replaces rank nine by two positive complementary
ranks. The source root/caller uses eighteen native calls, so
the complete signed moment gain is

\[
          18\bigl(28g_4(t)+30g_3(t)+g_2(t)+9g_1(t)\bigr)>0,\qquad 0<t<1.
\]

Here $g_r(t)=r^t+(9-r)^t-9^t$. Strict positivity follows from subadditivity of (x^t). Rank mass is unchanged;
this is a strict concave-moment gain. Both helpers and paid jobs are recounted
from the literal word. The full wrapper bill is independently derived from
the emitted caller and the root masks. Their difference must equal this formula.

Each call maps 416 local mains injectively to four distinct caller fields at
each of 104 ports. Every helper gets its own `(call, helper)` public label.
The checkpoint has 1,027 helpers per call and 22,646 complete public fields,
including 4,160 main fields. Every new input has its own public label, disjoint
from mains and owned fields.

The word retains 51 owned labels, 54 lifetimes, peak 30 live owned fields, and
53 dirty clears. Across eighteen sequential calls the slab is reusable only
after exact return: 972 native lifetimes in total, with unchanged native peak.
The separate LAMBDA lowering uses the existing query bank and adds no owned
slots or productive credit. Added helper normalizers, scalar operations and
target-tail field counts are all charged.

The checkpoint's reviewed ordinary upper rises from 971,071,328 to 974,705,744.
We conservatively add the simultaneous-LAMBDA lowering's entire 12,896,000
charge, avoiding reliance on its absorption into an existing envelope. The
total is 987,601,744, below (10^9), with no recursive rank discount. The exact
normalizer proof/receipt is retained at the published source pin in
`SOURCE-PINS.json`.

The separately source-pinned constant-block caller compression preserves
every nonconstant event, owner and phase, and proves the complete matrix at
every replaced block boundary. It therefore composes with this native word.
Its 1,194 events replace the original 2,492 events, reducing the caller
envelope by 172,789,760. The composed ordinary total, including the same
complete LAMBDA debit, is 814,811,984. Both caller views have identical
productive and paid histograms; their formal endpoints and fresh scalar
heights are checked separately. The construction also satisfies the budget
with the original caller.

## 6. Strict conditional price and limitations

Two rational interval engines certify the signed margins at both raw-bracket
endpoints and at the tested saving. A derivative upper bound proves uniqueness
of the crossing below the inherited BIT pin. The checker verifies all three
tail ratios, the power-1920 contraction, complement capacity, integer exits,
and an explicit uniform threshold. The largest productive rank is 145, but
the raw physical caller occupies 153 axes. The chronological product uses
ambient cap $153^{1920}$ and maximum target $145^{1920}$. The source-pinned
companion `retained/compiler/PROOF.md`, especially its parametric transfer
statement in §8, applies after this package checks its full native, caller,
chronological paid and fresh-field obligations. The companion
ambient-cap proof applies the exact Pascal matching with truncation
$A\rho_s c(a)\leq N$, source band $(N/A,N]$, and complement
$\eta=tA^{t-1}$. The code substitutes the ambient cap only in those geometry
and exit majorants; it leaves the actual target moments unchanged.
Logarithm power 2300 is an explicit fixed choice. All 54 strict and four
functional outer inequalities pass. Fresh finite constants are specified in
`PRECISION.md`; no enormous uniform template is claimed to be materialized.

The 68-split construction admits the conditional candidate headline
\(\kappa=0.00357027\), tested at (0.00357027007), with raw crossing in
\((0.003570274998199,0.003570274998200)\).
It inherits the open BIT admission (0.00376669) of
CrocSwap/integer-mult-bounds#6726. The source-pinned companion
`retained/compiler/bit-audit/PROOF.md` separately verifies its integral and
binary algebra, actual 134-axis ambient, strictification and two frozen
ordinary backend levels from canonical saving 0.0034. It preserves the
conditional ordinary saving 0.00376669 with fresh completed constants. The
completed physical, ROW-restoration, stock and delayed-cover hypotheses remain
explicit; this native package does not turn finite checks into their proof.
The selected result's five framework assumptions and the source's additional
owned-ascent/erasure dependencies remain. The accepted frontier is unchanged.

The finite construction search is not an optimality or impossibility proof.
Independent reverse propagation checks the native public matrix and formal
caller by a method separate from the author's forward replay; both methods
still inherit the stated physical chart and computational contracts.

Author: @CubeJerry, with substantial OpenAI assistance. Predecessor attribution
and exact source versions are retained in `NOTICE.md` and `SOURCE-PINS.json`.
