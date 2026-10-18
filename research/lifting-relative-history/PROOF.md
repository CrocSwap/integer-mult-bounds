# Configuration-relative history for the batched lifting core

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
This is a conditional written construction, not a new general reversible
simulation theorem, formal-kernel proof or independent human review.

## 1. Result and why the ratio matters

Retain Jose Manuel's PR3109 exact batched lifting map, its literal inverse,
parameter order, four-call protected evaluator and error bound. Retain the
complete-configuration envelope bound in PR3122, under the named exact-C,
ordinary-bit and source/compiler premises. For `N=2^n`, `n=Theta(r)` and input
component width `W=Theta(r)`, there is a checkpoint realization with

    time = O(N r^(2-997/1200000)),
    additional clean space = O(N r log(r+2)) + O(F log(r+2)),             (1)

where the exponent statement fixes the inherited compiler allowance F.
Unsimplified formulas below retain mutable F in both time and space. The
protected source and dirty target remain separate; no dirty-workspace
conversion is claimed. The error bound remains `r sqrt(N/2)` in integer
units in each direction because the executed nonlinear map is unchanged.

This exchanges some of PR3109's subquadratic time saving for nearly
input-sized clean work. It does not preserve its exact time exponent.
There is also a fixed-height family preserving that exponent, with clean
space exponent `1 + (997/1000)(599/600)/(H+1)` for each fixed height H.
H=1 recovers PR3122's exponent `1797203/1200000`.

The mechanism is classical multilevel Bennett checkpointing. The important
application detail is to stop its base segments at **configuration-scale
length S**, so the tree has `log_b(T/S)` levels. Applying a unit-step bound
in T would introduce a power of the full payload N into the time cost and
would miss (1). No such extra power occurs in the construction below.

The explicit fixed branching constant used to prove (1) is `b=2^1200`.
Constants and crossover sizes are enormous. This is an asymptotic interface
result, not a practical performance recommendation. Finite tests use small
radices and report their actual recomputation and routing costs.

## 2. Protected segment and configuration contract

Let a deterministic fixed-tape machine have uniform time bound T and a
complete mutable configuration of S bits, both fixed before reading values.
Include tape contents, head markers, finite control, resumable call state
and enough controller allowance that `S >= c log^2(T+b+H+2)` for a fixed c,
where b and H are the public plan parameters in section 3. In both useful
regimes of section 5 this requires only `O(log^2(T+2))` padding, with constants
depending on the fixed parameter. Section 6 shows that this does not change
the source's O(Nw)+F configuration envelope. Immutable transition code is
shared; mutable compiled data must be included in S.

A protected segment of length at most L uses the credited 1973 construction:
copy its source configuration into active work, simulate with a constant-size
old-symbol/state history per transition, XOR the requested endpoint into a
disjoint arbitrary target, reverse the trace, and XOR-uncopy the restored
active configuration. Its source is preserved and owned work returns zero.
It costs O(L+S) time and O(L+S) clean work. Copy, output projection, head
positioning, local rewinds and history erasure are included. Full configuration
copies or an increasing-position projection are allowed; a general random
output permutation is not granted a free scan. Early halting is padded with
identity transitions and a retained halt flag.

This segment need not be injective as a function of the source. Its protected
XOR endpoint is self-inverse even for a dirty target. The construction never
substitutes an inverse of the scaled C function for a trace reversal. In
particular, PR3109's two scaled orientations compose to a power of two times
identity, not identity.

## 3. Recursive controller and exact accounting

Choose integer radix `b>=2` and height `H>=0`. Reserve b-1 complete
configuration slots at each of H levels. All levels share one sequential bank;
there are no new physical tapes per level. Write

    C=(2b-1)^H,  L=ceil(T/b^H),  Q=H(b-1)S.                             (2)

At an internal node, partition its time interval into b consecutive balanced
subintervals (lengths differ by at most one). Using the next recursive level:

1. Compute configurations at the first b-1 cuts into this level's zero slots.
2. XOR the last subinterval's projected endpoint into the node's target.
3. Revisit the first b-1 subintervals in reverse order, using the same
   protected calls to XOR-clear their checkpoint targets.

At level H invoke the segment construction. Empty intervals are identity
segments and are still charged. Induction over height proves the source is
preserved, the target receives exactly the requested endpoint XOR, and all
checkpoint/active/history contents return zero. In cleanup, a checkpoint's
predecessor is still present when it is needed. The one subtree that reaches
the external target uses its declared projection; every other leaf outputs a
complete configuration.

There are exactly C segment calls and `(C-1)/(2b-2)` internal calls. Maximum
segment length is L, including nondivisible T. In the finite Boolean overwrite
model, let F_H(t) count the executed forward overwrite gates. With
`t=bq+u`, `0<=u<b`, balanced children and a once-visited last child give

    F_0(t)=t,
    F_H(t)=2[(b-u)F_(H-1)(q)+u F_(H-1)(q+1)]
             - F_(H-1)(q+[u>0]).                                      (3)

