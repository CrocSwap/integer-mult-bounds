# Kernel-checked regular-orbit endpoint interface

This package formalizes one implication used by the binary-stream lower-bound
interface: **equality of the complete operator on arbitrary dirty payloads
implies equality of every Boolean coefficient in every role block**, provided
the permutation family has a separating point and its label/role lists are
complete and duplicate-free. It also proves the required separating-point
property for invertible binary 3-by-3 matrices acting on **exactly three point
columns**, using the tuple of coordinate basis vectors.

The mathematical regular-orbit argument is credited to
[`bit-faithful-finite-address`](../bit-faithful-finite-address/README.md)
(woklerx) and [PR2599](https://github.com/CrocSwap/integer-mult-bounds/pull/2599)
(ywz65 with OpenAI Codex). PR2599 supplies the written sharp width thresholds
and legal short-width alias. The new result here is the Lean proof, its
explicit GL3 instance and the audited theorem-to-source boundary. This does
not claim a new width threshold or repeat the PR1974 lower-bound census.

## Exact theorem and assumptions

`RegularOrbit.lean` defines finite XOR sums, inverse-pullback permutation
actions and an arbitrary finite matrix of those actions. The theorem
`complete_endpoint_faithful` quantifies over **every** input role, output role
and address. In particular, helpers and off-diagonal blocks cannot be hidden
by assuming clean inputs. `gl3_complete_endpoint_faithful` instantiates the
address action with the actual Boolean matrix formula and the three basis
columns; it does not assume the separating-point conclusion.

The generic hypotheses are two-sided inverse laws, a separating point, and
complete duplicate-free lists. The GL3 subtype includes a two-sided linear
inverse; a concrete identity member proves that it is inhabited. Its finite
enumerator and list completeness are **explicit premises**, not kernel-derived
facts in this package. [BOUNDARY.md](BOUNDARY.md) maps every obligation to its
actual evidence and lists what remains external.

## Reproduce

From the repository root, using Python 3.12 or later:

```sh
python -I -O -B research/regular-orbit-lean-interface/verify.py
python -I -O -B research/regular-orbit-lean-interface/test_verify.py
```

These commands check exact source bindings, all 86,016 GL3/three-column action
comparisons, both inverse identities, 1,512 mixed coefficients across all nine
blocks of three dirty roles, and export/corruption controls. They **do not run
Lean**. The registered `VERIFY.json` hook has the same external-only scope.

For a fresh kernel check, supply an existing **Lean 4.34.1**, commit
`5045d0056413266e57c625dcd7c365b10e377c52`, executable:

```sh
python -I -O -B research/regular-orbit-lean-interface/formal_verify.py --lean /path/to/lean
```

The runner copies the exact hashed `.lean` bytes into a fresh directory,
compiles both modules, reads actual `#print axioms` output for 16 roots and
rejects four false statements. It does not reuse package `.olean` files or
download a toolchain. The reported axioms are confined to `propext`,
`Quot.sound` and `Classical.choice`; there is no `sorryAx`, custom axiom or
`native_decide` proof. `FORMAL-RESULT.json` is a retained local build receipt,
not a substitute for this command. `FORMAL.json` binds it and its sources.

Recorded runs used native Windows CPython 3.12.7 and Lean 4.34.1. Python 3.14.5
also checked the external conformance artifact. Separate OpenAI Codex agent
review includes a fresh Lean compilation and proof inspection; no human
review or hosted CI result is claimed.

## Controls and limits

`Controls.lean` proves concrete countermodels to dropping separation, label
uniqueness, label completeness or the arbitrary-dirty-input contract. For the
duplicate and missing-label cases the C2 action still has a separating point,
so those tests isolate the list assumptions. The formal runner first compiles
the countermodels and then requires their contradictory ground statements to
fail compilation.

The parser/encoding correspondence, enumeration completeness, word-to-matrix
translation and any prior census remain outside Lean. This is neither a
physical compiler nor a supplier, recursive admission proof or new exponent.
No selected result or frozen predecessor is modified.

## Open next questions

1. Supply a kernel-certified finite GL3 list and encoding map, removing the
   remaining enumeration premise in this concrete application.
2. Prove a source-pinned word evaluator commutes with the kernel action, then
   connect an actual lower-bound certificate. This package alone does not
   formalize the PR1974 census.

Prepared by ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
