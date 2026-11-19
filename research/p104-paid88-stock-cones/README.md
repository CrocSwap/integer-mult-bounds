# Paid slot 88 and linked chart bounds on the four-return P104 word

The six named chronological paid-row pairs fail to replace `95914 → 88` with a rank-seven direct send while preserving the stated observations. A separate directed price check closes the remaining 73 linked two-reversal chart cones. Both findings concern the exact 1,289-coordinate rational word in PR #7786 at `89a67c404226d51028e135de2b9169e9020d57af`. The source’s conditional finite joint lower is `0.00387944011068`. The target remains `0.00387981257853`. [PR #7786](https://github.com/CrocSwap/integer-mult-bounds/pull/7786) · [Canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19749165) · [Frozen source and replay](https://github.com/CrocSwap/integer-mult-bounds/tree/89a67c404226d51028e135de2b9169e9020d57af/research/p104-iterated-returns/continuation)

## Six causal paid-pair exclusions

The proposed collapse replaces `278 → 288 → 127` at paid slots `95914 → 88` with one `278 → 127` send. The two named payloads in each pair may use arbitrary rational linear forms of the stock available at their original slots. Their other paid rules, schedule, chart assignments, 387 exterior terminals and 901 retained receiving arrivals are fixed under this test. All six pairs have proportional additive pulses on these protected observations. The exact replay accounts for the earlier edit reaching the later producer, including an arrival between the two edited sends.

| Earlier and later paid slots | Later increment divided by earlier increment | Later stock rank | Obstruction |
| --- | ---: | ---: | --- |
| 94953, 98148 | −1 | 10 | The attainable earlier increment vanishes on the witness. |
| 95493, 95987 | −1 | 10 | The attainable earlier increment vanishes on the witness. |
| 88919, 95502 | 1 | 6 | The increments cancel on every possible direct sender input. |
| 88952, 95503 | 1 | 6 | The increments cancel on every possible direct sender input. |
| 95982, 98175 | −1 | 10 | The attainable earlier increment vanishes on the witness. |
| 95982, 98182 | −1 | 3 | The attainable earlier increment vanishes on the witness. |

For the input with `x[674] = x[722] = 1` and `x[1288] = −1/845660160`, with all other inputs zero, all ten direct-sender stock forms and all retained receiver arrivals vanish. The original terminal `155442` equals one. Every proposed direct replacement under this contract supplies zero at that terminal on this input. The replay also constructs compatible nonzero paid recodings for `88919/95502` and `88952/95503`. They retain all 1,288 protected observations and still lose terminal `155442` after the collapse. [Exact argument](STOCK.md) · [Stock receipt](STOCK.json)

## Linked two-reversal cones

The independently replayed nomination procedure generates 934 linked chart pairs. Necessary forward and backward closure or a strict orientation cycle excludes 795, leaving 139 price certificates. The replay checks all 66 inherited price certificates again. The 73 newly priced cones close with 17 exact integer-flow bounds and 56 integer potentials applied to the new chart domains. The zero-reversal control contains the source and a perturbed flow certificate is rejected.

The most favorable new directed upper is `−11.8737978602670848678835793786636822` signed units across the 48 rational calls, at linked index 81 and paid slots `94730/99158`. The enrolled target requires a saving of at least `0.379442169416081001142560448506083557440402716` units. Both reversals, the 400 physical main chart pairs and all 889 independent helper directions are constrained in this cone test. The 66 earlier cases and 73 new cases exhaust the saved linked roster under its stated nomination and geometry rules. A change outside those rules needs a new test. [Price and coverage receipt](cones/VERIFIED.json) · [Source and tariff](cones/SOURCE.json)

The replay uses a directed rational enclosure of the paid and productive tariffs, the signed native histogram and the published application invoice. Each certificate gives a lower bound on the new cost inside a necessary relaxation and an upper bound on savings. The stock witness is a direct exact obstruction for a different set of allowed edits. This package supplies no new native word or finite κ certification. The 36-call binary service, dirty physical caller, ordinary compiler, finite stock and outer assumptions remain obligations of a future construction.

## Reproduce

From this package directory, use standard-library CPython 3.12.

```sh
python3.12 -IB verify_stock.py --emit-result > replayed-stock.json
cmp STOCK.json replayed-stock.json
python3.12 -IB cones/portable.py
```

The stock replay used about 8 CPU seconds and 90 MiB of resident memory. The cone proof used about 105 CPU seconds and 300 MiB. Both read the packaged archive and work without Git or network access. The cone check compares all reproducible receipt fields and excludes the recorded CPU time from that comparison. The package pins the external #7786 source separately from its canonical main parent. Reproduce its original Git provenance by fetching the #7786 head and checking the source paths, compressed bytes and hashes. [Archive pins](ARCHIVE-SOURCES.json)

From the repository root, the registered commands are available with the pinned catalogue present.

```sh
python3.12 -IB scripts/research_package.py --package research/p104-paid88-stock-cones --check-only
python3.12 -IB scripts/research_package.py --package research/p104-paid88-stock-cones
```

## Open next questions

Can a repair change receiver 127's retained observations or its source stock while still fitting the complete signed target budget? The smallest first step is to name a specific additional live observation and its producing chart, then test whether it is nonzero on the three-coordinate witness. The previously allowed ten direct-sender forms and 901 retained receiver forms vanish on that input. A surviving observation must be priced together with every restored owner, changed paid operation, and ordinary and outer obligation.

## Credit

Clear1nsight prepared the result with substantial OpenAI Codex assistance. The earlier #7786 continuation and #7781 supply the exact word and caller succession. Ali Romman's #7776 supplies the signed P104 framework, and #7774 supplies the restored-chain work. Source-specific attribution, the earlier cone work and the inherited directed tariff are recorded in [NOTICE](NOTICE).
