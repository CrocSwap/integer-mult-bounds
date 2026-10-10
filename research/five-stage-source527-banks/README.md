κ = 7.10436534421701e-4

This extends [PR251](https://github.com/CrocSwap/integer-mult-bounds/pull/251), eumemic's 37-entrance transport at κ = 7.10433687047883 × 10⁻⁴, by a second exact frame retiming of its word: twenty-five internal forward-gate ADD frames are reassigned by local descent on the concave paid-rank objective Σ r·ln(120/r). The local paid histogram changes by {2: −2, 4: +24, 5: −48, 6: +25, 11: −1, 13: +2, 17: −1}, so one local recursive call per helper invocation disappears at unchanged rank mass 433,953. The literal construction keeps 24 replicas, stock 521,425 and deficit 105,600 with 11,792,160 paid calls and rank mass 62,465,400. `descent_transform.py` consumes the frozen `descent-selection.json` (explicit rational bases and record bindings), rebuilds every MOVE from the selected gate needs, recomputes the exact integer source span of each non-target operand from the actual scalar word and requires it inside the new frame, and checks nested chains, fixed endpoints, nondegenerate endpoint bases, both reflected annihilator ledgers, unchanged COPY lifetimes and the byte-identical scalar/COPY projection. Conditional κ improves by 2.85 × 10⁻⁹ over PR251. Prepared by Rohan Arun with Anthropic Claude assistance; everything below describes the inherited PR251 construction.

PR251 extends [PR249](https://github.com/CrocSwap/integer-mult-bounds/pull/249), which transported 21 dirty entrances at κ ≈ 7.10392186446856 × 10⁻⁴. The new shared intersections add 16 entrances and 224 entrance-rank units, giving 37 transported entrances with total rank 549.

Thirty-seven additional dirty entrances reduce the bank stock per replica by 22.875. Nine entrances have rank 18, nine rank 17, six rank 14, eleven rank 12 and two rank 9. Each selected helper is untouched up to the pinned cut after all 441 target-coordinate setup additions. Moving its original zero-frame compensation through that exact F₂ prefix changes its response to the corresponding transformed column. The 148 old reads become 150 reads at the new nondegenerate entrance frames. Every new entrance lies in the helper's first required frame and each affected target's next required frame. Several helpers share one entrance frame so the target paths can serve the whole cohort. Exact intersections of allowed frames and minimum-cut role selection find the additional cohorts; the verifier consumes their explicit rational bases and checks the resulting word independently.

The emitted word is checked on all 20,107 formal F₂ columns in both directions, including arbitrary dirty and source restoration. Both reflected frame ledgers are reconstructed from actual gate uses. The signed source527 producer keeps its original execution context; only the lowered word receives the separately cloned entrance context. The emitted signed prefix bounds remain 37,631 forward and 3,295,796 backward. This uses the retained F₂ payload contract and does not assert that the new integer lift has the old target decoder.

All five stages, bank assignments, exact charts, prime witnesses, routing, copied centers, cleanup and fallback remain charged. The charts require up to 548 elementary factors and normalizers up to 787 factors; the added bank selector bill is 376,079,448,960. This fixed bill is included in the finite accounting. The literal construction executes 24 replicas with stock 521,425, 11,792,160 paid calls, rank mass 62,465,400 and deficit 105,600. The exact moment uses that complete literal profile. The bit supplier binds.


Run with Python 3.11+, SymPy 1.14.0, and assertions enabled:

```sh
python3 -m pip install -r requirements.txt
python3 -B verify.py --output /tmp/regauged-source527-verification
```

Use a new output directory outside the package. The verifier reconstructs all eight mandatory stages without network access and rejects changed or missing package files. See PROOF.md, BANK-PROOF.md and the retained source notices for the construction, hypotheses and provenance.

This remains conditional on the inherited all-size compiler, common weighted chart, restored rows, selectors, tape routing, prime supply, precision/recovery, complex symbolic correctness and analytic reduction. Prepared by eumemic with substantial OpenAI Codex assistance; original licenses and contributor disclosures remain included.
