# Banked R715 target-interval factors

κ = 0.001168862033074029

The exact conditional value is `1168862033074029/10^18`, using bit lower endpoint
`1170229870339438219571/10^24` and the cited PR433 complex lower endpoint
`1183986549206329/10^18`. It improves the earlier non-hosting R740 target-mixing
value `0.001145834572824929` by about 2.01%. Other published packages report
higher numerical values using hosting and/or different complex suppliers;
this package does not claim to exceed those reported numbers.

This package puts the pinned R715 rank120 scalar word with fourteen target-interval
factors into PR443's independently checked, 32-replica whole-residual banks and
nine-stage schedule. It has 715 helpers, 55,920 live families, 55,929 physical
families, 1,261,440 paid children, rank mass 3,568,896 and deficit 9,984. No helper
residual is split across physical families or placed in idle data storage.

Dugongue's PR478 constructor regenerates the final fourteen factors from the pinned file
`vendor478/bit470/data/parent473.json` and `vendor478/code/SELECTION473.json`,
then compares the result byte-for-byte with the published UTF-8 scalar word.
This rank120 input is distinct from the repaired rank119 final word associated
with PR473. Reconstruction of the earlier R715 carrier and kernel search is
not claimed; the actual input and final words receive full independent replay.

## Reproduce

Python 3.11+, numpy, mpmath, sympy, a C++17 compiler and real Boost headers are
required. From this package directory:

```sh
python -m pip install -r e8-r740-replica32/parent436/requirements.txt
BOOST_INCLUDE=/path/to/boost python -B verify.py /absolute/fresh/output
```

The output directory must be outside the package. `CXX` may select a C++ compiler.
Every pinned upstream byte, including CRLF source files, is preserved. The wrapper
checks the complete manifest and upstream Git blob pins before execution, and
checks that source files and the manifest remain unchanged at completion.

The complete PR443/436 wrapper is rerun for its parent reconstruction and geometry.
The candidate verifier then rebuilds the fourteen factors, rejects 28 omitted
setup/recovery gates, and compiles the official legality and five-/nine-stage
formal-column checkers for 715 helpers. It runs six nonvacuous record mutations,
Gram/prime checks, full global scalar replay, residual isometries, both reflected
paid ledgers, fourteen global controls, the explicit 64-dimensional bank-owner
audit, both rational moment engines, the finite invoice, six bootstrap levels,
all 47 strict outer inequalities, and four invalid-parameter controls.

The unchanged independent operator audit checks 950 exact rational projectors,
3,414 forward/reflected transition pairs, all 955 scalar columns and all 140
target additions per orientation, including 112 inherited reads and 28 new
interval gates. It restores all 715 arbitrary dirty-helper inputs and closes
copied work. Its Boolean orbit cases are exhaustive for one-/two-cycle ADD
commutation; the separate small F3/F2 label checks are finite controls. No
exhaustive replay of all arbitrary array assignments is claimed.

`EXPECTED.json` binds the complete paid profile, actual word, global template,
bank route digest and exact result. The canonical word is plain JSON. The frozen
global engine receives a deterministic runtime gzip copy generated in the output
directory. Runtime-only geometry timing is normalized to zero before hashing.
Subprocess exits are retained in `STEPS.json`; a failed subprocess also writes
`FAILURE.json`. Success writes `RESULT.json`.

This is a finite conditional construction within the inherited all-size compiler,
compressed-window, correlated dirty-bank, restored-work, tape/common-grid,
prime/precision and analytic interfaces. The complex supplier is cited through
its pinned PR433 receipt; its complete phase suite is not rerun. No unconditional
integer-multiplication theorem, Lean proof or global optimality is asserted.

Provenance, licenses and AI disclosures appear in `NOTICE.md`, `SOURCES.json`, and
the unchanged upstream notices. Existing published PR heads and claims are frozen.
