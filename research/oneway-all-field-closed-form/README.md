# All-field closed form for one-way coupled full guards

This scoped counting proof was produced by Nick Petalas. Apache-2.0.

## Scope and evidence

For rank-one idempotents U,V over F_q^m with UV nonzero and VU=0, the
two requests I-U,I-V use one complete, uniformly weighted GL_m header.
A request passes when every leading principal minor through its rank
is nonzero. Put n=m-1 and

```text
alpha=(q^2-q+1)^2, beta=q^3-q+1, gamma=q^3-q^2+1.
```

The exact normalized passing-pair numerator is

```text
C(q,m)=(q-1)/q^2 * [(q-1)alpha^n-(q-2)beta^n-gamma^n].
```

Divide by `(q^m-1)(q^m-q)q^(2m-4)` for the probability, for every finite
field and every m>=2. At q=5 this is `(4/25)[4*441^n-3*121^n-101^n]`.
The m=2 passing fractions for q=2,3,4,5 are 1/6, 1/4, 7/20, 13/30.

[#4274](https://github.com/CrocSwap/integer-mult-bounds/pull/4274) supplied
the all-field transfer and the binary closed form. The new step in
[PROOF.md](PROOF.md) changes the initial matrix in
[#4747](https://github.com/CrocSwap/integer-mult-bounds/pull/4747)'s
three-function invariant system and solves its coefficient recurrence.
Both predecessor theorems are cited, not audited or claimed as new.

The self-contained verifier checks 4,095 integer-parameter coefficient
comparisons at 2<=q<=64 and 0<=n<=64, and 36 raw partial-Gram transfer
cases over F2,F3,F4,F5 at 0<=n<=8. It explicitly visits 182,048
source/target state pairs. It also enumerates every complete GL2 header
over F2,F3,F4,F5,F7,F8,F9, a total of 12,018 headers, including extension
fields. Six semantic controls and four input-bound rejections remain
active with assertions disabled. The generated stdout receipt binds all
six package files by SHA256; no handwritten receipt is stored.

This algebraic side result changes the `formal-interface-lemma` card's
premise, as recorded in [TASK.json](TASK.json). [SOURCES.json](SOURCES.json)
pins the original catalogue, selected record and retained #4274 proof as
historical provenance. There are no live external code inputs or Python
dependencies. The exact external #4747 theorem citation is at commit
`f51dcebce79b8b8958427a9a9b7bc8feca352c9d`; no pending Git object is
needed to execute the package or its publication preflight.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/oneway-all-field-closed-form/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/oneway-all-field-closed-form/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/oneway-all-field-closed-form
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/oneway-all-field-closed-form --check-source-history
```

Replace the local interpreter path with another CPython 3.12 installation
elsewhere. Expected markers are `PASS_ONEWAY_ALL_FIELD_CLOSED_FORM`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
The last command requires a publication commit and full Git history.
The direct verifier writes nothing and can run from a Git-free package copy.

## Limits and implementation constraints

The universal statement uses the written argument and the cited invariant
theorem. Finite execution corroborates its stated domains. Only two fixed
one-way coupled rank-one kernels and complete uniform headers are covered.
Physical selection, emission, dispatch, dirty restoration, precision and
stock costs remain unknown. No new kappa, supplier admission or complete
multiplication theorem follows. Independent human and formal proof-kernel
review are unclaimed. Lean, Docker and selected operator replay are unrun.

The verifier has no recursion or dynamic code loading. Its largest state
matrix is 400 by 400, replay length is at most eight, field tables have at
most 81 entries, and coefficient checks stop at q=64,n=64. Functions stay
below 60 lines. CPython allocation and iterator dispatch are managed-runtime
deviations from Power of Ten rules 3 and 9, bounded by these fixed domains.
No plugin or callback registry is used. Normal and optimized warning-strict
commands exercise the same explicit checks. A fixed-capacity native replay
would require a separately specified integer capacity and is not supplied.

## Open next questions

1. Does the one-way joint law have strict negative correlation over every
   finite field? Compare this formula with #4227's squared marginal after
   checking live claims. The odd-field inequality is not proved here.
2. Can a named odd-field producer use a fully charged one-way shared-header
   caller? Pin its kernel pair and header domain, then price selection,
   emission, dispatch and dirty return. Unknown physical costs block any
   supplier consequence. Structured first steps and blockers are in TASK.json.

## Credit

Nick Petalas's #4274/#4261 supplied the transfer and equal-header fibers;
#4747 supplied the all-field invariant identities; #4227 supplied the
corank-one guard and marginal context. The binary formula and small prime
examples are predecessor credit. Cinna Davis supplied the BIT request
context; source527, commdata2338 and Jose Manuel retain the normalizer and
recursive-closure lineage credit. No predecessor files are modified.
