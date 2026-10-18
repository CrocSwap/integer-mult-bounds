# A common-cut count envelope for native ADD

This is a written lifetime proof for Jose Manuel/jmbarrancoml's unchanged
PR2697 source at `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. It joins the
extent-preparation result of [PR2912](https://github.com/CrocSwap/integer-mult-bounds/pull/2912),
head `5ff0dc6019f1a7b1440ae51b5c2bf757e9698b5e`, and the countdown result of
[PR2905](https://github.com/CrocSwap/integer-mult-bounds/pull/2905), head
`119f74dfe6ff97d8d692a32ed02d6597220dd479`. Those component results retain
their credit. The new statement composes their actual lifetimes through
`stream_runner.action`, rather than asserting that separate maxima coincide.

## Metric and hypotheses

Sum `len(tape.cells)` over distinct strongly reachable count-construction
tapes. Include Natural/Count tapes, Counter tapes, the standalone raw Tape
in `Count.literal`, LEFT, RIGHT, erased tails and pending constructor results.
Count aliases once. Clearing preserves backing. Unreachable arrays awaiting
host reclamation and Python object overhead are outside this source metric.

The action is ADD and receives the two-bank `vendor/layout.py:Layout`.
The older class also named Layout in `stream_runner.py` is not the contract.
Assume a successful sequential complete-fibre execution with canonical
positive borrowed spectator counts, valid ordered physical endpoints and
`M=q^w>1`. Borrowed counts may have erased tails after their canonical RIGHT.
The residue arena has exactly `b=bit_length(M)+1` binary digits per Word.
Each index Word has I binary digits, including any high zero padding.
Both coefficient callbacks return the same canonical coefficient and preserve
the native configuration.

Let K count all entry count tapes, including any preexisting callback state.
Their backing is unchanged throughout. A callback may allocate at most H
additional count-tape cells simultaneously, including its construction
temporaries. All that private backing becomes unreachable before callback
return. No observer, factory or callback captures native owners, tapes,
arrays or execution frames. Releasing an owner while retaining its Tape or
bytearray does not meet this premise. Other mutable callback state needs a
separate ledger.

Numerical Word arenas and templates, payload arrays, records, programs,
continuations and physical allocation/movement are excluded. H is an
explicit allowance for the stated category, not a proved bound for every
selected coefficient evaluator.

## Components with one shared meaning

Let U,G,S be the three returned extent values, in order. They are the
complete physical before, intervening and suffix counts used by ADD,
including the appropriate external gap and powers of M. Set

```text
L = (bit_length(U), bit_length(G), bit_length(S))
T = sum_i (L_i+2)                  canonical originals
W = max_i L_i
R = sum_i (L_i+3)                  returned one-margin extents
E = T + max(I+2, 3W+9)             preparation upper bound

p = L_1+3, m = L_2+3, s = L_3+3
r = b+2 = bit_length(M)+3

C = p+r+m+max(m,r)                when S=1
C = p+r+m+max(m,r+2s)             when S>1
```

PR2912 proves E above K during the complete extent preparation and exact
returned backing R. Briefly, original counts grow monotonically toward
their final widths; one exponent Counter needs I+2 cells. Exactly one gap
product runs for ordered physical positions. Keeping its old multiplicand
and all product scratch requires at most an extra 3W+9. Original and
marginal tapes coexist during marginalization, also within that allowance.
The raw literal Tape is included. The returned marginals are the only
private count tapes surviving the preparation frame.

PR2905 proves exact native Counter maximum C for fixed marginal extents.
The active outer, source and middle Counters occupy p+r+m. A replacing
middle constructor overlaps its closed predecessor, adding m. Inside a
copy, its block Counter adds r, and S>1 creates suffix Counters whose old
and pending bindings overlap, adding 2s. M>=2 guarantees a reached leading
copy with at least two blocks. Thus the maximum is attained, including
zero coefficients. This counts retained erased backing, not live digits.

Neither statement includes the other's residents: E excludes entry tapes,
while C excludes the borrowed marginal tapes. In this composition those
marginals are private to the action and must be added as R.

## The joined statement and proof

For the stated source and hypotheses, total count backing is at most

```text
K + max(E, R + max(C,H)).
```

1. `action` calls `layout.extents` before entering its try/finally body.
   Before that call returns, E bounds all new count tapes. No coefficient
   callback or traversal has started.
2. After return, exactly the three marginals remain, with backing R.
   The ADD call borrows them throughout both traversals. It does not grow
   their backing. Each callback runs at the start of its traversal, before
   any traversal Counter exists. Callback-private backing adds at most H.
3. After each callback returns, its private count backing is unreachable.
   During that traversal only native Counters add to R, with maximum C.
   The first traversal frame returns before the second callback starts.
   Its closed local bindings therefore cannot accumulate into the second
   traversal. Native arithmetic allocates numerical Words, a separate
   category, and no additional Natural/Count tapes.
4. `action` finally clears the three marginals. This grows no array; R
   remains charged until the action frame exits. The entry baseline K is
   unchanged in all phases. Taking the maximum over these sequential
   phases proves the claim.

The post-preparation native phase attains R+C. If a compliant callback
attains H, its callback phase attains R+H. E is a conservative preparation
bound, so the displayed total upper bound is not universally sharp. If
the actual preparation maximum is e, the exact private maximum for such
a callback is `max(e,R+C,R+H)`.

## Successful distinguishing examples

With M=3,n=1, all borrowed spectators one, adjacent physical positions,
I=8 and no callback count scratch, E=21, R=12 and C=18. Preparation peaks
at 21, and the native phase peaks at 30. Using only preparation, or
`max(E,C)`, misses a reached 30-cell cut. Adding the independent peaks
E+C gives 39 although they do not coexist.

A callback constructing a B-bit Count followed by its Counter needs
exactly `H=2(B+2)` cells. The raw literal/result overlap and Count/Counter
overlap have that same maximum. For B=32 with normal release, the action
peaks at R+H=80, rather than E+C+H=107 at I=8.

For the same B=32, instead retain both cleared Tape objects after each
callback. Both coefficient values and the ADD permutation remain correct.
At I=12 the proposed released-callback bound is 80, but the actual action
peaks at `R+2H+C=166`. Direct Tape capture suffices; capturing an owner or
native frame is unnecessary. This refutes phase separation when release
is replaced by clearing.

At I=256 with no callback scratch the same returned marginals still have
R=12, but preparation reaches 267. A runtime-only `R+max(C,H)` budget
therefore also misses a reached cut. The numerical arena storing the
padded index is not counted here.

## Evidence and remaining boundary

The checker authenticates each executable input by SHA256 and Git blob,
then executes the unchanged source definitions. A weak-reference observer
samples every count Tape creation and write, including pending constructor
and final-clear cuts. It does not retain source objects. All count growth
occurs through the observed write method. Private strong-reference lifetimes
are acyclic in these fixtures; no garbage-collection timing is assumed.

Seventy successful fixtures cover both suffix branches, all coefficients
modulo three, callbacks above and below native cost, all three physical
gap branches, nonunit spectators, index padding, aliased entry counts,
M=5 and M=9, and all nine origin basis planes of a complete M=3 fibre.
Every execution checks an independent integer-address ADD permutation,
borrowed input restoration, numerical live-slot return and private release.
The escaped-callback execution is an additional successful counterexample.

Finite replay corroborates the written composition; it does not prove all
source contracts. No complete selected GL64 payload, arbitrary exception
cleanup, total private A, physical tape reuse, recursive/outer reserve,
supplier admission, new kappa or formal-kernel proof is claimed.