Thus `F_H(T)<=CL`; reverse work is identical. This independent aggregate
recurrence checks the actual interpreter's counts without executing its state.
There are CS copied and CS uncopied configuration bits, and `(C-1)S+P`
output XOR bits for a projection of length P<=S. Entry and return zero scans
of local banks total `(C-1)S`; initial/final whole-bank charges total 2Q.
Reserved payload is `Q+S+L`. These exact counts are for the finite fixture,
not a literal transition count for the inherited fast C machine.

## 4. One bank, with all routing charged

Place the Q checkpoint bits contiguously, level by level. The active
configuration, history, external source/target and controller use a fixed
number of other tapes. Each leaf moves the bank head from its origin to the
source slot, then target slot, then source slot, then back to the bank origin.
An external port is on its own tape. This intentionally simple router travels
at most 4Q cell positions per leaf, even for nonadjacent parent/child slots.
The finite implementation records these movements, and an independent port
recurrence sums the corresponding exact distances. Entry/return zero checks
also travel to their level's slots and return to origin: at most 4Q movement
per internal node. Initial and final complete-bank scans add at most 4Q.
Since there are at most C-1 internal nodes, the total bound is 8CQ.

Each copy/projection scan returns to its slot origin; those intra-slot scans
and rewinds add O(S) per leaf. They are separate from between-origin distance.
Controller frames contain interval bounds, child index, phase and slot numbers
on an encoded stack of O(H log(T+b+H+2)) bits, which fits O(Q+S). A child frame
is computed from a preserved parent frame, child index and phase. Compute the
integer subdivision and slot addresses reversibly with local compute-copy-
uncompute arithmetic, erase its arithmetic scratch before descent, and XOR-clear
the child frame from that same parent information on return. Phase/index
updates are reversible counters with known loop endpoints; run their final
public reset back to the known entrance state. Thus controller garbage does
not accumulate over the C leaves. Schoolbook arithmetic on these logarithmic
fields and encoded-stack access cost O(Q+S) per node under the declared padding.
Their scans and returns use a fixed number of control tapes.

A loop implementation of the recursion uses that stack and a fixed tape count;
the finite Python prototype itself is not claimed to be the physical compiler.
In the two regimes below, public plan preparation takes polynomial logarithmic
work, absorbed by O(T+S) for the respective fixed parameter. Include its local
trace and reversal to restore scratch. It does not inspect coefficient
magnitudes, and no list of all C calls is precomputed or retained.

Consequently the complete generic bounds are

    time = O(C (L+S+Q)),
    clean space = O(L+S+Q).                                            (4)

They include local scans, routing, depth control, initialization and cleanup.
No random checkpoint access or unpriced reset to origin is used. For the
finite payload invoice, the explicit upper bound is

    C*(2L+4S+8Q)+2Q.                                                    (5)

Actual source-machine serialization, controller and history-record constants
belong in (4), not in the numerical constant of (5).

## 5. Two useful regimes of the same construction

Put `R=max(1,T/S)`.

**Fixed height.** Fix H and choose `b=max(2,ceil(R^(1/(H+1))))`. Then
`b<=2 R^(1/(H+1))`, `L<=S R^(1/(H+1))+1`, and
`C<=4^H R^(H/(H+1))`. Equation (4) gives

    time = O_H(T+S),
    space = O_H(S + S^(H/(H+1)) T^(1/(H+1))).                          (6)

All H-dependent recomputation constants remain constants only when H is
fixed. H=0 is the full trace; H=1 gives the two-level square-root tradeoff.
No claim that the origin-return layout optimizes finite work is made.

**Fixed radix, variable height.** Fix b and choose the least H with `b^H S>=T`;
when T<=S choose H=0. Then L<=S. Define

    alpha = log_b(2b-1)-1 > 0.

Because `C <= (2b-1) R^(1+alpha)` and `H=O_b(1+log R)`, equation (4) gives

    time = O_b((T+S) R^alpha log(2+R)),
    space = O_b(S log(2+R)).                                          (7)

The logarithm includes the deliberately paid bank routing. It is not silently
removed. Both constants depend on b. If T and S both grow proportionally with
payload N, their ratio and this depth do not acquire a log N term. This is
why (7) is stronger for this application than substituting a unit-transition
simulation bound in T without the configuration-scale base case.

## 6. Bind the complete source configuration

PR3122 (`bd06efe0c53280c585d0f3b2f21c52d036f40902`) section 4 binds the
retained exact C source to

    S_w = A Nw + F,
    T_w = B Nw d^sigma + F,  sigma=599/600,                             (8)

with fixed source-dependent constants. Its proof counts parked ancestors via
geometric packet contraction, guarded component widths, monomial rotation and
repair streams, ordinary interchange scratch, head markers and mutable
compilation. The archived proof and its cited PR2287/2250/2899 sources are
pinned here. Their physical-source/compiler contracts remain assumptions;
this package does not independently certify the entire source machine.

