# B92: S1 scratch dependencies / pseudo-gauge. VERDICT: KILL, PROVEN [scope: shipped #656 word, B90 exact replay, value-level test; no frame replay needed]. ship=false
Tools: cards/B92/cls.py (rank + scalar-duplicate classes at end of A), feas.py/feas2.py (per B read of a scratch: does another live register hold the same row up to scale?). Single process, seconds.
## Facts
- End of A: the 16 scratch are DISTINCT sparse forms (nnz 1,2,4,8), not copies. Only 2/block equal a line register (S225~L56, S227~L59 in block 0; same in block 11), and these are not read in B (A-internal). Rank 8 of 24 is overcompleteness of Haar/Walsh stage forms, not frame duplicates. 2 nnz-1 scratch/block are clean copies of an original x_j, but the line register already holds a mutated row, so nothing to exchange (no cold-end rank-one structure as in Gauge44).
- Reads in B (value test, alt holder = any other live register): block (0,1,2,3): 12 scratch read; 0 fully covered; 8 have 2/3 reads covered, ONLY by a target accumulator that the first read just copied into (e.g. S226 -> reg 450, later reads could use 450); 4 never covered. Block (2,3,4,5): 11 read; 0 fully covered; 8 partial (1 of 2 reads, same mechanism), 3 never.
- All 14 blocks: fully value-covered scratch by own S/L registers = 0 for 6 blocks, exactly 2 for the 8 blocks (0,2,4,6)...(1,3,5,7) (S281/S285-type: pairs of mutually equal scratch, S277~S281, S282~S285; one member unread in B).
## Classification (blocks 0 and 11), per scratch
- g1 frame copy (value-feasible via a target accumulator, but that accumulator sits in hyper(P[t]) after the first read = B82 target-read timing): 8 and 8.
- g2 gauge-exchangeable at a common frame: 0 and 0 (kill gate: g2=0 in both).
- g3 value-forced (no alt holder at read time; distinct stage form): 4 and 3.
- g4 A-internal / unread in B: 4 and 5 (incl. the 2 line duplicates).
## Judge's butterfly question (in-place stage k over stage k-2)
Kept stages are all read throughout B (windows ~2245-3727, B90 life.py), max simultaneously live read-span per block 4-12 of 16 (reads.py); values are built in A, so overwriting a stage needs a recompute (extra climbs), not an exchange. Reads after any plausible overwrite point exist for essentially every scratch (reads per scratch 2-28 spread over B); the only alt holders are frame-locked targets (g1). No legal in-place count found; not a g2.
## Possible lead (small, unpriced): the 8 blocks with 2 mutually-equal scratch (16 helpers = 16 w9-ish, <=0.4% of b upper bound). Needs: why both exist (probably a copy for A-internal consumer), whether the unread-in-B twin can be deleted or reused. Below the 1% bar; not pursued.
## Escapes
1. Check the 16 twin helpers' A construction (why S277 and S281 both). 2. Order-free (B80) version of g1 targets. 3. Recompute-just-in-time with B66 pricing (B90 bound +38.9% unreachable).
