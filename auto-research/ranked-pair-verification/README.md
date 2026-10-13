# Independent verification of rank-first pair profiles

This directory preserves the first PR64 checkpoint. The later completed
real-characteristic, physical-interface, localization, ambient-frame and counter
proofs, plus newer finite audits, are in
[machine-transfer-verification](../machine-transfer-verification/README.md).
Its README gives the current proof boundary and reproducible checks.

This contribution certifies the rank-first pair construction and supplies the
conditional witness

```
kappa = 20411033624901463 / 400000000000000000000
      = 5.10275840622536575e-5
a_bit = 63787735011827529 / 1250000000000000000000
h     = 1 / 1000000000000000000
```

**Concurrent work:** Dominik Scholz's [PR #63](https://github.com/CrocSwap/integer-mult-bounds/pull/63)
independently publishes the same composition. Its decompressed words, complete
profiles, and finite bridge are identical to ours. The gain over #63 is only
parameter refinement: `5624901463 / 400000000000000000000`, approximately
`1.40622536575e-11`. We make no exclusive construction or priority claim.
See [the immutable comparison](pr63-comparison.json).

The main additions are independently coded word/scatter/charge checks, exact
characteristic and assembly arithmetic, an all-exponent concave-profile proof,
and five Lean files containing 45 audited theorems. The ranked profile is
strictly better than **PR62's original stacked profile** for every saving
`0 < a < 1`, at unchanged `m=575`, `W=137151806`, total rank `78860441550`,
deficit `1846900`, and maximum child width `529`.

This package does not establish the full uniform finite-alphabet multitape
multiplication theorem. Physical compiler, all-size tape recurrence, routing,
analytic resampling, prime setup, precision and exact recovery remain external
application obligations. Existing written arguments were reviewed in a focused
way; incomplete mechanization is not a counterexample to those arguments.
The repository's main released construction is not replaced by this package.

## Review map

- [PROOF.md](PROOF.md): exact refinement, cap identity, concurrent work and credits.
- [selected-certificate.json](selected-certificate.json): full child distribution,
  bit/complex bridge, exact parameters, all 47 slacks and seven margins.
- [selected-moment-verification.json](selected-moment-verification.json): independent
  outward rational logarithm/exponential enclosures and adjacent root bracket.
- [selected-assembly-verification.json](selected-assembly-verification.json):
  separately transcribed assembly arithmetic.
- [lean/README.txt](lean/README.txt): proof scope, exact toolchain and axiom audit;
  [declaration map](lean/declaration-scope-map.json) covers 99 actual declarations.
- [transfer-review.txt](transfer-review.txt): fixed-frame wrapper phases, floor
  remainders, row stock, spectators, parking and eligible-prime obligations.
- [research-addendum.tex](research-addendum.tex): the original self-contained
  mathematical addendum, preserved as a dated research snapshot. It predates
  PR63; this README and PROOF.md supply the later concurrent-work comparison.
  The existing upstream and repository notes are unchanged.
- [assembly-barriers.json](assembly-barriers.json): exact architecture-specific
  ceilings with the retained complex saving, not universal lower bounds.
- [finite-frames/source-word-manifest.json](finite-frames/source-word-manifest.json):
  immutable source/word hashes and the single compiler transformation.
- [compiler-rank-order.patch](compiler-rank-order.patch): reviewable one-line patch
  against the pinned PR62 compiler. Reproduction uses an unmodified checkout
  and applies this transformation in memory, so do not apply the patch there.

## Reproduce the exact offline certificate

Python 3.11 or newer; no third-party packages. From the repository root:

```sh
make ranked-pair-check
```

This checks word hashes, complete child reconstruction, the literal Lean profile
and parameter bindings, signed cap certificates, the exact characteristic root
bracket, all 47 strict inequalities and seven final margins. It compares against
checked-in receipts without rewriting them. It is included in `make verify`.

## Full independent finite replay and fresh CRT profiling

Clone the public construction into an ignored directory and select its exact
commit (a moving PR head is insufficient):

```sh
git clone --no-checkout https://github.com/CrocSwap/integer-mult-bounds.git build/ranked-pair-upstream
git -C build/ranked-pair-upstream fetch origin ad0f25ff7b23cff7f08ad237c2254e6ecf74257e
git -C build/ranked-pair-upstream checkout --detach ad0f25ff7b23cff7f08ad237c2254e6ecf74257e
make ranked-pair-verify UPSTREAM=build/ranked-pair-upstream
```

Requires a C++17 compiler. The separate interpreter replays every source,
output and arbitrary dirty basis direction in both orientations; binds literal
scatter and frame incidents; reconstructs the complete transition input;
rebuilds and runs the pinned exact CRT profiler; then compares profiles and
child counts with the selected certificate. Generated binaries, logs and
receipts stay under `build/`. CI runs this independently of the offline check.

To regenerate the words themselves using the same immutable sources:

```sh
python3 research/ranked-pair-verification/finite-frames/explore_pair_reclamation.py --upstream build/ranked-pair-upstream --generated build/ranked-pair-generated --priority ranked --h 23
python3 research/ranked-pair-verification/finite-frames/explore_pair_reclamation.py --upstream build/ranked-pair-upstream --generated build/ranked-pair-generated --priority ranked --h 25
```

The generator rejects modified source files and records the exact source
transformation. Compare the decompressed word SHA256 values with the manifest.
The independent audit above checks the shipped words without trusting this
producer implementation. Tampering controls and their pinned PR60 dependency
are documented in `finite-frames/README.md`.

## Lean

Use the existing Lean 4.21.0 / pinned Mathlib project:

```sh
(cd formal/lean && lake exe cache get)
make formal-ranked-pair-verify
```

The portable checker recompiles all five unchanged source files and audits all
45 theorem declarations, permitting only Lean's standard foundational axioms.
It is also included in `formal-historical-verify`, so existing formal CI runs it.
No `sorry`, `admit`, custom axiom or `native_decide` is used. The real
transcendental enclosure proof and compiler/tape transfer are not silently
claimed as Lean results.

## Provenance and license

The graph is Avi Eisenberg / ikeboy's PR62; the joint frame compiler is
eumemic's PR57; descending-rank retired-slot priority is Chafik Boukhalfa's
PR60. Dominik Scholz's PR63 is the independently published identical
composition. See PROOF.md for the full inherited credit chain. This verification
and formalization used substantial OpenAI Codex assistance, including
independent subagent checks. New sources follow the repository's Apache-2.0
license; retained source-specific notices remain applicable. No human
peer-review, practical speedup or global optimality claim is made.
