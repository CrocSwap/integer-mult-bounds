# B92b: equal S1 twins in 8/14 blocks of #656. VERDICT: KILL, PROVEN [scope: shipped #656 word, exact symbolic replay (B90/B76 FULL-WORD), all 16 pairs]. ship=false, no word built, no kappa.
Tools: cards/B92/twins.py (finds equal pairs, lists write/read sites per twin), cards/B92/tw2.py (value history of a pair). Single process, seconds.
## Facts (all 16 pairs identical in shape; example block (0,2,4,6): S277~S281, S282~S285)
- Class (b)/(c-ish): twins are NOT copies. S281 is a 4-write stage form {x12+x15} built at A-op 465-509 and READ in A (3 reads, ops 472-509) and in B (2 reads, B13, B244). S277 is a long-lived working register (13 writes, 13 reads, all A) that only reaches the same row at A-op 578 (end of A), after being {10},{10,15},{15},{14},{14,15},{15}.. etc. Equality is end-of-A coincidence of Walsh/Haar stage forms, not a construction duplicate.
- S277/S285-type partners are never read in B and never written in B; S281-type twins are the only ones read in B.
- B-reads of the 281-type twin could be re-pointed to 277-type (equal, unmutated through B): B11-legal, but saves 0 ops.
- The 281-type register cannot be retired: its value is needed in A at ops 472-509 while the 277-type holds {10}/{10,15}, a different form (value-forced, no alt holder). Its 4 build ops and 4 cleanup ops stay.
- Only conceivable gain: after re-pointing, 281-type is idle from ~A-op 509 to cleanup, so its register slot could host a B-only helper (<=1 reg/pair, <=0.4% b upper bound). Needs early zeroing of 281 (its inverse ops need A-time frames, not the cleanup frames) = new ops that cancel the saving, plus a B-only helper whose lifetime fits. Not shown feasible; below 1% bar.
## Result
0 of 16 pairs retireable. Pairs retireable: 0. SHIP CANDIDATE: no (no kappa).
## Escapes
1. Slot sharing of the idle 281-type (above) with exact early-zero pricing (B66). 2. Reorder A so the 277-type is built in 281-type's place and 281 derived from it (butterfly refactor, value-level only, unpriced).

Scripts: twins.py and tw2.py live in cards/B92/.
