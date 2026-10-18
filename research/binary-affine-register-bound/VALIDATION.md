# Observed verification — 2026-10-13

Environment: Linux x86_64, CPython 3.12.3, GCC 15.2.0 (`g++`, C++17, `-O2`,
`-Wall -Wextra -Werror`). The default `python3` is CPython 3.14.4; the registered
runner was explicitly invoked with `/usr/bin/python3.12`.

## Full mathematical certificate

```sh
/usr/bin/python3.12 -I -B research/binary-affine-register-bound/verify.py \
  --full --work /tmp/math-pass26-final-full
```

Observed:

```text
PASS_BINARY_AFFINE_QUICK affine_maps=1370 controls=7 not_full_dimension4_census
PASS_BINARY_AFFINE_FULL affine_maps=323930 exact_distances_and_attaining_words=true
receipt_sha256=e95e3af2f484cb03f600c8d669354465f4812a1316e842e248fc81a48d5a30d0
```

A second full run used CPython 3.14.4 under `-I -O -B` from `/tmp`, on a
minimal exported package whose 14 package/context files were read-only.
It rebuilt the C++ checker, repeated the complete census and returned the
same canonical receipt. All 14 input file hashes remained unchanged. This
run took 6.247 seconds; its output was stored outside the read-only export.
Canonical receipt hashing uses sorted-key compact JSON encoded as UTF-8.

The separate C++ Cayley BFS visited 2, 24, 1,344 and 322,560 affine group
elements in dimensions 1, 2, 3 and 4, respectively, with 72,642,074 directed
transitions in total. It uses no displacement-rank pruning. Python compared
**every** reachable state and distance with its rank formula and replayed an
explicit attaining factorization for every map. Noninvertible encodings must
remain unreachable. `EXPECTED.json` binds the complete distance-array and
factorization-stream digests as well as the full histograms.

The dimension-four histogram is `[1,225,11830,124200,186304]`. Its distance
array SHA256 is `a435930358a38584ee24ac00c7592aeb98bdb6dddcbd78ba3bbcd5b08f37a303`;
the factorization-stream SHA256 is
`5d250d76a1eb447b6701b0910619134da50d1f4cccdf1236905ba58d0a462c86`.
The first complete generation and comparison took 6.996 seconds locally;
this is a verifier measurement, not multiplication performance.

## Supplementary mathematical and package controls

The quick stage checked:

* every affine map through dimension three, with literal point evaluation of
  its complete factorization, plus a separate small point-permutation BFS;
* 44,020 elementary rank-one represented calls, covering every scalar rank-one
  idempotent through four registers and every paid address map through dimension four;
* 96 formal group-algebra words and 576 prefixes, comparing the actual formal
  image with separately multiplied represented calls and the paid-rank budget;
* 56 formal identities, including scalar basis conjugations, a four-call
  attaining example and the nine-call noncommuting three-target example with
  a fourth dirty register restored; an omitted paid call fails the latter;
* 32 constructed fixtures in address dimensions 5, 8, 16 and 32;
* seven explicit boundary controls: translation versus linear-part rank,
  noncommuting order, dirty-helper leakage, a nonzero formal element with zero
  natural image, underpriced rank-two address/scalar factors, and failure to
  remove the free scalar baseline.

```sh
/usr/bin/python3.12 -I -B research/binary-affine-register-bound/test_package.py
/usr/bin/python3.12 -I -B scripts/research_package.py --package research/binary-affine-register-bound
```

All five package tests and the registered replay passed. Tests reject a Boolean
substitution for an integer certificate entry, a corrupted native distance,
missing source inventory, corrupt source bytes, duplicate/nonfinite JSON, and
an existing output directory. A read-only minimal relocated quick replay under
`-I -O -B` passes with all file hashes unchanged. No critical verifier check
depends on Python `assert`.

The generic hook explicitly omits the full dimension-four C++ census. Its
success marker is not used as evidence that the native BFS ran. The dedicated
workflow runs `--full`; local results and hosted CI status remain separate.

## Source and scope

The task base and refreshed main are both
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The selected-record integrity check
passed with kappa `836330098538459/500000000000000000`. The task's first working
baseline returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; the other suggested
card's source-bound orientation also returned `PASS_R439_BSECTION_STARS`
before that already-covered helper-contract route was declined.

Source/provenance metadata and the two live context-document pins pass. Neither
predecessor implementation is imported into the new proof/checkers. No selected
source, compiler, frontier or frozen artifact is edited. Fresh overlap evidence
and exact nearby heads are in `OVERLAP.json`.

The all-dimension conclusion is a written proof, not extrapolation from the
finite census and not proof-assistant verification. The native BFS enumerates
address-group elements; it does not enumerate arbitrary-register formal
circuits. The sharp register bound follows from augmentation, representation
rank and the formal attaining construction in `PROOF.md`.

The result uses the declared binary-affine group and unit-price rule. It does
not cover free address transformations, different paid alphabets/payload
fields, clean-only output contracts, or reduction of rational frame entries
modulo two. Selected supplier cold replay, physical/native supplier admission,
hosting, roundoff/precision, tape/compiler costs and outer analytic transfer
were not performed. No new supplier or kappa claim, independent human review
or subagent review is made.
