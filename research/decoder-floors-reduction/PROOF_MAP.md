# PROOF_MAP: every claim and premise of README.md and the step that re-runs or proves it

Legend: **RERUN** = executed by `verify.sh`, asserted as a PASS line in `checks/check_logs.py`. **WRITTEN** = proof in the README (arithmetic parts re-run). **CONDITIONAL** = depends on a statement of another PR, named exactly. README claim text is unchanged by this file.

## A. Claims of this package

| README | Claim / premise | Status | Re-run step |
|---|---|---|---|
| 0, 2.1, 2.2, 2.3 | universality (decoders of N0), outside factors free, Sylvester m >= 10, m = 10 => (1,1), Lemma-D form | WRITTEN (finite inputs: none beyond the dense table) | none needed |
| 3.1, 3.2 | projection transfer, pivot bound | WRITTEN, CONDITIONAL (section B: #2816) | none |
| 3.3 | small circuits, m = 10 | WRITTEN, CONDITIONAL (#2724, #2338) | none |
| 3.4 | 1200 directions, |Off| distribution, |O_z| >= 48, minima 0/1/12/13/14, smallest intersections | RERUN | `cat1.py`, `cat2.py` |
| 3.5 | g(8,7,6) = 64, 36, 20 | RERUN | `gtab.py` |
| 3.5 | pair lemma, collinearity, <= 2 weight-7 columns, saving count | WRITTEN, CONDITIONAL (#2816 Lemma 3.1, (C1), (C3)); independent exhaustive check of the pair statement | `pair2.py` |
| 3.6 | 56 twelve-overlap sets, label span dim 7; Omega unique, rank 9, Omega(z_i,z_j) = 1; 119,616 cases | RERUN | `d4.py`, `omega.py` |
| 4.1, 4.4, 4.5 | multiplicity inequality, fold barrier, Lemma RR, covering ceiling | WRITTEN | none |
| 4.2 | Theorem TF; anchor batches (0,0), (0,1), (0,5): 64+64 / 72+72 / batch 136, 137 | WRITTEN + RERUN | `fold.py` |
| 4.3 | transport: dim span lab(R_t) = 8 for 112 lines, 2 transportable labels | RERUN | `transport.py` |
| 4.6 | Theorem C rank budget, Lemma K' count 64k - 1, Lemma E bounds 64k + 7 / + 63, Theorem M minimisations 64 + 56 k2 and 64 k1 + 48 k2 | RERUN (exact arithmetic) | `c_batch_arith.py` |
| 4.6 | digon clique: rank E = 64, col E and row E meet no class span | RERUN | `c_clique_lemmaE.py` |
| 4.6 | **the 72 arcs of the clique realised by explicit GL(9,F2) charts** (README: "RECORDED ... not shipped") | **FIXED: now RERUN** (66 charts, every slot normal and h.g = 1 verified) | `glclique.py` |
| 4.6 | Theorem M premises: P112 8 avoidable hyperplane classes, pair ranks {8: 64}; P104 (4 variants) 16 classes, {8: 192, 7: 64} | RERUN | `p104prem.py` (reads `data/p104reps.json`) |
| 4.6 | sharpness of Theorem M assumes each P104 call's coordinate decoder costs 56 | **FIXED: now RERUN** (exact 8-term decoder on 104 live lines, ranks 7^8, cost 56) | `p104dec56.py` |
| 4.7 | 28 twin pairs per coordinate; 56 cases with a twin block at Phi = I | RERUN | `twinblk.py` |
| 4.7 | closed in 277/512 cases; open: saving 8 x 11, saving 7 x 224 | RERUN | `s1close.py` (uses `dangle.py`) |
| 5 K6 | **break-even prices 51 / 46 / 42 at h = 12 / 13 / 14** (README: "RECORDED ... not re-run here"), plus the h = 11 value 55 | **FIXED: now RERUN** (~75 s, standard library; model code shipped unchanged in `checks/price/`) | `checks/price/price_breakeven.py` |
| 5, 6 | named conjectures K-P120, K1..K6, residues R1..R4 | OPEN by definition (statements of gaps, no claim of truth) | none |
| manifest | every package file is hash-listed | RERUN | `manifest_check.py` |

## B. Merged dependencies: rechecked by their own verify (FULL=1 runs `verify_deps.sh`)
All of these PRs are merged. `verify_deps.sh` runs each package's own `verify.sh` unchanged from the repository checkout (siblings `research/<pkg>/`), and prints one line per package. Status of the last run (logs not shipped, they are the packages' own):

| PR | package | status |
|---|---|---|
| #2816 | one-sided-decoders-all-m (Lemma 3.1, R1-R4, cover.py/d7.py, direction-list completeness, g(5) = 12) | merged and rechecked: 34 PASS, 0 FAIL |
| #2724 | nine-term-outside-colspace | merged and rechecked: ALL PASS |
| #2826 | one-sided-six-multisets | wired; the run was terminated externally (rc 143) before finishing, so NOT yet rechecked here |
| #2819 | e8-rank9-realisations | wired; its default run SKIPs the DRAT step because `drat-trim` is not installed on this machine, so NOT yet rechecked here (needs `DRAT_TRIM=`) |
| #2784, #2639, #2806 | a2-family-decoder-floors, decoder-floors-closures, punctured-e8-48-56 | wired; not yet completed in this session |
| #2719, #2694 | dn-unrestricted-root-code-floor, overcomplete-rank-interface (registered replay `scripts/research_package.py`; #2694's Lean part needs the pinned Lean/Mathlib toolchain of its README) | wired; not yet completed in this session |

Until a package shows PASS above, the claims that import it stay conditional on that merged PR's own verify.

## C. Still conditional
1. The dependencies in the table above that do not yet show PASS (exact dependency: that package's `verify.sh` passing, plus `drat-trim` for #2819 and the pinned Lean toolchain for #2694).
2. K6/K-P120: break-even prices are outputs of the shipped pricing model (`checks/price/`), not floor theorems.

## D. Reproduce
`bash verify.sh [outdir]` (about 6 minutes, at most 3 processes); `FULL=1 bash verify.sh` adds `verify_deps.sh` (hours). Logs of a run are in `logs/` (`*.log.txt`).
