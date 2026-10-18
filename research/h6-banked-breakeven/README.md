# H6 banked break-even and the I − K structure for the E8² Pauli factor

These are the scripts behind the H6 escape-map row of PR1590: the ×1.538 paper ceiling, R* ≈ 80,558 helpers, and 0.384 delivered rank per helper. They are published at an exact commit for an independent budget audit.

The package makes **no κ claim and no construction claim**. Everything uses PR606's merged `research/niemeier-lattices` unchanged, from this branch's base (origin/main).

## Reproduce (from the repository root; Python ≥ 3.11 with numpy)

```sh
python3 -B research/h6-banked-breakeven/price_h6.py                     # ~1 s
mkdir -p /tmp/h6 && cd /tmp/h6                                          # the structure scripts write/read b214_P.npy in the cwd
python3 -B $REPO/research/h6-banked-breakeven/structure.py              # ~30 s, writes b214_P.npy (sha256 349e8466…911fd)
python3 -B $REPO/research/h6-banked-breakeven/structure2.py             # ~15 s
python3 -B $REPO/research/h6-banked-breakeven/walsh.py                  # ~15 s
```

The saved outputs are in `outputs/` (macOS arm64, Python 3.14, numpy from our venv, 2026-10-14).

## price_h6.py: exact conventions

- **Invoice.** PR606 `workbench/paid-controller/banked.py` `invoice(n, h, hist, L, data, hp, R, virtual)` (L65–72), unchanged. The inputs are those of PR606's `complex` row:
  - `n = 30960`, `h = 17`, `hist = {17: 256, 15: 560}`;
  - data path `[16]`, helper path `hp = [1, 7, 8, 1]` (17 rank of stock per helper), `virtual = False`;
  - `L ∈ {3, 5, 7}`.
- **κ(L, R)** is the **lower** endpoint of `nominal_kappa_interval_scaled_1e18`, an integer scaled by 1e18.
- **R\*** is the largest R in `[0, 2,000,000)` with κ(L, R) **strictly** above the target. It is found by bisection on the invariant κ(lo) > target ≥ κ(hi). The boundary is re-checked (κ(R\*) > target ≥ κ(R\*+1)) and the output prints both values, so the integer boundary can be audited directly.
- **Comparison modes.** Both are reported:
  - `float`: `scaled/1e18 > float(target)`. This is the convention behind the published 80,558.
  - `exact`: `scaled > Fraction(target)·10¹⁸`.
- **Targets** are kept as exact decimal strings:
  - `0.001661957775`: the 10-digit #890 value we used;
  - `0.001661957774647029`: PR890's merged title;
  - `0.001676855229071321886206381217337893`: #1424's title, the open best when this was written.

  R\* is identical in both modes and for both #890 values. The κ margin above the target at R\* is ≈ 7.2·10⁻⁹ for #890 and ≈ 9.8·10⁻¹⁰ for #1424, far larger than the #890 rounding difference (3.5·10⁻¹³).

| target | L3 | L5 | L7 |
|---|---|---|---|
| #890 (either form) | 80,558 (0.3843) | 89,683 (0.3452) | 80,753 (0.3834) |
| #1424 | 79,617 (0.3889) | 88,409 (0.3502) | 79,399 (0.3899) |

The value in brackets is 30,960 / R\*: the full real rank of I − K (816 from K plus the 30,144-dim identity complement, PR606 `compensation_rank.py:50-60`) divided by the helper count. A *helper* is one banked restored-wire helper register in the invoice (path [1,7,8,1]), not a term or copy occurrence.

**The ×1.538 ceiling** is `ceiling()` in the script: the ratio of PR606 `COSTS.txt`'s zero-helper nominal κ for "E8^2 full Pauli factor" (.006945535353) to "E8 root reference" (.004515128332), which is 1.538281. That is the same 53.83% that COSTS.txt itself states. It is a paper ceiling: no compensation helpers, no bit-side cap, no construction.

**Not in the invoice**, so R\* is a necessary budget, not a sufficient one:
- the K encoder beyond PR606's base terms;
- compensation restoration and chronology (frame-0 precompensation, target cap-15 ↔ FULL, `COSTS.txt:160-161`);
- spectator or padding costs beyond `helper_pad`;
- sharing between compensation and other stages;
- any helper-loading or capacity lemma.

## structure.py / structure2.py / walsh.py: the exact I − K structure

These use PR606 `code/e8_cubed.py` `construct_shell()` and the port selection of `compensation_rank.py:11`.
- **I − K support and size.** I − K has zero diagonal and is supported exactly on odd t. It has nnz = 480,337,920, about 50% dense, with row degree 15,488–15,872.
- **Kronecker form on root × root ports.** There t = s_a + s_b. K is a sum of 6 Kronecker terms, and the Hadamard powers of the E8 Gram have ranks 8, 36 and 120. I − K itself is not a Kronecker sum: it has 3 block types, f(s+S) for s ∈ {0, ±1}, and the diagonal block I − f(2+S).
- **Walsh form (`walsh.py`).**
  - B = (t mod 2) = l M lᵀ, with labels l ∈ F2¹⁶ (14,670 distinct labels; multiplicities 2 and 8). This is checked on a 3000² sample.
  - I − K = (T∘B)/16 − ½·sgn(t)[|t| = 3], with max error 0.
  - T∘B = Σ_c D_c B D_c, where B = (J − W)/2 and W = (−1)^{l M lᵀ} is a submatrix of the 2¹⁶ symplectic Walsh matrix.
  - The |t| = 3 pairs are 0.70% of the non-zeros.

## Credits
PR606 (Dominik Scholz) for the E8² geometry, the K factor, `banked.py` and COSTS.txt. Escape-map analysis by DreamingOfClouds. Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
