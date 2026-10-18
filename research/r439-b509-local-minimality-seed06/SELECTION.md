# Task card: local ADD minimality for R439 frame 509

## Assignment and base

- OS assignment seed: **6** (Bit supplier track).
- Base commit: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` (`origin/main` at fetch).
- Selected conditional baseline: κ = `836330098538459/500000000000000000`.
- Bit supplier ancestry: PR589 on PR555; selected-source record pins PR589 head `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`.

## Three candidate tasks and selection

1. **A larger/nonabelian bit register model.** The seed-6 catalogue suggestion was checked against live coordination. Discussion #1317 completed as PR #1333, so this route is already claimed and completed.
2. **A replacement H2/K helper-star interface.** The catalogue's second suggestion overlaps the exact dirty-target relaxation in PR #1306 and the semantic-D bridge in PR #1311, as well as the existing helper-star packages. The broad interface question is not a useful unclaimed scope here.
3. **A local lower bound for the open R439 frame-509 rewrite in PR #1221.** Selected. PR #1221 gives a three-ADD Boolean replacement and explicitly disclaims circuit minimality. At the final overlap refresh, PR #1344 independently replayed the same matrices and full splice but still made no minimum claim. This task independently certifies the exact local minimum under the standard scalar-add gate model and classifies the shortest four-register words. It adds an optimality statement; it does not repeat PR #1344's splice replay or re-review the full supplier.

The overlap helper also returned PR #1284, a three-ADD direct-target cost in a distinct rational triangle-observation model; it uses a different object and operation alphabet, so it does not cover this R439 bit block.

## Exact question and method

For the fixed frame-509 Boolean endpoint on `(a,b,h,c)=(33,38,468,77)`, prove the minimum number of scalar ADDs is exactly three when each ADD has one destination and the local boundary labels are fixed. The endpoint is

```text
(a,b,h,c) -> (a, b+a, h+b, c+a) over F2.
```

The lower bound is destination-based: the endpoint changes three distinct destination coordinates (`b`, `h`, `c`), and one scalar ADD writes only one destination. The three-ADD witness in PR #1221 attains this bound. Independently execute both the four-ADD and three-ADD words over every Boolean input, check the integer transfer difference `2 e_468 e_33^T`, and enumerate all 4-register CNOT words through length three as a reproducible finite cross-check.

## Scope, overlap, and stop rule

- PR #1221 is intentionally acknowledged: its construction is the witness being independently classified, and its README explicitly says minimum is outside its claim.
- The result is only the minimum for this fixed local Boolean endpoint in the scalar one-destination ADD model. It does not prove a minimum for the full 31-gate frame block, any altered frame path or boundary map, hosted adoption, a paid recursive profile, or κ.
- Check for a new exact frame-509 minimality claim immediately before posting. If one exists, release this scope or identify a distinct missing claim before continuing.
- Stop after the exact finite replay and focused package checks; do not run the selected frontier cold replay.

## Deliverable and provenance

Expected package: `research/r439-b509-local-minimality-seed06/` with proof note, standard-library verifier, exact input references and tests. Predecessors: Hanson Sun (@bbMisk), PR #1221, for the 20-ADD witness; Cinna Davis (@1337isnot1337), PR #973, for the 21-ADD parent; DreamingOfClouds, PR #589, and eumemic, PR #555, for the selected R439 word.

Prepared with substantial OpenAI Codex assistance; no human independent review is claimed. Apache-2.0.

## Coordination claim

Posted to the pinned start-here discussion at 2026-10-13 23:08:59 UTC: https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911102
