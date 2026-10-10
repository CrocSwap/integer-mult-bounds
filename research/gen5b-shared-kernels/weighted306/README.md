# Shared156 composition with pinned PR306 reordering

This additive verifier checks the published 156-pivot shared-donor construction on
PR306 at `0314371983b8837f01723f5af2c70217f75b01cc`. It reproduces the declared
baseline and the combined exact conditional arithmetic:

| Fixed case | κ | Literal stock | Priced calls | Rank mass |
|---|---:|---:|---:|---:|
| Pinned PR306 | 0.000751458925311258 | 1,229,665 | 482,030 | 2,454,930 |
| PR306 + shared156 | **0.000751478472895775** | **1,229,275** | **483,015** | **2,454,150** |

The relative increase over that pinned baseline is about **0.00260128%**. This is
a historical, immutable comparison, with no current-best or optimality claim.
The old `weighted305/`, `weighted275/`, and original evidence remain unchanged.

## Exact verification boundary

The new checker verifies preservation of PR306's two reorder stages under the
shared156 change. **PR306's raw crossed-interval and full-word admission remain
inherited. Its 239 original raw crossings are not independently regenerated or
replayed here.** The aggregate reports that boundary explicitly.

All 353 selected paths are checked; 18 acquire a legal later rank22 visit.
The 156 relations, 197 donors, first frames, endpoints and role-bank inventory
are unchanged. A conservative raw-prefix bound, 656881, precedes every moved
interval (minimum 690991). All new/deleted scalar gates lie outside those
intervals. Exact signed and unsigned commutation therefore transports the
inherited admission and the established conservative scalar bounds.

F = 438151 and B = 14104135 give payload
`1070888631470889114458162912766400` (110 bits). **The old104 comparison is false;
the explicit112 bound passes.** The payload-cap justification is retained from
the immutable `weighted305/` evidence. It is not an odd-prime address budget.

All 281 changed chart inverse programs and 706 role uses are rebound and replayed.
The full prior role-bank certificate is hash-bound, with 925440 assignments per
stage over five stages, unchanged dimensions and stock. The displayed finite
coefficient is `90417469526202901` (<2^80). Three exact bootstrap checks, adjacent
moment-grid rejection and all 47 displayed assembly inequalities pass. The
unknown full primitive/compiler constant is not numerically instantiated.

The unchanged physical decoder, baseline source-span and chronological
admission, compiler, chart, cover, routing, restored-row, prime/recovery,
complex-supplier and analytic all-size interfaces remain conditional.
See [PROOF.md](PROOF.md) and [NORM_TRANSPORT.md](NORM_TRANSPORT.md).

## Reproduce without running upstream programs

Python 3.11+ and its standard library suffice. Use a checkout containing this
addon and its unchanged sibling packages. Main alone need not contain the
unmerged upstream PR306 inputs. `inputs.json` gives immutable download URLs,
Git blob IDs, SHA256 values and byte lengths for the13 new inputs.
The inherited39 inputs retain `../weighted305/inputs.json`; they are not copied
into this diff. Downloaded Python files have `.txt` names and are inspected only
as text/AST, never imported or executed.

From any working directory, set absolute paths:

```sh
P=/absolute/checkout/research/gen5b-shared-kernels
D=/absolute/external-data
O=/absolute/fresh-output
python3 -B "$P/weighted305/acquire_inputs.py" --output "$D/pr305"
python3 -B "$P/weighted306/acquire_inputs.py" --output "$D/pr306"
python3 -B "$P/weighted306/verify306.py" --check \
  --prior-inputs "$D/pr305" --inputs "$D/pr306" --output "$O"
PR305_INPUTS="$D/pr305" PR306_INPUTS="$D/pr306" \
PR305_OUTPUTS="$O/tests/prior156" PR306_OUTPUTS="$O/tests" \
  python3 -B -m unittest discover -s "$P/weighted306" -p 'test_*.py' -v
```

Assertions must remain enabled; do not use `-O`. Outputs stay outside the
checkout. The focused suite shares one aggregate fixture and does not run the
unrelated historical70/166 suites. The five compact frozen receipts are
compared exactly; only the generated wall-clock field is excluded. Full selected
paths and factor programs are freshly generated rather than duplicated here.
All reused source files and prior receipts are hash-bound by `DEPENDENCIES.json`.
