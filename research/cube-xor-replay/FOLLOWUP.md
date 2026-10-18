# PR1075 review continuation and current-main compatibility

The review at `d84d3b950127ff9252e5c059a629bb654500192a` stopped the
complete command at 180 seconds after its historical case passed. The unchanged
reviewed head has now completed both differential cases and all 17 tests on
macOS arm64 / CPython 3.12.12, in 118.575 seconds:

```text
PASS_CUBE_XOR_DIFFERENTIAL case=historical
PASS_CUBE_XOR_DIFFERENTIAL case=t6
Ran 17 tests in 1.226s
OK
PASS_CUBE_XOR_VERIFICATION rows=4324 coefficients=8596927616 t6_rank=3088 t6_excluded=false
```

Command: `python3.12 -I -O -B research/cube-xor-replay/verify.py`.
The fresh process had no preexisting bytecode caches. The complete local log
SHA256 is `2673a033caa449e61e7013040d09aa3a84db0ddfb74c83ac6a3239c87954de3d`.
This is execution time for differential verification, not a new benchmark of
the accelerated workload.

The existing [focused Linux CI job](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/38441043779/job/115447388058)
also contains both differential cases, 17 passing tests and the identical final
marker. It used Ubuntu 24.04.5 / CPython 3.12.15 and PR merge ref
`74be1199fb224e0ed24f3a9713e771f976066721`, combining reviewed head
`d84d3b950127ff9252e5c059a629bb654500192a` with then-base
`abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`. This receipt concerns that historical
merge ref; it is separate from CI on the current follow-up head.

## Compatibility delta

Canonical main `ffbd90dd90dbe0055464f3a1411b25a3a4fdc6b8` (priority revision 5)
changes three transitively imported files, causing the original source guard
to reject an integration with current main:

| File | Changed code, outside the cube replay's called path |
| --- | --- |
| `scripts/audit_fused_block.py` | Fraction reuse in `rational_rank` |
| `scripts/exclusion_circuit.py` | Equivalent expected-support masks in circuit verification |
| `scripts/shared_point_circuit.py` | Shared-point circuit construction, support, digest and frame routines |

`COMPATIBILITY.json` binds each original Git blob/SHA256 to the corresponding
current-main Git blob/SHA256. The replay authenticates both manifests and
requires exactly this three-path allowlist before applying the overrides to
an in-memory copy. The original `SOURCES.json` remains byte-for-byte intact.
No core, certificate, fixture, row generation, elimination, cap or rank decision
is overridden. Changes to any effective source, either manifest or the fixture
still fail closed; the existing relocated package controls exercise those cases.

A separate AI-assisted source/profile check observed only import/module and
class definitions from these changed files during the complete historical
differential case and a one-row t=6 probe. Their changed functions/methods were
not called. The full differential command below remains the acceptance check
for the integrated snapshot; the cheap profile does not substitute for it.

```sh
python3.12 -I -O -B research/cube-xor-replay/verify.py
```

The expected domain remains 228 historical rows / 6,993,024 coefficients plus
4,096 t=6 rows / 8,589,934,592 coefficients. Every complete packed row is
compared, including dependent rows. Both complete canonical receipts remain
the fixed oracles; rank equality alone is insufficient.

## Evidence and remaining scope

Current-head receipts and review handoff are linked from
[PR1075](https://github.com/CrocSwap/integer-mult-bounds/pull/1075) and
[the canonical continuation](https://github.com/CrocSwap/integer-mult-bounds/discussions/2884).
Historical `BENCHMARK.json`, `VALIDATION.json`, `CLAIM.json`, `SOURCES.json`
and `EXPECTED-T6.json` are preserved. Their original-head timing and selected
frontier context are historical, not measurements of this refreshed closure.

This follow-up establishes finite tooling equivalence. At t=6 the certified
rank lower bound is still 3,088 and positive deficit is not excluded. There is
no new kappa, exact full-rank result, supplier admission, selected-frontier
change, full multiplication theorem, or formal-kernel proof. No new performance
comparison or full selected cold replay is supplied.

## Open next questions

The loader uses ordinary Python imports after authenticating source. Reproduce
in a fresh process/checkout without `.pyc` files; `-B` prevents writes but does
not disable cache reads or existing `sys.modules`. A separate source-loader
hardening contribution could compile the authenticated bytes and test poisoned
timestamp/unchecked-hash caches. That broader loader contract is outside this
three-file compatibility refresh.

Maintainer incorporation and review-ledger reconciliation remain separate from
these author checks. A useful next action is to inspect the linked complete
current-head receipt and decide the stated tooling scope; this note does not
edit the maintainer's historical disposition.

Original cube family, permutation, rank screen and certificate: Douglas R.
Colkitt. Adapter and follow-up: Ross Richardson with substantial OpenAI Codex
assistance, including a separate AI-assisted mathematical/source audit. No
independent human review is claimed. Apache-2.0; all predecessor notices remain.
