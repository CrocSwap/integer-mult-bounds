# Independent integer-root check of the nine frozen packing ceilings

All nine packing-relaxation brackets in Douglas Colkitt's
[PR1264 census](../complex-queue-ceiling-census/README.md) pass a separately
written integer-root calculation. The fourteen source profiles and idle
histograms reproduce the census exactly. No numerical discrepancy was found.
**Independent finite verification; no new construction or kappa.**

Revision 3 uses this census to assess the remaining benefit of packing. Both
the census and its [PR1240 predecessor](../complex-local-word-ceiling/README.md)
use the same atanh/Taylor engine. This package adds a different numerical
method and an offline check of the original source extraction, including the
mixed-provider rational counts. It imports no predecessor executable.

## Result and exact scope

The table gives each certified upper endpoint `a_hi`; its lower endpoint is
exactly `a_hi - 10^-15`. At both 96/192 and 128/256 exponent/fractional bits,
the outward rational intervals prove

`relax(a_hi - 10^-15) < 1 < relax(a_hi)`.

| Profile | Exact `a_hi` | Frozen claims |
|---|---:|---|
| W1 | 0.001690166683079 | #1124, #1130 |
| W4 | 0.001690126076663 | #1152 |
| W5 | 0.001690094712065 | #1157 |
| W2, selected at the base | 0.001690054109089 | #1129, #1131 |
| W8 | 0.001687160482514 | #1195 |
| W9 | 0.001687102547672 | #1196, #1204, #1225 |
| W3 | 0.001687062088401 | #1148 |
| W6 | 0.001686657172581 | #1178 |
| W7, mixed providers | 0.001686519526354 | #1193, #1239 |

Thus the original common strict planning cap is corroborated:

`kappa < 1690166683079 / 1001690166683079 < 0.001687314840`.

This is the frozen fourteen-claim domain of PR1264, **not the current open PR
queue**. Profile labels identify aggregate paid profiles, not circuit
identities. The cap applies only under the fixed coverage law, width 73,
896/9 live families per call, centre charge 64, and rank-51 idle relaxation.
The conversion to kappa retains the predecessor's balanced-transfer premise.
A relaxation root is not an attainable supplier optimum.

The selected PR1094 assembly and independent receipt separately reproduce W2
with 144 calls, 14,336 live families, and 1,646 idle-rank units per call. Their
reported endpoint is below the W2 bracket. This does not re-execute that
assembly or re-certify its endpoint moment.

The committed [RESULT.json](RESULT.json) contains every exact rational moment
interval at both precisions, all profile memberships, per-claim count evidence,
14 semantic controls, 2,640 exact algebraic power comparisons, and 72 exact
zero-saving child costs. [test_verify.py](test_verify.py) adds 13 test groups
covering arithmetic corruption, source drift, missing inputs, omitted cases,
wrong brackets, mixed-count rounding, and optimized read-only relocation.

## Source extraction and its boundary

[SOURCES.json](SOURCES.json) pins the four immutable main-branch inputs and the
historical task/selection provenance at
`ee055dc44815497927ef618fc985b93c2dcbda2a`. [UPSTREAM.json](UPSTREAM.json) binds
21 original JSON blobs to each frozen head/path pair in the census. They were
retrieved through GitHub's Contents API at those exact heads; each response's
Git blob ID and raw bytes were checked. The compressed copies in `inputs/`
retain the exact original JSON bytes. Offline replay checks both SHA256 and
Git blob hashes of the **decompressed payload**, not the gzip container.

The new extractor uses explicit fields and JSON paths, not the predecessor's
recursive matching routine. Every call count is independently read from
`calls`, `complete_invocations`, or the sum of `provider_counts`. Ten claims
also provide an explicit `live` field. The cited receipts for **#1124, #1130,
#1178 and #1195 omit it**; for those four, `W = 896 N / 9` remains an explicit
template premise, now distinguished in the receipt. This audit does not claim
to have recovered their physical live stock from operations.

For each claim the checker requires nonnegative integer histograms, an idle
subprofile with ranks at most 51, `9 W = 896 N`, and
`sum_r r H_r = 72 W + 64 N`. It then computes each local count as
`L_r = (H_r - I_r) / N` using exact fractions and compares the complete census
grouping. Titles and recorded endpoints are checked against the original
source fields, not used as numerical evidence of admission.

W7's exact counts are
`{1:783550/333, 2:169496/333, 3:137362/333, 4:42458/333, 5:82, 8:8}`.
The predecessor's README displays rounded values, while its actual calculation
correctly retains these fractions. Substituting the display values changes
the lower-endpoint sign; this is a useful corruption control, **not a defect
in the predecessor's certificate**.

## Enclosure and ceiling arguments

Let `S = 2^P` and `x = m/r >= 1`. The initial integer bounds are
`floor(S x) <= S x <= ceil(S x)`. If `l/S <= y <= u/S`, then

`isqrt(l S)/S <= sqrt(y) <= ceil_sqrt(u S)/S`.

