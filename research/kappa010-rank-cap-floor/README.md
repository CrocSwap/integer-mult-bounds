# Exact rank-cap floor for a κ = 0.1 target

**Scoped negative budget result. No supplier or κ improvement is claimed.** The selected conditional result remains κ = 0.001672660197076918.

## Result

The retained transfer is `κ = a/(1+a)`, so κ = 1/10 corresponds to the primitive target `a = 1/9`. For any charged child of rank `r < m`, its moment contribution per unit rank mass at that target is

\[
\frac{(r/m)^{8/9}}{r}=m^{-8/9}r^{-1/9},
\]

which decreases with `r`. If all child ranks are at most `R`, total paid rank mass is `P`, and `w` families are served per call, every histogram therefore has moment at least

\[
F=\frac{P}{Rw}\left(\frac Rm\right)^{8/9}.
\]

Under the current coverage law `P = (m-u)w + c`, write `S=P/w=m-u+c/w`. Then `F^9 = S^9/(R m^8)`, so the strict comparison with one reduces to exact rational arithmetic. We also check the more favorable case `c=0`, which deletes the positive centre/copy mass entirely.

At the largest rank admitted by the current depth envelopes, even the centre-free, one-unpaid-coordinate lower bound exceeds one on both suppliers:

| Supplier | `m` | Current maximum `R` | Exact lower-bound comparison at `a=1/9` | Approx. `F` |
|---|---:|---:|---|---:|
| Bit | 64 | 53 (depth 4) | `63^9 > 53·64^8` | 1.005219793354 |
| Complex | 73 | 51 (depth 2) | `72^9 > 51·73^8` | 1.026397274382 |

Because this is already the cheapest histogram allowed by the aggregate law and cap, every actual histogram in that model costs at least this much. The moment increases with `a`, so neither supplier can support `a ≥ 1/9`, and hence neither can support κ > 0.1, while retaining one unpaid coordinate and these maximum child ranks. Keeping the existing centre charge only raises the floors to approximately 1.015407831801 (bit) and 1.035561535761 (complex).

The closest finite two-unpaid complex candidate in the local archive is the paired-plane identity fit: it reports `u=2`, centre charge `c=112`, `m=73`, `w=896/9`, and idle cap 51. At the 0.1 target its exact lower-bound parameter is `S=577/8`, with `(S^9)/(51·73^8)>1` and `F≈1.028179214095`. Thus even granting that local endpoint and then moving *all* mass to rank 51 cannot reach κ>0.1; the aggregate floor with `c=112` needs at least four unpaid coordinates. The paired-plane package itself reports only a favorable local ceiling `a≈0.00408`, and leaves routing, restoration, precision and the bit side open.

The exact threshold screens identify what could reopen the budget:

| Supplier | Current cap; centre kept | Minimum unpaid coordinates for the *ideal floor* to drop below 1 | With one unpaid coordinate, minimum rank after deleting centre | Halving-guard depth first allowing that rank |
|---|---|---:|---:|---:|
| Bit | `R=53`, `c=63` | 2 | 56 | 6 |
| Complex | `R=51`, `c=64` | 4 | 65 | 6 |

If the centre/copy charge is also removed, the minimum unpaid counts become 2 (bit) and 3 (complex). If it stays, the one-unpaid rank requirements rise to 61 and 70, requiring halving depths 15 and 17, respectively. Every rank and depth boundary is checked with exact integer or rational comparisons in [verify.py](verify.py).

These passing threshold rows are **necessary budget openings only**. They place all paid rank mass at the maximum rank, which is an intentionally generous relaxation and not a decodable local word. The deeper guard depths have not been shown to fit their row-coefficient invoices. No second unpaid coordinate, high-rank local consumer, physical endpoint, dirty-state restoration, bit/complex composition, or complete supplier has been constructed here. The result is scoped to the two current coverage identities and their rank/depth envelopes; a different outer algorithm remains open.

## Reproduction

```sh
python3.12 -I -B research/kappa010-rank-cap-floor/verify.py
python3.12 scripts/research_package.py --package research/kappa010-rank-cap-floor --check-only
python3.12 scripts/research_package.py --package research/kappa010-rank-cap-floor
```

The verifier uses only the standard library. It binds the selected record and the bit/complex budget receipts listed in [SOURCES.json](SOURCES.json). Its exact acceptance decision is the sign of `S^9/(R m^8)-1`; displayed decimal moments are orientation only.

## Open next questions

1. **Can two unpaid coordinates be carried through one complete dirty-input endpoint on the bit side?** This is the least aggregate change that opens the bit floor at `R=53`, but the actual word must preserve both coordinates and pay the consumer, frame, and restoration costs. First step: trace a named two-coordinate candidate through one full selected call. Blocker: the current endpoint contract and cost invoice have not been changed.
2. **Can the complex supplier leave four coordinates unpaid while retaining the current centre charge?** Four is the exact optimistic threshold at `R=51`; it does not follow from a local two-output anchor. First step: derive the replacement coverage identity for one full outer family, including delivery and restoration. Blocker: the anchor source columns are dirty and the centre consumer is still paid.
3. **Can the outer row invoice admit depth six, or a different construction with equivalent high-rank children?** Depth six is only the guard threshold with the centre removed and one unpaid coordinate. First step: evaluate the exact row coefficient and all non-rank charges at that depth. Blocker: no such invoice is currently available, and passing the guard alone does not construct a supplier.

## Scope, overlap and credit

This refines the `coverage-law-change` card for the user-set target κ > 0.1. It tests the cheapest possible aggregate moment under the pinned coverage laws before searching for a mechanism. It does not prove that changing coverage or depth is impossible, and it does not replace the card's complete-instance acceptance gate. Local overlap surfaced the earlier `kappa01-complex-target-screen`, several paired-plane coverage-law packages, and the concrete paired-plane identity fit; this result contributes the exact shared rank-cap floor and strict threshold table for the new 0.1 target.

The bit-side predecessor is Sagar Thakrar's `bit-revision3-levers-seed03`, building on DreamingOfClouds' PR589 / `format-limits`, eumemic's PR555, and the PR510 / PR442 template lineage. The complex predecessor is Douglas Colkitt's `complex-local-word-ceiling`, building on PR1012, the selected #1094 construction, and the credited frame/ownership chain. No predecessor artifacts were modified. The task began on `d8e0f83f00191df62174b641e9fff055c357f641`; canonical main was refreshed at `18aacb215fc3717b06be8ceb9fca62aeca0d3e99` (priority revision 6) on 2026-10-17. The only relevant guidance change adds a P104 precision-map pointer; the selected record and quantitative predecessor receipts are unchanged; the used κ conversion is unchanged.

A fresh overlap refresh on 2026-10-17 covered 259 open PRs and 1,866 discussions (complete pagination). It surfaced open PR #3093, which audits the paid terms of two fixed local profiles (#2979 and #3042) at the same target. That is complementary to this package's lower bound over every histogram admitted by the current aggregate coverage laws and rank caps; this package also computes the unpaid/rank thresholds for both suppliers. PRs #3064 and #3097 and Discussions #1163, #1166 and #1167 were also checked. The overlap helper reports possible overlap, not novelty; see the exact scopes and recheck before expanding the work.

Prepared by Codex with OpenAI assistance. New work is Apache-2.0.
