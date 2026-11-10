# A source-bound shrinking-domain Gaussian halo consumer

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Result, scope and predecessor boundary

This is a constructive local tensor result under a certified fixed-reference
row gap. It supplies the numerical consumer and its sequential data/page
protocol on one saved sparse rectangle. It does not prove the complete outer
Gaussian construction, admit the selected suppliers, or change kappa.

The fixed-source Horner identity is classical. In this repository, #1430 already
uses it to control rounding under a fixed approximate oracle with norm at most
0.42; #6490 allocates precision across that oracle's calls. #5159 implements a
rounded whole-period action on one actual rational Gaussian Reference, with
coefficient error, data error and storage charged at a host-array interface.
#5216 improves its tail and #5260/#5284 supply direct-solve alternatives, also
without a complete physical sparse caller. #3851 implements a different
principal-core/Schur interface, with its own source parameters and gap.

#6880 already proves direct row-gap locality, normalized nonlinear core/halo
composition, inward-rounded polynomial rows, and the specialization J=16p^4.
Those are not new claims here. That package leaves production of the global
polynomial coefficient pages and their physical access unpriced. #4100's HALO
argument permits a polynomial-time local correction but does not implement
the present recurrence, shrinking domains, or table/line schedule.

The contribution is an explicit replacement for that remaining polynomial-row
interface: store only the original reference band, shrink the dependency
interval after every iteration, expose axes by sorting only sparse records,
reuse one page across every spectator line, and use eight fixed local tape
roles plus one protected coefficient archive. Its quantified all-size bill
includes reference production, repeated full archive scans, encoded controls,
scalar arithmetic, copies, head returns and retained blank backing. A full-axis
scan is retained explicitly in the generic theorem; it is absorbed only in the
specified balanced growing-group regime.

The universal argument below is a written proof. The executable fixtures
corroborate it; neither finite traces nor separate AI review are formal-kernel
or independent human acceptance.

## 2. Exact input contract

For axis i, let H_i=I-E_i be a real rational matrix of period N_i. Let W_i be a
nonnegative integer with 2W_i<N_i. A matrix entry E_i[r,c] is zero unless c is
congruent to r+v for a unique integer v in [-W_i,W_i]. Require

    ||E_i||_infinity <= rho_i = 1-delta_i,   0 < delta_i <= 1.

The finite producer checks the mass of every stored row. In the generic
theorem, zero outside the stated band is a separate hypothesis: checking a
row's stored entries cannot certify unstored entries. For the source binding
in Section 7, the original Reference support rule proves this hypothesis;
the finite checker also enumerates the entire matrix independently of the
producer's band enumeration.

Let s_i=2W_i+1, J_i>=1, and choose an integer u_i>=0 with
a_i=2^u_i and a_i delta_i>=1. Choose one data/coefficient grid h=2^-q with
q>=max_i u_i. The incoming complex array has components on this grid and

    ||x||_* = max_r (|Re x_r| + |Im x_r|) <= R,

where the executable interface takes an integer R>=1. A complex-modulus unit
disk input fits this interface with R=2. Every actual incoming line is checked
against its stated bound. The theorem does not infer an outer caller's input
radius merely from an exact ideal map.

An output interval T_i=[t_i,t_i+m_i) is interpreted on the integer lift of the
physical circle. Set b_i=(J_i-1)W_i and

    D_i = [t_i-b_i, t_i+m_i+b_i),     d_i = m_i+2b_i.

Require d_i<N_i. Thus even a wrapping interval contains each canonical
coordinate at most once. The saved input rectangle is D=product_i D_i, and
the target is T=product_i T_i. Coordinates are reduced modulo N_i only when
addressing the fixed global reference or the original global array. A page
is never redefined as a translated Reference and does not merge the original
period's first and last phase cells.

The saved rectangle must already contain the original pre-core-mutation values.
Its construction and the final unique dense return belong to the enclosing
caller. This consumer owns and may consume the saved copy. Its per-axis source
line is immutable until that line's complete polynomial output has been made.
It returns only T, in increasing lifted lexicographic order.

## 3. Normalized fixed-source recurrence and actual numerical states

