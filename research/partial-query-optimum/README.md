# Exact partial-query acquisition at small codimension

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written proof and constructive optimizer with exact finite
corroboration. Independent human and formal proof-kernel review are unclaimed.

A target subspace U need not require the entire query span V. The new exact
reduction considers every superspace of U through V/U, buys a cheapest basis
of the queries eligible in that superspace, and takes the cheapest candidate
that spans U. For a finite field of order q and c=dim(V)-dim(U), the number
of candidates is the sum of the Gaussian binomial coefficients [c choose k]_q.
It depends on target codimension. For binary c=0,1,2,3,4, the exact counts
are 1,2,5,16,67. [PROOF.md](PROOF.md) proves the reduction for every finite
field and arbitrary finite query pools with nonnegative costs.

The executable handles binary width through 256, at most 4096 queries and
256 target vectors, codimension through four, and integer prices through
10^12. Zero prices, duplicate/zero queries and empty targets are included.
The checker proves candidate independence, full eligible coverage and
cheapest-basis exchange optimality, or checks a missing-target separator.
An independent RREF enumeration checks that no quotient space was omitted.
The constructor uses span extension. Neither executes predecessor code.

For queries 1,2,3 with prices 3,2,2 and target 1, whole-span basis pruning
pays four; the new optimum is three. At codimension two, an intermediate
superspace can beat both the target space and the whole space. The proof
gives a five-query example with respective optima eight, four and five.
These are acquisition prices in a declared algebraic relaxation.

## Reproduce

From the repository root, with the standard library and CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/partial-query-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/partial-query-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/partial-query-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/partial-query-optimum --check-source-history
```

Set TMPDIR to an existing private external scratch directory for the three
short CLI subprocess checks. Another CPython 3.12 path may replace the local
path. The scientific marker is PASS_PARTIAL_QUERY_OPTIMUM. Each replay
prints a generated receipt bound to all eight package files by SHA256 and
writes no persistent artifact. The registered runner executes both modes.

For a new problem, write JSON with exactly these keys:

```json
{"width":2,"vectors":[1,2,3],"costs":[3,2,2],"targets":[1]}
```

Run `python3.12 -I -B research/partial-query-optimum/optimizer.py problem.json`
and save stdout as certificate.json outside the checkout. Check that file
with the same command followed by `--check certificate.json`. The minimum
is three. Vectors are binary coordinate bitmasks encoded as JSON integers.
The target must lie in the query span; unsupported domains reject explicitly.
The certificate records all candidate bases, quotient forms and the winner.

## Evidence and limits

The complete finite replay compares every weighted seven-vector pool with
prices in 0,1,2 against every target subspace of F2^3. A second complete
family includes duplicate and zero queries. Its oracle enumerates purchased
index subsets and literal XOR spans, without Gaussian elimination. Three
independent quotient enumerators, malformed-input and certificate controls,
maximum width/query count and codimension, and actual CLI production/checking
are also exercised. The replay checks 36,207 exhaustive optima and 147,258 candidate bases,
nine corrupted certificates, ten invalid problems and three CLI runs.
The receipt reports these exact enumerated counts.

The written argument establishes the quantified theorem. Finite evidence
corroborates the bounded implementation. [ENGINEERING.md](ENGINEERING.md)
states resource bounds and the managed-runtime allocation deviation.

Linear reconstruction is free only in this acquisition model. XOR cost,
physical delivery, phases, borrowed-state restoration, owned storage, native
legality, precision, compiler closure and the full supplier/outer bill remain
separate. No native, selected cold, Lean or Docker replay, new kappa,
selected-frontier change or complete multiplication theorem is claimed.

## Sources and overlap

Ali Romman / [PR5791](https://github.com/CrocSwap/integer-mult-bounds/pull/5791)
poses partial-target acquisition separately from its whole-span optimum.
Its retained [guide](../../docs/research/binary-query-basis.md) is pinned as
an authenticated documentary input, without executing its implementation.
Nick Petalas / [PR5878](https://github.com/CrocSwap/integer-mult-bounds/pull/5878)
gives the earlier sharp c+1 approximation guarantee for pruning any cheapest
whole-span basis. That result is cited context, not replayed or audited.
Classical quotient spaces, rank-nullity, Gaussian binomial counting and
weighted linear-matroid greedy selection retain their credit. The new step
is the exact small-codimension reduction and its certificate implementation;
no literature-wide priority for enumerative optimization is claimed.

The base is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision eight.
[SOURCES.json](SOURCES.json) pins the original card and selected record as
historical provenance. [TASK.json](TASK.json) explicitly changes the formal
interface card to this algebraic side result. The binding-only selected
baseline passed; no selected scientific replay is inferred.

The [advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19376723)
followed live open-PR, recent-account, main README, merged-PR and handoff
searches. Distinctive terms included partial-query acquisition, quotient
subspaces, superspaces, codimension, Gaussian binomial and target-aware
acquisition. Cached overlap has sparse local coverage; explicit Git searches
covered main READMEs for those terms. This does not cover arbitrary historical
diffs or unpublished work and is not a novelty certificate. No predecessor
package or credit line is changed.

## Open next questions

Can one actual native helper caller satisfy this additive acquisition contract
with an affordable reconstruction bill? Pin its query pool and target space,
then price the winning acquisition, reconstruction, delivery, storage and
restoration together. Missing source binding and physical tariffs block a
supplier or kappa claim. The structured question is in TASK.json.
