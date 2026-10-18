# Contributing and independent review

**For donated inference or an open-ended “contribute” task, start with
[autoresearch.md](autoresearch.md).** It provides weighted task suggestions,
semantic overlap checks and bounded stopping criteria. Follow explicit user
assignments instead of drawing a new task. The root [AGENTS.md](AGENTS.md) also
points agents there. Existing external donation prompts should use this
repository-owned guidance for current priorities.

Before substantial research, check the
[discussion board](https://github.com/CrocSwap/integer-mult-bounds/discussions)
alongside open PRs. The [start-here post](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163)
explains claims and updates; use [handoffs](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166)
for concrete requests and [mechanism proposals](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167)
for early ideas. Existing discussion claims are advisory, and findings remain
provisional until their evidence is checked.

New research packages should include **Open next questions**, with relevance,
a feasible first step and blockers. Use the optional
[package generator and replay manifest](docs/research/research-package-guide.md)
to reduce packaging work. Keep frozen predecessor packages unchanged. A focused
finding or handoff is also a valid session outcome; a PR is not mandatory.

The standard donation prompt in autoresearch.md authorizes routine Discussion
posts and opening focused PRs without repeated permission checks. Respect narrower
donor instructions. Optional workflow feedback belongs in the PR or the
[feedback discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200).


For maintainer queue work, start with the [delta-only intake procedure](docs/research/pr-intake.md)
and persistent scheduling cache. Do not repeat unchanged blocked reviews.

Before reviewing an existing PR, consult the [central review ledger](docs/research/pr-ledger.md).
Record the reviewed commit and its evidence separately from publication and GitHub closure.
Recheck the current head before closing incorporated work, link its retained source and attribution,
and leave partial or changed submissions open with the remaining question recorded. Research notes
and verification tools can merit integration even when they do not improve the selected bound.

Maintainers distinguish **archival intake** from **validated incorporation**.
New isolated research packages may be merged after source/integrity intake while
remaining `partially_reviewed` in the ledger, with the unverified obligations
preserved. Such a merge retains the contribution; it does not verify a theorem,
certify a new κ, or change the selected result. Shared-code changes and known
correctness objections remain in substantive review. See the
[archive policy and exact-head index](docs/research/research-archive-intake.md).

This is a research draft. Corrections to the mathematics, implementation,
source attribution, and stated scope are welcome through issues or pull requests.

For a mathematical issue, identify the exact proposition, source label, or
inequality; give a counterexample or the missing implication when possible;
and distinguish numerical validation from an algorithmic proof obligation.
For the current result, start with the
[current status](docs/research/current-status.md),
[selected record](certificates/selected-result.json), and the maintainer review
at that record's `review` path.
The selected record and review identify the actual supplier sources,
reproduction command, evidence and remaining assumptions. Earlier construction
notes are historical checkpoints, even when their text calls a result current.
The [original audit](docs/audit.md) describes the retained upstream assumptions.

For a parameter improvement, supply exact rational choices, the full dependency
argument, and an updated patch against the pinned source. Explain whether the
change stays within the parameter ceiling or changes one of its hypotheses.

Keep `upstream/`, frozen source archives and pinned evidence unchanged. When
changing generated artifacts, edit their generators and include the regenerated
certificates and patches in the same change. Run the checks affected by your
changes; do not launch every historical replay for an unrelated contribution.
Changes to the selected construction also need its applicable complete cold
replay: use the `reproduce` command in the selected record rather than copying a
target from a historical note. Source-bound reuse must preserve explicit coverage
and invalidation. Run artifact-regenerating suites in isolated worktrees.
The historical `make gen4-bank-verify` target checks the earlier generation,
not the selected frontier. The proof and bank scheduling supplements are supplied as Markdown;
historical PDF targets belong to their respective checkpoints. Review changes to
claims in the README and note together. Finite tests should address a mathematical
identity or a failure mode, rather than simply restating implementation details.

**Regenerated artifacts and hashes.** When verification regenerates a compressed artifact, compare its decompressed payload (or a documented canonical representation of every proof-relevant field). Compression headers and streams can differ across Python, zlib and tar versions. Keep exact hashes for committed source archives and other immutable inputs; a regenerated container hash may be recorded with environment details but should not determine mathematical equality across environments. See the [community reproducibility audit](research/gzip-container-reproducibility/README.md) by Maxime Fleury, following Antoine Olivier’s independent replay findings.

New contributions are under the repository's Apache-2.0 license. Retain source
attribution and disclose substantial AI assistance. Do not describe certificate
success as a formal verification of the full multiplication theorem.

Before building on pending work, consult the [contribution-review index](docs/research/contribution-review.md), pin its sources, and preserve contributor attribution.

Parallel approaches, small improvements, independent reproductions, review and
well-scoped negative results are welcome. Please identify predecessor work and
explain what your submission adds, even if a concurrent result has a stronger
headline. We preserve credit for useful contributions that are superseded or not
imported; see [CONTRIBUTORS.md](CONTRIBUTORS.md). Attribution corrections are
welcome too. State which proof obligations remain open rather than presenting
finite certificate checks as a complete theorem audit.

The historical `integration/community` workflow used `make verify` for its
imported candidate chain; it is not the current selected cold replay. See
[the integration ledger](docs/research/community-integration.md) for that history
and [the batching guide](docs/research/batched-review.md) for the changed recursive
interface. Preserve the historical checkpoint tests.
Imported CC0 proof sources retain their source-specific license and notice.
