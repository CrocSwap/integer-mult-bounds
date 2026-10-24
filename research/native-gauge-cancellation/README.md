# Remove 60 native maps after the final Cao scalar compressor

This exact circuit change removes **60 native-map records and 42 more scalar
ADD records per native call**, after the 151-ADD reduction in
[PR #5350](https://github.com/CrocSwap/integer-mult-bounds/pull/5350).
The new scalar allowance saving is 236 per call. The total reduction from
Cao Yifan's final PR4610 word is 193 scalar records, 60 native maps, and 1452
scalar allowance units per call. The native-map count falls from 240 to 180.
These are circuit counts, not measured running times.

**Kappa does not change. This is not the requested bottleneck breakthrough.**
The complete paid Gaussian profile and all 408 productive helper boundaries
are unchanged. Thus the complete recursive moment is identical for every
exponent. The selected conditional kappa at the base is 0.0030217758. The
binding main-transform cost is unchanged. No selected record is edited.

| Orientation | PR4610 scalar allowance | PR5350 allowance | New allowance |
| --- | ---: | ---: | ---: |
| Forward | 158120 | 156904 | 156668 |
| Backward | 158168 | 156952 | 156716 |

The new pass tracks each field's scalar factor and formal native-map word.
It combines exact equal ADD operators across commuting instructions. It then
removes native maps that have become an unused inverse pair. It preserves
noncommuting dependencies and reset barriers. [PROOF.md](PROOF.md) states the
algebra and the physical-frame argument. [RESULT.json](RESULT.json) gives the
source-event patch, generated word hashes, both native receipts, complete
local invoices, and failure controls.

The base is canonical main `1ec1119972c9aefe42525172d07b332fcff81cb4`.
[SOURCES.json](SOURCES.json) pins all ten consumed files by SHA256 and Git
blob. The original native payload has decompressed SHA256
`cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd`.
The source constructor, archives, receipts and selected supplier are not edited.

## Verification

Use Python 3.12 and the standard library. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/native-gauge-cancellation
```

The scientific command ends with:

```text
PASS_NATIVE_GAUGE_CANCELLATION_NO_KAPPA_CHANGE
```

The verifier rebuilds both orientations. Two retained source interpreters
check all 632 arbitrary persistent columns, arbitrary owned entry state,
exact scalar frames, native-map words, and zero return of the owned field.
Every paid record from PR5350 is retained. Every original role/frame/rank
transition is retained. The complete paid profile remains
`{1:2201,2:412,3:510,4:127,5:40,8:8}` with 3298 jobs and rank mass 5327.
The formal prefix bounds remain 457 forward and 169 backward.

Exact dense controls check source writes, target reads, scalar-weight changes
and resets. A distinct native-map word cannot be cancelled. Both native
interpreters reject a changed scalar sign in the actual emitted word.
The default replay compares the deterministic receipt without writing it;
`--write` is the explicit receipt-generation command.

[VALIDATION.md](VALIDATION.md) records executed checks. No new phase recipe is
needed: the paid records are unchanged and each retained warp is an original
frame-bound warp. Their existing absolute-phase lowering is reused, not
rerun. No complete controller, compiler, BIT, outer-ledger, cold-supplier,
formal-kernel or end-to-end integer-multiplication replay is claimed. Native
all-column, ownership, uniform compiler, precision/tape and analytic-recovery
assumptions remain inherited. Independent human review remains open.

## Open next questions

This result does not justify another search with the same recursive bill.
A kappa claim needs a changed paid or productive profile and full admission.
The present package makes no claim about the best possible scalar circuit.

## Credit

Cao Yifan supplies the final native word in
[PR #4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610).
Cinna Davis supplies the commuting and triangle rewrites in
[PR #4692](https://github.com/CrocSwap/integer-mult-bounds/pull/4692).
ahrazzle supplies their paid-profile-safe final-word composition in
[PR #5350](https://github.com/CrocSwap/integer-mult-bounds/pull/5350).
Chrisbryan17 supplies the earlier bounded inverse-pair check in
[PR #5265](https://github.com/CrocSwap/integer-mult-bounds/pull/5265).
This package imports the prior constructor and both retained interpreters;
they are not new independent implementations. It adds scalar/native-map
normalization and the resulting cancellations.

Credit Cinna Davis's controller/helper lineage, Dugongue's native maps, zxv,
Jacob Alan Sussman, and all retained scalar, Clifford, geometry, compiler,
precision and analytic authors. Source notices remain unchanged. New work by
Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
