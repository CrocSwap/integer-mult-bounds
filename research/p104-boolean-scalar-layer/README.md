# A literal Boolean scalar layer for selected P104

The complete PR6030 word now has a source-bound scalar bit layer. Every ADD uses Nick Petalas's unchanged PR3080 reversible circuit. New SCALE circuits use in-place rotations, sign fill and a specialized constant increment. COPY uses CNOTs into the declared zero destination. INIT and CLEAR are explicit, charged reset requests; their physical implementation is not supplied.

At **64 bits per real component**, one complete word costs:

| Operation | Count |
| --- | ---: |
| Toffoli | 4,701,068 |
| CNOT | 4,783,210 |
| NOT | 38,610 |
| Bit reset request | 3,968 |
| Shared clean carry bits | 63 |
| Constant backing bits | 0 |

These counts include every scalar occurrence, all 31 INIT/CLEAR pairs and complete carry cleanup. They exclude native calls, tape movement, initial/final conversion and physical reset realization. For complex payload dimension D, multiply the scalar gate and reset counts by 2D. The one carry bank can be reused serially across fields and components; its placement and access are not free. No runtime, kappa or selected-frontier gain is claimed.

The selected signed-power ADD policy saves 672 Toffolis and 674 CNOTs at width 64 against the explicitly constructed binary-power control. Both are local compiler policies; the binary control is not asserted to be an upstream physical backend or an optimum. The complete implementation and its bill are the contribution, not those small control savings.

All 19,288 scalar source events pass an exact symbolic alignment check when each public entrance and native return is a multiple of 32 fine-grid units. Each native return is a fresh atom, so this covers arbitrary values on that grid. [PR6499](https://github.com/CrocSwap/integer-mult-bounds/pull/6499) gives the separate numerical contract under which W=p+16 bits have sufficient signed range. Its native error, COPY and reset premises remain explicit. This package checks alignment itself; it does not import PR6499 code or silently admit its native premise.

The circuits work for 26<=W<=256, the tested compiler's declared width range. Seven widths include powers of two, odd widths and widths divisible by three. Two complete 22,803-event executions at W=26 and W=64 match rational traces after every event. All shared carries return to zero. Seven-width template cases and 715 independent bit-list SCALE cases also pass. CIRCUITS64.json.gz stores every actual width-64 template, and the verifier compares its complete contents.

Run `python3.12 -B scripts/research_package.py --package research/p104-boolean-scalar-layer`. Replay is read-only. Only `verify.py --write` regenerates the circuit artifact and receipt. The full-word fixtures use arbitrary native-grid stubs to test the scalar interface; they do not execute the physical native maps. PROOF.md gives the arithmetic and cleanup arguments.

## Open next questions

Place the shared carry bank in an actual physical owner layout. Bind the source and target controls, including sign extension, to paid tape accesses. Implement the declared native return and reset interfaces. Then include this scalar bill in the complete caller cost. The five framework assumptions and the supplier's paid/target profiles remain unchanged.

## Credit

Nick Petalas / PR3080 supplied `rank7-aligned-bit-adders/bitadder.py`, including source preservation, signed-power expansion and clean carry return. That file is unchanged and pinned to main. PR6499 supplied the selected-word grid/range interface. DreamingOfClouds supplied PR6030. Retain David Arias, Cinna Davis, Gareth Davidson, Ali Romman, dcharb78, Jeremy Kothe, Marius-Paul Dumitrean, icekylinx, Tekalign and the full scalar/native/compiler lineage. Rotation, two's-complement negation and constant specialization are classical. New selected-word lowering, complete binding and checks by Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
