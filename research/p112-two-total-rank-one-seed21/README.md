# Two extra P112 totals need independent, overlapping coordinate lifts

**Scoped negative result; no new kappa.** In an exact ten-term P112 decoder
retaining the eight coordinate readers, adding two totals cannot lower the
pairing-rank copy cost below **64** if either added matrix has rank at most
one, if either added reader leaves the coordinate column space, or if the
two coordinate coefficient supports are disjoint.

Consequently any improvement in this model must have both added matrices
of rank two, both added readers inside `col_C(X)`, and **overlapping**
coefficient supports. The full coupled case with arbitrary source columns remains unresolved
by this package. The result
closes off-column cancellation and independent batching as ways around
Mihir Srivastava's #845 / @woklerx's #998 single-lift floor; it does not
claim a floor for every ten-term decoder.

The [proof](PROOF.md) gives two generalizations for any number `k` of
added totals: quotient rank `rank([X D])-8 >= k-1` forces source rank at
most one, and pairwise disjoint coefficient supports cannot help even
with independent sources. These are written complex-parameter arguments,
not conclusions drawn from finite search.

## Reproduce

From the repository root, Python 3.10+ and the standard library:

```sh
python3 -I -S -B research/p112-two-total-rank-one-seed21/test_package.py
```

Expected final status:

```text
PASS_P112_TWO_TOTAL_PACKAGE controls=8 identities=1180
```

This read-only command checks pinned inputs, replays both retained #845
checkers and #998's primary/independent checks, reproduces the new primary
and independent receipts, and runs optimized, mutation and relocation
controls. On the recorded macOS host the recorded run took 43 seconds;
actual timing is in [VALIDATION.json](VALIDATION.json).

For a quick new-result replay without the predecessor census:

```sh
python3 -I -S -B research/p112-two-total-rank-one-seed21/verify.py
python3 -I -S -B research/p112-two-total-rank-one-seed21/independent_check.py
```

The main marker reports **15 examples, nine mathematical controls**, and
`coupled_rank_two=open`. The independent checker emits deterministic JSON,
compared in full to `INDEPENDENT.json` by the package command. The main
certificate can be regenerated with `verify.py --write /new/file.json`;
existing outputs are not overwritten. `--check PATH` compares every field.

## Exact model and useful boundary

Write `X` for the pinned real `112 x 8` coordinate matrix. The identity is

```text
XX^T = XT^T + DZ^T,
D,Z have two columns; transpose is algebraic, without conjugation.
```

Cost is the sum of the binary label-pairing ranks of the ten reader/source
support rectangles. In the remaining case, `D=XA` uniquely and
`T=X-ZA^T`; both `A` and `Z` must have rank two. Arbitrary complex values
and zero terms are included in the theorem.

Mixing the two added terms by an invertible basis change preserves the
matrix identity but need not preserve this cost. An exact fixture retires
two coordinates with cost **64**; the sum/difference basis of those same
two terms costs **66**. Thus normalizing `A` by arbitrary column mixing
cannot be treated as free when searching the remaining case.

## Evidence and limits

- Primary: 15 full P112 identities, exact Gaussian-rational rank by rational
  realification, literal restricted binary-pairing ranks, rank-one
  contractions, disjoint complex lifts, and boundary examples at `k=3,4`.
- Independent: no primary or predecessor Python imports; pinned geometry
  JSON, rational column elimination, set-based binary elimination, **1,180
  full matrix identities** including **322 transposes** and **476 component
  identities**. All 28 coordinate pairs and all 210 unordered disjoint
  two-plus-two support partitions are completed. Dense overlapping controls
  are explicitly outside the proved reductions.
- Mathematical controls include source perturbation, omitted terms,
  conjugate transpose, improper rank-one contraction, non-free basis
  change, and a `k=3,q=1` exact example showing that one off-column reader
  alone does not force source rank one for three totals.
- Packaging controls reject four changed receipt fields and source drift,
  preserve existing output, reproduce identical certificate bytes, and run
  in a minimal offline tree whose path contains spaces. Guards survive `-O`.

The finite examples exercise the proof boundaries. They are not an
exhaustive complex-parameter search, a formal proof, or independent human
review. The uniform statements depend on the inherited #845/#998 theorem;
its finite premises are replayed and source-bound, not claimed as new work.

Before physical synthesis, all extra preparation, source access, frames,
restoration, hosting and recursive-child work are optimistically granted
zero cost. Even that relaxation cannot lower the copy-rank **sum** in the
covered classes, so no physical implementation is pursued. Rank distribution
at the same sum and other cost components may still improve the recursive
moment. This is not a complete moment or runtime obstruction.

The physical interpretation retains DreamingOfClouds' #446 separate-total,
drop-free gathering/copy-tree assumptions. Masked equality, changed retained
readers, other geometries, interacting delivery programs and the coupled
rank-two case remain outside scope. All-size/compiler, mutable-source,
hosting, precision/tape, analytic-transfer and bit H1-H5 obligations are
unchanged. No selected supplier, native admission, full cold replay, Lean
multiplication theorem, hosted CI result or new exponent is claimed.

## Provenance and overlap

Base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`; OS assignment seed **21**,
complex-supplier track. The selected result at this base is Rohan Arun's
#1094, conditional kappa **0.001672660197076918**, with PR589/PR555 on the
bit side. Its selected record, source inventory, assembly and maintainer
review were followed; they are context, not runtime inputs for this result.

[SOURCES.json](SOURCES.json) records immutable SHA-256 and Git-blob pins for
the full two predecessor packages. #845 head is
`125ce25bdae421627b56077adc14940c2d0aa52f`; #998 head is
`66b777bf2b0160ed926572ff8714ac7b7bba0859`. Both are incorporated in the base
review ledger. #1133's pending rational descent extends #998 in the scalar
field, while this result changes the number of added totals. #968/#1077
concern exactly eight terms with changed readers; #1098 verifies a
predecessor geometry premise. No pending code is imported.

At the final overlap check, @woklerx's **#1180**, head
`75b408646d558147a4eb250fc407d1fbfcb8df4e`, had appeared. Its written theorem
covers arbitrary term counts and punctures, but requires **both** factor
matrices to lie in the live root code. Within our `D=XA` subcase, the scopes overlap when
`Z` also lies in `col(X)` (and hence so does `T`). Our distinct coverage permits arbitrary source
columns outside that space, off-column canceling readers, and disjoint lifts
with independent outside sources. In `CERTIFICATE.json`, the disjoint complex
fixtures have `source_quotient_rank=2` and `1` respectively; #1180's hypothesis
therefore does not apply. Conversely our theorem retains eight coordinate
readers and does not subsume #1180's variable-reader result. This is a scoped
comparison of its pinned proof, not a complete independent acceptance of
#1180 or an imported dependency. Its factor-linear subcase is not claimed
as an unanswered research question here.

[CLAIM.md](CLAIM.md) records the three candidate tasks, assignment,
zero-extra-cost screen, coordination check and stopping rule.
[VALIDATION.json](VALIDATION.json) records final overlap and executed checks.
Only this new research package changes; `upstream/`, the selected frontier,
source archives and predecessor evidence remain unchanged.

Prepared by **Philipp / @mightyOil**, with substantial **OpenAI Codex**
assistance in analysis, proof, code, independent AI checks and writing.
See [NOTICE.md](NOTICE.md) for predecessor credit. Apache-2.0.
