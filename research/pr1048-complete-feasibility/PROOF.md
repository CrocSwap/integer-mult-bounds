# Complete two-transport reduction on the frozen PR589 word

This is a finite local claim about the exact input and transport contract below.
It is not a claim that all circuit rewrites, all subspaces, or longer paths have
been exhausted. The scalar supplier and its multiplication-theorem obligations
remain inherited. The numerical census accompanying this proof must complete
and both implementations must agree before the exclusion is accepted.

## Domain

The input is `research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz`,
container SHA256 `e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f`.
Flatten A and B into their 3,064 elementary ADD occurrences. Identity is the
original `(section,index)`, not the current list position. A transport removes
one occurrence and reinserts it in the same section, crossing only ADDs that
commute with it. For ADDs `t += u` and `a += b`, the test is `t != b` and
`a != u`; hence all crossings preserve the scalar map.

At the insertion slot, let L be the union of the two preceding register frames
and U the intersection of the two following frames. The permitted frame masks
are every original catalogue frame plus the exact rational span closure of L,
filtered by `L subset F subset U`. The 636 original frame masks are closed
under rational span; the independent checker verifies this. Thus containment
of their root-line masks represents the required subspace containment. D,
start/final frames and the A/B separator stay fixed. The resulting last A frame
of every retained register must equal its original COPY frame, including after
removal of its former last touch. No corresponding COPY restriction is imposed
on B. C is reconstructed by reversing the same eligible operations at the full
frame, as in the frozen supplier contract.

The catalogue is fixed: a closure introduced at an earlier slot is not added
as an unrestricted frame option at future slots. An intermediate word must be
legal. The claimed class consists of **at most two** such transports, allowing
either section and repeated choice of the same operation.

## Root comparison

Use the previously reviewed [pricing proof](../pr1048-certified-repair/PROOF.md).
The local baseline profile is `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`.
Replication is 288, m=64, W=28416 and the idle profile is fixed. With
`lambda = 32*64^2/10^16 = 2/152587890625`, define

    F_n(a) = sum_r n_r*r*(64/r)^a + lambda*(sum_r n_r)*64^a - 64*W.
    J_delta(a) = sum_r delta_p[r]*r^(1-a) + lambda*sum_r delta_p[r].

The reference root c is strictly between
`1733427039589844234749/10^24` and `1733427039589844234750/10^24`.
Both implementations establish the endpoint signs with outward rational
enclosures of log and exp. The signed price encloses J on the **whole** bracket.
At c, `F_candidate(c) = 288*64^c*J_delta(c)`. Consequently an upper bound below
zero certifies a larger, better root; a nonnegative lower bound certifies no
improvement; a straddling enclosure remains unresolved. Identical profiles are
exact ties. No acceptance depends on floating-point evaluation at an endpoint.

Every transport preserves total rank mass: register climb dimensions telescope,
and retained COPY dimensions are pinned. The global mass is M=1,808,352,
while `64*W-M=10,272`. Counts are nonnegative and ranks are in 1..64, so the
global call count N satisfies `0 < N <= M`. Therefore
`F_n(0) = -10272 + lambda*N < 0`. The positive surcharge makes F continuous,
strictly increasing and unbounded, proving a unique positive candidate root.
The implementations additionally check the concrete priced profiles.

## Singles and the easy pair cases

The complete single census enumerates every literal legal slot and frame for
all 3,064 occurrences. Caching `(frame,touch-counts)` is valid for this final
profile: all changed transitions lie on the mover's two register itineraries,
and this key identifies those transitions. It is not a continuation quotient.
The two existing enumerators separately reconstruct all 1,452,893 literal moves
and agree on every operation's domain digest and the 22-delta histogram.
There are 1,227,676 exact profile ties, 225,217 strictly worse moves, and no
better or unresolved move.

If both transports move the same occurrence x, delete x. The remaining word
is unchanged. Neither transport can cross an unchanged noncommuting blocker,
so the final position lies in x's original commuting interval. Its final
slot's lower closure, frame options and COPY constraints are exactly those of
a baseline single transport. Thus repeated-occurrence pairs reduce to singles.

