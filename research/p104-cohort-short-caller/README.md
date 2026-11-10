# Native/caller composition: conditional κ .003638885999709

This package composes dillona's exact [#7115 native](https://github.com/CrocSwap/integer-mult-bounds/pull/7115) with Rohan Arun's exact [#7113 signed 17-stage caller](https://github.com/CrocSwap/integer-mult-bounds/pull/7113). The complete conditional claim is **κ = .003638885999709**, up **.000000570171393** over #7115 and **.000000906229709** over #7113. Both the native word and literal caller retain their predecessor bytes. The new result is their fully recomputed composition and source-specific component application, with explicit invalidation of same-native caches.

| Input | Exact public head | Canonical artifact SHA256 |
|---|---|---|
| #7115 native | e63533f866455aa5cbc6c405770c31126d76e340 | ae30929ff3b5f6b49a5edac78e2164acfbf809113d0b9f03249ef940dd7b2491 |
| #7113 caller | 07a76c5e2738882c0cb322278e56f6cae3c9885d | 255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc |

The first hash covers the entire decompressed canonical native word; the second covers the complete literal caller JSON. `INPUTS.json` pins all 21 native-package and 76 caller-package files by SHA256 and Git blob. Their nested source archives, licenses and notices are preserved. The selected frontier is unchanged.

## Complete result

The native has 72,833 events, 1,485 public fields and 1,085 independent helpers. The caller has 4,783 events, 72 logical output fields and 17 native invocations. Its current application allocates 18,445 independent stage/helper inputs and 867 native owned banks. Each invocation includes all 51 owned labels and their checked lifetimes. There are 13,600 native contact boundaries on 145 ambient axes.

Compared with #7113, the full paid histogram is identical and the productive delta is `{3:+17,6:+17,9:−17}`. Thus the exact concave margin increases by `17(3^p+6^p−9^p)>0` for every `0<p<1`. The recomputed complete invoice has **110,638 paid positions**, **22,189 productive fields**, rank surplus **1,424**, and zero empty-root credit. The independent raw crossing is

```
(0.00363888599970985077388460370351374,
 0.00363888599970985077388460370351375).
```

The claim is `3638885999709/1000000000000000`. Both predecessors' complete invoices reject it. It is a new combined profile, not more digits of either old root. This bracket is the fixed-invoice ceiling; the paired BIT pin .00376669 leaves .000127804000291 of parameter headroom, without asserting that it is attainable.

The complete source-unit ordinary bound is **776,298,440 <10^9**, including all native and caller scalars, signed routes, native input conversions and the separate caller odd-scale conversions. The native grid remains scale 1125 with fractional height 24. The caller uses scale 675 with binary valuation 381; the independent integer Laurent replay checks all 176,874 required coefficient/product instances and rejects insufficient powers of 3 and 5.

Reusing #7113's native envelope would be wrong: the fresh composition has context height **405**, mass exponent **1164** and allowance **2328**, versus the predecessor's 2314. The new value remains below the retained 4096 allowance and is checked against the exact compiler threshold. All 54 strict and four functional outer inequalities pass with H=16480300000000000000000, logarithm power 2233 and gap10⁻¹⁷. `APPLICATION.md` explains the occurrence, common-grid and physical upper-cost substitutions.

## Verification and cache invalidation

```
python3.12 -B scripts/research_package.py --package research/p104-cohort-short-caller
```

The first registered command authenticates both complete exports and replays #7115's source reconstruction, exact cut, arbitrary-input forward/adjoint, grids, original caller/bills/precision/outer gates and finite physical checks. This validates the native ingredient; it does not substitute the old caller for the new one.

The second command reconstructs both source invoices and the literal 17-stage caller, reruns its rational and integer Laurent endpoints, and recomputes every affected component. Counted edits in `adapt.py` replace same-native receipt reuse with fresh native adjoint, grid and envelope execution. They apply only to temporary copies. The original caller construction and all physical-binding, integer-grid and fixed-tape engines retain their exact source bytes. Both exact price engines run on the newly reconstructed invoice. The emitted caller must equal every byte of the pinned caller.

All **3,047 paid/helper chart maps** and **104 main boundary pairs** are freshly replayed on the current native. Exact signed Pauli action plus absolute Gaussian phase determines every column for these Clifford maps. The preceding native replay additionally checks the three changed helper-chart maps on all 512 columns and the full width-512 physical word. Old catalogue logs are removed from the temporary copy before new slices are generated. Nothing is relabelled as a current certificate merely because the set of chart pairs happens to agree.

Current ordered occurrence, owner and phase checks bind the complete paid and productive counts. Aliased main owners reject. Missing retimings/corrections, changed paid histogram, wrong prefix/suffix/chart, insufficient native/caller grids, global phase and BIT-pin controls remain active. The signed rank-nine child is checked on finite widths 1, 2 and 3. Every returned composition receipt field is frozen in `RESULT.json` and compared in the final replay.

The standard-library replay needs no Git or network. `--out UNUSED_PATH` on `verify.py` writes a new receipt; the registered command compares it. Optimized Python is rejected. `VALIDATION.md`, `ENVIRONMENT.json` and `REPLAY.txt` distinguish actual executions from inherited evidence. This is source-aware reuse of credited engines, not independent human or formal-kernel approval.

## Scope, obligations and credit

The selected #7000 source-specific proof is pinned through canonical main `e54523517d0f03e58352e647c403a5af3e525a57`. This package supplies the changed-source component checks and finite cost substitutions described in `APPLICATION.md`; upstream admission and independent review remain open. The five framework assumptions are `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`. Owned erasure retains its nonzero-content premise. A compiled top-level multiplier is not materialized, and finite evidence does not constitute a formal verification of the complete multiplication theorem.

Prepared for dillona with substantial OpenAI Codex assistance; no subagents. Apache-2.0. **Rohan Arun** supplies the 17-stage signed caller, odd-grid application and verification adapters; **Ali Romman** the independent-helper/basis method; **Jerry Chen / CubeJerry** the retiming, inventory, caller/BIT, precision and native compiler engines; **DreamingOfClouds** the native chain; **ToikY** #7003/#7004 and the #7108–#7110 signed/native sources; **Douglas Colkitt and the #7000 reviewers** the source-specific occurrence/catalogue and fixed-tape application; and **dillona/OpenAI Codex** #7105/#7107/#7112/#7115. All original source notices are retained. Neither predecessor optimization is claimed as new here.

## Open next questions

- Check live signed-core/gap-group investigations before attempting another caller change. A new labelled endpoint and full cost may improve the fixed invoice; no global caller ceiling is established here.
- Independently review the complete component application: current owner/phase substitution, full-root odd-grid induction and physical upper-cost constants. The five framework assumptions remain and no top-level compiled execution is supplied.

`TASK.json` records relevance, first steps and blockers. The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521) records checkpoints and overlap.