Increase A if necessary for the controller allowance. For fixed H, the chosen
b is at most T+2; for fixed b, H=O_b(log(T+2)). Thus the strengthened padding
in section 2 is O(log^2(T+2)) with fixed-parameter constants. With n=Theta(r),
N=2^n, w=Theta(r), `log^2(T_w+2)=O(Nw+F)`. The same holds for a narrow
k-axis routine: its time `T_n=O(Nk^2)` and configuration `S_n=O(Nk)` absorb
`O(log^2(T_n+2))`, since n=Theta(r), k>=1 and N is exponential in r.
The narrow configuration must remain isolated from retained wide caller
banks; if it reads those banks, replace S_n by its true complete configuration.

All source conversion, exact output shifts, opposite-orientation exchanges,
protected copies and restoration already lie within (8). Each new protected
oracle has the identical interface as before. PR3109's four invocations per
in-place block and nonlinear inverse clearing are therefore unchanged.
Checkpoints close after each call and are reused; histories of all calls are
never retained simultaneously.

For `B_c <= r/d+K`, a full unsimplified ledger is

    O(Nw(ell+K) + F)
      + O(B_c) * Time_b(T_w,S_w)
      + O(sum_i Time_b(T_(n,i),S_(n,i))),

    space = O(Nw+F) + Space_b(T_w,S_w)
                         + O(max_i Space_b(T_(n,i),S_(n,i))).           (9)

Here Time_b/Space_b are (7), `k_i<=d`, `sum_i k_i<=r`, and the direct tail's
history, split fields, private outputs and control are charged. Replacing those
two functions by (6) gives the unsimplified fixed-height ledger. Formula (9)
retains F; it does not assume free mutable compilation or clean-stock hosting.

## 7. Near-input-space corollary with an explicit time margin

Use the inherited constants

    epsilon=997/1000, spacing=1/500, sigma=599/600,
    d=Theta(r^epsilon), K=Theta(d^spacing), ell=Theta(r/d), w=Theta(r).

Set the fixed radix to `b=2^1200`. The strict integer inequality
`b < 2b-1 < 2b` implies `0 < alpha < 1/1200`. No floating logarithm is needed.
For fixed F, the powers below conservatively replace alpha by 1/1200. All
fast/narrow terms may also have one factor log(r+2) from (7).

| Complete charge | Power of r, excluding N | Gap below `2-997/1200000` |
| --- | --- | --- |
| Full wide groups | 1439400803/720000000 | 997/720000000 |
| Short-group allowance | 1438676483/720000000 | 725317/720000000 |
| Narrow residue blocks | 2397397/1200000 | 803/600000 |
| Deferred low axes | 1003/1000 | 1195403/1200000 |
| Incomplete-chunk axes | 500997/500000 | 5983051/6000000 |

For example, the first exponent is
`2-epsilon(1-sigma)+epsilon*sigma/1200`; the narrow exponent follows from
`sum k_i^(2+alpha) <= r d^(1+alpha)`. Every gap is strictly positive, so the
logarithmic routing/control factor is absorbed into the stated time power.
The first gap is very small, another reason this is not a practical crossover
claim. The resulting time exponent is `2399003/1200000`, strictly below two.

Wide space in (7) is O((Nr+F) log(r+2)); narrow space is
O(Nd log(d+2)), which fits it. Caller banks and direct tails use O(Nr).
This proves (1). The input already contains Theta(Nr) bits, so the clean
space is within a logarithmic factor of input size. No optimality is asserted.

For (6), fixed H gives wide space exponent
`1+epsilon*sigma/(H+1)` and narrow exponent
`epsilon*(1+1/(H+1))`. Their difference is
`1-epsilon-epsilon*(1-sigma)/(H+1)>0`; the wide term dominates. Time remains
`1199003/600000` for each fixed H. One must not let H grow and keep its hidden
constants fixed; (7) is the separately charged variable-height conclusion.

## 8. Evidence and remaining obligations

The finite controller deliberately executes information-losing Boolean
writes. Its saved history, source return and dirty-target XOR are checked
against a separately spelled evaluator, and exact costs against (3) and the
port-distance recurrence. It also executes the frozen closed-coefficient
Gaussian circuit from PR3122 and feeds the new controller into PR3109's
unchanged four-call nonlinear macro. Both scaled orientations and literal
inverse pairs are checked. A unit-step-depth control exhibits the unwanted
payload-dependent depth, while the relative plan keeps height fixed under
common scaling of T and S.

The executable is a finite semantic and invoice prototype. It does not execute
the fast physical C machine, materialize the enormous radix, measure its
asymptotic runtime, or establish its inherited compiler premises. O(Nr log r)
work is **clean** work, not arbitrary dirty helpers. Native wrappers, complete
collector/consumer costs, physical clean-stock production, source review and
supplier admission remain separate. No selected frontier or kappa changes.

Credit Bennett, *Logical Reversibility of Computation* (1973),
DOI 10.1147/rd.176.0525, and *Time/Space Trade-Offs for Reversible Computation*
(1989), DOI 10.1137/0218053, for the general mechanisms. Credit Jose Manuel's
PR3109/2287/2250/2899, the PR3122 source-space binding and finite circuit,
Ross Richardson's PR3072 protected evaluation pattern, PR3033/3025, and the
full retained source lineage. Exact source pins and archive notices are retained.
