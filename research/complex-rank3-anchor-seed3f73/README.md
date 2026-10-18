# Rank-three common-sum output anchor

**Exact local construction and conditional moment screen. No tensor-rank optimality, selected-provider placement, or new κ is claimed.**

## Construction

For `q >= 2`, use `q+2` independent rank-one products. The clean anchor starts at zero and receives

`F0 = x0*y0 + x1*y1 + x2*y2`.

For each `1 <= i < q`, a dirty output accumulator `Ai` receives its own product and then the anchor:

`Ai_out = Ai_in + F0 + x_(i+2)*y_(i+2)`.

The reversible schedule computes the three anchor products once, computes one unique product for each non-anchor output, then performs `q-1` affine fanout additions from `A0`. The reverse first undoes the fanouts, removes the unique products, and clears the anchor products in reverse order. It uses no extra helper. A formal GF(2) polynomial replay covers every width `q=2..112`; an exhaustive `q=4` replay checks all 32,768 input/dirty-output states. The verifier also rejects an omitted anchor product, omitted fanout, and dirty anchor. “Three-product” describes the anchor sum; this package does not prove a minimum tensor rank for the full q-output map.

The parent rank-two anchor uses `q+1` products per block and saves 222 rank-one products at `q=112`. This rank-three anchor uses `q+2=114` products, versus `4q-1=447` when all four terms of every output are evaluated separately. It saves 333 products per block. Two disjoint blocks save 666 products and use 228 products plus 222 affine fanout additions.

## Conditional selected-profile screen

The exact source-bound profile is `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`. Replacing 666 rank-one children with the rank-three anchor gives `{1:1746, 2:418, 3:432, 4:142, 5:82, 8:8}`. With the pinned ceiling model (`m=73`, 896 families, 9 stages, centre charge 64, idle cap 51), the ceiling bracket changes from

- baseline: `[1690054109/10^12, 169005411/10^11]`;
- rank-three two-block profile: `[965291637/500000000000, 77223331/40000000000]`.

The interval ratio is about `1.1423`, clearing the 5% screen under the relaxation. Adding up to 411 rank-one-equivalent child charges still passes the exact 5% comparison; 412 fail. This allowance is only for additional recursive child charges. The 222 affine fanout additions are a separate operation line and are not silently converted into child charges.

## Limits

This is a local construction with a conditional profile screen. It is not mapped into the selected gauge44 provider. A provider mapping must bind the source products to the selected program and add its actual source, helper, frame, copy, hosting, precision, restoration, and interface costs. The selected source, theorem assumptions and frontier are unchanged. No `κ` claim is made.

The selected record is resolved through `certificates/selected-result.json`: review `docs/research/community-batch1099-review.md`, source manifest `research/community-frontier1094-audit/SELECTED-SOURCE.json`, certificate `research/community-frontier1094-audit/ASSEMBLY.json`, reproduction command `make frontier1094-verify`. The package pins these inputs and the exact ceiling engine in [SOURCES.json](SOURCES.json).

## Reproduce

From the repository root:

```sh
python3 -I -B research/complex-rank3-anchor-seed3f73/verify.py
python3 scripts/research_package.py --package research/complex-rank3-anchor-seed3f73 --check-only
```

Expected direct verifier output:

```text
PASS_RANK3_SUM_ANCHOR q=2..112 products=114 fanouts=111 two_blocks_saved=666 cap_extra=411/412 local_only
```

The generic registered replay uses Python 3.12. Local direct verification in this session uses Python 3.14.7.

## Open next questions

Can two disjoint `q=112` rank-three anchor blocks be placed in the selected gauge44 source program with exact input/output frames and a complete invoice that fits the 411-child-equivalent headroom? This matters because the local profile only affects the selected bound after that source map is realized. The first step is to bind candidate anchor products and target entry states to the pinned `CLIFFORD-RECIPES.json` and local word, then prove all 222 fanouts and dirty-source restoration. The blocker is the missing source-to-target map; this package does not search transformed provider frames.

## Predecessors and credit

The local rank-two common-sum anchor is in the finding at [Discussion #1167, comment 18931234](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931234), from commit `dc29def3`; it proves the analogous two-product contract and ideal profile, but does not place it in the selected provider. PR1094 supplies the selected construction. The nearby non-coordinate rectangle-plane rail in Discussion #1167, comment 18930746, changes helper frames and is a different mechanism.

Prepared by Cinna Davis (1337isnot1337) with substantial OpenAI Codex assistance in scope selection, exact derivation, verifier implementation, cost screening and packaging. Apache-2.0.

Maintainer integration note: the originating task catalogue is historical provenance. `task-catalog-snapshot.json` retains the exact originally pinned bytes, checked by the verifier; the current live priorities may evolve independently. Mathematical source pins are unchanged.
