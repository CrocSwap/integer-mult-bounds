# Contributing and independent review

Before reviewing an existing PR, consult the [central review ledger](docs/research/pr-ledger.md).
Record the reviewed commit and its evidence separately from publication and GitHub closure.
Recheck the current head before closing incorporated work, link its retained source and attribution,
and leave partial or changed submissions open with the remaining question recorded. Research notes
and verification tools can merit integration even when they do not improve the selected bound.

This is a research draft. Corrections to the mathematics, implementation,
source attribution, and stated scope are welcome through issues or pull requests.

For a mathematical issue, identify the exact proposition, source label, or
inequality; give a counterexample or the missing implication when possible;
and distinguish numerical validation from an algorithmic proof obligation.
For the current result, start with the
[current status](docs/research/current-status.md),
[selected record](certificates/selected-result.json), and
[current maintainer review](docs/research/community-frontier741-review.md).
The selected record and review identify the actual supplier sources,
reproduction command, evidence and remaining assumptions. Earlier construction
notes are historical checkpoints, even when their text calls a result current.
The [original audit](docs/audit.md) describes the retained upstream assumptions.

For a parameter improvement, supply exact rational choices, the full dependency
argument, and an updated patch against the pinned source. Explain whether the
change stays within the parameter ceiling or changes one of its hypotheses.

Keep `upstream/` unchanged. Edit the generators under `scripts/`, then run:

```sh
make verify
```

Include regenerated certificates and patches in the same change. Run the
checks affected by your changes. Changes to the selected construction should
also run its cold replay, currently `make frontier741-verify`; consult
[current status](docs/research/current-status.md) for later selected targets.
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

On `integration/community`, `make verify` also covers the imported candidate
chain. See [the integration ledger](docs/research/community-integration.md) for
remaining proof obligations and [the batching guide](docs/research/batched-review.md)
for the changed recursive interface. Preserve the historical checkpoint tests.
Imported CC0 proof sources retain their source-specific license and notice.
