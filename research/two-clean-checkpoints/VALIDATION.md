# Validation receipt

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Platform: macOS 14.6, arm64; CPython 3.14.7.
The scoped checks below completed on 2026-10-13 UTC.

```sh
python3 -I -B research/two-clean-checkpoints/verify.py
python3 -I -O -B research/two-clean-checkpoints/verify.py
python3 -B research/two-clean-checkpoints/test_package.py
python3 -B scripts/verify_selected_result.py
```

Both verifier modes matched the same frozen certificate. The package test
passed a relocated isolated/optimized replay and rejected three corruptions:
an altered integer cost, `true` substituted for clean count `1`, and changed
pinned proof bytes. Failed verification did not overwrite the evidence.
All eleven vendored files also matched `git show COMMIT:PATH` at the exact
source pins, independently of the JSON manifest.

Completed mathematical coverage:

- 1,619 decorated ordered binary trees through six factors, with independent
  preorder enumeration; Catalan counts and uniqueness checked.
- 723 whole-tree optimum comparisons: every `{1,3}` price vector through five
  factors and unit prices at six; every `0 <= clean <= scratch <= n-1`.
  449 states were feasible. 32,039 tree/resource admissions were checked.
- 61,804 forward instructions across complete free-noncommutative symbolic
  checks; every source and scratch coefficient, ordered target product and
  literal inverse checked. The same 1,619 trees passed nonlinear mod-101
  restoration and inversion, without claiming nonlinear product equality.
- The 50-factor witnesses passed separate whole-word symbolic execution;
  all 28 full-capacity `(s,c)` entries through `s=6` matched `4^(s-c)3^c`.
- 137 exact minima matched the unchanged PR788 optimizer, restricting the
  new recurrence to all-dirty or one-clean inputs.
- 192 actual PR628 rounded-leaf cases, including both signs/directions,
  length one/three, zero/one/two clean arrays and two nonzero dirt choices.
  Dense rational represented-factor comparisons, exact source/scratch and
  spectator restoration, literal inverses, zero-source identity, 3,760
  forward calls and 34,112 phase reads passed.
- Eighteen admission/instruction/accounting controls plus a rounded
  dirty-as-clean counterexample. Restoring a mislabeled dirty connector alone
  does not establish a correct target.

Separate workers reviewed the proof, implementation and evidence. Review
found and fixed a lazy-emission mutation hazard by freezing input trees,
and narrowed the magnitude statement to completed leaf boundaries; internal
leaf arithmetic still requires its own bound. These were AI-assisted checks,
not independent human review or a proof-assistant formalization.

The selected-record checker passed. The new package makes no change to
`upstream/`, the selected certificate, any supplier or repository generator.
No remote CI, Linux replay, practical performance gain, new κ or full
multiplication theorem is claimed.

## Repository baseline

One `make verify` ran on a disposable checkout of the exact base. Its first
seven groups passed; `gen4-bank-verify` then stopped because SymPy was absent.
An isolated CPython 3.14.7 environment supplied SymPy 1.14.0, NumPy 2.5.4
and SciPy 1.18.1. The resumed gen4 target passed all nine finite stages.

`frontier626-verify` initially could not find Boost in `/usr/include`. With
`BOOST_INCLUDE=/opt/homebrew/include` (Boost 1.88), the complete selected
replay passed: bit543, declarations, complex626, independent owner accounting,
helper interfaces and exact bindings. The selected conditional κ remained
`51110230636731/31250000000000000`. No supplier source was patched.

The resumed baseline also passed `verify-certificates` and `verify-ternary`.
The unrelated `verify-research` historical search group passed its bit and
mixed-point screens, then was deliberately stopped during
`audit_early_sharing.py` to bound the sprint. `verify-strips`, `verify-clones`,
`verify-positive`, `verify-joint`, `verify-pair` and `verify-tests` were not
reached. **No full `make verify` pass is claimed.** The complete new-package
verification and selected-frontier replay passed before this stop.
