# Concrete private-buffer integration for FOUR428

Prepared for Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
Apache-2.0; retains the notices and compiler/accounting lineage of PR2269,
PR1297, PR558, PR552 and PR531. Repository base:
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`; source PR2269:
`b479fc5567bc09ab9185bffe89b62594f36d74e5`.

The FOUR428 provider uses 652 live native streams and 76 simultaneous private
zero fields. `GLOBAL-BUFFER-BINDING.json.gz` contains every actual owner map for
all 666 invocations and four lowered provider/orientation programs. Each native
zero allocation and release has an explicit complex CLEAR, charged as two real
component primitives. The original native programs remain unchanged.

The private family intervals are disjoint, half-open ranges:

| Purpose | Families |
|---|---:|
| Live data and owner families | [0, 66304) |
| Private centers | [66304, 66312) |
| Reserved tableau | [66312, 66740) |
| Coefficient work | [66740, 66742) |
| Private zero fields | [66742, 66818) |

`runtime-overlay/code/emit_allcold.py` requires
`--buffer-binding candidate/GLOBAL-BUFFER-BINDING.json.gz`. It embeds the binding
in the actual global template, copies its bytes into hosted output and records
the file digest. The template's provider dispatch invokes
`buffer_runtime.iter_call_events(template, call)`. That entry point resolves
all remaining local L operands through the literal owner map; center and zero
operands already name physical F families. Event coefficients, frames and order
are retained. It covers scalar gates, warps, adapters and recursive children.

The checker reverses each lowered event to the exact native event and checks
allocation/CLEAR/use/CLEAR/release lifetimes. It requires every complete call's
provider, orientation, time, owner families and routes to equal the emitted
global controller. The inherited audit checks its original chronology, busy
windows, owner injectivity, residual/spectator charts and paid profile **before**
checking this additional binding. Thus its original mutation controls continue
to exercise the inherited geometric predicates. Six separate buffer controls
remove either CLEAR, alias fields, bypass dispatch, alter a call family or
corrupt the lowered-program digest.

The invoice first checks native scalar counts against the original local
receipts, then adds 152 complex CLEAR macros / 304 real primitives per call.
For each provider it charges

```
charged_macros = native_macros + 152
charged_real = native_real + 304
adapters = 16 * (max(charged_macros) + 112 + children + 652 + 76 + 8) + 64 * 73
```

Here 112 is the actual warp-event count per orientation. The nonlocal routing
inventory also adds `2 * 666 * 76` field bindings. Physical stock is 66,818;
recursive live stock remains 66,304. The parent reserve envelope and inherited
compiler constants remain unchanged. Both allocation and release clear a field
already justified as zero by the bound native restoration receipt; this layer
does not erase arbitrary dirty helper input.

Focused reproducible checks, from the repository root:

```sh
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/global-admission/check_buffer_binding.py
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/global-admission/check_runtime_buffer.py
python3 -B research/complex-structure-seed39/nonzero-lender-evidence/global-admission/check_private_buffers.py --out research/complex-structure-seed39/nonzero-lender-evidence/global-admission/PRIVATE-BUFFER-INVOICE.json --controls
```

Expected statuses respectively:
`PASS_INDEPENDENT_666_CALL_PRIVATE_BINDING_AND_EXACT_INVERSE_LOWERING`,
`PASS_RUNTIME_BUFFER_ADMISSION_AND_ALL_FOUR_DISPATCH_TEMPLATES`, and
`PASS_EXPLICIT_76_PRIVATE_ZERO_BUFFER_ARENA_AND_FINITE_OVERCHARGE`.
The focused runtime test constructs only the buffer-consumed metadata and
executes all four dispatch templates; the full runtime replay separately
verifies the inherited global controller, invoice, assembly and outer transfer.
The buffer tests alone are not an outer-bound certificate or a formal proof of
the all-size theorem. Exact all-column native endpoint algebra, uniform
compilation, precision/tape, hosting and analytic transfer remain the stated
inherited obligations. File hashes in the generated receipts bind these finite
checks to their actual source and data artifacts.
