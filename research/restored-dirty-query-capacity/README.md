# Exact query capacity with restored dirty helpers

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with exact finite corroboration; no new kappa.** An arbitrary
finite bank of restored dirty helpers cannot lower the square-zero query
capacity in characteristic two. This answers the dirty-workspace part of
Josie Elliston's [PR #6138](https://github.com/CrocSwap/integer-mult-bounds/pull/6138),
second Open next question. Its workspace-free attaining theorem is a cited
premise, not a replay target.

Over any characteristic-two field K, let Q be a formal central involution.
Free gates are constant invertible matrices. Each paid gate is I+Q N with
N^2=0 and rank(N)<=r. There are n>0 independent targets and any h>=0
independent dirty helpers. The full endpoint must be diag(Q I_n,I_h).
For k>=3 available calls and m_k=2 floor((k-1)/2), feasibility is exactly

```text
n is even and n + ceil(n/m_k) <= k r.
```

Whenever feasible, the least total paid rank is n+ceil(n/m_k), independently of h.
For example, adding restored dirty helpers cannot make four rank-two calls
twist six independent targets. The same capacity without helpers was
already proved by #6138; the new result is its invariance under arbitrary
finite dirty workspace.

[PROOF.md](PROOF.md) gives the all-field argument. Normalization replaces
an identity endpoint by a projection P. The call Gram matrix X then only
satisfies X^3=X^2. Factoring Y=I+X yields an invertible complement core C
with C^2=I, rather than C=I. Its diagonal blocks still give idempotents.
Rank subadditivity recovers the same even-call bound; a separate dimension
count gives the odd-call bound. A nonidentity core occurs in the finite
fixtures, so the identity-only predecessor argument cannot be reused
without this step.

## Evidence and reproduction

From the repository root, with the interpreter used locally:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/restored-dirty-query-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/restored-dirty-query-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/restored-dirty-query-capacity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/restored-dirty-query-capacity --check-source-history
```

Elsewhere substitute a CPython 3.12 path. Only the standard library is
needed. The direct verifier emits `PASS_RESTORED_DIRTY_QUERY_CAPACITY`
in a generated JSON receipt bound to the six package files' SHA256 hashes.
It writes no files and imports no predecessor program.

- A complete three-coordinate, four-call binary fixture uses two target
  coordinates and one arbitrary restored dirty helper. Pair joins and a
  separate direct scan of all 234,256 ordered four-tuples both find exactly
  648 valid words. The new complement identities hold for each, including
  all 288 nonidentity cores. Literal quotient-ring execution checks all
  eight dirty inputs of each word, for 5,184 executions.
- Padded dirty-helper fixtures exercise each call count from three through
  eight, covering both parity branches of the new rank argument.
- A separate complete two-pair minimization on four coordinates, two targets
  and two dirty helpers, gives minimum total rank three for caps one and
  two. It includes respectively 11,236 and 99,856 ordered pairs and retains
  every pair-sum cost. It does not enumerate all ordered four-tuples in this
  larger domain.
- Four rejecting controls cover a non-square-zero summand with unchanged
  total, the wrong complete endpoint, a nonprojection, and the enumeration
  dimension limit. A literal clean-helper example shows why a zero-input
  promise does not imply dirty restoration.

The written proof, not these small fixtures, establishes arbitrary field,
helper count and dimension. No predecessor counts were replayed as the
contribution. [SOURCES.json](SOURCES.json) pins the source question and
attainment theorem as historical provenance at canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.

## Limits and expansion decision

This theorem requires exact formal equality, constant free controls,
square-zero paid terms, and restoration of every arbitrary helper input.
Initialized clean helpers, discarded helper outputs, non-square-zero paid
operations, nonlinear controls and approximation remain outside its scope.
The clean-helper example in the proof can twist one target using three
rank-one calls and a clean zero helper, while its full dirty endpoint fails.

There is no physical multi-bank query, native alignment, charged basis
implementation, stage chronology, complete signed invoice, compiler or
precision/tape construction. The five selected framework assumptions are
unchanged. No selected cold replay, Lean or Docker run, independent human
review or formal proof-kernel acceptance is claimed.

This closes the restored-dirty-workspace route in this model. Further
construction work needs a changed hypothesis and a complete favorable
physical bill. A larger search inside the same dirty model is unnecessary.
The non-square-zero and initialized-clean alternatives remain open and
are not assigned by this package.

Power of Ten rule 3 has a managed-runtime deviation. Python allocates
integers, tuples and dictionaries during verification. Scientific loops
have fixed bounds: dimension at most four, at most 65,536 candidate
matrices per census, 234,256 streamed raw four-tuples, and at most 65,536
pair-sum keys. Gram fixtures use at most eight calls and matrices of width
at most eight. There is no recursion, network operation, subprocess or
dynamic code in the verifier. Every function is below 60 physical lines.
Warning-strict normal and optimized commands are registered. The deviation
is confined to this terminating verifier; any larger search must introduce
new capacity bounds before expanding it.

## Open next questions

- Can initialized clean helpers reduce the paid-rank floor for even target
  dimensions? This would separate clean from restored dirty capacity beyond
  the odd-dimension example. First classify the permitted unspecified
  helper-column blocks in a normalized endpoint. The complete endpoint and
  clean-return contract need to be fixed before claiming a capacity.
- Which invertible non-square-zero paid alphabet can improve a real caller?
  This is the remaining distinct branch of #6138's second question. First
  specify a native gate, its complete arbitrary-input response and paid
  rank. No such physical gate or profitable invoice is supplied here.

## Credit

Josie Elliston's #6138 supplies the question, all-call workspace-free
attainment theorem and its stated unresolved workspace boundary. Credit
Nick Petalas #6122 for the earlier four-call theorem, Cinna Davis for the
rank-one simplex and controller lineage, Ali Romman #5617 for the coupled
Gram framework and block simplex, and Matarener #6114 for the higher-rank
query question. Rank factorization, kernel correspondence and rank
subadditivity are standard linear algebra. The new contribution is the
projection-complement involution argument and the resulting sharp
restored-dirty-workspace exclusion. No predecessor credit line is changed.
