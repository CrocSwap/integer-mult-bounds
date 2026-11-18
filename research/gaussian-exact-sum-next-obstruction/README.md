# A stronger exact-sum Gaussian rounding obstruction

Every injective, exact-sum Gaussian-pair rounder with Euclidean error
at most one needs forward norm slack at least **sqrt(13)-3** (about
0.605551275464). This raises the necessary bound sqrt(5)-sqrt(3)
(about 0.504017169931) in [PR #7652](https://github.com/CrocSwap/integer-mult-bounds/pull/7652).
Eighteen inputs have only sixteen legal outputs below the new threshold.
An explicit matching attains it on all 22 sum-one inputs with squared
norm at most 13. No period or square identity is assumed.

This is a scoped proof with an exact finite certificate. Read
[PROOF.md](PROOF.md), [MATCHING.json](MATCHING.json) and
[RESULT.json](RESULT.json). Global attainment is not proved. No new
kappa, supplier admission or selected-assumption discharge is claimed.

## Evidence and reproduction

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -I -W error -B research/gaussian-exact-sum-next-obstruction/verify.py
python3.12 -I -W error -B -O research/gaussian-exact-sum-next-obstruction/verify.py
python3.12 -B scripts/research_package.py --package research/gaussian-exact-sum-next-obstruction
python3.12 -B scripts/check_research_commit.py --package research/gaussian-exact-sum-next-obstruction --check-source-history --check-modes
```

Expected statuses are PASS_GAUSSIAN_EXACT_SUM_NEXT_OBSTRUCTION,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES.
The verifier checks all 88 legal edges, the complete Hall neighborhood,
the 22-edge matching, direct four-coordinate Gaussian errors, exact root
comparisons, two maximum-matching sizes and four rejection controls.
The receipt is checked in normal and optimized modes. No predecessor
scientific replay, selected cold replay, Lean or Docker run is required
or claimed. Independent human and formal-kernel review remain open.

## Source and overlap

The package starts from canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`, with priority revision 8 and
selected PR #7000 unchanged. [SOURCES.json](SOURCES.json) pins the task,
selected record and the predecessor question. The predecessor is
[PR #7652 at 317fecee459888f4e4fecd8ca62adeb7583f696d](https://github.com/petalas/integer-mult-bounds/blob/317fecee459888f4e4fecd8ca62adeb7583f696d/research/gaussian-exact-sum-forward-slack/README.md).
Its candidate formula is derived again in the proof; no source code is
copied. The verifier needs no predecessor file at run time.

The overlap pass covered 972 open PR bodies, 6175 closed PR bodies and
7603 Discussion records, with complete remote pagination on 2026-11-18.
The sparse local note search covered 106 of 10178 tracked notes, so this
is not a complete novelty certificate. The live handoff had no competing
reply before the [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19702072).
PR #7651 concerns an unrestricted four-coordinate graph. PR #7570 adds
a square-to-swap identity. PR #7572 already treats affine-period slack;
that idea was dropped before this investigation.

## Open next questions

Can a global exact-sum injection attain the new threshold, or must it
have greater slack? First seek a structural matching or Hall argument
that treats the whole sum-one lattice. A larger successful finite check
alone does not answer this question. A physical implementation would
also need an inverse/caller contract, a range proof and a complete cost
invoice. [TASK.json](TASK.json) records these obligations.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Nick Petalas supplied the lower-bound question and candidate formula in
[PR #7652](https://github.com/CrocSwap/integer-mult-bounds/pull/7652).
Jerry Chen supplied the fixed-sum matching context in
[PR #7570](https://github.com/CrocSwap/integer-mult-bounds/pull/7570).
Ali Romman supplied the ideal Gaussian pair in
[PR #6509](https://github.com/CrocSwap/integer-mult-bounds/pull/6509).
The new obstruction does not require the extra order identity of PR #7570.
New work is Apache-2.0; the repository license applies.
