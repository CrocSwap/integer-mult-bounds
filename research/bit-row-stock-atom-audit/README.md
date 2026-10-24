# Audit of the #4359 BIT row stock and its #4470 atom change

**Audit with a positive scoped result; no new κ.** The selected κ is unchanged.

Base: `f626db5c3` (main after the #4470 review). This package independently
checks the BIT row-stock formulas that #4359 introduced, and the way the
#4440 → #4470 chain reuses them after raising the atom power from `0.003` to
`0.004`. The intake review of #4359 (`docs/research/pr-intake-evidence/pr4359/PROOF-REVIEW.md` §4)
argued the outer reserve in prose; no numerical or finite check of these
formulas existed.

## Statements checked

| Statement | Source | Outcome |
|---|---|---|
| `a_BIT = (1-δ)C1 + δ a_old` with `δ > a_BIT` (linear adapter paid), `δ < 1-a_BIT` (stock lower order) and the middle-exponent identity | DELAYED-COVER-BRIDGE §8; `query-thinned-controllers/verify.py` | Holds exactly: `0.0027418653797` (#4359, δ=.003) and `0.0034363538396` (#4470, δ=.004). With δ=.003 the #4470 adapter would fail, as its verifier says. |
| Cover prime `q > (256/d) N^5` gives fallback moment `(1+d/4)/(1+d/2) < 1` | DELAYED-COVER-BRIDGE §7 | Holds for `25,600,000` (#4359) and `2^26` (#4470). |
| Reserve `W(w)^D S_old`, `W(w) = B|GL_N(F_q)| q^(N^2(w-1))`, `D = floor(log_N ceil(e/w))` | DELAYED-COVER-BRIDGE §8 | Holds. `|GL_N(Z/q^w)| = |GL_N(F_q)| q^(N^2(w-1))` is brute-forced on small rings. The reserve divides exactly through D levels, and floor recursion has depth `floor(log_N n)`. The high-matrix factor is present, unlike the #4100 wording noted in #4432. |
| Borrowed digits `k = O(w log e) = o(e)` | DELAYED-COVER-BRIDGE §8 | Holds. With `log2 N = 6552928412` (#4359) or `25986965159937` (#4470 BIT), `2k < e` from `log2 e ≈ 2 log2 N/(1-δ)`: `1.3145·10^10` and `5.2183·10^13`. It keeps holding afterwards. |
| BIT-call width `≤ C h (log p)^2` | OUTER-TRANSFER-AUDIT §5, from SUPPLIER-SUPPORT-AUDIT | Holds with an explicit `C`. The exposed support is `2hK` and the three reservoirs add `9kG` with `k = 2hK`. With `K = 128G` and `G = 4⌈log2 p⌉+6`, the width is at most `2hK(1+9G) ≤ 232960 h L^2` for every `L ≥ 1`. |
| Its stock `O(h^δ (log p)^(1+2δ))`, nesting `log h`, plus complex `O(log h)`, giving `q0 ≤ C(log2 h + h^δ L^3 + 1)` | OUTER-TRANSFER-AUDIT §5 | Holds for both δ, because `2+2δ ≤ 3`. The comparison `e^δ log e ≤ C_w^δ(log2 C_w+3) h^δ L^(1+2δ)` is proved below and checked on a grid. |
| Threshold `H(p) = [1024 C L^3]^(1/(1-δ))`, `q0+O(1) ≤ h/64`, `R(h) ≤ 3h/128 + q0 + O(1) ≤ h/16` | OUTER-TRANSFER-AUDIT §5 | Holds. For `C ≥ 1` the displayed threshold already suffices; no extra multiple is needed. The phase sum is at most `1.067` times the first phase. |
| Old ordinary interchanges (`a_old`) act only on atom-width fields, so `S_old` is lower order | `notes/three-stage-cover-bit.tex` (weighted leaves; routing) | Holds. Its role split `W(w) = W_0 q^(m^2(w-1))` agrees with DELAYED-COVER-BRIDGE. |
| Delayed cover audit: cover size, routing bijection, projector matching, affine high-row carry | `delayed_cover_bridge.py` | Re-implemented independently for `GL_2(Z/9)` (3,888 rows) and `GL_3(Z/4)` (86,016 rows), with true inverses mod `p^w` and the carry for general `w`. Locally I also checked `GL_2(Z/27)` (314,928 rows) and `GL_2(Z/25)` (300,000 rows). All pass. |

## Corrections (wording only; no exponent changes)

1. **The written outer reserve is not updated for #4470.** OUTER-TRANSFER-AUDIT
   §5 writes `q0(h,p) ≤ C(log2 h + h^0.003 (log2 p)^3 + 1)` and the threshold
   `[1024 C (log2 p)^3]^(1/(1-0.003))`. The #4440/#4470 chain only says that
   the new constants are substituted, and it adds the check `β(1-0.004) > 0`.
   With atom `0.004` the literal display is false for large `h`, since it
   would need `h^0.001 ≤ C L^0.992`. The argument does not depend on δ. The
   correct statement for any atom `δ ≤ 1/2` is

   ```
   q0(h,p) <= C*(log2 h + h^δ*(log2 p)^3 + 1),
   H(p) = [1024*C*(log2 p)^3]^(1/(1-δ)),
   ```

   with `δ = 3/1000` for #4359 and `δ = 4/1000` for #4440/#4470. Every
   conclusion (`R(h) ≤ h/16`, polylog threshold, fit in `p^β`) is unchanged.
   The pinned file is source-bound by hash in the #4359 receipts, so it is
   left untouched; this package records the corrected display.
2. **`β(1-atom) > 0` is weaker than its name.** It is equivalent to `atom < 1`.
   It accepts, for example, atom `0.99999`, where `δ < 1-a_BIT` fails. The
   real condition `atom < 1-ordinary` is checked separately in
   `query-thinned-controllers/verify.py` and `joint-helper-lattice/verify.py`.
   No gap results.
3. **Three checks in `delayed_cover_bridge.py` cannot fail.** The projector
   matching `g P g^-1 = (gS) Q (gS)^-1` is equivalent to `P S = S Q`. Once
   `P = S Q S^-1` it holds for every `g`, so the 7,776 checks test arithmetic.
   The weight equality follows from projector equality. The 6,561-address
   scalar-gauge check builds `before` and `after` from the same expression.
   The cover size, routing bijection, carry formula and the two negative
   controls are genuine checks. The companion note's conjugacy argument, not
   the finite run, carries the claim, as the note itself says.

## Proofs

*Exponents.* The root costs are `e^(1-δ)`, `e^((1-δ)(1-C1)+δ(1-a_old))` and
`e^δ log e`. The middle exponent equals `1-a_BIT` by expansion. The first is
at most `1-a_BIT` iff `δ ≥ a_BIT`. The third is lower order iff `δ < 1-a_BIT`.

*Reserve split.* A level's rows are indexed by (role, low class in
`GL_N(F_q)`, high matrix in `(Z/q^(w-1))^(N^2)`, rest). This is a mixed-radix
digit of size `W(w)`. Ancestors own distinct digits, so `W^D S_old` rows give
every simultaneously live level its own digit and leave `S_old` at the leaves.

*Borrowed digits.* `|GL_N(F_q)| < q^(N^2)` gives
`k ≤ D(N^2 w + log_q B + 1) + log_q S_old + 1`, with `D ≤ log2 e/log2 N`.
Hence `k/(w log2 e) ≤ (N^2 + o(1))/log2 N`.

*Outer stock.* Let `e = C_w h L^2` with `1 ≤ h ≤ p` and `L = log2 p`. Then
`log2 e ≤ log2 C_w + 3L` and
`e^δ log2 e ≤ C_w^δ (log2 C_w + 3) h^δ L^(1+2δ)`. The `log h ≤ L` nesting
factor and the complex `O(log h)` give `L^(2+2δ) ≤ L^3`.

*Threshold.* If `h^(1-δ) ≥ 1024 C L^3`, then `C h^δ L^3 ≤ h/1024`, and
`C(log2 h + 2) ≤ h/1024` there as well. The derivative of `h/64 - q0` is
positive above `H`. So `q0 + O(1) ≤ h/64` and
`R ≤ 3h/128 + h/64 = 5h/128 ≤ h/16`.

## Scope

Conditional, like #4359 and #4470. Inherited and not re-proved here: the
outer analytic decomposition and fixed-tape model; that the finite compiler
really gives each live child distinct physical roles (DELAYED-COVER-BRIDGE
open question 1); the size of the fixed constant `C`. Thresholds in the
table use `log2 C ≈ 2 log2 N + 64` only for illustration. The astronomically
large templates are not materialized.

## Reproduce

```sh
python3 -B research/bit-row-stock-atom-audit/verify.py       # about 50 s
python3 -B research/bit-row-stock-atom-audit/test_verify.py  # 7 rejecting controls
```

The controls cover: the old atom with #4470's `C1`; the literal `h^0.003`
display at atom `.004`; a broken atom that passes `β(1-atom) > 0`; omitting
the high-matrix lift; a max instead of a product of stocks; an omitted carry;
and widths below the borrowed-digit threshold.

## Open next questions

1. Bind the constant `C` of the outer reserve to the actual #4470 template
   (`N`, `B`, `q`, centers). This would turn the illustrative thresholds into
   bound ones.
2. Audit DELAYED-COVER-BRIDGE open question 1. Does the lockstep compiler give
   each simultaneously live child role a distinct physical array? The
   row-digit argument above assumes that it does.

## Credit

zxv for #4359 and the delayed-cover bridge; Cinna Davis and zxv for the
#4440/#4470 controller chain; the capped-phase-fusion support-router and
three-stage-cover authors credited in those sources. Audit by Mark
(Matarener), prepared with substantial Claude Code assistance.
