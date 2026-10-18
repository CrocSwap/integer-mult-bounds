# Lean 4 check of the algebraic core of Lemma OC

`Overcomplete.lean` (46 lines) proves, over any field `K` and finite index types `T, m`, for `X, Y : Matrix T m K` with `X * Yᵀ = 1`:

* `oc_idempotent`: `(Yᵀ * X) * (Yᵀ * X) = Yᵀ * X`;
* `oc_trace`: `trace (Yᵀ * X) = T`; `oc_complement_idempotent`, `oc_complement_trace`: `1 - Yᵀ * X` is idempotent with trace `m - T`;
* `oc_square`: for `m = T`, `Yᵀ * X = 1` (biorthogonality).

No `sorry`; `#print axioms` lists only `propext`, `Classical.choice`, `Quot.sound`. **Not formalised** (written proofs in the README, §4): the rank statements `rank K = T`, the converse (`K² = K` and `rank X = rank Y = T` ⇒ `Σ x_j ⊗ y_j = id`), and the `m = T + 1` rank-one consequences.

Build (needs network the first time for Mathlib; the Mathlib revision is pinned in `lake-manifest.json`):

```sh
cd research/overcomplete-and-realisation-floors/lean
lake exe cache get      # optional: prebuilt Mathlib
lake build
```

`BUILD_OUTPUT.txt` is the output of this build on the author's machine (Lean toolchain in `lean-toolchain`, built against an already built Mathlib of the same pinned revision). The file is the one maintained in the author's project `decoder-duality` (which also holds the Shadow Lemma `lemmaCR2` cited in README §9.2; that file is not shipped here).
