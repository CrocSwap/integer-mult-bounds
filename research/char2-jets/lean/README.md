# decoder-duality

Lean 4 + Mathlib formalization of the two duality certificates behind the decoder lower bounds.
Everything is in `DecoderDuality.lean`. It has no `sorry`, and every theorem depends only on
`propext`, `Classical.choice` and `Quot.sound`.

## Build

```
export PATH=~/.elan/bin:$PATH
cd research/char2-jets/lean
LEAN_NUM_THREADS=4 lake exe cache get      # fetches the prebuilt Mathlib at the revision pinned in lake-manifest.json
LEAN_NUM_THREADS=4 nice lake build
```

Toolchain `leanprover/lean4:v4.33.0-rc1`. The Mathlib revision is pinned in `lake-manifest.json`. With a built Mathlib already in
`.lake/packages` only `DecoderDuality.lean` is compiled (about 20 s). `verify.sh` does not need Lean; `LEAN=1 bash verify.sh` runs this build as an optional extra step if `lake` is on `PATH`.
The three `#print axioms` lines at the end of the file print `propext`, `Classical.choice`, `Quot.sound` for `hadamard_diag_rank_sum`, `lemmaB`, `lemmaCR2`.

## Statements

Setup: `t, s ∈ Fin v`, `j ∈ Fin T`, and `P, Q : Fin v → Fin T → K` over a field `K`. Define

- `M t s = Σ_j P t j · Q s j`
- `R_j = {t | P t j ≠ 0}`
- `A_j = {s | Q s j ≠ 0}`

**Core lemma** (`hadamard_diag_rank_sum`). The setting is:

- a field `F` and a finite index type `ι`;
- a matrix `B : ι × ι → F`;
- vectors `p_j, q_j : ι → F`;
- sets `S_j ⊇ supp p_j` and `U_j ⊇ supp q_j`.

Suppose the Hadamard product `B t s · Σ_j p_j(t) q_j(s)` is diagonal with nonzero diagonal. Then

  `|ι| ≤ Σ_j rank_F B[S_j, U_j]`.

Proof: `N = Σ_j diag(p_j) B diag(q_j)` is that diagonal matrix, so `rank N = |ι|`. Rank is
subadditive (`rank_add_le`, `rank_sum_le`). Finally, `rank(diag p · B · diag q) ≤ rank B[S, U]`
when p vanishes off S and q vanishes off U (`rank_diag_mul_mul_diag_le`), because the product
factors as `X · B[S,U] · Y`.

**Lemma B** (`lemmaB`, the lift identity). Let `B` be over `K` with:

- `B t t ≠ 0`;
- `B t s ≠ 0 ∧ t ≠ s ⇒ M t s = 0`;
- `M t t ≠ 0`.

Then `v ≤ Σ_j rank_K B[R_j, A_j]`. This is the core lemma with `F = K`, `p_j = P·j`, `q_j = Q·j`,
`S_j = R_j` and `U_j = A_j`.

**Lemma CR2** (`lemmaCR2`, the char-2 realisation). The setting is:

- `B` over `𝔽₂ = ZMod 2` with `B t t ≠ 0`;
- `P, Q` over any field `K`, which define `R_j` and `A_j`;
- `P~, Q~ : Fin v → Fin T → L` with `L` a field of characteristic 2.

Assume:

- `supp P~ t ⊆ supp P t` and `supp Q~ s ⊆ supp Q s`;
- `B t s = 1 ∧ t ≠ s ⇒ P~ t · Q~ s = 0`;
- `P~ t · Q~ t ≠ 0`.

Then `v ≤ Σ_j rank_𝔽₂ B[R_j, A_j]`.

Proof: apply the core lemma over `F = L` to the image of `B` in `L` (via `ZMod.castHom`) with
vectors `P~, Q~` and sets `R_j, A_j`. The support inclusions are exactly the `S_j ⊇ supp`
hypotheses. Then use `rank_L(map B') ≤ rank_𝔽₂(B')` (`rank_map_le`, proved here for any ring
hom of fields because Mathlib does not have it), applied to each submatrix.

So the duality is one lemma used in two fields.
