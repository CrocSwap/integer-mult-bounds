# Seed 5 task selection

- OS-random seed: `5` (0–59); bit supplier track.
- Exact base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
- Candidate selection: `seed mod 3 = 2` chooses the third narrow task below.
- Within that task, sort shared PR589 registers by `dim(firstB)-dim(lastA)` descending, then register ID descending; `seed mod 3 = 2` chooses the third register from the top three.

## Three candidates

1. **Larger/nonabelian register relaxation.** The task card `bit-new-register-model` asks for a target-specific relaxation beyond the three-register abelian alphabet. PR #1333 already supplies an exact paid-cost theorem for binary affine register words; a fresh contribution here would need a materially different explicit alphabet and complete price.
2. **One helper-star interface contract.** The task card `bit-helper-contract` asks for a precise H2/K replacement. PRs #1307 and #1311 and nearby helper-star work already examine hosting and semantic-D bridges; another scalar-count-only case would not close the interface.
3. **Jointly boundary-adaptive A/B transport.** PR #1382's fixed-option census identifies a direct open question: the moved A/B pair can change the boundary that determines each other's feasible frames. The task is to solve this joint feasibility question for one seed-selected high-gap register and its boundary operations. This is selected.

## Seed-selected object and price

The shared-register source contains 336 A/B registers. Their largest baseline boundary rank gaps are `(gap 2, register 67)`, `(gap 1, register 660)`, `(gap 1, register 659)`. The seed-selected third object is register 659 (boundary rank gap 1), with last-A op 2071 `(501,290,659)` and first-B op 820 `(598,184,659)`.

Exact commutation-window slot regions are A: `[2070,2071]` (2 regions), B: `[65,819,820,822,823]` (5 regions). Ignoring only the counterpart boundary gives 8 A frame choices and 16 B frame choices. For each of 8 A choices and 5 B slot regions, the dynamic lower bound can add at most one closure frame to the B catalog set, so the conservative complete search cap is `8*(16+5)=168` frame pairs before full-chain filtering. The actual domain will be counted by the verifier.

## Overlap and current-state checks

- The selected certificate remains #1094, κ `836330098538459/500000000000000000`, on the #589 bit supplier. Its inherited assumptions and review remain unchanged; this task does not touch the selected record.
- PR #1382 is open at head `cf17b06c00c50a22315f210c5f6b5197c860abdd`. It exhausts fixed-boundary options and explicitly lists joint boundary-adaptive options as the next question. This task is a one-register extension, not a re-run of its fixed-option census.
- Fresh overlap scan at 2026-10-14 00:04 UTC covered 862 open PRs and 109 discussions. The query `PR589 boundary-adaptive register 659`, `last-A first-B joint frame`, `paired boundary adaptive options` returned zero possible matches; the scanner warns this is not a novelty certificate.
- Latest bit-supplier claim is seed 0 on the independent PR1363 R420 block-4 replay, a different object. No active claim covers register 659's A2071/B820 joint boundary.
- Coordination claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911738.


## Completed result

The exhaustive two-slot by five-slot joint pass generated 20 assignments after
applying the moved A frame to B's dynamic lower bound. Restoring the reciprocal
A upper bound rejected 8; 12 passed both directions and the complete register
chains on registers 184, 290 and 659. Their paid profiles were 8 ties and 4
strictly worse outcomes, with no improvement or unresolved interval. The fixed
original-boundary control also has 12 valid assignments, so this cut exposes no
joint-only pair. This is finite evidence for this one pair of operations, not a
general boundary theorem. See EXPECTED.json and `atlas.py` for exact witnesses.
