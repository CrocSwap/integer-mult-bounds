# Fixed installer bound at 28-bit ordinary heights and ten recipes

This note extends the 25-bit fixed-installer lemma of [#8081](https://github.com/CrocSwap/integer-mult-bounds/pull/8081) (`research/p104-expanded-budget-25bit/SETUP-PROOF.md`) and the 27-bit extension of [#8094](https://github.com/CrocSwap/integer-mult-bounds/pull/8094) (`SETUP-27BIT.md`) directly up to the sharp `w = 2^38` individual datum ceiling at `H < 2^28`. The encoding argument is unchanged; only the explicit numerical bounds below change. As in `#8081` and `#8094`, this is an encoding and action-count bound on the fixed installer constructors, not a rate-admission condition by itself.

**Scope.** The installed profiles contain 2 entry ordinary recipes, 6 terminal ordinary recipes, and 2 Gaussian recipes, totaling **10 height records** (`len(low) + len(high) == 10`, with `1 <= len(TERMINAL.rank_logs) <= 7`). Every ordinary height satisfies `8192 <= H < 2^28` (`max_native_H = 2^28 - 1 = 268435455`). Both Gaussian heights remain tiny (`ENTRY.complex_log = 1024`, `TERMINAL.complex_log = 52270 < 2^16 < 2^25`). The 128-bit scalar-encoding guard on `kappa`, `eta`, and `positive_stop_denominator` remains enforced (`assert all(abs(x).bit_length() <= 128 ...)`).

**Height-dependent paths & sharp `w = 2^38` ceiling.** As established in `#8081`, `Recipe.__init__` and `WeightedRecipe.__init__` record `H` and `92H` and defer constructing large calendars until caller invocation. For `H <= 2^28 - 1`:
- `92H <= 92 * (2^28 - 1) = 24696061860 < 2^35 < 2^38` (lazily materialized `2^(92H)` stays strictly below the source datum width bound `w = 2^38`).
- The fixed native control exponent `1024 * H + (m + 1).bit_length() <= 1024 * (2^28 - 1) + 3 = 274877905923 < 2^38 = 274877906944`. Note that `H = 2^28` gives `1024 * 2^28 + 3 = 274877906947 > 2^38`, making **28 bits (`H < 2^28`) the exact sharp upper limit** compatible with the inherited datum bound `w = 2^38` without lifting `w`.
- Each Gaussian carrier `1 << G` uses at most `G + 1 = 52271 < 2^16` bits (`<< 2^25`), keeping all Gaussian carrier arithmetic far smaller than `#8094` (`G = 208653`).

**Count.** Charging two maximal Gaussian carriers at `2^25` plus `2^24` elementary transitions per recipe across all 10 height records gives:

```
2 * 2048 * (2^25 + 1) + 10 * 2^24 = 137,606,729,728 < 2^40,
```

leaving `#8081`'s separate `< 2^40` setup carrier allowance and `< 2^228` complete transition bound intact (`assert setup["all_setup"] < 2**228` in `receipt.py`).

**Cuts and entrance logs.** Stage entrance cuts `(8290, 71968, 1077853, 16981277, 268435452, 536870971)` are computed as unbounded Python integers by `entrance_logs` and `activation` (just as cuts exceed `2^26` in `#8090` and `2^28` in `#8094`), while no fixed-width constructor descriptor stores a cut.

**What is not covered.** Heights `H >= 2^28` violate `1024 * H + 3 < 2^38` under the inherited datum bound and are excluded here.
