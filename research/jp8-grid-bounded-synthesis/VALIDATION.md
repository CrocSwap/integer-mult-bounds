# Validation record

Date: 2026-10-13. Base `f567884aeb8851b6e794af1184119a3bfbe1e631`.
Local macOS arm64, CPython **3.14.7** and **3.11.15**; standard library only.
No remote Linux, full repository suite or Lean result is claimed.

## Executed checks

1. `python3 -I -O -B research/jp8-grid-bounded-synthesis/verify.py` and the
   same command under `python3.11`: PASS. All 49 nonunit coefficients are
   reconstructed; seven strictly improve all four Horner variants. Complete
   source closure, type-preserving certificate comparisons and every field of
   [EXPECTED.json](EXPECTED.json) match. The circuit certificate and emitted
   words are unchanged from the initial submission.
2. Independent Bellman/potential checker: PASS for 3,703 vertices and 14,311
   distinct directed edges, exact coefficient coverage, four adverse controls,
   eight elementary distance checks and all five preparation primitive types.
   `crosscheck.py --self-test` also passed standalone.
3. Complete three-way primitive replay: PASS on both orientations, each with
   716 logical and nine arbitrary private input columns, 22,693 scalar macro
   boundaries, restored 492 helper columns and erased private registers.
   The historical, PR696 and replacement bills are respectively
   `257232/200380/200276` forward and `257280/200396/200292` backward.
   Exact maximum scalar fractional denominator exponents agree at 4 and 27.
   Exact maximum scalar-prefix row-L1 norms agree at `503316465` forward and
   `1469388997/2` backward in all three traces.
4. Independent integer replay: PASS for both complete orientations, using
   normalized sparse integer rows with a common power-of-two denominator.
   It imports neither `Fraction` nor any project module, independently emits
   PR696/replacement words, and compares each macro with direct integer
   semantics. The main verifier requires its full primitive-stream hashes,
   bills, tags, reads, denominator/row-L1 maxima and all shared accounting fields to
   match the Fraction implementation. Six adverse controls and six elementary
   integer/NAF cases pass.
5. Source-read Pareto certificate: PASS on all 49 graphs, 3,703 vertices,
   4,104 state labels and 16,096 edge-label closure obligations. Every label
   has a checked rational witness; all edges preserve antichain coverage.
   All submitted shortest witnesses minimize reads among shortest words.
   Exactly the seven selected coefficients have two Pareto options; four
   adverse controls pass. Occurrence-weighted instruction/read deltas agree
   with the complete primitive replay. This diagnostic changes no circuit.
6. `python3 -I -O -B research/jp8-grid-bounded-synthesis/test_package.py`:
   **14 tests PASS** on CPython 3.14.7 and 3.11.15. This includes a minimal
   checkout without Git metadata in a path with spaces, a different working
   directory and recompressed gzip input. Controls reject source/reference
   byte changes, missing pins, forged source identity, omitted coefficients,
   altered paths, altered JSON types and forged receipts. Existing output is
   preserved. Every subprocess also uses isolated optimized Python.
7. `python3 -I -O -B research/jp8-grid-bounded-synthesis/test_independent.py`:
   **six tests PASS** on both Python versions. Differential checks cover 7,000
   signed row multiplications, 39,200 row sums,
   1,400 intermediate primitive states and all 383 supported comparator
   coefficient pairs. Graph mutations cover 114 single-potential changes,
   missing/extra potential vertices and every one-operation deletion from
   the `7/4` witness. The bounded corpus spans denominator depths 0 through 27;
   it complements, rather than replaces, complete source-program replay.
   A separate scaled-integer Dijkstra calculation checks all 49 graphs at ten
   exact hypothetical read prices (490 graph/price cases), without importing
   the Pareto search, successor function or sensitivity code. It confirms
   the four aggregate interval costs, paid copy/accumulation/clear overhead,
   and both adjacent choices at all three breakpoints.
8. `make selected-record-check`: PASS, current PR799 exact kappa
   `1661634653669567/1000000000000000000` and source/proof inventory.
9. Whitespace and scope checks: PASS. Only this new research directory is
   included. `upstream/`, existing source packages and selected certificates
   match the exact base commit.
   An export of the exact staged Git blobs also passes optimized verification
   and the six independent tests without Git metadata, in a path with spaces.

## Adversarial review and corrections

The initial nine-test package passed before submission. Further independent
AI-assisted review found that Python value equality accepted JSON `true` in
place of integer `1`, and integral floats in place of integer certificate or
receipt counts. It also found that descriptive source-head/base/provider
metadata could be relabelled without changing the correctly pinned payloads.
These were checker-boundary defects, not counterexamples to the submitted
circuits. The main verifier now compares type-preserving canonical JSON,
checks exact provenance identity, and passes the submitted certificate entries
to the independent graph checker after reconstruction. Five new regression
tests exercise these failure modes. A separate reviewer reran the four input
corruptions and confirmed rejection under `-I -O`.

An earlier test expected an overly narrow error-message regex (`coverage`
versus `does not cover`). Correcting the regex did not alter the checker, which
rejected the missing coefficient throughout. The Pareto receipt wording was
also narrowed to **submitted** shortest witnesses: other shortest words can
use more source reads, as `double` versus `add` for coefficient two demonstrates.
No mathematical failure was suppressed to obtain a passing result.

## Interpretation and review status

The full scalar replays execute primitives; they do not interpret frame changes
or recursive children as physical numerical operators. Event/frame hashes are
preservation evidence by construction, and paid profiles are checked against
the pinned receipt. The nonincrease of magnitude and scalar fractional depth
also follows from the local substitution proof, separately from finite tests.
All source accesses in the primitive model are charged, including 92 more real
macro-source reads per orientation in the submitted replacement.

The two-coordinate audit makes that tradeoff explicit. Its hypothetical extra
read overhead is not a physical price or runtime benchmark. Alternative Pareto
words and aggregate menus are certified diagnostics, not installed or separately
replayed full programs. In particular, equal aggregate read counts do not prove
equal source-location, frame or physical access costs.

No full `make verify`, selected cold reconstruction, regenerated global invoice,
owner admission, native phase/wrapper rebuild, production compiler integration,
remote CI or formal multiplication theorem is asserted. None of those artifacts
is modified. Those inherited or integration obligations remain outside this
finite research contribution. The selected kappa is unchanged.

The [overlap record](OVERLAP.json) preserves the original pre-submission check
and a continuation refresh through PR893. The base and eight dependency heads
remain unchanged. No pinned sprint coordination issue is available; the local
claim already records the result and existing PR882. All subsequent evidence
stays in that same contribution. Independent implementations and reviews here
are AI-assisted; no independent human mathematical review is claimed.
