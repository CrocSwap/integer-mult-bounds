# Exact two-versus-three cost for distinct-factor quadratic lifts

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof with exhaustive binary corroboration.**
For every field K, let R=K[x,y]/(x,y)^3 and J=(x,y). On exactly two roles,
allow paid factors I+u v^T with u in R^2 and v in K^2, arbitrary free
GL2(K) maps, and singular paid factors. Write

```
M = diag(x,y) + Q,   Q in M2(J^2),
gamma = coefficient of y^2 in Q12,
delta = coefficient of x^2 in Q21.

cost(M) = 2 if gamma=0 or delta=0, and 3 otherwise.
```

Every lift is reachable. For a finite field of size q, the exact counts are
(2q-1)q^10 lifts of cost two and (q-1)^2 q^10 of cost three. For F2 the
counts are 3,072 and 1,024. No new kappa is claimed.

[PROOF.md](PROOF.md) gives the all-field argument. A radical shear followed
by two column replacements supplies the upper bound. The cited two-factor
ideal criterion reduces the lower bound to the two displayed coefficients.
The exact cost concerns arbitrary inputs in R^2, with no zero-input or
scratch assumption.

## What this adds

Ali Romman's [#5320](https://github.com/CrocSwap/integer-mult-bounds/pull/5320),
`research/cube-zero-lift-obstruction`, asks for another first-order pencil.
It classifies the binary repeated-factor pencil [[x,y],[y,x]], with some
unreachable lifts. This package settles the distinct-factor pencil diag(x,y)
over every field, with every lift reachable and some needing a third factor.
Its proof and computations concern the new pencil only. No predecessor
scientific verifier or census is imported, replayed or audited.

Nick Petalas's [#4276](https://github.com/CrocSwap/integer-mult-bounds/pull/4276)
supplies the exact two-factor criterion; #4764 supplies an earlier separate
pure-quadratic cost-three example. Wentao Li's #4099 following #2513 supplies
the alphabet, and ToikY's #4334 supplies related common-chart context. Classical
truncated-polynomial arithmetic and coefficient counting retain their credit.

## Evidence and reproduction

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/distinct-pencil-quadratic-lifts/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/distinct-pencil-quadratic-lifts/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/distinct-pencil-quadratic-lifts
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/distinct-pencil-quadratic-lifts --check-source-history
```

Another CPython 3.12 path may replace the local path. The direct scientific
marker is `PASS_DISTINCT_PENCIL_QUADRATIC_LIFTS no_new_kappa`. The checker
writes nothing and emits a generated receipt binding all package files.

The checker enumerates all 4,096 binary lifts. For each, it compares the new
coefficient test with the cited principal-ideal criterion. It searches free
GL2(F2) endpoint pairs until a witness is found, and exhausts all 36 pairs
for each rejection. It replays every attaining word and checks the action on
all twelve K-basis inputs of R^2. There are 49,152 basis-input comparisons.
The coefficientwise ring multiplication and packed binary action are separate
calculation paths. The criterion is a cited theorem; these checks apply it
to the new targets rather than independently validating that predecessor.

The checker also replays explicit words on 34, 74 and 122 distinct samples
over F3, F5 and F7. Samples include every single-coordinate perturbation and
one dense perturbation for every pair (gamma,delta), with exact deduplication.
Eight rejecting controls cover four omitted/reversed words, an odd-field
sign error, and three invalid inputs. Ring controls distinguish square-zero
from cube-zero truncation. Checks stay active under optimized Python.
Both registered commands were timed separately on CPython 3.12.15 at
0.33 seconds each. The complete registered launcher also passed.

[SOURCES.json](SOURCES.json) pins the unchanged source prose, catalogue and
selected record as historical provenance at canonical main
`e54523517d0f03e58352e647c403a5af3e525a57`. No external runtime input is read.
The source-binding orientation passed with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it is not a selected operator replay.

## Scope and implementation limits

The card formal-interface-lemma is explicitly changed to an algebraic side
question. This locates one boundary where cubic nilpotence permits a third
paid update; it does not discharge a selected framework assumption. The
selected frontier is unchanged. Native preparation, physical movement,
restoration, precision, stock and the complete recursive invoice remain
unknown. No native, compiler, Lean, Docker or selected scientific cold replay
was run. Independent human and formal proof-kernel review are unclaimed.

The offline checker has no recursion, subprocesses or dynamic evaluation.
All loops have fixed finite domains: six monomials, 64 binary ring elements,
six binary free matrices, 4,096 binary targets, twelve basis inputs, and at
most 122 stored samples per odd field. Every function is under sixty physical
lines. CPython managed allocation is a deviation from fixed allocation,
bounded by these domains and the 64-by-64 multiplication table. Explicit
contracts and warning-strict normal/optimized runs provide the available
runtime diagnostics. No external static analyzer or proof kernel is claimed.

## Open next questions

1. Classify lifts with a rank-one first-order pencil, such as diag(x,0).
   Start with a three-factor normal form and retain its second-order terms.
   The present proof uses two independent diagonal linear forms and does
   not supply the necessary all-word obstruction for that pencil.
2. Bind an attaining three-factor word to a literal native producer and
   consumer. First price its radical coefficient shear, overwritten inputs
   and restoration in one actual caller. Coefficient availability and a
   complete physical invoice remain the blockers.

Structured next steps and the bounded stop rule are in [TASK.json](TASK.json).
