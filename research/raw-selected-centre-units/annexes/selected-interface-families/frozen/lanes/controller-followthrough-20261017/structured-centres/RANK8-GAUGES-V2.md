# Put the dyadic scale on the query field

These four scalar programs implement exactly the common-frame gauges
from `RANK8-GAUGES.json`. They keep its one-field storage contract and
restore `C0` by subtraction of the updated query. They do not clear a
data-dependent owned value.

After the query is formed, scale `C0` by the common positive magnitude
of the scatter coefficients. Then use signed unit ADDs for the scatter.
Before the query is removed, scale `C0` so that it equals the updated
query. This replaces many half or quarter ADDs by two scales of one
owned field.

| Gauge | First query scale | Scale before removal | Real scalar primitives |
| --- | ---: | ---: | ---: |
| `A` | `1/4` | `4` | 2,368 |
| `A^-1` | `1/4` | `4` | 2,368 |
| `H` | `1/2` | `-4` | 1,172 |
| `H^-1` | `1/4` | `-2` | 1,172 |

All four programs have zero native children. The checker compares all
112 input columns with the preceding pinned words. It also checks both
inverse orders and restoration of `C0` to zero.

Run from the workspace root:

```text
python3 work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/structured-centres/check_rank8_gauges_v2.py
python3 -O work/centre-encoding-campaign-20261014/lanes/controller-followthrough-20261017/structured-centres/check_rank8_gauges_v2.py
```

Both commands must print `PASS_SCALED_QUERY_RANK8_GAUGES` and give
byte-identical receipts. `GAUGES-V2-FREEZE.json` pins this separate
version. The preceding frozen source files are unchanged.

The new-core-transfer lane supplied this scale placement. This packet
checks and prices the exact words. It is AI-assisted research. The
common physical frame remains a premise; this change does not supply a
mixed-frame decoder or a complete supplier.
