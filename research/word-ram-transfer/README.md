# Bounded-word RAM transfer and native kernels

This package starts the requested migration from multitape Turing machines to a concrete Word RAM. It supplies an executable finite TM compiler, a freshly kernel-checked logarithmic-word bridge using the actual Problem 1.8 compiler, packed-tape access kernels, and constructive RAM-native algorithms for affine permutations and quadratic Gaussian phases. It does not claim an improved kappa or a fully rewritten native multiplication algorithm.

## Results and review order

1. [Machine interface and checked bridge](machine/MACHINE-INTERFACE.md): for an actual bounded IMP execution of k steps whose values and indices are polynomially bounded in n, the existing fixed compiled program runs in at most 10k successful RAM instructions at logarithmic word width. The new explicit input-domain interface fixes a quantifier mismatch in the unrestricted list-of-naturals logarithmic-width wrapper. This reuses the implemented Problem 1.8 machine and compiler; the new Lean appendix has five checked theorems.
2. [Finite TM compiler](compiler/TM-TO-WORD-RAM.md): an actual emitter for a fixed finite-alphabet multitape machine, with signed heads, polynomial-envelope logarithmic word width, genuine halt and fixed-length LSB output adaptation. Its sufficient simulation theorem transfers any complete fixed-machine multiplication theorem at constant step overhead. This is a classical model conversion, not a new multiplication exponent. The emitter and simulation proof are not Lean-formalized.
3. [Packed storage](PACKED-TAPES.md): uniform n-dependent packing with 13-instruction reads and 17-instruction writes, preserving neighboring fields and high padding. This reduces storage words while retaining constant simulation overhead. It does not imply a word-factor time saving.
4. [RAM-native layout algorithms](cost/COST-THEOREMS.md): affine record permutations in at most 8NL + 40N + 8 instructions; quadratic Z/4 phases in O(N+r); exact monomial action on modular limb records in O(NL+N+r). An explicit X/S/Z/CNOT/SWAP/CZ metadata compiler costs O((m+1)(r+1)^2). These are candidate replacements for paid tape routing and monomial segments. Hadamards, arbitrary phase roots and ADD crossings are excluded from this local normal form.

The target is finite bounded-word memory with logarithmic word width, not unit-cost exact-complex cells or one unit-cost multiplication on an entire n-bit input. The new TM compiler, packed-access kernels and native layout constructions use no word multiplication or division. The general IMP bridge preserves the source command's operations and may use those instructions; it does not lower arbitrary IMP multiplication or division to additive operations. Every full buffer, table, register region and effective address must fit below 2^w.

## Why this is a useful first migration step

The universal compiler separates correctness transfer from native optimization: mathematical identities, precision/recovery proofs and conditional recurrence hypotheses remain available, while tape-specific routing can be replaced one subroutine at a time. The native kernels identify actual blocks that can be replaced with finite-word algorithms and complete local costs. No term is deleted from an existing multiplication invoice merely because random access is available.

A model comparison is essential. Fuerer's [2014 log-RAM paper](https://arxiv.org/abs/1402.1811) already gives linear-time integer multiplication with unit-cost logarithmic-word multiplication. Thus preserving a TM bound on that stronger model is a baseline, not a best-known RAM complexity claim. The present restricted additive/Boolean compiler is also not asserted to be a new complexity record.

## Reproduce

From the repository root, with Python 3.12 and no third-party packages:

```sh
python3 scripts/research_package.py --package research/word-ram-transfer --check-only
python3 scripts/research_package.py --package research/word-ram-transfer
```

A Git-free extracted package can instead run `python3 -I -O -B verify.py` from its own directory. The verifier authenticates every package byte listed in CONTENT-HASHES.json before executing any local checker. It launches isolated optimized Python subprocesses; no result depends on enabled assert statements. The Python command checks finite implementations and proof-source integrity, not the universal claims or Lean compilation.

The [Lean reproduction instructions](machine/REPRODUCE.md) pin Lean 4.33.0 and Mathlib db584cd6d46c92f209a44c0f1c829460d327499d. Nine dependency source files are included, unchanged. [INDEPENDENT-AUDIT.json](machine/INDEPENDENT-AUDIT.json) records a second fresh audit of all five new theorems using existing pinned canonical import artifacts: only propext, Classical.choice and Quot.sound occur. An isolated rebuild of all frozen dependencies is not claimed. Publication snapshots are not an additional active DAG.

## Scope, overlap and provenance

The assigned task is a model migration, explicitly replacing the usual kappa hill-climb objective. TASK.json preserves the nearest historical card and marks this changed scope. Main was refreshed at f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc. Selected-frontier files and prior research are unchanged. [Overlap and credit](compiler/OVERLAP.md) compares actual pinned proof sources from PRs #956 and #647, which already construct exact scalar RAM providers in their declared models. Their bit-lowering obligations must not be silently treated as bounded-word operations.

Retrieval covered the federated source catalog and canonical Lean tree, with sixteen selected machine precedents plus cost and compiler source pins. It returned 153 Problem18RAM modules and nine Lax13 modules, but missed some newer on-disk RamStd/RAMRoot identities and exact typed queries returned no records. This is substantial source retrieval, not a claim to have read or rechecked every registered theorem. SOURCE-MAP.json and the component manifests state that coverage.

## Open next questions

- **First native caller:** choose one pinned admitted multiplication caller and replace a fully specified monomial/layout segment, preserving its actual observation boundary, input/output order, precision and aliasing contract. First step: identify the exact executable segment and pay metadata, copying and serialization in its whole-call invoice. Blocker: these local kernels have not yet been wired into that caller.
- **Complete packed backend:** emit head updates, dispatcher and IO around the packed macros, then compare the resulting actual finite program with the existing unpacked reference. First step: a one-transition invariant with all reads before writes. Blocker: only the access macros currently have emitted code and finite checks.
- **Formal compiler refinement:** prove the new emitter against RamStd.step and the explicit input-domain contract. First step: fixed-bank non-aliasing and one finite dispatcher transition. Blocker: the five checked Lean theorems concern the pre-existing IMP compiler, not this new TM emitter.
- **Precision and full cost:** connect the native modular-limb representation to each chosen transform's signed headroom and rounding/recovery estimates. First step: instantiate the existing Problem 1.8 limb/gather contracts at the selected precision. Blocker: Gaussian-unit phase correctness alone does not prove arbitrary transform accuracy or complete multiplication cost.

## Credit

Prepared for Dugongue by OpenAI Codex with three parallel agents and substantial AI assistance. Existing Problem 1.8 formalizations supply the RAM, bounded IMP semantics, physical layout, compiler, simulation and limb/gather precedents. Szymon Torunczyk and GPT's compositional-polytime implementation is retained through the structured-TM precedent. The tensor/symplectic and frame/normal-form precedents motivate the restricted monomial segments without asserting that arbitrary Clifford circuits are free.

Retain the upstream lineage detailed in compiler/OVERLAP.md, including Dugongue's #390, Jacob Sussman's frame/bank/RAM/Fourier and P193 contributions, the bridge/normalization/audit chain, native/controller work by zxv, Jacob Alan Sussman's mixed-target recursion, Cinna Davis's query/helper work, and all physical, precision, prime, tape and outer-analysis suppliers. New material is Apache-2.0; existing source headers are preserved. No independent human peer review is claimed.
