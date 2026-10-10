# w3: cube-layer and line-pair redesign of the PR249 bit word

**Conditional κ = 94111687450666858500293 / 1.25·10²⁶ ≈ 7.528935·10⁻⁴.**
- That is **+5.824 %** over #270 (7.11457853376510·10⁻⁴).
- It is **+0.19 %** over the best open PR at packaging time: #309 at 7.51499·10⁻⁴; #308 is at 7.51472·10⁻⁴ and #306 at 7.51459·10⁻⁴.

The bit coarse saving is c = 7.5346077·10⁻⁴. The bit side binds with the complex supplier of PR #233 (7547/10⁷) and with that of PR #304 (7635/10⁷); both give the same κ. With the old #193 supplier (7.47455·10⁻⁴), the complex side binds and κ = 7.46897·10⁻⁴ (+4.98 %).

## What changed

The base is the PR249 / source527 local word: 20,107 roles, the five-stage layout of PR234, m = 120. Only the local bit word changes. The deficit stays at 4,400 per set (35,200 in the normalized 40-replica units).

1. **Design T (cube layer).**
   - The four 011 X-mixes of each cube happen at 2-dim mix frames M.
   - Each of the 8 non-mix tetra edges {a,b} gets a new 2-dim frame T = span(χa, χb). Its Gram matrix under G = I − J/9 is 2I.
   - At T, two line registers and one starter make the two block copies directly. The starter ends up holding x_a, which is exactly the K4 "partner single". So singles ride on registers that are needed anyway.
   - This covers all 220 cubes and frees 795 cube-layer helpers.
2. **Twin condensation of plane leftovers.**
   - At 810 planes whose two arrivals are both mix-frame starters, the rank-forced leftover enters at the 1-dim intersection line of the two mix frames (entrance rank σ = 1) and is absorbed by the block holder.
   - This adds 480 new 1-dim frames.
3. **Line-pair / all-but-one module template, found by SAT.**
   - It uses 20 registers per line: 10 plane block holders plus 10 fresh registers, with two copies per block.
   - The rounds are copies at s{X} (dim 3) → 5 triple frames (dim 7) → 5 six-block frames (dim 13) → final merge at F_Z (dim 21).
   - This adds 1,320 new frames (dims 7 and 13) and frees 660 helpers.

**Totals**
- 1,455 helpers are freed. They are encoded as entrance FULL (σ = 24) with no records.
- New entrance rank relative to PR249 = 35,280 = 3 · 11,760. That matches the stock drop of 11,760. It is not 795·24 + 810 + 660·24, because 36 of the 660 LP helpers already had σ > 0.
- There are 3,473 new frames, and every one is exactly nondegenerate.
- Local D per stage goes from 1,138,396 to 1,068,458.6 (−6.1 %).
- Normalized stock (40 replicas): 173,883 → 162,123.

## Verify (about 1 minute)

    apt-get install -y g++ libboost-dev ; pip install numpy mpmath
    bash verify.sh /tmp/w3-verify-work

`verify.sh` runs these steps:
1. Rebuild the word and the PR249 base snapshot from the gzipped files (`reconstruct.py`).
2. Compile the **unmodified** official PR266 checkers (`checkers/official/*.cpp`, copied byte for byte from research/multicut-kernel-condensation-883/code).
3. Run `cohort-legality-independent`. Expected: PASS, ADD 934,385, rank mass 398,897, 24 COPY / 24 ERASE.
4. Run `cohort-five-stage-columns`. Expected: PASS on 23,627 formal F₂ columns, payload prefix 2⁹⁴ < 2¹⁰⁴.
5. Run the independent checker `checkT`, which replays legality, checks nondegeneracy mod p for all 22,228 used frames and replays formal F₂ over all 20,107 columns. Expected: all zeros.
6. Run `exactnd.py` for exact rational nondegeneracy (Bareiss) and exact annihilators of all 3,473 new frames.
7. Price with `cost.py` (moment root).
8. Run `kappa_w.py`: PR265/#270's fixed-prime engine (`fixed_prime_math.py` with the retained moment, base_two_moment and outer engines), η = 10⁻²⁴, β = 10⁻⁹, grid 10⁻²⁷, all 47 outer constraints, and rejection of the adjacent grid point. It runs once per complex supplier.