Truncate each real coefficient of E_i toward zero to the q grid, obtaining
Ehat_i. This is truncation of the fixed rational reference, not an assertion
that one can determine the exact floor of an irrational Gaussian coefficient.
Then

    ||Ehat_i||_infinity <= rho_i,
    ||Ehat_i-E_i||_infinity < s_i h.

All s_i slots, including zero slots at holes and the zero diagonal, are stored
and paid for. Let Q_q truncate both real and imaginary components toward zero.
Its error in the component-l1 norm is less than 2h and it does not increase
that norm.

For a fixed incoming line x, use

    z_0=0,
    z_(k+1)=Q_q(x/a_i + Ehat_i z_k),       0 <= k < J_i.       (1)

Every z_k remains on exactly the same q grid. If ||z_k||_*<=R, then

    ||x/a_i + Ehat_i z_k||_* <= R/a_i + rho_i R <= R.

Truncation preserves the bound, so induction proves that every *computed*
state has radius at most R. The input to a later tensor axis consequently
fits the same contract. No unproved rounded-map Lipschitz property is used.

The program forms each dot product and its fixed-source summand exactly, then
rounds the completed real and imaginary sums once. If input/data numerators
are X and Z and a stored coefficient numerator is C, its accumulator is

    X * 2^(q-u_i) + sum C Z,

at scale 2^(2q). This is why q>=u_i is required. The absolute component-l1 sum
of any partial accumulator is at most R*2^(2q): it is bounded by the source
term plus a partial sum of coefficient absolute values times R. A signed
carrier of 2q+ceil(log2(R+1))+2 bits is ample. Coefficient and data carriers
have q+O(log(R+1)) bits. The code checks the actual partial accumulator bound,
not just the final rounded result.

Write y_k=(1/a_i) sum_(j=0)^(k-1) E_i^j x. Its norm is also at most R.
Subtract its recurrence from (1), evaluating the perturbation at the *actual*
z_k. If e_k=||z_k-y_k||_*, then

    e_(k+1) <= rho_i e_k + s_i h R + 2h,    e_0=0.

Therefore

    ||z_(J_i) - P_i x/a_i||_* <= nu_i,
    P_i=sum_(j=0)^(J_i-1) E_i^j,
    nu_i=(s_i R+2) h/delta_i.                              (2)

The sharper finite geometric factor could be retained; (2) is sufficient.
The exact normalized polynomial and inverse both have induced norm at most
one, and the tail is

    ||P_i/a_i-H_i^-1/a_i||_infinity
        <= tau_i = rho_i^J_i/(a_i delta_i).                 (3)

These numerical estimates retain standard Neumann/Horner reasoning and the
whole-period predecessor's coefficient/data accounting. Their role here is
to certify the actual finite-precision sequential local program.

## 4. The shrinking domain is exactly sufficient

Define

    D_i^(k) = T_i + [-(J_i-k)W_i, (J_i-k)W_i],
                         1 <= k <= J_i,

where the notation denotes the corresponding half-open integer interval.
Compute z_1=Q_q(x/a_i) on D_i^(1)=D_i. To compute z_(k+1) on D_i^(k+1),
read its source x there and every previous neighbor within distance W_i.
Those neighbors lie in D_i^(k). The global coefficient for the corresponding
canonical row and offset is obtained from the already fixed band page.

Induction on k now proves equality, bit for bit, with the restriction of the
full-period rounded recurrence (1). This statement does not require linearity
of rounding. It follows because each local update sees exactly the same
coefficient numerators, source numerator and prior neighbor numerators as the
global update. At k=J_i the returned interval is precisely T_i.

This is not the polynomial of E restricted to T_i or to the eventual returned
rectangle. Such a restriction loses paths that leave and reenter it. The
program retains D_i^(k) until its use at the next step, then discards only the
two already unnecessary boundary strips. The initial padding is exactly the
maximum dependency distance of the degree J_i-1 polynomial.

For h_axes axes processed in order, after completing axis i the maintained
rectangle is

    S_i = T_0 x ... x T_i x D_(i+1) x ... x D_(h_axes-1).     (4)

