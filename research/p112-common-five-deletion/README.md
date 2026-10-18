# The sharp common-five P112 deletion bound

For one binary seven-space and one common set of at most five deleted P112 lines, at most two distinct characteristic-zero directions have residual binary label rank at most seven. Six common deletions admit an explicit independent root triple. The deletion allowance five is therefore sharp.

This resolves the common-cut question left open by [PR3230](https://github.com/CrocSwap/integer-mult-bounds/pull/3230), whose counterexample uses separate five-line cuts with an eight-line union. The contracts differ. No new historical TWOSIDE profile, full C5, decoder floor, supplier or kappa is claimed. The selected frontier is unchanged.

[PROOF.md](PROOF.md) gives the statement, completeness argument and literal witness. [WITNESS.json](WITNESS.json) is the common-six counterexample. [RESULT.json](RESULT.json) retains the complete finite cut table; [REFERENCE.json](REFERENCE.json) records the separate implementation's checks.

## Exact evidence

```text
43,435 binary seven-spaces
43,181 distinct live traces, 121 signed-permutation classes
maximum two-trace union = 68
1,200 complete candidate directions, 148 affordable completions
five common cuts: at most two distinct directions
six common cuts: three orthogonal directions, Gram determinant 512
```

The primary checker reconstructs the geometry and direction classification, then compiles a portable C++20 direct two-flat census. Python checks every cut and every distinct-direction triple. The reference imports no primary or predecessor code. It reconstructs E8 from lattice conditions, solves the label equations independently, enumerates annihilators in RREF, validates all 121 trace classes and uses individual dual-functional violations to reproduce every completion. A separate union-closure check proves the two-direction bound from that table.

Thirteen behavioral groups include source corruption, malformed cuts, dependent directions, the separate/common-cut distinction, orbit capacity failures and compiled four-cut/six-cut census mutants. `CHECKS.json` records the executed commands, environments and output hashes.

## Reproduce

From the repository root, use Python 3.12 or later and a C++20 compiler:

```sh
python3 -B scripts/research_package.py --package research/p112-common-five-deletion
```

The registered replay runs both checkers and the controls, with timeouts 360, 300 and 240 seconds. It needs only the standard library and the system C++ compiler. `VERIFY.json` declares the single live geometry input. Source pins are in `SOURCES.json`.

Direct commands are:

```sh
python3 -W error -B research/p112-common-five-deletion/verify.py
python3 -W error -B research/p112-common-five-deletion/reference.py
python3 -W error -O -B research/p112-common-five-deletion/test_verify.py
```

The primary accepts `--scratch DIRECTORY` and `--compiler clang++`. Alternatively set `TMPDIR` to an external scratch directory. The compiler and native executable run synchronously in a private temporary directory, which is removed on success or failure. Replay writes no scientific artifacts into the checkout.

The full root classification uses the standard real Weyl-chamber theorem. Its finite simple-system, reflection, parabolic-count and orbit obligations are rechecked. The characteristic-zero transfer is a written rational-nullspace argument. No Lean, Docker, selected supplier cold replay, analytic transfer audit or independent human review was performed for this package. The separate finite implementation corroborates the table; it is not proof-kernel verification.

## Scope and sources

This session takes the explicit PR3230 handoff rather than synthesizing a helper inventory. `TASK.json` records the changed scope from `complex-new-helper-inventory`. Base canonical main is `463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6. The selected baseline and original card are provenance, not changing live inputs.

Credit DreamingOfClouds/PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d` for the retained four-line Lemma N, SMALL2/Pencil and decoder-floor reduction. Credit Nick Petalas/PR3230 at `98fcc78f5d46b18f0342ea13b9ab5a3cfd87d5f0` for the separate-five boundary and this named common-five question. The exact geometry source is retained from PR3161/PR3162 through PR3169 and preserves the E8/P112 lineage, including joaqcoo. The new theorem, witness and checks are by Nick Petalas. Apache-2.0.

Development and verification used substantial automated assistance. Evidence is author-checked with separately written finite algorithms, not independent human review.

## Code and resource limits

All new Python and C++ functions fit within sixty physical lines. Proof conditions use ordinary exceptions, not Python assertions, and controls run under optimization. Fixed inventories bound loops and memory: 120 roots, 112 labels, 43,435 flats, 43,181 live traces, 1,200 directions and 121 classes. Each census class has an enforced 2,048-record capacity; the actual maximum is sixteen. There is no recursion or concurrent replay inside a command.

Power-of-Ten rule 3 deviation: Python and C++ streams allocate dynamically. These bounded, terminating verification programs are not allocation-free services. Fixed domains, inventory caps, subprocess timeouts and private-directory cleanup limit the resource lifetime. Revisit allocation policy if dimension or input domains become variable.

Rules 8/9 boundary: the primary executes exactly one SHA256-authenticated geometry source through `runpy.run_path`. It does not resolve an ambient `geometry` import. The reference has no such dependency. The CLI intentionally permits selecting a local compiler; no command uses a shell. Ruff's security audit reports S603 on the two subprocess calls because it cannot establish these trust boundaries. These warnings remain visible and are not suppressed. The compiler receives explicit arguments and the executed native file is the source just compiled in the private directory. Do not use an untrusted compiler or modify the checkout during replay.

The normal diagnostics are Ruff's error, import, bugbear, modernization, simplification, comprehension, performance, unnecessary-code and implicit-string checks, plus formatting. C++ compilation uses `-Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror`. `CHECKS.json` records the full security-audit output separately. No shared lint configuration or frozen predecessor is changed.

## Open next questions

Can this common-five theorem close a still-open, literal normalized caller in the P112 reduction? It only helps when the caller supplies one common deletion set. First reconcile the current PR3154 survivors and public exclusions, then derive a named caller's retained code dimension and shared support. No such application is established here, and separately affordable cuts cannot replace that missing hypothesis. Do not expand into another census without that obligation. The structured question is in `TASK.json`.
