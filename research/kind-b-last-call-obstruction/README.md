# Prove the all-width kind B finishing obstruction

A nonplain kind B shared-call part `y=WD+cW gamma` cannot be finished by one last call alone at any address width or any nonzero rational coefficient. The final call must raise `WD` to level three. The proof supplies an explicit linear functional on two or three formal group terms that kills every available column and is nonzero on the target.

This upgrades the finite kind B observation in [PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629). It covers spare address bits. It does not exclude post-call free processing, joint use of both last outputs, three-term parts or a general two-in-five program. It is separate from the removal theorem in [PR #7679](https://github.com/CrocSwap/integer-mult-bounds/pull/7679). No new kappa is claimed.

[Proof and exact hypotheses](PROOF.md) · [Receipt and representative matrices](RESULT.json) · [Verifier](verify.py) · [Task and open questions](TASK.json)

## Reproduce

Use CPython 3.12 and the standard library. No external runtime input is needed.

```sh
python3.12 -I -W error -B research/kind-b-last-call-obstruction/verify.py
python3.12 -I -W error -B -O research/kind-b-last-call-obstruction/verify.py
python3.12 -B scripts/research_package.py --package research/kind-b-last-call-obstruction
```

Expected status: `PASS_KIND_B_LAST_CALL_OBSTRUCTION`. The verifier checks all 319488 nonplain three-bit part/call pairs for fixed first/shared calls. Polynomial separating certificates cover all nonzero rational coefficients on those pairs. Eighty full rational orbit-span checks and 240 varied-direction checks cover selected wider instances. Plain, zero-coefficient and lower-target-level cases give positive controls. A corrupt separator and two small linear-system checks test the proof and elimination boundaries. Each registered command has a 120-second limit.

The all-width conclusion follows from the written horizontal-plane and forced-coordinate proof. The finite census is not an exhaustive check of larger widths or arbitrary programs. The original scientific suite, selected cold replay, Lean and Docker were not run. No independent human or formal-kernel review is claimed.

## Task and next questions

Base: canonical main `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8, card `complex-rank-shape-decoder` narrowed to one formal finishing obstruction. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19704095) names that scope. The current priorities permit a scoped local result; no physical construction is proposed because a source-compatible native decoder and complete invoice remain absent. Open/closed PR and Discussion overlap contains the finite source and the distinct kind A and removal results. Sparse local and unpublished work remain coverage limits.

## Open next questions

Can a free map on the last-call output finish a nonplain kind B part? First add those output terms to the column family and check exactly where the two- or three-coordinate separator fails. The present theorem does not include those columns.

Can both last-call outputs be used together without losing either target? First put both input parts and both last-output families in one formal system with shared preparations explicit. One-part finishability does not decide that joint problem. A Pauli-phase lift and a complete physical invoice would then be separate requirements. [Structured questions](TASK.json)

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance. Credit Jacob Sussman for the definitions and finite kind B observation in [PR #7629](https://github.com/CrocSwap/integer-mult-bounds/pull/7629), [pinned source](https://github.com/jacobalansussman/integer-mult-bounds/blob/c2a2131e7dba35f9396b16588e125a7e8b5fab8e/research/complex-m3-shared-call-finish-or-remove/README.md); Nick Petalas for the related coset proof in [PR #7649](https://github.com/CrocSwap/integer-mult-bounds/pull/7649), [pinned proof](https://github.com/petalas/integer-mult-bounds/blob/f642d2740265a61f8ac64b3a087f0118382c56e3/research/kind-a-last-call-coset/README.md); and the endpoint method and reused arithmetic routines in Ali Romman's [PR #7679](https://github.com/CrocSwap/integer-mult-bounds/pull/7679), [pinned verifier](https://github.com/aliromman/integer-mult-bounds/blob/7c3b229d0788d6e980f75cbaabe07287899263a2/research/kind-b-frame-swap-removal/verify.py). The source retains the original frame-geometry lineage. New work is Apache-2.0.
