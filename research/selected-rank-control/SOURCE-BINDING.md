# Final rank-one control with supplied root cutoff and paid remainder hooks

Base: `e54523517d0f03e58352e647c403a5af3e525a57`. Prepared for @CubeJerry with
substantial OpenAI assistance; Apache-2.0. This refines the online controller's
source boundary. The earlier package remains unchanged. No new kappa or
framework-assumption discharge is claimed.

## 1. Exact source law, including the mismatch

`notes/batched-bit-rows.tex`, General moment condition, gives child width
`t_i*floor(e/m)`, not `floor(t_i*e/m)`. For e=mq+a, 0<=a<m, their difference is
floor(t_i*a/m), which can be positive. For m=3,t_i=2,e=5 the widths are 2 and 3.
Equality for every e holds exactly for t_i=1 within 1<=t_i<m: when t_i>1,
a=m-1 gives difference t_i-1. No raw mixed-rank substitution is made here.

`research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md`, Section 6,
instead makes every paid leaf rank one in a fixed compiled rank-N word. Under
tensor multiplicity f each becomes a rank-f call and the strict ratio is 1/N.
Combining this with the integer-width law gives exactly

    e = Nq+r, 0<=r<N; each of the P paid calls has width q=floor(e/N).

Here N and the paid-list length P are fixed finite constants of the compiled
word. This note does not materialize the enormous selected final word or prove
its compiler/owner semantics. It supplies a uniformly parameterized literal
controller for this exact final rank-one law.

The complex note's Stopping and weighted-tree bounds stops when e<d^beta.
For integer e this is equivalent to e<L with L=ceil(d^beta). L is a root
quantity, unchanged inside descendants. The new program receives L as a
positive unary input, and stops when e<max(N,L). Thus it agrees with the stated
complex stopping law when L>=N; small roots requiring individual processing
remain the source's fixed finite fallback. Generating L, or evaluating its
rational-power predicate from the actual binary root inputs, is not free and
is not implemented here.

## 2. Literal four-tape extension

`selected_control.py` uses the frozen earlier Builder and interpreter from
`controller_reference.py`, plus a read-only CUTOFF tape. N and P are compile-time
parameters. There are exactly

    30N+42+P(69+3N)

instruction locations, P+4 symbols and four fixed tapes, independent of e or L.
The N=3,P=2 example has 288 locations. No input-sized program or alphabet is
constructed at run time.

The old finite probe first detects e<N. Otherwise the comparator advances
WIDTH and CUTOFF in lockstep. It reads CUTOFF first: a blank means e>=L,
including equality; if CUTOFF is nonblank and WIDTH is blank, e<L. At either
exit it rewinds both heads. Each comparison step reads two symbols, moves two
heads and jumps, five transitions. If k=min(e,L), the two rewinds cost 6k+6.
Including terminal probes and the E/L edge and successor, the comparator costs
at most 11k+10. It never visits beyond k on either tape, never writes CUTOFF,
and returns both heads to their supplied markers. L can greatly exceed e;
comparison does not scan the entire cutoff in that case.

Internal entries emit E and then B_r, where r=e mod N. A separate finite
remainder-state scan proves r by the invariant current_state=k mod N after k
unary symbols, rewinds WIDTH and emits the hook. It costs 6e+7 transitions.
The P child calls use the old rank-one quotient machine, with the same tagged
parent-width push/pop and exact restoration. After the last return, a second
scan emits A_r, then X completes the node. Recomputing r avoids parking another
input-dependent descriptor. Both remainder scans see the restored parent e.

B_0/A_0 are explicit zero-remainder hooks: the payload consumer must skip the
remainder action, rather than interpreting zero as a positive recursive call.
All hook dispatch transitions are included in the controller invoice. Leaves
emit L,X and no remainder hooks. Arbitrary initial ancestors and all four
heads/cell contents are restored under the same valid-input convention.

The emitted hooks are labelled finite-control edges, not a materialized event
list. A consumer must preserve these descriptor tapes on return and pay its
own execution. Python traces and snapshots remain verifier observations.

## 3. Control time and retained backing

Parent-width park/return cost remains at most 48e+38 per child, excluding child
execution. The original N-probe costs at most 6e+7; the added comparison at
most 11e+10; both remainder scans total 12e+14. Counting node completion and
the root's final halt gives the conservative complete bound

    T_control <= 200(P+1) * sum_v e_v.

This includes every comparison rewind, remainder scan, continuation tag and
RETURN. The constant depends on the fixed number of paid sites P.