If the movers x,y have disjoint register supports, erase x from the intermediate
schedule and map y's slot to the baseline. Any extra crossing of x is harmless:
x and y commute, and x changes none of y's register frames, closure constraints,
section boundary frames or COPY conditions. Hence y's final effect is a legal
baseline single effect (possibly the identity). The two profile deltas add,
including the call-count surcharge, so their J values add. Nonnegative single
prices exclude every such pair.

## Exact projection for each remaining pair

Fix distinct overlapping occurrences x,y and put `R=supp(x) union supp(y)`.
There are at most three registers in R. In **both** sections erase every other
operation whose support misses R. Keep the original catalogue, D, start/final
data and COPY pins. Replay and price only R; a global profile of the erased
background would be meaningless.

Every erased operation commutes with both movers and touches no R register.
It cannot change a relevant neighboring frame, commuting blocker, slot closure,
A/B boundary, COPY snapshot, or C touch. Therefore projecting any full legal
two-step path yields legal projected transports or identities, with the same
final delta. Conversely, a projected transport lifts by inserting its mover
at any full slot in the corresponding gap: all additional crossed operations
are erased and commute with it, and the neighboring R frames are identical.
Lift the second step after the first; projection still agrees. Outside R,
neither transport changes a register itinerary. This proves equality of the
reachable final profile sets, not just a one-sided heuristic comparison.

The first step visits every projected slot and feasible frame, plus the
identity. The identity covers full moves that crossed only erased operations.
It does **not** collapse first states by their own register touch signature or
by equal profile: operations touching y's private register remain visible and
can change which second slots exist. The independent checker's small synthetic
example shows that the unsafe quotient can hide a strictly improving second
move even when every baseline single is neutral. It is a control, not an
improvement to the frozen word.

For each first state, enumerate every legal second slot/frame and the identity.
Only this final step may collapse equal `(frame,touch-counts)` contexts, because
there is no further continuation and those contexts have identical final R
profiles. No minimum-frame or maximum-frame dominance is used by the scan.
Every retained final delta is priced with the certified reference-root oracle.
Any better or unresolved result prevents a complete exclusion.

## Exhaustion and its limit

All `3064^2 = 9,388,096` ordered occurrence choices partition into 3,064 repeated
occurrences, 9,325,034 register-disjoint choices, and 59,998 distinct overlapping
choices. Of the last group, 13,054 cross the A/B section choice and 46,944 use
the same section. The first two groups are covered by the preceding lemmas;
the complete finite projected census covers the last group. These counts are
operation choices, **not** counts of literal two-move paths. Projected states
and final-profile representatives are likewise not claimed to be distinct
full words.

This argument does not cover three or more moves, noncommuting circuit
identities or Steinberg rewrites, simultaneous changes through illegal
intermediates, moves between sections, a growing frame catalogue, or arbitrary
new subspaces. It repairs a specific pricing and completeness claim about the
historical PR589 word; it supplies no new kappa, selected supplier, scalar
lowering, native/physical admission, precision result or full theorem audit.

Prepared by Brian Ross with substantial OpenAI Codex assistance, including
separate GPT-6 Astra analyses and replay. The supplier/tuner credit remains
with DreamingOfClouds and predecessors, the original search with flemhhh, the
existing counterexample with Douglas Colkitt/the maintainers, and the root
bracket repair with woklerx PR1182. The independent reconstruction and semantic
corruption approach adapts Brian Ross's
[Krenn verifier](https://github.com/brianross93/Krenn/blob/ab446724a61a293a3268c63b9e9e721c6a360561/experiments/krenn_quantum_graph/independent_verifier.py)
and [artifact tests](https://github.com/brianross93/Krenn/blob/ab446724a61a293a3268c63b9e9e721c6a360561/tests/test_krenn_artifacts.py);
exact-arithmetic discipline also draws on
[ThetaTwist](https://github.com/brianross93/thetatwist/blob/b4ec6c13088b89961834cc675b44b81372199b02/src/thetatwist/core.py).
These are methodological adaptations, not copied code. New material is
Apache-2.0; the unchanged predecessor notices remain in the certified package.
