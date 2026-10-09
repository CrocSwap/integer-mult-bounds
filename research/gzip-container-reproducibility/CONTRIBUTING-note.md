# Proposed `CONTRIBUTING.md` paragraph

Insertion point: as one new paragraph immediately after the paragraph that ends

> Include regenerated certificates and patches in the same change. Run the
> selected incremental target, `make entrance-bank-verify`, as well as the checks
> affected by your changes. The current proof and bank scheduling supplement are
> supplied as Markdown; historical PDF targets belong to their respective
> checkpoints. Review changes to claims in the README and note together.

and before "New contributions are under the repository's Apache-2.0 license."
The quote is verbatim from `CONTRIBUTING.md` at this branch's base (`main`, tip
`3b6b6689`); the paragraph around it stays unchanged.

## Text to insert

> **Regenerated artifacts and hashes.** When a check regenerates a file, compare
> payloads, not containers: the bytes of a gzip or tar container depend on the writing
> interpreter, zlib and tar build, so a pinned container digest can fail on unchanged
> inputs and can hide a real change behind an environment difference. Decompress before
> comparing (`#194`'s regeneration check does this:
> `old, data = gzip.decompress(old), gzip.decompress(data)`), or pin the payload's digest
> or the mathematical fields instead of the container's. Pinning the sha256 of a
> container that is committed stays fine, because those bytes are fixed in the repository
> and no check regenerates them. If a submission records a container digest, it should
> label it as an environment receipt, record the interpreter and zlib versions beside it,
> and not require it to match across environments.

## Why this paragraph, and not a patch to a specific package

The rule applies to any package that regenerates a container, and at least five merged or
open packages touch it. The one observed failure is #202's canonical check, whose integer
κ and every other leaf reproduce; the fix `#207` already prefers is to check the lift
through `exact_scalar_program_sha256` and the complex profile's fields. A general sentence
in `CONTRIBUTING.md` states the rule once, where a reviewer will meet it before writing
the next such check, instead of being re-litigated per package. The audit, its evidence
and the scanner that reproduces it are in
`research/gzip-container-reproducibility/`.
