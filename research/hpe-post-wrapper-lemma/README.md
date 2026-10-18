# Post-wrapper uniqueness for hyperplane-ended helpers

**One interface lemma, formalized with its actual hypotheses.** No new kappa, no
supplier, no frontier change. This package answers the drawn `formal-interface-lemma`
card ("Can one small, precisely scoped interface lemma be formalized with its actual
hypotheses?") by formalizing the one boundary lemma the hyperplane-end interface
leaves open on the wrapper side, and binding it exactly to the three certified
Lean pairs.

The hyperplane-end proof `research/hyperplane-end-lean/` formalizes
`factor_iff_pre` ("the pre wrapper must be the `(E, U)` recipe") in
`HyperplaneEnd/Labels.lean`. The integration review
`docs/research/community-hyperplane599-review.md` requires **both** pre and post
wrappers to use the pair `(E, U)` rather than `E` alone, but no post-side
counterpart of `factor_iff_pre` exists in the Lean sources or in any research
package (`hpe-prewrapper-binding` states only the pre-side implication and
explicitly defers its arithmetic). The lemma below is that missing post-side
statement, sharpened to pin the global-phase field.

## The lemma

Write `C7 = fourier(7)`, the residual on the seven coordinate qubits tensored
with the identity on the two spectators. As in `PROOF.md`, `(N)` for a pair
`(E, U)` is the exact identity `T_U T_E^{-1} = L (C7 \otimes id) R` between
linear maps, global phase included.

**Lemma (post-wrapper uniqueness, phase-sharp).** Assume `(N)` holds for the
pair `(E, U)` with invertible monomial wrappers `L, R`. Let `L'` be any
invertible wrapper and `\lambda` a scalar. Then

    L'^{-1} T_U T_E^{-1} R^{-1} = \lambda (C7 \otimes id)

holds if and only if `L' = \lambda^{-1} L`. In particular the identity with
`\lambda = 1` (hypothesis (F) of `hpe_word_exact`) holds if and only if the
executed post wrapper is exactly the `(E, U)` recipe's `L`; every other post
wrapper, including a FULL recipe `L_{E, FULL}`, breaks `(F)`. For wrappers
restricted to the gate family the only scalars are `\lambda \in \{1, i, -1, -i\}`,
and the wrapper record's phase field is decisive: `L' = i^{t} L` satisfies the
identity with `\lambda = i^{-t}` and with no other `\lambda`.

**Proof.** Substituting `(N)` turns the left side into `L'^{-1} L (C7 \otimes id)`,
so the identity is `(L'^{-1} L - \lambda I)(C7 \otimes id) = 0`. The residual
`C7` is invertible (a product of `C` gates), hence `C7 \otimes id` is invertible,
so `L'^{-1} L = \lambda I`, that is `L' = \lambda^{-1} L`. Conversely
`L' = \lambda^{-1} L` gives `L'^{-1} L (C7 \otimes id) = \lambda (C7 \otimes id)`
directly. The proof uses `(N)`, invertibility of `L'` and of `C7`, and equality
as linear maps; no phase may be dropped on either side, which is exactly why the
`\lambda` slack is the whole freedom. `\square`

The symmetric pre-side statement with `\lambda` is proved the same way and
strictly extends `factor_iff_pre` (its `\lambda = 1` case); this package claims
only the post side, which was missing.

## Hypotheses actually used, and what is not claimed

Used: exact `(N)` for the pair with these `L, R`; invertibility of the executed
wrapper `L'` (monomial wrappers are); invertibility of `C7`; equality of linear
maps including global phase; `\lambda` a scalar on a 512-dimensional complex
space (`C^{128} \otimes C^{4}`).

Not claimed: no Lean kernel proof of this lemma (the proof above is written, and
the instance binding is exact Python); nothing about the other conjuncts of
`hrec` (climb identities, tail shape, unit row, footprints, whole invocations);
no statement about pairs outside the three certified ones; no complete
multiplication theorem; no kappa.

## Exact instance binding (`verify.py`)

`verify.py` reads the pinned literal circuits of `HyperplaneEnd/Exact.lean` and
evaluates them with an independently written exact gate semantics over `Z[i]`
(the documented five gate kinds of `HyperplaneEnd/Clifford.lean`, `C` gates
without their `1/2`, denominators `2^{#C}` compared exactly; no floating point).
Packed superposition evaluation gives every matrix column at once, and witness
rows/columns are decoded exactly.

For each of the three certified pairs `(E, U)` (`pair1`-`pair3`):

1. **Port controls.** Our `adj`, GF(2) inverse and composition conventions
   reproduce the kernel-evaluated literals `lhsLit`, `rhsLit`, `wL`, `wR`
   (`lits1`-`lits3` in `Exact.lean`), and the permutation matrices are mutual
   inverses on all 512 basis states. This cross-checks the semantics port against
   the certified arithmetic before any new claim is tested.
2. **Positive fixture.** `L^{-1} T_U T_E^{-1} R^{-1} = C7 \otimes id` exactly,
   phase included.
3. **Width guard.** The same identity fails against `C8 \otimes id`.
4. **Mutant family (declared, one field at a time).** `phase+1`, `phase-1`,
   `phase+2` satisfy the identity at exactly their `\lambda` form and no other;
   `offset-xor-1`, `linear-Z4-flip`, `quadratic-live-bit`, `matrix-row-swap` and
   `swapped-L-R` break every `\lambda \in \{1, i, -1, -i\}`, each with an exact
   `(row, column)` witness; `quadratic-dead-bit` is a precision control and must
   **not** break the identity (see below).
5. **Checker failure control.** `--self-test` corrupts a wrapper literal
   self-consistently and requires the pipeline to reject it.

The `quadratic-dead-bit` control records one real observation: the documented
`qv` semantics reads a diagonal row `Q_i` only through bits above position `i`,
so low-triangle bits are record-dead. Two wrapper records differing only there
denote the **same** operator, and a semantics-level binding accepts them; a
byte-level recipe comparison would reject them. The binding therefore compares
operators, not records.

Run from the repository root:

```sh
python3.12 -B research/hpe-post-wrapper-lemma/verify.py
python3.12 -B research/hpe-post-wrapper-lemma/verify.py --self-test
```

Expected output ends with `PASS_HPE_POST_WRAPPER_UNIQUENESS pairs=3
mutants_per_pair=9 controls=3`. `RESULT.json` records the mutant classification
and witnesses. Standard library only, Python 3.10+; the registered replay is
`python3.12 scripts/research_package.py --package research/hpe-post-wrapper-lemma`.

## Credit

The interface is [PR 593](https://github.com/CrocSwap/integer-mult-bounds/pull/593)
by Jeremy Kothe (`jeremykothe2`): `factor_iff_pre`, the arbitrary-terminal
extension and the exact non-cold Clifford factorizations. The multi-gate and
cold extensions retained beside it are
[PR 599](https://github.com/CrocSwap/integer-mult-bounds/pull/599) by
DreamingOfClouds. The hyperplane-ended construction is
[PR 591](https://github.com/CrocSwap/integer-mult-bounds/pull/591) and
[PR 596](https://github.com/CrocSwap/integer-mult-bounds/pull/596) by Jeremy
Kothe. The pre/post wrapper requirement is the integration review's
(`docs/research/community-hyperplane599-review.md`, maintainer integration by
Douglas Colkitt with OpenAI Codex assistance).
[PR 2706](https://github.com/CrocSwap/integer-mult-bounds/pull/2706) by Riquelme
Soares (`hevlyo`) in `research/hpe-prewrapper-binding` stated the pre-side
boundary implication and left its arithmetic unrun;
`research/hpe-wrapper-event-binding` compares emitted records to the Lean
literals at event level. The local 511-hyperplane cold check referenced below is
[PR 1697](https://github.com/CrocSwap/integer-mult-bounds/pull/1697) by Aaron
Wang (`navinor`). This package supplies the missing post-side statement, its
phase-sharp form, and the deferred exact arithmetic on the certified instances.
Prepared by Aaron Wang with help from opencode (substantial AI assistance; no
model named; no independent human review claimed).

## Open next questions

- **Can the lemma be kernel-checked in Lean?** Why it matters: the written proof
  is two lines from `factor_of_exact` and would discharge the post-side conjunct
  of `hrec` with the same trust level as `factor_iff_pre`. First step: add
  `factor_iff_post` (and the `\lambda` sharpening) to
  `research/hyperplane-end-lean/HyperplaneEnd/Labels.lean` mirroring
  `factor_iff_pre`, and extend `PrintAxioms` coverage. Blocked by: no Lean
  toolchain in this session's environment, and frozen predecessor packages must
  not be edited in place; a successor note or additive PR is required.
- **Does the post-side binding hold for cold `(E = 0)` helpers and multi-gate
  tails?** Why it matters: the certified pairs are the three non-cold pairs only;
  cold ends (`width 8`) and multi-gate tails keep `(N)` and the wrapper hypotheses
  as assumptions (`PROOF.md` sections 4 and 7). First step: run
  `research/hpe-wrapper-event-binding/verify.py --run` on an emitted cold-end run
  and extend its literal comparison with cold recipe pairs, or certify one cold
  pair exactly with this package's semantics. Blocked by: no cold `(N)` literal
  pairs exist in Lean (only the local 511-hyperplane tool check), and the
  emitted HPE runs are not vendored in this repository.
- **Should record-level recipe comparison be relaxed to operator equality?**
  Why it matters: dead quadratic bits make byte comparison reject a correct
  wrapper record. First step: document the `qv` low-triangle degeneracy in
  `scripts/verify_hpe_lean_binding.py` and add a dead-bit mutation control there.
  Blocked by: shared-tool changes need maintainer review.
