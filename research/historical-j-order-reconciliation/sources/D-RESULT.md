# D-surrogate — ideas 61 / 55 / 91: fast κ surrogate, J-vs-exact-κ disagreement, incremental exact κ

All code and data under /tmp/radical/D (nothing written into any worktree; no commits/PRs).

## What was run

1. **Dataset.** Started the 100 stopped Daytona sandboxes in batches of 10, pulled every `cand_*/res_*` pair plus
   `start.json`/`log.jsonl`, stopped them again (`download.py`, 100/100 ok). Result: **989 evaluated designs**
   (653 local-recipe, 180 pair-module, 156 qmod-module; 761 unique: 589 / 139 / 33) in
   `/tmp/radical/D/dataset.jsonl` (sandbox, which, seed, t0, step, design, kappa_float, kappa, bit_root,
   literal_stock, R, entrances, dropped, seconds). The annealers ran 7–12 physical steps each (190–300 s per eval on a
   1-cpu sandbox).
   - The data are **not** "all within ±0.002% of 7.64231e-4": local mutations give κ ∈ [7.3620e-4, 7.6427e-4]
     (std 1.08%), pair ∈ [7.5015e-4, 7.5474e-4], qmod ∈ [7.4768e-4, 7.5896e-4]; only 209 unique designs lie within
     0.1% of the best. 33 distinct local start designs were used (κ 7.64231e-4 … 7.64266e-4, the best being
     7.642660e-4 = +0.0056% over the #315 baseline 7.642309e-4; all with R = 8230).
2. **Histograms.** `res_*.json` does not contain the climb histogram that κ is a function of, so I re-ran every
   unique design through a histogram-dumping copy of physical_eval (`physical_eval_hist.py`, identical except the
   output dict) on the same 100 sandboxes (7–8 designs each, `launch_hist.py` / `collect_hist.py`, all sandboxes
   stopped afterwards). 761/761 collected → `/tmp/radical/D/hist_dataset.json` (hist, J, mass, R, κ, ...).
3. **Exact κ from a histogram** (`kap/kappa_hist.py`), **incremental exact evaluator** (`kap/incremental.py`),
   **surrogates** (`surrogate.py`, `surrogate2.py`, `features.py`; sklearn 1.6.1 installed into a private venv
   `/tmp/radical/D/venv`), **derivative table** (`deriv_table.py`, `deriv_table.json`).

## Facts about the pricing block that every downstream search should know

- `five = 5*hist + idle; five[5a] += gauges; H = five; H[5a] -= gauges` — **the auxiliary entrances cancel
  exactly; κ depends only on the paid-climb histogram `hist`** (plus constants v=960, h=20, m=100, idle ranks
  38/19/42/4 at 1920 each, deficit 2040). R and `literal_stock` are both functions of `hist` (stock = 3·mass + 119880,
  mass = Σ r·n_r telescopes to Σ_registers (dimf[final] − dimf[initial])).
- `kappa_from_hist` (my `kappa_hist.kappa_exact_fast`) reproduces the sandbox κ **bit-for-bit on all 761 designs**
  (0 mismatches) and the package's `moment.certify` on the baseline.
- **Stock-floor trap.** `Wn = W_lit//5` is exact only when the paid mass ≡ 0 (mod 5). All 761 real designs satisfy
  this (structural: mass = 20R + 16450 − 17·g17 with g17 ∈ 5ℤ), but a hypothetical single-climb retiming that changes
  mass by r ≢ 0 (mod 5) lowers the deficit by 20·(3r mod 5) units of 24480 and κ by 0.08–0.33% — 100–400× the true
  effect of the climb. A gate-level search must either keep mass ≡ 0 (mod 5) (automatic for legal words, since mass
  is fixed by birth/death frames) or use rational W. Table column "+1 climb, W floored" in `deriv_table.json` shows it.
- **Module evaluations are non-deterministic.** Re-evaluating the *same* design: local recipes reproduced 589/589,
  but 4/33 qmod and 16/139 pair designs came back with a different κ (median 0.16%, max 0.69%, e.g. qmod u0598
  7.57897e-4 → 7.52670e-4; R also changes, 8320 ↔ 8410). The 139 pair designs only produce ~125 distinct κ values and
  the 33 qmod designs 12. The pair/qmod annealers were therefore partly annealing evaluation noise, and no surrogate
  can beat that floor on those two families. (Hash-seed test: see end of file.)

## (a) Surrogate of physical κ

Features (`features.py`): local recipe = per-plane position, tree max-depth, per-leaf depth, per-leaf-pair LCA depth,
left/right membership, per-position key type/axis/shape, #caterpillar trees (222 non-constant features);
modules = node/internal/root counts, depth statistics, fan-out (sharing) histogram, popcount histogram, per-root
depth/size, per-input fan-out/depth (113 pair / 46 qmod features). "Cheap outputs" = (R, literal_stock, g17, dropped).
5-fold CV on unique designs; MLP with standardized target.

| family (n unique) | features | model | CV R² | Spearman ρ | CV rmse | pair-rank accuracy by |Δκ|/κ: <0.002% / 0.002–0.01% / 0.01–0.1% / 0.1–1% / >1% |
|---|---|---|---|---|---|---|
| local (589) | design | ridge | **0.986** | **0.963** | 0.128% | 0.51 / 0.52 / 0.79 / 0.98 / 0.995 |
| local | design | GBR | 0.899 | 0.912 | 0.345% | 0.51 / 0.59 / 0.62 / 0.89 / 0.99 |
| local | design | MLP(64,32) | 0.842 | 0.858 | — | — |
| local | cheap outputs (R, stock, g17, dropped) | GBR | 0.997 | 0.970 | 0.057% | 0.40 / 0.39 / 0.81 / 0.98 / 1.00 |
| local | design + cheap | GBR | **0.998** | **0.982** | 0.048% | 0.41 / 0.54 / 0.91 / 0.99 / 1.00 |
| local, within 0.1% of best (207) | design | GBR | 0.925 | 0.915 | 0.008% | 0.54 / **0.94** / 0.98 / – / – |
| local, fixed R = 8230 (153; κ spread 0.067%) | design | GBR | 0.998* | 0.864 | — | 0.62 / **0.99** / – / – / – |
| local, fixed R = 8230 | design | ridge | 0.997* | 0.831 | — | 0.55 / 0.98 / – / – / – |
| pair (139) | design | ridge / GBR | 0.07 / −0.28 | 0.45 / 0.27 | 0.18% | ≈0.5 everywhere |
| pair | cheap | ridge | 0.980 | 0.864 | 0.026% | 0.46 / 0.40 / 0.44 / 1.00 / 1.00 |
| qmod (33) | design | ridge / GBR | −0.25 / −0.12 | 0.33 / 0.44 | 0.47% | – |
| qmod | design + cheap | ridge | 0.978 | 0.904 | 0.062% | – / 0.0 (6 pairs) / 0.54 / 0.97 / 1.0 |

(* R² inflated by a few far outliers in that subset; the pair-rank columns are the honest number.)
Design features → R (register count) for local: ridge R² 0.958, ρ 0.906.

Reading: a design-only surrogate of the local recipe ranks designs reliably when they differ by ≥0.01% (79–99%
correct) and, restricted to the near-baseline regime, resolves 0.002–0.01% differences 94–99% of the time, but
**at <0.002% it is a coin flip (51–62%)** — exactly the regime where the stage searches live (dataset-wide the
<0.002% bin has 4103 pairs). For the module families design features explain nothing (the evaluation noise above
is as large as the signal). The surrogate is a filter, not an oracle: it can discard the ~70% of random local
mutations that lose ≥0.1% before paying 76 s, and nothing more.

## (b) Exact κ versus the first-order proxy J

J = Σ_paid climbs r·ln(100/r) in hist units (baseline J = 487 690.4; five-replica J1 incl. idle = 3.197e7).
On the 761 unique designs (`analysis_b.py`):

- Pearson(κ, J) = −0.99993; **Spearman(κ, J) = −0.9999995**; Pearson(κ, 1/J) = 0.9999995.
  Near-baseline subset (209 designs within 0.1%): Spearman −0.99999, Pearson(κ, 1/J) = 0.9999986.
- Pairwise sign agreement (lower J ⇔ higher κ) over all 287 669 design pairs:
  >1%: 144303/144303; 0.1–1%: 102188/102188; 0.01–0.1%: 29057/29057; 0.002–0.01%: 8018/8018;
  **<0.002%: 4094/4103 (99.78%)**. Total disagreements: **9 of 287 669**, all with |ΔJ| ≤ 0.9 (ΔJ/J ≤ 2e-6) and
  |Δκ|/κ ≤ 0.0002%, e.g. u0006 vs u0241: κ 7.5000815e-4 vs 7.5000983e-4, J 497815.8 vs 497815.9 (mass 185805 vs
  186180, R 8455 vs 8580); u0095 vs u0242: κ 7.6371793e-4 vs 7.6371912e-4, J 488048.7 vs 488048.7 (R 8215 vs 8350).
  These are designs with different R whose J ties to <1 unit: the second-order term decides.
- The analytic reason: a solves Σ_r (r n_r/(mW)) e^{aL_r} + fallback = 1, so da/dn_r = −60·r(e^{aL_r}−1)/Σ r n_r L_r e^{aL_r}
  (one climb = 5 replicas × 12 from `literal//5`). The first-order weight r·L_r is off by the factor
  (e^{aL}−1)/(aL) = 1 + aL/2 — **+0.17% at rank 1 down to +0.03% at rank 20** — so J can only mis-order two designs
  whose ΔJ is below ~0.15% of the gross J they move. Adversarial composite mass-preserving gate moves confirm this:
  6 of 249 moves with |ΔJ| < 0.02 were mis-signed by J (all |ΔJ| < 0.004, i.e. Δκ < 1e-11); the curvature-corrected
  weight w_r = r(e^{aL_r}−1) got 3000/3000 random mass-preserving moves and all adversarial ones right.
- **Scale.** Measured dκ/dJ = −1.392e-9 per unit of J across the dataset (local slope at the baseline −1.430e-9,
  = −60·a·(dκ/dc)/J1e with dκ/dc = 0.998472). **COMMON.md's "6.3e-10 κ per unit of J" is 2.3× too small** for this
  convention (one term per paid climb, m = 100); the ranking is unaffected but ΔJ→Δκ conversions are.
- κ is a function of J to 0.011% rms (linear) / better with 1/J; the residual is the ΔR-dependent second order.

**Exact dκ/dn_r table at the #315 baseline histogram** (κ = 7.642308613202e-4, a = 7.648153571464e-4, D = 24480;
finite difference with +5 climbs of rank r, which keeps mass ≡ 0 mod 5; full table incl. idle ranks in
`deriv_table.json`):

