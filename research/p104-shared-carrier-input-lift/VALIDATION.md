# Verification record

Executed on 2026-11-06 with CPython 3.12.14 and the standard library, on a
checkout of the base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Complete scientific replays

| Run | Result | Elapsed seconds |
|---|---|---:|
| Receipt regeneration (`verify.py --write`) | PASS_SHARED_CARRIER_INPUT_LIFT | 281.88 |
| Standalone normal replay | PASS_SHARED_CARRIER_INPUT_LIFT | 272.97 |
| Standalone optimized (`-O`) replay | PASS_SHARED_CARRIER_INPUT_LIFT | 153.78 |
| Registered normal replay | PASS_SHARED_CARRIER_INPUT_LIFT | 297.95 |
| Registered optimized replay | PASS_SHARED_CARRIER_INPUT_LIFT | 172.96 |

The registered command was:

```sh
python3.12 -B scripts/research_package.py --package research/p104-shared-carrier-input-lift
```

It returned `PASS_REGISTERED_RESEARCH_PACKAGE` with outcome `completed`.
Every replay reproduced the committed `RESULT.json` exactly.

## Coverage

The replays rebuild the #6805 word from the #6702 word (payload SHA256
`292b3ab3afb74e87deffd7770e5627e94debd610459221686c05ca04b8885d3f`), apply
`LIFT.json` with every bound source event asserted, and check the result
(payload SHA256 `d3ccfce7bdbca3b79771844e6c9fee48f1a8066444a19218995648df96982821`):
all 801 x 801 endpoint coefficients for arbitrary inputs, all 2,940 used native
maps by signed Pauli action and absolute phase, all 512 columns of each of ten
chart pairs (5,120 columns), every caller contact, the independent field
allocation, and both exact interval engines, strictification, compiler and the
54+4 outer inequalities at conditional kappa 330823/100000000. The raw
crossing from the package is in (0.00330823456614, 0.00330823456615).

Separately written native and invoice audits agree, including the defect
vector before delivery, the unchanged erased values at all 47 owned clears,
and the cumulative histogram deltas against #6702. Negative controls reject a
wrong coefficient at each inserted `ADD`, a missing final repair, aliased
lifted helpers, a stale bound source event, a missing carrier delivery,
wrong phases, malformed ownership data, omitted canonical adapters, aliased
native helpers and an insufficient BIT budget.

## Recomputed bounds

The ordinary bound is recomputed from the literal word: 535,415,008 (old and
new equal). The compiler grid gap is 1/1,750,000,000 (old 1/1,400,000,000).
The public inventory 772, owned labels 29, owned lifetimes 47 and peak 14 are
unchanged; native scalar allowance is 138,352 (old 138,374).

The five inherited framework assumptions remain. Hosted CI, a materialized
full multiplier, formal proof-kernel acceptance, human peer review and
authentication of historical pending-commit ancestry are not claimed.
