# Fixed middle basis with copied reversed corners

Under the inherited analytic and fixed finite-alphabet multitape hypotheses,

$$T(n)=O(n(\log n)^{1-\kappa}),\qquad
\kappa=\frac{971668963}{25000000000000}=3.886675852\times10^{-5}>2^{-15}.$$

This specializes only the middle basis of [PR #37](https://github.com/CrocSwap/integer-mult-bounds/pull/37), pinned at
`2f7578affce416ad4b6c41f3438ebb734f66a899`: the ordered bit dimensions remain
(23,25), the first factor remains generic, and the second factor is fixed to
I+J. The complete original-envelope local profile replaces the entire
second-factor generic profile. The copied-center transforms remain paid.

The result is approximately **0.9324% above PR #37** and **0.011627% above
PR #38** (`cc794077f6c103e24ec0939be765cd1521239aab`, kappa=3.886224e-5).
PR #38 fixes both factors and uses a conservative single 21-block. Here a
common generic first basis retains the reversed **21+17** blocks while the
middle factor gains its exact fixed-basis profile. These are conditional
asymptotic exponent comparisons, not runtime measurements or global optimality.

## General argument

The [geometry proof](geometry-proof.txt) establishes compatibility in the
single family T_M(L23 tensor (I25+J25)), with the exact same controlled
permutations and physical coordinate order as PR #37. Universal rank-cut
identities from James Chang's PR #34 specialize to this family. For every one
of the 2,300 middle-factor triple lines, an exact modular witness proves all
47 required rational prefix minors are nonzero. Modular zeros are only
regression checks: the all-parameter rank-cut identities supply the proof of
zeros. The finite product of nonzero functions on irreducible GL23 gives one
rational first basis satisfying every physical occurrence simultaneously.

The proof also derives all 25 copied-center rank-one complements explicitly,
checks their nonzero coordinates and actual controlled local contractions,
and retains all rank-24 transforms on the copied streams. Thus the data
profile remains **9 singletons + [21,17,481]**. Every claimed block is an
actual contiguous physical interval; no free gather or runtime basis change
is introduced. The first-axis generic envelopes and the second-axis original
envelopes are independently compatible with their unchanged scalar graphs,
original oriented matchings, input and output interfaces.

The fixed second-axis local profile is computed from every actual transition,
not inferred from a rank histogram. The [independent CRT audit](review/fixed25-copied-crt-audit.txt)
gives a uniform integer-minor bound for diagonal masks plus rank-at-most-four
corrections. Every one of the 96,273 transition matrices is checked with five
primes. Their product exceeds the bound; every frame denominator is invertible.
For each northeast submatrix, its rational rank is the maximum modular rank;
mixed differences recover the ordered pivots. This proves the zeros as well
as nonzeros needed by the complete fixed local profiles.

Copied retained centers replace exactly 25 identity width-25 calls by 25
rank-one complement calls. All other fixed-profile entries, including every
paid rank-24 copied transform and its actual ordered profile, are retained.
The complete local rank falls from 1,283,675 to 1,283,075, as required by the
copied schedule. No second copy saving is added elsewhere.

## Accounting and transfer

The complete child list has 27 widths. It retains N=4,073,300 paid endpoint
corrections, W=188,181,929 role volume, m=575, L=2,226,400 and total rank
Wm-N+L=108,202,762,275. The complete new internal histogram is replicated
N/2300=1771 times. Every other PR #37 physical class is unchanged.

The exact bit saving is **3886826921/10^14 = 3.886826921e-5**.
Rational logarithm/exponential enclosures give a strict bit moment gap above
2.3000e-15. The inherited PR #36 complex moment is replayed at saving717/10^7,
using its actual (28,28), mixed-center19 construction. Its semantic envelope
E=64*(W_complex+m_complex+G_scalar+1)^3 retains the scalar gate charge;
C1=1 and product row stock p^2000 remain. Balanced semantic/bulk assembly
uses the PR #37 exact formulas and recomputes all47 strict constraints,
seven margins and eventual cutoffs. Final absorption gap exceeds6.2496e-15.
The next bit grid point of size1e-14 is excluded by a rigorous lower bound
for this same finite profile, without claiming global optimality.

The general copied-stream proof, restoration of arbitrary dirty scratch,
sequential fixed-tape role storage, analytic recovery, eligible prime
existence, constructive setup and eventual thresholds remain inherited
hypotheses. Changing address bases does not change scalar identities or
permit uncharged copying. See the parent guide and retained manuscripts for
those interfaces. Exact finite certificates do not prove the entire
conditional multiplication theorem formally.

## Reproduction

```sh
make copied-fixed-reversed-check
make copied-fixed-reversed-producer
make verify
```

Use Python3.11 or newer and a C++ compiler. All sources and fixtures needed
for reproduction are in this checkout; no sibling checkout is required.
The producer target regenerates the actual base-two graph, original labels,
oriented matching and complete five-prime profile. The check target replays
geometry, exact moments, constraints and negative controls. The focused
[patch](../../patches/copied-fixed-reversed.patch) applies to the pinned PR #37
commit. The inherited manuscripts are unchanged.

**Full verification passed** at research commit `50e54ece17afa4bd3cccd1927e9cdea5098038c2`: 192 tests, fresh producer/profile and geometry checks, and 18 historical patch checks. The ten focused tests also pass. The [validation receipt](validation.json) records the exact source commit and full log hash. This remains a conditional research result requiring mathematical review.

## Attribution

Rohan Arun, with substantial OpenAI Codex assistance, supplies this
fixed-middle/reversed-corner composition, common-basis proof, complete
controls and integration. Credit icekylinx for PR #32 fixed projectors and
profiling, PR #36 copied centers and complex construction; James Chang for
PR #34 reversed corners; Dominik Scholz for fixed-basis and dimension
refinements, including the live PR #38 comparison; Zhihao Chen/jacklightChen,
Aurel Prosz/Paureel, Swapnil Jain, RaD/hipotures, eumemic, Douglas Colkitt,
OpenAI, Harvey–van der Hoeven and every retained predecessor notice.
Inherited techniques are not claimed as new here. Original Apache-2.0/CC0
notices and historical AI-assistance disclosures are preserved.
