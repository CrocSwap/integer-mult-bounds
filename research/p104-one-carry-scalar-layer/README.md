# One clean carry for the complete selected P104 scalar layer

The selected PR6030 scalar layer can use **one clean carry bit** when each ADD has exclusive temporary write access to its source and each SCALE has paired access to its target's real and imaginary records. Every source and the carry are restored before the next scalar event. No separate dirty bank is needed. This binds existing mechanisms to the current word; it does not claim a new generic adder.

At W=64, the complete bill for one complex component pair is:

| Primitive | PR6506 read-only source | This implementation |
| --- | ---: | ---: |
| Toffoli | 9,402,136 | 4,959,280 |
| CNOT | 9,566,420 | 10,267,972 |
| NOT | 77,220 | 0 |
| Bit reset request | 7,936 | 7,936 |
| Clean carry bits | 63 | 1 |

The total falls by **3,818,524 unweighted logical gates**. CNOTs increase; this is not a claim of improvement under every physical gate tariff. Reset counts are unchanged. For payload dimension D, multiply gate/reset counts by D. Serial execution can reuse the one carry bit; its physical placement remains a cost. Native children, routing, input conversion and reset implementation are excluded, not free.

ADD reuses Nick Petalas's PR3152 wired signed-power circuits and the Cuccaro-Draper-Kutin-Moulton MAJ/UMA method. SCALE uses PR3159's four-shear paired negation. The current integration uses PR6506's direct rotations and removes known zero low bits from the paired negation. These reductions retain the same alignment and strict signed-range premises. COPY uses two component CNOT banks. INIT/CLEAR remain charged reset requests.

All 19,288 scalar events pass a fresh symbolic source-alignment proof for arbitrary coarse-grid native returns. Two complete 22,803-event Gaussian executions agree with rational traces, including 37,715 circuit calls per fixture. Every ADD source and carry return is checked. Seven widths from 26 through 256 have complete gate comparisons. Exhaustive tests cover 98,662 small truth columns, including every actual coefficient, literal inverse circuits and both Gaussian components. The width-64 circuits are serialized and checked in full.

Run `python3.12 -B scripts/research_package.py --package research/p104-one-carry-scalar-layer`. Replay is read-only. `verify.py --write` regenerates the circuit artifact and receipt. ORIGINS.json binds the byte-exact PR6506 comparator to its published head, path, Git blob and SHA256. All other live source files are on the pinned main parent; no pending source checkout or network is needed to replay.

The complete word's recursive paid/target invoice and selected frontier are unchanged. The inherited five assumptions remain. This is a logical scalar construction with an exact bill, not a physical multiplier or new kappa. The full-word fixtures use arbitrary native-grid stubs to test the interface; they do not run the actual native maps. The strict range premise is the separate PR6499 numerical contract.

## Open next questions

Supply actual source/target tapes for a selected ADD and both target component tapes for SCALE. Price every write, control read, carry access and head return. Bind the native return grid and the charged resets to real implementations. Those obligations must precede a full compiler or outer claim.

## Credit

Nick Petalas supplied PR3081, PR3152, PR3159 and PR3241's physical paired-access work. The one-carry `scalars.py` and PR3080 signed-power producer are used unchanged. The adder is due to [Cuccaro, Draper, Kutin and Moulton](https://arxiv.org/abs/quant-ph/0410184). PR6506 supplies the frozen comparator and direct rotation routine; PR6499 supplies the selected grid/range interface. DreamingOfClouds supplied PR6030. Retain David Arias, Cinna Davis, Gareth Davidson, Ali Romman, dcharb78, Jeremy Kothe, Marius-Paul Dumitrean, icekylinx, Tekalign and the full native/compiler lineage. New selected-word composition and verification: Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
