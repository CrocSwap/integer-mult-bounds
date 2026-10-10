# Lean verification of paired-cube finite identities and κ arithmetic

This package targets CrocSwap/integer-mult-bounds at merged commit `d1d6c070f5a8c684727ee7ec35d930f9ebfa9758`. It preserves the construction’s existing author-checked conditional value **κ = 4609169/10000000000 = 0.0004609169**. It adds no new exponent and does not claim a formal proof of the full asymptotic integer-multiplication theorem.

The frozen accepted set contains **3,606 Lean modules and 14,320 audited theorem declarations**, including 2,816 axiom-free declarations. Other transitive dependencies are restricted to `propext`, `Quot.sound` and `Classical.choice`. The complete finite identity `J6 M V + 3 K2 = 6 I` holds for arbitrary integer payloads at all 1,760 targets of the actual 49,424-step signed word, with dirty auxiliary restoration. The package also includes exact frame/operator results, scoped local register/storage and scratch-boundary results, and source-derived finite checks for all 47 assembly inequalities and seven margins.

`key_theorems/` provides readable copies of six principal theorem files. Their dependencies and the complete accepted source set are in the archive. The archive contains only accepted `.lean` sources and eight pinned scientific inputs: no historical logs, operational notes, diagnostics, compiled objects or unaccepted candidate sources. `INPUT_MAP.json` pins every file and the exact audit names.

## Reproduce offline

Use an already installed official Lean 4.21.0, commit 6741444a63ee, plus Python 3 on a POSIX system. No Mathlib or network access is needed for these accepted modules. Replace `/path/to/lean` below with that compiler. The installed pinned standard library is an explicit toolchain trust boundary.

```sh
sha256sum -c SHA256SUMS
mkdir -p unpacked
tar -xzf scientific_sources.tar.gz -C unpacked
python offline_check.py --map INPUT_MAP.json --source-root unpacked --check-only
python -m unittest -v test_offline_check.py
python offline_check.py --map INPUT_MAP.json --source-root unpacked --build --resume --lean /path/to/lean --output /tmp/paired-cube-lean-build
```

For a bounded arithmetic check, add `--module PairedCubeCore --module PairedCubeIdentities --module AssemblyParameters13955` to the final command; accepted dependencies are included automatically. Sources, imports and printed audit names must match the map. Compilation uses one Lean job, a 4 GiB address-space cap and the recorded 60/120/300-second per-module limits. Resume rechecks source, dependency-object, compiler, object and audit-log identities. It never silently adopts missing or unaudited objects.

## Evidence and remaining scope

The accepted modules have prior successful per-module compiler and complete transitive-axiom audits. The newly introduced portable driver passed 11 deterministic fixture tests and actual isolated compilation/audit of four approved modules, 168 declarations, followed by successful receipt reuse. The curated archive was independently read back against every file digest. A complete clean rebuild with this new driver has **not** been run. Historical accepted compiler durations total about 4 h 39 m for 3,564 baseline modules;5–7hours is a planning estimate for a sequential clean run on similar hardware, not a measured clean-run result.

Core integer-pair arithmetic now derives the 46 previously stored slack formulas and all seven margins from the pinned source expressions, with positive denominator conditions; the existing literal scalar guard supplies the 47th inequality. This is finite arithmetic. Real logarithm/exponential bounds, concrete rational/Gaussian field instantiation, full physical-word/readout composition, exact global restored-row and fixed-tape costs, and the inherited all-size analytic/compiler contracts remain explicit boundaries. Local scratch and storage theorems do not imply those global results.

Source extraction, parsing and cryptographic provenance are executable trust boundaries. The scientific certificate’s own conditional scope remains unchanged. The underlying community construction retains all existing repository attribution; this verification work was prepared with OpenAI assistance.
