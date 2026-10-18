# Signed block extraction audit

Status: adversarial mathematical audit with independent finite verification.
No new kappa. The retained extraction argument passes this audit under its
stated strict coefficient bound.

The contribution checks the actual fixed-width block interface of
`lem:signed-ring-product`, including its one-bit carry and terminal sign
extension. It adds a negative control that passes both integer recomposition
and the terminal carry test while recovering the wrong coefficients.
The existing signed-packing test instead repeatedly divides an unbounded
signed Python integer. That test remains useful, but does not cover this
block interface.

## Reproduce

From the repository root, using Python 3.9 or later and the standard library:

```sh
python3 -B research/signed-extraction-audit/verify.py --check research/signed-extraction-audit/RESULT.json
```

Expected output:

```text
PASS_SIGNED_EXTRACTION: 57160 words; 139776 transitions; 6561 exhaustive products; 180 sampled products; 6 negative controls
```

The checker verifies the source hashes in [SOURCE.json](SOURCE.json) before
running. `--json` prints the exact receipt. Checks remain enabled with
`python3 -O`; they do not depend on Python assertions.

## Statement and dependencies

The exact base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`. At that base,
the [selected record](../../certificates/selected-result.json) points to
the reviewed #626/#622/#623 complex construction and #543 bit supplier,
with conditional kappa `51110230636731/31250000000000000`.
The [maintainer review](../../docs/research/community-k492-review.md)
retains exact-recovery and tape assumptions. This audit examines one retained
arithmetic obligation, without changing that construction or certificate.

The audited source is
[`06-transforms.tex`, lines 463–609](../../upstream/build/sections/06-transforms.tex),
especially the extraction at lines 528–571. Its original source is OpenAI's
*Integer multiplication below n log n*, pinned in the repository to
`openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`.
[SOURCE.json](SOURCE.json) records the immutable source hashes and local
import commit. The upstream source is unchanged.

The source takes `r=2^ell < 2^p`, `p>=2`, input integer components bounded
in magnitude by `2^p`, radix `B=2^(4p)`, and `J=2r` blocks. An ordinary
product has padded coefficients `h[0]...h[J-1]`, with `h[J-1]=0` and
`|h[j]| <= r*2^(2p) < B/2`. Its signed evaluation `Z` has magnitude
less than `B^J/4`, so the source's signed fixed-width encoding is valid.

## The audited implication

Let `q[j]` be the unsigned blocks and `epsilon` be zero or minus one:

```text
Z = sum(q[k]*B^k, k=0..J-1) + epsilon*B^J.
rho[0] = 0.
```

After removing the first `j` coefficients, the source invariant is

```text
sum(h[k]*B^(k-j), k=j..J-1)
  = sum(q[k]*B^(k-j), k=j..J-1) + rho[j] + epsilon*B^(J-j).
