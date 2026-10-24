# Sharp entropy threshold for adaptive compiler tail gates

For two target ranks, the adaptive compiler's two-tail feasibility question
has a closed form. For arbitrary finite target profiles, the same expression
gives a sharp sufficient test from the rank range and tilted mean.
This is a scoped written proof with exact finite corroboration. It does not
give a native word, supplier admission, a multiplication theorem or a new κ.

Let `q=T(t)/P(t)>=1`. Normalize target log ranks to `[0,1]`, with target
tilted mean `p` and paid tilted mean `x`. When `0<x<p<1`, put

```text
D(x||p) = x log(x/p) + (1-x) log((1-x)/(1-p)).
```

The condition `log q < D(x||p)` guarantees both tail gates and their ordering
guard. For a two-rank target it is necessary as well. At equality, a profile
with a target rank strictly between its extremes still passes, whereas a
two-rank target fails. The boundary cases, proof and exact hypotheses are in
[PROOF.md](PROOF.md). The underlying exponential convexity and binary entropy
calculation are classical. The contribution is their sharp application to
this compiler gate contract, including its strict equality boundary.

## Exact integer-histogram transition

At exponent `t=1/2`, consider the abstract histograms

```text
W_4=1, W_256=32;   P_16=c,   1<=c<=128.
```

Here `T=514`, `P=4c`, `p=256/257`, and `x=1/3`. The exact minimum of
`T(t-lambda) exp(lambda mu_P)` over positive `lambda` is 24, attained at
`lambda=3/2`. The tail and ordering gates are therefore feasible exactly
when c>=7. The boundary c=6 fails despite moment surplus and a positive
mean gap.

For c=7, one explicit witness is

```text
a=1, b=31, M=2^132, s=1/2, lambda=3/2,
mixed tail u=2049/2056 < 1,
root tail v=64*(6/7)^32 < 1,
forward ratio T(t+s)/T(t)=4098/257 > 4=P(t+s)/P(t).
```

This c=7 profile has no nonnegative moment crossing. The source's crossing
hypothesis is sufficient for its wider theorem, not necessary for these
three gates. The proof gives the all-c transition. The verifier checks
all 128 integers and this literal rational witness. These histograms
are not asserted to be realizable native inventories.

The advance CLAIM incorrectly predicted mirror slack for this fixture.
Its source and exit windows are disjoint, so it fails mirror coverage.
The [progress correction](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19147154)
records the narrowed delivered scope. No full compiler admission follows.

## Reproduce

From the repository root, standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/adaptive-tail-entropy/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/adaptive-tail-entropy/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/adaptive-tail-entropy
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/adaptive-tail-entropy --check-source-history
```

Any CPython 3.12 executable may replace the absolute local interpreter path.
The direct verifier is read-only and Git-free. It prints a generated JSON
receipt bound to every package file, followed by `PASS_ADAPTIVE_TAIL_ENTROPY`.
It uses exact rational powers to compare the entropy threshold, a separate
rational search for actual passing tail points, finite interior-support
chord checks, symbolic derivative identities and rejecting controls.
The universal conclusion rests on the written proof, not a finite census.

The finite domain contains all 8,640 combinations of exponents
`1<=low<high<=5`, paid exponent `0<=e<high`, and three multiplicities
in `1..6`, with ranks powers of four at t=1/2. Of these, 8,439 satisfy
q>=1. The classifiers agree on all of them; 5,444 have an explicitly
checked rational passing point and 2,995 fail. The verifier also checks
288 three-position laws, including 256 strict interior cases and 32
endpoint equalities, and 14,975 literal failing-point controls.

The verifier has no recursion, subprocesses, network or external inputs.
Each witness search has at most 128 tail trials or 96 bisections. Every
function has at most 23 physical lines. Python's managed allocation is a
documented deviation from fixed storage: counters have fixed key sets,
only one histogram is live, the source inventory has six files capped at
128 KiB each, and all arithmetic domains and iteration counts are bounded.
Warning-strict normal and optimized execution and an AST inspection are
the available local diagnostics; no repository-wide static analysis is claimed.

## Scope and credit

Canonical base `ff3cc58e370d0f678e529246f8c73e8094e18fcf`, priority revision 7.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19147083)
records the change from `independent-moment` to an original algebraic gate
question. [TASK.json](TASK.json) records the remaining obligations and
[SOURCES.json](SOURCES.json) pins historical provenance. No predecessor code
or receipt is imported, executed or recounted as this contribution.

Credit Dillon Amburgey's [#4532](https://github.com/CrocSwap/integer-mult-bounds/pull/4532)
for the exact scalar gate criterion used as a cited premise, zxv's
[#4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436) and
[#4483](https://github.com/CrocSwap/integer-mult-bounds/pull/4483) for the
adaptive flow and gates, Jacob Alan Sussman's compiler, and Ryanson Jonathan's
[#4459](https://github.com/CrocSwap/integer-mult-bounds/pull/4459) mirror method.
Their retained native, helper, geometry and outer contributors keep their
credit. This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed. Global
literature priority for entropy or exponential-moment bounds is unclaimed.

The result screens only the two tail gates and their ordering guard.
General-profile failure of the sufficient entropy test is inconclusive.
Native realizability, full mirror/recurrence funding, chronological widths,
owned restoration, adapters, precision, movement, stock and outer transfer
remain separate obligations. No selected scientific replay, Lean or Docker
run is claimed. The selected frontier is unchanged.

## Open next questions

1. Can an actual changed native profile use the entropy screen to obtain a
   useful integer-height witness? Start with its exact target and paid
   histograms and complete mirror cells. Native semantics, width, funding
   and the physical bill remain blockers.
2. Can one interior target moment give a quantitatively sharper screen above
   the endpoint threshold? Start with a fixed positive mass separated from
   both extremes and bound the strict chord deficit. This proof uses only
   the presence of interior mass at equality, not a positive uniform margin.
