# The core-row operator lift: HALO's tensor bound needs no off-core polynomial estimate

**Claim type:** a written lemma with exact rational controls. **No new κ.** It answers the open question of
jwr404's [#4515](https://github.com/CrocSwap/integer-mult-bounds/pull/4515). #4515 shows that the
shared-row sum does not lift to the full operator norm `‖B − C‖₂ < 2ε`. It leaves open a bound on
`‖P_sec − P_global‖₂` off the rows at distance `A = ⌈p^{48}⌉`.

That bound is not needed. HALO only keeps core outputs ("Keep outputs at distance A from every face"),
so the right statement is restricted to those rows, and there it holds.

## Lemma

For axis `i`, define:

- `Π_i`: the coordinate projection onto the rows HALO keeps;
- `B_i`: the section inverse, extended by zero outside the section;
- `C_i`: the global inverse;
- `P_sec`, `P_glob`: the section and global Neumann polynomials.

Assume, as in #4491/#4452 and HALO:

1. `‖B_i − P_sec‖₂ < ε` and `‖P_glob − C_i‖₂ < ε`.
2. `Π_i P_sec = Π_i P_glob`. This is HALO's sentence that a row at distance `A` "is therefore EXACTLY the
   corresponding row of the global `P_i`".
3. `‖B_i‖₂, ‖C_i‖₂ ≤ M`, for example `M = 9p²` from #4493, or the global ceiling of #4462.

Then:

    ‖Π_i(B_i − C_i)‖₂ < 2ε,
    ‖⊗_i Π_i B_i − ⊗_i Π_i C_i‖₂ < 2g·M^{g−1}·ε,    with ⊗_i Π_i B_i = (⊗_i Π_i)(⊗_i B_i).

**Proof.**

- **One axis.** `Π(B − C) = Π(B − P_sec) + Π(P_glob − C)` by (2). Also `‖ΠX‖₂ ≤ ‖X‖₂`, since
  `XᵀX − (ΠX)ᵀ(ΠX) = ((I−Π)X)ᵀ((I−Π)X)` is a Gram matrix and hence positive semidefinite.
- **Tensors.** Telescope `⊗ΠB − ⊗ΠC = Σ_k ΠC_1 ⊗ … ⊗ Π(B_k − C_k) ⊗ … ⊗ ΠB_g`, use multiplicativity of
  the 2-norm under `⊗`, and use `‖Π_iB_i‖, ‖Π_iC_i‖ ≤ M`.
- **The kept outputs.** The core box is a product of per-axis intervals, so the kept outputs are exactly
  the range of `⊗Π_i`, and the mixed-product rule applies. ∎

This bound is slightly sharper than #4508's `2g(9p² + ε)^{g−1}ε`, because no approximant norm enters. The
off-core rows of `P_sec − P_glob` never appear.

## Exact controls (`verify.py`)

- The Gram certificate and the restricted two-error split, on 40 random rational 6×6 cases.
- The mixed-product rule and the **exact** restricted telescope, for `g = 2` and `3`.
- #4515's examples:
  - `[[3,0],[0,9]]` has a small first row but a column of length 9. Restricted to the kept row, its norm
    is 3.
  - `[[0,0],[0,2]]` vanishes on the kept row. The restricted sum is `3 + 0 + 3 = 6 < 8`, against the
    unrestricted `3 + 2 + 3 = 8`.
- HALO's phrases are pinned.

## Not covered

- The ideal-gap gauges, which stay hypotheses.
- The global ceiling `‖C_i‖ ≤ M`, which is taken from #4462/#4493 as a hypothesis.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/core-row-operator-lift --check-only
python3.12 -B scripts/research_package.py --package research/core-row-operator-lift
```

The verifier prints `PASS_CORE_ROW_OPERATOR_LIFT`, using only the standard library.

## Open next questions

1. **Plug the restricted bound into #4506's `2^{−Cp}` comparison with `M = 9p²`.**
   - *First step:* replace `(9p² + ε)^{g−1}` by `(9p²)^{g−1}` in #4506's inequality, and recheck the
     four-bit gate.

## Credit

- The chain and the question are James Reed's (jwr404: #4488 through #4515).
- HALO's locality argument is from the #4100 notes.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
