# Early restoration of cleanup helpers on the gen5 word — verification chain

**Conditional κ = 46580439664377 / (625·10¹⁴) = 7.45287034630032·10⁻⁴** (+5.58·10⁻⁷, +0.075% over PR #291's
7.44728650221677·10⁻⁴; +0.077% over PR #290; +0.157% over PR #287; +0.337% over PR #285's gen5 word).

PR #291 is PR #290's gen5 package (DreamingOfClouds' gen5 word, rohanarun's 904-gate concave-descent retiming and 220
target-prefix squares from #287, chafreaky's 450 collective response-kernel entries) with a second constructed-frame
descent. This package is #291's package with **one added stage at the end of the bit pipeline: PR280's early
restoration of cleanup helpers**, re-derived on the gen5 word (`restore_transform.py`, frozen `restore-selection.json`),
and the five-stage admission of helpers that retire below the full frame.

* **What the stage does** ([RESTORE-PROOF.md](RESTORE-PROOF.md)). At the first cleanup ADD, 440 helpers `a` have exactly
  one later scalar incidence, a write `a -= c·b` with a donor `b` unwritten in between; both sit at 22-dimensional
  frames whose span `E` is a nondegenerate 23-dimensional frame. The write commutes over the integers with every crossed
  gate, so it is moved to the cut: `a` and `b` advance to `E`, the unchanged ADD runs there and `a` retires at `E`
  instead of climbing to the full frame; `b` continues as before. Two rank-2 climbs per pair become three rank-1 climbs
  (local histogram delta {1: +1320, 2: −880}), the local rank mass drops by 440 and the priced literal stock by 1,100
  families (1,244,515 → 1,243,415). The scalar operator on every column is unchanged (the event order is not, so the
  scalar hash is recomputed and all 19,406 columns are replayed); row bounds, entrances, kernel entries, squares and
  every data endpoint are unchanged.
* **Admission.** A restored helper with entrance σ (dim 20) and endpoint `E` (dim 23) has residual `D_(E−σ)` of rank 3
  and one never-touched direction `E^⊥`, which is completed together with σ: the lowering reads every helper endpoint
  from the actual records and emits completions of rank 5·(dim σ + 24 − dim E); the geometry stage checks on an actual
  restored helper that completion and residual are exact commuting projectors summing to the identity;
  `bank_check` assigns families by the actual residual width (the 440 helpers become width-3 families beside gen5's
  354 rank-21 entrances), builds 440 new exact (σ, E) charts (985 charts in all) and tiles 3,484 (4³⁰) and 1,191 (3⁴⁰)
  banks per stage (821,015 banks, all 4,765,800 assignments enumerated); `math_check`/`finite_check` remove the
  completions from the priced histogram. Every changed count is a recomputed pinned value in
  `expected/kernel-pins.json`; then every stage of #291's verifier runs fresh — virtual, raw, bit (descent, target,
  kernel, second descent, restoration), scalar, primes, banks, complex, math, finite — with its omitted-stage negative
  controls.

| one invocation, m = 120 | PR #290 | PR #291 | this package |
| --- | ---: | ---: | ---: |
| five-stage calls | 477,859 | 478,184 | **480,384** |
| priced calls / rank mass | 475,180 / 2,484,630 | 475,180 / 2,484,630 | **477,380 / 2,482,430** |
| literal stock, 60 replicas | 1,244,515 | 1,244,515 | **1,243,415** |
| κ | 7.44714499357628·10⁻⁴ | 7.44728650221677·10⁻⁴ | **7.45287034630032·10⁻⁴** |

Conditional, finite construction under the retained public all-size hypotheses of the source527 lineage (no Lean
certificate). The bit side binds. #285, #287, #290 and #291 are open PRs; their stages are inherited unchanged and not
re-proved.

## Verify

    python -m pip install -r research/five-stage-gen5-restore/requirements.txt    # sympy 1.14.0
    python3 -B research/five-stage-gen5-restore/verify.py --output /tmp/gen5-restore-verification   # about 6 minutes; not under -I

`verify.py` is #290's; it prints `PASS_IMMUTABLE_GEN5_KERNEL_ENTRIES_FIVE_STAGE_BANKED_CONSTRUCTION` with the pinned κ.
The workflow `.github/workflows/five-stage-gen5-restore.yml` runs it on Ubuntu.

## Files

#291's package with: `restore_transform.py` and `restore-selection.json` (new), `RESTORE-PROOF.md`,
`discovery/build_restore_selection.py`, the modified `portable_bit.py`, `raw_ledger.py` (`rebind_restore`),
`code/global_lowering.py` (endpoint-aware completions), `code/geometry527.py` (restored-endpoint projector check),
`bank_template.py`, `bank_check.py` ((σ, E) charts, families by residual width), `math_check.py`, `finite_check.py`,
regenerated `expected/kernel-pins.json` and `MANIFEST.json`, this `README.md`/`PROOF.md` and `NOTICE.md`; #291's,
#290's and #287's README/PROOF kept as `README-PR291.md`, `PROOF-PR291.md`, `README-PR290.md`, `PROOF-PR290.md`,
`README-PR287.md`, `PROOF-PR287.md`. Prepared by Rohan Arun with Anthropic Claude assistance; Apache-2.0.
