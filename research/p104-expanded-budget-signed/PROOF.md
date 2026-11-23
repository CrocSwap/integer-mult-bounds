# Exact price and resource proof for the enlarged profiles

The parent is ToikY's #8072 at `75f7e1c44f48c43983016bcf8878c4d9e5e87c62`. The archived #8057 source is restored and authenticated by #8072's manifest. The parent installer and its literal cutoff, stage and floor checks have fixed SHA-256 images in `verify.py`. The new overlay changes only the profile, its expected complete price, and profile-dependent assertions; it keeps the original occupied-edge calendar and source tests. `retune.py` pins the two resulting `installations.py` hashes. `UPSTREAM-README.md`, `UPSTREAM-PROOF.md`, `UPSTREAM-RESULT.json`, and `UPSTREAM-VERIFY.json` preserve the parent claims.

## Prices and stopping margins

Let

```text
c_B = 4391986206293/2^50,  d_B = 11239/8192,
c_G = 17145637307/2^42,   d_G = 64939/524288,
g   = 1/10^18.
```

For each ordinary height `h_i`, the bank starts with `b_0=0` and sets an intermediate rate one `10^-21` tick below the directed floor of

```text
min(39/10000, (249 (c_B - d_B/h_i) + b_(i-1))/250).
```

The final rate is the booked `κ+5g` and is strictly below the same expression. The positive rate is `c_G-d_G/H_G` and is strictly above `κ+5g`. The two complete receipts give every rate and rational margin. Their necessary all-stage ordinary floors and positive floors are `(534380,743589)` for profile 300, and `(542837,978582)` for profile 340. The Gaussian heights attain their respective strict integer floors. The control lowers each Gaussian height by one and obtains an unfunded positive inequality. Reducing either installed second or third ordinary height by one also fails, as does imposing the #8072 heights on either new target.

The positive booking also gives a height-independent ceiling: `κ < c_G-5g`, because `d_G/H_G` is positive. In particular, this unchanged source cannot fund `κ=0.0039` at any finite height; reaching that rate requires a separately funded change in the positive source or its charge.

The materialized calendar retains the 18,906 K7 productive labels, 104,652 paid labels and 24 transfers. It keeps the literal ordinary lower floor 18,960 and separately checks every loaded receiving label and the finite occupied-edge return stream. The positive source keeps two physical types with frequencies 5 and 451, lower cutoff 1,874, upper divisor 1,724, 51 installed grade cells and 88 typed cells. The original checks reconstruct its directed moments, finite fringe and placement, validate timed source blocks and nested/exterior returns, and reject a wrong signed return. The additional independent rational enclosure checks both full finite factors and the inherited `375/376` child contraction. There is no newly claimed deletion or reduced recurring debit.

Each profile passes the inherited 54 strict and four functional signed outer inequalities with `g=10^-18`; the `ordinary-κ-4g` margin is `10^-18`. The numerical positive margins and all selected intermediate rates are in the generated `RESULT-*.json` files. An explicit control removes the required ordinary margin and is rejected.

## Why the stated invoices are economical

The high-fibre clock applies to three ordinary heights at least 8,192. In the declared tariff, and after charging selection and entry conversion, the candidate's terminal bound is

```text
log₂ C = 1731 + 320(h_1+h_2+h_3) + 220 H_G.
```

The ordinary height sums are 610,572 and 620,117 respectively. We prove each sum is minimal in this invoice family for the corresponding stated target. Dropping the clamp and rounding ticks gives the ordinary upper bound

```text
c_B(1-250^-3) - (249/250)d_B (w_1/h_1 + w_2/h_2 + 1/h_3),
w_1=1/62500, w_2=1/250.
```

For a proposed sum `M` one less than the installed sum and a rational `r` strictly below `1/sqrt(250)`, Cauchy's inequality gives

```text
w_1/h_1 + w_2/h_2 + 1/h_3
  >= w_1/h_1 + (1+r)^2/(M-h_1).
```

At `h_1=8192`, the code checks `w_1/8192^2 < (1+r)^2/(M-8192)^2`. The right side is therefore increasing for every allowed `h_1>=8192` with `h_1<M`. Its value at the endpoint already makes the relaxed ordinary cap strictly smaller than `κ+5g`. The check uses exact rational arithmetic, including `r^2 < 1/250 < (r+10^-41)^2`. Thus no permitted ordinary triple with smaller sum can fund the target. The separately monotone Gaussian price requires at least the given `H_G`. As the terminal invoice is a lower bound on this particular *computed invoice*, not on physical runtime, the installed invoice is smallest in this tariff family. No global optimality across other clocks, suppliers, stage counts or finite-debit arguments is claimed.

## Prefixes, clock and precision

The terminal cuts are `(8290,44036,610798)` and `(8290,44574,620343)`. Each previous cut plus two is strictly below the next native height. The producer's actual selector is checked on both sides of each cut, and the real stage dispatcher is exercised at direct and compiled widths for stages two and three. A control sets a stage height equal to the previous cut plus two and the stock check rejects it. The first reachable multiple-of-six terminal headers are `2^1354635+4` and `2^1599173+4`. At these entrances the historical first/cofinal stripe margins are `(675264,654180)` and `(797533,772628)`; all prefixes and later dyadic jumps satisfy the inherited stock bound.

The terminal ordinary charges are `log₂ B = 195383168` and `198437568`. Every `h_i>=8192` meets the inherited per-prefix high-fibre bound: `η=39/10000>1/258`, the endpoint gives `u>=2^30`, and `2660000(j+2)<2^j` at `j=30` with the subsequent dyadic induction. The inherited 320-per-height charge therefore continues to pay the variable compiler, scans, child contraction, rectangle, rounding and restoration. The ordinary and positive level floors, grid precision `2^(-64(H+1))`, Gaussian active calendar, signed opposite transforms, exact coefficient recovery and both full owner returns remain charged by the parent's all-size arguments.

The entry profile remains `(3000,3080;1024)` at κ `0.00345`, with its existing `log₂ B=125433359`, `log₂ C=125660241`, and low-height surcharges. At the new entrances, converting the entry interval to the terminal rate requires exactly `ceil((κ-0.00345) A)`, or 608 and 717 bits. Each converted entry charge is below the corresponding terminal charge. The final selector, header and restoration cost one further bit. The `17^16 * 10^(21*16)<2^1182` check retains the outer precision and stopped-tail allowance. The full bounds are 358,974,351 and 413,727,211 respectively, compared with the parent's 318,292,011. A one-bit-short cap is rejected.

All terminal ordinary and positive height *integers* have at most 20 bits, as required by the fixed source setup census. The physical words, role and grade counts, compiler structure and number of recipes are unchanged; the extra height fields fit the same bounded indexed arithmetic. The stated setup remains below `2^228` serial tape transitions under the predecessor's `2^68` indexed-action, `2^38` datum-width and restoration bounds. The native setup checker replays quotient, Bézout and rational operations as well as that exact integer ceiling. The private control envelopes become `761435139` and `1002067971` log units and the inherited live stock bound is `6.2 p T < 297.6 n` bits.

The terminal threshold does not fit a physical host execution. The product check performs signed finite products and an entry-tier physical coefficient fixture; separate tests exercise both signed source types, real exterior births, nonzero nested returns and the enlarged constructor/floor paths. Full asymptotic admission remains conditional on the five named inherited premises and independent assessment of their link to this machine.
