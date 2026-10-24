# Strict one-way corank-one correlation over every finite field

This scoped algebraic proof was produced by Nick Petalas. Apache-2.0.

## Result and evidence

Let U,V be rank-one idempotents over F_q^m with UV nonzero and VU=0.
The two requests I-U,I-V use a complete, uniformly weighted GL_m(F_q)
header. Each passes when every leading principal minor through order m-1
is nonzero. For every finite field and every m>=2,

```text
Pr(A and B) < (1-q^(-m)) Pr(A)Pr(B) < Pr(A)Pr(B).
```

This settles Open next question 1 of
[#4769](https://github.com/CrocSwap/integer-mult-bounds/pull/4769).
The new step in [PROOF.md](PROOF.md) uses
`q*gamma-alpha=(q-1)^3>0` to bound the one-way formula's weighted
correction in every dimension. The marginal and joint counting laws are
cited dependencies. Their proofs are not audited or rechecked here.
The binary strict-correlation result is already in #4274; the new claim
is the all-field quantitative bound. #4767 supplied the analogous
orthogonal-kernel proof pattern and retains its credit.

The verifier checks the polynomial identity by coefficient convolution
and compares exact rational expressions at every integer
2<=q<=64, 2<=m<=65, a total of 4,032 parameter pairs. Non-prime-power q
check only the algebra. Five fixtures include q=4 and the one-way value
J=53/351 with p=49/117 at q=3,m=3. Ten scenario controls cover independence,
wrong or missing corrections, a literal singleton-header counterexample
and six invalid finite-check inputs. A separate reversed-sign polynomial
control also rejects. All checks remain active under optimized Python.
The generated stdout receipt binds all six package files by SHA256.
No receipt is handwritten or committed.

This is an algebraic side result, with the explicit card scope change in
[TASK.json](TASK.json). [SOURCES.json](SOURCES.json) pins the task catalogue,
selected record and the three cited retained proofs as historical
provenance at canonical main 624de9dc66858af0945e5f8a0942488d62280d43.
There are no live external code inputs or third-party dependencies.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/oneway-pair-correlation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/oneway-pair-correlation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/oneway-pair-correlation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/oneway-pair-correlation --check-source-history
```

Use another CPython 3.12 installation in place of the local interpreter
path elsewhere. Expected markers are `PASS_ONEWAY_PAIR_CORRELATION`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The last command needs a publication commit and full Git history.
The direct verifier writes nothing and works from a Git-free package copy.

## Limits and implementation constraints

The universal statement rests on the written proof and cited counting
laws. Finite execution corroborates only the stated parameter domain.
Exactly two fixed one-way coupled kernels and the complete uniform header
domain are essential. The literal restricted-header example violates the
bound when its domain has one element. Two-way coupling and larger request
families remain open.

Selection, emission, dispatch, dirty restoration, precision, stock and
the complete physical caller bill remain unknown. No new kappa, supplier
admission, selected-frontier change or complete multiplication theorem is
claimed. Independent human and formal proof-kernel review are unclaimed.
Lean, Docker and selected operator replay are unrun.

The verifier has no recursion, subprocesses, dynamic code loading or
external mutable state. Its parameter grid stops at q=64,m=65; polynomial
inputs have at most four coefficients; fixtures and controls are fixed
finite tuples. Six sequential file reads each have a 1 MiB capacity check.
Every function is below 60 physical lines. Power of Ten rules 3 and 9
have managed-runtime deviations for CPython allocation and standard
iterator dispatch, confined to these bounded domains. Explicit contracts,
normal and optimized warning-strict execution, and syntax diagnostics
check the affected paths. Fixed-capacity native arithmetic would require
a separately specified integer representation and is not supplied here.

## Open next questions

1. What correlation signs occur when both UV and VU are nonzero? This would
   distinguish the remaining rank-one coupling types. First derive a joint
   count for one named two-way pair and compare it with the cited marginal;
   the one-way joint law does not apply to that pair.
2. Can a named odd-field producer use a fully charged one-way shared-header
   caller? Pin its kernel pair and actual header domain, then price selection,
   emission, dispatch, restoration and stock. Unknown physical costs block
   any supplier consequence. Structured first steps are in TASK.json.

## Credit

Nick Petalas's #4769/#4274 supplied the one-way joint law, #4227 supplied
the corank-one marginal law, and #4767 supplied the orthogonal comparison
and its proof pattern. The earlier binary strict-correlation proof remains
#4274's credit. Cinna Davis supplied the BIT request context; source527,
commdata2338 and Jose Manuel retain normalizer and recursive-closure
lineage credit. No predecessor package is changed.
