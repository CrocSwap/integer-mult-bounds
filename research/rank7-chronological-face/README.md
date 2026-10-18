# Rank-seven helper packing: an exact chronological cut and a cost-neutral repair

An independent check of Marius-Paul Dumitrean's [PR2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979)
at `be191346391661f4d35fc0d1508d0a6029572576` confirms a concrete bridge
needed by its changed helper boundaries: a pattern replacement can remove a
chronological width-seven deficit while preserving every recursive rank tariff.
This package makes no new kappa or complete supplier claim.

## Result and covered model

The source's six-width inventory is
`{4:26,5:2,6:16,7:52,8:99,9:213}` per call. Its T37 chronology has 333 calls.
On calls 45 through 332 inclusive, 14,976 width-seven roles can reach at most
13,440 capacity-16 bins. In the stipulated pattern family each such bin has
at most one width-seven slot. Therefore at least 1,536 of those roles must
use another capacity. This is a restricted pattern obstruction: an arbitrary
capacity-16 bin can instead contain two width-seven helpers.

Reverse the source's 1,063 declared swaps to obtain the naive integer mix.
After k swaps its four changing pattern counts are:

| capacity | helper widths | count |
| --- | --- | ---: |
| 16 | 7,9 | 16,253-k |
| 16 | 8,8 | 323+k |
| 32 | 7,8,8,9 | 1,063-k |
| 32 | 7,7,9,9 | k |

The nonnegative integer range is exactly `0 <= k <= 1063`. Width-seven slots
outside capacity 16 total `1063+k`; hence the displayed interval requires
`k >= 473`. In particular k=472 fails by one role. Passing this necessary
cut at k=473 does not construct a schedule. The shipped k=1063 fill is checked
separately against the actual chronology and provider-indexed widths.
The interval is the unique strongest one among all 55,611 contiguous intervals
under this global-reserve inequality. Arbitrary subsets and other constraints
can give different necessary conditions.

The swap

```text
[7,8,8,9]@32 + [7,9]@16 -> [8,8]@16 + [7,7,9,9]@32
```

preserves helper inventory, bin counts separately by capacity, and the complete
residual-rank histogram. All four bins are saturated. Thus it preserves the
whole rank moment for *every* tariff H, including the recursive power tariffs,
when the local word and all other charges remain fixed. It is stronger than
a rank-mass equality and does not claim that rearrangement is operationally free.

Every member has the T37 complete source-profile
`{1:822840,2:235098,3:79734,4:35964,5:6858,8:2664,48:14095}`;
doubling gives the frozen T74 profile. The integer family retains its existing
gap to the fractional cap. Its idle histogram minus 37 times the recorded
fractional-cap histogram is exactly
`-3 e1 -(57/20)e3 +(15/4)e5 -(3/20)e48`, which has zero rank mass and is nonzero.
No cap optimality, root digits or integral optimum are recertified here.

## Evidence and independence

[HALL-PROOF.md](HALL-PROOF.md) derives windows from the source event template,
literal order and replica cuts, then checks the relevant literal placement.
[FACE-PROOF.md](FACE-PROOF.md) proves the all-tariff identity and derives the
finite family and complete profiles. The two new standard-library implementations
do not import or execute predecessor owner, producer, LP or root routines.
All 1,064 integer family points and defect controls are checked explicitly.
`RESULT.json` records the exact finite coverage and controls.
The placement check covers all 271,728 roles, their integral masks and compact
prefixes, source windows, helper identities and same-call physical-family
exclusions. Both T74 copies project onto identical T37 rows. Each copy places
12,853 of the cut's width-seven roles in capacity 16 and 2,123 outside it.

`SOURCES.json` binds 19 frozen evidence files by SHA256 and Git blob identity.
The registered metadata check additionally checks their original Git provenance
and the pinned catalogue/selected record. The portable verifier authenticates
the frozen exports without requiring Git history. The width registry and event
template are conditional inputs: this check does not independently derive native
widths or prove arbitrary-dirty-input native restoration, phase adapters,
precision, physical tape costs, outer admission or all-size/compiler implications.
This is a written scoped argument with finite exact computation, not a
formal-kernel or independent human proof.

## Reproduction

```sh
python3.12 scripts/research_package.py --package research/rank7-chronological-face
python3.12 -I -B -O research/rank7-chronological-face/verify.py --check-result
```

The package directory alone, including its frozen sources, supports the second
command from any working directory with the script path adjusted. No solver,
network, native compiler or dependency installation is needed.

## Open next questions

What is the least k in this family admitting a complete chronological fill?
The necessary cut gives a lower bound and the shipped k=1063 witness supplies
an upper bound. Test remaining k with exact role, source-window, compact-mask
and physical-family constraints; a feasible cut alone is insufficient.
Changed words, pattern supports or chronologies require a new model.
The structured handoff is in `TASK.json`.

## Credit and scientific pins

Scientific base main `30f016dd79ee6a23c40d7dab44a9466c148c42dd`, priority revision 5;
selected-record SHA256 `bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`.
PR2979 supplies the construction and swap. Credit its author Marius-Paul Dumitrean,
Jeremy Kothe/PR2957/2966, Dugongue/2969, Mason Hale/2917, Jeremy Diviney/2908,
Yiyang Lu/2857, themilkman216, Tekalign, icekylinx and the retained owner/native
lineage. Original notices and detailed credit remain in `sources/`.
Ross Richardson, with substantial OpenAI Codex assistance and separate AI
mathematical checks; Apache-2.0. Earlier PR2974 checks a different frozen word
and does not establish this new inventory's placement.
