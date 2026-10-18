# Reader-aware restoration cuts

Status: claimed, recursive interfaces, OS-random seed 53. Owner Sagar Thakrar
with OpenAI Codex, chat `01a136c4-b32d-7a30-92f0-d8dffa66b80f`, local host.
Scope key: `restoration-coalescing/diagonal-readers/checkpoint-correct-cuts`.

Cycle starts 2026-10-13 19:37:19 UTC. Scope deadline 19:45:19 UTC;
verification starts by 20:07:19 UTC; hard finish 20:17:19 UTC.
Checkout: `/Users/thakrarsagar-dev/Documents/Codex/2026-10-13/continue-the-user-s-research-loop-13/work/integer-mult-bounds`.
Fetch completed 19:37:56 UTC. Clean local main and fetched origin/main were
both `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe` at 19:38:11 UTC, before
creating `research/cycle08-seed53-recursive-interfaces`. That is the base.
Prior branches are preserved.

## Three candidates and reductions before implementation

1. **Selected: permit diagonal readers during restoration coalescing.**
   PR1155, `9821c6e9388f3fc097e94b72be9fa7b41a849527`, gives read-free
   phase/permutation examples, a failing reader example, a written model and
   cost recurrence. Its README calls absence of readers necessary. Read the
   README, actual Batch interpreter, builders, verifier and certificate.
   Cheap counterexample in its exact model: five scalar children all negate
   W and read coefficients `[1,1,1,-1,1]`. Eager and deferred outputs both
   increment D by `3W`; one final negation restores W. All five children read
   W. At child two the data values differ, so an intermediate observation is
   a real constraint. New evidence: a necessary and sufficient interval test,
   minimum-cost checkpoint-correct partition tool, full node recurrence and
   exact independent enumeration. No novelty is claimed for matrix algebra.
2. **Rejected: extend four-way port borrowing to higher arity.** PR1164,
   `0b2077e929ec488a4d38b3523688a8a68bf1b43e`, already gives the chain word,
   endpoint/middle call multiplicities and a pool-count induction. Read its
   PROOF.md and embedded PR1057 proof. Replacing four by k is a direct
   consequence and a larger replay would add no distinct result.
3. **Rejected: fixed unequal positive/negative connector-query prices.**
   Accepted PR1088, `b0396aad724fec58630fbd4d13a809c562f18d9e`, proves the
   signed three-by-three weighted optimum. Read the retained README and
   query alphabet. Uniform correctness forces equal positive/negative counts
   for each named query, reducing its fixed directional prices to their
   average. This does not produce a new optimization problem.

## Scope and overlap

The selected domain is a fixed ordered batch of exact diagonal reader shears
and diagonal signs over characteristic zero. Every chosen restoration cut
must match eager D and W, with optional mandatory cuts. The tool does not
optimize arbitrary reversible programs, permit inaccurate intermediate cuts,
change children, or claim a supplier or kappa improvement. A complete price
must include child calls, source access, workspace, preparation, control,
restoration and any physical adapters.

Inspected all 1170 PRs available at the check, including 786 open PRs, their
bodies, the central ledger, selected PR1094 construction/assembly/source
manifest and review, prior loop negatives, and live discussions 1163/1166/1167.
There is no pinned sprint issue. The immediately refreshed discussion 1166 has
Adam Gall's unrelated PR279 provenance claim at 19:42:46 UTC; no overlapping
restoration claim appeared. The latest open PR was 1177.
Claim is local as specified by the research brief. No separate issue is opened.
PR249 `96495746c786d6d0339dbb38c7f553d4af3f88ed` and PR309
`aeb4808af1392e565e7071cbeb2c29608201cf24` transport dirty-helper responses
through concrete supplier words; that algebra is credited, not reinvented as
a new mechanism. The distinct deliverable corrects PR1155's applicability claim
and supplies a reader-aware cut planner with a precise observation contract.
Prior PR1168's pending-output fanout cap is a different query alphabet.

Stop if a matching planner or correction appears, or if no useful checked
artifact is ready by the verification deadline. At most one pivot, with the
original clock unchanged. Recheck overlap at first result and before submission.

## Result and release

Completed with [PR1199](https://github.com/CrocSwap/integer-mult-bounds/pull/1199).
Five nonzero readers admit one restoration instead of five. An observation after
child two removes the saving. The package supplies a written criterion and
restricted optimum, the cut planner, the exact complete-node accounting model,
and an independent literal-column enumeration of 19,167 partitions across 3,011
declared batches. The retained PR1155 certificate also reproduces unchanged.
No new kappa, adopted supplier or runtime improvement is claimed.

Verification and handoff started by 19:52:45 UTC. All relevant checks in
VALIDATION.md pass. Final overlap at 19:56:39 UTC covered 808 open PRs through
1196 and all active discussions; no matching correction or planner appeared.
Upstream main was freshly fetched again and remained
`1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`, the original investigation base.
No pivot. This scope is complete; do not rerun it as a new experiment.
