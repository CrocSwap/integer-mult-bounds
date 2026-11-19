# Continued rational returns in the P104 multiplier

The complete finite application gives **conditional κ ≥ 0.00387937849702**. Its directed raw crossing is **[0.00387937849710, 0.00387937849711]**. The finite point exceeds the preceding submitted #7786 word’s directed upper endpoint 0.00387827242164 by **0.00000110607538**. Against #7781’s directed upper endpoint 0.00386981257853, it gains **0.00000956591849**. The comparisons use the same 48-call rational caller, 36-call binary service and five outer premises. The target has a remaining κ gap of **0.00000043408151**. [Immutable #7786 predecessor](https://github.com/CrocSwap/integer-mult-bounds/tree/787cdddaa7f32b05c44452b8c52a376b600b5348/research/p104-iterated-returns) · [Original #7781 comparator](https://github.com/CrocSwap/integer-mult-bounds/pull/7781) · [Directed finite application](evidence/application.json)

## Construction

The source word is `e40b999de906fe3834c42af2dca8c0977211c606f6c9bd6a514771c3956f7ec3`. Each step reads a causal linear form, restores every later use of its calibrated stream and transfers the old helper identity to two independent addresses. Across all steps the 400 main roles retain both of their charts. The resulting word has 1,288 arbitrary input and output coordinates. Each step matches all forward and transposed coefficients, including the new identity. Removing its pulse or paid leg changes the recovered operator. The replay reports the affected coefficient in both directions. [Ordered birth journal](BIRTHS.json) · [Construction and omission evidence](evidence/construction.json)

| Step | Orientation | Old helper | Paid slot split | Intermediate chart | Paid grades | Productive grades |
| ---: | --- | ---: | ---: | ---: | --- | --- |
| 1 | Adjoint | 283 | 34003 | 288 | 6 → 1 + 5 | 9 → 4 + 5 |
| 2 | Adjoint | 403 | 95914 | 288 | 7 → 2 + 5 | 9 → 4 + 5 |
| 3 | Forward | 876 | 99044 | 117 | 8 → 4 + 4 | 9 → 4 + 5 |

The native SHA-256 is `ff3e57b958967ca37111524c7afdb2f0c59c42047902c1ca025fe14051e09649`. The layout SHA-256 is `efe715def1f12ca4549cf811147a05c58aa21030b7f0b22164ed316d8e934237`. The full caller charges **283,200 paid positions** and credits **52,464 productive targets** at the signed tariff `H(r) = r^(1−κ)`. Its directed signed margin at κ = 0.00387981257853 is **[-0.442216562986687234702576, -0.442216562986687234702575]**. Every surrendered target and every paid subdivision appears in the complete grade histograms. [Independent operator and invoice](evidence/operator.json) · [Canonical graph](WORD.json.gz) · [Canonical layout](LAYOUT.json.gz)

## Bounded ordinary arithmetic

The widest rational literal in this word has 37 bits. A literal with reduced coefficient `a/b` operates on an installed integer component `x`. Exact integrality on the product grid implies `b` divides `x`. The compiler divides by positive factors of at most 24 bits and evaluates the signed numerator in base `2^23` using short constants. Each partial magnitude is bounded by `max(|x|, |ax/b|)`. The implementation uses the original four component streams and W+26 guard. It charges every extra multiplication, exact division, ripple addition, scratch overwrite and retirement. This construction requires every individual denominator factor to fit the short primitive. [Scalar lowering](compiler.py) · [Independent plan, grid and recurrence audit](audit_expanded.py)

The complete ordinary charge is **1,320,738,816 scalar services** and an upper bound of **151,912,932,864 elementary records**. The candidate's least native product grid is `3203382489907091224335482880000`. Both previous words retain their exact original signed and ordinary prices under the shared lowering. A separate check embeds all three on one literal internal integer grid and rechecks ordinary conversion charges and the common depth envelope. The binary service is unchanged. Its independently replayed lower endpoint **0.0038799074072** supports the stated finite point. [Original comparator](evidence/7781.json) · [Immediate comparator](evidence/e40b.json) · [Common grid](evidence/common-grid.json) · [Independent binary qualification](../binary/INDEPENDENT.json)

The conditional application retains the upstream premises for all-column native operation, owned erasure, the finite compiler, the precision tape and analytic recovery. The package checks the actual caller, physical chart adapters, restoration, dirty reinstallation, numerical recurrence and all 54 strict and four functional outer predicates. The machine-selected record at the pinned upstream commit is #7000, κ = 0.00363005817. [Pinned selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json) · [Independent expanded qualification](evidence/audit.json)

## Reproduction

From the repository root, use Python 3.12 and the existing source manifest. The second command accepts each of `construction`, `operator`, `application`, `comparators`, `audit`, `charts-0`, `charts-1` and `charts-2`. Use a separate output directory for each part.

```sh
python3 -IB research/p104-iterated-returns/prepare_sources.py /tmp/p104-sources --fetch
python3 -IB research/p104-iterated-returns/continuation/replay.py --cache /tmp/p104-sources --part application --out /tmp/p104-application
```

Clear1nsight prepared the continued returns and finite arithmetic replay with substantial OpenAI Codex assistance. The source word, checked journals and binary supplier are from #7786 and #7781. The public paid splits, complete P104 caller and compiler machinery follow Ali Romman’s #7776 package. The earlier paid-projection and restored-chain work is credited in #7774. The retained physical, binary and outer framework and its contributors are credited in the package notice. [Attribution and license](../NOTICE) · [Source manifest](../SOURCE-LOCK.json)
