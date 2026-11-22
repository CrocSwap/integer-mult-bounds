# PROOF_MAP: every claim and premise of README.md, mapped to the step that checks it

Attachment only; no claim text of the README is changed. "verify N" = section N of `verify.sh` (default mode unless marked FULL=1); "replay F" = a line of `provenance/replay_spanfacts.sh` (run by `verify.sh` in FULL=1 step 6; shipped log `provenance/logs/REPLAY/replay_summary.txt`). A statement whose proof is a written argument (README §2-§5) is mapped to the finite computations that argument uses; the argument itself is the proof and is not a computation. Items that cannot be rerun are listed under CONDITIONAL.

| # | Claim / premise (README) | Checked by |
|---|---|---|
| R1 | `s = 7` forces Class I (§2, Z-lemma, peeling) | written proof §2.1-2.3; inputs: peeling and lift identity (CONDITIONAL, inherited), flat cap `g(8) = 64`: verify 1 "g(1..8) = 1,2,4,8,12,20,36,64" |
| R1' | `s = 6` scenarios (§2.4), `scen()` kill engine tests base cell and all variants | verify 5: `run_rrc.py` ("RRC engine ran; every certificate re-verified by verify()"), `lemp_audit.py`, `check_ledger.py` |
| R2 | Circuit Lemma (§3), G1 root counts (`57` / `>= 78`) | written proof §3; G1 is classical (CONDITIONAL), consistent with the direction census of verify 2 (`dirs.py`: min `|Off|` of non-roots = 70/77+) |
| R3 | Relative root counting (§4) and the immediate rule | written proof §4; finite inputs `g`: verify 1 `gtab.py`; `N_2 = 3`, `N_3 = 6`: verify 1 `nj.py` ("N_2 = 3", "N_3 = 6"); `N_4 = 12`: verify 1 FULL=1 ("N_4 = 12 (exhaustive)"); `N_5 = 20`, `N_6 = 36`: CONDITIONAL (ADE classification); every certificate: verify 5 `run_rrc.py` |
| R4 | Lemma P / P' (§5), parameters `(sigma, omega')` table | written proof §5; covering facts (a)-(f), `params`: verify 3 (`cov.c` targets) + verify 4 (`anroot.py`, `annon.py`, `facts_check.py`: "facts" PASS); parameters and 375 kills / 74 original reproduced: verify 5 `lemp_audit.py` ("Lemma P at T-level kills 375 of the 603 rows", "all 74 original class-A kills reproduced") |
| R4a | Fact D, direction list `|Off| <= 89` (112 roots, 8 frame, 21,340 non-E8 masks in 17 orbits) and the 3584 directions with `|Off| = 89` | verify 2: `mkgroup.py` (group order 172032), `dirs.py` ("non-E8 21340"), `mkreps.py`; harmlessness of the 89 orbit: verify 4 `facts_check.py` |
| R4b | Exact covering enumerations behind the facts (17 targets) | verify 3: root target and `non05_79`, `non06_80` recomputed by default; the other 15 are shipped outputs in default mode (RECORDED) and are all recomputed and compared with `data/left_*.txt.gz` under **FULL=1** (one run shipped: `evidence/verify_full_run.txt`) |
| R4c | D7 plane fact | verify 4 `d7plane.py` |
| R4d | Lemma P' extremal inequality, `m = 10`: `6 omega' >= 504 - 273`, `omega' >= 39 > 32` | arithmetic in §5; the remark "brute-force check over 3000 random maximal triple systems" is not used by any kill and is not re-run: CONDITIONAL (remark only) |
| R5 | Consolidated ledger: 480 KILLED, 7 KILLED(prior-only), 116 OPEN, table of §6, all 47 class-B, 25 root-count, 74 class-A kills | verify 5 `build_ledger.py` + `check_ledger.py` ("byte-identical to the shipped ledger"; counts 480/7/116) |
| R5a | The 7 KILLED(prior-only) rows rest on an earlier `(6,6,5)` span run at target 7 | CONDITIONAL (see below); the README already labels these rows prior-only and counts 123 OPEN without them |
| R6 | `robust6` base-configuration gap (no result changed) | verify 5: the shipped engine tests the base cell; ledger recomputed identically |
| R6a | Fact D correction (3584 directions with `|Off| = 89`) | verify 2 `dirs.py`, `mkreps.py`; verify 4 `facts_check.py` |
| G | Setting premises of §1: `g(1..7)`, `g(8)`; E8 model | verify 1 `e8.py`, `gtab.py` |
| G' | Inherited premises of §1: `|Off(h)| >= 53`, peeling, lift identity, Lemma B / kill criterion, classical root-system facts, ADE classification, Borel-de Siebenthal | CONDITIONAL (statements of earlier PRs and textbooks, cited); `|Off| >= 53` is consistent with the complete direction list of verify 2 |
| I1 | Input list: `rows_input.csv` has 603 distinct well-formed rows | verify 5 `check_ledger.py`; production: `provenance/reproduce.sh` (dominance filter reproduces the 603 rows from `generator/land7.out`; FULL=1 also reruns `land7.py` and compares) = verify 6 (FULL=1) |
| I2 | The eight span facts used by the dominance filter (`provenance/SPANFACTS.md`) | `provenance/replay_spanfacts.sh`, one line per fact: replay F1 (6,6)+1<=3 `s66.c` and independent `indep.py`; F2 (6,6)+2<=4 `s6x.c`; F3 (6,6,3)s0<=4 `s6x.c` + exact refinement; F4 (7,4)s0<=4; F5 (7,5)s0<=4 (+ `|Off|<=88` pass `s3x.c`); F6 (6,6,4)s0<=5 `s3f.c`, `s3y.c` (`|Off|<=88`, target 6 pass, target 5 crack), `s3x.c` pass, second implementation `s3z.c`; F7 (6,5,4)+1<=4; F8 (6,4,4)+1<=4 (F6-F8 also with `s3z.c`) |
| I3 | Direction lists `data.txt` (<=77), `data80.txt`, `data88.txt` and `gens.txt` | replay "direction lists regenerated" (`provenance/src/gen.py`, `gen88.py`; `data88.txt` and `gens.txt` compared with `provenance/data/`) |
| I4 | Completeness of the earlier enumeration of the `d >= 4` residue list (necessary conditions of #2816, Basis-Lemma kills of #2826/#2862) | CONDITIONAL (stated in the README as an input) |
| E | `evidence/logs` timing logs and `N_4` log; `evidence/verify_run.txt` | logs of earlier runs; superseded as checks by verify 3 / verify 1 FULL=1 and `evidence/verify_full_run.txt` |

## CONDITIONAL (cannot be rerun here)
1. Inherited statements of earlier PRs (peeling, lift identity, Lemma B, `|Off| >= 53`, flat caps `g(1..7)` as used in #2816) and classical theorems (ADE classification, Dynkin, Borel-de Siebenthal): cited, not computations. `N_5 = 20` and `N_6 = 36` rest on the ADE classification (no exhaustive run; the exhaustive run for `N_4` is the FULL=1 one).
2. The 7 prior-only rows: need the earlier `(6,6,5)` s0 span run at target 7 (single implementation, not re-audited, sources and logs not part of this package).
3. Completeness of the 603-row input list (earlier enumeration); only the dominance filter and `land7.py` are rerun.
4. The remark on 3000 random triple systems (§5, Lemma P'); no kill uses it.
5. Span facts are single-implementation except F1 (two implementations) and F6-F8 (`s3f`/`s3y` against the independent `s3z`; same algorithm family, written separately); a run at target 8 proves only span <= 7 and the stated bounds are the maxima the runs report (see `provenance/SPANFACTS.md`).
