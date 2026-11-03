# Linear error is unavoidable for the absolute rounded inverse oracle

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof with exact finite corroboration.

For every integer p>100, two entrywise nonnegative 2-by-2 operators have
the same odd, zero-preserving rounded oracle under PR1430's absolute error
contract, but their inverse answers differ by more than `(8/9)p*2^-p`.
Every algorithm that accesses the hidden operator only through that oracle
therefore has worst-case error greater than `(4/9)p*2^-p`, even with
arbitrarily many adaptive queries. The lower bound also holds for randomized
expected error. At any radius smaller than the exact two-instance radius,
one instance has success probability at most one half.

Hanson Sun / bbMisk's [PR1430](https://github.com/CrocSwap/integer-mult-bounds/pull/1430)
supplies the cited numerical contract and the `<p*2^-p` fixed-source Horner
upper bound. This new lower bound makes the error order optimal for that
oracle model. It is not an audit or replay of the predecessor. The exact
minimax constant and an actual Gaussian implementation are not determined.

The [proof](PROOF.md) uses

```text
h=2^-p, delta=(p/3-1)h, S=coordinate swap,
E_+/-=(2/5 +/- delta)S, T=nearest-grid rounding of (2/5)S,
u=(1,-1), k=p,
R_p=delta/[2(9/25-delta^2)] > (4/9)ph.
```

T is identical as a function on the entire complex disk grid for the two
instances. More oracle queries cannot distinguish them. A smaller asymptotic
error therefore needs an extra hypothesis or additional operator information.

## Reproduce

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/neumann-oracle-error-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/neumann-oracle-error-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/neumann-oracle-error-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/neumann-oracle-error-floor --check-source-history --check-modes
```

Another CPython 3.12 path can replace the local installation. Direct replay
writes nothing and requires only this package. It emits
`PASS_NEUMANN_ORACLE_ERROR_FLOOR` and a generated JSON report binding all six
package files by SHA256. No receipt is handwritten or frozen.

The verifier independently compares integer and Fraction rounding on every
complex disk-grid point at p=0..7, covers all 25 rounding residue pairs, and
checks 416 source-precision instances, p=101..512 plus 768,1024,2048,4096.
The latter include literal inverse equations, the separation formula,
boundary and complex oracle inputs, and six literal tail powers. It also
checks 3,104 scalar two-answer decisions and 136 randomized mixtures.
Six invalid precisions, four false inverse answers and four semantic
discriminators cover the relevant boundary and failure modes. These finite
domains corroborate the written proof; they do not establish its universal
quantifiers by extrapolation. No predecessor executable is imported.

## Scope, sources and research decision

The exact hidden operator is accessible only through the fixed-precision T.
Exact operator coefficients or a formula, additional E-dependent information,
refined precision and stronger relative-error promises can evade the result.
Nick Petalas's pending [PR6490](https://github.com/CrocSwap/integer-mult-bounds/pull/6490)
assumes access to a family of oracles at every requested precision and reduces
their precision volume. That changed-access model is outside this theorem;
the present target is the error floor for PR1430's single fixed oracle.
Entrywise nonnegative here means order-preserving; these swap matrices have
a negative eigenvalue. The construction is an abstract numerical interface,
with no claim that it occurs in an actual Gaussian resampling routine.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priorities
revision 8, selected PR6030. SOURCES.json pins the predecessor's retained
README and the original catalogue/selected record as historical provenance.
The source publication head is `1655c721a1c2aa92f584523afc93a192137cf910`.
The original uniform-transfer-audit card is explicitly changed to this
numerical-interface side theorem. The selected source-binding first command
passed; no selected scientific suite was run. This closes one scope and
provides no basis for extending a construction without its full cost ledger.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372374)
followed live handoff, active/open work, recent account, main README,
merged/general-form and local-reservation searches. The cached overlap helper
adds bounded remote coverage and incomplete sparse notes; unpublished work
and arbitrary historical diffs remain outside coverage. Searches do not prove
novelty.

Credit Hanson Sun / bbMisk for PR1430's absolute contract, Horner upper bound
and stronger-structure question; eumemic, icekylinx and the retained Gaussian
and Harvey–van der Hoeven resampling lineage for the underlying interface.
The predecessor's Artus Krohn-Grimberghe, Effy Elden, Alan Grillo and other
source attributions remain intact. Classical rounding and indistinguishable
oracle arguments retain their credit. No general literature-priority claim,
independent human review or formal proof-kernel acceptance is made.

Physical coefficient preparation, native implementation, actual Gaussian
structure, ownership/restoration, precision/tape/stock costs and complete
supplier/outer admission remain unproved here. All five selected framework
assumptions remain. There is no new kappa or selected-frontier change, and
no Lean, Docker or full multiplication replay.

## Open next questions

1. Can a source-bound Gaussian routine supply E-dependent structure that
   permits a smaller inverse error? Start with a proved local error law on
   its actual complex grid. The present indistinguishable pair must be
   excluded by that law, and physical precision/caller costs remain blockers.
2. What is the exact minimax constant for the fixed absolute oracle contract?
   Start with a scalar coefficient interval recovered from a complete oracle
   table, then compare its radius with the Horner upper bound. The current
   two-instance radius is a lower bound, not a solution of that whole problem.

## Implementation constraints

The standalone verifier uses exact rational arithmetic, direct calls and no
recursion, external libraries, network, subprocesses or write path. Every
loop has a fixed finite domain or a bound from the checked p<=4096 interface.
The largest disk enumeration has 257 squared candidate coordinate pairs;
only one point is retained at a time. All functions fit within sixty physical
lines. Explicit exceptions preserve checks under optimization. Syntax parsing
and warning-strict normal/optimized replay are the diagnostics used; no
separate type or lint analyzer is claimed.

Power of Ten rule 3 deviation: CPython allocates integers, Fractions and
bounded temporary collections dynamically. Precision is capped at 4096,
literal powered rational denominators below 70,000 bits,
and each of the six hashed files at 1 MiB. Runtime allocation internals are
not measured. A native steady-operation implementation would need a fixed
arithmetic-storage contract. Rule 9 deviation: rejecting controls use two
fixed callback targets, parameters and inverse-equation checks, only inside
their bounded local loops. No callback is accepted from outside the program.
