# Counterless reversal with an owned delimiter

This is a scoped proof for one fixed two-tape machine. The source sampling
law and edge-inverse lemma are credited premises, not new sampling theorems.
The new step replaces a numerical stopping counter by a local tape boundary.

## Statement and exact boundary

Let the random tape contain an infinite binary string beginning at position s,
with one caller-owned blank symbol `_` at s-1. Positions below s-1 are arbitrary
and protected. The random head begins at s. A second tape has one stationary
head on a dirty four-symbol cell A, interpreted as a two-bit accumulator.
The caller supplies the fixed `(1,1)` denominator-13 DDG of zxv's PR #6072.
Write i for its first output and T for its stopping depth on the binary string.

For every string with finite T, the machine in `machine.py` terminates with
A replaced by A XOR i, every random-tape symbol and both heads restored, the
owned delimiter cell blank, and finite control at its fixed return label.
It uses exactly 3T+4 two-tape transitions and 2T+4 random-head moves, has
maximum random-head excursion T to the right and one cell to the left, and
writes the delimiter cell exactly twice. It has no numerical stopping counter,
position register or per-step history. A finite certificate establishes 1,563
control states and 10,000 rules for this fixed graph.

A two-tape transition reads both current symbols, writes their replacements,
and moves the random head by -1, 0 or 1. The output head stays fixed. The random
tape alphabet is `{0,1,_,#}`; the output alphabet has four symbols. These are
finite-alphabet machine steps, not individual binary gates or the repository's
native paid calls. Fixed rule selection is part of finite control, with no
unit-cost RAM lookup assumption. Binary-alphabet lowering has an additional
constant cost not computed here.

## Predecessor facts used

The retained `vendor/paired_sampler.py` is zxv's exact PR #6072 source at
`9011bf83e85ecd0443c789cf03259442f750877d`. Only `make(1,1)` is called to obtain
its graph, phase layout and cited expectation. Its original `main`, sampling
census and optimality checks are not run.

JoyboyBrian's PR #6102 at `0422af13625c2e7e8ece28bdd74364a61764c64a`, retained in
`vendor/PROOF.reversal.md`, proves that the predecessor phase p, consumed bit u
and current DDG target identify a unique previous node. For an internal target,
recover q by adding the sum of the four binary digits to its node index. For a
leaf, recover q from that leaf's digit slot. Then the previous node is
(q-u)/2. The digit ordering and phase are essential. We use that lemma, rather
than claiming a new inverse or auditing the predecessor proof.

The source law gives the independent output probabilities `(144,12,12,1)/169`
and E[T] = 9960277917013927549978 / 4649714690825496825793 < 9/4.
These probabilistic statements remain predecessor premises. Our pathwise
construction does not need fair bits or independent bits for reversibility.

## Local machine

`F(p,j)` means forward DDG state j in phase p. `B(p,j)` means that j is the
current reverse target and the random head is immediately after its prefix.
`R(p,j)` means that the head has moved left onto the next bit to undo.
Here j may be a leaf in B and R. The phase is always modulo 156.

1. In `entry`, move left. In `prepare`, replace the owned blank by `#`, move
   right, and enter `F(0,0)`. These are two transitions.
2. For `F(p,j)` reading u, apply the source edge and move right. At an internal
   target enter its F state. At leaf i, XOR i into the second tape's symbol and
   enter `B(p+1,leaf_i)`. Output retention is part of this last transition.
3. In any B state, move left and enter the corresponding R state.
4. In R on a binary symbol u, apply the predecessor's inverse edge, decrement
   phase modulo 156, and enter its B state without moving the head.
5. The only rule on `#` in R is `R(0,0)`: replace `#` by `_`, move right, and
   return. Other R states have no marker transition.

No transition reads an absolute coordinate, stopping depth or elapsed time.
The Python observer's bounded loop, head coordinate and measured counters are
outside the finite rule key. The full rule key contains only control, current
random-tape symbol and current output symbol.

## Correctness for arbitrary terminating paths

After k forward steps, the head is at s+k and F has exactly the source's
phase and node, until the source first terminates. Thus after T steps the
output cell is A XOR i, the head is s+T and B stores the last target and phase.

By backwards induction, after reversing T-k edges, B stores the exact source
state after k steps, phase k modulo 156, and the head is at s+k. For k>0,
the next left move reads a binary symbol at s+k-1. The cited inverse lemma
recovers exactly the source state after k-1 steps. It leaves the output cell
unchanged. At k=0 the next left move reads the delimiter at s-1 and B's state
is the root at phase zero. The final rule erases the marker and returns to s.

A root revisit at a positive multiple of 156 does not terminate reversal:
its preceding tape cell is binary. The unique delimiter, rather than a root
state test, distinguishes the initial visit. No numerical T survives or is
needed during the call. The output value need not be retained in separate
scratch because it was copied before the leaf was undone.

All data symbols are read-only. The only first-tape writes are blank-to-marker
in preparation and marker-to-blank on return. Hence arbitrary protected cells,
the entire random string and the owned blank are restored. The output head
never moves. This proves the stated map on every terminating path.

The local rules are also one-step injective as a partial machine on arbitrary
configurations. Every destination control has a unique incoming head direction.
Given that direction, the written symbol and output symbol identify a unique
incoming rule. Forward injectivity is the cited phase-and-coin inverse. Reverse
injectivity is forward determinism. The marker/preparation ranges are disjoint
from binary ranges. The verifier checks these two finite injectivity predicates
on every generated rule. Invalid configurations may have no transition; total
behavior outside the stated entry invariant is not asserted.

## Exact accounting and finite certificate

Preparation costs two steps. The forward walk costs T steps, including output
XOR. Reversal costs two steps per consumed bit and two final delimiter steps.
The total is 3T+4. Preparation and the final marker probe each move twice;
each data bit contributes one forward and one backward head move. Travel is
2T+4. No per-step controller bit is allocated.

There are 312 F states. The actual source edges produce 624 distinct target/
phase pairs: 312 internal pairs and 312 leaf/phase pairs. Each has B and R
states. Entry, prepare and return add three, giving 312+2*624+3=1,563.
For each of four dirty output symbols, the rules contain 624 forward edges,
1,248 B moves, 624 inverse edges, two entry rules, one prepare rule and one
return rule. Thus 4*(624+1248+624+2+1+1)=10,000. The verifier enumerates the
states and rules instead of inferring these finite counts from a sample run.

Using the cited source mean, E[steps] = 3E[T]+4 equals
48479692514343769953106 / 4649714690825496825793 < 43/4.
This counts finite-alphabet machine steps. It is not a wall-clock speedup or a
comparison with a native recursive invoice.

The finite replay covers 4,088 short dirty-output runs and all 938 terminating
prefixes through depth 470. Those longer runs contain 942 reverse root revisits.
They corroborate the interpreter, wrap handling and exact bills. The induction,
not the finite fixture depth, proves correctness for arbitrary finite T.

## Scope and remaining cost

The changed contract supplies one owned blank immediately beside the random
segment and a stationary output head. The machine pays to mark and clear that
blank. Providing these positions in an actual caller, fixed binary-machine
lowering, parameter dispatch and native adaptation remain separate obligations.
The graph and finite control are fixed before any random bits are read.

The resident transcript and the random-head excursion have no finite worst-case
bound. This is constant auxiliary control and delimiter storage, not constant
total space. After output retention, the consumed tape is correlated with that
output. Restoring its symbols does not make them conditionally fresh. No actual
multiplier caller, supplier admission, new kappa, complete multiplication theorem,
independent human acceptance or proof-kernel verification is claimed.
