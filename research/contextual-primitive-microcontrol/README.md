# Lower the primitive wrapper and protected contexts to finite tape control

**Result:** the actual retained `Controller.primitive` operation has an
explicit finite-state implementation on the same fixed tapes and physical
alphabet. The construction includes dirty-work retirement before entry,
raw readonly binary contexts, source table execution, all successful head
returns and success-only final work retirement. It preserves the source's
partial failures and exact active trace, with serialized TM clock **C=A+U**
for the entire wrapper. **No new kappa or global assumption discharge.**

PR #6999 explicitly excluded contexts and the wrapper. This package reuses
its unchanged coded-port microcontrol and supplies the missing entry/return
composition. It does not re-prove its no-context result. Canonical source
base: [`e5452351`](https://github.com/CrocSwap/integer-mult-bounds/commit/e54523517d0f03e58352e647c403a5af3e525a57).
The selected `.00363005817` result and all five assumptions are unchanged.

The target contains no runtime source-row lookup, host arithmetic, dynamic
port selection or additional work tape. For `N` table rows, `L` participating
ports and `K` work ports, its state count is at most
`52N+3L+18K+9`. The positive finite precompilation and installation bill is
separate. A fixed caller can substitute this entry graph for the source
primitive under its stated alias, origin and provider conditions.

The old-work cost is explicit. Retiring a physical binary body of length
`B` from head `h` costs exactly `2h+5B+7` raw actions. If the post-table
work lengths are `B'_i`, the successful wrapper bill is

`C = U + A_table + sum_i(2h_i+5B_i+5B'_i+14)`.

`A_table` includes actual header reads and all table-final origins. Old
larger dirty bodies, displaced entry heads and even unused context-head returns
are not omitted. No physical-to-pass-tariff exchange rate is inferred.
Already blank historical allocated tails remain a separate storage
obligation; `B` counts the currently nonblank body, not that whole capacity.

## Reproduction

```sh
python3 -I -B research/contextual-primitive-microcontrol/verify.py
python3 -I -O -B research/contextual-primitive-microcontrol/verify.py
python3 -B scripts/research_package.py --package research/contextual-primitive-microcontrol
```

Expected `PASS_CONTEXTUAL_PRIMITIVE_MICROCONTROL 28 372 6`, followed by the
registered-package pass when using that wrapper. Standard library only.
The standalone commands require no Git, network, package installation or
external scientific input. Six retained files are authenticated locally.

The unchanged source oracle and emitted graph agree on 28 protocol cases,
372 exact/rounded SCALE cases and 660 independent retirement equations.
Six graph mutations and five invalid layouts are rejected. Arithmetic
cases exercise real source-generated tables from #6968 and #6988 with
dirty work, permuted global tape roles and borrowed raw contexts. Those
tables do not inspect context values; a separate descriptor scan exercises
the read-dependent context protocol and is labelled as a control.

`PROOF.md` contains the all-width bisimulation, precise domain, failure
semantics, setup and backing statements. `evidence/RESULT.json` records
the executed domain and checks. No complete selected native word or
multiplier is replayed here.

A separate lead review and target-only interpreter are recorded in
`LEAD-REVIEW.md` and `evidence/lead_verify.py` (38 hand-derived probes).

## Open next questions

1. Lower the actual recursive return/row-service boundary and connect it
   to this primitive entry without additional dynamic host state. Begin
   with one pinned continuation operation and its exact tape interface;
   source/header preparation, ownership and its complete bill remain.
2. Bind the complete selected event registry to actual providers and
   production headers. The first step is one fixed event family with its
   actual geometry/precision descriptor and return contract. This theorem
   transports such a contract; it does not manufacture it.
3. Convert the fully counted machine clock into one consistent physical
   volume and ordinary tariff. Include setup, source access, historic
   backing and caller ancestors. `C=A+U` alone is not that conversion.

## Credit

Prepared for **@CubeJerry** with substantial **OpenAI assistance**.
Credit the original lifecycle executor, exact scalar tables (#6968),
rounded scalar tables (#6988), and scalar microcontrol (#6999). Existing
source notices remain unchanged. The classical finite-state composition
principle is credited as general background; the contribution is its
concrete source-bound wrapper/context implementation and full local bill.
