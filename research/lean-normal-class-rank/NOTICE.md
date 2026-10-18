# Attribution

The normal-class argument and all-batch P112 application originate in
DreamingOfClouds' PR #2338, head 82700676e1d42acf98dc1921cb6ef82551620008.
Its exact README and NOTICE are retained under sources/ without editing.
Earlier batch-model work is credited in that source, including alephnan's
PR #1714. PR #2294 and SricharanVagvala's PR #2342 provide narrower two-call
and three-call results; the latter explicitly excludes the all-batch audit.

New Lean proofs, independent finite replay, counterexample controls and writing:
Gareth Davidson (@bitplane), with substantial OpenAI Codex assistance.
The verification wrapper, scoped workflow and fault-test structure adapt our
own PR #2341 (f448ce821ba32001bf1ec13f7088450d2edcd112) and PR #2295 harnesses.
That reuse is engineering reuse, not an independent third-party verification.
No subagents or independent human review were used.

The repository's Apache-2.0 license applies to the new contribution. Lean and
Mathlib dependencies retain their upstream licenses and authorship; downloaded
libraries and toolchains are not vendored in this package.
