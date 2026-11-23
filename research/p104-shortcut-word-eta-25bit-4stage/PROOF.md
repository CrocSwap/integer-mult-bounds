# Retuned K7 ordinary floor and exact height allocation

The comparator is [#8073](https://github.com/CrocSwap/integer-mult-bounds/pull/8073), κ 0.003898219753506. Its exact fixed-booking stopped ceiling is `523210198560303585338978849681/134217728000000000000000000000000`, and this package re-derives it in `check_stage_seam.py`. The new installed target is 0.003898224460300, above that ceiling. The signed words, source access, owner restoration, caller, compiler, fixed tape and precision, and analytic recovery stay under the same five assumptions.

## One parameter in the all-size K7 invoice

#8073's complete directed ordinary factor is

`(47/20)(256/255)(4097/4096)(1028/1024)(1024·134·L)^c (1+s/L+δ) / ((1−10/L)(1−δ)^3)`, with `c = 4391986206293/2^50` and `δ = 2^-128`.

Here `s` bounds `10Σk/(tΨ)`. #8073 proves `s < 7.439580926465596639` from the unchanged K7 source, with 18906 productive labels, 104652 paid labels, 24 transfer shares and 286098 weighted target axes. Ψ is a sum over the 24 directed edges only, so neither the bound nor its additive errors (`2^30/N^5`, `2^46/N^4`, `2^20/N^4`, the grid enclosure) depend on `L`. This package books `s = 186/25`. `check_ordinary_floor.py` asserts `0 < 10Σk/(tΨ) < 186/25` and reports the ceiling 7.439580927 (×10⁹ rounded up).

The floor `L` is a free construction parameter of the binary recipe (`level_floor`). #8067 picked 18960, which is where `c log L + (s+10)/L` is minimal when `s = 64`. With `s = 186/25` the minimum sits at `L = 4474`. Every floor hypothesis in `check_ordinary_floor.py` holds there:
- `L` is even and `24(L+2) < 25L`;
- `L^t > 1024` (about 4331);
- `(1−10/L)Ψ > 1`;
- the 77-power delay bound holds;
- the first two columns are `(4466, 4468)`.

The literal recipes open with `level_floor = 4474` through the installed `Recipe.open` seam, for all five ordinary stages (entry and terminal).

The directed factor at `(L, s) = (4474, 186/25)` is below 2.573602304817903473. Directed 192-bit roots show:
- `2^(1430037/2^20)` exceeds it by more than 7.58e-7;
- the next finer point `1430036/2^20` fails;
- #8073's own `(18960, 8)` booking fails the new allowance.

`receipt.py` also checks `upper^(2^20) < 2^1430037` exactly. The 47/20 child charge, the 375/376 contraction and the Gaussian booking `64939/524288` with its bands 1874/1724 are unchanged.

## Capped integer allocation

This uses the same model and the same cap as #8072 and #8073:
- three ordinary heights in [8192, 524288] and one Gaussian height;
- `1731 + 320Σb + 220G ≤ 318292011`;
- the stopped rate is the minimum of the three-stage recurrence (with 1e-21 booking ticks) and the Gaussian rate, less 5e-18.

At `G = 511587` the cap leaves `(8192, 110461, 524288)`. Its weighted reciprocal tangent slopes are strictly increasing, so #8073's integer-optimum argument applies unchanged. `G − 1` keeps the same ordinary heights and fails Gaussian, and `G + 1` forces `b₂ = 110460` and fails ordinary. Two- and four-stage schedules under the same cap are lower (two stages: 0.00389818; four stages: 0.00389822181).

## Literal invoice

The full recurring log₂ C is 318291991, after the entry path with 518-bit conversion. The funding floors are (516019, 511587). The binary cuts are (8290, 118815, 643167), the first terminal header and stock come from `RESULT.json`, and the maximum native height is 524288. Conservative fixed serial setup stays below 2^228, because the setup scope is unchanged.

## Predecessor credit

Everything except the floor, the suffix booking, the debit grid and the profile comes from [#8073](https://github.com/CrocSwap/integer-mult-bounds/pull/8073) (Campaign contributor with OpenAI Codex). That builds on:
- Ali Romman's [#8042](https://github.com/CrocSwap/integer-mult-bounds/pull/8042) suffix argument, [#8057](https://github.com/CrocSwap/integer-mult-bounds/commit/cbe847a953b971f9c6c5a0a6661e2008acd29086) signed producer and [#8055](https://github.com/CrocSwap/integer-mult-bounds/pull/8055) setup proof;
- SYLforge's [#8052](https://github.com/CrocSwap/integer-mult-bounds/pull/8052) K7 word;
- [#8059](https://github.com/CrocSwap/integer-mult-bounds/pull/8059) through [#8072](https://github.com/CrocSwap/integer-mult-bounds/pull/8072) for the Gaussian factor, the bands, the floor computation and the allocation method.

The floor retune and this package were made with Claude (Anthropic).
