# One P104 frame-indicator word

**No new κ.** The selected frontier stays `781451/250000000`. This package hosts
one frame-indicator row as a legal product of root-line labels and charges the
new monomials of that word. It does not host the other twelve rows and it does
not price a signed profile.

## Result

Frame 0 of the vendored 104-by-13 witness is the odd-graph clique

```text
11, 21, 38, 56, 140, 146, 161, 191.
```

A letter is the pairing of one root line with all 120 root lines. In `F_2`, a
product equals 1 only when every factor equals 1, so every factor of a hosting
word is identically 1 on these eight lines. The only such letters are the eight
frame letters. The 255 nonempty products of those letters were evaluated on all
120 lines. The products equal to the indicator begin at length 4: 56, 56, 28,
8, and 1 products of lengths 4 through 8. None is shorter.

Every length-4 hosting product expands, in the inherited simple-root chart, to
the same 48 square-free monomials

```text
(1 + x0)(1 + x1 + x2 + x4)(1 + x5)(1 + x6 + x7).
```

The lexicographically first such word uses ports `11, 21, 38, 140`. Eight
monomials have degree at most 1 (`1` and `x0, x1, x2, x4, x5, x6, x7`). The
other **40** have degree 2, 3, or 4, in counts 17, 17, and 6. Those 40 are the
new charges for this row. The proof of the factor restriction and of the
disjoint-variable identity is in [PROOF.md](PROOF.md). The support of the
function on the chart is a 16-point flat; exactly eight of those points are
root-line labels, and those eight are the frame.

The pairing matrix on the eight frame lines is the all-ones matrix and has
rank 1. That copy-cost is a different unit and is not added to the 40.

## Evidence class

The factor restriction and the reduction to the four-factor form are written
proofs. The census of 255 products, the check that only the eight frame letters
are admissible, the 120-by-120 chart identity, and the agreement of all 56
length-4 expansions are exhaustive finite checks. This is not a heuristic and
not an incomplete search inside that alphabet.

It is not a lower bound for sums of letters, for a different chart, or for a
circuit that is not a product. It is not a selected-invoice histogram. It does
not beat the selected profile.

## Scope

Catalogue card `complex-rank-shape-decoder`, priority revision 8, pinned at
`17469fff78c22941280f04d39dc5a1faee09c840`. The card asks whether a decoder or
coframe change improves the full signed moment. The live handoff in open PR
[#7014](https://github.com/CrocSwap/integer-mult-bounds/pull/7014) asks a prior
question: host one frame-indicator row and charge every new monomial before
touching the other twelve. Scope is **changed** to that first step, for frame 0
only. The connection to the bottleneck is recorded in [TASK.json](TASK.json):
a later joint bill cannot be priced until each row's new monomials are known,
and this package stops at the first row.

`data/frames.json` is the frame partition from that open pull request (head
`949c0ada285aae619468ae49317c8d9f4df130f7`), vendored and hashed inside
`verify.py`. This package does not reprove the rank-13 factorisation. Ports and
the E8 line map are the #6933 inputs pinned in [SOURCES.json](SOURCES.json).
The label chart is the simple-root chart of the inherited `e8model.py` pairing.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/p104-one-frame-indicator-word/verify.py
python3 -I -O -B research/p104-one-frame-indicator-word/verify.py
python3 -B scripts/research_package.py --package research/p104-one-frame-indicator-word
python3 -B scripts/check_research_commit.py --package research/p104-one-frame-indicator-word --check-source-history
```

The verifier prints `PASS_P104_ONE_FRAME_INDICATOR` with `word=11,21,38,140`,
`monomials=48`, and `new=40`. Failure controls delete one letter of that word,
count the 14 length-4 products that miss the row, delete the constant monomial,
and reject a letter from outside the frame.

## Open next questions

1. Host frame 1 by the same census and compare its degree-at-least-2 monomials
   with these 40. A shared monomial would make a joint bill smaller than the
   sum, which is the first place the thirteen rows can interact.
2. Decide whether a sum of letters, rather than a product, can host this same
   row with fewer than 40 new monomials. The product census does not speak
   about sums.
3. Name these 40 monomials as primitives on the selected #6030 invoice before
   asking whether thirteen rows beat the profile. No conversion is claimed here,
   and no κ change is available until that naming exists.

## Credit

Frame partition: unpaidmoon, PR #7014. Ports and odd-graph window: PR #6933.
Label pairing: the simple-root chart used by the complex-frame decoder notes.
Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0.
