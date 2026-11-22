# A complete normalized relay repair

All clocks are zero-based indices in the unmodified 39,600-instruction #8027
program. The following is a literal recipe, with every change anchored against
that program. The verifier checks all anchors, final owner locations, and all
630 input-to-output rows. Computation is over normalized scalar linear forms
on 630 independent binary inputs; it is not a physical field implementation.

1. Remove the ADDs at 8070 and 8071. Initialize owner 2327 at chart 531 at
   8073, add 2326 to it there at 8074, and send it 531 → 1 at 8075. These are
   the #8041 diagnostic edits and retain the old 2327 receipt.
2. At 10136 initialize 2862 at chart 326, add owner 2224 at 10137, and move it
   326 → 1 at 10138. Immediately after this MOVE add owner 2861 into 2862 at
   chart 1. This restores all 505 final chart-1 outputs; row 117 remains wrong.
3. Change 3152's MOVE at 11022 from 328 → 8 to 328 → 0. Omit the old 11025
   ADD into 3153 at chart 8. Immediately after its 11026 MOVE from 8 → 0 add
   3152 into 3153 at chart 0.
4. At 19845 initialize 3298 at chart 0, then ADD owners 117, 3152, and 3153
   into 3298 in that order. Omit the original instructions at 19846 through
   19951 inclusive. Omit original ADDs at 19954, 19958, 19959, 30079 and
   30080. Change the 39319 CLEAR of owner 3152 to chart 0. All other original
   instructions retain their order and operands. The complete expected old
   instruction and replacement list is [EXACT-EDITS.json](EXACT-EDITS.json).

The intermediate partial word fails only output 117. Dropping the ADD of 3152
at step 4 is a deliberate corruption and again fails exactly row 117. The full
word returns every native row and the independent reverse execution returns
its exact transpose. The five rational projector containments of all changed
endpoints are checked. This establishes the stated graph identity for every
input of the normalized binary model, not merely a finite sample of vectors.

The 2,803 paid scalar contacts remain. The complete one-word histogram changes
from 29 rank-five and 81 rank-six to 28 rank-five and 82 rank-six contacts;
all other rank counts agree. Thus the total rank rises by one. In particular,
3152's changed downward contact accounts for the extra rank unit. This word is
not a one-rank saving. Its powered cost must be evaluated in a complete caller.

All 3,433 private CLEAR values remain symbolically nonzero. Exactly five
records change relative to the native normalized trace:

| Owner | Old chart | New chart | Value changed |
|---|---:|---:|---|
| 2326 | 531 | 531 | yes |
| 3152 | 8 | 0 | no |
| 3298 | 7 | 7 | yes |
| 3299 | 330 | 330 | yes |
| 3300 | 531 | 531 | yes |

These are dirty records, not proven restorations. The replay does not prove the
physical register lifecycle, erasure, general-field adjoint, compiler, actual
36-call inventory, positive supplier, signed analytic application, or a new
κ. The full exact receipt, including the corruption's residual support and the
paid histograms, is [REPAIR.json](REPAIR.json).
