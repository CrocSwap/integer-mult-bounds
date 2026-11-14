# B12 final publication text review

**Corrections requested: two scope/metadata statements.** The mathematical result, reported evidence, novelty and credit otherwise agree with final proof3167e192 and the frozen receipts. No scientific code/proof change or new experiment is requested. Author files were not modified.

## Scope and metadata corrections

1. **TASK.json / bottleneck_link is stale B11 text.** It currently says to remove all raw division calls while retaining other source arithmetic. Replace it with a statement about closing compare/add/subtract/divmod at the exact admitted current producer, while retaining Word lifecycle, higher controllers, owner metadata, grants and global assumptions. The actual_scope/result_summary already describe the combined B12 result correctly.

2. **README.md / acquisition lifetime mixes quantifiers.** J,H and P are defined for one current invocation, but the next sentence says “One descriptor lifetime therefore pays” that expression. A lifetime can contain several invocations of different widths, as the proof and actual traces show. Replace this with: “One invocation at width P pays the two J/H terms below; add89 if it starts a selector lifetime. Across invocations sum the terms using each actual width and pay ACQUIRE once per actual lifetime.” The displayed89+…<2^16(P+2)^4 remains a valid per-invocation upper bound. The final proof already has the correct varying-width rule.

## Small publication clarifications

- Add the exact canonical base `e54523517d0f03e58352e647c403a5af3e525a57` to the PR description, rather than leaving it only in TASK/SOURCES. Keep the two already-correct immutable B10/B11 commit links.
- State “All five foundational assumptions remain” explicitly in PR/README alongside No new kappa. Current wording says inherited assumptions/selected frontier are unchanged and the proof is correctly scoped, but this explicit statement matches the user's requested status label.
- Define m,t,v,E,J,H together at the displayed formulas (v is the valid right-coordinate count; H excludes nested calls inside old divmod). State that the three bare Python reproduction commands run **from the package directory**. No new replay is needed.

## Confirmed PASS items

The title is descriptive, does not start with Research:, and accurately names the source-bound interface. The graph/stock/prefix counts1,304,162/68/336,150, primitive upper401P+1073, workload formulas and2^16(P+2)^4 new-subset ceiling match the proof. The surrounding Word/controller, metadata, grant and history charges are kept separate; neither a common physical tariff nor a runtime/kappa improvement is asserted. Caller-prefix/setup costs are not priced by a child-width bound in the PR text.

Novelty is correctly limited to the combined comparison/addition/subtraction source join with aliases, finite flags and allocation/cost composition. #5053 is credited for the algorithms, numerical admission and live-stock theorem; B10 and B11 are linked by their exact published commits. #5219/#5353/#7388 are valid same-upstream PR references in the proposed CrocSwap PR body, and README also supplies explicit clickable URLs. No PR number is invented.

The claimed85 source objects,167232 dispatch paths,840 primitive packets,1135 comparisons,1510 additions,107 subtractions,192 divisions,1258 aliases and22,179,316 literal instructions match the frozen primary receipts. All three normal/optimized receipt pairs are byte-identical. Separate review evidence is distinguished from primary execution, old arithmetic runs only in baselines/counterfactuals, and the active replacement has zero old-provider calls. Original-trace termination, erasable instrumentation, malformed-path limits, current owner stock and fixed payload boundaries are stated.

@CubeJerry/Jerry Chen and substantial OpenAI assistance are explicit; predecessor authors and retained notices are credited. No human or formal-kernel acceptance is claimed. TASK has the original revision8 card, exact canonical base, completed outcome and substantive remaining questions. README has the required Open next questions heading.

## Reviewed file pins

- PR-DESCRIPTION.md: `cdb399241e985529f0dae7df0a87029c575eb722717734c1bc6526b59fcdcb1a`.
- PR-TITLE.txt: `68fc54f03291e5caedcd0f3edec770ec6d029be115556a7a91585bde7fb75fb7`.
- TASK.json: `89dcb8887771c8f99d031be94bb5a86551bc9347db9de69b67b28349ad6c5c38`.
- README.md: `2dcb0813b6e38af6dc426b91bbb9477941e8f2be97d25bbeb2e24b7c3279af41`.
- PROOF.md: `3167e19209a8fee4e5095b7c5914661163c7d038b5f745b64dd8713a6a9252ac`.
