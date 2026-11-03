# Nested border calls need a global precision budget

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: scoped written proof with exact finite corroboration.** A
specified two-register nested border has the sharp minimax precision law

```
d>=1, P>=1: minimum oracle bits = (d+1)P+d.
attaining uniform parameter: epsilon=2^(-P-1).
```

The desired output is `Gx`, with `G=diag(1,-1)` and two independent input
registers of max norm at most one. The numerical call is allowed any error
at most `2^(-p)` times its own input norm. All surrounding scales and ADDs
are exact. The theorem optimizes over every uniform parameter
`epsilon=2^(-s)` for integer s>=1, and every integer precision. One bit less fails on an explicit input and linear
oracle perturbation.

Every exact completed subcall is within `2epsilon` of its target, is an
involution and has spectral condition number below four. Its chronological
input scaling can nevertheless amplify a permitted oracle error by
`epsilon^(-d)`. Completed-call bounds alone therefore do not fund nesting.
[PROOF.md](PROOF.md) gives the exact worst error, necessity and attainment.

This takes the recursive-precision opening in Dillon Amburgey's
[PR4623](https://github.com/CrocSwap/integer-mult-bounds/pull/4623), at
`fd5d3be12b9d6ee92c8fa089d95bd529c3236563`. That work's finite global
approximation lemma already requires global norm bounds. This new synthetic
template quantifies a failure of substituting completed-subcall bounds for
those bounds. It does not run or audit the predecessor's controller,
reproduce its counts, or assert a defect in its claims.

## Evidence and reproduction

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/nested-border-precision/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/nested-border-precision
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/nested-border-precision --check-source-history
```

Substitute another CPython 3.12 path elsewhere. Both warning-strict normal
and optimized modes are registered. The direct marker is
`PASS_NESTED_BORDER_PRECISION`. Its JSON receipt binds all six package files
by SHA256 and reports actual enumeration counts. Default execution writes
nothing. Optional `--receipt /absolute/external/new.json` creates a fresh
receipt and refuses to overwrite it.

The finite replay checks 192 literal matrix fixtures, 4,400 input/error-corner
executions on 275 fixtures, 4,055 precision choices across 30 finite minima,
384 sharp precision families and thirteen controls. These counts refer to
separate domains that overlap.

The checker multiplies the literal nested matrices, executes actual scale,
reflection and shear instructions with an injected error, and compares that
separate chronological calculation with the derived formula. It enumerates
all real input and error-sign corners on its finite fixture domain. A bounded
precision/parameter search checks minima independently of the theorem's
necessity argument. Sharp families check the sufficient request and a
one-bit-short failure. Invalid-domain and semantic controls remain active
under optimized Python. The universal statement rests on the written proof.

## Limits and engineering bounds

This is a contract obstruction for a synthetic real two-register template.
An implementation that computes the inner reflection exactly can evade the
worst-case oracle error. Componentwise, correlated or exact error contracts,
nonuniform parameters, different words and changed algorithms are outside the
minimum. The result is not a lower bound for every border compiler or a
rejection of any published physical caller.

The card scope changes from new productive credit to the global precision
obligation for an approximate independent-target interface. The selected
baseline binding check passed at main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected PR6030.
No target/paid histogram, complete optimistic supplier bill, native realization,
physical scale or ADD cost, dirty auxiliary protocol, compiler, stock/tape,
analytic recovery, new kappa or selected-frontier change is claimed. No
selected scientific cold replay, Lean, Docker, independent human or formal
proof-kernel review ran. All five framework assumptions remain.

The verifier has no recursion, network, subprocesses, dynamic code evaluation
or mutable shared state. Its numerical loops have explicit finite bounds and
all functions fit within 60 lines. Power of Ten rule 3 has a managed-runtime
deviation: Python allocates Fraction and collection objects during this bounded
offline computation. Matrices are 2 by 2; the finite search retains at most
387 feasible choices at once. Helper capacities cap depth at 64, scale at 256
and oracle precision at 65,536. The CLI does not expose these domains as
unbounded input. Warning-strict normal/optimized replay and AST inspection
supply diagnostics; no separate static analyzer is configured.

## Open next questions

1. Extract chronological scale exponents and actual numerical error contracts
   from one legally flattened approximate controller, then compare its global
   precision request with its complete paid bill. The actual source adapter
   and physical pricing are missing; this template cannot supply them.
2. Can a concrete componentwise error contract avoid the depth factor while
   preserving every independent input and the full numerical implementation?
   Start by bounding error transferred from the enlarged first coordinate to
   the unscaled second coordinate. Normwise accuracy alone permits that transfer.

## Credit and coordination

Credit Dillon Amburgey / dillona for PR4623's border construction, finite global
approximation lemma and explicit recursive-closure opening, with Cinna Davis,
zxv, Jacob Alan Sussman, Mark / Matarener, DaysSky, Ryanson Jonathan and the
retained native/compiler/precision lineage. Those results are cited premises,
not audit deliverables. Diagonal similarity, geometric sums and linear error
propagation are classical; general literature priority is unclaimed.

The new template, sharp error formula, minimax precision proof and checker
were produced by Nick Petalas. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372669)
records the scope. Live handoffs, account contributions, reservations, main
README searches and merged/general-form searches were checked. Sparse notes,
arbitrary historical diffs and unpublished work remain coverage limits.
[SOURCES.json](SOURCES.json) binds historical provenance only. No predecessor
scientific executable or receipt is imported or replayed.
