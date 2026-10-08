# Contributing and independent review

This is a research draft. Corrections to the mathematics, implementation,
source attribution, and stated scope are welcome through issues or pull requests.

For a mathematical issue, identify the exact proposition, source label, or
inequality; give a counterexample or the missing implication when possible;
and distinguish numerical validation from an algorithmic proof obligation.
For the current result, start with the
[batched-recursion review guide](docs/research/batched-review.md).
The [original audit](docs/audit.md) describes the retained upstream assumptions.

For a parameter improvement, supply exact rational choices, the full dependency
argument, and an updated patch against the pinned source. Explain whether the
change stays within the parameter ceiling or changes one of its hypotheses.

Keep `upstream/` unchanged. Edit the generators under `scripts/`, then run:

```sh
make verify
```

Include regenerated certificates and patches in the same change. If the note
changes, also run its corresponding PDF target (`make batched-note` for the
current result) and include the updated PDF. Review changes to
claims in the README and note together. Finite tests should address a mathematical
identity or a failure mode, rather than simply restating implementation details.

New contributions are under the repository's Apache-2.0 license. Retain source
attribution and disclose substantial AI assistance. Do not describe certificate
success as a formal verification of the full multiplication theorem.
