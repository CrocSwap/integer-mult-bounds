# Two added routes do not save a still-rejected dirty one-move word

**Exhaustive finite census. No new κ.** The selected conditional exponent stays
`363005817/100000000000` (`0.00363005817`) in
[certificates/selected-result.json](../../certificates/selected-result.json).
This package does not change that record.

On the emitted local word of
[PR #5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708),
[#6923](https://github.com/CrocSwap/integer-mult-bounds/pull/6923)
classifies 686,779 length-at-least-5 one-move assignments as dirty failures.
Open [#7074](https://github.com/CrocSwap/integer-mult-bounds/pull/7074)
inserts one route at the first missing edge. This package recomputes that
domain: 686,386 assignments still miss a different edge, and the first-edge
multiplicity table has the same SHA-256
`8f38eb2f6e526ede87a62c1fc88c35fd5d3ba87a16f755df690a76cea5a68494`.
Each of those 686,386 words is replayed with that second missing edge inserted
as well. Both inserted edges have rank 1. None is a strict saving on `(0, 1)`.
The argument is in [PROOF.md](PROOF.md).

## Task and overlap

Base `e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. Card
`bit-helper-contract`, scope **refined**. This is open question 1 of #7074.
[#6923](https://github.com/CrocSwap/integer-mult-bounds/pull/6923) is the
merged one-move census. [#6963](https://github.com/CrocSwap/integer-mult-bounds/pull/6963)
settled two moved corrections on length 5, and
[#7079](https://github.com/CrocSwap/integer-mult-bounds/pull/7079) is the
two-move length-6 census. Those packages hold the published route table fixed
and move corrections. This package adds a second route on a dirty one-move
failure. It does not rerun those screens, and it does not move a second
correction. No open PR answers this two-edge question. The family expansion
gate is unchanged: a local moment obstruction is not a new construction round.

## Census

Assignments are ordered by `(interval start, interval end, correction index,
moved frame)`. The lexicographically first still-rejected word is scalar
positions 1,003–8,891, length 12. The outer gate is `ADD(583, 60)`. Correction
0, `ADD(583, 87)`, moves from frame 1 to frame 326. After the first route
`(326, 1)` is added, the rejecting edge is `(591, 553)`. Both hops pay, three
times and once. With both edges present at rank 1, and again at rank 7, the
independent histogram still misses `(467, 396)`.

| Class | Assignments | Outcome |
|---|---:|---|
| A third edge is still missing | 673,425 | no paid histogram |
| Emitted, strict loss by rank split | 12,953 | not a saving |
| Emitted, strict loss by the elementary rewrite | 5 | not a saving |
| Emitted, positive at `t = 1/2` and negative at `t = 4/5` | 3 | not a saving |
| Strict saving | 0 | — |
| Total still-rejected words | 686,386 | no saving |

The same absence holds for every rank pair in `1..7`. A missing third edge is
missing at every such rank. On an emission, raising either inserted edge's
rank adds a nonnegative term `u (r^t − 1)` to the rank-1 moment, so a moment
that fails to be strictly negative stays that way.

The three sign-changing words have rank-1 shape `H1 + 3 H2 − H4 − H5`, with
one paying use of each added edge. They are not strict losses either. The
lexicographically first is scalar positions 5,661–7,047, length 17, correction
8, `ADD(179, 6)` moved from frame 593 to frame 360, outer gate `ADD(52, 6)`.
Its inserted edges are `(360, 358)` and `(360, 131)`. This is not the #6923
repair on the same interval, which moves that correction to frame 358.

## Reproduce

Python 3.12 and the standard library, from the repository root. The census
finishes in about two minutes here.

```sh
python3 -I -B research/g20-dirty-second-edge/verify.py
python3 -I -O -B research/g20-dirty-second-edge/verify.py
python3 -B scripts/research_package.py --package research/g20-dirty-second-edge
```

The direct verifier prints

```text
PASS_G20_DIRTY_SECOND_EDGE still=686386 third_missing=673425 split_loss=12953 elementary_loss=5 sign_change=3 savings=0 witness=1003-8891/0/326/326-1/591-553/third=467-396 no_new_kappa=true
```

Checks raise exceptions, so `-O` does not disable them. Not run: the #5708
integration replay, the 18-call caller, adjoint columns, moduli 101 and
10201, ordinary admission, Lean, Docker, and `make frontier7000-verify`.

## Open next questions

1. Does adding the third missing edge as well turn one of the 673,425
   still-rejected words into a strict saving? Two routes still leave those
   words short of an emission. The first step is the same lexicographically
   first word: its third missing edge is `(467, 396)`, and the replay puts
   all three edges at rank 1. The blocker is that this package inserts only
   the first two missing edges.

## Credit

The emitted word, route table, A2 relation, and the local-only conjugation
count are Ali Romman's `research/g20-conjugation-admission`, following
Dugongue, ai-nanachi, and the retained G20 lineage named there. The
length-4-and-above contact-frame obstruction is Nick Petalas's #6305. The
two-move classification at lengths 2..4 is Nick Petalas's #6664. The
length-1..3 one-move obstruction is unpaidmoon's #6337. The length-4 one-move
obstruction is unpaidmoon's #6633. The length-at-least-5 one-move obstruction,
including the dirty-failure count and the classifier replayed here, is
unpaidmoon's #6923. The length-5 two-move census is unpaidmoon's #6963. The
one-added-route census, including the 686,386 still-rejected words and the
first-edge table checked here, is unpaidmoon's #7074. The strict-loss splitting
inequality is the same elementary estimate used in those censuses.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
