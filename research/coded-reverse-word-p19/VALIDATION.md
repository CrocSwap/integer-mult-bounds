# Validation

The priced object is the **coded p=19 chain** (259 gates, 77 recodings). The 241-gate uncoded
trace is the formal controller reference.

| Command | Runtime | Generates | Result |
|---|---|---|---|
| `p19_word.py` | ~4 min | `P19_WORD.json` | the priced chain: 259 gates, 77 recodings, 17,248 monomial maps, 68,992 adds, 1,232 clears, randomised replay against the standard word (2,179,072 state entries) |
| `p19_plain.py` | ~13 min | `P19_PLAIN.json` | the formal reference: trace == `controller()`, 241 gates, denominators `[1]`, price 0.007578535 |
| `p19_native_symbolic.py` | ~4 min | `P19_SYMBOLIC.json` | fresh-block geometry: stage → block bijection, ambient rank 1+8p (153 at p=19), exact chain identity against the thinned controller operator at p=2,3,4,5,8,19, and the derived rank census beside the invoiced histogram |
| `p19_native_apply.py` | ~7 min | `P19_NATIVE_APPLY.json` | `apply(program, state)` transcribed from the pinned spec: both orientations, 21,449 records and 20,991 state steps each, frames end on `canonical.final`, and the paid histogram plus scalar tariff derived from the trace; the lineage word is run as a control |
| `p19_caller.py` | <1 min | `P19_CALLER.json` | the three items `PHYSICAL.md:59` names (caller, initial/final gauges, paid corrections) exhibited for the **abstract/controller** endpoint; encoding the chain into the native event stream is explicitly not proved |
| `p19_lowering.py` | <1 min | `P19_LOWERING.json` | binds each emitted gate kind to a line of `PHYSICAL.md` (R = D∘Q, X ← X − Q·C·Y, C⁻¹ after Q⁻¹, gauge cancellation, idle powers); cites the frozen program by hash instead of replaying its 21,449 records |
| `p19_lift.py` | <1 s | `P19_LIFT.json` | operator-level lifting lemma: 263,169 exponent pairs, axis commutation, identity, exponent bound, stage coverage |
| `p19_bridge.py` | <1 s | `P19_BRIDGE.json` | inherited unit: 448 adapters per direction, their bracketing positions, the listing-to-native kind mapping, and the pricer's dependence on ranks alone |
| `p19_bank.py` | ~10 min | `P19_BANK.json` | p=2 address-level control, pattern T (the pattern that retains terminal idles) |
| `p19_claim.py` | <5 s | `P19_CLAIM.json` | invoice, guards, compiler ranks, BIT chain, budgets, ledger, ABI vocabulary |
| `verify.py` | ~2 min | — | runs the controller suite, executes `p19_lift.py` and `p19_bridge.py`, checks the word/bank/claim receipts and their pinned hashes |
| `scripts/research_package.py --package … --check-only` | <5 s | — | metadata, pins, declared inputs |
| `python3.12 -B scripts/research_package.py --package …` | ~5 min | — | registered replay |

Inherited premise, not discharged here: the inherited producer/compiler contract admits this finite p=19 unit composition with the recorded native lowering, endpoint, field-state, ownership, precision, helper, fixed-tape, compiler-schedule, hosting and review interfaces. `P19_PRECOMPILATION.json` records that no serialized chain-to-event compiler exists in the repository, so that premise is stated rather than proved. `p19_word.py`'s state comparison is randomised; the operator-level argument is the lifting
lemma plus the rank-free recoding check. No command performs a git write.
