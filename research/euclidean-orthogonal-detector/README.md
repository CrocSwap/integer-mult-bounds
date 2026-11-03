# A smaller Euclidean guard for complete orthogonal-witness detection

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped written proof with exact finite corroboration; no new kappa. A new
whole-bank Euclidean error bound reduces the sufficient fractional grid of
one literal four-dimensional, twelve-call detector from **228 to 182 bits**.
The same coarse endpoint separator is used in both bounds. The new result
changes accumulated rounding amplification, without using a refined matrix
or program denominator.

For a side of m instructions, define its exact norm gains beta_i, entry
perturbation constants gamma_i, input radius R>=1, and

```text
s = ceil(sqrt(d))
G = product beta_i
A = sum gamma_i/beta_i
K = G (R A + s m)
```

Each exact orthogonal apply has beta=1. Aliased queries and arbitrary rational
scalar assignments have the fully charged bounds in [PROOF.md](PROOF.md).
At grid h=2^-p with hA<1, the complete side's register error is at most
`h K/(1-h A)`. For two sides it suffices to choose

```text
2^p >= max(1, 2 max(A_left,A_right), 8 (K_left+K_right)/eta)
```

to obtain endpoint error at most eta/4 and an exact zero/nonzero decision
under the credited separation premise. For apply-only words, K is linear
in the number of calls and dimension. No minimum-precision claim or strict
improvement for every scalar program is made.

## Evidence and reproduction

From the repository root with the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/euclidean-orthogonal-detector/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/euclidean-orthogonal-detector/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/euclidean-orthogonal-detector
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/euclidean-orthogonal-detector --check-source-history
```

Another CPython 3.12 executable can replace the displayed local path. The
standalone marker is `PASS_EUCLIDEAN_ORTHOGONAL_DETECTOR`; the registered
launcher also prints `PASS_REGISTERED_RESEARCH_PACKAGE`. Normal and optimized
warning-strict commands are registered with 120-second caps. The direct
verifier writes nothing and emits a generated JSON receipt binding all eight
package files. Redirect it outside the checkout to retain the receipt.

The exact finite evidence includes:

- 1,218 complete program/input cases over dimensions two through seven and
  Cayley parameters 1/4 and 1/7. Seven program-pair patterns include
  noncommuting order changes, restored inverse words, aliased queries,
  repeated scalar sources, zero coefficients, empty sides and scalar gains
  and denominators as large as 2^40. There are 84 mixed dirty input cases;
  the other cases enumerate every independent input column.
- 9,048 intermediate returned banks, comprising 138,528 scalar coordinates,
  checked against their own prefix Euclidean envelopes. Every final
  coordinate also has its difference error and selected threshold decision
  checked against a separate rational interpreter.
- A nonzero four-dimensional, twelve-call fixture executed at both 228 and
  182 bits, with the same eta=12^-48. Its exact selected endpoint is
  `33658561053084102656/87507831740087890625`. The new bound fails its
  sufficient inequality at 181 bits; this does not prove 182 is necessary.
- 240 finite product inequalities, 256 precision-rounding cases, fourteen
  invalid-input controls and four semantic controls. The latter detect
  omitted coefficient quantization, a wrong inverse table, use of updated
  values in an aliased query, and one fewer bit in the stated sufficient
  guard.

The universal statement rests on the written proof. These finite executions
corroborate it and the new implementation. No predecessor scientific program,
receipt or census is imported or replayed.

## Source, scope and credit

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision
8, selected PR6030. The selected binding-only baseline passed. [TASK.json](TASK.json)
records the explicit change from `formal-interface-lemma` to a quantitative
written precision-interface proof. [SOURCES.json](SOURCES.json) pins historical
provenance; there are no external runtime inputs or pending Git dependencies.
The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363345)
reserves this accumulated-error question. Discovery stopped at the first
verified strict grid improvement.

Credit Ali Romman / [PR5339](https://github.com/CrocSwap/integer-mult-bounds/pull/5339)
for the complete detector, coarse separator and open optimization question,
and [PR5315](https://github.com/CrocSwap/integer-mult-bounds/pull/5315) for the
orthogonal realization. Krzysztof Wojt / PR5262 supplies the inverse grammar
and witness compiler; zxv / PR5235 and the retained dirty-echo/tensor/phase
lineage keep their credit. Nick Petalas / PR5941 concerns exact matrix
separation denominators, a different step held fixed here. Euclidean
orthogonal invariance, Frobenius domination and forward-error propagation
are classical. No global literature priority is claimed.

Live open/account PRs, active Discussions, recent handoffs, main README
searches, merged general-form searches and local reservations were checked.
Cached overlap scanning has sparse historical-note coverage; unpublished work
and arbitrary historical diffs remain limits. These are bounded overlap
checks, not a guarantee of novelty.

## Limits and implementation bounds

The error theorem assumes exact real orthogonality, old-value instructions,
exact rational scalar arithmetic and once-per-output coordinate truncation.
Initial data must be exactly on the working grid and have the stated norm
radius. The allocator's coarse separation bound is for integer initial banks
and matching Cayley matrices. Nongrid input errors and noninteger-input
separation need separate treatment. Orthogonality and these caller premises
are essential; stored rounded matrices need not be orthogonal.

A zero at one selected endpoint is not a universal identity certificate.
The 46-bit reduction is a sufficient precision improvement, not a runtime,
optimality, native-call or exponent improvement. Matrix preparation, scalar
arithmetic, movement, ownership/restoration, stock, compiler, actual selected
precision/tape use and analytic recovery remain separate obligations. No
selected scientific replay, native suite, Lean or Docker build was run.
Independent human and formal proof-kernel review are unclaimed. The five
selected framework assumptions and selected frontier retain their status.

Build the Lever led to the explicit rational allocator and standalone replay.
Prove It Works led to complete intermediate-bank checks and literal execution
at the smaller grid. Power of Ten inspection found no recursion, subprocess,
network, dynamic evaluation or background work. Functions fit within 60 lines.
Allocation validates at most sixteen dimensions, four roles, three operators,
64 instructions per side, eight terms per scalar row, and 128-bit scalar
numerators and denominators. The fixed verifier uses dimensions at most seven,
three roles and at most 24 instructions on a side. Source-hash reads are
capped at 256 KiB per file. Exact exceptions survive optimized Python.

Power of Ten rule 3 deviation: CPython allocates managed rational and integer
objects during the bounded offline calculation. Fixed domains, explicit API
capacities and 8-by-256-KiB source capacity bound live state; runtime allocation
itself is not instrumented. A fixed-storage runtime would be required before
claiming that property. Rule 9 deviation: local `map` calls have only the
visible built-in or rational constructor targets and finite collections.
Rule 10 diagnostics are warning-strict normal/optimized execution and in-memory
AST compilation. No separate static analyzer or proof assistant is claimed.
Widening the stated capacities requires a new resource assessment.

## Open next questions

- Can one native-compatible orthogonal witness use this guard with a fully
  charged caller? Pin its actual operators, input grid and radius, then count
  preparation, arithmetic, movement and restoration. Native source binding
  and a complete physical bill are missing.
- Can exact instruction norms reduce a scalar-heavy guard further? Start
  with one fixed linear or aliased-query instruction and retain matrix
  quantization and data truncation. No optimal-norm or least-precision theorem
  is supplied. Structured relevance and blockers are in TASK.json.
