# A monogenic obstruction beyond diagonal Borel gauges

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with exact finite corroboration. No new κ.

A dyadic full-Borel superposition word cannot save paid rank when every
applied block is a Z_(2)-polynomial in one rational matrix T with 2-integral
characteristic polynomial, and its transformed data targets meet the cited
unit contract. In particular, targets n_I require total paid rank at least
mW for every width m, data-register count W and auxiliary count. The full
normalized power bill is then at least one for every saving in [0,1].

The constructive test is

```text
χ_T has odd-denominator coefficients
  => L = R^m + TR^m + ... + T^(m-1)R^m is invariant
  => one common paired analytic basis makes all applied blocks integral
  => the cited PR2613 rank theorem gives sum_paid rank(A) >= mW
```

If T itself occurs as an actual applied block, the characteristic-polynomial
condition is also necessary for a common paired lattice. A negative answer
is only a lattice obstruction, never evidence of a favorable word.

[PROOF.md](PROOF.md) supplies the quantified proof, the exact endpoint
contract and an explicit width-three family for every denominator 2^s,
s >= 1. That family has neither an original-coordinate diagonal gauge nor
a complete rational rank-one projector family in its applied block algebra.
It has useful ranks one and two, noncommuting address labels, and a sharp
abstract endpoint with paid rank three per data role. This broadens the
available obstruction filter without supplying a new physical operation.

## Evidence and reproduction

The standalone replay checks all 625 two-by-two matrices with entries in
{-1,-1/2,0,1/2,1}. It constructs and independently checks 125 stable lattices
and certifies a nonintegral characteristic coefficient for the other 500.
The checker uses a determinant expansion, separate from the producer's trace
recurrence. Four further matrices cover dimensions one and four, repeated
factors and odd denominators.

Eight explicit family parameters check the written basis, every applied
matrix in the actual word, the complete unit endpoint and noncommutation.
Literal F2[group] replay returns diag(g,g,I) after mixing/unmixing two data
roles and retaining an arbitrary dirty role. Twelve rejection controls and
five scope controls cover invalid bases, incorrect negative certificates,
unsupported inputs, an omitted free map, singular free reductions, an
actually applied inverse, nonintegral polynomial coefficients, distinct H/D
scalings and an unapplied generator.

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/monogenic-borel-lattice/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/monogenic-borel-lattice/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/monogenic-borel-lattice
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/monogenic-borel-lattice --check-source-history
```

Another CPython 3.12 executable may replace the displayed local path. The
direct marker is `PASS_MONOGENIC_BOREL_LATTICE`; the registered launcher also
prints `PASS_REGISTERED_RESEARCH_PACKAGE`. Each direct run emits a fresh JSON
receipt bound to the SHA256 of every package file. It writes no receipt or
other generated file into the checkout. Checks use explicit exceptions and
remain active under optimized Python.

The bounded constructor's public interface is `lattice.solve(T)`. It supports
dimensions one through four and exact integer/Fraction entries with numerator
and denominator lengths at most 64 bits. It returns a stable-basis certificate
or a nonintegral characteristic coefficient. Input limits are implementation
limits, not negative mathematical results. The theorem has no dimension cap.

Local warning-strict normal and optimized commands passed on CPython 3.12.15
on Darwin arm64. Each took about 0.11 seconds, against its 120-second timeout.
These are replay-budget measurements, not a performance improvement claim.
Registered replay and source metadata validation passed. In-memory Python
compilation, AST inspection and the whitespace check passed. No external
linter was run. All functions are below 60 physical lines.

## Scope and credit

Sagar Thakrar's [PR2613](https://github.com/CrocSwap/integer-mult-bounds/pull/2613)
supplies the dyadic-register question and the cited source-model rank theorem.
eumemic's PR288 supplies its general superposition/lattice framework, and
Swapnil Jain's P1 supplies the retained rank functional. The source theorem
is used as a premise; no predecessor executable is imported or reverified.

ywz65's PR2671 supplies the separate coordinate-diagonal gauge filter.
Nick Petalas's older PR6027 supplies a distinct complete-projector-anchor
test. Neither covers the displayed nonsplit family under its stated premise.
Neither theorem is needed in the new proof. Cayley-Hamilton, finite modules
over a PID, valuation-based elimination and the quadratic algebra's
idempotents are classical. No global literature priority is claimed for
those ingredients. Exact predecessor paths are provenance pins in
[SOURCES.json](SOURCES.json); existing credits and sources remain unchanged.

The `bit-new-register-model` card is explicitly changed to this analytic
side obstruction. It does not add a native alphabet or demonstrate a saving.
The source is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision 8. The selected binding-only baseline passed and gives
κ = 781451/250000000; historical orientation prose names an older checkpoint.
The selected frontier is unchanged. [Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19440637).

The complete applied block list and its R[T] representations remain caller
hypotheses. An inverse actually used must satisfy them too. Polynomial
coefficients over Q alone are insufficient. Unrelated H/D bases can lose the
unit target, and failure of this test says nothing about other representations.
The analytic basis is not supplied as a free physical gate. General
unanchored matrix algebras, native realization, dirty restoration beyond the
stated endpoint, full cost/precision/stock/tape, compiler and outer admission
remain outside scope. No selected scientific replay, Lean or Docker ran.
Independent human and formal proof-kernel review are unclaimed. All five
selected framework assumptions remain.

## Open next questions

- Does one concrete candidate dyadic Borel word expose a complete monogenic
  block list? First write every applied block, including inverses, as an
  R-polynomial in a common T and test the actual target units. The original
  endpoint and native legality must be supplied separately.
- Which two-generator block algebras admit an equally finite common-lattice
  certificate without complete rank-one anchors? Start with two noncommuting
  rational matrices and their finite module closure. Individual integral
  characteristic polynomials do not guarantee a common invariant lattice.
  This package supplies neither that decision algorithm nor a new search.

## Related open work and CI

Live overlap checking includes current-main README searches, merged-PR
searches and the open PR/Discussion corpus. Sparse local-note coverage is
incomplete, so an empty search is not proof of novelty. No open PR found in
that bounded search studies this monogenic common-paired-lattice criterion.
Related full-Borel exclusions already merged as PR2613, PR2671 and PR6158
retain different hypotheses. The latter deletes one lower-only phase; this
criterion allows arbitrarily interleaved maps satisfying its algebra condition.

CI is pending at publication. The registered normal and optimized commands
are intended to run in CI; scientific acceptance remains separate from
source-bound replay success.
