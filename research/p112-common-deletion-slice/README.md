# One complete common-deletion slice of C5

Fix the P112 root frame and six-dimensional binary label space `V1` in
[FIXTURE.json](FIXTURE.json). For **every** six-dimensional `V2` in `F2^9`
and every common set `P` of at most four live root lines, put

```text
X    = Lambda(V1) union Lambda(V2) union P
H(X) = {h : binary_rank(labels(Off(h) minus X)) <= 7}.
```

**Result.** The sharp maximum of `dim span H(X)` is **four**, over either the
real or complex numbers. This completes one first-space slice of the
[C5 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156).
It does not settle the other first spaces, C5, the full decoder-cost conjecture,
or a multiplication exponent. The selected frontier is unchanged.

[PR3160](https://github.com/CrocSwap/integer-mult-bounds/pull/3160) fixed **both**
spaces and proved sharp span three. Here only its first space is fixed; all
788,035 partner spaces are covered. The shared four-line budget is essential.
No direction gets its own deletion set.

Concurrent [PR3161](https://github.com/CrocSwap/integer-mult-bounds/pull/3161),
head `a1aba8389b87412e6f72ccf4d11f31e0ea232327`, now reports a global rank-six,
eight-deletion result and closure of the historical `(5,3)` beta cell. That
moves the original application forward; this package does not claim another
missing implication for that cell. Its new result is the sharp **rank-seven**,
common-four-deletion first-space slice, a different statement not implied by
the reported rank-six bound. This also supplies a complete calibration slice
for a future all-first-space rank-seven computation. The PR3161 theorem and
its newer follow-ups were not independently replayed here.

## Proof and exact computation

The executable certificate follows these implications. The written argument is
part of the result, not a claim of proof-kernel verification.

1. **Bound the possible orthogonality systems.** Independently enumerate all
   43,435 seven-dimensional binary spaces, obtaining a maximum of 36 live
   labels. The scanner enumerates all six-dimensional spaces and obtains a
   maximum of 20. Thus every admitted direction has
   `|Off(h)| <= 20 + 20 + 4 + 36 = 80`, and at least 32 live roots orthogonal
   to it.
2. **Cover all directions, including planes.** The E8 Weyl group is finite
   because it permutes the spanning root set. Choose `rho` with strictly
   positive simple-root pairings. A maximum of `rho dot w(h)` moves any real
   direction into the closed dominant chamber. Otherwise reflecting a negative
   simple pairing increases the maximum. There a positive root is orthogonal
   exactly when its simple support is contained in the zero simple pairings.
   Consequently every orthogonality system is a Weyl translate of a proper
   parabolic subsystem.

   Check all 255 proper simple-support subsets. Those with at least 32 root
   lines give four orbits, with sizes 1,120, 120, 3,360 and 1,080. All their
   live intersections have size at least 32. There are 4,560 rank-seven systems
   and **1,120 rank-six systems**. The latter have two-dimensional normal
   spaces. For each system the model uses the union of the nonzero supports
   of an exact integral normal basis. This is the generic support in that
   space. If it qualifies, every vector in the normal space qualifies by
   monotonicity. An exceptional vector has additional orthogonal roots and
   occurs under its own parabolic system. No catalogue-only or root-only
   restriction remains.
3. **Enumerate every partner space.** Every three-dimensional annihilator has
   a unique reduced row-echelon matrix. Enumerating its pivots and free entries
   covers 788,035 six-dimensional kernels. Their live-label masks have 776,806
   distinct values. Merging equal masks is sound because `H(X)` depends only
   on these live intersections. A second implementation, using successive
   least coset representatives instead of RREF, checks the full mask list
   and the multiplicity histogram.
4. **Find all relevant cuts.** A residual label set has rank at most nine.
   Rank at most seven needs no cut. At rank eight, a cut lowers the rank to
   seven exactly when it contains the nonzero support of a restricted binary
   character. At rank nine, it must contain the union of two distinct nonzero
   restricted character supports. The restriction map is injective in this
   case, so the two characters are independent. Enumerating all 512 characters
   and all relevant pairs therefore covers every cut of size at most four.
5. **Preserve one common set.** Start with the empty cut, and successively
   retain each old state or its union with a cut option for one system, only
   when the union has at most four lines. For any actual `P`, select one cut
   contained in `P` for each system it admits. Their union is a generated state,
   is contained in `P`, and admits exactly the same systems. Hence it suffices
   to check these states, without enumerating irrelevant supersets of `P`.
6. **Check the span.** There are 795,182 states across all partner masks, at
   most 16 per pair. At most 32 orthogonality systems qualify separately; no
   normal plane qualifies. Each admitted list with no more vectors than the
   running maximum has that immediate dimension upper bound. The remaining
   197 cases use arbitrary-precision integer elimination. The Python checker
   separately interprets every one of those boundaries, recomputes its
   residual binary ranks and checks its rational rank using `Fraction`.
   The maximum is four. [RESULT.json](RESULT.json) records the exact receipt.

For complex `h = a + ib`, a generic real combination of `a` and `b` has the
same zero pairings on the finite root set. Both components lie in the normal
space of that system. The computation includes its entire complex normal
space whenever its generic support qualifies. Rational basis ranks are the
same over `R` and `C`, so the same upper bound follows.

## Sharpness witness

One partner is the common kernel of binary characters `195, 8, 160`.
The common deletion labels are `{297, 299, 361, 363}`. Four independent directions
are the rows of

```text
 1 -1  0  0  0  0  0  0
 1 -1  1  1  1  1 -1  1
 1 -1  1  1 -1 -1 -1  1
 1 -1  1 -1  1  1  1  1
```

Their four residual binary ranks are all seven. Removing the common deletion
set invalidates this fixture. The checker independently reconstructs these
claims from the literal roots and labels.

## Reproduction

The tested environment is Linux x86-64, CPython 3.12.15, GCC 14.2.0 and
Boost.Multiprecision headers. Python has no third-party dependencies. GCC or
Clang must support `unsigned __int128`. The optimized scanner requires x86-64
POPCNT and rejects an unsupported CPU before scanning. This is not a native
Windows package. The dedicated workflow installs the compiler and Boost headers
on Ubuntu.

From the repository root, with an existing external scratch directory:

```sh
export TMPDIR="$RUN/tmp"
mkdir -p "$TMPDIR"
python3.12 -B scripts/research_package.py --package research/p112-common-deletion-slice
```

The registered commands run the complete scan and fifteen behavioral groups.
Direct commands also work in a Git-free export:

```sh
python3.12 -B research/p112-common-deletion-slice/verify.py --output "$RUN/replay.json"
python3.12 -O -B research/p112-common-deletion-slice/test_verify.py
```

Expected marker:

```text
PASS_P112_COMMON_SLICE flats=788035 masks=776806 systems=5680 common_span=4
```

Builds and temporary exports go under `TMPDIR` and are removed on exit. The
verifier does not regenerate committed files. `--bootstrap` still runs every
mathematical check but skips comparison with a prior receipt; it is only for
explicit receipt generation. [EVIDENCE.md](EVIDENCE.md) lists checks, resource
bounds and remaining verification limits.

## Open next questions

- Can the same shared-cut calculation cover the other first-space orbits?
  That would complete the stronger rank-seven relaxation. First identify a
  remaining caller that needs it, then bind the representative list and its
  frame-preserving action to these labels before scheduling disjoint slices.
  Their coverage, total cost and present application are not certified here.
- Can the absence of qualifying normal planes be proved uniformly in `V1`?
  That could remove an entire continuous family from later slices. Start
  with the rank-six parabolic orbit and its exact character cuts. This slice
  alone gives no uniform exclusion.

## Sources and credit

DreamingOfClouds's [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154),
head `708f0ad8928c383de8294aea3c126e9461d2066d`, supplies C5, FINITE/FINITE2,
the TWOSIDE application and the retained decoder-floor lineage. Its two
implementations establish the earlier `p=2` result, not this common-`p=4` slice.

Nick Petalas's [PR3158](https://github.com/CrocSwap/integer-mult-bounds/pull/3158),
head `8e2167bac550bd653bb74c50c1f7c3f14b6c1f70`, supplies the literal first
space and frame through the quantifier fixture. His
[PR3160](https://github.com/CrocSwap/integer-mult-bounds/pull/3160), head
`9ab8c4cc2aed4a87293d7d04b2abfdf854ae43e2`, supplies the geometry implementation
adapted here. This successor lowers its orthogonality cutoff from 40 to 32 and
retains normal planes. The new scanner imports neither FINITE implementation
nor their direction tables.

[SOURCES.json](SOURCES.json) records exact historical blobs and hashes.
Historical source heads are provenance, not runtime dependencies; the standalone
checker cannot authenticate those remote commits without Git objects or network
access. Local source comparisons were performed before publication.

Canonical baseline is `997e6a9ca7b4f95d50e366f61412fd640d72a88a`, priority
revision 6. Apache-2.0. Development and internal checking used substantial
automated assistance. This is author-checked finite evidence, not independent
human review, supplier admission or a full multiplication theorem.
