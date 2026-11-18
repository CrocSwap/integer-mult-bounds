# NATIVES: which premises of the Lean ceiling the three native words meet, and how that was computed

Words: `st1`, `#7637`, `x1t2a` (the current frontier words; they share one owned layer and one port set of 104 odd-weight vectors, so this is closer to one data point than three). Lean treats every object in `ceiling_native'` as abstract. **Nothing in Lean ties a word to these hypotheses.** The checks below are exact computations by Python scripts (exact modular arithmetic, exact integers or outward-rounded Decimal), run on the word files; the scripts and word files are not part of this package. "Value" = the premise as computed, not a Lean fact.

Honest summary: word-level premises are computed; hcong*, hdist, hspMono, hcstMono (now derived from the shape-DAG hypotheses of `CongestionNativeH`) and hst are paper theorems whose premises the natives meet. In the current Lean, `hspMono`/`hcstMono` are derived (CongestionNativeH `spShape_mono`, `cstShape_mono`, from `c2_anti`) and `hst` is still a hypothesis whose analytic proof (phi(a,b) = a^s + b^s - (a+b)^s increasing in a) is on paper only; `hdist` is derived from the new hypothesis `hdistShape`, `hcong*` from the per-cell path hypotheses (`hconf`, `hstart`, `hvisit`, `hleg`, `hclass`).

| Lean premise | what the natives satisfy (value) | computed by | words |
|---|---|---|---|
| hmono, hd9 (public registers ascend, end at most 9) | 0 violations of either | exact replay of the program, structural audit (`aud2a`) | st1, #7637, x1t2a |
| hmix (at most 5 mixed registers) | exactly 5: [1,3], [5,7], [1,4,7], [1,2,3,6,8], [3,7,8] | `aud2a` | all three |
| hk, hmass, hmd, hmr (ks = 24 descents + 13 non-unit rises, mr = 10 unit rises) | all ranks in [1,6]; sum 102 >= 56; length 37 >= 8; mr 10 >= 8 | `hc6`, `aud2a` | all three |
| hY (104 <= st + (len ks + mr)) | st = 1266 / 1266 / 1265, so 1313 / 1313 / 1312 >= 104 | `hc6`, `aud2a` | all three |
| hF (F-currency inequality, exact) | the exponential-polynomial coefficients on both sides are identical integers (difference {}), so equality holds for every real s | `hc13` (`hF`), `hc6` | all three |
| hEex (sum of register excesses <= E) | E is defined as that same exponential polynomial (identity) | `hc13`, `hc6` | all three |
| hst ((2 - 2^s) st <= E) | premises computed: every public gap >= 1 and every main moves; st = 1266 / 1266 / 1265; grid slack 158.3 / 159.4 / 158.2 (zero only at s = 1) | `hc13`, `hc6` | all three |
| hJ (1936 <= \|J\|) | \|J^arr\| = 4962 on all three (2536 forced cells on the route flags) | `hc12` (exact mod 2^61-1), `hc11` | all three |
| hconf, hstart, hpub, hnest (per-cell chart paths) | public moves are nested strict ascents (6124); 47 owned moves, all nested (23 up, 24 down); every one of the 4962 cells has a legal (u_s in every chart) owned-descent-free, hence ascending and D-confined, path; 0 cells need a cut | `hc12`, `aud2a`, `aud2b` | all three |
| hvisit, h48 (visits and the 48-law) | the 24 transport frames have max n*m = 24, total even-cell capacity 204; max n*m = 48 over all subspaces of F2^9 in the census | `hc8` (natives' frames), `aud2d` (exhaustive census) | all three (frames); census word-independent |
| hleg, hclass (Cap class) | Cap margin Omega - cst (Rm - 8) - U Nf >= 19.35 on s in [.9, 1 - tC0] (Omega 47.995, Nf 24, Rm 56); by the Jt = 0 route the margin is about 45 | `hc13` (certified, 2000 pieces), `hc2`, `hc1` | all three |
| hdistShape, hspShape, hcstShape (the shape DAG) | spF is a minimum of c2-weighted sums over the 230 shapes (n >= 1, m >= 1, plus duals) of the census of subspaces of F2^9 for the natives' 104-port set; the shape list was re-derived independently by exhaustive enumeration of all 8,283,456 subspaces of dimensions 1 to 8 and is identical (230 = 230, histograms equal) | `hc9` (outward-rounded), independent census program | word-independent; port set identical for all three |
| hspTab, hcstTab, hunitTab (rational tables) | all table entries certified: slack about 1e-9 (spFlo) and about 2e-6 (C pieces) | `hc9` (Decimal at 80 digits, weights rounded down, constants rounded up) | word-independent |
| rank 8, descent mass C = 56 (the premise behind hJ) | the 8 routes have rank 8 and mass 56 (computed); the numerical rigidity of the decoder matrix does not hold exactly (6 mismatches), so "the native decoder is the enumerated configuration" holds for supports only | `hc8` | all three |
| span law (the legality the natives actually obey) | 0 span-law failures over 7906 / 7925 / 7902 route checkpoints; the per-port form of legality is false on the natives (1277 to 1280 rows with per-port illegal content) | `hc14` | st1 / #7637 / x1t2a |

Not computed on a word and not in Lean: the class-wide bound |J| >= 1936 for decoders that are not rank 8, C = 56 (**a conjecture**), plane separation, and decoders with 9 or more rows or network decoders. For the natives the value is computed (4962), not bounded.
The link from the Lean `n` and `caller 6 7` / 17 to each word's invoice is the pricing script's, not Lean's.
