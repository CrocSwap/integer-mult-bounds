# Community queue review: verifier hardening and deferred endpoints

Maintainer review with OpenAI Codex assistance, 2026-10-09. This is not
independent human peer review or formal verification of multiplication.
Main remains at `56b66d58297deca1d7dd130247d720e960f77a37`; this review does
not select a new exponent, merge a PR, or publish a GitHub review.

The [queue snapshot](community-round5-queue.json) contains 104 open PRs,
including 51 numbered above #83 and 16 drafts. Some older open PRs are already
represented in main; open status does not mean their contributions are absent.
The snapshot is an inventory, not approval of the listed submissions.

## Dispositions in this pass

| PR | Contributor | Reviewed head | Disposition |
|---|---|---|---|
| [101](https://github.com/CrocSwap/integer-mult-bounds/pull/101) | Andrew Barnes / Bortlesboat; counterexample credited to rfu08 | `76f55061bb50d8244c985807909a5f44254bd906` | Ready to integrate as verifier hardening; affected checks pass |
| [90](https://github.com/CrocSwap/integer-mult-bounds/pull/90) | anxkhn | `8e0442641696b4c284bf7fbb4f2c97dccf24ea6c` | Ready to integrate as documentation correction |
| [97](https://github.com/CrocSwap/integer-mult-bounds/pull/97) | Zhihao Chen / jacklightChen, using Swapnil Jain's pinned construction and credited earlier interfaces | `e15350b66e4bf796153a68c240a6cc1b788abe3e` | Partial construction review passes; repair optimized-Python validation before integration; full local bit replay remains outstanding |

The accompanying [validation receipt](community-round5-validation.json)
distinguishes local replay, inspected CI evidence, and unresolved scope.

## #101: bind algebra to the charged physical word

The old replay could accept an extra pair of identical scatter XORs because
they cancel algebraically. Their physical incidences were absent from the
output inventory used for the cost calculation. The fix requires equality of
the literal scatter multiset and the paid output-incidence multiset. It retains
multiplicities while permitting reordering: the scatter source and target banks
are disjoint, so these gates commute. This resolves the shared-entry-point
issue identified by rfu08 in #64 and independently tested during round four.

The shared preflight also validates nonnegative physical indices, frame masks,
source-slot uniqueness and output coverage. A module-level runtime guard
rejects interpreters that remove assertions. Both replay and native-profile
preparation invoke the preflight. The mutation helper now exercises each
checker independently rather than stopping after the first rejection.

Local validation on the exact submitted files passed all 16 focused tests,
the complete skip-frame replay/profile/assembly, regenerated joint-dual
words and their replay/profile/assembly, and the pair-assembly frame replay,
profiles and assembly. Every one of the ten submitted changed files remained
byte-identical after these checks. Recursive comparison of the six changed
JSON files found only provenance-hash changes; all mathematical fields remain
unchanged. The exact commit also has 36 successful jobs in its research-artifact
CI run, plus successful historical-candidate and Swapnil-reference workflows.
The full historical suite and Lean builds were not repeated locally.

This is a checker correction, not an improvement to kappa or incorporation of
the separate machine-transfer work in #64. Retain the counterexample credit.

## #90: distinguish main, release, and historical notes

The contribution guide currently points reviewers to the historical ternary
checkpoint. The patch instead links the reviewed main checkpoint, selected
parameter certificate and reproduction guide. It also distinguishes the
published PR #39 release from later reviewed main. Those descriptions agree
with main's existing review and release records. All 25 local links in the
two submitted files resolve. No mathematical artifacts change, so numerical
regression tests were not needed for this patch.

## #97: deferred bit endpoints and signed complex correction

The proposed conditional witness is `63965813/10^12`, above `2^-14`.
This review has not adopted it as main's witness. Swapnil Jain supplies the
pinned deferred-readout and complex construction. Zhihao Chen supplies the
explicit physical/reflected ledgers, commuting fan ordering, nonzero endpoint
gauge accounting, signed complex correction and integration with the retained
assembly. Their distinct contributions and all imported attribution must be
preserved.

The bit ledger sorts commuting fan targets by frame dimension, but does not
use dimension alone as proof of inclusion: its paths depend on the separate
exact frame and lifted-geometry checks. It checks the complete dirty basis,
reflected schedule and actual event histogram. Complemented auxiliary exits
include the nonzero entrance gauge; both data connectors and the rank-one
correction remain charged.

On the complex side the commutator uses signed readouts and the inverse word
negates coefficients as well as reversing their order. The endpoint formula
needs both a source translation and an inverse rank-one child. Dropping either
is invalid. Local regeneration passed the small complete signed-basis controls,
all 65,536 tensor Fourier addresses (each wrong-endpoint control fails 32,768),
the full h24 event/frame ledger, the 4,096,576-coefficient scalar identity,
exact rational tensor endpoint controls, and regenerated assembly. Regenerated
payloads match the submission after excluding elapsed-time fields. Both moments
are strictly below one; 47 constraints and seven assembly margins pass.

One 1,524,681-byte compressed bit input could not be materialized through the
available connector: file retrieval returned an empty large-file payload and
blob retrieval attempted UTF-8 decoding. Git blob checks caught this; the
missing file was not replaced or treated as verified locally. The exact-head
Python 3.13 Linux CI log was inspected and records the full bit ledger plus
`check_word`, `check_frames`, `check_lifted`, `check_stair` and its negative
control, all 138 source pins, and clean regeneration. All 39 jobs succeeded.
That is remote CI evidence, not a fresh local execution of those bit checks.

### Required verifier repair

`research/deferred-signed/verify.py` begins `main()` with
`assert __debug__`. Under `python -O` that statement and all the verification
assertions disappear. In a controlled local mutation, replacing the pinned
workflow hash with 64 zeroes makes `verify_pins()` raise `AssertionError` in
normal Python but return `138` under `-O`. Thus the reported pin count can
survive a bad pin without validating it.

Use an explicit module-level `if sys.flags.optimize: raise ...` before any
verification work, consistent with #101. A temporary test of that change
rejected `-O`, `-OO`, and `PYTHONOPTIMIZE=1` before argument handling. The
original PR file was restored afterward. Apply the same fail-closed convention
to directly runnable new checkers that rely on assertions; retain immutable
upstream snapshots. Add subprocess negative controls and refresh affected
source manifests/receipts. This finding concerns verifier behavior, not a
counterexample to the claimed finite network or multiplication theorem.

The all-size common-basis, precision, row-stock and fixed-tape applicability
arguments still require the stated proof review; arithmetic and finite CI
alone do not discharge them. Do not describe this pass as full acceptance.

## Queue order after these repairs

1. Integrate #101 and #90 with their authorship intact. Carry the strict scatter
   boundary into older pending packages that vendor or adapt the shared code.
2. Finish #97's verifier repair and retained-interface audit. Its physical
   ledger is an input to later constructions, so reviewing it once carefully
   is more useful than approving each downstream numerical claim separately.
3. Review #104's stopped product-ring and rational-center transfer, then the
   producer refinements used by #115/#117. These change mathematical interfaces
   and cannot be approved solely from passing parameter checks.
4. Review #130's three-stage Cayley-cover construction, arbitrary-subspace
   frames, weighted local-ring compiler, rare-class fallback and borrowed-row
   restoration before the #131/#137/#138/#142/#143 refinements. The larger
   submitted values remain unaudited here. Drafts remain drafts.

Other finite-search and composition contributions remain in the queue. They
should retain credit even when another construction supplies the selected
number. Do not close older PRs solely because a later title reports a larger
value. In particular, #74 and #82 have changed heads since their prior review;
those earlier reviews do not approve the new heads. The old #81 CI-coverage
finding also still needs resolution.
