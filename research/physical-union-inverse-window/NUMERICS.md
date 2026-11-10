# Same-reference source, pages and numerical contract

This note binds the physical first narrow inverse window to the current
immutable rational `Reference`. It is part of the complete transaction in this
package, not an independent claim about the global multiplication algorithm.
**No new κ.** The selected frontier and its five inherited assumptions are
unchanged.

The source, carve geometry, Schur identity and generic boundary error estimates
are inherited. The new composition supplies the original coupling shear and
the Schur solve together to the literal many-column page caller, from the same
reference and at the actual current input. It does not identify the older
`physical-gaussian-core` matrix with the current reference. Its exact rational
matrix storage, rational operations and `prepare_pages` are reusable setup
primitives; their original old-matrix fixture is not the numerical source here.

## 1. Frozen source and admitted window

The canonical source is commit
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The manifest pins the unchanged
`research/rational-unitary-fft/{gaussian_reference.py,gaussian.py,exact.py}`
and `research/certified-gaussian-recovery/intervals.py`. The retained source
adapter changes import bindings only, authenticates the input bytes and leaves
each executed numerical body unchanged. `Reference.for_cap`, which needs the
full circuit compiler, is not called by this adapter.

Let the same narrow reference have certified row gap δ>0, source period S,
target period T, original phase labels and original holes. Choose an ordinary
target window `[a,a+L)`. Retain a complement of length at least the source's
conservative physical bandwidth `2*source_halfwidth+2`. The setup also checks
every nonzero entry's retained lift is zero, every entry outside an admitted
ordinary half-band W is exactly zero, and

\[
 Q=(\operatorname{Reference.entry}(\mathrm{narrow},a+i,a+j))_{i,j<L},
 \qquad \operatorname{gap}(Q)\ge\delta,\qquad\|Q\|_\infty\le2.       \tag{1}
\]

`make_window` accepts an explicit proposed interior partition and validates it.
Each interior is a contiguous dyadic interval, of length at most the declared
dyadic cap, with no hole and one **original** phase. It is checked against
`Reference.interior`, including the original selected target coordinates and
period cut. Interiors are disjoint and increasing; every coupling between
different interiors is exactly zero. Thus this interface admits the retained
carve without claiming to implement or improve that carve. The boundary J is
the complete complement of the interiors I. Small windows may have no interior.

In I,J order prepare the exact matrices

\[
 Q=\begin{pmatrix}A&B_0\\C_0&D\end{pmatrix},\qquad
 F=D-C_0A^{-1}B_0.                                          \tag{2}
\]

The inverse and (2) are computed from exact source rationals, never from an
online approximate interior solve. Setup checks the exact Schur gap and norm
again. The inherited elimination argument gives gap at least δ and norm at
most two, without a symmetry or positive-definiteness assumption. Let E be J
together with every I coordinate incident to an original nonzero B₀ or C₀.
Both E and J retain increasing original target order. Setup verifies the
compressed F half-band is at most 2W−1 and the chosen dyadic block b covers both
that band and the compressed C₀ band. No live global entry oracle is supplied
to the online caller.

The first sparse window occurs **after** the first dense A⁻¹ call. Its admitted
current input u therefore has the form `u_I ≈ A^-1 x_I`, `u_J=x_J`; errors from
that prior call are already part of u. The local exact target acts on this
actual u:

\[
 T(u)_J=F^{-1}(u_J-C_0u_I),\qquad
 T(u)_{E\setminus J}=u_{E\setminus J}.                       \tag{3}
\]

It is incorrect to extract the current J values and apply F⁻¹ alone. All source
columns of C₀ are in E, so no omitted interior value is queried by (3). The
admitted radius is

\[
 \|u\|_*:=\max_{i,\text{complex columns}}
          (|\Re u_i|+|\Im u_i|)\le R,\qquad R\ge1.          \tag{4}
\]

This is a mathematical input promise, not a claimed modulus check by the tape
program. Inputs are already on the common P grid and fit the declared signed
word width. Any earlier grid conversion and dense A⁻¹ computation are outside
this component and must be paid by the caller.

## 2. Exact block factors for the original coupling shear

In E order embed N with entries from C₀ in J rows and `(E\J)` columns, and zero
elsewhere. Every pair of matrices supported in that same row/column mask has
zero product. In particular N²=0. Split by **block** position into N_L, N_D,
N_U: strictly lower blocks, diagonal blocks, and strictly upper blocks. Set

