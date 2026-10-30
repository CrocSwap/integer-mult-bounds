Locally verified conditional arithmetic refinement of [PR #1875](https://github.com/CrocSwap/integer-mult-bounds/pull/1875), exact head `5b06a3fd5f80a6ca3d62f28e04cd650897a5b47a`. This updates our earlier 160-digit candidate in this PR.

**Kappa:** `0.001679754956125544521335670993920702576998311438502580295460327520162864548260325638826305656132844632274451316908586220972070448120165412142771300636692956715734962527390622927714845418099553756337112475558813976784140553038674557881956561879800689254171219767487483694675693056982788922757319255565606685566411725238449650999339827075715283714270157705762309226038611771955655377501414652136546310799999999999999999997996640490086748910957328658012158594846`.

**Gain over PR1875:** `6.06685566612061189440976108244094209914067854870157705762309226038611771955655377501414652136546310799999999999999999997996640490086748910957328658012158594846E-301`. This is an extremely small numerical refinement of the same physical supplier and paid profile, with no new construction or practical speedup claimed.

The new endpoint uses a 10^-400 bracket, checked by two separately implemented rational enclosure algorithms; positive slacks use h=10^-420. All numerical precision parameters are explicit in PARAMETERS.json. Arithmetic replay passed: both endpoint enclosures, 57 strict inequalities, 17 rejecting controls, and the independent balance calculation. Full finite replay passed locally, including fresh native supplier admission. The earlier 160-digit package and its receipts are retained separately; this 400-digit revision has now passed its own fresh full replay. No hosted CI pass is claimed.

Reproduce: `PYTHONINTMAXSTRDIGITS=0 python3 -B research/fine-prime-root400/verify.py --work /absolute/new/work [--arithmetic-only] [--dependency /path/to/pinned/PR1800/package]`.

Conditional on all inherited PR1800/1786/1758/1673 compiler, common-label/mutable-source, hosting, semantic online precision C1=1, fixed-tape/prime-packing, interchange, recovery and analytic assumptions, plus the cited Trudgian prime theorem. Finite arithmetic does not establish the written all-size prime/precision/locality or accretive-circuit arguments. No unconditional theorem, practical cutoff, independent human review or maintainer acceptance is claimed.

Credits: Rohan Arun and the Claude-assisted PR1875 endpoint refinement; Jeremy Kothe and PR1839/1800 contributors; Rohan Arun and the Codex-assisted PR1828/1876 positive-slack replays; Chafik Boukhalfa (PR1786), Tim Trudgian, Vlado Vojdanovski (PR1673), PR1758 contributors, LeverRank, mdumitrean, midhatn, and all retained supplier authors. Original checker sources and notices preserved. Prepared by Rohan Arun with substantial OpenAI Codex assistance. Apache-2.0. No independent human review claimed.

Comparison refreshed: PR1875 head `d31827d128197345be2d8d5649f5103abb2759ba` retains the identical claimed kappa and now reports its full local replay passed. The exact improvement comparison here is unchanged.


Local verification result: `PASS_CONDITIONAL_SLACK_REFINEMENT_FINITE_ADMISSION`. The fresh replay passed both exact endpoint engines, the 57 strict inequalities and 17 rejecting controls, the independent balance calculation, inherited outer checks, the native supplier and strict T74 admission, and the final assembly-to-ledger bindings. The release changes only status metadata and documentation and adds receipts; all mathematical inputs, parameters and verifier code remain byte-identical to the replayed source. Hosted CI remains separate.


Subsequent comparison: [PR #1897](https://github.com/CrocSwap/integer-mult-bounds/pull/1897) at `6dc189fd49c297d28bc4be3778e2ea331a7cff31` reports a higher 500-digit candidate, approximately `8.1185746917580802515643905477766E-401` above this 400-digit result. This PR does not claim the current lead. That package reports a fresh parent replay followed by authenticated reuse for the refined point; it has not been independently replayed here.

Additional exact guard: PR1897 identified an inherited disabled `or True` assertion in `outer/check_gaugefree.py`. Our separate checker expands the two original Gaussian exponents and proves the corrected shift bracket `(1-L)x^2-L(1-L)y^2+d^2-d^2/L+2d(1-L)y`, for nonzero L. The inherited disabled expression has both constant and linear sign errors. Three exact identities and four nonzero polynomial mutation controls pass. Original dependency files are preserved. This strengthens finite identity coverage without changing the supplier profile, numerical parameters or kappa; it does not prove the inherited all-size analytic hypotheses.

For this supplementary coverage, also run `python3 -B research/fine-prime-root400/check_broad_shift.py /absolute/output.json`. Its code and receipt are included. The earlier full replay and this supplemental check are separate executions; no second full replay is claimed for the added files.
