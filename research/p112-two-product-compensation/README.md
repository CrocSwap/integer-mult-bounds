# Sharp COPY64 floor for the P112 (4,6) rectangle family

**Scoped negative result; no new kappa.** On the fixed P112 coordinate pair
(4,6), arbitrary GL(3,C) mixing of two coordinate terms and one nonzero free
rectangle cannot lower the complete separate COPY sum below **64**, or lower
its separate power bill at unchanged width and normalization.

The new argument closes the **exactly-two projected-product branch** left
open by Cinna Davis's [PR1373](https://github.com/CrocSwap/integer-mult-bounds/pull/1373).
It uses the compensation term's COPY rank to bound its support. Rank at most
one permits at most three support rows; those deletions cannot reduce the
other terms' ranks. Larger compensation rank already pays for possible
losses. Omitting that term in an explicit fixture falsely reports **63**,
while the actual bill is **70**.

The three-product argument belongs to PR1373. Both implementations here
recheck its finite premise before combining it with the new branch. The
result covers arbitrary nonzero free rectangles for this one coordinate
pair, including rank-nine masked completions. Identity mixing attains 64.
The exact statement, complete coefficient reduction and power inequality are
in [PROOF.md](PROOF.md); executed commands and validation limits are in
[VALIDATION.json](VALIDATION.json).

## Reproduce

From the repository root, using Python 3.12 and only its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p112-two-product-compensation
```

Expected final line:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/p112-two-product-compensation outcome=negative-result
```

The hook authenticates the base/source pins, runs both checkers and runs three
CLI corruption/export test groups. Direct
commands work with Python 3.10+ and preserve checks under optimized execution:

```sh
python3 -I -O -B research/p112-two-product-compensation/verify.py
python3 -I -O -B research/p112-two-product-compensation/independent_check.py
```

Default replay is read-only. To create a fresh certificate without overwriting
an existing file, use `verify.py --write /tmp/p112-compensation-new.json`.
Use `--check PATH` to check a different certificate. All fields must match.

## Evidence and boundaries

[CERTIFICATE.json](CERTIFICATE.json) records all five complex support strata,
2,555 character evaluations, 2,800 one-sided survivor ranks, and 145,600
credited three-product records. It includes eight exact Gaussian-rational
matrix fixtures covering 100,352 entries, eight semantic negative controls,
the complete compensation bill and a rational concavity witness.
The registered corruption controls also reject altered finite receipts, an
altered compensation invoice, modified source bytes and modified blob pins;
a minimal relocated export passes with assertions disabled.

The primary checker constructs Euclidean E8 roots and uses 112-bit binary
rows. The separate checker uses the pinned nine-bit labels, a bilinear-image
calculation and a different elimination order. Their complete finite receipts
agree, including every histogram and ordered transcript hash. The separate
checker also verifies five sharp erasure boundaries and an affine-coordinate
omission control. Both implementations are from the same AI-assisted author;
this is code/method independence, not independent human review.

This is finite exact evidence plus a written proof for all coefficients in
the stated family. It is not a finite search promoted to a universal decoder
theorem. Other pairs, three or more mixed coordinates, multiple rectangles,
arbitrary nine-term factorizations, zero-factor families, other geometries,
shared copies and changed normalization remain outside scope.

All additional preparation, source access, mixing, frame changes,
restoration, hosting and recursive-child expenses are optimistically free
for the separate COPY rejection screen. No complete supplier or improved
recursive moment is constructed. Physical interpretation retains the
separate-total/drop-free copy-tree assumptions; the selected construction's
all-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape, analytic and bit H1-H5 obligations remain untouched.

## Sources, overlap and credit

Exact base: `cd91ac8e2652bfee6bf09da3b8724253bcf78f5f`.
The selected conditional result at that base is PR1094,
`kappa = 836330098538459/500000000000000000`, with PR589 on PR555 for bits.
Its actual construction and maintainer review were read; no selected cold
replay, native supplier admission or hosted CI is claimed for this package.

[SOURCES.json](SOURCES.json) pins the live geometry and notices by Git blob
and SHA256, plus the originating catalogue and selected record as historical
provenance. [TASK.json](TASK.json) records the OS seed **46**, three candidate
tasks, local claim, bounded coverage and overlap distinctions. No pinned
sprint issue existed, so the claim was recorded locally.

- **Cinna Davis, PR1373**, head `3eaef3e4427068b33847dc1147c8a2e5709a970e`:
  same pair, three-active-product theorem, and explicit remaining two-product
  question. The new branch is the contribution; neither the same seed nor
  replaying the predecessor is claimed as novelty.
- **Arham Tahir, PR1331**, head `f08b698cc2bd74e2425486728a008e531fc35f0e`:
  one-coordinate rectangle obstruction and survivor-containment method.
- **@commdata2338, PR1375**, head `4a533aff2a7a87c9b36e077a31774b332a7f64bd`:
  all-pair small-rectangle result and erasure distances. This package handles
  unbounded rectangle support on (4,6) through compensation accounting.
- **Hanson Sun / @bbMisk, concurrent [PR1432](https://github.com/CrocSwap/integer-mult-bounds/pull/1432)**,
  head `4bcc49e3f4041018b0607da46a87d8928a6e0fd0`: fixed 24-row support on
  (0,1), arbitrary amplitudes including zero factors. That result is not a
  dependency. The reported (7,8,7) compensation pattern is independently
  corroborated here on (4,6); this package removes the support-size cap for
  nonzero rectangles on that pair through a different support-rank argument.
- **Mihir Srivastava, PR845**, and **DreamingOfClouds, PR717/446**:
  exact geometry snapshot, binary labels, masked model and physical COPY
  convention. **Joel Pulikkan / GamingPuzzled, PR620**: coordinate COPY64
  construction. The pinned PR845 and PR717 notices retain their wider
  predecessor and AI-assistance attribution.

Prepared for **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex**
assistance in mathematics, implementation, checking and writing. New work is
Apache-2.0.

## Open next questions

Can three or more original coordinate terms mixed with one free rectangle
reduce the complete COPY power bill? This changes a remaining restriction of
the theorem. The first useful step is a minimal-active-product normal form
and a compensation-support bound before physical synthesis. New projective
support classes and simultaneous survivor-rank bounds are the blockers;
this package does not predict a gain. See the structured question in TASK.json.
