# Class C cells of the one-sided K2 residue: help package (no kappa claim)

Companion of a Discussion thread asking for help with the "class C" cells (4-flat span questions). Nothing here is a claim about kappa; the relative-root-counting kills used to shrink the list are under audit.

Files
* `s4z.c` -- 4-flat span checker (a,b,c,d label flats, s = 0). `s3z.c` -- the 3-flat checker it generalises (S3FLAT lineage, exact match checked on sampled slices).
* `gens.txt` -- generators of the frame stabilizer acting on the 112 lines (used for orbit representatives).
* `data88.txt` -- complete direction list |Off| <= 88 (E8 frame split, P112), 18100 directions.
* `rows70.csv` -- the 70 class C rows (d, s, weights, e, status, covering 4-flat configs); `rows17.csv` -- the 17 rows not killed by relative root counting.
* `validate.sh` -- compiles both, reproduces the (6,6,4) s0 crack at T=5 (rep 82, V2idx 103676) and a T=6 pass slice, about 25 s.

Usage: `s4z data88.txt a b c d 88 T M rem` (a >= ... as the dims of V1..V4 with V1 over orbit representatives; the run splits V1 reps into M chunks, `rem` selects one). Env: `ONLY=r1,r2` restrict reps, `JMOD=J JREM=j` split V2 into J slices, `EXITCRACK=1` stop at first CRACK, `PAIRLOG=1` per-pair log. Output: `CRACK? target T span S ...` if some pair has relaxed span >= T, and an `OVERALL ... max span` summary. A complete run with no CRACK at target T proves span <= T-1 for that config in the relaxed model (kill needs span <= d-1).

Arguments: for a config {f1>=f2>=f3>=f4}, b = f1 (the largest flat, V2, enumerated), a = one other flat (V1, over orbit representatives; chosen to minimise pairs), c <= d the remaining two (never enumerated, d <= 5). E.g. (6,5,4,3) is `a=3 b=6 c=4 d=5`, T=8 `s4z data88.txt 3 6 4 5 88 8 M rem`. Pair counts: (6,5,4,3) a3 b6 c4 d5 2.6e7 pairs; (6,5,4,4)/(6,5,5,4) a4 b6 1.1e8; (5,5,5,4)/(5,5,5,5) a5 b5 3.3e8.

Cost at T=8: 70-100% of pairs survive the relaxed gate; 4-10 s per pair for the closure; ETA ~4e4 CPU-h for (6,5,4,3), ~3e5 for the others.
