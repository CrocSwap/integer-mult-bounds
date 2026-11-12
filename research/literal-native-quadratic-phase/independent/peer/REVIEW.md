# Independent review of the literal selected native quadratic phase

**Disposition: accept the scoped component theorem. No new kappa or removal
of a complete selected foundational assumption.** This is an independent
AI-assisted review for Jerry Chen / @CubeJerry, not human or proof-kernel
verification. The author program was not edited. The source-specific local
phase, supplied packed ABI, successful-call lifecycle, and displayed complete
cost bounds are consistent with the frozen graph.

## Exact objects and reproduction

Canonical base: `e54523517d0f03e58352e647c403a5af3e525a57`.
Package: `research/literal-native-quadratic-phase` in the B3 worktree.

| Object | SHA256 |
|---|---|
| `phase.py` | `2be149aa1be504509bb480f85396f0be302082d638e81422f747daee5a3c1ce7` |
| `PROOF.md` reviewed revision | `55f0a575f618bf467d0e25a25802053455d701cee1f23fb8811a671a1bd59ff3` |
| Canonical generated graph JSON | `e10a0070af3331d23963fb97ebcd4bb7e81314d94a43d41ce00d4c84c5747638` |
| Retained C2 helper source | `9a360817b80e869398927f38a4f110de0b5a1f9620eeb23b19e166f112b83f23` |

The author made two proof-only precision edits before this final receipt:
external simulation budgets do not belong to the program, and counter heads
align at carry-bit reads after the intervening sequential moves finish.
These clarifications are correct. They do not change the graph or theorem.

Run this independently written interpreter with an absolute or relative
path to the reviewed package:

```sh
python -I -W error -B check.py /path/to/research/literal-native-quadratic-phase
python -I -O -W error -B check.py /path/to/research/literal-native-quadratic-phase
```

Both executions must emit the same JSON receipt, headed by
`PASS_B3_INDEPENDENT_STRUCTURE`. The checker imports only the graph builder;
it does not call the author's `Machine`, `Tape`, numerical oracle or
verification program. Its own tape objects record every local instruction,
head motion, visited extent, and write. It checks the complete instruction
graph for fixed tape numbers, alphabet, destinations and unit moves.

## Source phase and universal invariant

The source selection is the actual retained native event 24472,
`["MOVE",415,3,99,false]`, with frames 3 and 99. The retained source binding
and complete monomial decomposition are distinct from this review's local
ABI theorem. This package implements only the right factor's diagonal
action before its affine map; it does not implement the whole event.

The right recipe has `q0=1`, linear entries 3 on
`J={0,1,2,3,5,6}`, entry 2 at coordinate 7, and the complete quadratic graph
on J. Its diagonal entries are already included in the linear term. For
`h=sum_{i in J} x_i`, the phase contribution is

`1 + 3h + 2*binom(h,2) + 2*x7 = 1 + h*h + 2h + 2*x7 mod 4`.

The middle two terms are 0 for even h and 3 for odd h. Thus the alternative
source formula `1 - parity_J(x) + 2*x7` is correct. For f tensor columns
the constant is **f*q0**, and not a single q0. The graph increments its
constant control state once for every unary COLUMNS cell, so initialization
has exactly this phase.

For the independent execution checks I use the full integer quadratic form

`f*q0 + sum_i alpha_i*popcount(a_i) + 2*sum_{i<j,Qij=1} popcount(a_i & a_j)`

modulo 4. This is a separate expression from root's selected XOR/popcount
oracle and from the author's incremental update. It is evaluated at every
record entry while independently deriving the mixed-radix address from the
record ordinal. The oracle also verifies the outer and spectator positions,
coefficient reset, and exact DATA offset. Zero payloads deliberately remove
numerical values from this structural check; root supplies the independent
nonzero Gaussian tests.

Universally, flipping bit x of coordinate i changes the linear phase by
`(1-2x)*alpha_i`; a cross term changes by
`2*(1-2x)*x_j = 2*x_j mod 4`. The graph reads exactly the fixed neighbors
at their common column before changing its own bit. All active counter
heads then move once before another carry-bit read. Returning all of them
to their own guards preserves the relative column geometry. A full field
wrap propagates the carry to the preceding coordinate. A full m-field wrap
returns all counters to zero with phase f*q0, by the same bit-flip invariant.
The absence of an explicit phase reset is therefore correct.

This reasoning proves the phase invariant for every positive f and arbitrary
joint arrays; it does not extrapolate that quantifier from finite tests.

## Exact independently derived movement census

Write `b=2^f` and `Q=b^m`. In one complete address cycle, coordinate i,
indexed from 0 at the slow end, receives `b^(i+1)` nonempty carry segments.
It flips `(2b-2)*b^i` bits. Hence

`F = sum_i (2b-2)*b^i = 2Q-2`

and the total number of segments is

`C = sum_{j=1}^m b^j = b*(Q-1)/(b-1) < 2Q`.

Every flip moves every active counter head forward once. A segment with t
flips rewinds each active head by t+2 unit moves: t back across the body,
one onto its guard, and one back to the origin. Thus each active counter
has exactly `2F+2C` ripple/return moves in a complete cycle. Initialization,
final body clearing and guards add exactly `4f+8`. For P repetitions the
full accepted-call census is therefore

