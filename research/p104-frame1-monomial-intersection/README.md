# Frame 1 of the P104 window, and its overlap with the recorded forty

**No new κ.** The selected frontier stays `781451/250000000`. This package hosts
frame 1 of the odd-character P104 window as a product of root-line labels,
charges every monomial of degree at least 2, and intersects that set with the
40 monomials recorded for frame 0. It does not host the other eleven rows and
it does not price a signed profile.

## Result

Frame 1 of the vendored 104-by-13 witness is the odd-graph clique

```text
13, 26, 131, 148, 262, 273, 392, 415.
```

A letter is the pairing of one root line with all 120 root lines. In `F_2` a
product equals 1 only when every factor equals 1, so every factor of a hosting
word is identically 1 on these eight lines. The only such letters are the eight
frame letters. Their linear parts, in the inherited simple-root chart, are the
eight vectors of one affine hyperplane in a 4-dimensional space. A subset hosts
the row exactly when those vectors span the space. The hosting products are
therefore 56 words of length 4 and every subset of length 5, 6, 7, or 8. None
is shorter. Every one of the 149 products equals

```text
(1 + x1 + x3)(1 + x0 + x1 + x4)(1 + x1 + x2 + x5 + x6)(1 + x0 + x1 + x5 + x7).
```

The lexicographically first length-4 word uses ports `13, 26, 131, 262`. The
square-free support has 120 monomials, with degree counts 1, 8, 27, 47, and 37.
The constant and all eight variables `x0, ..., x7` are the degree-at-most-1
part. The other **111** monomials are the new charges for this row.

The recorded forty are the degree-at-least-2 monomials of the frame-0
polynomial from PR #7031,

```text
(1 + x0)(1 + x1 + x2 + x4)(1 + x5)(1 + x6 + x7).
```

That expansion is locked by ANF hash
`26803d29aa3141a357da4aa551195fe6378d3f2e1cba0c4291a4dedbce6ded2a`. The frame-0
census is not rerun.

**Intersection:** 31 of the 111 lie in the recorded 40 (degrees 16, 13, 2).
**Additional bill:** the other 80 (degrees 11, 34, 35). Once the recorded 40
are paid, frame 1 still charges these 80 monomials. Nine recorded monomials are
absent from frame 1. The joint degree-at-least-2 support of the two words has
120 monomials. Fifty-one of the 111 contain `x3`; the recorded polynomial does
not use `x3`, so all 51 are inside the additional 80.

The names, hashes, and the proof of the hyperplane count are in
[PROOF.md](PROOF.md). The pairing matrix on the eight frame lines is the
all-ones matrix and has rank 1. That copy-cost is a different unit and is not
added to the monomial bill.

## Evidence class

The hosting classification, the length count, and the equality of every hosting
product with the four-factor polynomial are written proofs under the product
alphabet and this chart. The chart identity, the admissible-letter test, the
16-vector orthogonal, the 255 subset products, the boolean expansion, and its
Möbius cross-check are exhaustive finite censuses. Each domain is finite and
fully enumerated. This is not a heuristic and not an incomplete search inside
that alphabet.

The same census gives no lower bound for a sum of letters, for another chart,
or for a circuit that is not a product. The 80 additional monomials are not a
selected-invoice histogram. The selected frontier stays `781451/250000000`.

## Scope

Catalogue card `complex-rank-shape-decoder`, priority revision 8, pinned at
`17469fff78c22941280f04d39dc5a1faee09c840`. The card asks whether a decoder or
coframe change improves the full signed moment. Open PR
[#7031](https://github.com/CrocSwap/integer-mult-bounds/pull/7031) hosts frame
0 and leaves, as its first open question, the hosting of frame 1 and the
intersection of the new monomials with the recorded 40. Scope is **changed** to
that question. The connection to the bottleneck is recorded in
[TASK.json](TASK.json): a later joint bill of two rows has to know which
monomials are shared, and this package stops at that intersection.

`data/frames.json` is the frame partition from open PR #7014 (head
`949c0ada285aae619468ae49317c8d9f4df130f7`), the same bytes vendored by #7031,
hash `c75915c18fc06ac19cc90fb9911209517c071862fdf401b998d5075efc0cda0d`. This
package does not reprove the rank-13 factorisation and does not reprove the
frame-0 census. Ports and the E8 line map are the #6933 inputs pinned in
[SOURCES.json](SOURCES.json).

Overlap was searched on 2026-11-10 against 339 open PR records, 7013 discussion
records, and the complete local note inventory at the base commit. The hits for
this question are #7031 and discussion comment 19514167, which state the
question and do not answer it. No open PR hosts frame 1.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/p104-frame1-monomial-intersection/verify.py
python3 -I -O -B research/p104-frame1-monomial-intersection/verify.py
python3 -B scripts/research_package.py --package research/p104-frame1-monomial-intersection
python3 -B scripts/check_research_commit.py --package research/p104-frame1-monomial-intersection --check-source-history
```

The verifier prints `PASS_P104_FRAME1_INTERSECTION` with
`word=13,26,131,262`, `new=111`, `intersection=31`, and `additional=80`.
Failure controls delete one canonical letter, count the 14 length-4 misses,
reject the rank-3 prefix, delete the constant monomial, and multiply by one
non-frame letter.

Not run: the frame-0 product census, a sum-of-letters search, frames 2 through
12, the selected-supplier replay, `make frontier6030-verify`, and Lean.

## Open next questions

1. Host frame 2 of the same witness and intersect its degree-at-least-2
   monomials with the joint 120-monomial support of frames 0 and 1. The
   two-row union is not yet a thirteen-row bill. The first step is the same
   spanning test on `frames[2]`. Frames 2 through 12 are unexpanded here.
2. Can one circuit charge each of the 31 shared monomials once and still host
   both rows? The intersection compares two separate expansions. It does not
   exhibit a joint word. The first step is to take one hosting product from
   each row and see whether a common subproduct realises exactly those 31
   monomials.

## Credit

Frame partition: unpaidmoon, PR #7014. Frame-0 hosting and the recorded forty:
PR #7031. Ports and the odd-graph window: PR #6933. Label pairing: the
inherited simple-root chart. Prepared by unpaidmoon with substantial Cursor
Grok assistance. New work is Apache-2.0.