At the next axis, every needed neighbor differs only in that next coordinate.
The earlier coordinates therefore need no padding after their axes have
completed. The later coordinates must retain their complete original D_j.
Applying the one-axis induction to every spectator line proves exact agreement
with the corresponding restriction of the full-period nonlinear tensor
recurrence. That full-period recurrence is an analysis device, not an executed
dense algorithm.

Compare this global rounded composition first with the product of P_i/a_i.
Each local error bound (2) holds at the actual incoming state, which has radius
R. Each exact P_i/a_i is a contraction. Telescoping against these exact maps
gives numerical error at most sum_i nu_i. Telescoping (3), using contraction
of both factors, then gives the complete inverse-tensor guarantee

    ||returned - [product_i (H_i^-1/a_i)] x |_T||_*
        <= sum_i nu_i + R sum_i tau_i.                     (5)

No factor depending on the global tensor dimension occurs in (5). No
assumption that the rounded program itself is additive or nonexpansive is
made. The proof applies to every global extension of the saved input with
radius at most R, since all omitted inverse dependence is explicitly funded
by (3).

## 5. One sequential line and its exact invoice

The global band table is ordered by canonical row, then by offsets -W_i to
W_i. A local page is ordered by lifted row, then by the same offsets. If D_i
wraps, one complete table scan emits its final-period part, and a second
complete scan emits its initial-period part. All skipped coefficients are
read and both complete scans return to the origin. No constant-cost global
row query, arbitrary seek or hidden page cache is assumed.

`apply_line` uses the immutable source, immutable page, and two owned iterate
tapes. It forms z_1 by one source scan. During an update, a row reads the
2W_i+1 adjacent previous records in increasing order. Before the next output
row, the previous-state head walks back exactly 2W_i records. Thus the next
window advances by one. At the final row the head is at the end of the prior
live body. The source and page also make explicit forward skips and complete
returns. Before reusing an iterate role, the program clears its complete
previous live body, including all rows that existed before the next shrink.
It never substitutes the smaller newly produced length for that old length.

Each role maintains a live-body length and a separate historical extent. All
cells at or beyond the live length are already zero. The invariant is true
on a fresh blank tape. A write extends the live length through its position;
the formerly unoccupied gap and remaining suffix were already blank. Clearing
the complete previous live body makes the live length zero and leaves the
invariant true. Thus a historical blank suffix remains paid in space without
being rescanned at every later reuse. Program transitions use this invariant
and encoded lengths, not an uncharged host inspection of the backing array.

This distinction is necessary for the claimed tariff. A long L-sized line
followed by an A-sized face line must not pay L cells per clear on each short
line. That alternative adds a factor L/A and can consume the sparse volume
saving. The verifier executes a long-line/short-face/long-line history on the
same roles, checks actual blank suffixes independently, and compares an
executed counterfactual that clears the historical extent on every reuse.

For target length m, the live lengths after k terms are
n_k=m+2(J_i-k)W_i. A complex line performs exactly

    2s_i sum_(k=2)^J_i n_k
      = 2s_i[(J_i-1)m + W_i(J_i-1)(J_i-2)]

integer products and the same number of accumulator additions. It performs

    2 sum_(k=1)^J_i n_k = 2[J_i m + W_i J_i(J_i-1)]

component roundings. The fixed-source shifts, reads, output writes,
initialization, complete old-live-body erasure and all head motion are separately
counted. J_i=1 and W_i=0 are allowed by these formulas.

Let w bound the numerical carriers and the entire encoded descriptor/control
block, including signed absolute origins, lengths, periods, iteration counts,
loop counters and local keys. A decoded scalar integer addition, shift,
comparison, multiplication or division is implemented by ordinary fixed-tape
binary arithmetic. Schoolbook multiplication/division costs O(w^2). Even
charging O(w^2) for each scalar encode/decode, rather than treating a host
integer shift as unit time, a line costs

    O(J_i d_i s_i w^2) bit operations.                     (6)

Its source plus two iterate roles occupy at most 6d_i times the component
carrier width; its page occupies d_i s_i(q+2) bits. Add O(w) scalar/control
storage and the separately retained global archive. A returned output occupies
one of those two iterate roles, so it is not omitted from the space count.
Unused suffixes can remain allocated but are blank and are included in this
bound. `maximum_single_tape_extent` is only the largest individual tape;
the verifier separately sums every retained local role.

