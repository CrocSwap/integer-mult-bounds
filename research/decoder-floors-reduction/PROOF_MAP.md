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
| 4.6 | sharpness of Theorem M assumes each P104 call's coordinate decoder costs 56 | CONDITIONAL, see C1 (README already says "not re-checked") | none |
| 4.7 | 28 twin pairs per coordinate; 56 cases with a twin block at Phi = I | RERUN | `twinblk.py` |
| 4.7 | closed in 277/512 cases; open: saving 8 x 11, saving 7 x 224 | RERUN | `s1close.py` (uses `dangle.py`) |
| 5 K6 | **break-even prices 51 / 46 / 42 at h = 12 / 13 / 14** (README: "RECORDED ... not re-run here"), plus the h = 11 value 55 | **FIXED: now RERUN** (~75 s, standard library; model code shipped unchanged in `checks/price/`) | `checks/price/price_breakeven.py` |
| 5, 6 | named conjectures K-P120, K1..K6, residues R1..R4 | OPEN by definition (statements of gaps, no claim of truth) | none |
| manifest | every package file is hash-listed | RERUN | `manifest_check.py` |

## B. Cited from other PRs (not re-derived; not private cards)

Merged: #1212 (rank-8 rigidity), #2338 (Theorems P, R, B, Bk; Lemma D), #1714, #968, #1633 (as cited in README section 1).
Open or draft, so every dependent claim is CONDITIONAL on the PR landing: #2816 (Lemma 3.1, R1-R4, cover facts C1/C3 (`cover.py`, `d7.py` live in that PR, not here), completeness of the 1200-direction list, g(5) = 12), #2724, #2826, #2819, #2784, #2639, #2806, #2719, #2694.
Each is named in the README row it supports ("CONDITIONAL on #n"). `cat1.py` regenerates the 1200-direction list; only its completeness is imported.

## C. CONDITIONAL items, exact dependency

1. Sharpness of Theorem M (not a lower-bound claim): the cost of a P104 call's coordinate decoder being exactly 56. Needs a re-run of the decoder-cost evaluation on P104; not shipped here.
2. All rows in section B marked open/draft: the named PR.
3. K6/K-P120 as stated: the break-even prices are outputs of the shipped pricing model (`checks/price/`), not theorems about all decoders; the README already presents them as pricing, not as a floor.

## D. Reproduce
`bash verify.sh [outdir]` (FULL=1 accepted; the default run already executes everything, about 5-6 minutes, at most 3 processes). Logs of a run are in `logs/` (`*.log.txt`).