| r | exact dκ/dn_r | r·ln(100/r)·(−1.430e-9) | exact/first-order | r·ln(100/r)·(−6.3e-10) (COMMON.md) |
|---|---|---|---|---|
| 1 | −6.596e-9 | −6.585e-9 | 1.00172 | −2.90e-9 |
| 2 | −1.1203e-8 | −1.1187e-8 | 1.00142 | −4.93e-9 |
| 3 | −1.5061e-8 | −1.5042e-8 | 1.00124 | −6.63e-9 |
| 4 | −1.8431e-8 | −1.8410e-8 | 1.00111 | −8.11e-9 |
| 5 | −2.1439e-8 | −2.1418e-8 | 1.00101 | −9.44e-9 |
| 6 | −2.4159e-8 | −2.4137e-8 | 1.00092 | −1.063e-8 |
| 7 | −2.6639e-8 | −2.6617e-8 | 1.00084 | −1.173e-8 |
| 8 | −2.8914e-8 | −2.8892e-8 | 1.00078 | −1.273e-8 |
| 9 | −3.1010e-8 | −3.0988e-8 | 1.00072 | −1.365e-8 |
| 10 | −3.2946e-8 | −3.2924e-8 | 1.00067 | −1.451e-8 |
| 11 | −3.4739e-8 | −3.4718e-8 | 1.00062 | −1.530e-8 |
| 12 | −3.6402e-8 | −3.6381e-8 | 1.00057 | −1.603e-8 |
| 13 | −3.7945e-8 | −3.7925e-8 | 1.00053 | −1.671e-8 |
| 14 | −3.9378e-8 | −3.9358e-8 | 1.00049 | −1.734e-8 |
| 15 | −4.0709e-8 | −4.0690e-8 | 1.00046 | −1.793e-8 |
| 16 | −4.1944e-8 | −4.1926e-8 | 1.00043 | −1.847e-8 |
| 17 | −4.3090e-8 | −4.3073e-8 | 1.00040 | −1.898e-8 |
| 18 | −4.4151e-8 | −4.4135e-8 | 1.00037 | −1.945e-8 |
| 19 | −4.5134e-8 | −4.5118e-8 | 1.00034 | −1.988e-8 |
| 20 | −4.6041e-8 | −4.6026e-8 | 1.00031 | −2.028e-8 |

