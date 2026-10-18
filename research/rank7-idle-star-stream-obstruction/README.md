# The current idle-star overlay changes the physical operator

PR3184's first committed idle-star group fails an exact eight-stream equality
check under its own unchanged completed local-invocation contract. At replica
zero, port zero, cover identity and Fourier character 16, the baseline is
`i I_8`; the overlay leaks `-1-i` from input Y0 to output Y1.

This closes a specific acceptance gap on a pending frontier claim. It supplies
no new kappa and changes no selected record. The [proof](PROOF.md) gives the
necessary transfer equation `E_receiver M = M E_donor` and an interval argument
that allows arbitrary diagonal hosted-helper phase values.

## Reproduction

Python 3.12 or later, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/rank7-idle-star-stream-obstruction
```

Direct source-export commands are:

```sh
python3 -B research/rank7-idle-star-stream-obstruction/verify.py
python3 -B research/rank7-idle-star-stream-obstruction/test_verify.py
```

Both write no generated files. `verify.py --print-receipt` prints the actual
hosted rows and both exact matrices. Direct replay needs this package and the
six live inputs in VERIFY.json at their repository-relative paths. It needs no
Git database, network, solver, Lean, native compiler or numerical dependency.
The registered runner additionally checks historical Git provenance.

## Evidence

The independent checker imports no predecessor producer or verifier. It rebuilds
and authenticates all 2,717,280 literal PR3148 fill rows, follows all 30 hosted
occurrences affecting the witness, checks the declared axis conditions for the
two literal moves, and computes the eight-stream operator with exact Gaussian
integers. The baseline passes 147 specified Fourier modes; the overlay fails
at character 16 in exactly three entries. RESULT.json stores the receipt.
Nineteen behavioral groups test the physical guard, inactive modes, undo,
journal preimages, dirty-host slices and invalid events.

[CHECKS.json](CHECKS.json) records executed checks and limits.
[ENGINEERING.md](ENGINEERING.md) records bounded execution and review choices.
An internal reviewer separately identified the same literal counterexample
and checked the interval proof. This is author-checked computational and written
evidence, not independent human or proof-kernel review.

## Scope and credit

Audited: Rohan Arun/PR3184 at `ffab383a5f78eb1a4ad4c7c7259a4f32b86f9481`.
Allocation: Jeremy Diviney/PR3148 at `f2927a4b8afcf0701a6b945e14f30de1d94f5176`.
Base main: `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority revision 6.
Exact source heads, paths, Git blobs and SHA256 digests are in SOURCES.json.

Gareth Davidson/PR1387 at `1d427e04346c4cce6430220c2e8ec1146ad4c396`
already established the physical-stream obstruction on selected PR1094 inputs.
Credit also its acknowledgment of Rohan Arun's earlier cross-family objection.
This package adds the current-candidate binding and actual T740 helper chronology,
not discovery of the underlying flaw. The local macro/frame convention and
eight-stream method follow that credited proof; new checker code here is
independently written.

The pair rule is Gonzalo-Mier/PR1252; the star class is Guéorgui Maissouradze/
PR1276; the simultaneous-assignment predecessor is Jeremy Kothe/PR1324.
The current words and allocation retain dcharb78/PR3133, Marius-Paul Dumitrean/
PR2979, Jeremy Kothe's rewrites, Mason Hale, Jeremy Diviney, Yiyang Lu,
Tekalign, icekylinx, Nick Petalas and the full E8/selected-supplier lineage.
Unchanged predecessor notices and credits remain in vendor/.

The new source projection, guard, proof application and checks are by
Nick Petalas, under Apache-2.0. Development and local checking used substantial
automated assistance. Native word internals and full supplier/outer admission
were not replayed. [Canonical investigation and status](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19000570).

## Open next questions

Can an operator preserving axis assignment lower the complete bill? First
enforce `E_receiver M = M E_donor` on the source schedule, using this literal
star as a rejecting control, before optimizing profiles. A complete symbolic
criterion over covers and characters, then full native/controller/outer
admission, remain necessary. TASK.json records the handoff. Further structural
rank optimization is paused because it does not resolve the equality failure.
