# PR288's open item 3 (full-Borel bit register model) on unit targets: closed for 2-integral data, open only where data outside Z_(2) is needed

**Scoped corollary (obstruction) with exact finite checks; no new κ, no change to any supplier.** Card
`bit-new-register-model`, bit track, seed 9.

## Where this sits

[PR288](https://github.com/CrocSwap/integer-mult-bounds/pull/288) (eumemic; closed and unmerged; written arguments
incorporated by the ledger) studies the bit primitive in its *general register (superposition) model*, where gates
may join registers at different frames.
- **Theorem `G₀` (§1.2(e)).** Free Levi maps applied in the middle of the network never save at `m = 2`.
- **Open item 3 (§3).** Theorem `G₀` "does not cover the free lower-left updates `D += K·H`." Natively those updates
  are free: upstream Lemma `ordered-affine-streams` updates a later field from earlier ones in `O(V)`.

PR288 §1.4(a) also states, as a general tool, that "FO on `Λ/pΛ` applies whenever the H and D parts split the lattice
mod p".

## Result ([PROOF.md](PROOF.md))

This note writes out the `p = 2` instance of that tool for the full lower Borel, using P1's `ν(g) = len(im g_HD)`.
The model has:
- `W` data registers and any number of auxiliaries, dirty or clean;
- free `GL(F2)` mixing;
- free lower-triangular register maps (Levi maps and `D += K·H`) inserted anywhere;
- paid shears `H += A·D` at cost `rank_Q A`.

If every *applied* matrix is 2-integral (odd denominators; inverses need not be), then

    Σ_paid rank_Q A  ≥  Σ_w rank_F2( (g_w mod 2)_HD )  =  mW   on unit targets,

where `g_w` are the entries of the data-to-data block of the final state. For example, `g_w = l' n_{C_w} l` with `C_w`
and the free factors invertible mod 2 is a unit target. So on unit targets the bill satisfies `(1/W) Σ n_r (r/m)^{1−a} ≥ 1` for every `a ∈ [0, 1]`, where `n_r` is the number
of paid calls of rational rank `r`. There is no saving at any width, register count or auxiliary count.

**Consequence.** On unit targets, PR288's open item 3 is closed for 2-integral data. What remains open is everything
that, once targets are normalised to `n_I`, needs data outside `Z_(2)`:
- dyadic paid frames;
- applied free maps with even denominators, such as the natively free scaling `diag(½I, I)`;
- 2-integral words on targets that are not units mod 2, such as `n_{2I} = d·n_I·d⁻¹` with `d = diag(2I, I)`. These
  get only the weaker bound `Σ rank (g_w mod 2)_HD`.

The note follows PR288 §1.3(b) and PR2110 in constraining only the data–data block, which covers clean ancillas with
garbage, permuted outputs and free factors on targets. Beyond specialising PR288's tool, it adds one thing: applied
free maps may be **singular mod 2**, such as `diag(2I, I)`, because the argument runs over the monoid algebra.

A remark gives the `m = 1` case for any rational data via a mod-`p` permutation module. It is a sanity bound with no
exponent content: PR288's flag theorem already covers `m = 1` without `D += K·H`.

**Is 2-integrality needed?** In general, yes. Upstream Proposition `bit-motif-interface` (`03-motifs.tex`) is an XOR
network on rational shear frames with unit targets and `s_b < W_b m`. Read as a word in this model, it must apply a
matrix with an even denominator; P1 Cor. alg-mixed(ii) says the same for XOR motifs. What remains open is the **smallest** width at which data outside `Z_(2)` saves in this model. The
abelian and `G₀` models never save at `m = 2`, so the first open case is `m = 2` with `D += K·H`.

## Finite checks (`verify.py`)

These are sanity checks of the lemmas, not a proof. In `verify.py` and `RESULT.json`, `rho` and `rho_p` denote
PROOF.md's `ν_π` and the `m = 1` module functional. All arithmetic is exact (Fraction and F2), in the standard
library, with fixed seeds. A shipped `--mutations` mode injects 8 defects in-process and requires each to be
rejected, which shows the checks are not vacuous:
- OR instead of XOR in the group algebra;
- a wrong mod-2 reduction;
- an upper entry in the free maps;
- undercounted paid rank;
- a non-unit data block;
- a skipped Borel factor;
- the upper-map control replaced by a lower one;
- the wrong axis in the mod-`p` module.

