# Changed helper inventories screened against the packing ceiling

**Scoped obstruction and one screened lead. No new kappa; the selected record is
unchanged.** Card `complex-new-helper-inventory` (construction reading of method 1,
with the small completed instance and independent endpoint/rank-bill check of method 2).

## Question and outcome

The card asks whether a new local cost interface can change the
deficit-to-recursive-cost ratio beyond current packing. Two answers, both exact
within the pinned ceiling model (`research/complex-local-word-ceiling`, m = 73,
896 live families per nine-stage replica, centre charge 64, one unpaid coordinate
per live family):

1. **The deficit side is closed.** The per-call deficit `unpaid * w - centre = 320/9`
   is fixed by the coverage interface alone; it does not depend on the helper
   inventory or the paid profile (`ceiling.model()` computes it from `unpaid`,
   `families`, `stages`, `centre` only). Any new local cost interface can therefore
   move the ratio only through the recursive-cost side.
2. **The two recorded new-inventory contracts move it the wrong way.** R489
   ([PR 1004](https://github.com/CrocSwap/integer-mult-bounds/pull/1004), jeremykothe2)
   and R480 ([PR 1005](https://github.com/CrocSwap/integer-mult-bounds/pull/1005),
   jeremykothe2), the two changed-helper-inventory contracts the frozen-catalogue
   bound explicitly leaves open ([heterogeneous-owner-assembly](../heterogeneous-owner-assembly/README.md)),
   have optimistic exact moments strictly below the selected word's packing ceiling.
   Even ideal rank-51 idle packing does not rescue either. **Exact obstruction,
   smallest falsifying instance first: R480.**

One comparison lead survives the screen: the same-inventory U10 profile direction
([PR 987](https://github.com/CrocSwap/integer-mult-bounds/pull/987), rohanarun) strictly
beats the ceiling along its mass-neutral family, but only by up to **+0.082%**
relative at the nonnegativity boundary. That is not a helper-inventory change, no
word realizing it is known here, and it is two orders of magnitude below the
target scale and inside the +0.87% packing headroom.

## Exact screens (grid 1e-12 certified brackets)

| Contract | Per-call profile (rank: children) | Ceiling bracket | Verdict vs selected |
|---|---|---|---|
| selected word | 1:2412, 2:418, 3:432, 4:142, 5:82, 8:8 | 0.001690054109 to 0.001690054110 | baseline |
| R489 (PR1004) | 1:2463, 2:388, 3:429, 4:166, 5:70, 8:8 | 0.001683186050 to 0.001683186051 | fails, at least 0.406% below |
| R480 (PR1005) | 1:2412, 2:418, 3:418, 4:170, 5:68, 8:8 | 0.001689769942 to 0.001689769943 | fails, at least 0.0168% below |
| U10 direction t = 1 | 1:2412, 2:418, 3:436, 4:134, 5:86, 8:8 | 0.001690135316 to 0.001690135317 | beats by at least 0.0048% |
| U10 family argmax t = 17 | 1:2412, 2:418, 3:500, 4:6, 5:150, 8:8 | 0.001691435705 to 0.001691435706 | beats by at least 0.0817% |

The screen margin is the strict one of the acceptance gate: a candidate beats only
if its entire certified bracket lies above the selected bracket. Every verdict
above is bracket-separated, not a float comparison. The R480 row is the smallest
falsifying instance: it keeps the selected local mass (5,586) and changes only the
helper width inventory (56, 32, 30, 122, 240 at widths 4, 5, 7, 8, 9) and the
children split, and it already fails.

The U10 family is `selected + t * (3:+4, 4:-8, 5:+4)` at constant local mass
5,586, screened for every integer t from -4 to 17 (17 is the last t with a
nonnegative rank-4 count). The ceiling rises monotonically in t; the movement
reduces rank-4 mass toward ranks 3 and 5. R480 sits at the opposite side of this
direction, which is exactly where its loss comes from.

## Rank bill and deficit (method 2 instance, independently verified)

For every screened contract the per-call bill is closed exactly:

- coverage identity: total delivered mass `72 * (896/9) + 64 = 7232`;
- paid local mass + ideal idle mass = 7,232 (R489: 5,604 + 1,628; others: 5,586 + 1,646);
- capacity minus delivered: `73 * (896/9) - 7232 = 320/9`, the invariant deficit.

`verify.py` recomputes the bill on two paths (the exact `Fraction` arithmetic and
an independent `math.log`/`math.exp` implementation of the relaxation moment) and
checks that the independent float root lands inside each exact bracket. This is
the completed per-call instance of method 2: the endpoint and rank bill of each
contract are independently verified. The arbitrary-dirty scalar identity of the
R489/R480 words themselves is inherited from their own packages and was not
replayed here.

## What is and is not established

Established, within the pinned ceiling model and its stated scope (one fixed
template, coverage law and halving guard; fractional ideal idle packing allowed):

- deficit invariance across all screened inventories, exactly 320/9 per call;
- the strict exclusion of R489 and R480 from beating the selected packing ceiling;
- the exact U10 family table and its argmax at the boundary t = 17.

Not established: no word realizing any U10-family profile is constructed; no
physical owner map, hosting, precision or outer invoice is replayed; no supplier
admission or kappa change is claimed; and nothing here bounds helper inventories
outside the two screened contracts. Passing an optimistic relaxation is not
acceptance, and expanding into a construction round needs the family-level budget
and obligation gate in [research-family-status.md](../../docs/research/research-family-status.md).

## Scope and coordination

Drawn card `complex-new-helper-inventory` (chooser seed
`e64193c0fde4d77694e6b2ad660b009a`, track complex-mechanisms, priority revision 6,
catalogue SHA-256 `47b42433f5a85809a3aadd29c2c339da2c6ed728e4f7762df6b88bccb7874cf0`),
scope **unchanged**; `actual_scope` equals the card question byte-for-byte in
[TASK.json](TASK.json). Pair-collision pass over discussions
[#1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166) and
[#1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317) found no
live claim on this card's object: philippeVV's helper-endpoint inventory claim
(expires 2026-10-14 05:53 UTC) was released with negative results in
[k8-inventory-screens](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18914656),
and navinor's queue-ceiling census claim (expires about 2026-10-14 07:00 UTC) is
expired; neither covers the moment screens run here. No advance CLAIM was posted
(this bounded session finished in one run). Prior readings of this card cover
helper terminal frames ([selected-k8-unrestricted-ends](../selected-k8-unrestricted-ends/README.md),
PR1995/PR2013); this package takes the changed-inventory axis those readings
explicitly leave open.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -I -B research/helper-inventory-moment-seede64193c0/verify.py
python3 scripts/research_package.py --package research/helper-inventory-moment-seede64193c0 --check-only
```

Expected marker: `PASS_HELPER_INVENTORY_MOMENT_SCREEN`. `verify.py --write`
regenerates `RESULT.json`; a normal run requires the committed receipt to match
byte-for-byte (written with newline `"\n"`). When git history is available the
verifier also cross-checks the embedded R489/R480 profile and inventory constants
against the pinned SPEC blobs at PR1005 head
`779e80aef469bc3a28b19f1adde199871a9a22e3` and fails on any drift. Controls:
one extra rank-1 child strictly lowers the selected ceiling; an over-mass profile
and an idle rank cap of 52 are rejected for the recorded reasons.

## Open next questions

1. **Realize a U10-family direction as a word.** The family is the only screened
   beating direction here. First step: pin the t = 1 profile and attempt one
   scalar-word construction with the fixed entrances and cleanup contract, then
   screen its complete charged bill. Blocker: no priced changed-word contract;
   the family expansion gate applies.
2. **Screen the rest of the new-inventory class.** R489 and R480 fail, but the
   catalogue bound leaves every changed inventory open. First step: extract each
   outside-catalogue width inventory with byte-pinned SPEC vectors and run the
   same strict-bracket screen. Blocker: per-contract profile extraction.

## Credit

The packing-ceiling model and the selected word's profile are
[complex-local-word-ceiling](../complex-local-word-ceiling/README.md)
(PR 1240, Mister-Meeseeks / Doug Colkitt), on the coverage identity of
[PR 1012](https://github.com/CrocSwap/integer-mult-bounds/pull/1012) (thakrarsagar).
The changed-inventory vectors are the mutable-leaver contracts of
[PR 1004](https://github.com/CrocSwap/integer-mult-bounds/pull/1004) and
[PR 1005](https://github.com/CrocSwap/integer-mult-bounds/pull/1005) (jeremykothe2),
byte-pinned from their SPEC blobs and cross-checked against the
[heterogeneous-owner-assembly](../heterogeneous-owner-assembly/README.md) controls
(Ali Romman). The comparison direction is the U10 delta of
[PR 987](https://github.com/CrocSwap/integer-mult-bounds/pull/987) (rohanarun).
Prior card reading: [selected-k8-unrestricted-ends](../selected-k8-unrestricted-ends/README.md)
(Gareth Davidson). Prepared by Aaron Wang with help from opencode; substantial AI
assistance, no independent human review claimed. Apache-2.0.
