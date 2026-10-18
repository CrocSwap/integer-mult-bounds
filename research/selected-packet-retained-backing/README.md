# Retained packet backing at a common prefix-return cut

The unchanged PR2697 packet loop retains cleared `local` and `changed` payload
arrays while the next field prefix is read. They coexist with the directory,
the cleared Consumer preflight prefix, the old prefix, and the new prefix.
This package gives an exact identity-aware sum at that cut, including transitions
between primitive passes. It is one component of the released caller-storage
handoff, not total physical reserve or a new kappa.

For N prefixes of F payload symbols, source backing K, directory backing D,
prefix backing Q, primitive ordinal t and j already completed prefixes:

```
B(0,0) = K + 1 + D + 2Q,
B(t,j) = K + [t>0](NF+1) + (jF+1)
         + (1+delta)(F+1) + D + 3Q     otherwise.
```

Here `delta=1` when the previous action's changed result is distinct from local,
and zero for the explicit alias interface control. All lengths include LEFT.
Source/current count once in the first pass. Clearing does not deallocate.
The written source argument covers all admitted parameters under the freshness,
length, alias and successful-execution contracts in [PROOF.md](PROOF.md).

For native distinct outputs and at least two primitive passes, the maximum over
these **return cuts only** is `K+(2N+1)F+4+D+3Q`. It does not bound primitive
interiors, all reachable objects, Python heap capacity, or a physical allocator.

## Scope and evidence

Scientific source: Jose Manuel/jmbarrancoml's [PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697),
commit `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. The 23 exported source/license
files retain exact Git blobs and SHA-256 hashes in [SNAPSHOTS.json](SNAPSHOTS.json).
The historical task catalogue and selected record are pinned in [SOURCES.json](SOURCES.json).
No selected source or frontier is changed.

The primary checker covers 130 cuts, including real sign primitives over Z/3
and Z/9, source padding and an alias control. One actual Consumer.apply
production/preflight witness retains its canonical 22,894-entry prefix while
the native packet engine executes a toy payload at the run seam. Its final
observed return cut has payload26 plus record114469 = **114495 named entries**.
Synthetic source specifications and toy layout/payload do not constitute
selected GL64 execution or catalogue admission.

The separate [independent audit](INDEPENDENT.md) derives the identity from source
before reading the primary proof/checker. It executes the literal packet engine
at 5,184 cuts in 864 cases, with all eight fresh/alias action words of length
three and padded source/directory backing. Its action/layout are explicit
interface fixtures, not native selected arithmetic. Nine accounting controls
reject omitted roots, marker errors and incorrect aliases. Additional primary
controls reject source/manifest corruption, preloaded modules, invalid cut
parameters and bool/int receipt substitution.

The all-parameter written argument, finite computation and source authentication
are separate evidence. No formal-kernel proof, independent human review,
full selected cold replay, failure-path theorem, recursive reserve, physical
reuse/movement implementation, supplier admission or new kappa is claimed.

## Reproduction

With standard-library Python 3.12, from the repository root:

```
python3.12 -B scripts/research_package.py --package research/selected-packet-retained-backing
python3.12 -B scripts/check_research_commit.py --package research/selected-packet-retained-backing
```

From an extracted package, including a read-only directory, without Git/network:

```
python3.12 -I -B verify.py
python3.12 -I -B independent.py
python3.12 -I -B test_verify.py
```

The verifier compares [RESULT.json](RESULT.json) and does not regenerate it.
Integrity controls create and remove a private temporary mutation copy; they
need a writable system temporary directory but do not modify the package.
The same three commands support `-O`; acceptance does not rely on assertions.

## Open next questions

Add Program, arena backing, count/continuation tapes, layout/event objects and
external payload/key owners to this exact same-cut baseline. Then cover
primitive interiors and prove the last-borrower, physical erasure, movement and
reuse contract. These missing categories block total reserve admission; arrays
that are no longer named cannot be declared physically reclaimed here.
[TASK.json](TASK.json) records the refined catalogue task and stop rule.

## Credit

Jose Manuel/jmbarrancoml supplies the unchanged PR2697 caller and runtime;
[its original notice](sources/pr2697/NOTICE.md) retains the source lineage.
starship-s's [PR2731](https://github.com/CrocSwap/integer-mult-bounds/pull/2731)
proves the separate `3v+3R` **nonblank payload** result, explicitly excluding
backing. Nick Petalas's [PR2743](https://github.com/CrocSwap/integer-mult-bounds/pull/2743)
joins caller payload/key phases, with the other storage categories still open.
Ross Richardson's [field-producer finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18964702)
at `d1881858a8dfe487822434f25dca15501b27cb62` already proves the prefix-only
D+3Q cohort and producer invariant. Its source loader and Consumer preflight
fixture scaffold are adapted here with credit. The subsequent
[Program acceptance result](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18965046)
at `dec8964bdd82402d78105d9ae1eafe5a8642442c` closes a different representation
premise and motivates this common-cut handoff.

The new contribution is simultaneous payload-plus-record backing at the precise
return cut, including first-cut aliasing and cross-primitive retained bindings.
Prepared by Ross Richardson with substantial OpenAI Codex assistance and a
separate math-storage-lifetimes AI derivation/checker. Apache-2.0; original
source notices are retained. Public claim:
[Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18965395).