```

Reduction modulo `B` identifies `h[j]` with the centered representative of
`q[j]+rho[j]`. The strict bound identifies that coefficient uniquely.
Subtracting it and dividing by `B` gives the same invariant at `j+1`, with
`rho[j+1]=(q[j]+rho[j]-h[j])/B`. Since `q[j]+rho[j]` lies in `[0,B]`,
the next carry is zero or one. At `j=J`, the invariant is exactly
`rho[J]+epsilon=0`.

The endpoint `q[j]+rho[j]=B` must emit zero and retain carry one. For
`p=2`, `r=2`, `a=[-1,0]`, `c=[1,0]`, the four blocks are all 255.
Extraction emits `[-1,0,0,0]`, finishes with carry one, and cancels
`epsilon=-1`. For `a=[-1,1]`, `c=[1,0]`, the blocks are `[255,0,0,0]`;
the carry resets from one to zero at the second block.

This is a restatement and audit of the source's induction. The finite replay
below corroborates it; it is not a proof-assistant formalization.

## A coefficient alias that weaker checks miss

Deliberately replace the source's radix 256 by 32 at `p=2`, `r=2` and
`a=c=[4,0]`. The true padded product is `[16,0,0,0]`. Its first coefficient
equals `B/2`, so centered extraction instead gives `[-16,1,0,0]`.

Both lists evaluate to 16 at radix 32, and the decoder's final carry cancels
the sign extension. Integer recomposition and final-carry checks therefore
both pass. Only the coefficient comparison or the separation requirement
rejects this alias. More generally, `[B/2,0]` and `[-B/2,1]` have the same
evaluation for every even `B`.

This is a counterexample to relaxing the strict symmetric separation bound
to `|h[j]|<=B/2`, and to using those two weak checks as a coefficient oracle.
It violates the lemma's radix choice and is **not** a counterexample to the
retained lemma. The arithmetic audit found no failure under the stated domain.

## Completed coverage and controls

| Check | Completed domain |
| --- | --- |
| Entire coefficient words, input packing, extraction and every residual identity | All lengths 1–4 over integers `-B/2 < h < B/2`, at abstract bases 4, 8, 16: 57,160 words |
| Local output transitions, including incoming carries zero and one | All unsigned blocks at source radices 256, 4096, 65536: 139,776 transitions |
| Products compared with direct polynomial convolution | Every pair of length-two integer vectors with entries in `[-4,4]`, at `p=2`, `r=2`: 6,561 products |
| Larger source-domain products | Seed 60; `p=2..12`, `ell=1..min(p-1,5)`, four independently drawn pairs per cell: 180 products |

The small abstract bases exhaust the recurrence, not the source's parameter
domain. The product checks use the source radix, input bounds and padded
length. The oracle forms each coefficient by direct multiplication and
addition; it does not decode an evaluation integer. The block converter
starts from sign and magnitude and explicitly complements and increments
negative products, separately from the input coefficient/carry scan.

Six deterministic controls demonstrate omitted extraction carry, omitted input
packing carry, reversed block order, omitted terminal sign extension,
incorrect zero filling of negative high blocks, and the forbidden positive
half-radix tie. Omitting the sign extension does not change the decoded list;
the terminal residual detects that particular error. The receipt records the
exact wrong outputs. The stopping rule was completion of these domains and
controls; the sample is not an exhaustive search or an impossibility theorem.

## Validation and concurrent work

Local verification passed on CPython 3.14.8:

```sh
python3 -B research/signed-extraction-audit/verify.py --check research/signed-extraction-audit/RESULT.json
python3 -O -B research/signed-extraction-audit/verify.py --check research/signed-extraction-audit/RESULT.json
python3 -B -m unittest discover -s tests -p test_finite_identities.py -v
make selected-record-check
```

All four existing finite-identity tests passed. Two additional in-memory
implementation mutations were rejected by the main audit: removing the
decoder's incoming carry failed the coefficient oracle; returning zero for
a negative product's sign extension failed the input-encoding comparison.
The mutations did not alter any repository file. A separate scoped AI review
checked the induction, examples, code and coverage counts.

The final overlap refresh found concurrent
[PR #690](https://github.com/CrocSwap/integer-mult-bounds/pull/690), by
Ryan Pinto, @Ambassators, at `8dd49f5e322f682502d9ab3c03d393a50f046e24`.
It independently checks `packed_lower` from Chafik Boukhalfa's pending
Gaussian implementation in #489. This contribution instead checks the retained
upstream lemma's signed two's-complement block scan and carry invariant.
The exact transition census and positive-half-radix alias control are the
additional evidence here. No #690 code or result is used by this checker.

The repository-wide `make verify` and selected suppliers' cold replay were
not run: this adds an isolated audit and changes no supplier, generator,
certificate, production checker or upstream source. Remote CI and other
Python/platform versions are not claimed as verified.

## Scope and credit

The goal was to test the source's streamed signed extraction against an
independent coefficient oracle and document its failure boundaries. Acceptance
requires every declared positive case and all six negative controls to pass,
with an exact receipt. Changes are confined to this research directory.

This does not implement a fixed-tape multiplier, prove its time bound, audit
complex coefficient combination, negacyclic reduction, final truncation,
Gaussian resampling, or the full integer multiplication theorem. Those and
the selected construction's uniform/compiler/common-label/mutable-basis,
hosting, precision and analytic assumptions remain unresolved by this audit.
Python's exact integers implement the finite oracle; their runtime is not
evidence for the manuscript's tape complexity.

The original lemma and proof belong to OpenAI and retain their upstream CC0
notice. Douglas Colkitt's [dependency audit](../../docs/audit.md) and
[finite identity test](../../tests/test_finite_identities.py) are predecessors.
Jeremy Kothe's reviewed complex construction and eumemic's bit supplier
identify the accepted checkpoint, but this contribution does not replay or
claim changes to those suppliers. No pending PR supplies code or a new premise.

Prepared by Sagar Thakrar, @thakrarsagar, with substantial OpenAI Codex
assistance for investigation, implementation, prose and an additional scoped
AI review. No human-only or formal verification is claimed. New files are
under the repository's Apache-2.0 license.