\[
 L_s=I+N_L,\qquad U_s=I+N_D+N_U.
\]

Because all the cross products vanish,

\[
 L_sU_s=I+N,\qquad (L_sU_s)^{-1}=I-N.                       \tag{5}
\]

Covering the ordinary band by b makes these factors block bidiagonal. The
lower diagonal blocks are exactly identity; the upper diagonal inverses are
exactly `I−N_D` on their respective blocks. These blocks need not be scalar
triangular. Every no-pivot elimination pivot is one: a nonzero entry has a J
row and an I column, so it cannot meet another such entry through a pivot.
The unchanged `prepare_pages` accepts this block support and computes the
stated inverse blocks exactly. We do **not** substitute scalar Doolittle
factors for the shear.

Separately, exact ordinary Doolittle setup produces `F=L_f U_f`, checking its
positive pivots and exact residual. Its ordinary bandwidth is inherited.
`physical_factors` serializes the four exact factors into the retained Matrix
format. The fixture then actually calls unchanged `prepare_pages` for each
factor pair. Page order is lower inverse diagonals, lower preceding blocks,
upper inverse diagonals in reversed **padded** order, upper preceding blocks.
The final incomplete block is padded by identity. Coefficients and exact
diagonal-block inverses are rounded toward zero once at P bits.

The producer's `rounded_pages` is only an expected-value observer. Supplying
its values in place of physical page generation would not satisfy the
executed preparation check. Factor serialization and page preparation occur
once per immutable source/window/grid key. They do not receive a payload,
RHS count or spectator coordinate and are never recomputed per RHS batch.

The current transaction first applies these shear pages on all E rows, extracts
J, applies the F pages, and replaces J. Every `(E\J)` value remains bitwise
unchanged. Rounded coefficients preserve the mask and exact identity entries;
all rounded errors in J are never used as shear source values. This proves the
preservation statement through both physical passes, including their padding.
It does not say that their several rounding sites equal one one-shot-rounded
shear. The independent checker includes a case where they differ.

## 3. Completed-residual budget and actual input radii

We retain the residual estimate of
CrocSwap/integer-mult-bounds#4186, also stated with the current source in
`rational-unitary-fft/CORE-PROOF.md`. Let η=2^(1−P), so a pair of real/imaginary
toward-zero truncations has complex-l1 error at most η. For a block lower
bidiagonal pass, let a bound the exact diagonal-block norm, c the preceding-block
norm, and M the norm of the full exact factor inverse. For the reversed upper
pass use the fully padded matrix with both axes reversed. Put

\[
 c_0=ab+2a+1,\qquad c_1=b[a(c+1)+1],\qquad
 K=M(c_0+4Mc_1).                                           \tag{6}
\]

Prepared inverse and coupling page errors are at most bη in row norm. With

\[
 b\eta\le1,\quad c_0\eta\le1,\quad Mc_1\eta\le\tfrac12,
\]

the completed block residual, followed by absorption, gives

\[
 X\le4MY,\qquad
 \|\widehat z-T_{\rm factor}^{-1}y\|_*\le K\eta Y.          \tag{7}
\]

Here X is the maximum of the **actual rounded** pass states. No exact-state
radius is silently reused for a rounded recurrence. Integer matrix products
are completed exactly before their inherited P rounding; the new seven-product
kernel preserves this ABI. Distinct columns never numerically mix, so arbitrary
batching, including across different prefix records, preserves (7).

For two successive passes, numbered 1 then 2, (7) gives error

\[
 e_{12}(Y)=\eta(M_2K_1+4M_1K_2)Y.                          \tag{8}
\]

The producer evaluates (6)–(8) with exact rational norms and inequalities. Let
e_s be (8) for the shear at R. Since `||(I−N)||≤1+||N||`, the actual F-solve
input radius is

\[
 R_s=(1+\|N\|_\infty)R+e_s.
\]

If e_f is (8) for F at R_s, the entire first-window error is bounded by

\[
 \|\widehat T(u)-T(u)\|_*
       \le\|F^{-1}\|_\infty e_s+e_f.                      \tag{9}
\]

There is no error on `(E\J)`. `make_window` rejects when (9) exceeds 2^−q.
It also explicitly checks every absorption condition and the signed carrier
range. Fractions in the receipt are exact; decimal fields are display only.

