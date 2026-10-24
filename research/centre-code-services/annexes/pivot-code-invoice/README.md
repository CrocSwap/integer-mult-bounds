# Literal pivot-code invoice

This annex preserves the original common-entry pivot code on 112 existing
data fields. It puts sixteen centre sums in sixteen pivots and retains
independent complement data in the other 96 fields. Its exact conjugated
response is -5 on eight pivots, -7 on eight pivots, and identity on the
complement. It uses no new field and does not require a zero input.

The [proof](PROOF.md), [source pins](SOURCES.json), [source credit](NOTICE.md),
and [validation limits](VALIDATION.md) give the complete local scope.
The original [construction](frozen/work/centre-encoding-campaign-20261014/lanes/new-core-transfer-20261017/low-displacement-20261020/pivot-codes/PIVOT-CODES.md) and
[separate moving-code review](frozen/work/centre-encoding-campaign-20261014/lanes/bridge-review-20261017/moving-code-review-20261020/REVIEW.md) remain byte-exact.
This is an addition to the accepted 277-file centre-code-services core.
Its original manifest and files are unchanged; this annex has its own
[manifest](ANNEX-MANIFEST.json) and [core binding](CORE-BINDING.json).

| Word | Old real scalar units | Separate real scans | Explicit translations |
| --- | ---: | --- | ---: |
| C | 2,078 | 16 multiplications by 3 | 0 |
| C inverse | 2,078 | 16 divisions by 3 | 0 |
| Common entry C L, with L=Q squared | 2,078 | 16 multiplications by 3 | 112 |
| Inverse entry L C inverse | 2,078 | 16 divisions by 3 | 112 |

The scalar count is `470+664+944`. It does not include the scans,
address-map costs, descriptor work, or a global precision guard. The
forward stored-prefix row norm is at most 12. The inverse bound is 8,
with at most three new binary fractional bits and one new factor three.
The eight disjoint six-mode blocks do not add eight odd-height levels.

**Valid code images and generic inverse inputs are different contracts.**
On a valid image of C, each division by three is exact on the existing
dyadic grid. A generic inverse has a coefficient 1/12 and needs an admitted
odd grid. A middle operation must preserve the code image to use the first
contract. No arbitrary integer on a finest common grid is declared valid.

The formal transported code `q C q`, where `q=Q inverse`, diagonalizes
the physical response by ordered adjacent cancellation. This identity
does not implement that code at a retired cut. Productive transport,
actual cross-bank phases, source views, helper progress, and raw terminal
decode remain separate. This annex gives no complete kappa improvement
and no automatic applicability to the current selected construction.

## Replay

Use Python 3.11 or later and its standard library, one worker, at least
3 GiB free disk, and a new output directory. No Git, network, original
workspace, or compiler package is needed.

```sh
python3 -I -B research/centre-code-services/annexes/pivot-code-invoice/replay.py --out /tmp/pivot-code-invoice-check
```

Expected final output:

```text
PASS_PIVOT_CODE_INVOICE_ANNEX
```

The runner executes the unchanged producer, the unchanged prior review,
and a small invoice/domain check, each in normal and optimized Python.
Each job uses a private copy. The prior review receipt has absolute input
paths, so only registered source paths are converted for comparison.
All other fields are compared. Compressed programs are compared after
decompression. The producer and invoice receipts match byte for byte.
[REPLAY.json](REPLAY.json) records six passing packaging runs.
No independent human review is claimed.

## Open next questions

- Can a productive caller preserve this code through its actual physical
  operations? A first step is one exact full cross-bank endpoint with
  declared input and output types. The odd phases, source access, and
  helper progress remain blockers.
- Can the output code be removed at a useful complete cost? A first step
  is a literal `Q C inverse Q` decoder at one specified output cut.
  Its phase wrappers, views, and full map prices remain open.
- Can a complete recursive supplier use the local grid bound? A first
  step is its full finite-parent prefix and type invoice. Root conversion,
  all borrowed streams, decoded child entries, and the final dyadic
  endpoint must be proved before the common-grid theorem applies.
