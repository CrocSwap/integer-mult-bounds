# C(P112) >= 64: complete reduction to stated conjectures

No kappa claim, no window, no supplier word.  Pure finite combinatorics on the E8 root lines and the unit P112, in the line of #2816, #2832, #2985, #3029, #3040, #3045, #3049, #3074 and #2854.

## What this package contains
- The reduction of C(P112) >= 64 to the conjectures C1-C7 of `CONJECTURES.md` (via #2832: K1 two-sided + K2 one-sided; K2 via #3074 needs only the L120 residue).
- One-sided: the ledger of #3049 (38 open rows) updated to **37 further rows closed** with per-row certificates, each shipped with two (mostly three) implementations; 602 of 603 rows are KILLED; row 579 is CONDITIONAL on C6 (DEG2). The 7 rows of the (6,6,5) s0@T7 span run (381, 384, 576-578, 580, 581) are KILLED by two implementations (original s3y run + independent s3z rerun, 192/192 slices, 0 cracks). `data/ledger3_consolidated.csv` (603 rows) is recomputed by `verify.sh` from `data/ledger2_consolidated.csv` + `data/new_kills.csv`.
- Two-sided: BUDA11, Theorem S with -n01, Theorem DR', TWOSIDE Lemma BK, F7, BX extension, FINITE alpha/beta, CONJG2 reductions.
- `PROOF_MAP.md` (claim -> check), `checks/` (self-contained copies of every script, small output and note; no absolute paths), `MANIFEST.sha256`.
- Audits applied: AUD-1, AUD-2, AUD-3, AUDIT-IMP, AUDIT-TS (fixes: E6A1 exclusion via KILL-A8 (a); 399 needs the s=6 scenario (II)/(III) argument; G3 dependency for 596-601 plus the target-completeness check; Theorem S and BUDA11 use the sound P2 with -n01 (G2-BUDGET P2 as first stated overcounts by 1 per cost-0 (8,1)/(1,8) term); the (1,t) closure is Lambda_P + n01 <= t-1).

## How to check
`bash verify.sh [outdir]` (Python >= 3.11 with numpy; `PYTHON=...`).  Default run: manifest, ledger recomputation, 15 independent reruns (a few minutes, <= 3 processes).  `FULL=1` adds the heavy reruns listed in `checks/full.sh` (which calls `full_a.sh`, `full_b.sh`, `full_c.sh`, `full_c/res/asm_check.sh` and `PRIOR7/rerun.sh`, each writing its own log; PRIOR7 alone is about 4 CPU-h). The heavy FULL was not rerun at integration; the recorded evidence of a completed rerun is `evidence/full_a.log`, `full_b.log` (four labelled partial runs), `full_c.log` and `evidence/prior7/`; the SAT/DRAT and table-based claims are regenerated from the shipped encoders (kissat, drat-trim required) in chunks of < 20 minutes, and their big CNF/DRAT/table artefacts are not shipped.

## Honesty box
- Row 579 is CONDITIONAL on C6 (DEG2); partial evidence only (impl A).
- Two-sided is complete only modulo C1-C5 (C5 = FINITE beta R = 7, p = 4 only; p = 2 is resolved); nothing here proves K1.
- Claims marked R in `PROOF_MAP.md` have shipped sources and hash-pinned recorded outputs; they were audited (see the audit files) but are not re-executed by the default `verify.sh`.
- The DP/LP filters behind the d >= 1 lists are shared imports (OS-CHARGE2).

Files: `CONJECTURES.md` (statements of C1-C7), `PROOF_MAP.md`, `checks/<CARD>/NOTES.md` (proofs and reasoning of each card), `data/`.
