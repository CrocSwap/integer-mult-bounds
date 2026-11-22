# Independent computational and mathematical review

## Result and scope

The nine-contact statement is proved for fixed, input-independent schedules in
which each downward contact conveys at most one **binary** scalar, all other
cross-chart contacts are between nested projectors and go upward or remain at
the same level, arbitrary cochart computation and storage are permitted, and
register names travel with the chart and value under SWAP. The original 630
public inputs are independent; private initial states carry no input information.
All 111 native head and body endpoints are fixed. Contacts and computation can
be changed, including through feedback. The receiver may use its entire
history. The stated assumptions exclude input-dependent free control or
communication through the schedule.

An independent exact-rational check reproduces the small obstruction witness.
An independent instruction interpreter checks the emitted nine-contact word,
all 630 public output rows and their 630 literal transpose rows. Thus the
minimum **number** of downward bit contacts is nine in this normalized model.
The word uses nine grade-8 contacts, raising the native total rank from 4,813
to 4,822; a count saving alone does not establish a price or κ improvement.

The channel alphabet matters. Binary **inputs alone** are insufficient if an
arbitrary nonlinear encoder may emit an unrestricted integer or rational
scalar: after collecting 111 bits at chart 1, it can encode them as
`sum(2**i*x_i)` in one scalar, send it to chart 0 and decode each bit there.
That is an explicit counterexample to a purported one-bit transcript bound in
an unrestricted integer-scalar channel. The result here assumes binary-valued
messages or an equivalent one-bit communication bound. The replay is over
GF(2); it does not certify the full physical field implementation, private
erasure, or the asymptotic caller.

## Reduction, including interacting feedback

Let `S_i` be the initial rank-1 chart for head bit `x_i`, and let `T_i` be
its rank-7 output chart. Write `P <= Q` for `PQ = QP = P`. This is transitive:
if `P <= Q <= R`, both `PR=PQR=P` and `RP=RQP=P`. A nondescending nested MOVE
therefore carries information only to a chart above its source in this order.
An equal-dimensional nested MOVE has the same projector at both ends.

Pretend that every chart receives the entire ordered transcript `D` of all
downward payloads. Simulate the fixed schedule, using this transcript in place
of the contents of downward contacts and granting free retention to charts.
Inductively, the local state at chart `Q` is a deterministic function of `D`
and the initial input bits whose charts are at or below `Q`. For a local
operation this is immediate. A nondescending MOVE preserves it by transitivity;
a downward MOVE is supplied in `D`. A SWAP exchanges global owner names along
with their values and chart labels: no value has traveled to a different chart.
This induction allows the actual downward messages to depend on all earlier
traffic and therefore permits backward feedback and arbitrary cross-field
recoding. Fix the other 617 public inputs and all independent initial helper
states to constants; this cannot hurt a purported universal implementation.

For 13 selected head bits, the other paired body inputs are among those fixed
constants, so terminal chart `T_i` must recover `x_i`. It follows that each
selected terminal can recover its own bit from `D` plus all `x_j` with
`S_j <= T_i`, even after granting that entire side-information set for free.
The exact-projector replay verifies these incidence sets directly from the
authenticated native frames, without trusting either producer's code.

## The eight-color obstruction

Use clique vertices `C=(0,14,15,30,31,60,69,70)` and the five outside bits
`z_78,z_77,z_93,z_61,z_110`. Their receiver-to-clique side-information sets
are respectively `(0,14)`, `(0,15)`, `(0,30)`, `(14,15)`, `(14,30)`. A
receiver among these five sees another selected outside bit only when their
endpoint pairs are disjoint. The side-information relation is symmetric on
these 111 native ports. No clique receiver sees any clique bit, including its
own.

Suppose there are at most eight downward contacts, padding the transcript with
fixed zeros if necessary. For each fixed outside vector `z`, the eight clique
bits map injectively to the eight-bit transcript: if two vectors had the same
transcript, each clique receiver would see identical information but one
would have a different demanded bit. Consequently the map is bijective. Fix
one transcript value `d`. For every one of the 32 choices of `z`, exactly one
clique vector maps to `d`. At this fixed `d`, clique bit `x_c` is a Boolean
function `h_c` only of the outside bits whose edges are incident to `c`.

Consider one outside bit `z_e` whose endpoint pair is `(u,v)`, and fix every
outside bit disjoint from `e`, which only gives its receiver extra information.
The remaining nuisance bits of `h_u` and of `h_v` are disjoint sets: there is
at most one edge for a pair of vertices, namely `e`. For `z_e=b`, the possible
pairs `(h_u,h_v)` form a Cartesian product `A_b x B_b` of two nonempty subsets
of `{0,1}`. The receiver must distinguish `b=0` from `b=1`; these two
rectangles must be disjoint. Hence `A_0` and `A_1` are disjoint or `B_0` and
`B_1` are disjoint. Since both sets are nonempty binary subsets, one endpoint
function equals `z_e` or its complement for **all** nuisance choices. A
single endpoint function cannot equal two independent outside bits up to
complement. Five edges would therefore need five different endpoints, but
there are only four. This contradiction proves the lower bound of nine.

The cardinality/bijection step is essential: it ensures all 32 outside vectors
actually occur in the fixed-transcript fiber, so the independent-nuisance
rectangle argument is valid even though the transcript arose from an
interactive protocol.

## Reproduction

Use Python 3.12 with standard library only; from the repository root, the two positional arguments to each script bind the checks to the packaged inputs:

```sh
python3 -I -B research/p104-nine-downward-contacts/check_index.py research/p104-nine-downward-contacts/pinned/strong-bit.json.gz research/p104-nine-downward-contacts/INDEX-WITNESS.json
python3 -I -B research/p104-nine-downward-contacts/check_word.py research/p104-nine-downward-contacts/pinned/strong-bit.json.gz research/p104-nine-downward-contacts/NINE-WORD.json.gz
```

`check_index.py` authenticates the pinned source, recomputes all 636 exact
rational projectors, checks all 2,803 original MOVE nestings and 12,321
head-to-body side relationships, verifies the clique and five-edge witness,
extracts the nine native terminal return forms, and checks all 111 saved
decoders. It rejects wrong endpoint incidence and a repeated clique vertex.
Its deterministic output is `INDEX-RECEIPT.json`.

`check_word.py` authenticates both complete source words, executes them with
independent symbolic forward and reverse interpreters, compares all 630
forward and all 630 transpose rows, confirms identical ordered upward MOVEs and
all 3,415 retained typed clear values, and checks the exact downward and grade
histograms. Removing a single actual source coefficient in the changed word
leaves a legal trace but corrupts 55 public outputs. Its deterministic output
is `WORD-RECEIPT.json`. Identical nonzero clear expressions are a normalized
trace check, not a proof of physical disposal.

This review and the distinct replayers were prepared independently by a separate OpenAI Codex agent, not by an independent human or a proof kernel.
