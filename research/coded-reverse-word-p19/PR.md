**Price the p19 coded-reverse chain: conditional κ = 0.0033999964**

## Change and mathematical scope

The p19 coded-reverse chain is materialised, replayed and priced, and the target census it realises is the census the invoice prices. The accepted conditional endpoint is **κ = 951999/280000000 = 0.0033999964**.

| Comparison | Conditional κ gain |
| --- | --- |
| Selected record `605457647/200000000000 = 0.003027288235` | `+12.31%` |
| Earlier record `60403/20000000 = 0.00302015` | `+12.58%` |

The complex supplier is **0.007578535190** and the BIT supplier **17/5000** binds the endpoint: at exactly `0.0034` one outer predicate fails (`actual_bit_above_effective`), so the claim sits five grid steps below it. Guards at the endpoint with the unchanged invoiced census are α `0.995794142`, γ `0.963763313`, δ `0.951560608`; both decay blocks stay under `1/16` and the power-1024 tails under `2^-32`. The compiler majorant is shape-correct at `v = 1024`, `h = 1/64`, `B = (5+8h)v`, `H0 >= 8v`, giving `H0 = 5,170,423,668,736` with `20^64 < 21^63` and maximum target rank `153 < 256`. All 54 strict and four functional outer predicates are positive.

The word has 259 gates: 19 gauge loads, 20 forward, 19 reverse, 19 letters, 36 retained idles, 108 bridges and 19 closing swaps. It carries 77 recodings, 17,248 monomial field maps, 68,992 scalar adds and 1,232 owned clears, with no recursive Gaussian children. The ambient target rank is 153. Replay against the standard word differs on **0 of 2,179,072** entries at p=19 and 0 of 229,376 at p=2.

## Target census

A target is what a role ends holding, an entry of the factorisation diagonal, not the row or column closure of the thinned matrix. Measured on the diagonal, the realised multiset equals the designed one at every tested size.

| p | Realised diagonal supports | Designed |
| --- | --- | --- |
| 3 | `{1:4, 3:2}` | identical |
| 4 | `{1:4, 2:2, 4:2}` | identical |
| 5 | `{1:4, 2:4, 5:2}` | identical |
| 8 | `{1:4, 2:4, 3:4, 4:2, 8:2}` | identical |
| 19 | `{1:4, 2:4, 3:4, 4:4, 5:4, 6:4, 7:4, 8:4, 9:4, 19:2}` | identical |

At p=19 this is the invoiced histogram `{9:448, 17:448, 25:448, 33:448, 41:448, 49:448, 57:448, 65:448, 73:448, 153:224}`. An earlier version of this package measured the row closure, concluded the census did not match, and derived several results from that reading; the row-closure measurement is the wrong observable, and those results are retained only as superseded diagnostics.

## Receipts

| Receipt | What it establishes |
| --- | --- |
| `P19_DIAGCENSUS.json` | the diagonal target census equals the invoice at p=3,4,5,8,19 |
| `P19_LOWERING.json` | the gates are the primitive `PHYSICAL.md` states — `R = D∘Q`, `X ← X − Q·C·Y`, `C^-1` after `Q^-1`, gauge cancellation, idle powers |
| `P19_NATIVE_APPLY.json` | the frozen base word's event encoding and frame/tariff trace executed: 21,449 records and 20,991 state steps per orientation, frames ending on the recorded final frames, derived profile `{1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}` and tariff 158,120 forward / 158,168 backward |
| `P19_LIFT.json` | operator identity for every block count, by multiplicativity over 263,169 exponent pairs and every axis pair |
| `P19_UNITS.json` | 19 units, 19 loads / 19 unloads / 19 signed swaps, endpoints `[1]` and `[1,13]` |
| `P19_CLAIM.json` | guards, compiler ranks, BIT chain and the outer ledger |
| `p19_gates.py` | 62 checks over the receipts and their pinned hashes |

The paid profile is the base program's, derived from its own frozen trace and reused here as an inherited input; it is not derived from a p19 trace. Rank 8 is absent for the same reason the chain emits no CENTRE gate: the PR4929 profile applies and `invoice()` prices exactly the dict it is given (`coded-reverse-controller/verify.py:167-168`). The frozen comparison word keeps its eight centre calls, which is why its declared profile shows `8:8`.

## Limitations

The inherited producer/compiler contract must admit this finite p=19 unit composition with the recorded native lowering, endpoint, field-state, ownership, precision, helper, fixed-tape, compiler-schedule, hosting and review interfaces. `P19_PRECOMPILATION.json` reports `FINDING_PRECOMPILATION_CONTRACT_MISSING`: no serialized chain-to-event compiler exists in the repository, so that admission is not discharged here. The macro, forward, reverse and resource receipts are owned-work and operator checks, not native event programs, and none is presented as a compiler. The claim records `physical_attachment: CONDITIONAL` and `kappa_attached_to_physical_chain: false`.

Not claimed: unconditional attachment, a proved lowering of this chain to native events, a new selected κ, resolution of the precompilation finding, or any global optimality statement.

## Verification

Registered replay `PASS_REGISTERED_RESEARCH_PACKAGE outcome=completed` against a 980 s four-command budget. The gate table reports 62 checks and no failures; package metadata and pins pass. Python 3.12, standard library only.

## Credit

The controller and its invoice model come from `research/coded-reverse-controller/` (PR4940 lineage) and the paid profile from the PR4929 construction. The retained native word is `research/coded-native-caller/` over `research/joint-helper-lattice/`; its event specification is `research/kappa-lean-verification-20261022/NativeCore.lean` with `native_generate.py`, from the PR4470/PR4610 lineage. The lifting argument and the moment engine are shared with `research/higher-moment-strictification/`. See those packages for authorship. Prepared with Claude Code assistance; no subagents. New work is Apache-2.0.
