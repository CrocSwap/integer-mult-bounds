# A sharp frozen-fill limit for rank-seven inverse swaps

Status: independently checked finite result; public submission pending.
Scientific base `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority revision 6.
Sources: [PR2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979)
`be191346391661f4d35fc0d1508d0a6029572576`; necessary-bound predecessor
[PR2987](https://github.com/CrocSwap/integer-mult-bounds/pull/2987)
`02c3047a1e78e6e35e7573c12434ba26f6f9bd96`.

PR2979 changes the restored-helper boundaries and hence the ordered helper
inventory. Its favorable recursive cost still needs a legal chronological
owner fill. PR2987 proves `k>=473` necessary in its exact cost-neutral pattern
family, while the source witness uses `k=1063`. This package tests a concrete
route from that literal source fill to the necessary boundary.

**Result.** Among pairwise-disjoint direct inverse swaps on the source bins,
with all original call/helper identities fixed, the exact minimum is **k=940**.
The complete graph has 1,386 capacity16 `[8,8]` bins, 1,063 capacity32
`[7,7,9,9]` bins and 26,959 legal edges. A 123-edge matching and a 123-vertex cover
certify its exact maximum. A fully checked 123-swap journal attains 940. The 590
swaps required to reach 473 are impossible in this restricted model. Every
prefix of the certified journal also composes, giving a written construction
for every integer `940 <= k <= 1063` at unchanged cost; this is not 124
exhaustive full-geometry replays.

This is **not** a940 lower bound for arbitrary owner fills. Adaptive exchanges,
changed roles, vacancy relays and general grouped flows remain outside the
matching obstruction. Full chronological feasibility at473 remains a separate
question; the single bounded solver experiment is reported in
[CONSTRUCTION.md](CONSTRUCTION.md), with float solver status kept distinct from
an exact mathematical proof.

The independent checks reconstruct the full graph from exact source events and
role times; they do not trust an optimizer's edge list or infeasibility report.
They check source family lifetime separation, active data exclusions and the
journal's complete literal realization. The separate parent implementation
checks 135,864 T37 and 271,728 T74 helper roles, every ordered width, source window,
physical-family exclusion, capacity, disjoint integral coordinate masks and
compact prefixes. Both source order and provider dispatch are retained.

The complete paid T37 histogram remains
`{1:822840,2:235098,3:79734,4:35964,5:6858,8:2664,48:14095}`;
T74 is exactly twice it. Thus every recursive rank tariff, rather than just
rank mass or scalar operations, is unchanged. All 91 private buffers remain
charged. No better profile, kappa, fractional-cap attainment, supplier admission
or selected-frontier change is claimed.

Read [MATCHING-PROOF.md](MATCHING-PROOF.md) for the exact restricted model,
cover argument and cost ledger, [INDEPENDENT.md](INDEPENDENT.md) for the separate
source-to-flow and composition audit, and [SOURCES.json](SOURCES.json) for exact
source blobs/SHA256. Existing PR2993 frame and helper 249 native/private 953 audits
are complementary and are not repeated here.

## Reproduce

Standard library, no network, optimizer, native build or historical cold replay:

```sh
python3.12 scripts/research_package.py --package research/rank7-face-boundary-fill
python3.12 -I -B research/rank7-face-boundary-fill/verify.py \
  --candidate research/rank7-face-boundary-fill/candidate/repair/attained \
  --k 940 --check-result
python3.12 -I -B research/rank7-face-boundary-fill/independent.py
```

The registered checks authenticate frozen source bytes, complete literal
geometry, the graph/matching/cover/journal and targeted rejecting controls.
Optional candidate-generation commands and their separate dependencies are in
CONSTRUCTION.md. They are not part of the registered mathematical replay.

## Limits

These are finite exact computations and written scoped proofs, with independent
AI implementations/review. No independent human or formal-kernel proof is claimed.
The source ordered native widths/local profiles are premises. Arbitrary dirty
input native arithmetic, phase/restoration, complete physical stock and movement,
precision/prefix/tape, consumer/outer admission and all-size/compiler implications
remain separate. Namespace counts are not physical execution certificates.

## Open next questions

Can a general grouped chronological flow or a multi-bin vacancy relay realize
one of the remaining values `473 <= k <= 939` in the same exact family? First
pin the preserved model and inspect the
saturated cut routing, then construct all actual helper roles and check the full
invoice. The matching obstruction only closes the direct frozen-fill route.
Do not repeat the predecessor Hall count or this exact matching census. See the
structured next question in TASK.json. No new search round is launched here.

Credit Marius-Paul Dumitrean/2979 for the construction, face and original cut;
Ross Richardson/2987 for its independently checked necessary boundary; Yiyang Lu
for chronological flow/coloring; Jeremy Kothe, Dugongue, Mason Hale, Jeremy
Diviney, themilkman216, Tekalign, icekylinx and the full retained owner/native
lineage. See NOTICE and frozen source notices. New work by Ross Richardson,
with substantial OpenAI Codex GPT-6.1 Sol Max assistance, Apache-2.0.
