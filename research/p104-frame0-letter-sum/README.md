# No sum of letters hosts one P104 frame indicator

**No new κ.** The selected frontier stays `781451/250000000`. This package
answers open question 2 of PR #7031: whether an `F_2` sum of root-line letters
can host frame 0 with fewer than 40 new monomials. It does not redo the
product hosting, it does not host frame 1, and it does not price the selected
invoice.

## Result

Frame 0 is the odd-graph clique `11, 21, 38, 56, 140, 146, 161, 191`. A letter
is one root-line pairing. In the inherited simple-root chart every letter is
affine of the form `1 + (linear form)`, so every `F_2` sum has degree at most
1. The new-monomial count, using the same degree cut as #7031, is therefore 0
for every sum.

The explicit sum of four frame letters cancels:

```text
λ_11 + λ_21 + λ_38 + λ_56 = 0.
```

Its monomial list is empty: zero monomials of degree at most 1 and **zero**
new monomials. The value is 0 on every root line, so the sum misses all eight
frame lines and does not host the row. A single letter such as `λ_11` expands
to `1, x1, x2, x4, x5`, also with zero new monomials, and equals 1 outside the
frame.

No sum hosts the row. The four P104 ports `478, 11, 14, 475` have augmented
chart labels summing to 0, so every affine function has value-sum 0 there.
The indicator is 1 only at port 11, so its value-sum is 1. The same
contradiction holds for `21, 13, 493, 501`. The argument is written in
[PROOF.md](PROOF.md). It already fails on the 104 P104 lines, before the 16
lines outside P104 are considered.

The 120 letters span all 512 affine functions. On the 120 root lines their
Hamming distances from the indicator are `8, 48, 56, 64, 72, 112` with
multiplicities `1, 7, 248, 248, 7, 1`. The unique closest sum is the zero
polynomial, at distance 8. No subset of one, two, or three root lines gives
this parity obstruction; 7168 subsets of size 4 do, and 4384 of those lie
inside P104.

## Evidence class

The degree bound and the four-line parity are written proofs. The chart
identity, the rank-9 span, the distance histograms, the 7168 four-line
obstructions, the 32130 four-letter syzygies, and the 255 subset-sums of the
frame letters are exhaustive finite censuses. This is not a heuristic and not
an incomplete search inside the sum alphabet.

It is not a proof that 40 is minimal for sums of products, for another chart,
or for a circuit that is not an `F_2` sum of letters. The #7031 product remains
a hosting with 40 new monomials. That product is not a sum. No selected-invoice
histogram is computed, and the result does not beat the selected profile.

## Scope

Catalogue card `complex-rank-shape-decoder`, priority revision 8, pinned at
`17469fff78c22941280f04d39dc5a1faee09c840`. The card asks whether a decoder or
coframe change improves the full signed moment. Scope is **changed** to open
question 2 of
[PR #7031](https://github.com/CrocSwap/integer-mult-bounds/pull/7031): the
product census there does not cover sums. The connection to the bottleneck is
recorded in [TASK.json](TASK.json). A joint bill cannot undercut the product
charge by replacing this row with a sum of letters, because no such sum hosts
the row. That is not a signed histogram and not a supplier admission.

`data/frames.json` is the frame partition vendored by #7031 from PR #7014
(head `949c0ada285aae619468ae49317c8d9f4df130f7`), byte hash
`c75915c18fc06ac19cc90fb9911209517c071862fdf401b998d5075efc0cda0d`. Only frame 0
is evaluated. Ports and the E8 line map are the #6933 inputs pinned in
[SOURCES.json](SOURCES.json).

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/p104-frame0-letter-sum/verify.py
python3 -I -O -B research/p104-frame0-letter-sum/verify.py
python3 -B scripts/research_package.py --package research/p104-frame0-letter-sum
python3 -B scripts/check_research_commit.py --package research/p104-frame0-letter-sum --check-source-history
```

The verifier prints `PASS_P104_FRAME0_LETTER_SUM` with `explicit=11+21+38+56`,
`monomials=0`, `new=0`, and `hosts=0`. Failure controls delete one letter of
that sum, reject each proper subset of the obstructing four, keep a
frame-supported dependence with even indicator parity out of the obstruction
count, and reject the constant-1 function and the single letter `λ_11`.

## Open next questions

1. Can one explicit `F_2` sum of two products of root-line letters, each
   product of length at least 2, host this same row with fewer than 40
   monomials of degree at least 2? Pure sums are affine and cannot host. One
   product of four letters already hosts with 40. A sum of two products is the
   first expression that neither census covers. One miss is not a minimum.
2. Among the `2^16` functions of the four #7031 forms
   `p = 1 + x1 + x2 + x4`, `q = x0`, `r = x5`, and `s = x6 + x7`, what is the
   minimum number of degree-at-least-2 monomials of a function that matches
   the indicator on all 120 lines? This finite family contains the length-4
   product and every sum of letters inside its span. It does not decide a
   general circuit.

## Credit

Frame partition: unpaidmoon, PR #7014, as vendored by PR #7031. The product
hosting and the 40-monomial charge: PR #7031. Ports and the odd-graph window:
PR #6933. Label pairing: the inherited simple-root chart. Prepared by
unpaidmoon with substantial Cursor Grok assistance. New work is Apache-2.0.
