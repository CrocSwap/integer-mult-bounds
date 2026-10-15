# Three-source clean cache across two output lines

**Exact local helper contract and conditional profile screen. No selected-supplier integration or new κ is claimed.**

This construction changes the one-source assumption in the earlier clean-cache result. A single clean helper stores the coded sum of three independent source lines, sends it to two distinct output registers, and is restored exactly. In the rank-interface model, the route replaces six direct rank-2 channels with two rank-3 channels (load and restore) and two rank-1 output channels. The small exact protocol passes its dirty-scratch and restore controls.

## Result

The selected word's pinned per-call profile is `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`. For each cache block, the profile change is

```text
rank 1: +2   (two output channels)
rank 2: -6   (six direct source-to-output channels)
rank 3: +2   (cache load and exact restore)
```

The route uses one additional clean helper coordinate, charged by increasing the per-call centre cost from 64 to 65. One helper is restored and reused sequentially. The added helper operations require eight scalar additions per block versus six in the direct route; all coefficients are `+1` or `-1`, source reads are unchanged, and no frame changes are needed. These linear gates are listed separately from recursive children, which are the quantities in the repository's exponent moment.

For `g=69`, the exact screened profile is `{1:2550, 2:4, 3:570, 4:142, 5:82, 8:8}` with local rank mass 5,310. The rank cap `floor(418/6)=69` is the complete profile-only domain examined here.

| Screen | Exact α bracket | Approximate α cap |
|---|---:|---:|
| Selected profile, centre 64 | `[1690054109/10^12, 169005411/10^11]` | 0.001690054110 |
| 69 cache blocks, centre 65 | `[1721731989/10^12, 172173199/10^11]` | 0.001721731990 |

The fully charged profile screen raises this fixed-word cap by about **1.8744%**. The corresponding balanced-transfer planning cap is `α/(1+α) ≈ 0.00171877`, still far below `1/99`. This is a profile-level conditional bound, not evidence that 69 compatible bundles exist in the selected #1094 event word. The new helper's hosting is charged as one extra centre coordinate; the selected supplier's actual array/frame itinerary and physical compiler do not yet provide this cache contract.

## Exact instance

Let `x1,x2,x3` be independent source values, `y1,y2` arbitrary output values, and `h=0` a clean helper. The desired endpoint is

```text
(x1,x2,x3,y1,y2,0)
  -> (x1,x2,x3, y1+x1+x2+x3, y2+x1+x2+x3, 0).
```

The direct route adds each `xi` to each output, using six additions. The cached route is

```text
h += x1; h += x2; h += x3
y1 += h; y2 += h
h -= x1; h -= x2; h -= x3
```

It uses eight additions and returns `h` to zero. The sources remain unchanged. Under the rank-interface contract, the source union has rank three, the coded cache/output line has rank one, and each direct source/output join has rank two. The two output registers are physically distinct but share the same one-dimensional interface frame.

`verify.py` checks the exact integer linear maps for one and 69 sequential blocks, the direct positive control, source immutability and zero scratch endpoints. Dirty initial scratch, an omitted restore and aliased outputs are adverse controls. It also recomputes the exact outward-rational profile ceilings from the pinned base calculator.

## Scope and open obligation

This is distinct from the one-source/two-output inequality in `research/complex-clean-cache-seed9df789`, which explicitly leaves multi-source coded scratch open. Open PR #1972 is a P104 dirty-restored gather/query channel with 72 arbitrary dirty helpers and COPY56; it uses a different boundary and does not establish this clean three-source contract. Active Discussion #2032 screens three-source nonconsecutive gathers into one destination in the selected k8 word by replacing gathered rank sums; this package instead constructs a clean coded line, fans it to two output registers, and exactly restores it. It does not search event chronology or claim selected-word occurrence.

No actual selected-word event bundle is identified. In particular, rank counts alone do not prove that the selected supplier has 69 sets of three source channels with matching two output interfaces and legal chronological placement. The result should be treated as a new local helper mechanism with a conditional profile screen, not as a replacement supplier, admitted construction, precision certificate or κ improvement. Integrating even one block into the pinned selected event word requires a source-level compatible window and an actual hosted endpoint proof.

## Pins and reproduction

- Assignment: seed `ab666b51c0ceafe204ff1721601c19b7`, track `complex-mechanisms`, task `complex-new-helper-inventory`, priority revision 3.
- Exact research base: `b5d138e63a10da21cc625088d1d953f962f05a8f`.
- Contribution PR: [#2045](https://github.com/CrocSwap/integer-mult-bounds/pull/2045), initial head `922a5489a91977ce403c32f72ecee7f49f885eb3`.
- Selected record: SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Selected assembly: `research/community-frontier1094-audit/ASSEMBLY.json`, SHA-256 `1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`.
- Selected source manifest: SHA-256 `79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b`.
- Review and reproduction: `docs/research/community-batch1099-review.md`; `make frontier1094-verify`.
- Predecessor: `research/complex-clean-cache-seed9df789/PROOF.md`.

Run from the repository root:

```sh
python3 -I -B research/complex-multisource-cache-seedab666b5/verify.py
python3 scripts/research_package.py --package research/complex-multisource-cache-seedab666b5 --check-only
python3.12 scripts/research_package.py --package research/complex-multisource-cache-seedab666b5
```

Expected exact replay marker begins `PASS_THREE_SOURCE_CACHE groups=69`.

## Attribution

Predecessor credit: Cinna Davis's one-source clean-cache proof. Adjacent work: Rohan Arun et al., PR #1972, on the P104 dirty-restored gather. Prepared by Cinna Davis with substantial OpenAI Codex assistance; no independent human review is claimed. Apache-2.0.

## Open next questions

1. **Can the 69 bundles be embedded in the pinned selected word?** A source-level event grouping and chronological endpoint proof is required; matching only the aggregate rank histogram is insufficient.
2. **Can the extra clean helper be hosted at centre charge 65 in the selected provider?** This needs concrete entry/exit frames, phase and precision checks, and global ownership replay.
