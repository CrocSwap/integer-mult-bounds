# PR589's bit word is exactly transport-locally optimal (scoped negative result, no new kappa)

**Claim.** Keep PR589's gate multiset, operands, scatter, start/final frames, D, the
rebuilt literal-reverse C, and the retained totals' COPY frames (decoder constant 63)
fixed. Then no **transport** — relocating one elementary addition `r += s` to any
position inside its exact commutation window at any legal catalogue frame (or the
closure frame of the slot bounds) — lowers the moment `Σ_d n_d·d·(64/d)^c` of the
local paid profile at the exact bit saving `c = 1733427039589844234749/10^24`.
The same holds for every pair of simultaneous transports sharing a register.
PR589's own gain came from two transports, and its tuner (`../e8-bit-p111-tuned/tune/`)
reached the word by greedy single moves with **floating-point** chain fees at the
rounded exponent `a = 0.001733`, making no optimality claim. `bit589-frame-optimum`
proved the word exactly frame-optimal with the gate sequence fixed and stated that
future bit headroom on this word must come from gate-order or structural changes.
This closes the gate-order part of that question exactly and independently.

**Scope: no new kappa.** The selected assembly binds on the complex primitive
(`a_c = 0.0016754627 < a_b = 0.0017334270`, bit slack 3.46%); no bit-supplier change
can raise the selected kappa at this base. As in `bit589-frame-optimum` and
`bit589-width-packing`, the contribution is bit headroom / door closure.

## Method (`atlas.py`, standard library only, independent of the contributor tuner)

1. **Exact objective.** The pinned moment engine
   (`../complex-k492-owner-repair/vendor/multicold/engines/base_two_moment.py`,
   sha256 `aee70c24…`) gives outward rational bounds for `d·(64/d)^c` at the exact c;
   no float decides a comparison. The scored quantity is the full per-register
   frame-chain cost (D, A, B, C, final) plus scatter tops, which reproduces the
   replay paid profile `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` exactly —
   this also repairs the tuner's section-local model, which double-counts the
   last-A-to-first-B climb and ignores D.
2. **Moves.** For each of the 2130 A and 934 B elementary additions: exact
   commutation window, context-constant slots, feasible catalogue frames between the
   operand bounds (plus the closure frame), COPY-frame preservation on retained
   totals, and full-chain nesting. 3411 distinct slot-bound pairs.
3. **Simultaneity.** Transports on disjoint register pairs are independent (chain
   costs decompose per register), so with no improving single transport no disjoint
   simultaneous move improves either. The remaining coupling is shared registers:
   every pair of movable transports sharing a register is enumerated with all
   frame/slot choices. Full components are one 1924-op giant (A) and five
   ~200-op giants (B) — combinatorially out of reach; see Limitations.
4. **Legality cross-check.** Sample moves of each outcome class are applied to the
   word, C rebuilt, and replayed exactly (nested frames, F2 endpoint); the replayed
   profiles match the chain-model predictions.

## Result (`result.json`)

| class | A | B |
|---|---|---|
| elementary additions | 2130 | 934 |
| legal non-home single placements | 5830 | 3561 |
| same paid profile | 5580 | 3226 |
| strictly worse (exact) | 250 | 335 |
| **improving** | **0** | **0** |
| smallest strict loss | 8.00e−6 | 1.94e−3 |
| shared-register pairs / combos scored | 13673 / 225152 | 6006 / 218448 |
| **improving pairs** | **0** | **0** |

No comparison was left unresolved by the rational bounds. The 8 replay spot-checks
(4 same-profile, 4 strictly-worse) reproduce the predicted profiles.

## Limitations

- Simultaneity is certified for pairs, not for triples or larger shared-register
  sets (giant components); a superadditive triple is not excluded.
- Steinberg 3→2 substitutions and other structural changes are a different move
  class, out of scope here (frames alone: `bit589-frame-optimum`).
- Cross-section simultaneous moves (one A, one B transport on a shared register)
  are not enumerated; they couple only through the single last-A-to-first-B climb.

## Reproduce

```sh
bash research/bit589-transport-atlas/verify.sh   # ~70 s; last line PASS_BIT589_TRANSPORT_ATLAS
```

Python 3.11+, standard library only (CPython 3.12 used). Base commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Seed 10 (bit supplier track).
