# Exact descent for four alternating BIT calls

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof with finite exact corroboration.** No new
kappa, native supplier or complete multiplication theorem is claimed.

Let K be any characteristic-two field and let P,Q be rank-one idempotents
of any finite size. Write E_z(P)=I+(z-1)P, with z an infinite-order address
monomial. Then

    E_z(P) E_z(Q) E_z(P) E_z(Q) is even
    if and only if P=Q or tr(PQ)=0.

Here even means that every entry has only even powers of z. If P=Q, the
word equals E_(z^2)(P)^2. Otherwise, for tr(PQ)=0, its exact factorization is

    E_(z^2)(P+PQ) E_(z^2)(Q+QP).

The new projectors are rank one and mutually orthogonal. Exactly two coarse
calls are necessary by determinant degree, even with arbitrary free constant
invertible maps. Their native cost is not established by this algebraic count.

A noncommuting example has

    P=[[1,0],[0,0]],  Q=[[0,1],[0,1]],  word=z^2 I_2.

All nine proper nonempty consecutive blocks are not even. Four is the
smallest call count that can have an even endpoint without exposing an even
adjacent pair. Thus iterating an adjacent-pair rule cannot exhaust even
four-use words. The explicit coarse factorization resolves this alternating
class without such a rule. The complete argument is in [PROOF.md](PROOF.md).

## Evidence

The verifier enumerates all ordered rank-one idempotent pairs in each row.
One engine multiplies polynomial matrices. A second engine applies literal
factors to every basis column without polynomial matrix multiplication.
Both compare the complete endpoint, including arbitrary dirty spectator
columns. Every even case also has its proposed coarse factors multiplied.

| Field | Width | Ordered pairs | Equal | Orthogonal distinct | Noncommuting even | Not even |
|---|---:|---:|---:|---:|---:|---:|
| F2 | 1 | 1 | 1 | 0 | 0 | 0 |
| F2 | 2 | 36 | 6 | 6 | 12 | 12 |
| F2 | 3 | 784 | 28 | 168 | 336 | 252 |
| F2 | 4 | 14400 | 120 | 3360 | 6720 | 4200 |
| F4 | 1 | 1 | 1 | 0 | 0 | 0 |
| F4 | 2 | 400 | 20 | 20 | 120 | 240 |
| F8 | 1 | 1 | 1 | 0 | 0 | 0 |
| F8 | 2 | 5184 | 72 | 72 | 1008 | 4032 |

There are 20807 pairs in total. Separate controls enumerate the nine proper
blocks, check five semantic predicates including missing cross-term and
changed-call mutations, and reject six invalid inputs with exact reasons.
The generated stdout receipt binds the package files by SHA256. No receipt
is handwritten and replay writes no files.

## Reproduce

From the repository root, using the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/bit-four-use-alternating-descent/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/bit-four-use-alternating-descent/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bit-four-use-alternating-descent
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bit-four-use-alternating-descent --check-source-history
```

Other hosts may use any CPython 3.12 interpreter. The expected receipt status
is `PASS_BIT_FOUR_USE_ALTERNATING_DESCENT`. Each registered command has a
120-second timeout. Direct replay is also Git-free and needs only these six
package files. Source pins are historical provenance, not imported code or
runtime dependencies. The selected baseline binding command passed at
canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.

## Credit and scope

CubeJerry's [PR6148](https://github.com/CrocSwap/integer-mult-bounds/pull/6148)
poses the four-odd-call question and proves two-use descent. This result
answers its suggested first step for an alternating class; it does not
replay the predecessor or settle general four-use descent. Its README is
pinned as provenance in [SOURCES.json](SOURCES.json).

Credit JosieElliston PR6111 and JoyboyBrian PR6104 for the two-frame questions,
apoursh PR6089 for the one-frame work, Nick Petalas PR2910 for the determinant
model, Cinna Davis PR2085/2112 for the endpoint/operation model, Philippe Van
Velzen for the earlier BIT call floor, and their retained lineage. Rank-one
factorization, determinant degree and characteristic-two expansion are
classical methods; no literature priority for them is claimed.

The originating card is explicitly changed to this algebraic side result in
[TASK.json](TASK.json). No actual native doubled-frame tariff, target inventory,
physical caller, stock, compiler, precision/tape implementation or outer bill
is supplied. No general four-projector theorem, arbitrary intervening-even
operation theorem, finite-order address claim or other-characteristic claim
is made. The universal claim rests on the written proof. The finite census
has only its displayed coverage. Independent human and formal proof-kernel
review are unclaimed. Lean, Docker, predecessor scientific suites and the
selected complete replay were not run. The selected frontier is unchanged.

## Code constraints

Scientific loops have fixed domains: width at most four, field size at most
eight, word length at most four and polynomial degree at most four. The
largest pair domain has 14400 entries and is streamed. Matrices have at most
16 entries, the largest projector list used has 120 entries, and no search,
subprocess, recursion or external import is used. Every function has fewer
than 60 physical lines. Checks use explicit exceptions and remain active
under optimized Python. Both registered commands make warnings errors.

Power-of-ten rule 3 deviation: Python integers, tuples and standard-library
operations allocate dynamically. The fixed domains above bound live data;
only one pair's polynomial endpoint is retained at a time. There is no
real-time guarantee. Extending the finite domains requires revisiting those
bounds before enlarging the replay. The package's standalone verifier has
no public mutable state or cleanup ownership. Optional external analyzers
are not part of its environment; syntax is checked by in-memory compilation.

## Open next questions

1. Does an even word of four unrelated rank-one projectors always admit two
   coarse calls? Start with full polynomial endpoints at width two and seek
   a counterexample or a replacement invariant. The alternating-square
   calculation does not cover that question.
2. Can an actual BIT profile use this factorization with a favorable native
   invoice? First identify the exact four-call region, source/target contracts
   and a priced doubled-frame implementation. No physical realization or
   complete bill is supplied here.

TASK.json records why these questions matter, their first steps and blockers.