The output of every step is recorded in `receipts/`. `receipts/pr256-complex233-verify.txt` is a fresh PASS of PR #256's verifier, which re-checks PR #233's complex word at 7547/10⁷.

Word SHA-256 (COHORT249-RECORDS.bin): `a9501525563d3ec656ebf01aea9f2c9839e033563ea4a022500d68b12756ae86`.

## Files

- `word/`: COHORT249-RECORDS.bin, COHORT249-FRAMES.json (new frames only, with B and exact annihilator A), COHORT249-INITIAL.json and an empty COHORT249-SELECTION.json (no kernel cohorts are selected). It also has the full w3 249-states.json and the frames.txt / states.txt exports used by checkT.
- `base/`: the PR249 snapshot (249-records.bin, 249-states.json, frames.json, donor ownership). The same snapshot is produced by `checkers/official/export249.py` from PR266's vendored pr249-source.zip.
- `checkers/official/`: the unmodified PR266 native checkers, plus json.hpp and export249.py.
- `checkers/independent/`: checkT.cpp + sub.hpp, exactnd.py, and exactprice.py (the PR234 certify() engine).
- `pricing/`: cost.py, kappa_w.py and the retained #270 engines.
- `builders/`: provenance only.
  - Agent A's Design T builder (`build_v5.py`, `gather.py`, `addcomp.py`, `verify.cpp`) and twin step (`twin.py`).
  - Agent B's LP builder (`build_lp.py`, `rebuild.sh`), the SAT design `sat/sol_z5_m3t6.json` with its models, and the census tools.
  - The builders were written against local scratch paths and intermediate pickles that are not included. They show how the word was made; they are not needed to check it.

## What is NOT done yet (for whoever publishes)

The word-level checks pass with the unmodified official tools. The later native stages of the #270 pipeline hard-code facts about the PR249-derived word and must be generalized before an official replay. The exact items:

1. **Bank review (`cohort-bank-review.cpp`).**
   - It hard-codes the base residual census {4:2200, 6:22, 7:5, 11:48, 12:23, 15:2, 24:…} and expects the r = 24 count to be 14,287 minus the changed roles.
   - w3's residual multiset is {0:1,455 (freed), 4:2,200, 6:22, 7:5, 11:24, 12:13, 23:810, 24:12,058}, with total residual 317,409, which is divisible by 3.
   - A feasible width-120 tiling exists: mix(23,4,7)×8,100, rep(4,30)×973, rep(24,5)×96,464, and so on. Freed (r = 0) roles must be deleted rather than banked.
2. **Native price (`cohort-price.cpp`).**
   - It hard-codes the old complex supplier 747454944651775/10¹⁸ and the PR266 baseline regression.
   - Run it with w3's histogram and new_entrance_rank = 35,280, using the PR #233 or #304 complex constant.
3. **Finite invoice (`cohort-finite-invoice.cpp`).**
   - It hard-codes R = 16,587 and `actual_role_replica_stage_assignments == 3,317,400`.
   - With 1,455 freed roles these become 15,132 roles and 3,026,400 assignments. The bounds only shrink.
4. **Source binding.**
   - Write a `verify.py` in the style of #270 that regenerates the base from the PR249 source.
   - The w3 word itself can be shipped as data, as most open PRs do. Note that the `record_sha256` field inside 249-states.json is stale (inherited) and should be recomputed.
5. **Optional stacking.** The community's stage transforms (kernel entries, descent, target squares, restorations, sinks, reorder) were developed on PR249/gen5b words. Re-deriving them on w3 should add further small gains.

The result is conditional on the same retained all-size interfaces as #270, #299 and the other open PRs: compiler, charts, selectors, routing, prime supply, precision/recovery and complex correctness. It is not a Lean certificate.
