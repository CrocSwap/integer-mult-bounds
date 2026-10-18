# complex-571-hpe46: conditional κ 0.001613569610580215

Prepared by higherbeing with Claude Code assistance. Apache-2.0; see NOTICE.md for the inherited contributors.

## What changes against PR592/PR596

PR591 (jeremykothe2) ends 38 entering width-8 helpers per call on a hyperplane U instead of the full frame, so their residual
width drops to 7. Its candidate rule requires the helper's single cleanup gate to be the **first** cleanup gate on both of its
registers. Eight more helpers per call fail that rule only because their partner is *read* by an earlier cleanup gate; reading a
register twice commutes, so the partner's earlier gate is not an obstruction. This package replaces the rule by the exact
condition: the helper's cleanup gates, together with the non-commuting closure of the gates they must pass, run right after
part B at the minimal common frames (the closure here is the gate itself), and the helper ends at the hyperplane spanned by its
own and its partner's last frames. On every provider word (ck, atm3) this ends **46** helpers per call (the 38 of PR591 and 8
more), with the same local paid Φ and eight more width-7 residuals per call.

The owner map is renominated for the new width inventory with a window MILP (HiGHS) plus lazy cross-time Hall cuts and an exact
per-window matching. Idle remainders: {3:197, 25:1, 48:1986} (PR592: {1:2, 2:1, 3:280, 12:1, 48:1969}); the LP bound for this
menu is 41,862.3 Φ against 42,321.7 Φ for PR592's menu.

Everything else (geometry, pinned sources, the other build steps, dispatch ck×53 / atm3×19, the asynchronous call order, the
HPE verifier code of PR592) is unchanged. `verify.py` gains one allowlisted step type, `hyperplane_end_closure`
(`code/build_hpe_closure.py`), whose output is recomputed from the input word and must equal the recipe; it is followed by
PR592's unchanged raw-word control audit (`hpe_controls_atc.py`, 8 mutations rejected) and by the same independent comparison
as `hyperplane_end`. `code/witness.py` records pins in discovery mode (`WITNESS_RECORD`); strict mode is unchanged.

## Verification

Same pinned sources as PR592 (PR568 `71c99ac`, PR569 `897213a`, PR571 `b7bdc5a`, PR575 `eac6f7e`, PR583 `89be768`):

```sh
python3 -B research/complex-571-hpe46/verify.py --work /tmp/hpe46 \
  --source multicold=../pr568/research/complex-multicold --source larger_gain=../pr569/research/larger-gain \
  --source structural_gain=../pr571/research/structural-gain --source joint_prefix=../pr575/research/complex-joint-prefix \
  --source frame_coalescing=../pr583/research/kernel-frame-coalescing
```

## Scope

Conditional on the same inherited assumptions as PR592 (all-size compiler, common-label/mutable-source realization, whole-call
hosting, precision/tape, analytic transfer, Lemma A for hyperplane-ended helpers as stated in PR592's PROOF-HYPERPLANE-END.md and
PR593's Lean). The eight additional helpers satisfy exactly the hypotheses of PR591's construction (one cleanup gate, run at U
right after B, helper never touched afterwards, partner continues to FULL); only the commutation argument for moving the gate past
the skipped cleanup prefix is generalised, and it is checked by the exact scalar replay of the reordered program in
`hpe_audit_and_transport.py` and `hpe_controls_atc.py`. No unconditional theorem.