Squaring both nonnegative sides proves each inequality. Repeating this gives
outward bounds for `x^(1/2^j)`. For a binary exponent `k/2^B`, multiply the
root factors selected by the bits of `k`, rounding every scaled product down
for the lower bound and up for the upper bound. Positivity preserves the
enclosure at every multiplication. For rational `a`, set
`k_lo = floor(2^B a)` and `k_hi = ceil(2^B a)`. Since `x >= 1`, exponent
monotonicity sandwiches `x^a` between those two dyadic powers. Multiplication
by the exact positive rational `r/m` encloses `(r/m)^(1-a)`.

The arithmetic oracle in the controls is different: for rational `a = p/q`,
it checks `lo^q <= x^p <= hi^q` by direct exact integer powers. This catches
root rounding, bit-order and exponent-bracketing errors without using another
root or transcendental implementation. Equality and intervals crossing one
produce an explicit unresolved error, never a successful endpoint decision.

For the inherited ceiling theorem, write `w = 896/9`. The coverage law gives
total rank mass `72 w + 64 = 7232` per call. Subtract the local mass to obtain
idle mass `M`. At `a >= 0`, a rank-r child's cost per rank unit is
`m^(a-1) r^(-a)`, nonincreasing in `r`. Therefore every idle histogram with
ranks at most 51 costs at least `(M/51) (51/73)^(1-a)`. The guard admits 51
and excludes 52 because `2*51^2 < 73^2 < 2*52^2`. The resulting lower bound is

`relax(a) = [sum_r L_r (r/73)^(1-a) + (M/51)(51/73)^(1-a)] / w`.

All terms have positive bases below one and nonnegative counts, so the
relaxation is strictly increasing for these profiles. Its two certified signs
bracket its unique root. At or above the upper endpoint, even this favorable
relaxation exceeds one; adding nonnegative implementation charges cannot
repair that inequality. The theorem and model are credited to PR1240/PR1012;
the new result is their independent numerical and extraction corroboration.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/independent-queue-ceilings
```

This validates provenance, runs the complete receipt check and the corruption
tests. The generic hook uses the four explicitly declared external inputs.
The direct check also works without Git or network when those four files and
this package are copied with their repository-relative paths:

```sh
python3.12 -I -O -B research/independent-queue-ceilings/verify.py
```

Expected output begins `PASS_INDEPENDENT_QUEUE_CEILINGS` and reports 14 claims,
9 profiles, 18 endpoint signs, 18 refined signs, 14 semantic controls and 21
source blobs. `verify.py --write` explicitly regenerates only this package's
receipt. Ordinary replay is read-only. Full Git history is needed by the
registered wrapper's provenance checks.

Unrun obligations: operation/frame or owner reconstruction, native supplier
admission, chronological hosting, physical live-stock derivation, exceptional
charges for actual suppliers, bootstrap/outer feasibility, precision/tape,
all-size and analytic interfaces, and a full Lean multiplication theorem.

## Open next questions

Can the four template-derived live counts be bound to explicit physical
inventories in their original packages? This would remove a source-extraction
premise, not improve kappa. A first step is to locate each pinned template or
owner inventory and recount active data families while retaining its role
distinction. Those additional inputs and the physical reconstruction are
outside this package. The structured question is in [TASK.json](TASK.json).

## Credit and overlap

Douglas Colkitt's PR1240 supplies the ceiling theorem and original numerical
engine; PR1264 supplies the frozen census and all nine reported brackets.
PR1012 supplies the coverage identity. The fourteen frozen constructions are
credited to jeremykothe2 (#1124/#1130), aliromman (#1129), chafreaky
(#1131/#1152/#1196), tomdif (#1148), rohanarun (#1157/#1178/#1225),
jeremydiviney (#1193), mdumitrean (#1195), and GamingPuzzled (#1204/#1239).
This package asserts no construction or discovery credit.
The selected lineage includes Rohan Arun, Jeremy Kothe and Hao Yan, with full
attribution in the selected review.

Integer-root endpoint verification already appears in arkfx's PR706 and
Arham-Tahir64's PR1577; this implementation was written separately.
Arham-Tahir64's PR1605 independently checks the
selected baseline bracket as part of its rank-one block-budget study. This
package's additional domain is the complete nine-profile census and its
twenty-one original source blobs. Discussion #1606 changes port count and
Discussion #1328 changes the coverage law; neither is attempted here.

Started from current main at the exact base above, using task `independent-moment`
and nonce `488b8bb97d866ded02e80a47a4e9d7e1`. Coordination:
[Discussion #1620](https://github.com/CrocSwap/integer-mult-bounds/discussions/1620).
Search coverage and limits are recorded in TASK.json; a clear search result is
not a novelty certificate.

Prepared by Hanson Sun (bbMisk) with substantial OpenAI Codex assistance in
scope selection, implementation, mathematical explanation, testing and writing.
New material and copied repository inputs retain Apache-2.0.
