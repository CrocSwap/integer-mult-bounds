# One paid exit funds the chart-1031 split

The source is [#7156 at b44944c3058d522cbff17836e16240d40d77a927](https://github.com/CrocSwap/integer-mult-bounds/tree/b44944c3058d522cbff17836e16240d40d77a927/research/p104-temporal-chart306-continuation).
Its normalized native word returns every helper coordinate and leaves all
other outputs independent of those helper inputs. The candidate retains
the signed 17-stage [#7113 caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
at `07a76c5e2738882c0cb322278e56f6cae3c9885d`.

## Literal exit extension and temporal access

Role 133 starts at frame 3 and returns at frame 591 of rank eight. Append one
public MOVE from frame 591 to frame 127, whose span strictly contains it.
The unchanged scalar endpoint for role 133 now belongs to the arbitrary
helper group with boundary frames 3 and 127. The new MOVE has rank one and
is charged. Both the prefix and suffix vectors use role 133, so omitting
the extension makes the unchanged-boundary constructor reject the witness.

At chart 1031 of rank five and original cut 42,379, pivot 1,336 is resident.
[WITNESS.json](WITNESS.json) binds twelve gathers and five injections to
the exact original cuts. Roles 1,362 and 1,386 are literal stationary
gathers at cut zero, with windows `[0,35561]` and `[0,35607]`. The other
fifteen observations use the contact-free retimings in
[PATHS.json](PATHS.json). The retiming preserves all original paid MOVE
ranks. Every read and write stays in one literal frame.

Let P(t,r) be the complete normalized scalar prefix row at cut t, and let
S(t,r) be the suffix perturbation response in all final public and owned
coordinates and all COPY destination-zero guards. A guard for an injection
at cut t includes a COPY performed at event t. The two weighted sums give
the vectors c and d in the witness, with zero in every outside coordinate.
Their support intersection is roles 133, 445, 1,242 and 1,336. Its dot
product is `6 - 2 - 5 + 2 = 1`. The retained exact certificate recomputes
both vectors. Separate controls reject an omitted exit, a wrong exit
frame, a false stationary frame, a MOVE inside the claimed stationary
interval and an observation after CLEAR.

## Arbitrary-input split

The retained causal construction builds a scalar basis G with pivot row
c and `G d = e_pivot`. It applies G inverse at the input frame and G at
the final frame, where the paid extension has already arrived. Both
directions are emitted with the literal scalar coefficients. On original
group input u, the internal input is `G^-1 u` and the gathers put the
original pivot input x in an owned buffer A.

At retirement let v be the current pivot continuation and z the independent
new public input at chart 1031. The literal middle operation leaves x in
the retiring pivot, v in its new continuation and z−x in a second owned
buffer B. The scheduled suffix injections add `d(z−x)` without changing
any other output or COPY guard. After the exit basis the continuing pivot
returns z, since `G(G^-1 u+d(z−x)) = u+e_pivot(z−x)`. The two owned
lifetimes retire explicitly. This is an arbitrary-input identity,
including when v differs from x.

The common-frame scalar operators act on the normalized complete arrays
at every positive column multiplicity. A MOVE is the exact nested-frame
quotient with its absolute phase, and its tensor lift is one charged child
with two whole-job adapters. The separate native and complete caller
replays check the affected maps, phase, ownership, and exact grids.
The signed caller's 17 stages use the same distinct physical owner and
central-phase bindings as the selected application framework.

## Complete price change

The extended helper changes one rank-eight target to rank nine and adds
one paid rank-one child. The causal split then replaces one rank-nine
target with ranks five and four. Thus the net per-native change is
`T4 +1, T5 +1, T8 -1, P1 +1`. All seventeen occurrences are charged.
Rank surplus stays 1,424. For `p=1-C` in `(0,1)`, strict concavity gives
`4^p + 5^p - 8^p - 1 > 0`. The complete directed engines certify the
funded price `C=0.00364489006794007` and conditional
`κ=0.003644890067940`, an exact gain of `482172401/10^15` over #7156.
The original complete invoice has a strictly negative moment at the new
claim. The fixed BIT premise is 0.00376669.

For a fixed-profile ceiling, hold this exact target invoice and the
seventeen native profiles fixed. The remaining paid rank mass is 109,088.
The most favorable fractional remainder under the ambient cap 145 puts
all that mass at rank 145, because `r^(-C)` decreases in r for positive C.
The early receipt certifies a decreasing relaxed crossing on `[0,1/32]`
and records the rational ceiling bracket and fraction realized. This
relaxation has different hypotheses from the nine-stage equal-target cap.
It bounds the fixed profiles and rank mass stated here.

The common exact-grid, finite stock, movement, compiler and outer
application follows the [selected #7000/#7001 review](../../docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)
and the [exact #7156 application review in #7158](https://github.com/CrocSwap/integer-mult-bounds/pull/7158).
Use the regenerated full ordinary and physical bills, common-grid bounds,
precision context and complete outer receipt for this candidate. The
five inherited assumptions remain native_all_columns, owned_erasure,
compiler, precision_tape and analytic_recovery.