**`4f + 8 + P*(2F+2C)` moves on every active counter**.

Every unused fixed counter has exactly four guard-install/removal moves.
The checker verifies these identities, the separate per-coordinate flip
counts, and synchronization at each bit replacement. These are exact
checks, not measurements fitted to an asymptotic curve.

There is also a direct instruction bound. A flip at coordinate i costs
`m+n_i+4 <= 2m+3` instructions, where n_i is its fixed number of neighbors.
A nonwrapping segment's return costs `m*(3t+3)+1`. A wrapping segment's
blank checks, return and carry cost at most `3mt+4m+3`. Consequently all
segments cost at most

`(5m+3)*F + (4m+3)*C < (18m+12)*Q`

per full outer cycle. This is well below the proof's deliberately loose
`128*(m+1)^2*P*Q` allowance. In particular, no full f-cell scan is charged
per ordinary address.

## Headers, arithmetic, complete cost and history

An AST comparison confirms identity of all nine retained C2 helper
functions: fresh labels, clearing, unary copying, header stepping, Gamma
decoding, trace return, component load, signed negate, and component stage.
Only the fixed global tape numbers differ. Their current loops were also
inspected in this graph. The previous independent C2 review's direct loop
counts remain applicable: a unary prefix update costs at most `47v+35`
before its bounded wrapper, and the sum of previous binary prefixes is less
than the final positive integer. Thus the five header decodes cost linear
time in `E+f+r+P+S+w`. Unary expansion is paid.

The complete two-component load/possible negations/stage cost is at most
`62w+32 <= 94w` for w>=1, below the proof's 256w allowance. The signed
minimum rejection test remains correct even at w=1: both old and new sign
bits equal 1 only when modular negation tries to represent the forbidden
positive endpoint. Required rotations negate exactly the components listed
in the proof. No DATA write precedes successful processing of all fields
and the exact final blank check. The subsequent commit targets the same
DATA tape and exact cells that were read.

Coefficient and spectator loops are linear in N, and the two returns plus
commit cost `24V+13` under the retained helper convention. The explicit
guard, initialization, parameter cleanup, header, odometer and Gaussian
allowances sum far below

`65536*(E+(m+1)f+r+P+S+w+(m+1)^2*P*Q+V+1)`.

Because f>=1 and m is fixed, the advertised O(V) absorption on the supplied
packed ABI is valid. This does not pay for obtaining that ABI from a
native compiler invocation.

Storage is bounded by active extents: OUTPUT and DTRACE use V each; HTRACE
and LENGTH use at most E each; DOUBLE uses at most the largest parameter;
the five unary parameters use their lengths; real/imaginary buffers use w
each; and the m counters use f each. Each role has a fixed guard and end
probe. These extents fit the stated additional bound

`2V+4E+(m+4)f+4(r+P+S)+8w+256`.

This bound counts new backed cells, not currently nonblank cells. The
review's surfaces retain their historical extents after erasure. The three
selected-graph calls on the same physical objects grow private historical
extent `105 -> 49264 -> 49264 -> 55410`. The shorter middle call uses exactly
the same number of instructions as a fresh call. All origins, opaque
exterior values, guards and retired private bodies are checked. As the
theorem states, rejection does not provide cleanup or later-call reuse.

## Executed evidence and mutation detection

The receipt contains 11 successful complete executions totaling **9,362
record entries and 6,786,145 local transitions**. The selected m=9 graph has
complete f=1 runs with differing r/P/S/width, including the reuse chain.
Separate fixed recipes with m=1,2,3,4 exercise complete f=2,3,9 domains and
nonzero constants, interactions and field carries. These smaller fixed
graphs test the builder family; they are not advertised as complete
selected m=9,f>1 enumeration. Root's separate checks cover selected higher-f
prefixes and explicitly delimit that coverage.

For every success the checker verifies HEADER has exactly E reads and 2E
moves; DATA has exactly V+1 reads, V writes and 4V moves; all fields and
repetitions have been consumed; public zero payload and exterior cells are
unchanged; private bodies and guards are erased; and all 23 heads return.
Extra and missing final DATA cells are separate rejection controls, each
with zero public writes.

Three independent source mutations are rejected:

1. Removing the tensor constant update violates the absolute phase oracle.
2. Advancing only the active counter head violates common-column geometry.
3. Scanning to full counter width before every ordinary rewind preserves
   all functional checks but fails the exact carry/return movement census.

For the third mutant the checker first runs with only that census disabled
and requires complete functional success. It then requires the movement
diagnostic. This demonstrates a genuinely cost-sensitive negative control.

## Retained limits

Acceptance is limited to the stated diagonal component and supplied local
geometry. Source binding to one native event does not create a descriptor
emitter, affine route, recursive child interface, scalar/grid bridge or
global allocation theorem. Earlier incremental phase mathematics remains
credited to #5375; the helper/table/commit predecessors remain credited.
All five selected foundational assumptions and the complete selected kappa
remain unchanged. The exact packed-descriptor and affine/native joins in
the author's open questions are substantive remaining obligations.
