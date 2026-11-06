# P104 single-cut enlargements cannot fund one paid delivery per added coordinate

Applying [PR6064](https://github.com/CrocSwap/integer-mult-bounds/pull/6064)'s two-channels-per-added-coordinate opportunity to the selected P104 invoice requires a cheaper delivery contract. Under the explicit single-cut realization contract in [PROOF.md](PROOF.md), all additional binary helper splits earn less than **.773 per added coordinate**, even granting 18 LOCAL invocations and charging only one new rank-one call in the entire assembly. That call costs at least one. The route cannot retain selected kappa .003125804, throughout the unchanged BIT range up to .0034. No new kappa is claimed.

The theorem assumes at most two additional binary helper splits per added coordinate per LOCAL, ranks at most nine, unchanged other targets/paid jobs, and at least one new paid job per added coordinate globally. PR6064's capacity theorem alone does not establish that every supplier realization satisfies this target-count contract. Productive carriers, shared multi-coordinate transport, multi-cut reuse and changed prefixes/boundaries remain outside this exclusion.

The free-delivery alternative was also checked on the actual selected PR6030 word. The unmodified full-subspace census from [Matarener](https://github.com/Matarener)'s [PR5994](https://github.com/CrocSwap/integer-mult-bounds/pull/5994) already grants every role present at a chart. Both exact group and relaxed boundary supports have zero pure helper splits at all 8,734 evaluated cuts. An added eligible role already in one of those full banks cannot help within that pure split contract. This is an application of the predecessor's algorithm, with its credit retained.

## Significance for researchers

The sharp algebraic two-for-one gain in PR6064 is not enough to fund individually paid coordinate delivery in the current assembly. A useful successor should change the delivery/credit contract before growing the scalar fixture. Exact rational bounds cover the entire kappa interval; they do not use a grid that could miss the crossing behavior identified in [PR6049](https://github.com/CrocSwap/integer-mult-bounds/pull/6049).

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/dyadic-cut-delivery-budget
python3.12 -B scripts/check_research_commit.py --package research/dyadic-cut-delivery-budget
```

Normal and optimized commands use the standard library. They authenticate the selected result/word and frozen census, prove rational margin/derivative bounds, recompute both complete cut screens, and check positive, orthogonality and changed-contract controls. RESULT.json is compared with the full recomputation. The current-word census reuses the original engine and is not an independent engine audit or full selected/native/outer replay.

## Open next questions

Can one paid transport deliver at least two newly eligible coordinates, or can an existing paid trajectory provide a coordinate at no extra recursive cost? Start with one exact native chart/time/lifetime and the complete signed bill. The one-call-per-coordinate hypothesis would change; this certificate does not rule out that case.

Can a newly productive carrier or a changed multi-cut continuation earn enough additional credit? First give the independent target, unchanged dirty endpoints and all native/restoration fees. Those credits cannot be inferred from capacity.

## Credit and limitations

Prepared by [zxv](https://github.com/zxv), with substantial OpenAI Codex assistance. Credit [Ali Romman](https://github.com/aliromman)'s dyadic cut/P104 work, [Matarener](https://github.com/Matarener)'s source census, [DreamingOfClouds](https://github.com/DreamingOfClouds)'s selected PR6030 word and invoice, [Nick Petalas](https://github.com/petalas)'s related carrier-price [PR6033](https://github.com/CrocSwap/integer-mult-bounds/pull/6033), and their retained predecessors. The pending PR6064 statement is preserved byte-for-byte with its source head and SHA256; no unavailable foreign commit is required. Apache-2.0. No new native construction, supplier admission, global P104 barrier, selected change, independent human review, proof assistant or full multiplier is claimed. The five framework assumptions remain.
