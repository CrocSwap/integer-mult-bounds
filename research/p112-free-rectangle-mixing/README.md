# P112: one free rectangular correction cannot improve one coordinate COPY

**Scoped obstruction; no new kappa or physical supplier.** Start with the
standard P112 coordinate decoder of COPY cost 64. Add any complex rank-one
correction whose support rectangle has zero binary label pairing, then apply
any invertible complex two-term basis change mixing that correction with
**one** of the eight original coordinate terms. The replacement costs at least
eight, so the whole decoder still costs at least **64**. Identity mixing is
sharp, including a genuinely rank-nine masked decoder.

The correction is unconstrained on odd entries and zero on every even entry;
its supports and coefficients are arbitrary. This changes the all-pairs,
eight-term premise. It is a bounded subfamily of the masked rank-nine problem,
not a conclusion about arbitrary rank-nine decoders. See [PROOF.md](PROOF.md)
for the quantified argument over C with ordinary transpose.

The proof separates triangular changes, dense changes and zero outer products.
For a nonzero correction and two active original-coordinate products, each
replacement has pairing rank at least six; their sum is at least twelve
(not asserted sharp). The finite geometric premises are deliberately weaker
than an initial tempting argument: all 896 relevant affine slices have span
**seven**, and 53,760 of their 100,352 cross pairings have rank **six**.
The remaining 46,592 cross pairings have rank seven.

For a separate COPY bill with ranks `r1,r2`, the theorem implies
`r1^(1-a)+r2^(1-a) >= 8^(1-a)` for `0<=a<1`. With unchanged width,
normalization and common multiplicity, this replacement cannot improve that
COPY contribution even granting all additional work zero expense. This
conditional screen does not determine a complete supplier histogram or price
a changed hosting/owner layout. It does not justify a kappa or runtime claim.

## Reproduce

Python 3.10+ and the standard library suffice for the direct checks, from the
repository root:

```sh
python3 -I -B research/p112-free-rectangle-mixing/verify.py
python3 -I -B research/p112-free-rectangle-mixing/independent_check.py
```

Expected final lines:

```text
PASS_P112_FREE_RECTANGLE_MIXING slices=896 cross_pairs=100352 fixtures=8 controls=9 copy_floor=64 no_new_kappa
PASS_P112_FREE_RECTANGLE_INDEPENDENT slices=896 cross_pairs=100352 basis_rows=6272 controls=6
```

The registered Python 3.12 replay also checks historical task provenance and
working source bindings:

```sh
python3.12 scripts/research_package.py --package research/p112-free-rectangle-mixing
```

To regenerate the deterministic receipt explicitly without replacing it during
ordinary verification:

```sh
python3 -I -B research/p112-free-rectangle-mixing/verify.py --write /tmp/p112-free-rectangle.json
```

The primary implementation constructs Euclidean roots independently and binds
every coordinate/support and all 12,544 pairings to the pinned PR845/PR717 model.
It records 896 seven-row bases, computes every ordered cross pairing, and
checks eight exact Q(i) factor-change fixtures on all 12,544 entries each.
Fixtures include an odd singleton giving rank nine, dense complex mixing,
substantial support cancellation, triangular/antitriangular changes, and a
degenerate dense boundary that rules out incorrectly applying the twelve bound.
Nine semantic/source controls reject weakened conditions and false premises.

The separately implemented finite-premise replay imports no primary checker.
It uses explicit nine-bit labels from the pinned predecessor and reduces from
the opposite end of the bit vector. It checks every stored basis and support,
independently recounts all cross pairings, and rejects six corrupted receipts.
This is a separate implementation by the same AI-assisted author, not human
review. Both finite checks support the written proof; no proof assistant is used.

## Scope, accounting and remaining obligations

Exactly one original costly term and one zero-pairing rank-one correction are
mixed. The other seven terms are fixed. The theorem includes arbitrary complex
coefficients, arbitrary zero rectangles, proper sub-supports, and zero vectors.
It does not cover several free corrections, coupled mixing of multiple original
terms, different punctures, or shared-copy accounting. A succession of changes
can leave this family, so this is not a global local-search barrier.

No coefficient preparation, gathering, physical word, frame/owner admission,
restoration schedule or complete native moment is constructed. The physical
interpretation retains the separate-term label-pairing cost convention; it
does not prove its implementation contract. All-size/compiler, common-label
and mutable-source realization, hosting, precision/tape, analytic transfer and
the selected bit H1-H5 obligations remain inherited. The selected cold replay
is unrelated and was not run. Hosted CI and independent human review are
separate obligations.

## Task, overlap and credit

Base `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` was fetched from current main.
Chooser nonce `4db6ec8657b781ead81a5f0b421eff29` selected complex mechanisms;
card `complex-masked-decoder` is refined to the single-coordinate/one-free-
rectangle GL(2,C) family. [TASK.json](TASK.json) records the scope, bounded stop
rule, exact overlap heads and structured follow-up. The public claim is
[Discussion 1316](https://github.com/CrocSwap/integer-mult-bounds/discussions/1316).

The entry overlap check completely paginated 804 open PRs and 56 discussion
records. Pending PR1180/1191 concern root-linear factors; PR1212/1213 concern
rank-eight masked solutions; PR1224 concerns nine-term **all-pairs** decoders;
PR1236 concerns exact root-star/trimmed-star support envelopes. This family
permits rank-nine masked solutions and non-star arbitrary correction supports,
but only one original costly term is mixed. None of those pending theorems is
used as a proof premise. Overlap checks search bodies and local package notes,
not every code diff, and do not certify novelty. Final coverage is recorded in
TASK.json.

Credit DreamingOfClouds / PR717 for the B14 model, E-graph mask and mixed-rank
question, PR446/595 for the separate-total/format lineage, Joel Pulikkan /
GamingPuzzled / PR620 for the cost64 coordinate decoder, Mihir Srivastava /
PR845 for the pinned exact P112 geometry, and themilkman216 / PR968 for the
pairing-cost definition and geometric predecessor. PR1077's exact
complex-coefficient replay was the task card's positive control. All predecessor
files, frozen inputs and the selected frontier remain unchanged. Sources retain
Apache-2.0; this package is Apache-2.0.

Prepared by Arham Tahir (@Arham-Tahir64) with substantial OpenAI Codex assistance
in mathematics, implementation, verification and writing. Exact validation
commands and environments are in [VALIDATION.md](VALIDATION.md).

## Open next questions

Can one free rectangle mixed coherently with **two or more** original coordinate
terms lower the complete COPY moment? This enlarges the bounded family where a
masked escape could occur. First fix two coordinate columns and one explicit
zero-pairing rectangle, then partition GL(3,C) by exact cancellation ratios and
price every actual support. The present triangular/dense proof does not handle
that coupled change. Any algebraic improvement would still need fully charged
gathering, frame, restoration, hosting and precision costs before supplier
admission. The question is a proposed next experiment, not a feasibility claim.
