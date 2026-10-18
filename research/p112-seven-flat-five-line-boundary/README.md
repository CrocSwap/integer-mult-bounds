# The five-line boundary of P112 Lemma N

Three explicit independent root directions disprove the five-deletion extension of the retained four-deletion Lemma N. Each direction needs exactly five deletions outside one fixed binary seven-space. The deletion sets differ and have union size eight.

The predecessor's stronger, independently deleted version allows four lines per direction and admits at most two directions. This package supplies an explicit next-integer counterexample. It does not reprove that global four-line bound.

[PROOF.md](PROOF.md) gives the statement, literal flats and field transfer. [WITNESS.json](WITNESS.json) is the complete witness. [RESULT.json](RESULT.json) and [REFERENCE.json](REFERENCE.json) record exact checks.

## Evidence and reproduction

From the repository root, using Python 3.12 or later and only the standard library:

```sh
python3 -B research/p112-seven-flat-five-line-boundary/verify.py
python3 -B research/p112-seven-flat-five-line-boundary/reference.py
python3 -B research/p112-seven-flat-five-line-boundary/test_verify.py
python3 scripts/research_package.py --package research/p112-seven-flat-five-line-boundary
```

The primary verifier reconstructs the pinned geometry and examines all 43,435 seven-spaces for each direction. Its chosen completion is unique within five deletions. A separate lattice/label reconstruction and Gaussian algorithm check all 66,045 four-deletion subsets per direction. Every one leaves rank at least eight; the displayed five deletions leave rank seven. A nonzero rational minor proves independence over every characteristic-zero field. Fifteen behavioral controls include bad cuts, a dependent triple and the false common-five-cut interpretation.

## Scope and correction

The initial investigation targeted historical TWOSIDE profile `2,7^7`. The source audit found that FINITE alpha already excludes it, and OS-CHARGE2 Lemma N already covers four independently chosen deletions. The discarded two-deletion census and that profile are not new contributions. The task changed to the first unproved deletion allowance, five.

This is a boundary result about an existing proof relaxation. It does not refute a common-five-line statement. The three displayed completions need an eight-line common union of binary rank four. It proves no new historical profile exclusion, full C5, decoder floor, supplier or multiplication exponent. The selected frontier is unchanged.

## Sources and credit

DreamingOfClouds' PR3154 at `708f0ad8928c383de8294aea3c126e9461d2066d` retains the four-line Lemma N and its preceding SMALL2/Pencil lineage. [vendor/LEMMA-N.md](vendor/LEMMA-N.md) is a verbatim excerpt of its OS-CHARGE2 note. The source file SHA256 and excerpt boundaries are in [SOURCES.json](SOURCES.json).

The live exact geometry input is Nick Petalas' retained PR3161/PR3162 construction, as preserved in PR3173's package at base `463113d675af7410ac91d53a4fed51ec6494eb9a`. Its original E8/P112 attribution remains intact. The new witness, proof and checks are by Nick Petalas. Apache-2.0. Evidence is author-checked with separately implemented algorithms, not independent human or proof-kernel review.

## Code and verification limits

Both verifiers are read-only, iterative and bounded by fixed domains. All new functions fit within sixty lines. The primary census checks 43,435 spaces three times. The reference checks 66,045 deletion subsets three times and reconstructs roots from a grid of `5^8` points. Registered commands have separate 60/120/60-second timeouts. Invalid inputs propagate a nonzero exit; proof checks do not depend on Python assertions.

Power-of-Ten rule 3 deviation, Python requires dynamic allocation. The scope is these finite verification commands, not a steady-state service. The compensating bound is fixed inventories of 112 labels, 120 root lines, 43,435 masks and at most 66,045 streamed subsets per direction; subsets are not accumulated. Static loop inspection, the complete replay and invalid-input controls verify the bounds. Revisit this choice if the checker becomes a service or accepts variable dimension. There is no claim of allocation-free execution.

Diagnostics use Ruff's error, import, bugbear, modernization, security, comprehension, performance, unnecessary-code and implicit-string checks. Mathematical constants and standalone-script layout do not adopt every optional style/docstring rule from the exploratory all-rules scan. No diagnostics are suppressed. Compilation runs with warnings treated as errors. No global lint configuration or predecessor code is changed.

## Open next questions

Can one common set of five deletions admit three independent directions? That is a different question and cannot be answered by combining the separate deletion sets here. First enumerate all affordable completions for one candidate triple and test a common set. The current triple cannot work within five because each completion is unique and their missing-line union has size eight. A larger census needs its own budget and a named downstream obligation.