The Python program executes every binary tape read/write and one-cell head
move. Its integer operations implement scalar-macro semantics; its elapsed
Python time is not asserted to equal the asymptotic bit bound (6). The proof
supplies the fixed-tape implementation and cost of those scalar macros.

## 6. Complete local rectangle schedule and generic cost

The payload has a fixed-width key comprising the nonnegative offsets within
the original D_i, followed by signed fixed-width real/imaginary numerators.
Let K=sum_i max(1,ceil(log2 d_i)); unused field encodings are not valid
coordinates. An initial lexicographic stream is encoded in one charged pass.
The same fixed key fields remain valid after an axis shrinks. Return converts
offsets back to lifted coordinates; the outer caller may reduce them modulo
the periods in another explicitly charged pass.

To expose axis i, perform stable least-significant-bit distribution into two
fixed buckets. Process the bits of field i first, then the bits of the other
fields in reverse natural order. Concatenation of the zero and one buckets
after each pass leaves the other fields in natural lexicographic order, with
axis i innermost. Each pass scans and clears the entire live owned sparse body
and both live buckets; already blank retained tails obey the same invariant.
It never scans the dense
global data array. There are exactly K passes per axis. The conservative
scalar encode/decode convention above charges O(K C_i w^2) bit work for a
body with C_i records, rather than hiding key operations in a unit-cost word.

After exposure, each complete spectator line is copied into one reusable
immutable line role, evaluated by Section 5, and emitted with target-only
keys into the alternate rectangle role. The local band page is produced
once per rectangle/axis, before its first line, and reused across all of those
lines. Only after the entire axis output is complete is the previous rectangle
cleared. Equation (4) gives the next live shape. After the final axis, natural
lexicographic order is already restored.

There are eight local roles: current/next rectangles, two radix buckets,
one line source, two iterates and one local page. Their count is independent
of J_i, the number of lines, rectangles and axes. `tensor.py` creates the pool
once in `TensorWorkspace`, passes the same iterate roles to every line, and
clears every nonreturn role. After the caller consumes and clears the returned
rectangle, the same workspace accepts the next rectangle through the explicit
`rectangle_input(..., tape=...)` and `apply_tensor(..., workspace=...)` interfaces.
The verifier seals all tape constructors across a long/short/long sequence of
complete rectangle calls and checks that the identical eight role objects
return blank. Across such a history, space is the sum of the eight historical
extents, bounded by the largest admitted body for each role; time depends on
the currently occupied lengths, by the invariant in Section 5.
The global tables are concatenated in one protected archive; `pack_tables`
consumes and clears one temporary table before requesting the next from its
generator. Thus a growing number of axes does not require a growing number of
physical tapes. Descriptor tuples in the Python reference represent one
encoded control block. Scan/selection costs on that block are bounded by w
and included in the w^2 allowances; indexed metadata is not free access to
payload or coefficients.

Let C=product_i d_i and G=sum_i N_i s_i be the total band coefficient count in
the current group's archive. The executable scans the *entire concatenated
archive* once or twice for each axis page, including other axes' coefficients.
If T_ref denotes reference production and quantization, the complete generic
local bill is

    T_ref + O(w^2 [h_axes G + C sum_i (J_i s_i + K + 1)]).   (7)

Input codec, all source/data/page transfers, output copying, sorting,
arithmetic, head returns and erasure are included. T_ref is a separately
amortized group setup if the archive is reused for several rectangles. The
term h_axes G remains present for each rectangle; it is not automatically a
local polynomial merely because d_i is polynomial.

With eight local roles, their total retained extent is

    O(Cw + max_i d_i s_i q),

plus O(w) control/scalar storage and the protected archive G(q+2). At most a
constant number of old/new rectangle bodies coexist. The producer's setup
scratch is additional, as quantified next. The code's physical action counts
and full retained extents are evidence for this schedule, not a byte-exact
claim about Python's object allocator or secure memory zeroization.

## 7. Binding to the actual retained Gaussian entry producer

