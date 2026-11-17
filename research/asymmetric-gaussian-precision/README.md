# Relax normalized forward accuracy by 2Gamma bits

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. In the
normalized convolution channel of Jerry Chen / CubeJerry's
[#6993](https://github.com/CrocSwap/integer-mult-bounds/pull/6993), the two
forward transforms may each have map error `2^(-a-Gamma)` instead of
`2^(-a-3Gamma)`. The opposite-transform budget and common q grid stay as in
that interface. All actual-input radius guards and the final strict
integer-recovery error `<1/4` still hold under the stated source contracts.

With `a=2ceil(log2 S)+2b+7`, `1<=S<2^b`, and integer `Gamma>=0`, the stage
requests become

```text
forward expansion/middle/compression: tau = a+2
opposite expansion/middle/compression: tau = a+2Gamma+2
common grid: q >= a+3Gamma+7, plus actual source and ledger guards
```

This saves exactly `2Gamma` requested accuracy bits at each forward stage.
It does not guarantee smaller physical widths. Fixed q, other finite
source guards and preparation can dominate. There is no new kappa or
completed physical supplier.

[PROOF.md](PROOF.md) gives the separate error polynomial, every reached
radius, the unchanged recovery scale and source-request substitutions.
The new step is this asymmetric allocation. The normalized identity,
S-squared scale and physical scalar endpoint belong to the predecessors.
Credit #6993, Cinna Davis #4100, Ryanson Jonathan #4320/#4415 and all retained
native, scalar, source, codec and Fourier contributors in #6993's NOTICE.
The classical product perturbation inequality is not claimed as a new
mathematical discovery.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/asymmetric-gaussian-precision
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/asymmetric-gaussian-precision/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/asymmetric-gaussian-precision/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/asymmetric-gaussian-precision --check-source-history
```

Replace the absolute interpreter with another CPython 3.12 installation
when reproducing elsewhere. Both registered commands print
`PASS_ASYMMETRIC_GAUSSIAN_PRECISION` in a generated JSON receipt bound to the
six package files. Optional `--receipt /absolute/external/path.json` saves
the same receipt outside the package. No receipt is hand-written or
required as a committed input.

Local normal and optimized checks pass 315 budget cases, 1,152 convolution
executions, six abstract scalar equalities and ten controls. Both direct
commands took 0.17 seconds locally; these are validation durations, not a
runtime improvement. The registered replay also passes both commands.

The verifier checks all its declared finite cases, not all mathematical
parameters. It includes literal inward rounding and an independent direct
convolution oracle for lengths 1, 2 and 4. These dyadic fixtures illustrate
the contract; they are not production odd-source transforms. The proof
covers arbitrary admitted source length under the inherited norm and
identity contracts. No predecessor scientific replay is run.

## Limits

Independent human and formal proof-kernel review are unclaimed. The selected
#7000 record, five framework assumptions, complete native/scalar costs,
original-coordinate extraction, CRT, carry/output and production source
admission are unchanged. New stage requests require their own source-first
preparation and finite applicability gates. No physical runtime, storage,
common-grid reduction or multiplication theorem is inferred.

The verifier uses bounded finite loops and functions below 60 physical
lines. Python's Fraction and container operations require runtime allocation.
This is the managed-runtime deviation from Power of Ten rule 3, confined to
this offline checker. Fixture vectors have at most four entries; scalar
allocation inputs enforce b and Gamma at most 128, and dyadic helpers cap
exponents at 2048. Hashing reads at most one MiB per package file. There is
no recursion, dynamic code evaluation, solver,
network access or predecessor import. Warning-strict normal/optimized runs
and source compilation are the diagnostic checks. Any larger finite sweep
must explicitly revise those bounds; arbitrary-parameter correctness rests
on the proof rather than an unbounded checker loop.

## Open next questions

- Can an actual separately prepared forward controller use these relaxed
  requests to lower a binding source or phase width? Pin its normalizers,
  recompute its finite reference guards and compare complete paid costs.
  No such controller is implemented here.
- Can a separately admitted pointwise precision schedule reduce the shared
  q guard without adding conversion errors? Start from the four separate
  terms in equation (1), include each grid adapter and retain the opposite
  error budget. This package keeps the original common grid.

The structured versions and blockers are in [TASK.json](TASK.json).
