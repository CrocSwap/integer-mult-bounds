# Exact costs for singular polynomial targets

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped algebraic proof with finite corroboration. For every field K, every
determinant-zero target in M2(K[t]) has paid right-vector cost at most three,
with free GL2(K) maps anywhere and no scratch roles. The exact classification
is in [PROOF.md](PROOF.md). No new kappa or supplier admission is claimed.

For nonzero M, take its primitive polynomial column factorization M=a b.
Let V be the K-span of the two entries of b, and let d be their monic gcd.

```text
cost 1: a is constant and V contains a nonzero constant;
cost 2: otherwise, a is constant or d belongs to V;
cost 3: otherwise.
zero:  cost 2.
```

An attaining three-factor word has fixed right vectors e1,e2,e1. Over every
field, `a=(1,t)^T`, `b=(t,t²+1)` gives exact cost three. This settles singular
polynomial endpoints at every degree. Invertible polynomial endpoints can
have unbounded cost, as proved in #4763 and counted in #4784; those results
are complementary, cited context.

ToikY's #4334 leaves singular targets outside its field-product theorem.
Nick Petalas's #4276 supplies the exact two-factor criterion and #4243 the
free-map normal form, following Wentao Li's #4099 and #2513. These are
credited dependencies, not audit deliverables. The primitive PID and gcd
facts are classical. The e1,e2,e1 field-product template in #4780 is related
precedent for the outer-product word. SOURCES.json pins #4334 and #4276 as
historical provenance. No predecessor code or live input is imported.

## Evidence

The verifier enumerates every determinant-zero matrix with the listed entry
degree bounds, using literal polynomial determinants. For each nonzero
matrix it constructs its primitive factorization, compares the new formula
against a separate constant-chart divisibility test, checks the one-factor
constant-image condition and multiplies all three literal paid factors.
The direct two-factor test also returns and multiplies a complete witness,
including its free endpoint maps. Zero is tested separately.

| Field | Maximum entry degree | Targets | Cost 1 | Cost 2 | Cost 3 |
|---|---:|---:|---:|---:|---:|
| F2 | 4 | 8704 | 279 | 7489 | 936 |
| F3 | 2 | 6561 | 800 | 5761 | 0 |
| F4 | 1 | 2176 | 975 | 1201 | 0 |
| F5 | 1 | 6625 | 3024 | 3601 | 0 |

These are 24066 distinct targets across four separate domains. Each row
includes zero once in cost two. All 35 enumerated control groups pass. They
cover the sharp example in all four fields, factor order and omission,
constant-image and constant-column exceptions, row-content normalization,
gcd membership, invalid fields and a zero polynomial divisor. All checks
remain active under optimized Python. The generated stdout receipt binds
all six package files by SHA256; no receipt is handwritten.

## Reproduce

From the repository root, with the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/singular-polynomial-cost/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/singular-polynomial-cost/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/singular-polynomial-cost
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/singular-polynomial-cost --check-source-history
```

Any Python 3.12 interpreter may replace the displayed local path. The direct
marker is `PASS_SINGULAR_POLYNOMIAL_COST targets=24066 controls=35 no_new_kappa`.
Both registered checks must finish within 120 seconds each.

The original card is explicitly changed to this algebraic side question.
Its historical baseline command stops at an omitted sparse input,
`research/fresh-helper-thinned/PROOF.md`; no baseline or selected scientific
replay pass is claimed. The selected record remains 60403/20000000.

## Limits and code constraints

The universal result is the written proof. The finite census corroborates
only the displayed fields and degrees. The exact classification requires
two roles, one polynomial variable and a field of constants. No statement
about multivariate rings, general singular coefficient algebras or more roles
is supplied. Native coefficient preparation, access, routing, precision,
reversible dirty restoration, stock and complete supplier costs are unknown.
No complete multiplication theorem, selected-frontier update, independent
human review or formal proof-kernel acceptance is claimed. Lean, Docker and
selected operator replay are outside scope and were not run.

The verifier has no recursion, subprocess, dynamic code or indirect callback
chain. Every function is below 60 physical lines. Explicit exceptions retain
checks under -O, and registered commands make warnings errors. Polynomial
capacity is 33 coefficients, bounded division and gcd take at most 34
iterations, and census inputs are fixed. The largest matrix census considers
32^4 matrices over F2. Product caches contain at most 1024 entries; only
accepted targets are processed further, one at a time. Field operations are
bounded to F2,F3,F4,F5, with F4 represented modulo x²+x+1. Python and the
standard library allocate dynamically. This is a managed-runtime deviation
from fixed allocation, bounded by those input and live-collection capacities.
There is no real-time claim. A future larger census must revise and verify
the resource bounds first. Optional external Python analyzers are not
required and were unavailable; in-memory compilation is the syntax check.

## Open next questions

1. Which singular targets are reachable over the nonprincipal domain
   K[s²,st,t²]? Start with `[[s²,st],[st,t²]]`, testing its outer-product
   factorization and restricted-right-vector reachability. The one-variable
   primitive-factorization argument does not supply that step.
2. Can an actual native producer and consumer use one of these words at a
   favorable complete cost? Specify coefficient preparation, ownership,
   overwrites, restoration, precision and the full paid list before expanding
   the construction. Unknown costs are not zero.

TASK.json records the motivation, first steps and blockers for both questions.
