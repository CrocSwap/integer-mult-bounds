# The 40 frame-0 monomials are not selected-invoice primitives

**No new κ.** The selected frontier stays `781451/250000000`. This package
asks whether the 40 monomials charged by open PR #7031 can be named as
primitives on the selected #6030 invoice. Under that invoice's constructors,
they cannot. The missing map is stated in [PROOF.md](PROOF.md). Naming them
would not by itself be a κ change, and this obstruction is not one either.

## Result

The charged polynomial is

```text
(1 + x0)(1 + x1 + x2 + x4)(1 + x5)(1 + x6 + x7).
```

Its 40 degree-at-least-2 monomials are the object #7031 asked to place on
the invoice. A recursive primitive of the selected invoice is a pair
`(side, rank)` built from frame-dimension gaps, eighteen local copies,
fifteen query shears, the idle lengths 7 and 8, and one rank-145 target.
Ordinary names on the same word are the opcodes `ADD`, `CLEAR`, `COPY`,
`INIT`, `MOVE`, and `SCALE`. Those constructors do not read a chart monomial.

Against that alphabet:

- 32 of the 40 exponent integers are keys of neither histogram. The six
  degree-4 masks `99, 101, 113, 163, 165, 177` are among them.
- The eight integers that do collide are not unique names. Masks `3` and `5`
  are both paid keys and target keys.
- No printed monomial equals an opcode.
- 14 exponent integers occur in the selected port list, and 26 do not.
- Degrees 2, 3, and 4 are histogram keys, but the constructors do not set
  rank equal to degree. That reading is not adopted.

The chart is a different coordinate system from the invoice. The simple-root
labels of ports `11, 21, 38, 140` are `282, 284, 270, 454`, not the ports
themselves. An integer collision with a port or a frame vector is not an
identification.

## Evidence class

The product expansion is an exhaustive 48-element census. The invoice
histograms are an exhaustive replay of the selected word, matched to
`RESULT.json`. The failed readings are exhaustive checks of the 40
exponents. The degree reading is refused because the constructor texts do
not mention it. This is a scoped proof together with those censuses. It is
not a heuristic, not a search over arbitrary maps, and not a proof that
another contract could not name the monomials.

## Scope

Catalogue card `complex-rank-shape-decoder`, priority revision 8, pinned at
`17469fff78c22941280f04d39dc5a1faee09c840`. The card asks whether a decoder
or coframe change improves the signed moment. Scope is **changed** to the
naming step in open question 3 of
[#7031](https://github.com/CrocSwap/integer-mult-bounds/pull/7031). The
connection to the bottleneck is in [TASK.json](TASK.json): a thirteen-row
comparison with the selected profile is not available until each charged
monomial has a primitive name, and this package stops when that name is
shown to be missing.

The selected record, `upstream/`, and the #6030 word are inputs, not edits.
Open #7031 already hosted the row and charged the 40 monomials; this package
does not redo that hosting. It does not host frame 1, and it does not ask
whether a sum of letters can use fewer than 40 monomials.

Overlap searched on 2026-11-10: the open-PR search for this naming returned
only #7031, whose discussion finding
[19514167](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19514167)
leaves the naming open. No fork branch had taken the question.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 -B research/p104-frame0-invoice-primitive-names/verify.py
python3 -I -O -B research/p104-frame0-invoice-primitive-names/verify.py
python3 -B scripts/research_package.py --package research/p104-frame0-invoice-primitive-names
python3 -B scripts/check_research_commit.py --package research/p104-frame0-invoice-primitive-names --check-source-history
```

The verifier prints `PASS_P104_FRAME0_INVOICE_NAMES` with `monomials=40`,
`outside_both_histograms=32`, `degree4_outside=6`, and the unchanged κ.
Failure controls drop the factor `x0`, accept mask `99` as a paid rank, and
replace the 18 local copies by 17.

Not run: `make frontier6030-verify`, the native Clifford replay, Lean, and
any expansion of frames 1–12.

## Open next questions

1. Give a total map from these 40 exponents to the inherited primitive
   alphabet that one of the selected constructors determines. The
   thirteen-row comparison stays blocked until that map exists. The first
   step is to make one constructor read one of these exponents, or to show
   that a constructor already does, and then check the image of all 40.
   The present constructors read frame dimensions, idle lengths, and a
   diagonal popcount only.

The thirteen-row profile comparison is not opened. Frames 1–12 remain the
separate hosting question already stated by #7031, and a missing name for
these 40 blocks that comparison on its own.

## Credit

The 40 monomials and the factored word: unpaidmoon, PR #7031. The selected
invoice and word: DreamingOfClouds, PR #6030, on the PR #5827 verifier chain.
Ports and the odd-graph line map: PR #6933. Prepared by unpaidmoon with
substantial Cursor Grok assistance. New work is Apache-2.0.

Workflow note: https://github.com/CrocSwap/integer-mult-bounds/discussions/1200
