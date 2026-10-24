# Exact right-vector cost of ordinary rank-one matrix targets

Scoped proof with finite corroboration. For every field K, every matrix size
m>=2 and every role count n>=1, every target M in M_n(M_m(K)) of ordinary
K-rank one has exact paid cost

```text
cost(M) = n.
```

Paid factors are I+u y^T with u in M_m(K)^n and y in K^n. Free GL_n(K) maps
may occur anywhere. Rank here means rank on K^(nm). It is not the
column-image dimension on K^n used in the earlier delta invariant. There is
no new kappa or selected-frontier change.

[PROOF.md](PROOF.md) gives the proof and explicit factors. Each paid factor
has nullity at most m, so n-1 paid factors cannot reach rank below m.
Conversely, write M=a b. After moving one nonzero block b_1 to the first
position, replace column 1 by a b_1 and then replace each column j by column
1 times C_j, where b_1 C_j=b_j. All n replacements are legal paid factors.
This is a singular family for arbitrary role counts, extending the
noncommutative exact-cost questions of #4265 and #4276. The classical rank
inequality and rank-one matrix count are not claimed as new.

## Exact finite evidence

The standard-library verifier enumerates each rank-one target exactly once:
normalize the first nonzero coordinate of a to one and take every nonzero b.
The classical count is (q^(nm)-1)^2/(q-1). It checks the literal flattened
matrix product, each factor's rank bound and a separate chronological
block-vector interpreter on every standard basis input. Linearity then
covers every data input for each enumerated target.

| Field | Roles n | Block size m | Enumerated targets | Exact paid cost |
|---|---:|---:|---:|---:|
| F2 | 1 | 2 | 9 | 1 |
| F2 | 2 | 2 | 225 | 2 |
| F3 | 2 | 2 | 3,200 | 2 |
| F4 | 2 | 2 | 21,675 | 2 |
| F2 | 3 | 2 | 3,969 | 3 |
| F2 | 2 | 3 | 3,969 | 2 |

There are 33,047 targets across the six domains. F4 is implemented in the
polynomial basis F2[t]/(t^2+t+1), with complete finite field-law checks.
Nine discriminating controls check a dropped factor, reversed order, the
odd-characteristic sign, multiplication on the wrong side, the omitted
input permutation, each of two n-1-factor deletions, the predecessor zero
target and the scalar-block boundary. At m=1 a nonzero rank-one target has
cost n-1, as already follows from the predecessor diagonal theorem.

The verifier writes nothing. It generates a receipt from the six package
file hashes and computed results. Warning-strict normal and optimized runs
execute the same explicit checks; no check depends on Python assertions.

## Reproduce

From the repository root, using CPython 3.12 and the standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-rank-one/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-rank-one/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-rank-one
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/right-vector-rank-one --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path. Expected
marker: `PASS_RIGHT_VECTOR_RANK_ONE targets=33047 controls=9`, followed by a
generated receipt digest and `no_new_kappa`. The package runner ends with
`PASS_REGISTERED_RESEARCH_PACKAGE`.

## Provenance and scope

The historical card is `connector-alphabet-change`, explicitly changed to
this algebraic side question. Its first working example passed with
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
The package base is canonical main 1f87c3578ae546c8f903f7f4d83dc2e2fb99650b,
priority revision 7. [SOURCES.json](SOURCES.json) pins that
base, the full card, selected provenance and two predecessor documents.
Neither predecessor verifier is imported or replayed as this contribution.

[The advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19131172)
reserves this question. Live open PR bodies, recent handoffs, main READMEs
and distinctive merged searches were checked. The initial overlap helper
reported complete pagination for 426 open PRs and 3,684 Discussion records;
sparse local coverage was 49 records of 6,061 HEAD candidates. This is search
coverage, not a proof of novelty.

This is a formal alphabet with singular, data-discarding factors. Native
coefficient preparation, reversible dirty-state restoration, frames, routing,
precision, stock and the complete recursive invoice are unknown. It does
not produce a native supplier or complete multiplication theorem. No Lean,
Docker or selected-construction replay is required or claimed. Independent
human and formal proof-kernel review are unclaimed.

The finite verifier is bounded to q in {2,3,4}, n<=4, m<=3 and nm<=8, with
at most 4,096 stored vectors. The six actual census domains have nm<=6.
All calls are direct and nonrecursive; functions stay below 60 lines.
Python allocates bounded temporary lists during replay, a managed-runtime
deviation from fixed preallocation. It holds one target and word at a time,
rather than all target matrices. Explicit checks remain enabled under -O.
No language-specific static analyzer is required by this package; the
registered warning-strict replays are its executable diagnostics.

## Open next questions

1. Which targets of ordinary rank 2 through m-1 still cost n? This would
   locate the first obstruction to a higher-rank singular extension. Start
   with m=3, n=2 and the block-restriction rank criterion of #4276. A higher
   dimensional row space need not have one block retaining its whole rank.
2. Can a literal native producer and consumer implement these column
   replacements with a favorable full invoice? First specify one matrix
   coefficient's preparation, overwrite, routing and restoration contract.
   All physical costs remain unknown; this note does not justify a supplier
   construction campaign.

The structured questions and blockers are in [TASK.json](TASK.json).

## Credit

This contribution was produced by Nick Petalas. Nick Petalas's #4276 and
#4265 supply the exact-cost questions, and #4243 supplies the free-map normal
form and diagonal boundary. Wentao Li's #4099 supplies the right-vector
alphabet and column bound, following #2513. ToikY's #4334 supplies the
commutative-product comparison. The current invertible matrix-block
extension is Nick Petalas's #4749; this note concerns singular targets.
Ordinary matrix rank inequalities, rank-one decomposition and finite-field
rank-one counts are classical. All predecessor credit remains unchanged.
Apache-2.0.
