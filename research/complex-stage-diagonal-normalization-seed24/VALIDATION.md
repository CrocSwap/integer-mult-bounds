# Validation receipt

Host: Windows, CPython 3.14; 2026-10-13 UTC. Frozen base `ba82555c64e1879e4b7decce28186f208fcb8262`. Standard library only; no network is needed to replay.

From repository root:

```text
python -I -B research/complex-stage-diagonal-normalization-seed24/verify.py
python -I -O -B research/complex-stage-diagonal-normalization-seed24/verify.py
```

Both default saved-receipt checks passed:

```text
PASS_COMPLEX_STAGE_DIAGONAL_S24 registers=41+22 gain_real_per_orientation=540 Horner_gain=340 controls=10
```

The 540/340 counts combine both components of one complex invocation; the per-component savings are 270/170. Both orientations are individually checked. The receipt was generated with explicit `--write`, then verified in normal and optimized modes without regeneration. Complete equality of the reconstructed certificate and canonical candidate payload is required, in addition to mathematical checks.

```text
python -I -B scripts/verify_selected_result.py
```

Passed: `PASS selected record, exact kappa, original source inventory and proof supplement: 1672188119205421/1000000000000000000`. This is the frozen base's selected control, not the newer live PR1094 frontier.

```text
make verify
```

Could not run: `'make' is not recognized as an internal or external command`. No repository-wide make validation, native execution, or hosted assembly replay is claimed. Python prints a host relocation warning before execution; all reported Python runs exited zero.

The exact independent stage replay, full retained arbitrary-column/frame/wrapper replay, 326 distinct-coefficient work checks, complete primitive accounting, and primitive-prefix propagation are included in the default verifier. Ten required controls cover source/JSON/identity rejection and actual altered programs or lowering, plus the fully priced blanket failure. The unchanged receipt stores all five mandatory source hashes and both archived member container/payload hashes.

Final source/artifact checks are also recorded in the root HANDOFF.json after commit; only this package is staged.
