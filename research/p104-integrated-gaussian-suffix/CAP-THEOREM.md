# Capped stopped rates for one through seven stages

The theorem here concerns the source's fixed bookings and tariffs, not all possible integer multipliers. Let `b₁,…,bₙ` be ordinary terminal heights, `1 ≤ n ≤ 7`, each in `[8192,524288]`; let the Gaussian height `G` lie in `[1024,524288]`. The source tariff requires

```text
1731 + 320 Σ bᵢ + 220 G ≤ C₀.
```

The source's entry price and conversion must also be paid; the explicit invoices show that the terminal branch dominates for the samples. Set `cB = 4391986206293/2^50`, `cG = 17145637307/2^42`, `η = 39/10000`, and `δstop = 5·10^−18`. Start `r₀=0`, apply `rᵢ < min(η, (249(cB−dB/bᵢ)+rᵢ₋₁)/250)`, with the source's downward `10^−21` grid and one extra guard tick for each intermediate stage, and require `κ + δstop < cG−dG/G`. These are the prices of the original signed caller, including the strict stopping reserve.

| Family | `C₀` | `dB` | `dG` | exact stopped supremum | crossing `G` |
| --- | ---: | --- | --- | --- | ---: |
| e−6 | 318291911 | `11204/8192` | `125645/2^20` | `523210571423785163651433485201/134217728000000000000000000000000` | 491002 |
| e−8 | 318291911 | `11204/8192` | `130699669/2^30` | `523210399077391326763724428177/134217728000000000000000000000000` | 496173 |
| published #8073 family | 318292011 | `11204/8192` | `64939/524288` | `523210198560303585338978849681/134217728000000000000000000000000` | 501831 |

The e−8 sample invoice uses `G=496174`; the row above is the fixed-family crossing and does not claim that the displayed sample has the least e−8 clock. The #8073 family cap is the `318292011` cap in its published proof; its installed invoice is `318291911`.

For three stages, relax the clamp and directed intermediate floors to obtain the weighted reciprocal objective with weights `(1/62500,1/250,1)`. At each listed crossing the optimal relaxed heights have the first at its floor and the third at its ceiling. Their reciprocal tangent slopes increase strictly. Every other integer allocation under the same sum budget loses at least the positive tangent gap computed in [seven-stage.json](data/seven-stage.json), greater than the actual intermediate grid loss. The unrelaxed directed recurrence therefore attains the displayed ordinary upper endpoint as a supremum. The Gaussian bound is monotone in `G`, and the feasible ordinary budget decreases with `G`. The adjacent Gaussian heights settle both sides of the crossing.

To rule out a strictly better rate with one, two, or four through seven stages, the Gaussian inequality first gives the smallest `G` capable of beating the three-stage supremum. The clock then gives a maximum ordinary height sum. A one-stage relaxation uses `b=524288`; the two-stage reciprocal tangent gives the stated optimum. For four or more stages, at least one earlier height costs `8192`; its entire contribution to the last three stages is bounded by `η/250³`. Dropping all further earlier-height costs, clamps and grid losses can only increase the relaxed upper bound. The exact rational comparisons in [all_stage_caps.py](checks/all_stage_caps.py) put all of these upper bounds strictly below the corresponding three-stage supremum. The smallest e−6 separation is more than `2.827240394×10^−9` for the four-or-more relaxation.

The same calculation proves a separate minimum-clock statement for the **booked** e−6 rate `0.003898222531555482` in this model. At complete clock `318291610`, positive funding forces `G≥491002`, leaving ordinary height sum at most `657091`; even the relaxed best three heights `(8192,124611,524288)` fall short by the positive fraction in [minimal-clock.json](data/minimal-clock.json). The one-, two-, and four-or-more-stage relaxations also fall short. The actual signed receipt pays `318291611`. This is an exact integer invoice result for the declared prices and stages; it does not rule out a new native word, tariff, budget, owner contract or compiler.
