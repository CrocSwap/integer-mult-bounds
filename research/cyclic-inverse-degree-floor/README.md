# Circle-gap inversion needs a growing degree factor

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped mathematical proof with exact finite corroboration.
There are explicit real dyadic polynomials of degree `d=2^(2s+2)-1`, for
every integer `s>=0`, with no zeros in the closed unit disk and circle gap
at least `1/2`, for which

```text
||1/P_s||_W                 >= 1 + sqrt(d+1)/4
||P_s(Z_L)^(-1)||_infinity   > 3/4 + sqrt(d+1)/4
L = (d+1)(2s+7).
```

The Wiener norm sums absolute Taylor coefficients; the matrix norm is the
maximum absolute row sum. Thus a degree-independent circle-gap inverse
bound fails even for exterior-root dyadic polynomials. The explicit cyclic
length is `O(d log(d+1))`. The same matrices have Euclidean inverse norm at
most two. [PROOF.md](PROOF.md) gives the all-parameter construction and proof.
No optimal growth rate, supplier admission or new kappa is claimed.

Rafael Guevara's [PR803](https://github.com/CrocSwap/integer-mult-bounds/pull/803)
leaves its degree factor nonoptimal. Its cited sufficient bound is linear
in degree on this exterior-root class. This contribution supplies a
square-root lower obstruction, using the classical Rudin-Shapiro pair and
a finite Neumann-tail transfer. It leaves a gap between the two growth rates.
The source theorem is a cited premise and motivation, not a replay target.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -X dev -I -B research/cyclic-inverse-degree-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -X dev -I -O -B research/cyclic-inverse-degree-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cyclic-inverse-degree-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cyclic-inverse-degree-floor --check-source-history
```

A reviewer can substitute another CPython 3.12 executable. The standalone
verifier writes no files and prints generated JSON with marker
`PASS_CYCLIC_INVERSE_DEGREE_FLOOR`, exact evidence and SHA256 of all six
package files. Redirect it to an external scratch path to retain a receipt.
No receipt is hand-written. The standalone command also works without Git
or predecessor files; repository metadata checks require Git provenance.

The finite checks cover:

- Four complete coefficient certificates at degrees `3,15,63,255` and cyclic
  lengths `28,144,704,3328`. Every pair autocorrelation is checked, and every
  Rudin-Shapiro coefficient agrees with the independent binary-adjacency
  formula. The unaliased first blocks and full polynomial Neumann residuals
  agree exactly, including every coefficient through degrees `21,135,693,3315`.
- Sixty-five exact parameter substitutions `s=0..64`, including the spectral
  contraction identity and the finite-length one-quarter tail inequality.
  Only `s=0..3` materialize the polynomial certificates.
- A separate dense rational solve of all 28 equations in the first circulant
  fixture, followed by literal cyclic convolution. Its inverse row norm is
  exactly two, consistent with the proved strict lower bound `5/4`.
- Seven controls reject a negative level, a Boolean parameter, an excessive
  polynomial family, a broken flat-pair identity, a wrong inverse sign,
  reversed cyclic direction and a singular inverse system.

The all-size assertion follows from the written proof. The finite corpus
does not prove it by sampling and does not enumerate a production multiplier.

## Scope and implementation limits

The `uniform-transfer-audit` card is changed to a new component obstruction
for the analytic-recovery norm-transfer question. It discharges none of
the selected frontier's five assumptions. This is a side result, not a
source-specific obstruction to a PR621 kernel or to stronger special-kernel
bounds. No predecessor scientific suite is rerun.

No coefficient preparation, rounded recurrence, dirty restoration, physical
tape/storage cost, complete caller, supplier admission, selected-frontier
change or complete multiplication theorem is supplied. Lean, Docker and
the selected cold replay are unrun. Independent human and formal proof-kernel
review are unclaimed.

The verifier uses no recursion or subprocess. Materialized polynomials have
at most 3,316 coefficients; its bounded multiplication helper accepts at
most 3,329 coefficients per input. Dense elimination uses 28 rows of 29
rational entries. Functions remain below 60 lines and explicit exceptions
keep scientific checks active with optimization. Warning-strict ordinary
and optimized Python runs are registered. AST compilation passes; the largest
function has 32 lines. No separate static analyzer is installed.

Power of Ten deviations are limited to Python's required dynamic allocation
and the named rejection-control callback targets. Polynomial degrees,
coefficient inputs, 65 scalar parameter cases and the 28-equation system
bound live arithmetic storage. At most one certificate is materialized at
a time. The control callbacks are local, explicitly named functions;
no plugin dispatch or runtime code generation is used. A lower-level
implementation or an expanded input domain would need its own allocation
and dispatch review. No shared build settings are changed.

## Credit and overlap

Credit Rafael Guevara / alephnan for PR803's circle-gap inverse setting and
unresolved degree factor, and Ali Romman / PR621 for the cyclic-kernel context.
Golay, Shapiro and Rudin retain credit for the classical flat-polynomial
construction. The inspected exposition by Paul Balister is linked with
precise locators in PROOF.md and SOURCES.json. The recurrence and needed
energy identity are proved here; no global literature-priority claim is made.

Nick Petalas's older PR4914 concerns the sharp fixed mixed quadratic, and
PR5080 improves an upper-bound constant. They are related context, not
the source of this target or executable dependencies. Their upper results
are not independently rechecked. New files are confined to this package.

Historical source pins use main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
Live claims, local reservations, current main README searches, merged formula
and object searches, and open/account PR data were inspected. The cached
overlap report has complete remote pagination but incomplete sparse local
note coverage. Unpublished work and arbitrary historical diffs remain outside
coverage. These searches are not a novelty certificate.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361635).

## Open next questions

1. What is the optimal degree dependence for exterior-root polynomials?
   Start with a direct upper estimate exploiting the missing interior poles,
   or a lower family using more than the isolated first coefficient block.
   A matching bound would close the square-root versus linear gap. Neither
   such estimate nor a stronger construction is supplied here.
2. Can an actual prime-power cyclic kernel avoid this generic penalty through
   its arithmetic structure? First identify a source-bound kernel constraint
   that excludes this family, then retain all costs in a rounded consumer.
   Source-specific structure, preparation and the full rounding recurrence
   remain blockers.

Structured questions and the changed scope are in TASK.json.
