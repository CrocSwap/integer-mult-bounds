# B171 (reduced): S1 lemma on blocks (0,1,*), Lawler on #799. VERDICT: Lawler PROVEN on #799 (268/268); S1 lemma does NOT extend to (0,1,*) (not tight). ship=false, no kappa claim. No heavy jobs used (all runs <2 min, single process).
Tools: scan01.py/scan01b.py (B167 plane-partner scan on blocks (0,1,*), reuse B98c gate.py loader), lawler799.py (B172 certificate on any word; copies found by first row-fill of S3/S4 ledger ids), pair799.py (two-visit conflicts).
## 1. B167 lemma on blocks (0,1,2,3),(0,1,4,5),(0,1,6,7) (16 scratch each; 104 distinct columns, 56 per block, rank-8 vectors, all 104 cols are start-dim-1 line registers)
- Same block anatomy as the 11 S1 blocks: per block 1 register with |support|=56 (whole bound), 7 PLANE stoppers (|S|=4, hull=bound=4 cols; 21 stoppers, 21 DISTINCT planes), 4 scratch with |B|=8, 4 pair-bound.
- BUT the lemma gives no register lower bound: line registers (cols) have end-of-A bounds |B| 48 (21 cols) / 56 (18 cols), so they can serve as plane couriers. Max matching stopper->partner = 21/21 with cols alone; scratch-only partners 15/21 (5 wide scratch per block vs 7 stoppers). Hall bound is slack, not tight => NO certificate that the 48 scratch registers are needed. (PROVEN: the counting bound is not binding here; the 16-scratch minimality for (0,1,*) is UNPROVEN, not refuted. Whether line registers can really courier (their own row/bound duties, the 3-block sharing) is not modelled.)
## 2. Lawler (B172) on #799 canonical word (cards/B147/.../x4/local/CANONICAL-WORD.json.gz; 5687 add ops)
- Copies identified WITHOUT tags: first op that fills an empty helper row from a nonempty one, restricted to ledger S3/S4 ids: 156 S3 + 112 S4 = 268 (all coefficient 1, all in B part).
- Visits = all later adds touching a or b; g = partner pre-frame lower bound (target-side replay from start frames, centre joins ignored = weaker, sound), cap = perp(ports of targets reached, a,b sinks), base = a's frame at copy. NO precedence (relaxation).
- RESULT: 268/268 FAIL (S3 156/156, S4 112/112); each chain alone passes 268/268 (caps not over-tight); every copy already has a TWO-visit conflict (pair799.py). So no copy can be merged by any reorder. PROVEN [scope: #799 op multiset fixed, value-forced monotone lower-bound frames, caps = reached-target ports]. Identical outcome to #656 (B172).
- Not done: #870 (not local), precedence-aware variant (unneeded), multiset-changing merges.
## 3. Helper classes NOT covered by either proof (the unproven slack)
- S1 scratch of blocks (0,1,*): 48 regs (incl. 3 centres 224,240,256). B167 lemma slack (above).
- S3/S4 (268) vs multiset-CHANGING merges (undo/redo ADD, B169-style holder merges: 16 holders 484..569, 8 entering slots 450..457): outside the Lawler scope.
- 12 non-helper bridge registers 716..727 (start frames 423-427, 8-support fill in B): no proof either way.
- cut ops (224 cut entries) and 8 centre copies/centre frames: not examined.
- The 11 S1 blocks (176 scratch) are covered only for fixed interface (shipped bounds + end-of-A rows), not under interface change.
- S1 B167 lemma, Lawler S3/S4 and the frame-lower-bound g are not independently audited by a second reader.
