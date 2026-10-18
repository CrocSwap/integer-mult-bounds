# Every integer in the T29 capacity-16 projection is feasible

For the fixed whole-helper inventory and sharp T29 remainder profile of
[PR1160's capacity audit](../t29-capacity-audit/PROOF.md), let `x` count
capacity-16 bins containing the pattern `{9,7}`. The possible values are
**exactly the integers `4824 <= x <= 12992`**. The predecessor proves this
necessary range and gives two realizations, but explicitly leaves the other
values open. This closes that one-dimensional projection; it does not
classify all realizations or produce a physical schedule.

## Fixed problem and necessity

The capacity quotas at capacities `(8,16,32,48)` are
`(19488,12992,12992,12992)`. The whole-helper demands at widths
`(4,5,7,8,9)` are `(20880,8352,14094,31842,56376)`. The exact remainder
profile is `{0:49770,1:4,2:1,48:8689}`. Bin prices use width prices
`(-1,-20,-8,-2,4)` and capacity bonuses `(2,4,8,-13)`.

Independently enumerate all 1,163 legal capacity-tagged multisets and let
`u(r)` be the maximum bin price at remainder `r`. The fixed inventory price
and profile upper price both equal `-112868`; thus every bin of a realization
must be tight. The tight-pattern census forces every width-five helper into
`32:{9,9,9,5}` (8,352 bins). All four rank-one bins and the rank-two bin have
capacity 32 and no sevens or fives. The only tight capacity-16 pattern with
a seven is `{9,7}`; no other capacities except 32 hold sevens, and a tight
capacity-32 bin holds at most two. Therefore only
`12992-8352-4-1=4635` capacity-32 bins can hold sevens, giving
`x >= 14094-2*4635=4824`. The capacity-16 quota gives `x <= 12992`.
The verifier checks these implications from a fresh census rather than
importing the predecessor's pattern table or verification functions.

## Construction, including odd values

Write `x=4824+2t+e`, with `e` equal to 0 or 1. The allowed parameters are
`0 <= t <= 4084`, excluding `(t,e)=(4084,1)`. Use these bin counts:

| Capacity | Whole-helper pattern | Count |
|---:|---|---:|
| 8 | `{8}` | `11202` |
| 8 | `{4,4}` | `8286` |
| 16 | `{9,7}` | `4824+2t+e` |
| 16 | `{8,8}` | `8168-2t-e` |
| 32 | `{9,9,9,5}` | `8352` |
| 32 | `{9,9,9,4}` | `4` |
| 32 | `{9,9,8,4}` | `1` |
| 32 | `{9,9,7,7}` | `4635-t-e` |
| 32 | `{9,8,8,7}` | `e` |
| 32 | `{8,8,8,8}` | `t` |
| 48 | empty | `8689` |
| 48 | `{9,9,9,9,8,4}` | `4303` |

Every count is nonnegative in the stated domain. Each row is legal and
tight. Summing capacities, each width separately, each remainder class and
the signed price gives the required constants, with zero coefficients of
both `t` and `e`. This proves feasibility for every integer in the interval.
The one `{9,8,8,7}` bin supplies the parity adjustment for odd `x`;
interpolating only between endpoint realizations would miss these cases.
At `x=4825`, the variable counts are `4825,8167,4634,1,0` in table order.

## Evidence and reproduction

```sh
python3.12 scripts/research_package.py --package research/t29-capacity-projection-spectrum
python3.12 -I -O -B research/t29-capacity-projection-spectrum/verify.py
```

Both passed. The checker separately builds an affine coefficient ledger
and replays all 8,169 choices with complete capacity, width, remainder, and
price invoices. `CERTIFICATE.json` records the whole-family digest and five
boundary/interior examples. Controls reject values immediately outside the
interval, a boolean masquerading as an integer, and a changed pattern count.
The source pins bind the actual predecessor proof and witness. No
floating-point optimization or solver is used. Source metadata and the
registered Python 3.12 replay also passed.

## Open next questions

This is a side result on a fixed U8 arithmetic family. It does not improve
the selected complex profile or kappa. Owner geometry, chronology, chart
compatibility, controller costs, and a native schedule remain unbuilt and
untested. No all-supplier lower bound or moment uniqueness is claimed.
It would be useful to characterize the joint projection of `x` and the
number of capacity-8 `{4,4}` bins: begin by eliminating the tight-pattern
equations while retaining their integral parity conditions. This describes
packing freedom; physical scheduling still needs a separate construction.

## Credit

Prepared by woklerx with substantial OpenAI Codex assistance; Apache-2.0.
The capacity audit is PR1160 (Hope7Happiness; Claude Fable 5.1 implementation
with separate AI review). Prices and the fixed family are Chafik Boukhalfa's
(PR795/PR890), the all-replica relaxation Jonathan Capalbo's (PR942), the
sharp T29 profile woklerx's (PR992), and the T16 owner lineage Hao Yan's
(PR858). This package contributes the complete projection theorem and its
independent constructive verification. No human peer review is claimed.
