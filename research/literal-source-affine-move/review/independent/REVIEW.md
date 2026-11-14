# Independent source and kernel review

## Decision

Pass for the scoped source identity, factor orientation, absolute phase, affine placement, and one-column original-frame kernel. The independent exact checker re-extracts the event and frames from the bundled canonical archive, then compares (K C^{\otimes3}K^{-1}) with the recipe's (M_L C^{\otimes3}M_R) across all 512 basis addresses and 4,096 nonzero Gaussian entries over denominator 8.

The checker rejects inverse orientation, reversed factor order, a wrong absolute phase, moving the offset before (G), and (C^\dagger). It is separate from the author compiler and literal emitter. The original workspace checker is preserved at `original/kernel_check.py`; the portable derivative is `kernel_check.py`. Their mathematical and negative-control functions have identical ASTs, checked by `check_derivative_ast.py`.

## Source binding and phase lift

The selected event is `[MOVE,727,3,470,false]`, frame3 is empty, and frame470 is `[75,137,265]`. The false field is ownership metadata, not inverse orientation. For the source chart (K=D_QP_G), the target operator is (K C^{\otimes3}K^{-1}), with (C=((1+i)I+(1-i)X)/2).

The runtime ordering is right phase → right (G) → right (X_b) → the three positive (C) leaves → left phase → left (G) → left (X_b). The selected right offset (b=5) is applied after (G), and its global phase is (i^2). `phase.py` initializes its four-state mode by scanning the (f) columns and incrementing by (a) on each; the scalar is therefore (i^{af}), while the input polynomial is summed independently over columns. The (f)-extension is tensor-product algebra plus code inspection, not an all-(f) graph run.

## Reproduction

From the repository root:

```sh
python3 -I -B review/independent/kernel_check.py implementation/RECIPE.json source/selected-final.json.gz
python3 -O -I -B review/independent/kernel_check.py implementation/RECIPE.json source/selected-final.json.gz
python3 -I -B review/independent/check_derivative_ast.py
python3 -O -I -B review/independent/check_derivative_ast.py
```

The bundle is authenticated by its Git blob SHA-1, compressed SHA-256, canonical-word SHA-256, and exact selected event/frame fields. The normal and optimized receipts are byte-identical.

The conditional complete-root prefix bridge review is in [`common-grid-prefix-bridge-review.md`](common-grid-prefix-bridge-review.md). It applies only to completed and committed numerical components acting on an injective view that retains complementary root coordinates; it does not establish that a selected producer supplies those premises.

## Limits

This is not an independent full literal-machine execution. Root's separate physical replay and proof review are in `../root/`. Neither review establishes that an actual caller meets the stated numerical prefix promises or pays for the source producer, bank transport, global ownership, cutoff, or nonleaf recurrence.
