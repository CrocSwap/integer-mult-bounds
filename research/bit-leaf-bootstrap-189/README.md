# Bit leaf bootstrap on PR194: conditional kappa = 6.678525e-4

## Result

**kappa = 267141/400000000 = 6.6785250e-4**, against PR194's
1668581/2500000000 = 6.674324e-4 (+0.0629%).

This package changes exactly one thing in the current record: the ordinary leaf
that prices the binding bit supplier. The complex supplier (PR193 as carried by
PR194), the bit word (PR189), the terminal sinks, the reuse pairs, the finite
bridge and the 47-constraint balanced assembly are PR194's, unchanged.

| quantity | PR194 (record) | this composition |
| --- | --- | --- |
| complex saving | 7.009184e-4 | 7.009184e-4 (unchanged, PR193) |
| bit coarse saving `C` | 6.68298937775631e-4 | 6.68298937775631e-4 (unchanged, PR189) |
| bit ordinary leaf | 384599/10^10 = 3.84599e-5 (legacy) | 6.68298899999874e-4 (bootstrapped) |
| bit effective saving | 6.67878244234e-4 | 6.68298899999874e-4 |
| **kappa** | 1668581/2500000000 = 6.674324e-4 | **267141/400000000 = 6.6785250e-4** |

## Change and why it is the live lever

The record's assembly prices the two supplied profiles and then

    a = min(bit_effective, (1 - 1e-9)*complex_saving - 1e-10),   kappa = a/(1+a).

The bit side binds (6.6788e-4 versus 7.0092e-4). PR194 prices that side with
PR184's `select()`, whose atom blend is

    effective = (1 - atom)*C + atom*OLD,   OLD = 384599/10^10 = 3.84599e-5,
                                           atom = least payable atom on 10^-12,

so the legacy leaf `OLD` holds the effective value 4.207e-7 *below* the coarse
saving `C`. PR185 replaced that legacy leaf by a finite acyclic wrapper whose
leaf value obeys

    a_0 = legacy effective,   a_{n+1} = (1-C)*C + C*a_n = C - C^n (C - a_0),

and verified it (three finite levels, 47 strict constraints, 7 margins, 11
rejecting controls per depth, adjacent grids). Three levels give
`a_3 = 6.68298899999874e-4`, i.e. `C` to within 1.3e-15. Applying that recurrence
to PR189's bit word on PR194's own assembly recovers the slack:

| depth | bit leaf | kappa | gain vs PR194 |
| --- | --- | --- | --- |
| 0 (record) | 6.67878244234e-4 | 1668581/2500000000 | — |
| 1 | 6.68298618876e-4 | 3339261/5000000000 = 6.678522e-4 | +0.0629% |
| 2 | 6.68298899812e-4 | 267141/400000000 = 6.678525e-4 | +0.0629% |
| 3 | 6.68298899999e-4 | 267141/400000000 = 6.678525e-4 | +0.0629% |

All 47 strict constraints and 7 margins pass at every depth; the strict paid
atom and row tolls (`a_0 < a_n < C < 1 - a_n`) hold; depth 0 reproduces PR194's
kappa exactly from PR194's own inputs, so the delta is the leaf alone.

## What was searched and rejected

Both W-lowering levers on the binding word are maximal, so this leaf slack is
the only remaining room before a new word is needed. `word.py::row()` gives
`W = 2*v + (R - pairs)` at fixed rank deficit, so terminal sinks and reuse pairs
each lower W and raise the coarse saving.

* **Terminal sinks: 34 of 34.** All 474 per-root-admissible sink roots were
  enumerated (34 rank 21, 440 rank 23); the shipped 34 are the rank-21 family and
  reproduce the frozen terminal profile bit-for-bit (W = 21074, rank = 1515392,
  maxchild = 60, coarse = 668298937775631/10^18). Each of the 440 further
  candidates is rejected by the exact target chronology of `bit/terminal.py::prove`
  (`target chain nesting`), so no larger target-disjoint packing exists.
* **Donor reuse: 1760 of 3960 gauges.** Every one of the 2200 unpaired gauges has
  a rank-20 entrance birth frame, and no donor end frame among all 8628 donor
  frames is contained in any of them, so no donor can be aliased in. PR186's own
  description of this word names the same 2,200 rank-20 entrance gauges.

Observed outputs and commands: [bit-maximality.md](bit-maximality.md). The scans
run against PR189's package (`research/paired-cube-twin-local-168`), which is an
open dependency of this PR and is not vendored here.

The remaining lever on the bit word is its frame layout; PR192 bounds the
family's frame-layout ceiling at 7.010e-4, which the complex side already
attains. The next real step is a new bit word, not another sink or pair search.

## Reproduce

```bash
python3 -B research/bit-leaf-bootstrap-189/verify.py
```

which pins every input and package file by SHA-256 (`SOURCE.json`), re-runs the
assembly harness on the vendored inputs, requires the exact reproduction of
PR194's kappa, and compares the regenerated result with
[certificate.json](certificate.json).

## Verification boundary

* Reproduced exactly here: PR194's kappa from PR194's own profiles through
  PR194's own `select()` and `assemble()`; the wrapper recurrence and its closed
  form; the 47 strict constraints and 7 margins at every depth; the strict tolls.
* Inherited pinned inputs, not replayed here: the physical complex and bit words
  and their terminal-sink, reuse and frame artefacts (PR168 v4 `fd25adb7`,
  PR184/PR182/PR189/PR193/PR194 packages). The wrapper's physical realization is
  PR185's claimed construction, not one built in this package.
* Conditional on the retained contracts of the inputs and on the assembly
  arithmetic (PR183's closed-form acceptance ceiling, PR184's finite bridge).
* The gain is small (0.0629%) and lives on the 10^-10 selection grid, where the
  bootstrapped value saturates at the same kappa the untolled limit `C` gives.

## Stacking

Open dependency: PR194 (`research/source-assisted-v4`, `research/source-assisted`,
`research/paired-cube-twin-local-168`) and, through it, PR193, PR189, PR185,
PR184 and PR182. This PR claims only its own package; those changes are not
claimed here. See [NOTICE.md](NOTICE.md).
