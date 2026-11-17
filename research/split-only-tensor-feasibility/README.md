# Exact tensor feasibility under capped splitting

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. For any
fixed finite positive-integer paid and target inventories, real 0<t<1
and positive integer cap base c, tensoring and disjoint capped splitting
can beat the unchanged target moment at some positive tensor power exactly
when

```text
max(P_t, P_1 c^(t-1)) < T_t.
```

Here P_s and T_s are the inventories' power sums. At power v the cap is c^v.
The optimal paid charge S_v has the exact exponential rate

```text
lim S_v^(1/v) = max(P_t, P_1 c^(t-1)).
```

Equality in either inequality excludes a strict gain at every power. This
can reject a futile cap choice before searching tensor powers or tail
parameters. Every partition of each job into capped integer pieces is
covered. Cross-job merging and target completion are outside this model.
No new kappa, native supplier or selected-frontier change is claimed.

[PROOF.md](PROOF.md) gives the all-real, all-power argument. Its elementary
two-sided bound is

```text
max(P_t^v, (P_1 c^(t-1))^v) <= S_v
    <= P_t^v + (P_1 c^(t-1))^v.
```

If k>=2 is the least target rank, some legal integer cap c<k gives both
separation and a moment gain at some power exactly when P_t<T_t and
P_1 (k-1)^(t-1)<T_t. This is an accounting criterion for padding-free
splitting. Native tensor closure and a full compiler remain separate.

## Discriminating examples

At t=1/2, the abstract inventory T={4,4,4}, P={9} has both raw moment
surplus and rank-one surplus equal to three. Cap base two still fails at
every power, because 9/sqrt(2)>6. Cap base three passes the criterion.

For T={81}, P={17}, c=4, the first-power split charge is exactly nine,
equal to the target. At the second power it is 73<81. This distinguishes
eventual feasibility from an immediate win. The verifier also treats both
types of equality obstruction. None of these inventories is asserted to
have a native realization.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/split-only-tensor-feasibility/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/split-only-tensor-feasibility/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/split-only-tensor-feasibility
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/split-only-tensor-feasibility --check-source-history
```

Other machines may substitute any CPython 3.12 path. The direct verifier
writes nothing, imports no predecessor executable and works without Git or
network access. It prints generated JSON bound to all six package-file
hashes, followed by `PASS_SPLIT_ONLY_TENSOR_FEASIBILITY`. No receipt is
handwritten or used as an answer oracle. The metadata and committed-byte
checks separately authenticate provenance and publication bytes.

The finite replay checks 18,432 one-job splits at six rational exponents;
256 exact dynamic-programming partition optima; 468 tensor histograms;
and 2,496 profile/cap/target-moment decisions. The 1,767 passing decisions
each have an actually evaluated sufficient-power witness, at powers up
to twenty. Independent literal enumeration checks 3,072 ordered job tuples
and 176 explicit partition contexts. Thirty-nine boundary checks and
fifteen invalid-input rejections protect remainder costs and strictness.
Rational root brackets use integer arithmetic; comparisons fail if their
intervals do not separate. The universal theorem rests on the written proof.

## Sources and scope

Base canonical main is `e54523517d0f03e58352e647c403a5af3e525a57`, priority
revision eight. The selected record is #7000 and kappa=0.00363005817.
The selected binding-only orientation passed; it is not a supplier replay.
[SOURCES.json](SOURCES.json) pins historical provenance, including zxv's
PR4433 framework document. There are no external scientific runtime inputs.

Credit zxv's [PR4433](https://github.com/CrocSwap/integer-mult-bounds/pull/4433)
for the tensor paid-splitting framework; Cinna Davis's PR4412/4414/4416
for chronological product and completion; and Jacob Alan Sussman for the
integer compiler. Their native, helper, controller and outer lineage retains
its credit. The new step is the exact exponential rate and any-power
feasibility criterion. Concavity and the product/squeeze arguments are
classical; no global literature-priority claim is made for those ingredients.

Nick Petalas's PR4832/6390 one-job coefficient results and PR7135 net-tax
optimizer are background, not premises or main steps of this proof. This
result does not change their optimizers or reuse their constructions. It
changes the independent-moment card from audit to an original quantified
accounting theorem, as recorded in [TASK.json](TASK.json).

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19595330)
states the same scope. Entry checks covered live open/own PRs, the handoff
and active Discussions, all tracked main README/proof literal searches,
and merged-PR searches. The cached helper reported 826 open PRs and 7,445
Discussion records with complete pagination. Its sparse local coverage
was only 228 of 10,178 notes, supplemented by direct Git searches.
Arbitrary historical diffs and unpublished work remain outside coverage.

This is not a complete signed invoice when completion, target debits or
other costs apply. Physical arbitrary-input realization, ownership,
restoration, chronological native closure, stock, precision, tape and outer
recovery remain unproved and unpriced here. All five selected assumptions
remain. No predecessor scientific verifier, selected cold replay, Lean or
Docker run was performed. Independent human and formal proof-kernel review
are unclaimed.

## Open next questions

1. Can one changed native inventory use this screen to avoid target
   completion? Start with its complete tensor/splitting contract and the
   two moments at c=min(target)-1. Native realization and full physical
   costs remain blockers.
2. What is the exact feasibility criterion when same-owner target completion
   is also allowed? Start with both completed inventories at one fixed
   floor base. A joint two-sided estimate is missing; this result cannot
   discard the completion charge.

## Verifier constraints

The verifier has no recursion, subprocesses, network access, writes or
generated code. Every function is under sixty lines. Integer-root bisection
has a bit-length iteration cap. Scientific fixture loops have explicit
finite domains; tensor powers are capped at 64, profile supports at three,
histograms at 5,000 entries and power inputs at 1,024 bits. Source reads cover
six files capped at 256 KiB each. All guards remain active under optimization.

Power of Ten rule 3 has a managed-runtime deviation. CPython allocates
integers, fractions and bounded containers dynamically. The fixture caps
bound live algorithmic state; allocator internals are not instrumented.
Warning-strict normal and optimized runs and AST/function-size inspection
are the available diagnostics. No repository-wide static analyzer or
fixed-allocation implementation is claimed.
