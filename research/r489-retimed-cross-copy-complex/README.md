# #493's R489 bit word with #495's retimed complex word on hybrid cross-copy hosting (draft)

Conditional candidate **κ = 726474255625747/500000000000000000 = 0.001452948511251494**, complex-bound, **1.22 % above PR #494** (κ =
358867191156973/250000000000000000 = 0.001435468764627892 at commit `419907c71246c050f1c3fd2a504469b74bf7798e`), the
strongest open comparable witness when this was prepared. This package is stacked on PR #494. The bit supplier is
PR #493's R489 word, run unchanged through PR #493's own `verify.sh`; only the complex supplier changes.

## What changes

The complex word is PR #495's retimed R560 word (Ali Romman), which combines PR #449's shared-donor kernel (DreamingOfClouds) with PR #458's paid two-sided residual adapters (chafreaky). It is rebuilt from its frozen `FULL-WORD.json.gz` by PR #495's own word-level scripts, vendored byte for byte (`SOURCE.json`). It is placed in PR #433's nine-stage template (m = 73, eight replicas), the template PR #494 prices. Every helper residual is hosted on idle data coordinates, so no banks are needed:

- the 79 entering (width-8) residuals per stage go whole onto pattern copies, with PR #495's route chart and adapters, each alone on its family in its call, as in PR #495;
- the 481 width-9 residuals per stage go on PR #448's cross-copy tape, as in PR #494.

Pattern copies and tape copies are different families. The complex lower bound rises from b = 1.437532·10⁻³ (PR #494) to b = 1455062642351477/10¹⁸ = 1.455063·10⁻³. The bit side is unchanged (c = 1.565442·10⁻³). `PROOF.md` gives the construction and the compatibility argument.

## Evidence

- `code/build_word.py` runs PR #495's scalar and frame audit, both local programs, the exact phase recipes, the paid adapters and the independent local read-back. All pass, with 158 residual-adapter events per call and all 800 columns read back.
- `code/complex_retimed9.py` emits the hosted template from the frozen selection `data/SELECTION.json`: 40,320 hosted residuals, 12,024 split, live 7680, physical 8258, deficit 2496, largest child 48.
- `code/invoice_retimed9.py` computes a fresh finite invoice. It is asserted to exceed the parent's per-vertex invoice and to meet every PR #442 inequality.
- `code/audit_retimed9.py` is an independent audit with no code shared with the emitter. It rejects 20 mutations.
- `code/assemble_complex.py` is the exact assembly (PR #494's `assemble_489.py`): the bit root equals PR #493's, plus six bootstrap levels, the 47 strict outer inequalities, and the next-grid and η/β controls.

## Reproduce

From the repository root of PR #494's branch with this directory added, with Python 3.11+, numpy, SymPy, a C++17
compiler and Boost headers (`BOOST_INCLUDE` if they are not on the include path):

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONINTMAXSTRDIGITS=0 python3 -B research/r489-retimed-cross-copy-complex/verify.py /absolute/new/output
```

By default this first runs PR #494's `verify.py` unchanged (PR #493's `verify.sh`, PR #442's complete verifier,
PR #448's cross-copy hosting of PR #433's complex word, its independent audit and the exact assembly) and checks it
against PR #494's `EXPECTED.json`. Then the steps of this package run, `RESULT.json` is compared with `EXPECTED.json`,
and κ must exceed PR #494's. `--parent-output /absolute/completed/pr494/output` reuses a completed PR #494 output
instead: its receipt status, manifest digest, every step-log digest and its result against PR #494's `EXPECTED.json`
are checked, and the receipt is marked as a component receipt. The integrity of this package and of PR #494's
package, with the PR #493 and PR #442 manifests that PR #494 pins, is checked against the manifests before and after
the run.

## Scope

Every assumption of PR #494 stays an assumption, including PR #448's cross-copy slot (complex side), PR #493's review
points (bit side) and the inherited all-size compiler, correlated dirty-helper, compressed-window, restored-work,
tape/common-grid, precision and analytic interfaces. PR #448's cross-copy slot is disputed in the discussions on PR #451 and PR #485, and this package uses it only where PR #494 does. This package adds PR #495's assumptions for its word: PR #449's expanded scalar interface, PR #458's paid two-sided residual adapters, and PR #495's pending mutable-target, idle-hosting and Gaussian-adapter interfaces. It also adds one new composition point: PR #495's whole entering-residual hosting is used in the nine-stage m = 73 template, on families kept separate from PR #448's tape. The audit checks that separation in every call; `PROOF.md` gives the argument. A finite certificate is not a formal proof of the
asymptotic multiplication theorem, no Lean proof is claimed, and κ is an exponent saving, not a measured runtime
speedup.
