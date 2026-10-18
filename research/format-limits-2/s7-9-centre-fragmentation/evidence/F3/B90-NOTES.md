# B90 (team idea): helpers as the shadow of a true step / pseudo-gauge in #656. VERDICT: KILL (no priced true step); structural knowledge recorded. ship=false
Scope: shipped #656 word (B76 FULL-WORD.json.gz, byte-identical), exact Fraction replay of A+cut+B+cleanup (replay cleans to 0 on helpers), B76 tags. Tools: work/replay.py, an.py, blk.py, tstruct.py, reads.py, walsh.py, life.py. Output: composite_summary.csv. No heavy jobs (heavy.sh was BUSY; all runs < 2 min, single process).
## Composite per site (clean source rows; rank over Q, mod p)
| site | helpers | rank (end of A) | rank (end of B) | rank of all values ever held | notes |
|---|---|---|---|---|---|
| S1 block scratch (14x16) | 224 | 8-9 per block (16 helpers) | 8-15 | 8-26 | 99-119 distinct values per block over 16 registers |
| S3 packet copy | 156 | 0 (all zero until B) | 4 (7 blocks, 10-12 helpers), 10 (7 blocks) | 4-20 | |
| S4 slot copy (8/block) | 112 | 0 | 8 (full) | 8 | residue ratio 1.0 |
## S1 internal structure (the real finding)
- Each block owns 8 X lines (14 x 8 = 112, a partition). Block-local program = 152 ops; canonical form (registers relabelled by first use, coefs, frame sizes) is IDENTICAL for 6 blocks (0,1,2,11,12 and the first 152 ops of 13) and differs by 2 extra scale ops in 8 blocks (blocks 3-10); block 13 has extra trailing ops beyond its 152; frame-size histogram identical in all 14 ({4:72,1:28,2:24,3:8}).
- After the program, the 8 line registers hold T (8x8, rank 6, nnz 36, charpoly x^3(x^5-5/2x^4+11/4x^3-7/8x^2-1/2x+1/2) identical in all 14 blocks); lines + 16 scratch = 24 forms spanning R^8 exactly (rank 8, injective clean map R^8 -> R^24).
- The 24 forms are Haar/lifting pair forms (x_a+x_b, (x_b-x_a)/2) plus 4-term and 8-term +-1 sums: 4 of 24 are full Walsh characters (all-ones, 4|4, 2|2|2|2 sign patterns), the rest are not a Walsh frame. Best Walsh relabelling of the 8 lines cuts nnz only 86 -> 76 (4/24 forms become unit vectors).
- Snapshot duplicates (row equal to another register up to scale): end of A 60/224 S1 helpers (28 equal an X/Y register), end of B 130/224 S1, 76/156 S3; S4 0. Not removable: B19/B82 (reader frame, timing, in-place).
## Hypotheses
- h-a (composite = change of basis in Free group / relabel): NO. T is non-monomial (36 of 64 nonzeros, rank 6), so not in Free; the only basis that would sparsify it is a Hadamard rotation of the 8 lines, which mixes registers of different frames = B69/B23 (common-frame ADD illegal). Gain bound anyway 86 -> 76 nnz.
- h-b (gauge x small residue): NO. S1 rank 8 of 16 is not a gauge factor, it is an overcomplete frame (24 forms, dimension 8); S4 residue 8/8 = 1.0 (killed by the card's 0.8 rule); S3 mixed (4/10 on 7 blocks), but B82 already proves those 124 copies frame-blocked.
- h-c (14 blocks conjugate): TRUE (same local program, same T, same S up to 2 classes). But conjugacy shares no registers: the 14 scratch sets are separate and every block's scratch is read across the whole of B (windows 2245-3727 for most blocks), so no time multiplexing without reordering B. Read-span bound: at most 66 distinct S1 scratch forms are simultaneously within their first..last-read spans vs 224 registers; this IGNORES creation (all built in A, ops 0-2192) so it is not a bound on helpers and nothing here prices a just-in-time recompute (extra ops add climbs; B82/B83 order-fixed).
- h-d (known transform): partially (Haar lifting butterflies + a few Walsh characters on an octad's 8 lines); no direct frame-legal expression found, because the consumers need the stage values, not the transform output (B84 lifting reduces to B23).
## Priced
Nothing. No step removing >= 5 w9-equivalent helpers; no >=1% structural claim (the 14-fold conjugacy is real but earns no cost).
## Honest lead (unpriced, NOT a claim)
Time-multiplexed S1 scratch (run the 152-op local program just before each block's consumers) would need B ordered block-major or per-form recompute; B's reads are interleaved across blocks for the whole phase. Upper-bound removal price from B76: S1 +38.9% b (all climbs deleted), not reachable.
