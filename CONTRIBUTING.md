# Contributing and independent review

This is a research draft. Corrections to the mathematics, implementation,
source attribution, and stated scope are welcome through issues or pull requests.

For a mathematical issue, identify the exact proposition, source label, or
inequality; give a counterexample or the missing implication when possible;
and distinguish numerical validation from an algorithmic proof obligation.
For the current result, start with the
[current maintainer review](docs/research/community-pr279-review.md),
[selected certificate](research/community-pr279-audit/certificate.json), and
[reproduction guide](research/five-stage-gen4-banks/PROOF.md). Earlier notes are historical checkpoints.
Read the [bank proof](research/five-stage-gen4-banks/BANK-PROOF.md)
alongside the construction argument. The [original audit](docs/audit.md) describes the retained upstream assumptions.

For a parameter improvement, supply exact rational choices, the full dependency
argument, and an updated patch against the pinned source. Explain whether the
change stays within the parameter ceiling or changes one of its hypotheses.

Keep `upstream/` unchanged. Edit the generators under `scripts/`, then run:

```sh
make verify
```

Include regenerated certificates and patches in the same change. Run the
selected incremental target, `make gen4-bank-verify`, as well as the checks
affected by your changes. The current proof and bank scheduling supplement are supplied as Markdown;
historical PDF targets belong to their respective checkpoints. Review changes to
claims in the README and note together. Finite tests should address a mathematical
identity or a failure mode, rather than simply restating implementation details.

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

On `integration/community`, `make verify` also covers the imported candidate
chain. See [the integration ledger](docs/research/community-integration.md) for
remaining proof obligations and [the batching guide](docs/research/batched-review.md)
for the changed recursive interface. Preserve the historical checkpoint tests.
Imported CC0 proof sources retain their source-specific license and notice.
