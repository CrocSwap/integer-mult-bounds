# Which P104 precision contract is established?

This navigation map summarizes the cited contracts. It does not independently
validate every row; consult the [review ledger](pr-ledger.json) for exact-head
review and archival status.

Use this map before reopening a P104 precision handoff. The retained packages
cover different words, entrances and numerical implementations. In particular,
**seven extra fractional bits at one layer is an exact-grid statement; it is
not a seven-bit relative-error guarantee or a paid recursive implementation.**
The [lifetime scope map](p104-helper-lifetime-scope-map.md) covers a separate
set of information and transport bounds. Resolve the selected construction
through [the selected record](../../certificates/selected-result.json).

## Entrances, words and guarantees

Here `f` is the initial physical fractional width and `lambda >= 1` is payload
tensor depth. Whole-word grid statements assume arbitrary public components
in `2^-f Z[i]`, including dirty helpers. At depth `lambda`, chart/native maps
are tensor-powered while scalar ADD coefficients stay unchanged. The collector
rows instead assume a grid at the **collector entrance**, after its producer.

| Evidence | Exact object and entrance | Established numerical contract | Boundary still to check |
| --- | --- | --- | --- |
| [PR2674: atomic grid](../../research/p104-physical-dual-grid/README.md) | PR2586's unchanged 5,398-event physical dual | `max(10 lambda,9 lambda+2)` extra fractional bits suffice at atomic instruction boundaries; eleven at one layer | Does not cover arithmetic inside a native child |
| [PR2730: completed collector](../../research/p104-mixed-grid-collector/README.md) | First collector, five dirty sources and dirty query already on `h Z[i]` in their physical charts | Completed outbound `U` needs `h/16`; correlated return `VU S=S` permits return on `h` and exact private cleanup | Does not establish this entrance grid from the original caller, or quantized internal prefixes |
| [PR2754: internal collector](../../research/p104-internal-grid-collector/README.md) | The same two rank-seven recipes and coarse-grid entrance | Four extra fractional bits suffice throughout the native prefixes and are necessary for its fixed uniform implementation | Local collector result, not a whole-word producer or recursive price |
| [PR2772: whole-word internal grid](../../research/p104-whole-word-internal-grid/README.md) | All 5,398 PR2586 events, native prefixes and eight private erasures | `max(14 lambda,13 lambda+2)` extra bits suffice; fifteen at one layer | Sufficient, not minimum; native correctness and tensor lifting remain inherited |
| [Joint divisibility successor](../../research/p104-joint-prefix-grid/README.md) | The same unchanged word, accounting for relative chart/native factors together | `ceil(15 lambda/2)+2` extra bits suffice; ten at one layer | Sufficient, not minimum; its next task is a paid recursive representation |
| [Ross Richardson's sharp-grid finding][sharp] | The same unchanged PR2586 word | Reported sharp uniform guard `ceil(9 lambda/2)+2`; seven at one layer | Public Discussion proof/archive, not a locally replayed `research/p104-clifford-grid` package in this checkout |
| [PR2813: changed-word binding](../../research/p104-retimed-internal-grid/README.md) | PR2725's actual 5,268-event ADD-retimed word and its new recipes | The same sharp `ceil(9 lambda/2)+2` guard, including scalar products, internal prefixes and eight exact erasures | This is a separate source binding, not transfer from a matching rank profile or from PR2712 |
| [PR2878: completed errors and recovery](../../research/p104-retimed-error-recovery/README.md) | PR2725, assuming completed relative Hilbert defects for **all** ADDs/transports and the ideal output lattice | `E <= 5534*u*B/(1-(6047/4)*u)` for `(6047/4)*u<1`; strict nearest-grid thresholds recover private zeros and public outputs | Needs actual implementations meeting every completed-operation allowance and a priced recovery scan |
| [PR2891: rounded reference](../../research/p104-rounded-native-child/README.md) | Only PR2725's X90/N90 rank-seven/eight calls, events 4642/4643; arbitrary dyadic inputs | Explicit per-stage rounding and exact wrappers give `norm_2(computed-Ux) <= 2^-b norm_2(x)`, retaining the chosen working grid | Scalar expansion, not a fast recursive child; other transports, ADDs and whole-word recovery remain unbound |

PR2772 and PR2813 have local maintainer reviews in the
[seventeenth review](community-efficient1700-review.md). PR2878 and PR2891
are retained in the [nineteenth review](community-efficient1900-review.md).
Follow those reviews and exact sources; a Discussion finding or archive merge
alone does not establish supplier admission.

## Three implications that must not be skipped

**An entrance grid is part of the contract.** The local collector's four-bit
result is relative to its actual `h`-grid physical entrance. It cannot be
substituted for the whole-word seven-bit guard relative to the original public
inputs. Their values measure different things. Nor can the coarse return be
applied to an arbitrary fine-grid array: it uses the correlated input `US`.

**Exact grids and approximate recovery are distinct routes.** PR2813 proves
that the ideal computation, including internal divisions, can run exactly on
one fine grid. PR2878 permits errors under its completed-operation assumptions.
Its `E` and `B` use the maximum of individual register Hilbert norms, not an
addresswise maximum norm. If `F=f+ceil(9 lambda/2)+2` and `B<=2^h`, its sufficient
thresholds are `u<=2^(-F-h-9)` for private-only recovery and
`u<=2^(-F-h-14)` for all-public-output recovery. These thresholds do not
construct rounded children or pay for scanning and rounding.

**The reference must return its declared grid.** PR2891 chooses a working
fractional width from the actual input scale and requested relative accuracy.
Its final downcast to the entrance grid has a failing fixture. It covers two
specific recipes, not the other 1,938 transports or scalar ADDs; consequently
it does not instantiate PR2878 on the whole word. A relative-error bound also
does not by itself prove exact dirty cleanup. See the
[canonical precision thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750)
for current follow-ups before assigning that question again.

The sharp witness is another source-binding check. On `Y2=2^-f delta_0` with
other public inputs zero, D18 reaches
`-2^-f (1/4) ((1-i)/32)^lambda`. In the unchanged word the transport is
zero-based event **2142**, or cut **2143** (after 2,143 events). PR2813 rebinds
it to zero-based event **2040** in the retimed word. Reusing either event number
on the other word would miss the intended instruction.

## Reproduce the actionable entry points

From the repository root, Python 3.12 or later and the standard library:

```sh
python3 -I -B research/p104-internal-grid-collector/verify.py
python3 -I -B research/p104-retimed-internal-grid/verify.py
python3 -I -B research/p104-retimed-internal-grid/independent.py
python3 -I -B research/p104-retimed-error-recovery/verify.py
python3 -I -B research/p104-rounded-native-child/verify.py
```

These direct checks are read-only. Expected markers respectively start
`PASS_P104_INTERNAL_GRID_COLLECTOR`, `PASS_P104_RETIMED_INTERNAL_GRID`,
`PASS_P104_RETIMED_INTEGER_ORACLE`, `PASS_P104_RETIMED_ERROR_RECOVERY` and
`PASS_P104_ROUNDED_NATIVE_CHILD`. Each primary replay includes its declared
failure controls. The retimed grid replay executes two full one-layer fixtures;
the separate scalar oracle checks all 30,007 pre-add products. All-depth
statements use the written arguments, not extrapolation from those fixtures.
Use each package's `VERIFY.json` for its additional registered checks.

Ross Richardson's original sharp-grid ZIP is linked in [the public finding][sharp]
and its text is retained in
[PR2813's source inputs](../../research/p104-retimed-internal-grid/inputs/DISCUSSION-2750-SHARP.md).
Its advertised `research/p104-clifford-grid/verify.py` path is not available
directly from this checkout. The commands above replay the retained **retimed**
binding; they do not claim execution of that original archive.

## Open next questions

Bind an admitted fast recursive child to a complete viable consumer: specify
its input scale, retained output grid, scratch, restoration, bit operations,
accesses and movement. First test one actual invocation against its complete
allowance. For full approximate recovery, also bind the remaining transports
and scalar ADDs. The current
[fixed-consumer objections](../../research/p104-consumer-budget-audit/README.md)
remain relevant; exact-format improvements alone do not remove them. This map
does not propose another format search or dependent construction round.

## Source pins, scope and credit

Navigation audit on main `b3f3ee0392b71b118fd086a6eaf6b4cab54ef455`, priority
revision 5. Draw nonce `7ebcd183906eb1e731c7410218adc26b`, complex mechanisms;
scope **changed** from decoder synthesis to this contract map after live overlap
found the apparent missing precision tasks already covered. No new mathematical
bound, paid profile, supplier, selected-frontier change or all-size theorem.
Before submission, canonical main advanced to
`836b19bfa309ceafbc8ee32a15e8c4b10dde7e11` (priority revision 6).
The updated handoffs retain the distinction
between local precision and a complete paid implementation. The selected record
and consumed numerical packages were unchanged; this documentation was rebased
onto that checkpoint without another task draw.
The five direct commands above passed on Windows AMD64, CPython 3.14.6,
including their built-in failure controls. This navigation pass did not run
the additional package suites, original sharp-grid ZIP, native compiler,
selected cold replay, Lean or hosted CI.
Coordination: [scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18977831).

Exact predecessor heads: PR2586 `7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`;
PR2674 `aeb5551b162b78e33c0b42681abaff92eb608d70`;
PR2730 `99a81c88d095bbde548d3e67cdb986009cb3e99e`;
PR2754 `23d8aa7f11cd6a2e9d44a6ce4f6beebe1016492c`;
PR2772 `69ba5a423246a1c9281bdd5c1f51240b454f2aa6`;
PR2725 `71d24b655c2fdddc063b9aaf285e8425ce197499`;
PR2813 `bfd6b68d1cd01913c7619f6b4115da8e584286f5`;
PR2878 `d4870b711a8a0967df8ce2c089d978d10c3103d1`;
PR2891 `cfe7c810eb6a3461b7e9c737fd948fb991b6dd6a`.
The joint-divisibility source is retained at main commit
`6d10a887a902d00a29868b39f575c57e446d7c98`.
Package source manifests retain byte hashes and detailed ancestry.

Credit Nick Petalas for PR2754/2772/2813 and the prior rounded-line method;
Ross Richardson for the sharp Clifford-grid argument; David
(`sandersdavid90-droid`) for the joint-divisibility successor; Vasek/flyingviper
for PR2725; ywz65 for PR2586/2730; commdata2338 for endpoint fusion; Arham Tahir
for PR2674/2878/2891; Alejandro Zarzuelo Urdiales for Gaussian parity methods;
and the retained native/geometry/precision lineage, including Adam Gall,
Rohan Arun, Chafik Boukhalfa, Josie Elliston, Ali Romman and icekylinx.
Prepared for Arham Tahir with substantial OpenAI Codex assistance. Apache-2.0.
Frozen predecessors remain unchanged.

[sharp]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2750#discussioncomment-18959185
