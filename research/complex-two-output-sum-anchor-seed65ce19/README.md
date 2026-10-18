# Two-output temporary sum anchor

**Outcome: partial local construction and conditional moment screen. No selected-provider placement or new \(\kappa\) is claimed.**

## Local bilinear map

Over \(\mathbb F_2\), take independent rank-one products

\[
P=x_0y_0,\qquad Q=x_1y_1,\qquad R_i=x_iy_i\quad(2\le i<q),
\]

and required outputs

\[
F_0=P,\qquad F_1=Q,\qquad F_i=P+Q+R_i\quad(2\le i<q).
\]

At entry, the two result coordinates \(A_0,A_1\) are clean; all other output accumulators are arbitrary. The forward schedule computes \(P\) into \(A_0\), computes \(Q\) into \(A_1\), XORs \(A_1\) into \(A_0\) to make the temporary sum \(P+Q\), and fans that sum into each other target before its private \(R_i\) child. A final XOR of \(A_1\) into \(A_0\) restores the required separate result \(A_0=P\). The second clean output remains \(A_1=Q\).

The exact invoice for each \(q\)-output block is \(q\) rank-one children and \(q\) affine additions, with no scratch helper, copies, or frame changes. Reversing the full schedule costs another \(q\) inverse children and \(q\) additions and restores both clean outputs and every arbitrary dirty accumulator. The sources are only read.

A straightforward joint rank-\(q\) schedule can keep both anchor outputs unchanged and fan each into every other target separately. It also uses \(q\) child calls, but needs \(2(q-2)\) fanout additions. The temporary shear has the same child count and uses \(q\) additions; at \(q=112\) it saves 108 affine additions. If each addition were charged as one rank-one-equivalent unit, that separate-fanout schedule would spend \(e=220\) per block and return the hypothetical profile to the selected baseline. The temporary-sum schedule spends \(e=112\) under that tariff and passes the exact 5% screen.

The output-slice matrices are

\[
E_{00},\quad E_{11},\quad E_{00}+E_{11}+E_{ii}\quad(2\le i<q).
\]

They are linearly independent because each \(E_{ii}\) for \(i\ge2\) occurs in only its own slice, after which \(E_{00}\) and \(E_{11}\) remain independent. Thus the tensor rank is at least \(q\); the displayed \(q\) products attain rank \(q\).

This output contract requires two separate clean result coordinates. Open PR #2213 instead stores a rank-three common sum in one clean output; the earlier rank-two common-sum handoff is [Discussion #1167 comment 18931234](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931234). This package studies a temporary shear between two required outputs, with the separate output values restored after fanout.

## Exact local cost and selected-profile screen

For \(q=112\), independently evaluating each output uses \(2+3(q-2)=332\) rank-one children. The joint block uses 112 children and the temporary shear uses 112 affine additions. Seven repeated independent groups fit within the selected profile's 2,412 rank-one children: \(7\cdot332=2324\). Eight do not: \(8\cdot332=2656\). If seven source-compatible groups in the selected word were currently evaluated independently, the block replacement would give this zero-tariff hypothetical profile:

```text
{1:872, 2:418, 3:432, 4:142, 5:82, 8:8}
```

Using the pinned exact interval ceiling at \(m=73\), 896 families, 9 stages and centre charge 64, the zero-tariff upper endpoint is `593544586351/250000000000000`, above the exact 5% target `35491136290869/20000000000000000`.

To price interface work in the same moment screen, let \(e\) be the total additional rank-one-equivalent charge per block. It includes the 112 affine additions and any other entry, source, frame, copy, hosting, precision or restoration costs if those are translated to this tariff. The exact boundary is:

| Added tariff per block | Profile rank-one count | Ceiling bracket | 5% gate |
|---:|---:|---:|---|
| 112 (one unit per affine addition) | 1,656 | `[1968447407841/1000000000000000, 984223703921/500000000000000]` | passes |
| 183 | 2,153 | `[355220358437/200000000000000, 888050896093/500000000000000]` | passes |
| 184 | 2,160 | `[886830512167/500000000000000, 354732204867/200000000000000]` | fails |
| 220 (ordinary separate-anchor fanout) | 2,412 | `[52814190909/31250000000000, 1690054109089/1000000000000000]` | fails |

At the 183 boundary, the exact target relaxation is below one; at 184 its lower endpoint is above one. The profile moment is monotone in this nonnegative rank-one-equivalent tariff, so no larger integer tariff passes. The 112 additions are an exact local cost. Their conversion to recursive-child equivalents is a what-if charge, not an asserted physical price. The reduction from 332 independent child calls to 112 is conditional on replacing repeated occurrences of this same map in the selected source word; the package does not locate those occurrences.

## Scope and limits

The verified family is \(3\le q\le112\); finite Boolean replay exhausts every source and dirty-target assignment for \(q=3,4,5\), while symbolic register propagation proves the forward map and inverse for all 110 widths. Four controls detect a dirty entry anchor, a missing final restoration shear, a missing target fanout and substitution of the second common product.

Seven repeated blocks, a matching common-source schedule and two clean output values at each block are hypothetical. The current provider trace does not enter this local construction. A selected realization would need to establish source occurrence/alignment, clean-output availability, chronological placement and complete outer supplier transfer. The moment screen does not charge or prove those selected-provider obligations, so no selected supplier or exponent change follows.

## Reproduction

From the repository root:

```sh
python3 -I -O -B research/complex-two-output-sum-anchor-seed65ce19/verify.py
python3 scripts/research_package.py --package research/complex-two-output-sum-anchor-seed65ce19 --check-only
python3.12 scripts/research_package.py --package research/complex-two-output-sum-anchor-seed65ce19
```

Expected direct result:

```text
PASS_TWO_OUTPUT_TEMPORARY_SUM_ANCHOR q=3..112 q112_children=112 q112_adds=112 blocks=7 tariff=183/184 local_only
```

`SOURCES.json` pins the base, selected record, catalogue, exact ceiling and one-output anchor predecessors. `RESULT.json` contains the symbolic, exhaustive, rank and moment receipts. `VERIFY.json` registers the bounded replay.

## Claim and overlap

Cycle 42 seed `65ce19d6105a0483da6b7dc247aaf0ae`, task `complex-new-helper-inventory`, scope key `bf91e52ded4a1c3ca05f`; exact base `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; priority revision 4. Claim: [Discussion #1167 comment 18937965](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18937965). The fresh overlap scan covered 471 open PRs and 932 Discussions with complete pagination and no warnings. Its nearest active construction is [PR #2213](https://github.com/CrocSwap/integer-mult-bounds/pull/2213), whose one-output rank-three common-sum interface has the different output contract described above.

## Open next questions

Can a pinned selected-provider subword supply seven disjoint 112-port instances with two clean required outputs and the shared operand pairs used here? A first step is to find one source-bound instance, list its two clean target registers and product-pair occurrences, then charge the chronological source, frame and caller interface against the 183-unit per-block ceiling. No such source search was performed in this cycle.

## Credit

Prepared by Cinna / commdata2338. Retain attribution to the one-output shared-product predecessors cited in `SOURCES.json` and to the active PR #2213 authors for the rank-three common-sum interface. New work is Apache-2.0. Substantial OpenAI Codex assistance in scope selection, exact map/inverse, rank proof, cost screen, verification, and exposition is disclosed in `TASK.json`; no independent human proof review is claimed.