The live source is `research/rational-unitary-fft/gaussian_reference.py` at
the exact base in SOURCES.json. Its original geometry and proof are retained
in `RAW-GAUSSIAN-PROOF.md`. `source.py` authenticates all source bytes before
execution. It rebinds the original import dependencies and extracts only the
unchanged `rational`/`load_intervals` helpers from `gaussian.py`, avoiding an
unused full-circuit compiler import. It changes no executed numerical function
body. `Reference.for_cap` is not called by this adapter; its use would require
the larger compiler dependency closure.

For original source size S, excess K0, target period N=S+K0, and
theta=K0/S, the source fixes

    c_j=floor(theta*j+1/2), q_j=j+c_j, beta_j=theta*j-c_j.

The narrow reference has identity holes and zero selected/hole cross entries.
For a source halfwidth w0 with 2w0<S, it keeps the unique nearest-period source
offset of size at most w0. Its physical target halfwidth is at most 2w0+2.
The producer's shared-weight-ratio, cross-cell and cross-period branches are
retained exactly. The diagonal is exactly one. A physical band W>=2w0+2
therefore contains every nonzero entry of E=I-H. Our table loops over every
canonical target row and every physical offset, calls that exact entry rule,
checks the original row mass and truncates the resulting rational toward zero.
Holes and genuine period crossings use the same rule as all other entries.

The source's relative-weight construction avoids silently replacing tiny
positive weights by zero. With entry precision b_e its weight precision is

    P_weight=ceil(2 alpha^2/theta)+b_e+7,

and its kernel precision adds O(alpha^2 w0). Under the retained caller's
theta in [1/(4p^2),1/p^2], alpha^2=O(log p), b_e=O(p), and W<p, these are
O(p^2 log p) offline heights. The source interval proof gives terminating
Machin/Taylor loops at requested precision. The rational reference entries
are generated before the present q-grid truncation; they are not redefined
at each rectangle origin.

Here is an intentionally loose fixed-tape production bound. Let B exceed
all coefficient/parameter descriptor heights, requested interval precisions,
W+1, q+1, and log2(N+1). Source coordinate arithmetic uses O(B)-bit integers.
The two Machin arctangent loops have O(B) terms: their denominators contain
5^(2j+1) or 239^(2j+1), and the requested tail is 2^-O(B). Their exact rational
sums are then rounded to the requested B-bit dyadic interval. The positive
Taylor loop for exp(-x) has O(B) terms on that dyadic grid; the source proof
gives a stop by ceil(J/3) at working precision J. The source either takes its
large-argument shortcut or performs at most O(B) range-reduction and squaring
steps (the logarithmic bound would also suffice). These are explicit finite
loop bounds, not an assumed polynomial-time exponential oracle.

Even a product of all denominators in O(B) exact Machin terms has O(B^2) bits;
reduction cannot increase that bound. Temporary products and row-mass sums
also have O(B^2) bits, since W<=B. On H-bit integers, schoolbook operations
and Euclidean reduction have a safe O(H^3) allowance. O(B) such steps therefore
cost at most O(B^7); O(B^8) per source evaluation safely includes powers,
encoded loop controls, conversion and the fixed number of source branches.
The dyadic Taylor and squaring operations need smaller bounds. This justifies
the deliberately loose polynomial used below without hiding rational heights.

The original Python caches can be serialized and looked up by complete
sequential scans. There are O(Ns) cached records, each of polynomial B size.
Charging such a full scan at each of O(Ns) entry calls, rather than assuming
a constant-time dictionary, yields the safe production bound

    T_ref = O(N^2 s^2 B^10),    setup space O(Ns B^2),         (8)

including scalar arithmetic, cache records, coefficient division/rounding,
table writing, cache erasure and all returns. Several axes sum their versions
of (8). This is a conservative implementation argument, not a fast setup
benchmark. A producer that recomputes instead of caches also satisfies a
fixed polynomial allowance. The finite source run executes the retained
producer and records cache counts and actual rational heights; it does not
claim that the host dictionary trace itself is the serialized simulation.

