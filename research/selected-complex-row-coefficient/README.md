# The complex row coefficient of the selected outer reserve is one

**Source-bound audit with an exact recomputation. No new κ.**
The selected conditional exponent stays 60403/20000000.

## Result

`research/lockstep-live-role-audit` bounds the #4470 outer-reserve constant
`C` of OUTER-TRANSFER-AUDIT §5 at `log2 C ≤ 64,215,200,000,088`. That bound
rests on two inherited, assumed coefficients: the complex row proportionality
`c_row ≤ 2^64` and the old-supplier stock `A_old ≤ 2^64`. Its open question 1
asks for both.

1. **`c_row = 1`.** The complex row field is exactly
   `q_0 = ⌈log2 B_c⌉ · ⌊log_{N_c} d⌋ ≤ ⌈log2 B_c⌉ · log_{N_c} d` chunks.
2. **`A_old` never binds.** It enters only as `log2 A_old + 10` inside a
   maximum whose complex term exceeds `6·10^13`. ([#4970](https://github.com/CrocSwap/integer-mult-bounds/pull/4970)
   separately derives `S_old = 1`.)
3. **New figures.** Rerunning lockstep's own pinned computation with `c_row = 1`
   gives:

| Quantity | Assumed `c_row ≤ 2^64` | Derived `c_row = 1` |
|---|---:|---:|
| Complex share `log2` | 64,215,200,000,086 | **64,215,200,000,022** |
| `log2 C` upper bound | 64,215,200,000,088 | **64,215,200,000,024** |
| Fit point `log2 p` | 64,473,100,659,114 | **64,473,100,659,050** |

The same computation gives a lower bound of `2^64,215,199,999,954` for the
complex share in this realization. So the upper and lower complex shares now
differ by 68 bits instead of 132.

## Derivation

Each step is a verbatim phrase checked against a pinned source.

1. **The reservation.** `notes/batched-complex-rows.tex` (a #4470 proof
   supplement) replaces the complex row reservation with
   `k_0 = D_c(d)` and `q_0 = ⌈log2 W⌉ k_0`. The row field "consists only of
   the first `q_0` chunks". It is padded once to a multiple of `W^{k_0}`, and
   every child gets exactly `1/W` of its parent's volume. OUTER-TRANSFER-AUDIT
   §5 counts `q0` in the same unit, "reserved complete chunks".
2. **`W` is `B`, and the child ratio is `1/N`.**
   `research/kappa-rebuild/transfer-audit/AUDIT.md` §6 says: "The row stock is
   based on B, not B+O", with the retained bound proportional to
   `ceil(log2 B)*log_N(d)`. It adds: "The new child ratio is `1/N`". Its
   semantic recurrence uses `f = ⌊e/N⌋`.
3. **No deeper recursion hides inside the compiled program.**
   FINITE-PRECOMPILATION: "Induction removes all recursive calls: the only
   remaining paid children have rank one." Exit batches handled by smaller
   uniform programs are finite composition inside the fixed rank-`N` program.
   They are not extra outer depth. Every outer recursive child is a tensor job
   of size `⌊d/N⌋`.
4. **Depth.** So `D_c(d)` counts the steps `d ↦ ⌊d/N⌋` until `d < N`, which
   is `⌊log_N d⌋`. The verifier checks this at five ranks over thousands of
   widths, including `N^j ± 1`. Hence
   `q_0 = ⌈log2 B_c⌉⌊log_{N_c} d⌋ ≤ ⌈log2 B_c⌉ log_{N_c} d`, and the
   proportionality is `c_row = 1`.

The old-lineage "row coefficient" 20,161, cited in lockstep's comment, was
an allowance in the κ≈0.0015 assemblies (16,467 used out of 20,161). That
was a different reservation, counting chart digits per level. It is not a
coefficient of the #4470 batched-complex-rows formula.

## Recomputation

`verify.py` authenticates the bytes of
`research/lockstep-live-role-audit/constant_c.py`. It runs `compute()`
unchanged and reproduces lockstep's published values. Then it substitutes
exactly one assumption line in memory, `log2_c_row = 64` → `log2_c_row = 0`,
and runs `compute()` again. The pinned file on disk is never modified.

All of lockstep's internal checks still pass in the substituted run. These
include the threshold proofs `q0 ≤ h/512` at `h = H` for six values of `L`,
and the dominance of the #4618 term.

## Scope

Card `selected-stock-envelope` (adversarial audit), scope **refined** (see
`TASK.json`). This does not re-derive:
- `B_c` or the compiled ranks;
- the support router;
- the BIT share;
- the analytic outer premises.

It is a source-bound reading of the retained reservation, not a new proof of
it. Base: canonical main `b91956876e5b4122fd89179f1b57557ff8378f15`,
priority revision 7. Claim:
[#1166 comment](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19138183).

## Reproduce

```sh
python3.12 -B research/selected-complex-row-coefficient/verify.py
python3.12 -B scripts/research_package.py --package research/selected-complex-row-coefficient
```

It runs in under a second. Changing the derived `log2 C`, using
`log2_c_row = 1`, or perturbing the depth recursion makes it fail.

## Open next questions

1. **Close the 68-bit gap.** The upper and lower complex shares of `C` now
   differ by 68 bits. *First step:* compare lockstep's upper bound for
   `log2 B_c / N` with its `2^(N−m)` lower bound term by term, and locate the
   rounding steps that contribute the gap. *Blocked by:* nothing.

## Credit

- Mark (Matarener), `lockstep-live-role-audit`, for the constant `C`, its
  computation and the open question.
- The `batched-complex-rows` authors, for the reservation.
- The authors of `research/kappa-rebuild` (AUDIT, OUTER-TRANSFER-AUDIT,
  FINITE-PRECOMPILATION).
- Cinna Davis and zxv, for the #4440/#4470 chain.

Prepared by James Reed with substantial Anthropic Claude (Claude Code)
assistance. Apache-2.0. No independent human review is claimed.
