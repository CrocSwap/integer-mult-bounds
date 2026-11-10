# Polynomial constants do not help a homogeneous operator alphabet

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped proof with exact finite corroboration. For an infinite
field, allow arbitrary coordinatewise scalar polynomials before or after each
labelled linear-operator call. Their constant terms may be nonzero. If every
allowed operator T preserves the constant-vector line, T e=lambda_T e, then
an exact linear endpoint has a linear implementation with no larger count in
any label. This includes arbitrary dirty inputs and every required workspace
return. The linear comparison must permit scalar multiples of T at the same
label charge.

[PROOF.md](PROOF.md) proves the statement by following the actual constant
trajectory before taking chronological derivatives. For b += p(Ta), the
extracted coefficient is p'(lambda_T c_a); for b += T p(a), it is p'(c_a).
The constant-row-sum hypothesis keeps these derivatives scalar multiples of
the original operator. No commutativity, invertibility or common flag is
required. If the row sums are independent of width, one extracted word also
works uniformly across the original operator family.

Nick Petalas's [PR6017](https://github.com/CrocSwap/integer-mult-bounds/pull/6017)
proves profile domination when every polynomial fixes zero, and asks whether
nonzero constant trajectories can help. This answers that question negatively
for the stated homogeneous alphabet. It cites that predecessor without
replaying its scientific checks. The new proof permits trajectories that
PR6017 excludes. The chain rule and polynomial identity principle are classical.
Jose Manuel / jmbarrancoml's PR1757 and Chris R / Clear1nsight's PR3992 retain
credit for their distinct nonlinear-cut and Jacobian contexts.

For example, shift the arbitrary source by c e, add (Ta)^2 to the arbitrary
destination, restore the source, subtract (Ta)^2, and remove the constant
square correction. The exact endpoint is b += 2c lambda_T T a. The first
square call has a nonzero derivative at its actual constant source, although
its derivative at local zero is zero. Extraction keeps one of the two
square-call labels. Thus this construction supplies no cheaper profile than
the permitted linear class. It is an example of the theorem, not a physical
nonlinear supplier.

## Reproduce

Use CPython 3.12 and its standard library, from the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/homogeneous-polynomial-profile/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/homogeneous-polynomial-profile/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/homogeneous-polynomial-profile
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/homogeneous-polynomial-profile --check-source-history
```

Another absolute CPython 3.12 path can replace the local path. Expected markers
are `PASS_HOMOGENEOUS_POLYNOMIAL_PROFILE`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`. The direct verifier prints a generated JSON
receipt binding all six package files by SHA256 and writes nothing.

The finite checks cover 348 complete rational polynomial endpoints, all with
nonzero constant trajectories, at dimensions one through four. They include
singular operators, noncommuting operators, rational coefficients, both gate
placements and active clean or dirty workspace returned exactly. A separate
literal interpreter checks 1,392 rational inputs and complete inverse round
trips. Another 24 nonlinear prefixes compare their full degree-one polynomials
with the extracted word. Twelve named controls cover missing correction or
restoration, differentiation at local zero, placement, nonlinear endpoints,
row-sum and shape violations, aliased ports, finite-field function identities
and both uniform-family boundaries. These finite checks corroborate the
written proof; they do not prove its universal statement by enumeration.

## Scope and limitations

This is a changed scope under `bit-new-register-model`, a helper-interface
side result. Within this alphabet, adding polynomial constants cannot evade
a linear call-profile lower bound. It supplies no native implementation,
physical supplier, full signed invoice, new kappa or multiplication theorem.
The selected frontier and its five assumptions remain unchanged.

Coordinate-dependent polynomials or vector constants, nonconstant row sums,
branching, rounded operations, restricted grids and finite-field function
identities are outside the theorem. Width-dependent row sums retain pointwise
domination but do not automatically supply uniform coefficients. Scalar work,
precision, tape, storage, stock, ownership, compiler and analytic recovery are
not priced. No predecessor scientific replay, selected cold replay, native
replay, Lean or Docker run is claimed. Independent human and formal proof-kernel
review are unclaimed.

The original card, selected record and predecessor text are provenance pins
in [SOURCES.json](SOURCES.json). There are no runtime predecessor imports or
live scientific inputs. Base main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
priority revision eight. The scope and structured follow-ons are in
[TASK.json](TASK.json). The first current selected-baseline command passed
with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; it was orientation, not a replay.
The card's old GL3 census is skipped because the investigation changes to
an infinite-field nonlinear polynomial alphabet rather than that finite model.

## Open next questions

- Can an alphabet that does not preserve the constant-vector line yield a
  strictly cheaper complete polynomial helper profile? First give its exact
  linear endpoint, every constant-preparation and restoration gate, and a
  linear-model lower bound. A cheaper word and physical native contract are
  missing. For T=diag(1,2), the after-square derivative at e is diag(2,8),
  which is not a scalar multiple of T; this identifies where the proof stops.
- Can a named width-dependent-row-sum family still have a uniform extracted
  word? First follow its constant orbit symbolically in width and specify the
  permitted coefficient ring. No source-bound native family is supplied here.

## Verifier bounds

The checker has no recursion, subprocesses, network, file writes or imported
predecessor implementation. Functions remain below sixty physical lines.
Fixture dimensions are at most four, roles at most four, word length at most
forty and coefficient lists at most four. Polynomial operations enforce at
most 4,096 retained terms, 4,096 term products and degree sixteen. A temporary
sum can hold at most 8,192 terms before normalization. Each exponent tuple
has at most sixteen entries. Receipt reads cover at most twelve files, each
at most one MiB. All iteration ranges come from these bounds or
fixed case lists. Explicit exceptions remain active under optimized Python.

Power of Ten rule three deviation: CPython allocates integers, fractions and
containers dynamically. The finite domain and enforced polynomial capacities
bound live mathematical state, with temporary products capped before creation.
Fixed-allocation arithmetic would require a different runtime; a bounded-array
port is the follow-up if this checker enters a fixed-memory environment.
Normal and optimized warning-strict runs provide the available diagnostics;
no repository-wide analyzer configuration is changed. This exception concerns
the finite checker, not the mathematical word or its unpriced physical cost.