The complete row-gap certificate and the analytic comparison between this H
and the ideal Gaussian remain inherited from the cited source. Our setup
checks the chosen rational gap on every actual reference row. If a caller
also supplies ||H-H0||<=E0<delta, the standard resolvent identity adds

    R E0 / [a delta(delta-E0)]

for a normalized single-axis inverse. This is the already known reference
perturbation bridge, not a new analytic proof. Each such error must still be
included when adopting (5) in an outer caller.

## 8. Complete substitution into the retained sparse budget

This section is a conditional implementation substitution into #4100's
archived route, not acceptance of that route or of a new multiplication
theorem. Its exact parameters are in the pinned PROOF/GAUSSIAN/HALO files.
The underlying direct row-gap specialization is already in #6880:

    delta_i >= 1/(16p^2), W_i<p, J_i=16p^4,
    b_i=(J_i-1)W_i<16p^5.

Keep the existing conservative A=ceil(p^48) and
L=2^ceil(400 log2 p); no new core geometry is needed. Require eventual
checks L>4A, b_i<=A and N_i>=2L. Then every first-face expanded side has
length at most L+2b_i<N_i. It satisfies the nonaliasing contract in Section 2,
including physical wraps.

Use a common q>=F_in, max_i u_i, where F_in is the actual incoming grid, and
fund, for a desired local group allowance 2^-Cp,

    q >= Cp + ceil(log2(4 h_axes max_i[(s_i R+2)/delta_i])).   (9)

This makes sum_i nu_i<=2^-Cp/4. Since rho_i^J_i<=exp(-p^2), the tail term in
(5) is also below 2^-Cp/4 eventually for fixed C and polynomial R. The chosen
q is O(p) whenever F_in=O(p) and R is polynomial. No exact incoming bits are
discarded: q is at least F_in. One may choose a_i between delta_i^-1 and
2delta_i^-1, or use the caller's larger existing dyadic p^100 normalization.
The same normalizer must be used by any core route with which these outputs
are spliced. The total outer compensation is O(d log p)=o(p), and must be
paid/restored by the existing caller; it is not canceled for free here.

For completeness, implement the source's “balanced groups” explicitly. With
d>=g>=2, put m=ceil(d/g) and split the d axes into m groups of sizes
floor(d/m) or ceil(d/m). Every group has at most g axes and at least
floor(g/2) axes. Thus there is no exceptional final one-axis remainder to
which a growing-group amortization has been incorrectly applied.

The source has ell=Theta(p^(1-epsilon)), axis periods at most 2^ell,
d=Theta(p^epsilon), and g=Theta(p^beta), with beta>1-epsilon. A first-face
rectangle has at least h_axes-1 long sides of length L-2A, so its volume C
satisfies

    log2 C >= (h_axes-1) log2(L-2A).

Because h_axes=Omega(p^beta), the right side dominates
ell + c log p for every fixed c. Therefore even a complete concatenated
axis archive scan, of size 2^O(ell) poly(p), repeated once or twice per local
axis, is eventually bounded by C. This proves absorption of the repeated
scan term in (7). It is stronger than simply saying local setup is polynomial
in p. For arbitrary fixed h_axes, or any failed finite comparison, retain
the full h_axes G w^2 term. The effective comparison can be made with integer
bit lengths before adopting the asymptotic branch.

Offline production across all d axes costs
d*2^O(ell)*poly(p)=2^o(p)=o(V), using (8), where V=T_total*p is the source's
full bit volume. This is a different charge from repeated per-rectangle
archive scans. Preparing each group's archive once as it is reached gives
the same summed bound and uses a constant physical tape pool.

In the actual balanced regime, all control/coordinate fields fit O(p) bits:
h_axes log L=o(p), h_axes ell=o(p), and the source uses beta+1-epsilon<1.
Numerical carriers have O(p) bits by (9). Thus w=O(p), J_i=O(p^4), s_i=O(p),
and K=O(p). Equation (7) gives the deliberately conservative local bound

    O(C h_axes p^7) bit work, plus the explicit offline setup. (10)

There are O(h_axes A/L) copied records per original full-array record in a
group. Summing (10) over all rectangles and O(d/g) balanced groups gives

    O(V d g A p^6 / L)                                    (11)

