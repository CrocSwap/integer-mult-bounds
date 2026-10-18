# Research audit: exactly which carry-grade moduli are safe

**No new kappa.** This audits the mixed-radix carry filter in
[Chafik Boukhalfa's PR524](https://github.com/CrocSwap/integer-mult-bounds/pull/524).
The original `T=D` choice is correct and is sharp when every axis has length
at least two. With singleton axes, a smaller modulus can be safe, but simply
using the number of non-singleton axes is unsafe, and increasing a safe
modulus can make it unsafe.

The [proof](PROOF.md) characterizes every attainable carry count as a subset
sum of the gaps between consecutive non-singleton axes. A modulus is sound
exactly when none of the positive counts is divisible by it. This gives an
exact admission test and explicit counterexamples, not an unrestricted
convolution lower bound. Singleton compaction or different weights change
the model.

| Shape | Attainable counts | Illustrative result |
|---|---|---|
| `(2,1,2)` | `{0,2}` | Two active axes do not make `T=2` safe. |
| `(2,1,1,2)` | `{0,3}` | `T=2` is safe; `T=3` admits a false coefficient. |
| `(2,1,2,1,1,2)` | `{0,2,3,5}` | `T=4` is safe; `T=5` is unsafe. |
| `(2,2,2,2)` | `{0,1,2,3}` | Exactly `T>=4` is safe. |

For the second shape, the retained encoding uses 47 potential coefficient
slots at `T=4` and 19 at `T=2`. Both use four signed-split integer products.
These are exact layout sizes, **not runtime measurements or exponent gains**.
The admission result does not optimize over other coordinate layouts.

## Reproduce

From the repository root, with Python 3.11+ and its standard library:

```sh
python3 -B research/graded-modulus-audit-seed74/verify.py
```

Expected:

```text
PASS_GRADED_MODULUS_AUDIT: 741 exhaustive + 74 seeded shapes; 5507 modulus cases; 8 negative controls
```

The command checks source hashes, recomputes the entire bounded census,
executes signed integer products, exercises all eight controls and compares
the complete deterministic receipt with [EXPECTED.json](EXPECTED.json).
It does not regenerate predecessor artifacts. `python3 -O -B` must give
the same result; this audit uses explicit checks and loads the pinned
predecessor with its assertions enabled in either mode.

Optionally append `--details /absolute/new/census.json` to retain every
shape's counts and alias totals. The output must not already exist.
`--write /absolute/new/receipt.json` is a development option that writes a
fresh receipt instead of comparing the committed one.

## Completed coverage and controls

The domain is fixed, with no time-based or first-success stopping rule:

* All **741 shapes** with `D=1..6`, radices in `{1,2,3}`, and `N<=48`.
* **74 additional distinct shapes**, generated with seed **74**, `D=7..12`,
  and two to four active axes of radix two or three (`N<=81`).
* Every modulus `1..D+1` for every shape: **5,507 cases**, **1,539,134
  below-N pair/modulus checks**, and **3,001 constructed count witnesses**.
  There are 220,190 distinct ordered below-N pairs across the shape domain;
  the larger number counts their repetitions across moduli.
* **653 adapter convolutions / 2,612 integer products** across eight
  selected shapes: all basis pairs plus seven signed, zero and dense
  cases per shape, at the least sound modulus and inherited `D` where
  distinct. Eight inherited layouts and **48 nonzero source convolutions**
  also agree with the pinned PR524 implementation.

[independent.py](independent.py) imports neither the predecessor nor the
structural checker. It computes grades from flattened-index floors and
enumerates coordinate pairs directly. [audit.py](audit.py) uses the
inherited weight recurrence and the new gap-subset criterion. Constructed
witnesses receive a third check using index remainders at each place value.

The eight explicit controls exhibit failures of: active-axis-count sizing,
monotone admission, checking only the maximum count, gapwise coprimality,
checking only distinct prefix residues, omitted grade-wrap extraction,
omitted index padding, and omitted signed cross products. Each includes
actual wrong output and a correct coordinate-convolution oracle. The first
five also confirm that admission rejects the unsafe modulus before packing.

The lcm family in the proof establishes a scoped negative result for all
`K`: with two active axes separated by `lcm(1,...,K)`, every `T<=K` fails
under the unchanged recurrence. The receipt checks the arithmetic for
`K=1..12`; it does not allocate those long symbolic shapes or pretend the
finite checks alone prove the family.

## A separate source assertion observation

While comparing signed products, the pinned predecessor rejects
`graded.apply([0], [5], (1,))` with `AssertionError` at its operand-width
bound. Its product-derived coefficient bound is zero, so it chooses a
one-bit slot, which cannot bound the nonzero operand five. This is a
**failed source assertion**, not a counterexample to the convolution
identity: the correct product is zero. The audit records this input
separately from successful source comparisons and checks the adapter and
direct oracle return `[0]`. Predecessor sources remain unchanged.

## Provenance, review boundary and attribution

Base: **`f567884aeb8851b6e794af1184119a3bfbe1e631`**.
Track: adversarial mathematical audit, OS-random assignment seed **74**.
[CLAIM.json](CLAIM.json) records task selection, overlap checks and handoff;
[SOURCE.json](SOURCE.json) pins all consumed predecessor files.

PR524 head: `9161fb1ff1c71bd8255e32d57ab5164aa8109376`, merged as
`5b8622c928b482ef40c42acef86b597dd1df6cfc`. Its retained review is
[research-notes-20261011.md](../../docs/research/research-notes-20261011.md).
Its Gaussian predecessor is PR489 at
`8922e3b3f0fd7772b0fb42028eb2532984c3ab42`; this audit does not verify that
weighted Gaussian algorithm or its unresolved interfaces.

At the base, the selected conditional saving is
`1661634653669567/1000000000000000000` from the PR799/PR589 assembly.
The selected certificate, construction and maintainer review were inspected
for orientation. This contribution leaves them and `upstream/` unchanged.
No selected-supplier cold replay, all-size compiler, tape implementation,
analytic transfer, or full formal multiplication proof is supplied.

Credit **Chafik Boukhalfa / chafreaky** for PR524's mixed-radix carry
identity, four-product signed packing, bounds and tests, and PR489's
underlying experiment. The rank-filtered convolution literature remains
credited in his original proof; no global originality claim is made here.
The audit's new scope is modulus admission and its exact counterexamples.
Prepared for **Ross Richardson (@RossRichardson)** with substantial
**OpenAI Codex assistance** in the proof, implementation and review.
Apache-2.0, as in the repository; original notices remain intact.
