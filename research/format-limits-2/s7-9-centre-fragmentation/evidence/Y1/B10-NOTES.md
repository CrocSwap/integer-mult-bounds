# B10 notes (Oct 12). VERDICT: KILL at gate (a). PROVEN, scope below. ship=false. Nothing built, no heavy job.

## Gate (a): span (script g.py, B3R R.npy = the 8 centre functionals on the 112 sources, rank 8)
- A converted block's X-face total = the sum over a face's 4 sources in 4 different blocks (B7/J21-K): a weight-4 vector in source space.
- Every nonzero vector in span(8 centres) has large support: over F2 (package field) the centre code (R mod 2 has rank only 4, kernel 15 x's) has nonzero weights exactly {56 (128 vectors), 64 (112)}; over Q the min weight found across 20000 random hyperplane normals is 53 (of 112).
- So a weight-4 total is in span(centres) never (4 << 53). Each total adds +1 to rank: rank([C|T]) = 8 + rank(T) = 12 for one block's 4 totals, up to 8+56 = 64 for all 14 blocks' totals. Kill bar was > 10. Fast KILL.
- Reason: centres are global D8-root combinations (every source enters with +-1 in ~half the centres); X totals are local 4-source sums. B3's rank-8 state carries the Gram part of M, not arbitrary local sums, and the 8 centres are not a basis of anything local. Kill risk (i) realised.
- Gate (b) legality and (c) hybrid pricing not run (moot once totals are outside span; a centre read could only supply span vectors). Note B3R fixed-cover pricing is ill-posed anyway.

PROVEN scope: totals defined as source-subset sums of X faces (J21-K), centres = B3R's exact 8 centre functionals on the #623 content map. Not shown: totals defined on other quantities (e.g. M-row/target-side or dirt/F2-frame strand totals), a different (non-matched) centre set.

## Escapes (>=3)
1. Different state: choose a rank-r > 8 state (r ~ 12-16 centres = centres + 4 per-block local totals) -- that is exactly the helpers charge again (+4 per block) unless centres double as totals; price with moment engine.
2. Re-gauge: pick the X-face source sets to lie in the centre code (weight-56/64 faces are unusable, but faces defined by D8 root lines that happen to be low weight in a different centre basis); check J21-K tiles against root-line geometry.
3. Totals defined target-side: supply X strands' totals from partially-written targets (cut timing), not sources; test span of M rows rather than R columns.
4. B3R escape 2 (wide-climb mass padding) could make a wider, cheaper hybrid; independent of totals.
Rescue check (not run, ~10 min): take J21-K's actual X-face definition from archive/r21/K_skeletons code (if totals are F2 strand totals rather than source sums, recompute rank([R mod 2 | T]) on the real vectors); if rank <= 10, reopen gate (b).

## Rescue check (Oct 12, g2.py) -- result
- Real totals (J17-T/J21-K): per block, 4 totals + 4 complement = f(+)+-f(-) strand rows, i.e. linear forms supported on the face sources: a face has <=10 sources, a total <=20 sources, 4 blocks = <=32 sources. Every nonzero centre combination has support >=53 (Q) / 56 (F2), so no strand total (block-local or X) lies in span(centres) either: rank([C|T]) = 9 per total. Same KILL as the source-sum reading.
- Escape 3 (target-side): rank(C) = 8; rank([C | the block's 8 target rows]) = 16, and adding the block's 8 unit source vectors E_b stays 16 -> the block-local 8-space (which includes any block-local total and its complement) IS in span(centres + own block's 8 target rows), blocks 0,5,13 checked. So an X total on blocks {a,b,c,d} lies in span(C + the 32 target rows of those blocks) (rank 8+32=40, by the same per-block containment; my random-sample check used blocks not covered by M[:32], so its +1 is expected).
- But this is the trivial identity "targets = M u": the supply needs 4 target rows read per total, and targets get their final writes only in the last 224 ops (B3), i.e. after/at the cut -- the totals are needed to produce those very writes (circular), and the reads climb into cross-block frames. Legality/pricing not run; no helper saving shown.
- FINAL: KILL stands for centre-only supply (PROVEN, scope: centres alone). Target-side supply: span exists but is circular with the cut ordering -> LEAD at most (unpriced, <=5% odds); not built.
