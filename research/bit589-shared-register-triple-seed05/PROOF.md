# Exact finite census on a fixed single-move-option product

## Claim and scope

For the seed-selected A-section triple `(927, 928, 930)` in the pinned
PR589 `v=111`, `R=439` word, let `D_i` denote the frozen `(slot, frame)`
choices certified for moving operation `i` **individually** by the PR1345
atlas on the unchanged word. Every tuple in `D_927 x D_928 x D_930`,
under the verifier's specified deterministic reinsertion, either fails the
full chain-nesting replay, preserves the paid profile, or strictly raises
its exact moment cost. There are no improvements or unresolved tuples in
**this fixed product**. No completeness for jointly enabled frames or
commutation-dependent placements is asserted.

## Fixed inputs

`SOURCES.json` pins the selected-result record, review, assembly, selected word
bytes, bit-cost record and moment-cost implementation to base commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. It separately pins the exact
PR1345 atlas source and the relevant predecessor heads. `verify.py` checks both
Git blob IDs and SHA-256 hashes before using these inputs. It also checks that
the selected certificate still names
`836330098538459/500000000000000000` and that PR589's bit saving is exactly
`1733427039589844234749/1000000000000000000000000`.

The vendored atlas is loaded only through the definitions needed for legal
options and exact scoring. The verifier stops before executing PR1345's own
single/pair census, so this package independently applies those definitions to
the new triple.

## Domain construction

Let each A operation's legal options be its exact `(slot, frame)` pairs from
the pinned atlas. Form the graph on movable A operations, joining operations
whose source/target register sets intersect. Keep components whose product of
individual option counts exceeds 200,000. Within that large component, collect
same-register triples with option-product at most 5,000 and with more than one
distinct legal frame for each member. Sort by `(option product, operation
indices)`. This gives 200 tuples; seed `5 mod 200` selects index 5,
`(927, 928, 930)`.

The selected operations all write register 325 at frame 282, from sources
256, 442 and 392. Their frozen **single-move** option lists contain 7, 6
and 5 entries, so the Cartesian product has exactly 210 tuples. This is
complete enumeration of the specified product, not a proof that the product
contains every globally legal triple placement. In particular, the atlas
single-move lists need not include choices enabled only after another move,
and alternative commutations/reinsertions are outside this finite model.
No random sampling is used within the selected product.

## Classification and pricing

For each Cartesian-product tuple, the verifier reinserts the three selected
A operations according to the fixed key `(slot - 0.5, original_index)`,
while all other A operations retain their original index order; the C section
is then rebuilt. The pinned PR1345 chain scorer checks nesting for precisely
this joint reconstruction. If it returns no score, the reconstructed word
is also replayed and required to fail the full map check. Otherwise, the
candidate preserves the selected gates and operands, and the exact paid
profile is computed by replaying all 661 registers. This reconstruction
does not enumerate other commutation schedules with potentially different
legal frame options.

It then prices the profile difference against the original using the pinned
rank-cost intervals. The independently aggregated profile interval must be
contained in the full-chain scorer's interval. Equal profiles have exact zero
direct delta. For changed profiles, the reported interval is strictly positive;
all 64 such assignments have the same changed profile. This establishes a
negative result only over the 210 assignments in the stated finite domain.

The full census is: 46 nesting-incompatible assignments, 100 valid assignments
with the baseline profile, and 64 valid assignments with a strictly higher
profile cost. There are zero improvements and zero unresolved assignments.

## Controls and limitations

The replay checks an all-home identity, rejects a changed source operand, and
rejects a word with the selected A ADD omitted. These controls check the input
identity and coverage paths used by this finite verifier; they do not turn the
census into a formal proof of all PR589 transports.

Jointly enabled placements not present in the fixed single-move option
lists, alternative admissible gate commutations/reinsertions, other triples,
four-way changes, cross-section triples, structural changes, and other
supplier words remain open. No optimum theorem,
new supplier admission, or new `kappa` is claimed. Inherited PR589/compiler,
realization, hosting, precision/tape, and analytic assumptions are unchanged.
