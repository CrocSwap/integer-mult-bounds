# Lean certificate for the five-source connector exclusion

Independent verification and scoped formalization; no new kappa.

Lean 4.28.0 checks [PR943](https://github.com/CrocSwap/integer-mult-bounds/pull/943)'s finite five-source exclusion in an explicit matching grammar. Every word in `Pairing 5` misses at least one of the 32 possible paired-readout masks. The proof quantifies over all 945 insertion codes. It also checks the four-source universal witness, the ten-toggle witness that misses exactly mask 21, and the twelve-toggle universal repair.

This supplies a kernel-checked certificate for a result previously supported by two Python enumerations. It does not change the result or claim independent human review. All 11 audited statements use only Lean's standard `propext` and `Quot.sound` axioms, or no axioms. The accepted proof uses `decide`, with no `sorry`, custom axiom or `native_decide`.

## Formal statement and boundary

`Pairing` is a recursive first-endpoint matching grammar. Begin with the empty word. To add a source, increment every existing label, prepend label zero, and insert its second occurrence into any gap of the remaining word. Five pairs have 9, 7, 5, 3 and 1 choices, giving 945 codes.

`pairing_five_has_code` proves that every derivation in this grammar has one of the four finite indices used by `word`. `code_is_pairing` proves the converse. `code_shape` checks that every code has length ten, labels below five, and exactly two occurrences of each label.

`prefixes` records the source-parity mask at every boundary, including the initial and final boundaries. `covered` tests all XOR differences of two such masks. `covered_iff` connects its Boolean implementation to the explicit existential statement about two prefix values. `Universal` requires coverage of every mask below 2^n.

The certificate stores one missing mask per code. `missing_certificate` proves that each mask is below 32 and is absent from that word's prefix differences. `five_source_exclusion` then proves `Pairing 5 w → ¬ Universal 5 w`. The witness table is untrusted data checked by the kernel; the Python census is not a premise of this theorem.

The usual connection to an arbitrary word using each of five source labels twice is a separate mathematical argument: pair the first occurrence with its mate, delete both, recurse on the remaining positions, and rename labels by first occurrence. Reversing this process gives the insertion grammar. A coordinate permutation preserves full-mask coverage. This renaming argument is explained here but is not formalized in Lean. The proof also does not formalize the reduction from dirty linear queries to prefix masks, the 74-query optimum, recursive leaf costs, or tape execution. Those remain in Ross Richardson's source argument.

## Reproduce

Use the full repository checkout, Python 3.10 or newer, and the already installed official Lean 4.28.0 toolchain. Run from the repository root:

```sh
python3 -I -B research/lean-connector-exclusion/verify.py
```

Expected final line:

```text
PASS_LEAN_CONNECTOR_EXCLUSION pairings=945 theorems=11 controls=8
```

The wrapper resolves the pinned Elan toolchain. Alternatively pass `--lean /absolute/path/to/lean`. It checks compiler commit `7e01a1bf5c70fc6167d49c345d3bf80596e9a79b`, compiles fresh in a temporary directory, treats warnings as errors for the accepted proof, audits every named theorem's compiled dependencies, and compares the complete receipt with `EXPECTED.json`. `--write /new/receipt.json` saves a receipt without overwriting an existing file. No third-party Python package or Mathlib is needed. [Boundary.lean](Boundary.lean) can also compile by itself with the pinned Lean version.

The independent Python recount constructs words by insertion and recomputes interval parity from occurrence counts. It reproduces all 105 four-source and 945 five-source records, including the predecessor's complete sorted-record hashes and coverage histograms. No predecessor executable is imported. Literal source witnesses and every stored missing mask are compared, rather than checking only the maximum coverage.

Eight controls reject a covered-mask witness, an out-of-range witness, false ten-toggle universality, false twelve-toggle exclusion, a custom axiom, `sorryAx`, `native_decide`, and on-disk predecessor-certificate corruption. The three assumption controls deliberately compile with warnings permitted so that their actual dependency reports reach the rejection gate. The accepted proof always uses warnings as errors.

## Provenance and scope

Exact base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`. Subject: Ross Richardson's PR943 at `cf360b4b09b7d0419decdd6ac85421fefed55bdd`. [SOURCES.json](SOURCES.json) records SHA256 and Git blob pins for the source statement, notice, certificate and independent checker, plus separate base-context pins. Later changes to the selected frontier do not invalidate these historical context records.

The selected conditional kappa at the base is `0.001661960547713947`, from PR942. This contribution adds no supplier, stronger bound, all-size compiler, ownership/hosting realization, precision result or full multiplication theorem. Its formal scope is the matching grammar and finite prefix-mask coverage.

Contributor: Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance in formalization, implementation, verification and writing. Credit Ross Richardson for PR943's theorem, witnesses and Python evidence, and PR934 for the preceding binary connector interface. New files use the repository's Apache-2.0 license. [CLAIM.json](CLAIM.json) records OS-random seed 76, candidate selection and the local claim; no pinned coordination issue was present.
