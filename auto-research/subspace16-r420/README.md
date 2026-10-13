# Subspace16 complex supplier with R420 bits

Conditional **κ = 0.001591968902833346**, about **0.06189551% above PR547** at `eecca20a24258cb6d9f698b1984a95029bac0a1c` (κ = 0.001590984155135328). The complex supplier binds at b = 0.001594507308884431019637; PR543's unchanged bit supplier gives c = 0.001653826988146798944268.

The new contribution is a frozen assignment of 63 gate frames. Starting from PR548's complex word, exact suffix-response pruning removes 238 preparation gates and regenerates inverse cleanup. The frame assignment then replaces 16 pairs of rank-2/rank-3 children with rank-1/rank-4 children. It preserves scalar operations of the sliced word, all helper widths, starts, the central cut, and the complete physical owner assignment. Its local histogram is `{1:2300, 2:440, 3:472, 4:184, 5:56, 6:56, 8:8}`.

The verifier reconstructs both suppliers, including PR543's complete native/interface/global driver, all 2,929 complex phase edges and 224 endpoint adapters, literal owners, finite invoices, two independent exact moment engines, and all 47 strict outer inequalities. Search output is a recipe, not a trusted certificate. No search or optimizer is needed for the new frame construction; the unchanged PR543 driver retains its own nomination controls.

## Reproduce

Use Python 3.11+ with NumPy, SciPy and SymPy, a C++17 compiler, and genuine Boost multiprecision headers. Keep assertions enabled.

```sh
python -B research/subspace16-r420/verify.py \
  --work /absolute/new/subspace16-check \
  --cxx c++ --boost-include /usr/include
```

The output directory must be new and outside the package. The input manifest is checked before and after replay. The retained PR543 driver is copied to scratch only to pin its source directory and normalize the gzip OS metadata byte; its mathematical checks remain unchanged. Cross-platform raw template hashes may differ because PR543 includes measured timing in its geometry metadata; semantic comparisons must disclose that distinction.

See [the proof and scope](proof/SUBSPACE16.md), [source pins](SOURCES.json), and original notices under `vendor/`. PR548 supplies the 477 frame lifts from PR534, its cold-dirt substitution and owner assignment; PR541/544 supply static44; PR535/531 supply the earlier complex construction and physical audit; PR543 supplies R420 bits. These dependencies are credited, not claimed as new here.

This is a finite conditional witness. All-size compiler realization, common-label/mutable-source transfer, complete-call hosting, precision/tape costs and analytic transfer remain inherited premises. PR543's interleaved phase-B source writes use its stated H1–H5 interface argument. The unchanged complex data controller is a pinned dependency. No unconditional multiplication theorem, new Lean certification, measured speedup or κ = 1 result is claimed.