### A conservative allocation for every admitted size

Let

\[
 \bar p=\max\{W+1,\lceil\sqrt{1/(16\delta)}\rceil,1\}.
\]

Choose a dyadic `max(2,b_F,b_N)≤b≤4 pbar`; the minimum two accommodates a complex
column in the physical wrapper. For valid ordinary source geometry deletion
does not enlarge the N band, and the checked Schur band is at most 2W−1.
`sufficient_allocation` chooses a block from this conservative bound.

Because `||C₀||≤2`, each shear factor and inverse has norm at most three. In
(6), `a≤3,c≤2,M≤3`, so `K≤390b`. The two-pass shear error is at most
`5850bηR<2^13 bηR`. When `2^13 bη≤1`, its completed output is at most 4R.

For the Schur factors the inherited current-reference estimates are

\[
 \|U_f\|\le2,\quad \|L_f\|\le65\bar p^3,\quad
 \|L_f^{-1}\|\le32\bar p^2,\quad
 \|U_f^{-1}\|\le1040\bar p^5.
\]

Their complete solve error at radius 4R is less than
`2^42 pbar^16 ηR`. Propagation of e_s through `||F^-1||≤16 pbar²` therefore
gives a total less than `2^43 pbar^16 ηR`. It suffices to use

\[
 P\ge\max\{P_{\rm in},q+45+16\lceil\log_2\bar p\rceil+
                                      \lceil\log_2R\rceil\}.       \tag{10}
\]

This leaves a factor-two error margin and also funds all absorption conditions.
One conservative scalar word width is

\[
 w=P+52+16\lceil\log_2\bar p\rceil+\lceil\log_2R\rceil,            \tag{11}
\]

increased if necessary to cover the largest encoded source/runtime descriptor.
The inherited completed-state and arithmetic bounds are below
`2^48 pbar^16 R`; (11) leaves additional range. For the precise finite allocation
the producer checks the maximum of every pass input, `4MY`, coefficient row
norms `M+1,c+1`, and the explicit residual bound

\[
 Y+(c+b\eta)4MY+\eta.                                      \tag{12}
\]

Thus this check needs no unstated lower bound on M. A larger redundant guard
`6M(c+1)Y` is also retained in the code.

These are **scalar record** widths. The seven-product child uses operand width
`w+log₂b+2`, internal product width `2w+4log₂b+4`, and returns exact products at
the inherited width `2w+log₂b+2`. It then clears all owned roles. No scalar
record width is substituted for a packed argument length or an exact rational
setup height.

In the intended source regime, `pbar=O(p_master)`, target and incoming grid
`O(p_master)`, `log R=O(p_master)`, and the encoded descriptors have
`O(p_master)` bits. Only under these premises do (10)–(11) yield `w=O(p_master)`.
The finite fixture is not an asymptotic proof of those caller premises.

## 4. Current-grid chronology across union records

The source key is the axis reference pin, absolute coarse origin, window and
interior partition, and common block/grid/width. Spectator and prefix values
change only the RHS and header, so one such key may share pages across prefixes
inside its complete `(round,axis)` microbox substream. A different coarse origin
or reference is a different key. No cross-microbox sharing or free regrouping is
asserted.

Rounded axis maps need not commute. The valid schedule argument instead uses
the invariant classes determined by E-membership flags. A complete E_f-line
keeps all other coordinates fixed and stays in the same flag class. On each
class all records receive their first active axis, then their second, and so on
in increasing axis order. The line map is exactly identity outside E_f.
Consequently the round-by-active-axis order equals a full increasing-axis
**rounded** schedule, class by class. This requires neither linearity nor
rounded commutation. The independent finite whole-grid oracle uses that
increasing-axis rounded schedule; an exact tensor matrix is only an analytic
reference, never an exact rounded-output oracle.

For g sequential local maps with norm at most K, a caller may take
`R_(j+1)=K R_j+epsilon_j` and propagate preceding numerical error by
`E_(j+1)≤K E_j+epsilon_j`. A uniform `R≥(K+1)^g R_0` when local errors are at most
one, and local target `epsilon≤epsilon_total/[g max(1,K)^(g−1)]`, are sufficient.
These add `O(g log(K+1)+log g)` guard bits. Their actual outer application,
incoming dense errors and final recovery are not proved by this component.

## 5. Setup and retained-storage invoice

