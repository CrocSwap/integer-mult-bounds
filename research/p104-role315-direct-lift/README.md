# Conditional κ = 0.0036502223357: one productive-helper315 lift

This candidate improves the exact published [PR7603](https://github.com/CrocSwap/integer-mult-bounds/pull/7603) invoice by replacing helper315's two unobserved rank-one moves with one rank-two move. The verified conditional claim is **κ = 0.0036502223357**. Directed pricing and fresh complete native/signed application checks pass. Five inherited framework assumptions remain. This package does not change the selected result or claim a complete unconditional multiplication theorem.

The sole new word edit is against PR7603 commit `3f031ccb7ae7229a7323b1601877f24a46dfcf57`: delete event42077 `MOVE 315 729→789`; replace event42156 `MOVE 315 789→808` with `MOVE 315 729→808` at that later position. All other events are identical. The 78 intervening events never reference315. The strict nested frame dimensions are4→5→6. Crucially,315 is a productive public helper: its arbitrary-input identity and initial/final charts3→127 remain unchanged, so its productive target survives.

[PROOF.md](PROOF.md) gives the operator telescope, exact phase/adjoint and tensor-product scope, helper-target argument, signed invoice and stopping result. In the unchanged17-call caller:

| Quantity | PR7603 | This candidate |
| --- | ---: | ---: |
| Paid recursive positions | 110400 | 110383 |
| Productive positions | 22461 | 22461 |
| Rank surplus | 1424 | 1424 |
| Paid histogram change | — | P₁−34, P₂+17 |

For `0 < C < 1`, the target-minus-paid moment improves by exactly `17(2−2^(1−C)) > 0`. This changes paid work; it is not a more precise decimal for an unchanged crossing. The certified PR7603 crossing upper bound is `0.003650000454084`; the stated new claim exceeds it by `0.000000221881616`. The new crossing is bracketed by `[0.0036502223358272, 0.0036502223358273]` using256-bit integer power bounds, separately from the application engine's directed bounds. See [data/PRICE.json](data/PRICE.json).

## Verification and reproduction

Python3.12, standard library only, no network or foreign Git commits needed for the mathematical replay:

```sh
python3.12 -I -B research/p104-role315-direct-lift/verify.py
python3.12 -I -B research/p104-role315-direct-lift/independent.py
python3.12 -I -B research/p104-role315-direct-lift/physical.py
python3.12 -I -B research/p104-role315-direct-lift/price.py
python3.12 -I -B research/p104-role315-direct-lift/application.py --stage native
python3.12 -I -B research/p104-role315-direct-lift/application.py --stage signed
```

The registered equivalent is `python3.12 -B scripts/research_package.py --package research/p104-role315-direct-lift`. Its six commands have an1190-second total timeout budget. The full application stages run sequentially in isolated temporary directories and compare fresh deterministic receipts with committed expectations. Execution timings are excluded from mathematical equality. Regenerated gzip payloads, not compressed container hashes, determine equality. Exact hashes still bind immutable source archives.

- `verify.py` authenticates100 retained files, including exact PR7603 archive members, and reconstructs the unique edit and complete invoice.
- `independent.py` imports no predecessor checker or builder. Independent forward legality and reverse rational propagation compare PR7546, PR7601, PR7603 and this candidate on all1501 arbitrary public inputs, all1569 final rows and all74 pre-CLEAR rows. It checks helper315 identity/target, all owned lifetimes and the fixed caller residual. Coefficient grid remains denominator exponent25, odd factor1125, numerator bound40bits. Incorrect chart, premix/correction coefficient and hidden-erasure controls reject. These checks also pass under `-O`.
- `physical.py` checks all512 forward columns,512 adjoint columns and512 rank-two columns, including absolute phase. Dropped quadratic phase and wrong global phase reject. It independently enumerates the permitted fusion family.
- `price.py` proves uniform concave improvement and directed signs at the prior upper bound, public claim, compiler probe, and both sides of the new crossing. Restoring the old costs rejects the new claim.
- `application.py` authenticates the unchanged PR7546 engines, applies counted explicit adaptations in scratch space, and rebuilds the complete native, signed caller, invoice, ordinary work, Gaussian chart operators, physical catalogue, coefficient/precision and fixed tape bounds. The full58 outer predicates are checked at the framework claim and the conservative public claim; the public gate's tape inequality is also checked. Every affected public chart route receives all512 forward and512 adjoint columns. No historical receipt alone is accepted as a new execution.

`data/NATIVE.json`, `data/SIGNED.json` and `data/FINAL.json` record the complete application:3039 catalogue maps,104 main-boundary pairs,17 native calls, ordinary work782716348<10^9, precision factor2430, and54 strict+4 functional outer checks. The stronger fully checked framework claim is0.003650222335827; the stated conservative claim follows by weakening, with its own public-gate tape inequalities also verified. `data/independent.json` and `data/PRICE.json` record the separately authored rational audit and the integer-power bounds. The execution environment and final registered replay are described in `VALIDATION.md`.

## Source, overlap and scope

Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`. The selected reviewed bound at that base remains κ=`0.00363005817`; pending improvements are not selected admission. The revision8 task card is preserved as historical orientation in TASK.json. Exact live predecessors are:

- SYLforge PR7603 `3f031ccb7ae7229a7323b1601877f24a46dfcf57` (two contractions and removed315 observations).
- DreamingOfClouds PR7601 `eccf3d1fe814ea86a373d37a783105ceb853c390` (token settlement).
- ToikY PR7546 `99438c43df7aac1e5dbcc43c1578fcd886c119ec` (complete application), with the retained PR7113 signed caller and all embedded predecessor notices.

The investigation first independently found the166 contraction on7601. A fresh overlap check found the concurrent, stronger7603 submission; that overlapping candidate is not published as a novel result here. This package instead adds the315 step on7603. The canonical [investigation claim and updates](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19613348) and `data/overlap.json` record the transition. Overlap searches are bounded coverage leads, not a novelty proof.

All required historical code and certificates are retained because the complete replay executes them. The unchanged7603 published archive authenticates its word and invoice. SOURCE-VERSIONS.json binds retained bytes and credit without requiring unmerged commits in a clean checkout. SOURCES.json binds only historical base provenance through Git. No selected-result, shared-code or frozen predecessor file is edited.

The fixed-scalar family permits only sequential fusion of two strictly ascending MOVEs with no intervening access to that same field. It has exactly one candidate on7603 and none after this edit. On the inherited BIT-admissible interval `[0,0.00376669]`, `ceiling.py` certifies a strictly negative moment derivative and its unique raw crossing. This finite family’s raw-moment ceiling is below `0.0036502223358273`, leaving less than `1.273e-13` between the conservative claim and that ceiling. This is not a bound on other scalar words, interfaces, stock, schedules or integer multiplication.

The remaining conditional assumptions are `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`. Finite all-column checks, source-bound application replay, and a scoped algebraic substitution do not discharge all-width framework premises, constitute formal-kernel verification, or replace independent human review.

## Open next questions

1. Can a changed scalar observation pattern enable another paid MOVE fusion on this exact word? The fixed-scalar family is exhausted. First identify one legal premix/correction that removes an observation, then compare all output/erasure rows and the complete signed bill before root search. The blocker is a legal rewrite with every correction, ordinary and precision cost charged; no further gain is asserted.
2. Does an independent reviewer confirm the complete conditional application? Start with the registered replay, PROOF.md, explicit source adapters and fresh receipts. Substantive independent review and the five inherited assumptions remain blockers to admission.

Prepared by Hao Yan (@FanPUYen), with substantial OpenAI Codex assistance in search, implementation and checking, including separately scoped agents for mathematical and application review. These are independently implemented checks and separate agent reviews, not independent human review. Apache-2.0; all predecessor attribution and source-specific notices are retained.