| Check | Coverage |
|---|---|
| `π` multiplicative on exact group-algebra products (free maps singular mod 2 included; counted in RESULT.json) | 90 products, `(m,W)` ∈ {(1,2), (2,2), (2,3)} |
| Forced F2 cancellation: `(I + N([n_A]−1))² = I + N([n_{2A}]−1)` for `yᵀx = 1`, and `π` on it | 18 cases |
| `ν_π = 0` on free moves; `ν_π(paid) ≤ rank_Q A` for nonzero `A`; subadditivity; `ν_π(word) ≤` paid rank | 96 random words, 864 steps, up to 2 auxiliary registers, 74 free maps singular mod 2 |
| Positive controls reaching the target exactly at cost `mW` | 4 direct words, 2 Levi-conjugated, 2 Borel-conjugated with lower-left updates `K ≠ 0` |
| The data block alone has `ν_π = mW` (permuted outputs, Levi factors, clean-ancilla garbage); garbage cannot lower `ν_π`; a factor singular mod 2 drops `(g_w)_HD` | 3 instances, plus 1 |
| `m = 1` remark: mod-`p` module on dyadic words; `ψ_p` multiplicative, including free maps singular mod `p`; `≤ p − 1` per call, 0 on free moves, `W(p−1)` on targets | `p` ∈ {5, 11, 13}, 384 steps |
| Scope controls: a dyadic frame has no reduction; the commutator `d n_A d⁻¹ n_A⁻¹ = n_A` needs `d⁻¹ = diag(½I, I)`; a free upper map would reach `n_I` with no paid call; an even-diagonal target weakens the bound | 4 |

```sh
python3 -I -B research/bit-full-borel-2adic-floor/verify.py              # about 6 s
python3 -I -B research/bit-full-borel-2adic-floor/verify.py --mutations  # about 15 s
```

Expected final lines:
- `PASS_BIT_FULL_BOREL_2ADIC_FLOOR_FINITE_CHECKS products=90 cancellations=18 words=96 steps=864 singular_free=74 direct=4 conjugated=2 borel=2 general_targets=3 width_one_steps=384 scope_controls=4`
- `PASS_BIT_FULL_BOREL_2ADIC_FLOOR_MUTATIONS rejected=8/8`

The computed receipt must equal the committed `RESULT.json`; `--out` regenerates it. Inputs that are not 2-integral,
or not `p`-integral, surface as a `FAIL_` line. All results were run on CPython 3.14.4. The registered Python 3.12
replay was not run locally.

## Scope

- **Covered:**
  - 2-integral words on unit targets in the model above, including the block-lower parabolic free class (P1's
    Interface I);
  - `m = 1` with any rational data (a sanity remark).
- **Not covered:**
  - words at `m ≥ 2` that apply a matrix with an even denominator;
  - 2-integral words on targets that are not units mod 2, such as `n_{2I}`, which normalise to `n_I` only through
    dyadic free maps;
  - affine or carry-shift address maps;
  - nonlinear frames;
  - the complex primitive.
- **Not attempted:** mapping the selected bit supplier PR589, or any native word, into the model.
- **Selected frontier:** unchanged.

## Open next questions

- **`m = 2` with data outside `Z_(2)`.** Does the full Borel model save there? This is PR288's open item 3, now
  narrowed. Related dyadic work, abelian with a fixed small frame set:
  - merged PR1604 (Tuafo) and PR1679 (Maximooch): half- and quarter-integral ternary frames, nine-call floors with
    dirty registers;
  - open PR2085 (four roles with dyadic frames, an exact eight-call floor) and PR2112 (a fifth dyadic frame, six
    calls excluded, `7 ≤ min ≤ 8`), both by Cinna Davis, with Discussion 2091.

  First step: the smallest instance, with `W = 2`, three rank-one calls and one inserted `D += K·H`.
- **Where does PR589 leave `Z_(2)`?** If PR589's local frame path is a rational-frame XOR word of this kind, then
  because it saves on unit targets it must use an even denominator somewhere. First step: express one PR589 local
  frame path in this model and read off where the even denominators enter.

## Credits and licence

- **Swapnil Jain (P1, [doi:10.5281/zenodo.23265442](https://doi.org/10.5281/zenodo.23265442)):**
  - `ν` (Lemma struct-rho) and Theorem A;
  - Interface I's free class;
  - Cor. alg-mixed(ii) and its remark;
  - Prop. alg-origin.

  These are cited by statement and source label.
- **eumemic (PR288):**
  - the superposition register model (§0);
  - the FO lemma (§1.1(a)) and its `Λ/pΛ` form (§1.4(a));
  - the data–data block use (§1.3(b));
  - permutation-module FO certificates (§1.2(d), §1.3(f));
  - the §1.2 theorems and open item 3.
- **Cinna Davis:** PR2110 (square-zero map with dirty auxiliaries), PR2085 and PR2112.
- **Others:**
  - Gareth Davidson: PR1333;
  - Tuafo: PR1604; Maximooch: PR1679;
  - philippeVV: the masked-plane decoder floor (Discussion 1587);
  - Ali Romman (PR468): the three-register bound;
  - the upstream authors: Lemmas `ordered-affine-streams` and `matrix-shear`, and Proposition `bit-motif-interface`.

Prepared by Sagar Thakrar with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5). Three rounds of
adversarial AI review (seven reviewers) found the overclaims, credits and control gaps fixed in this version. No
independent human review is claimed. Apache-2.0.
