# Fixed-prime refinement of the retimed 527-source five-stage construction

Conditional saving:

`κ = 710346593569665/10^18 = 0.000710346593569665`.

This improves PR244's common-frame retimed source527 banked candidate at `a568d94f941929232ab393c7d33dc5a30e017892` by exactly `3901490/10^18`. It chooses the kernel-checked prime `q = 2^127 - 1`, replaces the inherited `10^-16` rare-class envelope with the exact bound `2m^3/q`, continues the paid ordinary recurrence to five finite levels, and retains every fallback child and selector cost. It adopts PR243's smaller outer backoff `eta = 10^-24` and recomputes that backoff on PR244's retimed rank histogram. The exact gain splits into `3899360/10^18` from fixed-prime density and `2130/10^18` from the smaller `eta`. The physical retiming and source paths are inherited byte-for-byte from PR244. The full exact certificate records the parent, intermediate fixed-prime-only, and final results.

## Reproduce

On this branch, install the pinned dependency and run the complete source-bound verifier:

```sh
python3 -m pip install -r research/five-stage-source527-fixed-prime/requirements.txt
python3 -B research/five-stage-source527-fixed-prime/verify.py --output /tmp/source527-fixed-prime-run
```

The command first runs the pinned PR244 verifier from scratch, including the retiming witness and independent frame-path census, all-column F2 and signed-inverse checks, physical frame and global lowering, prime witnesses, all bank assignments and routes, the complex supplier, and the inherited finite bill. It then independently recomputes the fixed-prime moments, finite recurrence, cutoff gaps, all 47 outer constraints, seven margins, and next-grid rejection, and compares the complete exact result with `expected.json`. The output directory must be new and outside the repository. No saved execution receipt is read as a proof input.

The fixed-prime Lean proof is checked separately in CI with the pinned Lean 4.24.0/mathlib project. Copy this directory to a temporary directory before running `lake update`; generated Lake files are not part of the immutable package.

## Conditional boundary

This is a finite conditional certificate. The all-size weighted compiler, common weighted chart, restored rows, selector and routing interfaces, exact-tape movement, prime-supply framework, precision/recovery, complex symbolic correctness, completed ordinary-leaf theorem, and analytic reduction remain inherited assumptions. The Lean proof establishes the selected prime and density bound only; it does not formalize the integer-multiplication theorem. No measured multiplication performance or unconditional theorem is claimed.

This is a stacked refinement of PR244. Its PR against `main` carries PR244's not-yet-merged retiming witness as an ancestor; the exact gain stated here is only the increment over PR244's κ.

See `PROOF.md`, `SOURCE.json`, `FRONTIER.md`, and `NOTICE.md` for exact lineage, the live public comparison, and proof limits.