for this numerical consumer, with sparse layout, pages and arithmetic
included. It is inside the older allowance O(V d g A^3/L polylog p).
With A=p^48 and L>=p^400 its exponent is at most
epsilon+beta+54-400<0. The dense gather/return scans remain the separate
O(V d/g) row of the outer ledger; this package does not invoke a dense scan
per numerical axis. The existing first-face copy producer and unique-return
transaction must provide those operations. Formula (11) is not a new kappa
claim; it establishes that this explicit consumer does not exhaust the
already reserved conservative halo budget.

## 9. Evidence, limits and remaining composition

The verifier uses exact integers and Fractions for every acceptance decision.
It checks 32 signed nonstationary cyclic-band lines, including identity holes,
negative/positive coefficients and wrapping targets. Its independent dense
polynomial evaluator forms successive powers and their sum. A second global
rounded evaluator checks exact bit equality, while the written proof supplies
the universal quantifiers.

Two synthetic tensors execute the complete sparse tape schedule in two and
three dimensions. A second history executes three differently shaped rectangles
with the same eight roles and no new tape construction permitted. The actual source fixture is
Reference(32,8,2,1,8,32), with period 40 and eight identity holes. All 1,600
original entries are checked, including omitted entries and genuine wraps.
Three local lines and a 756-record two-axis saved rectangle are executed;
the latter returns exactly twelve target records. Its source-certified gap,
numerical bound, tail bound, complete products/roundings, page scan count,
radix count and summed retained extents are recorded in RESULT.json.

These finite source parameters are legal for the retained Reference API but
are not an execution of the eventual outer production regime. The all-size
parameter substitution rests on Sections 7–8 and the explicitly retained
source hypotheses, not on extrapolation from forty rows.

Controls reject wrong normalization, insufficient source grid, ambiguous band
offsets, missing row gap, oversized actual data, aliased page intervals,
incorrect dependency crops and negative-zero records. Actual consumer code
mutations exercise wrong recurrence sign, wrong neighbor rewind and omitted
erasure, wrong sparse-axis exposure, stale axis pages and shifted return keys;
a dropped actual periodic branch changes the returned source answer. The
long-short-long history and counterfactual high-water tariff guard the
physical reuse obligation that is invisible to a numerical-only comparison.
Normal and optimized replay do not rely on Python assertions.

Two additional checks were independently developed during adversarial review.
Neither imports verify.py, the dense-power oracle, or its expected outputs.
The first solves four rows of the original forty-by-forty H inverse by exact
rational elimination of H^T. Every computed row satisfies its exact inverse
equations. Tensoring these rows then gives an independent original-inverse
answer at four two-axis targets, against which the physical consumer has
maximum component-l1 error below 5.252e-9, within (5)'s 8.213e-8 allowance.
Its nested target has identical returned bits, all eight tape roles are reused
with constructors sealed, and the reference archive stays unchanged. A shifted
target control has error greater than 0.109.

The second executes every singleton output of one forty-row input, computes
the original-reference residual r=x/a-Hy, and uses
||H^-1||_infinity<=1/delta to certify ||y-H^-1 x/a||<=||r||/delta.
This gives error below 7.667e-9 without using a polynomial oracle. For a
cyclically shifted returned vector, ||r||/||H||_infinity gives an error lower
bound greater than 0.543. Every acceptance decision is exact rational
arithmetic. Both scripts run normally and with assertions disabled as
registered checks; their decimal output is only a readable summary.
The independent method and implementation provenance concern a separate AI
reviewer in the same research effort, not external mathematical acceptance.

No arbitrary native implementation, complete finite-core adoption, dense
first-face copy/return protocol, broad Gaussian map, all-depth supplier,
outer tensor/CRT algorithm or exact integer-recovery theorem is established
here. The source H, its certified row gap and ideal-Gaussian comparison remain
named dependencies. #5325 and #4415 already address other error-join/suffix
questions; their results are not duplicated or silently assumed compatible
with a different rounded reference. A complete join must verify that the
core, this consumer, normalizers and the eventual outer recovery use the same
source interface and actual grid/radius contracts. All five selected
framework assumptions remain in force. No new kappa.
