κ = 6.83883297459132e-4

# Shared entrance gauges and refined physical bit word

Conditional κ ≈ **6.83883297459132 × 10⁻⁴**, exactly `170970824364783/250000000000000000`. Four groups of shared rank-18 gauges change 13 physical entrances; two donor substitutions improve the internal paid profile. The operation frames inherit our checked plateau/cascade refinement of PR211. The final bit coarse saving is `342175656946149/500000000000000000`.

## Reproduce

Python 3.11+, assertions enabled:

```sh
python3 -B research/coordinated-crossover-pr200/verify.py --temp-root /tmp
```

The five pinned archive parts include source and frozen complex witnesses. Verification uses a temporary extraction without git or network and leaves submitted files unchanged. The current executable path is `verify_inner.py` → `joint/replay_joint.py`, `joint/pack_joint.py`, exact frozen complex replay, then `joint/price_joint.py`. The retained geometry and frame-search files document and support the predecessor construction; its standalone `arithmetic.py` is not the current entry point.

The actual word adapter and selection are in `joint/`. See `JOINT-GAUGES.md` for the new gauged-donor argument, physical banks and complete paid ledger; `PLATEAU-REFINEMENT.md` records the preceding frame search. Float scores propose candidates only. Exact scalar/frame replay and rational moments determine the final claim.

The normalized profile has m=72, W=225491, rank mass16212120 and deficit23232. There are 36 physical replicas, with literal stock676473; the moment normalization is a factor12 and is not the physical replica count. Full bank assignments, normalizers, both reflected word ledgers and the adjacent-grid rejection are checked.

## Scope and attribution

All-size compiler, completed weighted/restored selector, routing, prime, precision, fixed analytic tape and finite bridge hypotheses remain inherited. The complex supplier retains its exact local-flow contract; no new global scalar transcript or unconditional theorem is claimed.

PR211: Rohan Arun, c63e50a5dde96fe1459d6b29e55e47f42f104347 (Anthropic Claude assistance). PR207: Dugongue, cd14825023b75af4f5919a30e5e6d548b6ade5bc. PR200: Chafik Boukhalfa, a1175449f34d39ff933d9d8ab23ced1f32b290ec. PR202: 8d8d67bcf69c5ea67d3a29dbc64ba588156d6e8d. PR197: Evan McKinney, completed-bank construction. All original licenses/notices and AI disclosures remain. This refinement was prepared by eumemic with substantial OpenAI Codex assistance.