Preparation receives no online payload and no RHS count. It executes the
authenticated source's interval algorithms; reads the L² needed entries;
checks holes, phases, cuts, zero support and row bounds; forms exact interior
inverses, Schur matrix and factors; serializes those exact factors; and actually
executes the retained sequential `prepare_pages`. The latter scans its exact
matrix tapes for every requested entry, checks the complete adjacent-block
support, computes exact block inverses by reduced Gauss–Jordan, rounds once,
and writes the page banks. All of this work is separate from the online bill.

For an explicit deliberately loose invoice, write `u=2+L+b`. Let h bound the
numerator/denominator bit lengths of the generated reference entries and all
other source rationals used here, including the certified gap and coordinate
parameters. Put `h_R=bitlen(num R)+bitlen(den R)`. An admitted rational R close
to one may have an arbitrarily large description; its value or `log R` alone
does not pay for reading it or exact setup arithmetic. Let A_ref be
the **charged** bit work and C_ref the retained storage of the source interval
generation including its original-coordinate calculations. Exact rational
setup operations here number polynomially in u. Reduction is performed after
every arithmetic operation. Clear the denominators of the original matrix
using a product of at most L² h-bit denominators. More precisely, an n-by-n
rational determinant has numerator/denominator height `O(n²h+n log n)`: the
denominator of every permutation term divides the product of **all original
entry denominators**, while summing at most n! numerators adds only O(n log n)
bits. Exact Schur entries are ratios of bordered minors of the original Q.
The following Doolittle and consecutive-block inverse transformations apply a
fixed number of further polynomial-height bounds. Intermediate partial sums
add at most another matrix-dimension factor. A safe common envelope is

\[
 H=O\bigl(u^8(h+h_R+P+w+\log u+1)\bigr).
\]

This envelope also covers intermediate products and sums before reduction.
School multiplication/division and Euclidean gcd cost at most O(H³) with a
conservative elementary implementation. Simulating every host exact-matrix
lookup by a full sequential scan of its O(u²H)-bit store, including serialization,
support checks, physical Matrix get/set scans, loop counters and rewinds, gives
the sufficient bound

\[
 C_{\rm setup}\le A_{\rm ref}+O(u^8H^4+u^2w).               \tag{13}
\]

This is not an asserted exact Python action count. It is a complete polynomial
sequential simulation bound; the actual `prepare_pages` tape actions are also
reported separately by the fixture. Neither a matrix lookup nor transcendental
evaluation has constant cost in (13).

For clarity about A_ref, the unchanged source uses working precisions polynomial
in its entry bits, `alpha²/theta`, the squared retained cuts and their encoded
coordinates. Its Machin pi series and dyadic exp routines have polynomially
many precision-bounded operations; repeated references reuse the explicitly
retained caches. With

\[
 D_0=2+S+T+L+\alpha+\text{cuts}+\text{entry bits}+P+w+h_R+
       \lceil\alpha^2/\theta\rceil,
\]

both source heights and its complete sequential preparation are polynomial in
D₀. In particular for periods `2^O(ell)`, polynomial-p numerical parameters and
a radius description of height `h_R=poly(p)`, (13) is at most
`2^O(ell) poly(p)`. The online scalar-width consequence still needs only `log R`;
it does not require this stronger setup-description premise. This observation permits a separately
funded offline catalogue; it does not erase (13) from the generic theorem or
prove its amortization over a particular outer caller.

Fresh exact matrix storage is `O(u²H+C_ref)`. Page storage is exactly

\[
 2[(2K_E-1)+(2K_J-1)]b^2w\quad\text{bits},\qquad
 K_E=\lceil|E|/b\rceil,\ K_J=\lceil|J|/b\rceil,             \tag{14}
\]

apart from delimiters and fixed descriptors. Reusing physical tapes retains
their historical maximum allocated extents. Historical interval caches are
also retained unless their namespace is explicitly cleared; (13)'s fresh
space bound does not discard that history. Across source preparations either
use a fresh/cleared source namespace and pay its release, or add the complete
previously retained cache and physical backing extents to space. The online
consumer's live, parked, restored and erased roles are invoiced in the main
physical proof. The complete time is **setup + online**, not just online.

## 6. Finite source and evidence scope

