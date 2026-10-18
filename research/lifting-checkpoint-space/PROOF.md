# Checkpoint space for the batched lifting core

Tekalign, with substantial OpenAI Codex assistance. Apache-2.0.
Ordinary written conditional proof; no formal-kernel or independent human review.

## 1. Source and endpoint

Keep Jose Manuel's PR #3109 (`15eac811648182bdac7254a91fd9b841b1414ebc`)
nonlinear order, scalar periods, complete batches, exact scaled-linear routines,
and four-call in-place evaluator unchanged. We alter only how an irreversible
routine becomes a protected XOR oracle. The endpoint is

```
(x, y, 0_work) -> (x, y XOR Enc(f(x)), 0_work),
```

where y is arbitrary. We do not invert f. In particular, the two scaled ideal
orientations in PR #3109 compose to 2^(2g)I, not I. Each direction gets its own
protected evaluator. Recomputing the same endpoint XOR clears a private target.
The predecessor's literal inverse of the *nonlinear* block still clears its old
bank. Thus its error bounds and all semantic contracts remain identical.

The generic checkpoint technique is classical: C. H. Bennett, *Time/Space
Trade-Offs for Reversible Computation*, SIAM J. Comput. 18(4), 766–776 (1989),
DOI [10.1137/0218053](https://doi.org/10.1137/0218053). The segment routine uses
his 1973 compute-copy-reverse construction (DOI 10.1147/rd.176.0525).
No novelty of checkpointing or a general reversible-simulation theorem is claimed.
The result here is the explicit source-space binding, sequential layout, and
complete time/space consequence for this particular lifting core.

## 2. A complete checkpoint lemma

Fix a deterministic machine on a fixed number of tapes with a finite alphabet.
Suppose its execution, including setup, normalization and output extraction,
takes at most T transitions and uses a complete mutable configuration of at
most S bits, where S includes the tape contents, finite control, head markers,
call state and O(log(T+2)) control bits. T and S are uniform bounds fixed before
reading values. An immutable transition table is shared, not copied into each
configuration. Any mutable compiled data belongs in S.

We require disjoint complete configuration ports and owned clean checkpoint,
active-configuration and history regions. Arbitrary dirt in y is allowed;
arbitrary dirt in those work regions is not. The supplied output is a full
configuration or a declared subsequence obtainable in one sequential scan.
A general random permutation of its bits does not get a free O(S) projection.
The finite implementation rejects unordered projections.

Set

```
k = max(1, ceil(sqrt(T/S))),
L = ceil(T/k).
```

Partition the T steps into k contiguous segments of length at most L. T=0 uses
one empty segment. For a uniform upper time bound, halting earlier can be padded
with identity transitions, with a finite halt flag. Segmentation is independent
of the actual branch history. A resumable checkpoint includes the full state,
not just an output array or the visible data bits.

Let Phi_i be the function advancing a configuration through segment i. A
protected segment oracle computes Phi_i into active work, recording a constant
number of old state/symbol bits per machine transition. It XORs the completed
configuration into the target, then reverses the recorded trace and XOR-uncopies
the active configuration from its preserved source. The history cells and active
work return to zero. Its time is O(L_i+S) and clean space O(L_i+S).

These bounds include sequential configuration copy/serialization, moving every
head to its encoded position and returning it after the trace, the clock and
output scan. No head address is logged per transition: the fixed transition's
finite direction/state data suffice to reverse its head moves. Binary countdown
work can be amortized over a segment; alternatively use a unary step/history
marker of length L. Both fit the stated history and time allowance.

Store k−1 intermediate configurations c_1,…,c_(k−1) in clean S-bit slots.
With c_0=x, execute

```
for i=1,...,k-1:  c_i XOR=Phi_i(c_(i-1))
y XOR=output(Phi_k(c_(k-1)))
for i=k-1,...,1:  c_i XOR=Phi_i(c_(i-1)).
```

For k=1 the middle call uses x directly. Forward induction gives c_i equal to
the original machine's state at that cut. Backward induction clears c_i while
its predecessor c_(i−1) is still present. Therefore the complete endpoint is
the required dirty-target XOR, x is unchanged, and every owned cell returns
zero. No injectivity of Phi_i is required. A function inverse or a clear/reset
of an unknown history is not used.

There are 2k−1 protected segment calls. Each original transition except those
in the last segment is simulated twice before each simulation's trace reversal;
the total underlying forward transitions are 2T−L_last, and the same number of
reverse transitions. Total copy, output, checkpoint setup/zero checks and control
work is O(kS). A single history region of length O(L) is reused across calls.
Thus

```
T_checkpoint = O(T+kS) = O(T+S),
S_checkpoint = O(kS+L) = O(S+sqrt(S T)).                 (1)
```

The elementary inequalities kS≤S+sqrt(ST) and L≤sqrt(ST)+1 prove the second
bound. Also sqrt(ST)≤(S+T)/2. These include non-square ratios, T<S and a short
last segment. They are not estimates based on finite replay timings.

## 3. Sequential checkpoint layout, not random access

Keep the checkpoint slots in increasing cut order on a single separate tape;
use a fixed set of other tapes for active execution, history and the external
source/target ports. The number of tapes is independent of k, T and r.

For the i-th forward segment, the input checkpoint is slot i−1 and its target
is the adjacent slot i. Copy the source into active work before moving to the
target. After the endpoint XOR, move back to that source before the final
source uncopy. Before the next call, advance by one slot. The last segment's
target is the external port. Visit the intermediate slots in reverse order for
cleanup. The external source is on its own tape, so it does not require crossing
the checkpoint bank. All slot boundaries and control markers are paid.

For zero-based intermediate slots, the controller's **between-slot-origin**
motion is exactly `6 max(0,k−2) S` cell positions in its declared layout.
The head finishes at the bank origin. Each intra-slot copy/XOR scan returns
to that slot's origin before the next between-slot move; those scans and
local rewinds cost an additional O(kS). Per-segment serialization/head
positioning on the active configuration tapes is also O(S), already in the
lemma. In particular, mark each execution head's current cell on a temporary
track before serializing; scan to the region origin and back to the marker
before reversing the trace, then erase the marker. The fixed number of heads
adds O(S) time and space. Counter setup and storage fit O(kS) because S
includes the control width.

Returning to the bank origin after every segment instead would add Theta(k²S)
movement. The finite adverse-layout control executes that alternative and records
its larger bill. We do not make that reset in the construction. Ancestor state is
on disjoint ports and is not scanned once per simulated transition.

The prototype counts exact Boolean trace/copy/checkpoint payload operations and
bank distances. Its `18*T+15*S` bound is an envelope for that logical invoice,
not a literal transition bound for an unmaterialized source machine. Source-machine
serialization constants and constant-size history records belong in (1).
Python indexing is not offered as a physical tape implementation.

## 4. Complete configuration size of the retained exact C routine

This is the load-bearing source binding. A T-step black box alone gives no
small S; assuming S=T would erase the improvement. We retain the mathematical
and physical-source premises of PR #2287, rather than claim to have independently
proved its whole compiler.

In `research/selected-complex-layer-closure/PROOF.md`:

- Section 1 defines the complete stream volume V with O(p) bits per component.
  Section 6's grid guard has width p+2Delta+3, Delta=ceil(2^210000 d), d≤p.
  Thus the guarded width is O(p), with its very large fixed constant retained.
- Sections 3–5 use existing address coordinates for row/compact fields; the
  initial whole-row padding increases volume by less than two. A recursive
  boundary keeps W original families and at most 720 packet/control slots,
  each packet having volume v=V/(W Gamma), W=14336 and Gamma>2^2627.
- A complex child receives one complete packet. Parent streams are parked;
  local monomial/scalar/selection scratch closes before that child, and
  sequential calls reuse work. Even allowing a conservative factor two for
  padding, active descendant volume contracts by at most 2/(W Gamma)<1/2.
  The sum of parked ancestor payloads is therefore bounded by a geometric
  series, not V times the recursion depth.
- Leaf C kernels and coefficient scans need O(V) work. Monomial scratch
  between child boundaries must also be counted. PR #2250's
  `research/selected-complex-compact-adapters/PROOF.md` sections 1, 3 and 4
  retain a fixed number of rotation pieces, good/bad streams, holes and
  radix buckets. With M records of R bits and A=O(p)-bit keys, their peak
  volume is O(M(R+A)+poly(p))=O(V), since R dominates every fixed power
  of p. Radix passes reuse their buckets; they do not retain A copies.
  The fixed monomial word composes these operations sequentially.
  Its ordinary interchange calls have O_q(V)+F_q space, explicitly stated
  in PR #2899's `research/physical-ordinary-interchange/PROOF.md`; q is fixed.
  Their work is empty before the next complex child. Descriptors,
  stack/head markers and the fixed polynomial in p fit the declared
  exponentially long records, including at the deepest admitted packet.

These source contracts yield a complete mutable-configuration envelope

```
S_w ≤ A N w + F,
T_w ≤ B N w d^sigma + F,   sigma=599/600,                 (2)
```

for fixed source-dependent constants A,B and its fixed compilation allowance F.
All spectators and coefficient fields are included in N. Normalization, exact
rescaling and real/imaginary exchange from PR #3109 section 3 add O(Nw) time and
space, already inside (2). The protected source and outer lifting banks remain
on disjoint caller ports; no internal partial computation reads them.

If compilation is immutable it is shared once and may be omitted from S_w.
If it contains mutable cells, retain F in (2) and in the unsimplified formulas
below. F is never silently treated as zero or as arbitrary dirty storage.
We make no statement uniform in a changing compiler/prime with unbounded F.

For a narrow k-axis residue block, isolate its complete O(Nk)-bit input/work
region from the caller's retained wide arrays. PR #3109's sequential direct pair
routine has T_n=O(Nk²) and S_n=O(Nk). Its public axes/countdown state fits this
volume. Applying (1) to it gives O(Nk²) time and O(Nk^(3/2)+Nk) clean space.
It does not copy the full wide caller into every narrow checkpoint. If an
implementation accesses that caller during the narrow routine, this smaller
configuration bound must be replaced and the conclusion re-priced.

## 5. Complete core recurrence and exponent

Retain PR #3109's parameters epsilon=997/1000, spacing=1/500,
d=Theta(r^epsilon), K=Theta(d^spacing), ell=Theta(r/d), w=Theta(r),
N=2^n, n=Theta(r). There are at most B_c=r/d+K full/short batch calls,
block ranks k_i≤d with sum k_i≤r, and fewer than ell+K direct axes.

Each wide protected XOR call now costs O(T_w+S_w); all four calls per in-place
block, both orientations, their trace reversals and output cleanup are retained.
Narrow calls cost O(Nk_i²) each. Calls reuse checkpoints and history after zero
return. The source-preserving split, quotient/residue copies, recombination,
old-bank clearing, direct tail and parameter scans are unchanged and charged.
A sufficient complete time bound, with mutable F conservatively left visible, is

```
O(Nw(r/d+K)d^sigma + N r d + Nw(ell+K)
  + (r/d+K+1) F).                                      (3)
```

One-time compilation is included. The extra F repetitions are conservative
configuration charges; with a read-only compiled table its shared cost is just
F. For fixed F they are absorbed by the same N-dependent asymptotic bound.
The time exponent remains exactly **1199003/600000 = 2−997/600000**.

A complete additional clean-space bound is

```
O(Nw + F + sqrt((Nw+F)(Nw d^sigma+F)) + N d^(3/2)).      (4)
```

The Nw term includes source preparation, retained wide/narrow/sum banks,
configuration-port construction and output delivery. Only one backend trace
is active at a time; its checkpoints are not duplicated across all B_c calls.
The direct tail's O(Nw) history fits (4). Parameter/header space is also included.

For the fixed inherited machine, substitute w=Theta(r):

| Space component | Power of r, excluding N |
|---|---:|
| Wide checkpoints/history | 1+epsilon sigma/2 = 1797203/1200000 |
| Narrow checkpoints/history | 3 epsilon/2 = 2991/2000 |
| Retained data and direct axes | 1 |

The wide power exceeds the narrow power by 2603/1200000 and dominates.
The predecessor's wide-history power is 1197203/600000. Hence the new clean-work
bound is **O(N r^(1797203/1200000))**, versus its
O(N r^(1197203/600000)), with no loss in its stated time exponent. The exponent
reduction is 597203/1200000, approximately 0.497669. Formula (4), not a bare +F
suffix, is the parameter-uniform claim when mutable F is kept variable.

This is a conditional asymptotic space improvement. It is not a measured speedup,
a full selected supplier, physical stock admission or a new multiplication κ.
The history changes no axes, native labels, numerical map or consumer interface.
External wrappers and the actual collector under another contributor's active
scope remain outside this package.

## 6. Finite evidence and limits

`checkpoint.py` executes irreversible Boolean overwrites with one logged old bit
per gate, exact endpoint XOR, reversed logs, source uncopy and sequential checkpoint
addresses. `gaussian.py` emits a direct integer scaled-C Boolean program, including
negative inputs, modular carry arithmetic, both orientations and nonconsecutive
axes. Its gate list is immutable input recipe data shared by both comparisons;
the reported payload-space counts exclude it and are not Python process memory.
The theoretical source C machine has fixed compiled control, not this generated
dense program. No fast tariff is assigned to these fixture circuits.

The Boolean compiler uses a closed coefficient formula independently of the
predecessor's pair-by-pair linear evaluator. For input/output active-index
difference delta, the scaled coefficient is
`2^g ((1+i)/2)^k (-i)^wt(delta)`. At k=2j its common factor is `2 i^j`;
at k=2j+1 it is `(1+i)i^j`. Conjugate these coefficients for the opposite
orientation. Modular signed carry arithmetic realizes the resulting integer
sums; the predecessor's separate headroom check excludes fixture overflow.

For every Gaussian call, the verifier executes both the original whole-trace
schedule and the checkpoint schedule on the same program, source and dirty
target. It measures their peak logical history and checks identical outputs
and clean returns. The reported payload bits exclude Python objects, program
storage and the controller's host-language state; they are not a measurement
of the complete physical configuration S in (1).

The verifier installs that Boolean backend in PR #3109's authenticated
`inplace_block` interface and runs its existing private-cleanup checks. It separately
checks exhaustive small input/dirty-target states, exact integer plan inequalities,
all tail boundaries in the declared finite domain and the rational exponents.
Controls reject missing cleanup, broken trace reversal, unordered projection,
aliasing, headroom/source drift and corrupt receipts. A more expensive bank-reset
schedule demonstrates the physical cost that the sequential construction avoids.
These finite checks corroborate the proof; they do not prove an all-size source
compiler, instantiate its enormous cover or benchmark its runtime.
