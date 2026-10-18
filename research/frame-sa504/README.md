# Frame-chain search on the 504-helper word: conditional κ = 0.001526158885117467

Prepared by **rohanarun** with Claude Opus 5.5 (Anthropic). Apache-2.0. This is a derivative of
[#531](https://github.com/CrocSwap/integer-mult-bounds/pull/531) by **icekylinx**
(its direct-delivery 504-helper word, owner map, controller and every checker are reused unchanged).
The only new mathematical object is a different assignment of operation frames.

## Result

| Quantity | #531 | This package |
|---|---:|---:|
| Conditional κ | 0.001517760977820331 | **0.001526158885117467** |
| Complex lower rate b | 0.001520068077832496458155 | **0.001528491606163040267702** |
| Cited #493 bit rate c | 0.001565442026981656908596 | same |
| Local profile | {1:2028,2:752,3:156,4:392,5:56,6:56,7:8} | **{1:2220,2:368,3:460,4:168,5:168,6:56,7:8}** |
| Helpers / widths / entrance rank | 504 / {8:152,9:352} / 152 | same |
| Owner map, live/physical, deficit | 36,288 roles, 7168/7682, 2560 | same |

κ is **+0.55331%** over #531 and **+3.96329%** over #532. The complex supplier still binds.

## What changed

#531 ran a single-node greedy pass (248 promotions in delivery body B, each to the meet of its successors, accepted on the linear
entropy fee). We instead search the whole lattice of **monotone frame lifts** of the constructor word:

* every A/B operation frame G must contain the frame the #531 constructor assigned to it (`F ⊆ G`);
* every register chain (start frame, A, centre/target barriers, B, final frame) must stay monotone;
* scalar operations, cut, centres and centre frames, helper start frames, target levels and final frames are fixed.

Any such assignment is reachable by #531's own coalescing lemma: lift nodes from last to first; each step has predecessors inside the
constructor frame and successors already at their final frames. A seeded local search (`code/frame_chain_search.py`, moves = one-vector
raises with upward closure and codimension-one lowers with downward closure, bounded below by constructor frames) minimises
Σ_r H_r · r((73/r)^b − 1), the moment-excess fee. A 40-sandbox run (25 min per seed, temperatures 0 to 0.004) converged to the same fee in 23 of 40 seeds; the selected word lifts 725 frames (versus 248 in #531). Rank mass is unchanged
(6240), so helper widths, the owner map and all 7,968 idle remainders are identical; only the local histogram changes. Spreading rank
mass across children of ranks 3 to 5 moves the moment root up.

## Verification (all #531 checkers, fresh on the new word)

```
python -B verify_fast.py --work /absolute/new/output/dir
```

New stages: rebuild the #531 constructor word from the frozen selection (no search), then `code/check_frame_lifts.py`
proves every changed frame is a lift of its constructor frame and every chain is monotone. Then the unchanged #531 stages run:
exact arbitrary-dirt forward and inverse-transpose scalar replay on all 728 columns with native frame chains, binding to the 112-port
controller, emission and independent audit of the actual whole-owner placement, fresh prefix and finite invoice (prefix 225 < 512 bits),
and two exact moment engines with all 47 strict outer inequalities.

The local evidence was regenerated with #531's code: `phases_delta.py` lowered **928 fresh phase edges** (1,994 reused) and checked every
tableau and global phase; `emit_local.py` emitted both orientations (22,937 events each); `audit_local.py` passed the independent emitted
replay with 13 controls rejected; `adapters_local.py` proved Lemma A for all 7 entrance frames with 5 mutations rejected. These receipts are in
`evidence/local/`. `evidence/FRAME-LIFTS.json` and `evidence/FRAME-SEARCH.json` record the lifts and the search objective.

## Scope

A finite conditional witness under the same inherited interfaces as #531 (all-size compiler, common-label/mutable-basis realisation,
normalised Lemma A, restored-row, precision/tape and analytic transfer). The #493 bit operator is cited, not rebuilt. The search is a
bounded heuristic, not an optimality claim. All credit for the 504-helper construction and its proofs belongs to #531 and its
ancestry listed in `NOTICE.md` and `SOURCES.json`; the parent README is preserved as `PR531-README.md`.
