# Six-column Gaussian pricing with ToikY’s ordinary child tariff

At the same complete recurring bound of 318,291,900 log₂ units, the six-column construction raises conditional κ from 0.003898223617430 to **0.003898226579820971**. The increase over ToikY’s exact stopped #8076 ceiling is 6334499898761145463273 / 2138306510848000000000000000000. The gap to 0.0039 is 0.000001773420179029. [Pinned #8076 source](https://github.com/ToikY/integer-mult-bounds/tree/d502eb21637717fe22fc16d4c4e3ede6ec59a106/research/p104-weighted-child-tariff)

| Charged quantity | ToikY #8076 | Composite |
|---|---:|---:|
| Ordinary debit | 11178/8192 | 11178/8192 |
| Gaussian debit | 64939/524288 | 125645/1048576 |
| Ordinary heights | (8192, 111681, 524288) | (8192, 118919, 524288) |
| Gaussian height | 509812 | 499284 |
| First terminal header | 2^1154447 + 4 | 2^1151157 + 4 |
| Entry conversion | 518 bits | 516 bits |
| Complete recurring log₂ bound | 318291900 | 318291900 |
| Serial setup log₂ bound | 228 | 228 |
| Largest native height | 524288 | 524288 |

Both tiers pass 54 strict inequalities, four functional conditions and the positive Gaussian condition. The positive margin on the terminal tier is 1072827333439 / 2094148878336000000000000000000. The entry ordinary bound is 125433364. The terminal ordinary bound is 208447817. The ordinary tariff 2401/1024 contracts by a factor at most 2400/2401, so its geometric sum is at most 2401. The invoice retains the five additional entry bits and three additional bits per terminal stage from #8076.

The preceding six-column proof supplies the Gaussian debit. For a matched grant from grade r to k, its mean retained suffix is bounded by 7(k−r) + (1−c)r²/(2kL) at L = 1054. Substitution into the exact 51-cell table, including all 88 typed shares, yields a finite multiplier below 1.086602588030. The square-root calculation rejects the next smaller debit on denominator 2²⁰. The donor, endpoint, quadrature and unmatched charges appear in the complete Gaussian account. The underlying all-column operators inherit their phase and spectator convention. The other four premises concern owned erasure and suspended fields, uniform chronological mixed compilation, fixed-tape precision and movement, and analytic recovery. Finite fixture execution and the all-size conditional implication have distinct scopes.

## Exact comparison for one through seven ordinary stages

For l ordinary heights at least 8192, terminal accounting gives the necessary bound 1731 + 3l + 320ΣH + 220G. The released checker replays the three-stage crossing at the actual cap and the slightly larger 318291911 comparison cap. It recovers #8076’s exact stopped ceiling 1667119388378402860472786027 / 427661302169600000000000000000 and the composite ceiling 1632693363926333812833543539 / 418829775667200000000000000000 at both caps.

At fixed G at the crossing, the reciprocal tangent maximizes the relaxed three-stage ordinary recurrence at its first minimum height and last maximum height. All other integer triples lose more than the two intermediate downward grid roundings. The next G has an ordinary upper below the current Gaussian upper. The Gaussian upper increases with G and the set of feasible ordinary profiles decreases with G. These two neighboring slices therefore locate the exact crossing.

For one or two ordinary stages the common clamp directly bounds the recurrence, and the relaxed two-height optimum uses the final height 524288. For four through seven stages, remove the cost of at least one earlier height from the available sum and retain the maximal entering credit η/250³. The reciprocal tangent on the surviving three heights quantifies a strict gap in every case. Repeating the argument at clock 318291899 puts the best stopped upper below the booked composite κ. Thus 318291900 is the smallest integer clock bound permitting that rate within this pricing and height family.

## Reproduction

Place the preceding six-column #8073 archive alongside this addendum. From the extracted addendum directory, run

```sh
python3.12 -IB replay8076.py --predecessor-archive /path/to/six-column-8073-public.tar.gz --output /path/to/new-results
```

The runner checks the preceding archive SHA-256, the nested 88-file #8057 archive and the 15 Git blob identities of #8076. Each run creates a fresh source tree. By default it checks all 14 candidate scopes, the authoritative #8076 invoice, the independently repriced ordinary tariff and the exact one-to-seven-stage optimization. A shorter economic/control run uses `--scope source_invoice ordinary_tariff stage_caps invoice independent_price cutoff corrupted_owner`. The output directory must be new so earlier observations stay recoverable.

Ali Romman supplied the signed 48-call Gaussian word, physical compiler, installer and fixed-resource argument. SYLforge supplied the K7 ordinary word. ToikY supplied the two-type calendar, the ordinary 8/L estimate and the 2401/1024 child tariff. The six-column price and its safety proof belong to the accompanying Gaussian contribution. The original notices, licenses and further source credits are preserved in the pinned scientific package and nested archive.

The registered package price command runs the short economic and source-control selection. For just that selection, run `python3.12 -I -B research/p104-integrated-gaussian-suffix/verify.py addendum`. The other ten scientific scopes are not run by that command; their separate observed source-replay status is in [EVIDENCE.md](EVIDENCE.md). The complete source replay remains available from the unpacked `source-view-8076/replay8076.py` with the pinned predecessor archive and a new output directory.