The reproducibility source is `Reference(61,3,2,1,3,32)`, target period64.
Its description
hash is
`156be0b0199657b95b636597b332b378a1fe82d1a80e8b9cc84eaf90425694c5`.
The primary physical fixture uses ordinary window `[16,20)`, explicit cap2
interior `[1,2]`. The exact source checks give

\[
 I=(1,2),\quad J=(0,3),\quad
 E=(0,1,2,3),\quad J\text{-mask}=(1,0,0,1).
\]

The actual local Q and compressed F have band1. With b4,P24,w32,R1 and local
target2^−10, the exact rational error allowance is approximately
`4.65456e−5`, and the checked scalar-record radius is below24.019<128. There are
64 coefficient-page words across the two stages. Two complex E-lines fill one
four-column batch across different prefixes.

The inexpensive exact source checks also retain the larger ordinary window
`[16,24)`, cap4 interior `[1,2,3,4]`, with
`J=(0,5,6,7), E=(0,1,4,5,6,7)` and mask `(1,0,0,1,1,1)`. It has allowances
`4.65461e−5` at b4 and `2.50628e−5` at b2. These are rigorous finite admissions
evaluated with exact Fractions; a source-only admission is not a claimed
physical replay. The primary four-coordinate window has E equal to the whole
axis and therefore one flag class. The larger exact source and independent
rounded-grid controls permit multiple classes without attributing their source
checks to the primary physical run. A separate small rational masked-shear
physical control exercises nonzero lower, diagonal and upper block pieces and
distinguishes the inherited multiple-rounding function from one-shot rounding.

The 80-bit version of the same source geometry was also inspected during
preparation, but its different source pin is not substituted for the executed
fixture. Final receipts distinguish any completed extended run from interrupted
or source-only preparation.

The finite fixture uses an **exactly checked local band1**. It does not claim
to instantiate CORE-PROOF's sufficient global guard `W≥2*source_halfwidth+2=4`.
The four-coordinate interior is an admitted explicit partition, not an output
of the retained carve: that carve keeps every coordinate as boundary when
`L≤6W`. The all-size statement covers every partition satisfying its stated
checks, including ordinary retained carves; the small test does not claim to
be a production carve instance.
The general interface retains both original-period and exact zero-support
checks; conservative production geometry may use the larger global W.
This contribution makes no ideal-Gaussian error assertion from the finite
32-bit reference. Its target is the exact immutable rational matrix (1).

`source_checks.py` checks both block choices, omission of the essential C₀
shear, non-dyadic blocks, inadequate grid/carrier, crossing an original phase,
and overlapping proposed interiors. It also instantiates (10)–(11). These are
exact source checks, not physical execution. The independent source oracle
forms the original H directly and derives F by inverting the J-principal block
of H⁻¹, using a separate pivoted elimination/backsubstitution implementation;
it does not replay this producer's A-inverse Schur computation. Exact physical
setup, original-header transport, preserved bank values and nonlinear rounded
whole-schedule checks have their own executed receipts. Only receipts actually
completed by the final verifier count as evidence.

## 7. Provenance and limits

The retained reference geometry, immutable coefficients and narrow chronology
are from `rational-unitary-fft`, with the original Gaussian/union construction
in CrocSwap/integer-mult-bounds#4100. The generic residual/Strassen guards are
from CrocSwap/integer-mult-bounds#4186 and the source's CORE-PROOF. The header
and finite union chronology are inherited from the packages associated with
CrocSwap/integer-mult-bounds#4327. The actual inverse-page preparation and
two-pass ABI are from CrocSwap/integer-mult-bounds#5059. The new exact physical
seven-product implementation is pinned separately in this package's manifest.
Older old-H reference and return bridges, including
CrocSwap/integer-mult-bounds#5500 and CrocSwap/integer-mult-bounds#5506, are not
used to identify this source.

Credit belongs to Vlado Vojdanovski and the retained construction authors;
Jose Manuel for the common reference/core integration; Mason Hale for the
interval arithmetic; and the named predecessor contributors in the source
notices. Prepared for `@CubeJerry` with substantial OpenAI Codex assistance.
An independent research worker checked the original-matrix source relation
and the all-size residual carrier bound. Apache-2.0.

This component does not supply the incoming dense/raw circuit, literal global
union emission/routing, the broad forward window, core/halo assembly, normalized
return, FFT/CRT recovery or a complete lower integer-multiplication bound.
Those remain separately funded proof and implementation obligations.
