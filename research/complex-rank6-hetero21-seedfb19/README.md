# Mixed rank-six blocks with two scalar children

**Scoped negative result.** The exact direct-sum construction is available at 28 strict source windows in each orientation of the selected gauge44 provider. A maximum disjoint schedule uses 13 blocks. Even with every added interface charge set to zero, that profile raises the local ceiling by less than 0.5%, below the task's 5% gate. No supplier or new \(\kappa\) is claimed.

## Construction

For 2-by-2 matrices \(A,B,C,D\) and scalars \(a,b,c,d\), the block-diagonal product gives

\[
\operatorname{diag}(A,B,a,b)\operatorname{diag}(C,D,c,d)
 =\operatorname{diag}(AC,BD,ac,bd).
\]

This fuses the child-rank multiset \((2,2,1,1)\) into one rank-six matrix-multiplication child. The paid rank mass stays six. The operation is exact over any associative coefficient ring. A nonzero off-diagonal input entry can create a cross-block output, so a realization must supply diagonal inputs and route the four outputs to the original destinations. The screen below grants those steps zero cost.

## Exact source schedule

The input is the member `candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz` in the selected replay archive. The archive SHA-256 is `f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`; the decompressed member SHA-256 is `241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a`. The selected-record SHA-256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

The verifier scans every raw, consecutive four-event window in both 24,767-event orientations. A window qualifies only when all four events are climbs, their ranks are exactly \(\{1,1,2,2\}\), and the four destination columns are distinct. Any scalar, adapter, centre, phase marker, or other climb between children breaks the window. It then computes a maximum disjoint interval schedule and independently checks its cardinality by dynamic programming.

| Orientation | Events | Qualifying windows | Maximum disjoint blocks |
|---|---:|---:|---:|
| Forward | 24,767 | 28 | 13 |
| Backward | 24,767 | 28 | 13 |

The complete qualifying windows and one maximum schedule per orientation are recorded in [CERTIFICATE.json](CERTIFICATE.json). Their event indices and rank order agree across orientations; the certificate retains each orientation's destination columns.

## Cost screen

The pinned baseline paid profile is `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` with rank mass 5,586. Thirteen fusions produce

```text
{1:2386, 2:392, 3:432, 4:142, 5:82, 6:13, 8:8}
```

The exact rational ceiling brackets from `ceiling.ceiling(profile, 73, 896, 9, 64)` on a \(10^{-12}\) grid are:

| Profile | Lower endpoint | Upper endpoint |
|---|---:|---:|
| Baseline | `1690054109/1000000000000` | `169005411/100000000000` |
| 13 ideal fusions | `212305837/125000000000` | `1698446697/1000000000000` |

The card's 5% screen is the baseline upper endpoint multiplied by \(21/20\), exactly `3549113631/2000000000000`. The 13-block candidate upper endpoint lies strictly below it. Relative to the baseline lower endpoint, its best-case upper-endpoint gain is exactly `8392588/1690054109`, less than one half percent.

The minimum number of zero-charge fusions needed to cross that 5% threshold is 126. With 125 blocks, the ceiling upper endpoint is `1774368109/1000000000000`, still below the target. With 126, the lower endpoint is `11094229/6250000000`, strictly above it. Each additional fusion lowers the local moment for \(0<a<1\), since \(\sum r_i^{1-a} > (\sum r_i)^{1-a}\) for positive ranks; therefore the ceiling is monotone in the fusion count, and the adjacent exact brackets identify the minimum.

This is the most favorable cost model: source access, operand copies, diagonal gather, output scatter, frame changes, interface transitions, hosting, precision, and arbitrary-dirty restoration are all free. The source-limited count of 13 misses the gate before any of these costs are charged. The result closes only this pinned, strict-contiguous schedule; it does not exclude a different word or a fully specified buffered interface.

## Relation to prior work

- [PR #1779](https://github.com/CrocSwap/integer-mult-bounds/pull/1779) batches sixteen rank-one children into rank sixteen. This package uses two rank-two and two rank-one children in one rank-six block.
- [PR #1866](https://github.com/CrocSwap/integer-mult-bounds/pull/1866) constructs the different tensor \((3,1,1,1)\to6\) and checks phase A, where its pinned stream has no rank-three climb. This package studies \((2,2,1,1)\to6\) and enumerates both complete selected orientations.
- Open [PR #1960](https://github.com/CrocSwap/integer-mult-bounds/pull/1960) optimizes consecutive blocks whose child ranks are two and three. This package includes rank-one children and the exact rank-six multiset above.
- The adjacent [claim on Discussion #1167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18926727) also restricts blocks to ranks two and three. This search includes rank-one children and the exact rank-six multiset above.
- The current claim and scope update for this complementary result are [Discussion #1167, comments 18929907 and 18930030](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18929907).

These results share the broad direct-sum idea. This package's added evidence is the distinct mixed-rank tensor shape and the full, source-pinned occurrence census for that shape in both selected traces.

## Reproduce

From the repository root, using the standard library and Python 3.12 or later:

```sh
python3 -B scripts/research_package.py --package research/complex-rank6-hetero21-seedfb19 --check-only
python3 -B research/complex-rank6-hetero21-seedfb19/verify.py
```

Expected output:

```text
PASS_PACKAGE_METADATA_AND_PINS
PASS_MIXED_RANK21_BLOCK_SCREEN windows=28 disjoint=13 target_minimum=126 profile_gain_below_0.5_percent
```

The replay checks the source pins, exact event profiles, every qualifying interval, maximum disjoint schedules, direct-sum identity, profile mass, rational ceiling thresholds, and negative controls for off-diagonal support, wrong ranks, duplicate destinations, and overlapping intervals. It reads frozen inputs and does not modify them.

## Open next questions

Can another selected word or a charged buffered schedule realize at least 126 useful \((2,2,1,1)\to6\) blocks? The current trace reaches only 13 groups under strict chronology. A first step is to derive operand-ready/use intervals and the dirty-output contract for one explicitly selected alternative, then price source access, copying, frames, hosting, precision, and restoration. The current event trace does not contain that multi-block lifetime map.

## Provenance and credit

The assignment was drawn from task `complex-rank-shape-decoder`, seed `fb19d5d7333247ee6fd2818087dc4509`, priority revision 3, exact base `f0c1cd4495674afcc81d618774949690b504217d`, and selected-record hash above. Current upstream main later advanced to `1d201395e037bd3fcb0175007fdcd0154878e613`; the package retains the assigned base and live source hashes.

Predecessor credit includes the selected provider lineage in PR #1094, rank-one batching in PR #1779, heterogeneous rank-six tensor construction in PR #1866, and the mixed rank-two/rank-three family in open PR #1960 and comment #18926727. Prepared by Cinna with substantial OpenAI Codex assistance in scope selection, source analysis, mathematical formulation, verifier and certificate construction, exact cost calculation, and writing. No independent human review is claimed. New material is Apache-2.0; frozen source archives and certificates are unchanged.
