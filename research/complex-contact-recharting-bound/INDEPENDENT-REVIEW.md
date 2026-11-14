# Independent full-corridor review and integration receipt

## Scope and method

A separate research worker rebuilt the pinned source with an independent
visit parser, union-find construction and finite-field subspace implementation.
It derived public floors and caps without importing the primary solver's
domains, then enumerated all mixed growth/shrink choices and checked owned
comparability in both directions. The portable scientific core of that review
is `independent.py`. It does not execute the primary `core.py` or `solver.py`.

The integration wrapper compares the complete profile multiset, not only the
optimum: 96 variables, 77 factors, 253 raw factor assignments and 214 legal
assignments. All profiles agree. The independent inventory has 6,232 ascending
public MOVEs, 23 ascending owned MOVEs and 24 descending owned MOVEs. Public
edges alone may be used for monotone boundary propagation. There are 13 edges
between growth and shrink variables; separate one-direction checks would not
prove the combined result.

## Mathematical checks

The original source chart belongs to every enumerated domain. Subspaces in
each floor/cap interval are enumerated completely through its quotient; the
quotient dimensions are at most 3. Every affected MOVE is assigned to exactly
one connected factor. The checker rejects illegal public containment and
checks owned comparability in either orientation. All factor maxima are zero
for each of the nine tariffs `min(r,k)`.

The nonnegative cone decomposition in `PROOF.md` extends those exact integer
inequalities to all increasing concave tariffs. The rank inequality for the
symplectic mixing block gives a dimension-gap lower bound for any actual
quotient, while ordinary maps and their phase, address, lifecycle and precision
costs are optimistically free. No assertion that a rank-zero quotient is the
identity is used. The theorem is restricted to fixed template positions; it
does not prove all-column multiplicity scaling or admit a full supplier.

## Controls and complete invoice

The same primary optimizer accepts the older canonical positive control with
exact `min(r,2)` saving 1 and paid delta {1:+1,2:-2,3:+1}. This improvement is
already in #7481. The main wrapper rejects a mutated source in both parsers and
a false ownership flag. Its full caller recount matches all target and paid
entries, not just totals: 17 calls, 22,461 targets, 110,519 paid jobs.

An earlier exploratory review accidentally labelled a decimal power-price
value as the integer-tariff result. The reviewer corrected it: the integer
tariff saving is exactly 1. No decimal power-price estimate is needed or used
by this published proof or verifier.

The review and integration are OpenAI-assisted algorithmic cross-checks for
@CubeJerry, not independent human acceptance or a proof-assistant theorem.
`VALIDATION.json` records the final executed package checks.
