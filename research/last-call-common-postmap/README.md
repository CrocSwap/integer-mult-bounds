# Enforce one common free map after one last call

If a shared part has one level-two leading term and only lower-level companions, a free map on one last-call output adds no finishing power. Projection onto the level-three target frame forces that map to be an invertible element of `Q[P intersection TPT]`. It can be moved before the call.

For nonplain kind B parts, the [call-alone obstruction #7683](https://github.com/CrocSwap/integer-mult-bounds/pull/7683) therefore extends to arbitrary common free postprocessing, at every address width and every nonzero rational coefficient. An explicit two-column identity shows why the larger span of independently postprocessed calls is insufficient as a one-call test. A known kind A post-call mechanism gives a positive control when there is a second level-two term.

[Proof and scope](PROOF.md) · [Exact receipt and matrices](RESULT.json) · [Verifier](verify.py) · [Task and questions](TASK.json)

No general two-in-five impossibility, joint decoder, phase lift, native word or kappa improvement is claimed. The theorem concerns one common map applied to one prepared call output. The call-alone proof is a mathematical dependency and is linked at its exact commit.

## Reproduce

Use CPython 3.12 and its standard library. No external file is read at run time.

```sh
python3.12 -I -W error -B research/last-call-common-postmap/verify.py
python3.12 -I -W error -B -O research/last-call-common-postmap/verify.py
python3.12 -B scripts/research_package.py --package research/last-call-common-postmap
```

Expected status: `PASS_LAST_CALL_COMMON_POSTMAP`. The verifier checks all 344064 three-bit preparation/call pairs, all 24576 surviving target-frame columns, 32 unit/nonunit cases, 96 wider conjugated contracts, the relaxed-span false positive and an actual kind A one-call post-map. The latter is a boundary control, not a new construction. Each registered command has a 120-second bound.

The written proof covers all widths and all common free maps. Finite checks do not enumerate arbitrary rational maps or the full wider groups. The predecessor's full call-alone census, native operators, selected cold replay, Lean and Docker were not rerun. Independent human and formal-kernel review are unclaimed.

## Task and scope

Base: canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8, card `complex-rank-shape-decoder` refined to the post-call boundary. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19704278) explicitly separates a relaxed span from one common-map realization. The family gate keeps this a bounded proof task; no physical cost or supplier gain is inferred. Refreshed open/closed PR and Discussion overlap contains the earlier finite, kind A and call-alone results. Sparse local and unpublished work remain coverage limits.

## Open next questions

Can two last outputs jointly decode both input parts? Keep separate common-map factors for each physical output. The relaxed identity here uses two calls and shows why freely summing prepared/postprocessed columns can undercount them.

Can the target-frame unit argument handle two or more high-level companions? First compute their full projected coefficient algebra. The kind A control shows that it can exceed the intersection subgroup and that the present fold then fails. A phase lift and full physical invoice remain separate obligations. [Structured questions](TASK.json)

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance. Credit Jacob Sussman for the definitions and kind B post-call question in [PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629), [exact source](https://github.com/jacobalansussman/integer-mult-bounds/blob/c2a2131e7dba35f9396b16588e125a7e8b5fab8e/research/complex-m3-shared-call-finish-or-remove/README.md); Nick Petalas for the related coset method and boundary in [PR #7649](https://github.com/CrocSwap/integer-mult-bounds/pull/7649), [exact proof](https://github.com/petalas/integer-mult-bounds/blob/f642d2740265a61f8ac64b3a087f0118382c56e3/research/kind-a-last-call-coset/README.md); and Ali Romman's [PR #7683](https://github.com/CrocSwap/integer-mult-bounds/pull/7683), [exact call-alone proof](https://github.com/aliromman/integer-mult-bounds/blob/9b99d7b30972a78e1ad0e90dd6ff3187bd3cc86c/research/kind-b-last-call-obstruction/PROOF.md), for the corollary's required predecessor. Its binary matrix code, originally from [PR #7679](https://github.com/CrocSwap/integer-mult-bounds/pull/7679), is reused. New work is Apache-2.0.
