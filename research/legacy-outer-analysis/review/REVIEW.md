# Independent review of the outer-analysis extraction

Reviewer: a separate OpenAI Codex agent. This is not human review or formal
proof verification. The review used the package in
`legacy-audit/packages/legacy-outer-analysis` and current main
`cef4b52f2a59009865bf8eabde1be3f159063703`.

## Finding

The four submitted arguments are valid within their stated interfaces.
All material findings from this review are resolved. The package is
ready for the coordinator's publication checks. It proves no complete
supplier and no improvement to the complete multiplication kappa.

The useful results are a smaller borrowed spectator requirement for one
retained router, a lower bound for every complete inverse of the retained
Gaussian sampler, an explicit good root for all Newton prefixes, and
precise limits on two common-carry extraction methods. These statements
do not require a new research direction to complete their publication.

## Proof review

### Polylogarithmic spectators

I read POLYLOG-SPECTATORS.md, both retained arbitrary-routing reports,
the portable harness, and its source-revision change. I checked these
steps against the inherited contract:

- With `s=ceil(log2 p)^2`, the three fields are disjoint when `n>3s`.
  Each matching edge avoids one field. The first and second fields have
  disjoint suffix destinations, including `3s<n<4s`.
- Conjugating a matching by the field placement puts both edge endpoints
  in the prefix. Returning the field restores every named coordinate.
- The suffix record has `R0*2^s` bits. It absorbs each fixed polynomial
  descriptor charge after a finite threshold. This changes the record
  layout, not scalar precision or the number of address coordinates.
- For `n<=3s`, the retained fixed-block elementary operation gives
  `O(V log^2 p)` cost. The prefix fallback below `64G` is also paid.
- The conclusion retains full binary boxes, a polynomial supplied-map
  description, complete records, fixed tapes, and the original arbitrary-gap
  equal-width interchange. It is not arbitrary computed-key sorting.

Thus the old `epsilon>a` condition is unnecessary for this router. The
proof does not remove the other Gaussian, exposure, or supplier terms.
The hypothetical relaxed parameter row is a diagnostic, not an admitted
exponent or construction.

### Every complete Gaussian inverse

I checked the matrix against the exact `T` definition in the retained
07-resampling.tex and checked the source identity `(D N^-1 C) T=I`.
For coprime `3<=s<t`, with odd `s`, a selected unit column has phase
`beta=(s-1)/(2s)>=1/3`. The periodic tail bound is valid because

```
9(v+1/2)^2-1/4-(2+v)=9v^2+8v >= 0.
```

The relative tail is below `1/28`. Therefore the column norm is below
`2 exp(-pi u beta^2)`. Applying any linear left inverse to this column
gives the claimed lower bound. Tensoring the selected columns proves
the bound for a joint inverse; it does not assume that the inverse
itself factors by axis.

For an approximate linear inverse, a complete residual norm at most
`1/2` loses at most one bit. The `u>=12` exact and `u>=24` approximate
thresholds are correct. The historical review's even-size extension is
also valid by replacing the selected phase with `floor(s/2)/s`; its
separate historical 354-case receipt was not replayed here.

This is a necessary normalization cost for the declared arbitrary-input
disk interface. It does not exclude a different sampler, a restricted
error direction, or a different representation. The strict
`epsilon+r<1` conclusion is for sublinear normalization. Equality is
not excluded for a new `O(p)` normalization analysis.

### Newton root selection

I read ROOT-CHOICE.md, its independent review and binding, and the
retained local compiler. The union bound gives an accepted unit with
`B=16h`; it uses primality and exact integer tests. It does not establish
a composite-radix result. The search cost is polynomial in `q`.

The rational continued-fraction estimate is correctly non-strict. The
first accepted root is below `q/2` by symmetry, so its first denominators
are distinct. Consecutive denominator ratios are at most `B`, and the
greedy block decomposition has at most `B(2h+1)` blocks. Grid displacement
then gives interval discrepancy at most `480h^2`.

The capped logarithm has variation at most `2 ln q` and integral between
zero and `4/q`. The bounded-variation estimate proves the stated
`1000h^3` bound for every prefix `0<=j<q`. The endpoint `j=q` is excluded
as required. The finite q-binomial identity gives the reciprocal
coefficients, and the unit output permutation is correct.

These are coefficient magnitude bounds. They do not establish short
exact algebraic encodings, a complete rounding program, or fixed-tape
sector movement. The stated conservative `O(p log^6 p)` intermediate
guard is not an `O(p)` fixed-format supplier.

### Common carry and reciprocal spill

The weight recurrence telescopes to the number of ordinary mixed-radix
carries. Constant extraction is the desired tensor lower Toeplitz map.
At output zero, the stated basis inputs supply all degrees `0..ell`.
Thus at most `ell` nonzero evaluations at that output cannot determine
the constant for arbitrary inputs. The ambiguity witness can be scaled
to a disk input. This proof does not cover coupled readout across outputs.

The small-positive-marker example requires `lambda<=2^(1-p)` and gives
the stated inverse-gauge norm. Its precision consequence is for separate
gauges on a common absolute grid. The exact root average avoids that
gauge growth but still uses more than `ell` complete cyclic products.

