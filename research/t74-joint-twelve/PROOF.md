# Changed recovery contract and complete moment

The exact object is the two finite T74 words reconstructed by `generate.py`. The experiment uses a single explicit assignment, not a search over all assignments. Starting before PR2462's lowfour transformation is essential: applying the old lowfour patch first is a positive control reproducing its complete original words.

The new `(removed helper, recovered source, partner)` assignments are:

```
(696,33,49), (697,55,101), (698,74,83), (700,85,98),
(680,49,33), (681,83,74), (682,98,85), (684,101,55),
(688,68,4), (689,80,88), (690,88,80), (692,31,12).
```

The last eight are PR2696's assignment. For each of the pairs33/49,55/101,74/83,85/98, let `(x,y)` denote the values after their last original uses, in their shared frame. The two added gates are `x += y/2` followed by `y -= x`, hence the linear map is `(x+y/2, y/2-x)`. For the actual predecessor state these restore the two original source values. The proof of that word-specific premise is the full arbitrary-input exact symbolic replay, not a claim that this map is the identity on arbitrary `(x,y)`.

These restorations precede the new alias handoffs. Original operator IDs remain stable; twelve new chart transformations are appended. Removed-helper echoes are deleted only where they are target additions. For each new source, the generator computes the complete symbolic residual, transports its negative through precondition/compensation, and emits explicit initial correction gates and inverse source warps. Every residual must consist of a single new operator applied to its recovered source. Independent forward/dual propagation checks the resulting arbitrary-input identity, including dirty registers, and separately checks inverse cleanup.

All lifted targets have frame `[45]`; their offsets are14,21,37,41,43,47,52,78,99,104,106,110. None is a target read by any cut gate. Actual frame propagation therefore leaves all eight centre children rank8. This changes the old-four recovery/target paths fixed in PR2720; its obstruction is respected within its stated domain.

Apply the six PR2679 pre-life substitutions to the actual resulting state, refit the unique `515 += 563` gate (now B904), then alias653 into563. The complete generator checks semantic equality of both resulting words. The source-bound original checks and negative controls are rerun. No helper saving is inferred solely from nominal register labels.

The complete local profile is `{1:2366,2:646,3:297,4:120,5:26,8:8}`. Compared with the PR2733 composition it changes by `4*(H8-H7-H1)` per local word. The same415-helper inventory admits the explicit complete allocation; `independent_owners.py` checks276390 roles, strict temporal windows, every physical cell, family masks and all remainders. There are666 call equivalents, giving global delta `2664*(H8-H7-H1)` and rank mass4816512 unchanged.

At exponent `0<p<1`, strict subadditivity gives `8^p < 7^p+1`; thus this delta strictly decreases the paid moment throughout that interval. This comparison alone is not a complete outer bound: the package independently brackets the new moment root with rational arithmetic, rebinds the actual native words and physical stock, and reruns strict supplier admission and the modern outer release.

The rational endpoint bracket is `(0.001717141586348426338109,0.001717141586348426338110)`. The modern outer witness uses κ equal to the lower endpoint minus `10^-46+10^-70`. All required inherited checks must pass for the conditional bound; a smaller native moment alone would not suffice if another supplier bound became binding. The retained bit branch does not bind this witness. Universal realization and analytic obligations remain as listed in README and the pinned source review.
