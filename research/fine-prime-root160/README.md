Draft conditional arithmetic refinement of [PR #1839](https://github.com/CrocSwap/integer-mult-bounds/pull/1839) at `836ef6a1a550f439e42be65423cffd624658af6a`.

**Kappa:** `0.001679754956125544521335670993920702576998311438502580295460327520162864548260325638826305656132844632274451316908586220972070448120165412142771300636692956715699999999999999999997996640490086748910957328658012158594846`.

**Exact gain:** `6.56132844832610402308233695125239204646904306012142771300636692956715699999999999999999997996640490086748910957328658012158594846E-91`. This is an extremely small numerical improvement of the same conditional construction. The physical supplier and paid profile are unchanged; no practical speedup or new construction is claimed.

The supplier moment is enclosed on a 10^-160 grid by two independently implemented rational algorithms. Positive slacks use h=10^-180, epsilon=1-2h and beta=1-6h. The endpoint upper neighbour is rejected, and the two ledger calculations must agree on the exact candidate. Arithmetic replay passed: both endpoint enclosures, 57 strict rational inequalities, 17 rejecting controls, and the separate nine-cost balance derivation agree. Full finite replay is pending. No hosted CI pass is claimed.

Reproduce arithmetic: `PYTHONINTMAXSTRDIGITS=0 python3 -B research/fine-prime-root160/verify.py --work /absolute/new/work --arithmetic-only`.

For full replay, omit `--arithmetic-only`. The immutable 381-file PR1800 dependency is fetched and checked, or supplied with `--dependency`. The actual assembly profile is bound to the new two-engine certificate; the old supplier admission endpoint is retained as a weaker valid value. All outputs stay under the explicit work directory. Ready status requires the full replay to pass.

Conditional on all inherited PR1800/1786/1758/1673 compiler, common-label/mutable-source, hosting, semantic online precision C1=1, fixed-tape/prime-packing, interchange, recovery and analytic assumptions, plus the cited Trudgian prime theorem. Finite arithmetic does not establish the written all-size prime/precision/locality or accretive-circuit arguments. No unconditional theorem, practical cutoff, independent human review or maintainer acceptance is claimed.

Credits: Jeremy Kothe and contributors, PR1839 endpoint refinement and PR1800 composition; Rohan Arun PR1828 slack replay; Chafik Boukhalfa / chafreaky PR1786 and Tim Trudgian's prime theorem; Vlado Vojdanovski PR1673; PR1758 contributors, LeverRank, mdumitrean, midhatn, and all retained PR1319/1297 supplier authors. Full predecessor notices and original checker sources are preserved. Prepared by Rohan Arun with substantial OpenAI Codex assistance. Apache-2.0; no independent human review claimed.