The finite reciprocal spill is correctly nonconstant. Pairing `k` and
`q-k` gives the degree-q coefficient `-(q-1)/(2q)`, and the final term is
`u/q^2`. A scalar residual correction does not follow.

## Fresh verification

The command used CPython 3.14.7 and the standard library. No retained
third-party environment was needed. It ran one check process at a time,
with thread-count variables set to one. Assertions were enabled.

```
/opt/homebrew/opt/python@3.14/bin/python3.14 -B \
  /Users/aliromman/Projects/IntegerMultiplicationBounds/work/project-final-cleanup-20261022/legacy-audit/packages/legacy-outer-analysis/verify.py \
  --work /Users/aliromman/Projects/IntegerMultiplicationBounds/work/project-final-cleanup-20261022/reviews/outer-analysis/fresh-run
```

All six checks returned zero. The final line was
`PASS_LEGACY_OUTER_ANALYSIS checks=6`. Total elapsed time was 66.13 seconds.

| Check | Fresh coverage |
| --- | --- |
| Spectator routing | 4,280 complete tiny addresses, 192 larger forward/inverse probes, 96 independent named-slot classes |
| Gaussian normalization | 227 coprime size pairs, 118,992 periodic-distance checks |
| Newton identity | 408 exact matrix entries, reciprocal and output-map identities, seven selected larger primes |
| Actual q-kernel carry | 954 input-kernel pairs, 336 coefficient outputs, exact root averages |
| Independent root choice | 8,256 prefixes, 56 convergent-block checks |
| Independent carry | Six finite cyclotomic spill cases, three rational tensor layouts, 11,259 pairs |

All mathematical arithmetic in these checks is exact integer or rational
arithmetic, including the cyclotomic quotient calculations. Timing,
memory, and free-space fields are measurements. Larger address probes
and some discrepancy probes are samples. The written proofs establish
the infinite statements; the finite checks alone do not do so.

The six runs include the existing negative controls. No full supplier,
selected certificate replay, proof assistant, or full multiplication
theorem check was run. No extra broad test suite was required for this
extraction.

COMMAND.json, RESULT.json, fresh-run/RUN.json and the fresh logs record
the execution. CHECKED-FILES-BEFORE.json and CHECKED-FILES-AFTER.json bind
the inspected bytes. SOURCE-HASH-REVIEW.json checks all 37 final frozen
manifest entries. PINNED-INPUT-CROSSCHECK.json records 12 exact historical
Git-source comparisons and six imported-source Git-blob comparisons.

## Current-source comparison

I inspected the current-main normalized Gaussian section packages and
the shifted-Gaussian conditioning package. Their claims concern finite
normalized Schur sections or a different shifted-kernel interface. They
do not give this bound for every complete inverse of the original
periodic sampler.

I also inspected current-main newton-prefix-audit, which concerns rounded
reciprocal and square-root routines. It is unrelated to this root-choice
lemma. The current batched CRT package uses different nonlinear switch
controls and reservoir charges. This extraction retains the older
coordinate-permutation contract and does not claim to replace that CRT.

The saved OPEN-PRS.json contains 315 records. I inspected the complete
bodies for PR3910 and PR647 and saved them in RELATED-OPEN-PRS.json.
PR3910 bounds a forward Gaussian row mass. PR647 supplies an exact-RAM
DFT realization and explicitly excludes numerical stability. Neither
body supplies the claimed complete-inverse obstruction or uniform
Newton root-choice conditioning lemma. Narrow searches of current-main
research files found no duplicate of these specific statements.
This is a bounded overlap check, not a literature-priority proof or a
review of every other repository theorem.

## Packaging findings

1. Resolved: the retained RaD license is CC0 1.0. The new NOTICE.md now
   distinguishes it from Apache-2.0 new work and retained OpenAI/eumemic
   files. Frozen historical wording remains unchanged.
2. Resolved: the historical omnibus cyclic-hybrid/PROOF.md referred to
   omitted blocked-convolution and growing-dimension material. The owner
   removed that copy from the extraction. The submitted carry proof is
   independent/COMMON-CARRY-GAUGE.md. The original historical file remains.
3. Resolved: the owner resolved eumemic's abbreviated source revision to
   `6f87d1a0c9ae462cdcb2034a1361c87623221e66` and recorded it.
4. Resolved: the first new NOTICE.md said that the retained eumemic note
   credits Ryan Shea. That credit was not in the retained note. The owner
   replaced it with the note's direct credit to icekylinx for inherited
   batched recursion and retained the other community contributors.

The coordinator must still verify the final PR description, complete
source links, rendered Markdown, and published readback. This review
does not substitute for those publication checks.

The later wrapper-only assertion propagation fix is reviewed in
WRAPPER-ASSERTION-ADDENDUM.md. Its positive and negative controls pass.
The frozen mathematical inputs remain unchanged.
The final file manifest excludes top-level review/ and publication-review/
copies to avoid self-reference. The wrapper addendum records the later
check of the owner's full optimized-environment replay evidence.
