# Fixed-grid kappa ceiling over PR2161

This is a further conditional arithmetic improvement over PR2161. It reduces only free positive proof gaps to r0=10^(-30080), retaining the supplier endpoint C, the kappa floor denominator F=10^30046 and the backoff B=10^(-30022). The exact new kappa is **C-1/F-B**, the maximum admissible point in this declared fixed-grid family. The gain is about 2.00168139534e-30010, so this is still numerically tiny and is not a material paid-supplier improvement.

PROOF.md derives the strict-grid bound and its attainment. The verifier checks all 62 original inequalities, an explicit main-binding invariant, the 17 original mutation vectors, independent cost equations and the exact gain over the frozen PR2161 claim. Parent sources, native words, owners and invoices are unchanged.

The fast registered hook runs `verify.py`. Run the fresh provider-point check first; complete finite binding also requires the same personally replayed supplier and parent outer work as PR2161: run `verify.py --supplier-work SUPPLIER_WORK --outer-work OUTER_WORK --outer-log OUTER_LOG --out RESULT_FILE`. Fresh high-precision checks at the new interior point use `check_provider_point.py --out PROVIDER_RESULT`; optional gmpy2 acceleration is supported by the unchanged engines. Public evidence contains no private paths, machine identifiers or raw local logs.

The parent aggregate Linux CRLF/LF reproduction limitation and the pre-existing broad split-skip source-pin failure remain disclosed in PR2161. No whole-repository green, hosted-CI pass, new supplier endpoint, formal theorem or independent human review is claimed. All inherited hypotheses remain conditional.

Credit PR2161, PR2044 and Jeremy Kothe's package; PR1786 (Chafik Boukhalfa / Tim Trudgian), PR1673 (Vlado Vojdanovski), PR1758, and the retained T74 supplier, native and precision-repair lineage. Source notices preserve detailed attribution. Prepared under dataisfire with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

A material gain needs a cheaper complete paid construction. Fixed-inventory T74 packing already has only rank-48 idle blocks. The screened early-query route fails once one additional rank-seven carrier is charged, even with favorable idle-volume credit; this is a scoped negative, not a universal obstruction. Further decimal tuning of this fixed grid/backoff family cannot improve its attained cap.
