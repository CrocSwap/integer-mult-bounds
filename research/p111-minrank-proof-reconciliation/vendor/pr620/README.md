# Research notes (no κ claim): E8 decoder floors and #615/#617 cold-end levers

Negative results and one open lead, recorded so others don't repeat them. Scripts are included as they were run (paths reference a local scratch dir and `~/imb-src` pinned sources; Python 3.11 with numpy, scipy, sympy, python-sat, ortools). SAT results come from CaDiCaL via python-sat **without proof logs**. Nothing here is packaged with a verify.sh.

## 1. Unit screen (`ade_screen.py`)
Real ADE root systems as units (v lines, window h = rank, c = F2 rank of (J+G) mod 2, proxy x = c·h/v, ceiling via #595's `skel.X`): only E8 gives a useful ceiling. E7 (v 63, h 7, c 7) reaches X* ≈ 1.84e-3; A_n, D_n and E6 have x ≥ 1 and give no saving. X scales roughly as 1/h, consistent with the Leech (#598) and Niemeier (#606) losses.

## 2. E8 decoder floors (`s2-decoder/`, details in `REPORT.md`)
- **P111 (shipped bit puncture 39,52,57,71,76,78,103,109,114):** the 9-total F2 decoder is unique (= B0 on the live lines); 8 totals is UNSAT (`uniq.py`).
- **#446 Theorem C floor = star floor** on all realised units checked: P120 bit 72 (all 511 reader sets span Q^8, `t1.py`); P111 bit 63 (exact SAT over all label-decoder decompositions: cost ≤ 62 UNSAT, 63 SAT; `run62.py`, `dec9sat.py`, `p111c.py`); P112 complex frame decoder 64 (`cxp.py`). Decoders differing from B0 off-pattern (rank ≥ 10) are not covered.
- Where slack would have to come from: a total whose readers lie in a hyperplane orthogonal to a punctured line can drop to that line (cost 6 for orthogonal punctured pairs). It does not get P111 below 63.
- Deeper punctures (annealing, 9–26 lines removed), sub-root-system units (D8, E7+A1, A8, …) and mixed units with non-root ports (≥ 14 lines must be removed; best x ≥ 0.67) are all worse. Search results, not exhaustive. Exact W(E8) hyperplane orbit counts: E7 120, D7 1080, E6+A1 3360, A7 8640 (`hyper.py`).
- Asymmetric sinks on P112: 0 of 28,560 target/sink pairs relax for free (floating-point rank, `asym.py`); one extra copy unit frees 2 sinks (matches #595 C.6). Pricing (argued): ≤ 2 × 4.4 helpers × 0.143% ≈ 1.3% b < 2.82% per copy unit, so net negative.

## 3. Levers on #615 / #617 (`r1-cold14/`, details in `REPORT.md`)
Measured on #615's words (#615 re-verified locally: κ 0.001626010676080313):
- **"e2" entering ends are infeasible** at all three Lean (E,U) pairs of #593: the row-cone left-nullity equals the number of helpers already ended (12/24/12) on jp8 and atm3. Cold-mixing directions (542/543/554/555, 566/567/578/579) have no column-cone solution (`nulls.py`, `broad2.py`, `probe2.py`).
- Extra cold dim-8 hyperplane ends all lose (best −5.67e-9 b per call). E1 partners 438/440 can't be replaced by already-lifted registers.
- No PR583-type frame coalescences on jp8, with or without commuting gate moves (the same scan finds #583's six on atm3) (`coal*.py`, `movecoal.py`).
- #615's owner map + dispatch equals the aggregate LP optimum over {jp8, atm3}, even with unlimited windows (`aglp.py`).

**Open lead on #617 (κ 0.001635183729255778):** #617's owner solve stopped at its time limit with remainders {1:24, 2:2, 3:2, 7:2}. The aggregate LP bound (`aglp617.py`) is **+119.3e-9 b** above #617's map at fractional dispatch jp8 60.9 / atm3 11.1. An integer packing at jp8×61 / atm3×11 that meets the bound would give about **+1.1e-7 κ**. `mip617.py` (free-dispatch MIP with Hall constraints) and `expand617.py` (to OWNERS/PLAN) are included; the integer packing is not yet solved or verified.

## Credits
Builds on jeremykothe2 (#591–#601, #607–#617), DreamingOfClouds (#595 format limits, #604, #610), chafreaky (#583, #616), #446 (Theorems A–C), eumemic (#543) and the contributors listed in those PRs. Prepared by Joel Pulikkan (GamingPuzzled) with Claude Opus 5.5 (Anthropic) via Claude Code. Apache-2.0.

## 4. E8 over extension rings and K12 (`s1-extension-rings/`, details in `REPORT.md`)
On the bit side ranks are counted over Q, so a K-line unit is a rank-k unit with k = [K:Q] and h = k·w_K (argued). Exact F2 minrank of the decoder pattern, asymmetric decoders allowed (SAT, no proof logs):

| view | lines v | w | largest non-orthogonal set | minrank | v/w |
|---|---|---|---|---|---|
| Gaussian E8 | 60 | 4 | 12 | 15 (13, 14 UNSAT) | 15 |
| Eisenstein E8 (Witting) | 40 | 4 | 7 | 10 (7–9 UNSAT) | 10 |
| Hurwitz E8 | 10 | 2 | 5 | 5 | 5 |

- In every extension view, minrank = v/w. Real E8's cross-field gain (minrank 9 < 120/8) disappears. Under the full-rank-totals premise that #595 uses for E8's 72, x_K = 1.0, so D ≤ 0: no saving.
- Copy-cost searches (CP-SAT, 900 s, not proven optimal): Gaussian best 60 (proven lower bound only x_K ≥ 0.15); Eisenstein best 40 (x_K ≥ 0.225). Hurwitz symmetric decoders: optimum 10 (x_K = 1). Hurwitz asymmetric decoders: open.
- **Open question:** a structural lower bound Σ_j dim span A_j ≥ ~0.71·v for these units (the threshold to beat bit E8's ceiling at w = 4, float screen). This has the same open status as E8's 72.
- G34 / Coxeter–Todd K12: 126 lines, w = 6, largest non-orthogonal set 15, so x_K ≥ 0.714 even at minrank 15; it loses.
- Complex side (argued): F4-Hermitian (Eisenstein) labels give an alternating F2 trace form, so there are no odd-norm residuals and the phase calculus fails. Gaussian labels reduce mod (1+i) to F2, so they bring no extension.
- Side finding (float screen only, not certified): the paper's original triple family has a higher X* than E8 (~7.4e-3 bit, ~7.2e-3 complex at h = 24, s = 3), but 630 orthogonal neighbours per target (vs 63 for E8) makes its helper cost the issue. X* alone does not rank unit families.