Recommended weights for any stage search: w_r = r·(e^{aL_r} − 1) with a = current bit root (or just the exact
column above; it is linear in n to 1e-5 over the whole dataset range). They differ from J's r·ln(m/r) by ≤0.17%.

## (c) Incremental exact evaluator (`kap/kappa_hist.py`, `kap/incremental.py`)

- `kappa_exact_fast(hist)`: Decimal bisection seeded by a float Newton root (±2e-18 bracket, 1e-30 stop) → 1e-24 grid
  point → rigorous verification with a **dyadic-integer (2^-256, outward-rounded) reimplementation of
  `moment.moment`** (same Mercator log bounds via the package's cached `logarithm`, same 24-term exponential + tail),
  then the package's outer chain. Identical κ and bit-root to `moment.certify` on the baseline and to the 761
  sandbox values. **Time: 22–31 ms per exact certified evaluation** (package certify on the same histogram:
  0.58–0.72 s; full physical pipeline: 76 s locally, 190–300 s on a sandbox). `kappa_float(hist)` (Newton in floats
  + exact chain): **50–80 µs**, max error vs exact 2.1e-16 (the 1e-18 floors can flip the last digit).
- `IncrementalKappa`: holds the certified interval (lo, hi) of width 1e-24 and per-rank cached certificate terms
  e_lo[r], e_hi[r] at the two endpoints (memoised; the `logarithm` bounds are memoised globally). `compare(delta)`
  for a gate move touching k ranks costs O(k) big-integer ops and returns exactly whether the new certified root is
  > hi (better), < lo (worse) or inside the 1e-24 window: **11–50 µs per move**, verified against full
  re-certification on 150 random moves (0 mismatches) and 3000 mass-preserving merge/split/transfer moves.
  `apply()` re-certifies in 23–42 ms. So an exact-sign descent can test ~50 000 gate moves per second per core and
  pay 25 ms only on acceptance; a Metropolis step needing |Δκ| uses `delta_float` (50 µs) or the linear table above.
- Target "< 50 ms" is met by a factor 2 (exact) / 1000 (float) / 2000 (incremental sign test).

## Verdict

**Surrogate (idea 61): not good enough to drive millions of steps on its own.** On the local recipe it is an
excellent coarse filter (ρ = 0.96, ≥98% correct ordering for ≥0.1% differences, ~94% for 0.002–0.01% in the
near-baseline regime), but it is a coin flip at <0.002%, which is where the live searches operate; for the pair/qmod
modules it has no signal at all because the physical evaluation of a module design is itself non-reproducible at the
0.2–0.7% level (fix that first — it is a bigger lever than any surrogate). Use it only to pre-screen local-recipe
mutations (it rejects the ~70% that lose ≥0.1%).

**J (idea 55): essentially not wrong.** Exact κ is a monotone function of J to within second order: 287 660 of
287 669 design pairs are ordered identically, Spearman −0.9999995, and the 9 exceptions are ties to <1 unit of J
(Δκ ≤ 2e-6 relative). The first-order weights are accurate to +0.17% (rank 1) … +0.03% (rank 20); the only real
correction is the scale, −1.43e-9 κ per unit of J rather than 6.3e-10. Stage searches should keep optimising J (or
the curvature-corrected w_r = r(e^{aL_r}−1)), and never trust physical_eval's stock floor for moves that change the
paid mass by a non-multiple of 5.

**Incremental exact κ (idea 91): done and promising.** 22–31 ms exact certified evaluation from a histogram, 11–50 µs
exact accept/reject per gate move, 50 µs float κ — i.e. the 76 s pipeline is only needed to produce the histogram of a
*structurally* new word, never to price a histogram move. The missing piece for "millions of design steps" is not the
pricing but a fast design→histogram map (the regenerate/prepare/physical527/parity pipeline); the surrogate results
say that map is not learnable to ±0.002% from 600 samples.

## Hash-seed test of the module nondeterminism

qmod design u0598 (annealer-logged κ = 7.578965e-4, R 8320): fresh evaluations — sandbox re-run 7.526699e-4 (R 8410),
local PYTHONHASHSEED=0 → 7.526699e-4, PYTHONHASHSEED=1 → 7.526699e-4 (identical F2-observer hashes). So the
evaluation itself *is* reproducible now and hash randomisation is not the cause; the 20 discrepant module labels come
from the original annealer runs (that sandbox's `log.jsonl` stops at step 4 while `res_5/res_6` exist, cand_6 ≡ cand_7
yet res_5 carries the R of the earlier steps — the annealer's cand/res bookkeeping or the sandbox being auto-stopped
mid-evaluation and restarted is the likely cause). Practical consequence is unchanged: module-family labels in
`dataset.jsonl` are noisy for ~12% of designs; `hist_dataset.json` carries the fresh, consistent values for all 761.

## Files
- `/tmp/radical/D/dataset.jsonl` — 989 rows (design + outputs) as downloaded; `hist_dataset.json` — 761 unique designs
  with climb histogram, J, mass, R, fresh κ.
- `/tmp/radical/D/kap/kappa_hist.py` — `kappa_exact_fast`, `kappa_float`, `certify_dyadic`, `moment_dyadic`, `chain_kappa`.
- `/tmp/radical/D/kap/incremental.py` — `IncrementalKappa(hist).compare(delta) / delta_float / apply`.
- `/tmp/radical/D/deriv_table.json`, `analysis_b_summary.json`, `surrogate.log`, `features.py`, `surrogate*.py`.
- Sandboxes: all 100 stopped (not deleted — they still hold the raw outputs).
