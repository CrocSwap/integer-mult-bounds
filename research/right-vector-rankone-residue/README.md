# Exact costs above a rank-one residue

Scoped counting proof with finite corroboration. No new kappa.

Let R be a finite-dimensional local algebra over K = F_q, with K central
and canonical residue field R/J = K. Put z = |J| = q^dim_K(J). For any fixed
rank-one residue A in M_2(K), the z^4 lifts M = A + N, N in M_2(J), have
the exact paid right-vector cost distribution

```text
cost 1:  q*z^2 - q + 1
cost 2:  z^4 - q*z^2 + q - 1
```

This formula is independent of A and of radical multiplication, including
noncommutative radicals and higher nilpotency. The new result is the uniform
count, not the previously proved two-factor upper bound. It answers the
nonzero rank-one part of the singular-target direction in #4601. The
[proof](PROOF.md) counts q eligible scalar kernel lines with disjoint nonzero
parts. The hypothesis that the scalar image is nonzero is essential.

Paid factors are I + u y^T with u in R^2 and y in K^2. Common GL_2(K) maps
are free anywhere. This is the formal alphabet of Wentao Li's #4099 and
Nick Petalas's #4243/#4276. Theorem D of #4276 supplies the unit-pivot
two-factor upper bound; its Theorem A supplies the one-factor column
criterion. Those results are cited and specialized, not re-audited here.

## Exact finite evidence

The standard-library verifier independently constructs the complete literal
one-factor image from all paid left vectors, projective right vectors and
free endpoints. It then enumerates every rank-one-residue lift. For each
target it checks the new line condition against literal membership,
constructs a two-factor word and evaluates that word on every basis input
of the underlying K-vector space. No predecessor code is imported.

| Algebra | Rank-one residues | Lifts | Exact cost 1 | Exact cost 2 |
|---|---:|---:|---:|---:|
| F2 | 9 | 9 | 9 | 0 |
| F2[e]/e^2 | 9 | 144 | 63 | 81 |
| F3[e]/e^2 | 32 | 2,592 | 800 | 1,792 |
| F4[e]/e^2 | 75 | 19,200 | 4,575 | 14,625 |
| F2[x]/x^3 | 9 | 2,304 | 279 | 2,025 |
| F2[x,y]/(x,y)^2 | 9 | 2,304 | 279 | 2,025 |
| F2<x,y>/(x^2,y^2,yx, all degree-three words) | 9 | 36,864 | 1,143 | 35,721 |

The total is 63,417 lifts over 152 residues. F4 is implemented as
F2[t]/(t^2+t+1), so the checks include a nonprime field. The final algebra
has basis 1,x,y,xy with xy nonzero and yx zero. Exhaustive ring-table checks
establish associativity, distributivity, a central base field and units
exactly at the nonzero residue elements in every fixture.

Controls discriminate allowing a zero scalar image, reversing the two
factors, omitting a factor, changing the odd-field Schur sign and reversing
the noncommutative inverse order. Invalid field orders 1 and 6 are rejected.
The zero-image control is applicable to the six nontrivial-radical fixtures;
over the field itself that erroneous condition does not change the answer.
A separate binary dual-number compatibility count is [6,54,36] for the
invertible cost-0/1/2 classes, agreeing numerically with #4601/#4613/#4749.
That small compatibility check is not the contribution's deliverable.

Every run prints a generated JSON receipt binding all six package files by
SHA256. No receipt or replay output is hand-written or saved in the checkout.
All checks use explicit exceptions and remain enabled under optimized Python.

## Reproduction

From the repository root, using the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-rankone-residue/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-rankone-residue/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-rankone-residue
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/right-vector-rankone-residue --check-source-history
```

Any CPython 3.12 installation can replace the displayed local interpreter.
Expected verifier marker is
`PASS_RIGHT_VECTOR_RANKONE_RESIDUE targets=63417 residues=152`.
The runner executes both normal and optimized commands, each with a 120-second
limit. SOURCES.json pins the prior criteria as historical provenance at base
b58ad9ef4d4e861b0eaa5dba41742bdc072dca51. There are no live external inputs.

## Limits and verification design

The quantified proof covers every finite field and every radical dimension;
the finite software checks cover only the table above. The residue field must
equal the central base field. Zero-residue targets and products of local
algebras are excluded. Native coefficient preparation, conversion, routing,
control, precision, restoration, stock and complete supplier cost are unknown.
No selected operator replay, Lean or Docker build is part of this package.
Independent human and formal proof-kernel review are unclaimed.

The verifier uses no recursion, child process, network, solver or CLI input.
Its fixed cases enforce q in {2,3,4}, algebra dimension at most 4 and size at
most 16. Ring-table validation uses at most 16^3 triples. Literal one-factor
generation uses at most 16^2*5*180 = 230,400 triples. Any image set has at
most 16^4 entries. Each lift enumeration has at most 36,864 targets and each
target uses at most eight basis inputs. Receipt inputs are six fixed files,
each limited to 1 MiB. The program writes only to stdout.

Power of Ten rule 3 has a managed-runtime deviation in verify.py. Python
allocates tuples, integers and set entries during the finite enumeration;
prohibiting allocation would require a different implementation language.
The preceding enforced domain bounds limit live collections to at most one
65,536-element image set plus fixed arithmetic tables and one current target.
Warning-strict normal and optimized replays verify the same bounded path.
Follow-up is a fixed-buffer implementation if these domain bounds are ever
expanded. No such expansion is part of this result. Other functions remain
below the 60-line review ceiling. Warning-strict execution is registered in CI;
no separate Python type checker or linter is a package dependency.

## Open next questions

1. What is the lift distribution when the local residue field is a proper
   extension L/K? The shared right vectors remain K-valued, so the eligible
   line count can depend on the residue matrix. Start with F4[e]/e^2 viewed
   over F2 and one rank-one residue. The present scalar-residue assumption
   blocks applying this formula there.
2. Can a literal native producer and consumer realize this alphabet at a
   favorable complete cost? Specify one pair, its coefficients, access,
   restoration and precision contracts before constructing more words.
   Those physical costs remain unknown.

These questions and their causal relevance are also recorded in TASK.json.

## Credit

This package was produced by Nick Petalas. Nick Petalas's #4276 supplies the
one-factor and local unit-pivot results, following #4265/#4243. #4601 supplies
the singular-target question, following ToikY's #4334 local-product direction.
Wentao Li's #4099 supplies the alphabet and column bound, building on #2513.
The projective-line and finite-field tools are classical. The new claim is
their stated rank-one-residue counting application. Apache-2.0.
