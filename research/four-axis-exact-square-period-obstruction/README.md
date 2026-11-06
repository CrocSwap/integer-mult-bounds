# Exact native square requires a larger affine period

**An odd real four-axis map with the exact native square needs an affine-period
index divisible by 4,096.** The phase-only minimum of 2,048 real classes cannot
support that additional identity in the componentwise real architecture.
Existence at the larger index remains open.

Write `A=W16/4`, `S_jj=(-1)^popcount(j)`, and let `J` complement all four
coordinate bits. The stronger theorem applies to every odd integer map `R`
commuting with `K=SJ`: any full-rank affine period with linear part `A` has
index divisible by 4,096. For `F=-D R_C D`, the exact square `F^2=J` implies
`RSR=J` and the required commutation. The theorem derives invariance through
`Γ+KΓ`; it does not assume an arbitrary declared period is invariant.

This excludes neither generic `F^4=I`, nonperiodic maps nor arbitrary coupled
complex architectures. No radius, exact-sum or bijection premise is needed for
the commuting-map theorem. The exact-square identity itself implies bijectivity.

## Proof and verification

[PROOF.md](PROOF.md) gives the complete argument. In the integrality quotient
`V=L/2L`, the even-class subspace `E` has dimension 5. Oddness makes the period
image avoid `E`. The operator `K+I` has rank 1 on `E`, but two independent
vectors of `E` lie in its image on `V`. A codimension-5 invariant period image
would preserve those two independent classes in a rank-1 image, a contradiction.
This yields a divisor of `64·64=4096` for the period index.

[verify.py](verify.py) imports no predecessor code or solver. It uses integer
arithmetic to check complete matrix identities, the integrality criterion, all
31 nonzero parity-basis combinations, the rank-one action and both decisive
image witnesses. Three controls reject a malformed preimage, a false image and
omission of the essential sign phase. Its predicates stay active under `-O`.
The checker emits all package file hashes. A separate [independent.py](independent.py)
uses literal Walsh divisibility modulo eight as its lattice-membership oracle
and constructs the second preimage from the lattice generators. It imports
neither the primary checker nor a predecessor package; normal and optimized
modes emit `PASS_INDEPENDENT_PERIOD_WITNESSES`. A scoped proof, rather than failure
to find a matching, establishes the result.

From the repository root, CPython 3.12 and the standard library:

```sh
python3.12 -W error -B research/four-axis-exact-square-period-obstruction/verify.py
python3.12 -O -W error -B research/four-axis-exact-square-period-obstruction/verify.py
python3.12 -B scripts/research_package.py --package research/four-axis-exact-square-period-obstruction
python3.12 -B scripts/check_research_commit.py --package research/four-axis-exact-square-period-obstruction --check-modes
```

The supplied repository is shallow; full `--check-source-history` validation
requires a full-history checkout and is not claimed. No formal proof-kernel
verification, complete physical tariff or new kappa is supplied.

## Scope and sources

This is the bounded seed-66 follow-up to the seed-27 native precision audit.
[TASK.json](TASK.json) retains the full original `uniform-transfer-audit` card
and records the changed scope. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8. None of the
selected multiplication theorem's five inherited assumptions is discharged.

The related phase-only construction is published at
[commit 362b20bc934500bc503e850059f0d34daa5dcae3](https://github.com/CubeJerry/integer-mult-bounds/tree/362b20bc934500bc503e850059f0d34daa5dcae3/research/four-axis-phase-covariant-grid).
It remains unchanged, has no upstream PR number, and is discovery context
rather than a runtime dependency.

Nick Petalas's #6561, head `e8a55a6edf91c5067b26cdfefbcc76517f86ab02`, was
inspected for overlap: its integral signed-permutation equivariant rounders
have no bijection or exact-square requirement. Its contract is distinct.
Nick Petalas's #6574 supplies the sharp native starting interface; credit is
retained to Ali Romman and David Ganz / Dugongue for the Gaussian native lineage.
[SOURCES.json](SOURCES.json) records the exact inspected commits and bytes.

Prepared by @CubeJerry with substantial OpenAI Codex assistance, including
independent root-agent witnesses and Worker A's adversarial [proof review](REVIEW.md).
New work is Apache-2.0. Review does not imply formal or scientific admission.

## Open next questions

Can a larger period support a sharp exact-square map? First seek a `B=SA`-
invariant period of index 4,096 satisfying both odd half-period conditions.
For `T(z)=Bz+c([z])/4` and quotient transition `p(s)=[T(r_s)]`, exact square
requires `c(p(s))=-B c(s)`, alongside integrality, oddness, sharp energy,
weighted sum and a class bijection. Ordinary bipartite matching does not
impose that coupled cycle identity. Neither the larger period nor a compatible
rounding certificate is constructed here.
