# Five-source parity-hyperplane connector schedules

**Exact structured-family construction; no new kappa.** For the fixed binary
dirty connector alphabet, every five-source affine parity-hyperplane output
family has an exact minimum complete query count. The 62 families fall into
ten source-coordinate symmetry classes. Their minima are 38, 40, 42, or 44
queries; only the odd-weight family needs 44 because no restored ten-toggle
source walk covers all sixteen odd masks.

This refines the open subset question left by the five-source all-mask result
in [PR934's universal connector package](../universal-connector-boundary/README.md).
It keeps that package's binary source/readout alphabet and changes the output
matrix to a structured parity family. The ten-toggle evidence is an exact
enumeration of 945 canonical restored source words, followed by explicit
boundary-pair constructions for all requested rows. This is a new restricted
family construction and its exceptional obstruction; it is not an audit or
an extension of the operation alphabet.

## Reproduce

With Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/five-source-parity-hyperplanes-seed595e
```

The registered replay checks source pins, regenerates the certificate, and
uses a second pairing-based enumerator plus exhaustive scalar dirty-state
replay. Direct commands work with the available Python 3.14 runtime:

```sh
python3 -I -B research/five-source-parity-hyperplanes-seed595e/verify.py
python3 -I -B research/five-source-parity-hyperplanes-seed595e/independent_check.py
```

Expected final lines:

```text
PASS_FIVE_SOURCE_PARITY_HYPERPLANES families=62 symmetry_classes=10 minima=38,40,42,44 ten_words=945 scalar_dirty_checks=246016
PASS_INDEPENDENT_PARITY_HYPERPLANE_CHECK pairings=945 odd_max=15 plans=62 dirty_states=246016
```

## Result and evidence

[PROOF.md](PROOF.md) gives the exact query minima and the prefix-difference
identity. [CERTIFICATE.json](CERTIFICATE.json) records the 945-word census,
ten representative constructions, all 62 source walks and output-boundary
pairs, and the complete dirty scalar checks. The independent checker uses a
recursive matching enumeration rather than the restricted-growth generator
used by `analyze.py`.

All five source maps and every output map are treated as arbitrary fixed
linear maps; each is one unit-cost complete call in this bounded model. The
query count charges every source/readout call and its fixed-width query
record/dispatch. The dirty connector and target rows are never assumed clean.
The certificate's scalar replay checks all source products, initial
connector bits, output coefficients and target bits for each row. The proof
establishes the identity for arbitrary dimensions and maps.

## Selected bound context

The selected record at exact base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea` is unchanged, SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
It selects conditional \(\kappa=836330098538459/500000000000000000\) with
the review in
[community-batch1099-review.md](../../docs/research/community-batch1099-review.md),
certificate [ASSEMBLY.json](../community-frontier1094-audit/ASSEMBLY.json),
source manifest [SELECTED-SOURCE.json](../community-frontier1094-audit/SELECTED-SOURCE.json),
and reproduction command `make frontier1094-verify`. The selected construction
and its bit/complex obligations are unchanged. This abstract interface result
does not instantiate a supplier and gives no new \(\kappa\).

## Overlap, attribution and handoff

The pre-claim refresh at 2026-10-14 10:15:08 UTC completed pagination
for 460 open PRs and 434 Discussions with no exact parity-hyperplane match. A
final pre-submission refresh at 2026-10-14 10:31:21 UTC covered 470 open PRs
and 447 Discussions with no warnings; its only remote match was this task's
claim in Discussion #1163, and its only local match was this package.
The nearest predecessor is Ross Richardson's PR934: its all-mask source-path
criterion leaves restricted output subsets open. PR938 covers one-source
dirty fanout. PR1518 and PR1531 extend the source-call alphabet; Discussion
#1579 studies a common-B all-mask endpoint with unequal readout prices. This
result keeps the alphabet fixed and treats structured subsets with five
heterogeneous source maps.

The selector's centre-path-sharing suggestion was not chosen because of the
active work in Discussion #1516 and PR1708/PR1748. Persistent-boundary work was
not chosen because of current claims and PRs including #1163 and #1776. The
connector-alphabet suggestion was refined because the source-side alphabet
extensions are already crowded. The original claim is in
[Discussion #1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18921524);
the result update is
[here](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18921770).
The focused package is under review in
[PR #1811](https://github.com/CrocSwap/integer-mult-bounds/pull/1811).

Prepared by Cinna Davis with substantial OpenAI Codex assistance in scope
selection, derivation, implementation, checking and writing. This is not
independent human review. Predecessor notices and exact Git blob pins are in
[SOURCES.json](SOURCES.json).

## Open next questions

Can any selected multiplication supplier expose a complete-call interface
whose output masks form one of these parity hyperplanes, with the unit query
price replaced by its actual recursive child profile? The first step is to
derive the exact source/output map inventory for one concrete block and price
all children and local conversions. Until then this result is a bounded
interface construction only; it does not imply a supplier saving or a new
frontier.
