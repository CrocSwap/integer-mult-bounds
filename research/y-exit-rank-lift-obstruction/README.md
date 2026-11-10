# Y-exit rank lift loses against the centre budget

On the pinned round-three centre word, raising every rank-8 Y exit chart to
the unique rank-9 frame and lowering it back adds **224 rank-1 children**.
The word's entire rank-8 budget is eight centre transports, rank mass **64**.
For every moment exponent `θ` in `(0, 1]`, deleting any submultiset of those
transports leaves a paid-moment increase of at least **160**. The constant is
attained at `θ = 1` by deleting all eight. **No new κ is claimed.** The
selected value stays `781451/250000000`.

The argument is in [PROOF.md](PROOF.md). The checker reads the pinned word and
the retained emitter; it does not trust the counts above as inputs.

## Scope

Catalogue card `complex-rank-shape-decoder`, priority revision 8, scope
**changed**. The card asks whether one changed itinerary improves the full
signed moment, and it says to stop when the optimistic budget fails. This
prices the Y-exit round trip from discussion #1166 comment 19133861. PR #5698
already closed the compatible binary coframe class, and the independent
one-transvection census on this contact graph is closed through induced
four-contact blocks. Those are different alphabets. Helper targets stay at
the retained histogram. This is not a decoder of the selected #6030 word.

A one-way raise, without the return, still loses by at least 48 rank mass and
does not restore the rank-8 exits. The proved tariff is the round trip.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/y-exit-rank-lift-obstruction/verify.py
python3 -O -B research/y-exit-rank-lift-obstruction/verify.py
python3 -B scripts/research_package.py --package research/y-exit-rank-lift-obstruction
```

The marker is `PASS_Y_EXIT_RANK_LIFT_OBSTRUCTION` with
`round_trip_h1=224`, `rank_mass=64`, and `moment_gap_at_least=160`.
Controls reject a ninth centre call, a nonpositive rank, a negative child
count, and a width-2 claim for dimensions 8 and 9. The retained `replay`
rechecks the paid histogram and the output charts.

Not run: a physical caller, native phase beyond this emitter, Lean, Docker,
and `make frontier6030-verify`. `scripts/research_selected_baseline.py` is a
binding check only.

## Open next questions

1. Can a route that moves only some Y exits, or that also deletes helper
   calls, clear a positive paid moment while restoring every rank-8 Y exit?
   The all-Y round trip cannot, because 224 already exceeds 64. First step:
   one literal route whose added rank mass is at most 64, with these exit
   charts and the 408 helper targets fixed. No such route is supplied here.
2. Can the one-way move onto frame 1 be accepted as an endpoint? It leaves a
   gap of at least 48, and it replaces each rank-8 Y exit by frame 1. First
   step: compare one Y role's exit chart before and after. The restored-exit
   tariff proved here does not apply to that chart change.

## Credit

The word is Cao Yifan / intqwq, PR #4610. The width law and the eight-centre
emitter are the retained centre extension used by the contact-frontier
package, following Cinna Davis and Dugongue's chart convention. Discussion
#1166 comment 19133861, Chris R / Clear1nsight, named the 224-against-64 stop.
The centre-chain terminal prices a different bill (112 rank-8 children and
114 rank-9 children). The chart-pair, triple, four-vertex-tree, and
four-cycle certificates price one-transvection contact moves, not this exit
transport.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review or proof-kernel check is claimed.
