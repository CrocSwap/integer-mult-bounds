# Native cost and asymptotic boundary

This certificate lowers the finite **copy-init scalar** invoice. It does not lower
the current admitted native or hosted invoice and supplies no new κ.

At pinned upstream commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`,
[`invoice_allcold.py`](https://github.com/CrocSwap/integer-mult-bounds/blob/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/gauge44-slots/code/invoice_allcold.py#L149-L152)
charges each scalar event as a macro and uses

```text
compiler = 64 * (m + 1)^3
adapters = 16 * (macro_bound + children + registers + centres) + 64 * m
primitive_bound = max(real_component_primitives) + adapters * compiler
```

The retained selected receipt reports compiler `25934336`, local adapters `387056`
and local primitive bound `10038040553630`. These values are in the pinned archive
member `candidate/strict/global/audit/PREFIX-AND-INVOICE.json`, SHA-256
`212cf4ee3b16081bf66f300fa18b4070d25c17210c21c78c2967892c91870d12`.

All nineteen schedules add 194 SCALE macros per orientation, compared with 54 for
the PR1388 pair. With the other terms unchanged, the generic local adapter allowance
therefore grows by 3,104 over the static background or 2,240 over the pair. No adapter
discount has been proved. The selected native invoice also uses Horner arithmetic
and its own factor-of-two convention; the copy-init saving must not be subtracted
from that invoice without a matching, complete recount.

The original nonscalar event stream, paid histogram, helper inventory and endpoints
are preserved. A role-local complex-linear map commutes with multiplication by
`2^k`, which supports carrying the gauge through such a map. This identity alone
does not establish phase, ownership, input encoding, adapter, controller or whole-call
admission. The selected helpers have no incident COPY/CLEAR or residual adapter,
and their terminal gauges are restored. Full scalar-column replay verifies that
limited endpoint claim.

The recursive histogram stays `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`.
With unchanged recurrence and supplier premises, its paid moment and conditional
cap are unchanged. The scalar result therefore provides no new exponent. We did
not run a native, hosted or all-size frontier experiment for this package.
