# A fixed contact obstructs a stop deletion

## Model and claim

An epoch is a visit by one register to one frame between consecutive MOVE
events. INIT starts a new owned lifetime and CLEAR ends it. An intermediate
stop is an epoch with both an incoming and an outgoing MOVE in the same
lifetime. Initial and terminal epochs are excluded.

Freeze the word in DreamingOfClouds's PR6345, at the source bytes recorded in
SOURCES.json. Let S be its public non-main registers with exactly one MOVE.
The main registers are `live` and `112 + live`, as in the predecessor contract.

Consider the following simultaneous relaxation.

1. Every register in S may replace both endpoint frames by arbitrary binary
   subspaces, retaining its unique MOVE at its original position among scalar
   events. These endpoint choices need not belong to the published catalogue.
2. Choose one intermediate stop U of a different register r. Replace its two
   neighboring transports A -> U -> C by one transport A -> C. This transport
   may occur at any cut between the retained surrounding epochs. In particular,
   the scalar events formerly at U may be divided between A and C.
3. All other epochs retain their frames, and scalar coefficients, operands,
   operations, lifetime boundaries and scalar order are fixed. Scalar chart
   annotations may be rewritten, but each ADD or COPY still requires equal
   source and destination frames. Additional transports are excluded.

The new result is a scoped impossibility statement. No such assignment exists
for any intermediate stop of this word. There are exactly 2,660 such stops,
2,654 public and six owned, and S has 42 members. This is a stronger endpoint
freedom than choosing just one helper from the existing native catalogue.

This statement concerns deletion of one stop while the other non-S epochs
remain fixed. It does not exclude coordinated changes to two non-S registers,
changed scalar schedules, new transports or a different word.

## Fixed-contact lemma

Suppose an intermediate stop U of r contains an ADD or COPY involving another
register s. Suppose s is outside S and its epoch at that event stays fixed at
U. If U differs from both neighboring frames A and C, deleting the visit to U
is impossible under the model above.

Proof. At the contact, the common-chart rule forces r's frame to equal s's
fixed frame U. After replacing A -> U -> C by A -> C, r's frame at every
scalar event between the surrounding epochs is either A or C. Neither is U.
Thus the contact cannot satisfy the common-chart rule. This argument permits
any position of the merged transport and does not depend on the new endpoint
frames of registers in S. QED.

## Exact application to the frozen word

`certificate` in verify.py indexes every constant-frame epoch and each
ADD/COPY contact. For every intermediate stop it chooses the first contact
whose other register is outside S. The direct contact itself is the witness;
no transitive equality inference or optimization solver is needed.

Each witness has seven integers:

```text
[register, lifetime, stop ordinal, event index,
 partner register, partner lifetime, partner epoch ordinal]
```

Event indices and public lifetime numbers start at zero. Owned lifetimes start
at one. Stop ordinal k means the epoch after the kth MOVE of that lifetime.
For each candidate, explicit binary spans show strict nesting of the three
neighboring frames, increasing for public registers and decreasing for owned
registers. In particular U differs from A and C as subspaces, irrespective of
frame labels or basis choices.

Every one of the 2,660 candidates has a direct fixed-partner contact. A second
streaming implementation, `check_certificate`, discovers its candidate set by
recording the epoch left by every MOVE after the first MOVE of a lifetime.
It checks exact candidate coverage, unique witnesses, actual event operands,
both current epoch identities, the common chart and the partner's exclusion
from S. It does not call the primary trace builder or domain enumerator.
The fixed-contact lemma therefore applies separately to every candidate.

The generated receipt contains every witness and hashes of the input,
decompressed payload and package files. The receipt is generated on request
outside the checkout. Reproduction computes all witnesses anew.

## Consequence for the open question

PR6345 asks whether a re-spanned helper can enable a stop drop elsewhere.
For the stated fixed-schedule, single-stop move, even all 42 one-step helpers
together cannot do so. A successful continuation must alter at least one
additional non-S epoch at a blocking contact, change the scalar incidence or
schedule, introduce another transport, or change the word. This is a necessary
change of scope, not a sufficiency theorem for any of these alternatives.

The predecessor's legality, paid invoice and reported crossing are premises,
not results re-established here. No price calculation or native operator replay
is needed to rule out a move that already fails a necessary chart equality.
No new kappa, supplier admission or complete multiplication theorem is claimed.

Ali Romman's PR5590 already supplies an all-frame price floor with all scalar
contact frames fixed on PR5580. That theorem is credited rather than repeated.
The present finite step concerns the different PR6345 word and allows helper
contact charts to vary with the 42 re-spanned helpers. It finds a different,
fixed-partner contact at each stop. Common-chart equality is inherited syntax;
the new contribution is its complete source-bound obstruction in this move
domain, not a new general theory of frame transport.

## Controls and limits

The verifier rejects an omitted witness, a duplicate witness, five incorrect
contact/epoch fields, a free-helper partner, an unanchored toy and a collapsed
toy with a fixed contact. Two positive toy controls demonstrate an anchored
stop and an actual unanchored stop deletion enabled by helper respanning.
These toys test chart constraints only, not complete productive suppliers.

The two implementations are new code by the same contributor. They do not
constitute independent scientific review or formal proof-kernel checking.

New result, proof and implementation produced by Nick Petalas. Apache-2.0.
