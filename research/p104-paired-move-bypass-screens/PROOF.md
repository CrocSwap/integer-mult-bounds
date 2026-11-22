# Proof of the bounded screens

All spaces below are over the field with two elements. At every clock a chart
retains every normalized field it has owned. This retention is a free grant; it
is not an assertion that an actual physical realization gets unlimited memory
or scrubbing for free. The 630 public inputs are independent. The native
instruction replay verifies every final field against the intended `(x,y+x)`
pair map and all helper identities before constructing the screens.

## Path census and chart admission

Read every actual MOVE, its ordered endpoints and its zero-based instruction
clock. Select all pairs `a → h` at `i` and `h → b` at `j > i` such that both
native rank differences are one and the absolute difference of endpoint ranks
is two. The rank condition makes the two steps monotone. Check both orders of
the projector product on each original pair and each replacement pair:
`P_small P_large = P_large P_small = P_small`. The rational matrices and their
denominators are exact and denominators are units at three. There are 1,557
pairs, involving 859 distinct original endpoint pairs and 333 distinct direct
endpoint pairs. Thus every enumerated replacement has a valid rank-two nested
chart difference. This check does not emit its physical MOVE implementation.

## Receipt-preserving overgrant

Fix one selected pair. Delete its first MOVE, put the direct contact at the old
second clock, and retain every other contact and its clock. At any surviving
contact, let `S` and `R` be the complete sender and receiver historical spans,
and let `f` be the original received field. All sender fields are eligible
payloads and all receiver fields may be XORed freely. We require the receiver
to reconstruct `f` immediately. If `f` is not already in `R`, this is possible
only when `f ∈ S + R`; the stock after such a single scalar is necessarily
`R + span(f)`, since the scalar must equal `f + r` for some `r ∈ R`. If `f`
already lies in `R`, we give the receiver the full `S`, dominating any
one-scalar choice. Induction over the contacts proves that this recurrence
contains every causal history satisfying the stated receipt contract. If the
recurrence cannot reproduce a receipt or final output, no such history exists.
It does not exclude a valid program with different receipt values.

The computation reports the first failed receipt or terminal result for every
pair. Totals are 616, 619 and 18 first failures respectively before, at and
after the replaced contact, and 304 terminal failures. Neither the unmodified
run nor any tested alternative actually triggers the full-sender overgrant:
every retained native receipt is independent of the receiver's stock. The
result file records all 1,557 cases. Its separate chronological control
restarts from public inputs for each case, using the same linear-basis routines
as the incremental implementation.

## Final targets under fixed exterior source envelopes

For a bypass whose hinge `h` contains a required final public field `t`, take
the union `U` of the initial fields at `h` and the native preclock sender spans
of every retained contact entering `h`. Grant all these spans in their entirety
at the hinge, irrespective of their individual one-scalar capacities and
without preserving any native receipt. The direct edge ends away from `h`.
If every actual remaining sender is constrained to information in its native
preclock span, all information arriving at `h` lies in `U`. If `t` is not in
`U`, a vector `q` can be chosen with `q·u = 0` for every `u ∈ U` and `q·t = 1`.
The two independent public inputs differing by `q` produce the same granted
source data but different required target values. This rules out arbitrary
local recoding even with unlimited ingress capacity.

All **854** enumerated paths with a final output at their hinge admit such a
witness, across **111** hinges and **304** distinct hinge-and-ingress cuts. The
verifier checks each `q` against every basis vector of every granted source span
and checks that adjoining the removed native receipt makes `t` representable.
These 304 positive controls show that each tested cut detects the deleted native
direction in the stated
frozen-exterior model. They do not show that changed exterior producers obey
that model or that a different contact schedule cannot work. For the specific
`344 → 525 → 1` example with ingress clock 8243 and egress clock 10093,
`q = e111 + e589`, while the missing target is `e0 + e111`. A second parser
replays the primitive word and rebuilds every stock using low-pivot elimination,
then checks all 854 certificates, all restored-row controls and a deliberately
corrupted target probe for each case.

## Unlimited-bandwidth input ancestry

Remove all receipt requirements. Give every surviving contact **every input
coordinate** in the sender's causal history. At each clock, take the union of
input labels at the receiver and sender. By induction this is an upper bound
on which original inputs any causal computation at that chart can depend on,
regardless of how its scalar payloads are encoded. If a target output requires
an input absent from this overgrant, that output cannot be correct for all
independent public inputs. Only fixed endpoints, order and public charts are
assumed; finite payload capacity and native receipt values are not assumed.

The ten exclusions are:

| Hinge | Deleted ingress clock | Replaced egress clock | New direct edge | Missing input | Failed output at final chart |
|---:|---:|---:|---|---:|---|
| 12 | 208 | 215 | 0 → 196 | 10 | 121 at 535 |
| 12 | 211 | 215 | 0 → 196 | 10 | 121 at 535 |
| 44 | 792 | 799 | 0 → 206 | 42 | 153 at 567 |
| 44 | 795 | 799 | 0 → 206 | 42 | 153 at 567 |
| 82 | 1575 | 1589 | 0 → 171 | 80 | 191 at 605 |
| 82 | 1578 | 1589 | 0 → 171 | 80 | 191 at 605 |
| 83 | 1593 | 1604 | 0 → 257 | 81 | 192 at 606 |
| 83 | 1596 | 1604 | 0 → 257 | 81 | 192 at 606 |
| 515 | 8312 | 10063 | 351 → 1 | 80 | 191 at 605 |
| 515 | 8312 | 10066 | 351 → 1 | 80 | 191 at 605 |

The other 1,547 pairs pass only this overgenerous necessary test. In
particular, no positive supplier or optimization follows. Changing clocks,
adding/replacing other contacts or changing the port bindings is outside the
screen. The full sequential and incremental ancestry runs agree on every case.