All child widths are floor(e/N), hence at most e/N and strictly positive at an
internal node. The original three-tape retained interval argument applies with
rho=1/N. CUTOFF adds visits to only min(e_root,L)+2 cells. If D is maximum depth,

    S <= K0+2(e+2)+e/(1-1/N)+D+2+min(e,L)+2
      <= K0+(4+N/(N-1))*e+8.

K0 includes the entire supplied cutoff and all preexisting erased backing.
Consequently this is a bound on new historical interval usage plus entry
backing; it does not hide a huge supplied L in a supposedly O(e) input bound.
Completed siblings reuse the same origins, so the bound does not accumulate
over the whole tree. No ancestor prefix below the entry delimiter is scanned.

When L>=N, the exact number of descents is zero for e<L, otherwise
1+floor(log_N(e/L)); the operational definition is repeated integer division
until below L, with no real logarithm routine. This follows from
floor(floor(e/N^j)/N)=floor(e/N^(j+1)) and
floor(e/N^j)>=L iff e>=L*N^j. Earlier stopping never requires more row stock than
the source's cutoff-N depth bound. This does not itself generate that stock.

## 4. Remainders and conditional node-volume composition

The complex note's Integer axis counts processes the r<N removed kernels
individually before the N equal q-axis slots. Removed axes remain completed
spectators. Tensor maps on the disjoint parts commute, so B_r is the appropriate
pre-hook; its A_r consumer may be a no-op. The bit note's Bit interchange with
a remainder instead exchanges/gathers the two high r-digit parts before the
main circuit and ungathers after it. Its consumer must implement both B_r
and A_r with the correct whole-field layout. A pre-hook alone is insufficient
for that retained BIT interface.

The compiled word's ordinary operations between paid calls must also remain
chronological. Attach its initial scalar/frame segment to the B_r consumer
(after remainder preparation), and each following segment to U_i while parent
WIDTH is restored, before the next descent or A_r. Thus the event interface
does not require pretending the paid children are consecutive with no scalar
work between them. Source binding of these segments and their charges remains
an explicit consumer obligation.

These are source-prescribed consumers, not newly implemented kernels. If their
complete transition costs are bounded by C_pre(N)*V and C_post(N)*V, including
all r individual operations, and their exact frame/ownership contracts hold,
then their combined local bill is a fixed multiple of V. The r axes are not
additional recursive children or artificially tiny stopping leaves. For r=0
these payload actions are skipped, with the controller's finite hooks paid.

Under the selected review Section 5 complete-root-factor invariant, at least
one complete D-bit factor per node gives V_v>=2^D>=D>=e_v. The full controller
bill is then at most 200(P+1)*sum_v V_v. Combining it with admitted remainder,
frame and scalar fees gives the conditional node recurrence

    T(V,e) <= P*T(V/W, floor(e/N)) + C_template*V

above the supplied cutoff, and the existing separately paid leaf routine below.
C_template includes controller and both consumer constants; it is not an old
numeric cap. Each child receives V/W only if the actual complete-row/stock
interface supplies that volume. This controller does not prove the grants,
remainder operators, compiler, native endpoints or numerical/analytic bounds.

For the complex stopping source, if d^beta>=2N, every nonroot stopping leaf
arises from a parent e>=d^beta and has width floor(e/N)>=d^beta/(2N).
The bounded r<N remainder actions stay local hooks, so they do not create
extra width-one stopping leaves that would violate that guard interface.
This is the source's quantitative boundary instantiated at the compiled N;
the precision/guard theorem itself remains retained.

## 5. Verification, novelty and remaining work

The verifier observes both event labels and actual unary widths. It checks the
exact cutoff equality, repeated paid sites, pre/post remainders (including
zero), restoration and retained intervals. A separate dense CPU corroborates
translated examples. Controls mutate the cutoff equality branch, a cutoff
head move, post-remainder identity and omission; a raw-mixed rounding fixture
prevents treating the two floor laws as identical. Universal claims are the
written loop/stack inductions, not extrapolations of these finite executions.

The extension's new work is the actual rank-one source-law/cutoff/remainder
connection. It does not repeat #5158's fixed-bank recursion or #6719's much
richer delayed-cover binary-root/grant/payload program. It adds no selected
kappa and discharges none of the five full framework assumptions.

Next steps: supply actual binary root cutoff/width production; bind the selected
P,N and any remainder/leaf adapters to a final occurrence emitter; join literal
payload consumers to the hooks with exact tape frame and step contracts. Those
remain substantive obligations, not completed consequences of this control proof.
