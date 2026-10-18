# B247 COLD-SLOT LEDGER - VERDICT: NO-GO for the card's target (coded pairs / S4 cold M reads): 0/112 targets can host a 2nd T pair, at ANY schedule. No word built, no SHIP CANDIDATE, nothing pushed.
SIDE FINDING for B245 (not my lane, flagged): at gauge-forward, all 16 S3 sel x4 copies delete (NH 480->464) with STAG=1 + lazy widening of ALL explicit-frame ops (GLAZY=1, gates cgx_x.py): scalar identity assert passes, 0 y-cap violations. Rough price on w1018 terms +1.3% (H16 mass credit) .. +2.0% (H48), -0.35% (H1 credit). NOT chained/audited; the G6 "partner pollution" failure disappears once partner ops widen (WIDEN list: 32 events, 3->5, 4 per consumer block).
## Q(A) exchange rate "own row warm" (cold-slot rate)
- One cold-first packet read in a block (CF=0, STAG=1, GLAZY=1): own rows of that block's 8 targets are deferred behind it; only ONE explicit event per consumer block widens (3 -> 5), not one per target. Profile vs base: H1 -6, H2 -9, H3 +3, H4 +1, H5 +1, H6 -1, H7 +1 (helper deleted, NH 479). Mapped price on w1018 (H6/H7 -> H1, mass to idle): +0.05% (H1), +0.12% (H16), +0.14% (H48).
- Isolated widen cost: a lone 3->5 event = -0.02..-0.04% (H16/H48 credit), ~0 at H1 credit. Per held block (4 events, all 8 targets) about -0.025% at H48 = well below the card's 3 x 0.07% bar. So the PRICE of a cold hold is cheap (~0.006% per event). It is not the blocker.
- Plain deferral (own row after the block's late events, POST=1) is frame-illegal: r_ at dim 3 is not inside hyper(P_t) (POSTFAIL 16 and 72). The only legal deferral is behind another cold read, which then widens r_.
## Q(B) capacity of coded pairs in cold-held targets (exact, cgx_x.py PROBE at the slots stage, all 112 non-selected pairs)
- Cold coded T edge for the pair ALONE: 112/112 OK (join of the two M slot frames, dim 5, lies in hyper(P_t) and hyper(P_u)). So a cold target hosts ONE coded pair.
- Warm (after selected loads): 0/112 (matches B248).
- SECOND pair on the same target, T edge join must contain whatever pair 1 left in y_t: pair-1 slot frame in partner hyperplane 0/224; both keys 0/224; selected loads 0/224; RAW halves (dim 3/4) 0/448. Independent of schedule and cold hold, because frames only grow. Max 1 T pair per target = the 56 selected pairs (B248 matching bound re-confirmed from a second angle). Hosting 2+ coded pairs: 0 targets.
- Single-M cold read (G7 form) needs the reader's cold slot AND a coded basis; the coded basis is the T edge, so it falls to the same 1-pair bound. S4 copies removable by the coded route: 0 of 112.
## Ledger (cold slots, 112 supply = one per target)
- Supply 112 (frame () first read of each y). Today: 112 spent on own-row reads (dim 2).
- Demand: S3 16 copies (need cold reads of P at consumers: 32 consumer blocks x targets; per CF: 4 targets); S4 112 (coded pairs: 0 feasible, 2nd T pair 0/224); MIXSEL 32 (B246).
- The exchange rate is cheap (lazy widening), so cold slots are NOT scarce for S3: the S3 family is limited by widening, not by supply. For S4 the wall is the one-T-pair-per-target matching, not slots.
## Closure
Cold-slot family for S4/coded pairs CLOSED (rate irrelevant: capacity 0). S3 branch (B245) alive: see side finding; needs chain.sh carry + audit_local + price1018.
Files: cgx_x.py (cf2 + DEFT/POST/GLAZY/PROBE), run.sh, pr.py/step0.py (pricing helper, uses B248/pricep.py), o logs in a scratch directory.
