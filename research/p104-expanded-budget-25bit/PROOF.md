# Price, cutoff and charged 25-bit installer

The exact predecessor is ToikY's #8072 at `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`. `upstream_verify.py` authenticates the archived #8057 members; `prepare.py` restores the #8072 signed source and `retune.py` binds the new installation image. The unchanged paid words, their source notices, and #8072's proof and invoice are preserved with the package. This is an enlarged-resource result, conditional on the same five premises as the predecessor.

## Complete price

Use

```text
c_B = 4391986206293/2^50,  d_B = 11239/8192,
c_G = 17145637307/2^42,   d_G = 64939/524288,
g = 1/10^18.
```

The ordinary bank starts at `b_0=0`, and each intermediate rate is one `10^-21` tick below the directed floor of `min(39/10000, (249(c_B-d_B/H_i)+b_(i-1))/250)`. The terminal booking is `κ+5g` and the positive funding is `c_G-d_G/H_G`. For `κ=0.00389846`, `H=(8192,38102,604362)`, and `H_G=18845936`, both strict inequalities hold. The receipt retains the exact rational rates, all 54 strict and four functional outer checks, and the positive margin `1131296769828489/3952279237427200000000000000000`.

The entry remains `(3000,3080;1024)` at `κ=0.00345`. The terminal cuts are `(8290,46456,650882)` and the first multiple-of-six public header is `2^19497094+2`. Exact conversion costs `ceil((0.00389846-0.00345)*19497094)=8744` bits. With `log₂ B=208210048`, the complete high-fibre price, including the final selector bit, is

```text
log₂ C = 1731 + 320*(8192+38102+604362) + 220*18845936
       = 4354317571.
```

The installed ordinary sum is `650656`. The checker proves, in this declared three-stage invoice family with heights at least 8192, that even a relaxation of any smaller sum fails the booking. It combines Cauchy's inequality with a rational lower enclosure of `1/sqrt(250)` and checks that the relaxed loss is increasing in the first height from 8192. Monotonicity also makes `18845936` the first Gaussian integer that funds this rate. Separate controls reject one-unit cuts in the second or third ordinary height, one-unit Gaussian reduction, the old heights at the new rate, an unfunded outer margin, a previous-cut prefix, and a one-bit-short recurring budget. This is invoice optimality in the stated family, not physical-time optimality or a bound on different suppliers or clocks.

The inherited first/cofinal stripe margins are `9746477` and `9441934`; the direct and compiled stage dispatch seams are exercised at both transitions. The private control envelope is `19298238467` log units and the inherited live-stock estimate is `6.2 p T < 297.6 n` bits. The untouched positive source also has `κ < c_G-5g < 0.0039`, so no finite Gaussian height of this source reaches the registered target.

## Source opening and cutoff

The positive source retains its two native types, weights `(5,451)`, lower cutoff 1874, upper divisor 1724, 51 grade cells and 88 typed cells. The calendar replays real finite owner returns and the lower-cutoff birth fixture. It authenticates the source `grades.py` and invokes its actual `WeightedRecipe.open` with an exact algebraic representation of powers of two. This captures its `M`, `M**6`, `M**82`, `M**2`, `2**(92H)` and even upper-fence expressions without allocating their terminal-size integers. At heights 1024 and 2048 every captured argument is compared against a literal integer execution. The bound `floor(x/a)-floor(x/b) >= floor(x(b-a)/(ab))` for `x=2^H` proves strict separation of the two upper divisors for all admitted `H>=1024`; `2*4*258 < 1724*306` proves the stated carrier fence. The separate finite lower fixture and direct/compiled ordinary seams still run literally. These checks do not claim a materialized terminal calendar.

## Installer and physical boundaries

`SETUP-PROOF.md` derives and states the separate 25-bit fixed-installer charge, including generation of the actual `2^H` Gaussian carrier and the inherited indexed-action and datum-width hypotheses. The exact check instantiates all seven entry and terminal heights, forbids lazy native opening and width materialization during `compiler_state.construct`, checks the actual carrier, and reproduces the 2,407,819-record directory. The 137556398080 added carrier/scalar steps fit inside a separately added `2^40` allowance; the fully recalculated serial upper bound remains below `2^228`. The check also executes the original serial integer/rational arithmetic controls. It is not a new portable WASI fuel trace.

The raw, exterior and nested checks execute finite source and owner-return fixtures. The physical product scope tests signed products and an entry-tier coefficient fixture; it also checks construction of both profile suppliers. None executes the terminal-scale input or by itself discharges the five inherited assumptions. The status is a conditional author result pending independent review, and neither the `0.0039` target nor a maintainer-selected frontier is claimed.

The lower-profile predecessor [#8078](https://github.com/CrocSwap/integer-mult-bounds/pull/8078), head `b72d3fa097d2521939f6b8536029da674648d863`, established the earlier 20-bit allocation and economic-control method on which this higher-width follow-up builds. The high result independently charges and tests the larger installer and rate.
