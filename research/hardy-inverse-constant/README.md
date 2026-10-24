# A sharper degree-controlled cyclic inverse constant

For a degree-n polynomial P with |P| >= delta > 0 on the unit circle,
and m interior roots counted with multiplicity, this scoped analytic proof gives

\[
 \|1/P\|_W\le(1+\pi m)(1+\pi n)/\delta
 \le(1+22m/7)(1+22n/7)/\delta.
\]

The same envelope bounds ||P(U)^(-1)|| whenever U is an invertible bounded
operator with ||U^k|| <= 1 for every integer k. In particular it applies
to unit-phase cyclic shifts at every length and stride.

Rafael Guevara's [PR803](https://github.com/CrocSwap/integer-mult-bounds/pull/803)
uses 4 instead of pi. The new step evaluates its positive Schur kernel
integral exactly, then carries the smaller constant through its cited
Hardy, rational arc-length and root-reflection chain. The rational envelope
is strictly smaller at every positive degree. The leading quadratic
coefficient at m=n changes from 16 to 484/49.

The sufficient binary norm-bound ceilings decrease from 19 to 18 at radix 3,
441 to 440 at radix 9, 11,999 to 11,998 at radix 25, and 347,859 to 347,858
at radix 71, using the same explicit PR621 circle certificate. These are
ceilings of upper bounds, not measured norms or working-precision savings.
Later PR1025's improved circle gap is a separate input and is compatible
with the general delta-parametric statement.

[PROOF.md](PROOF.md) contains the written all-degree argument and identifies
the inherited analytic premises. The classical constant pi and the positive
integral proving pi<22/7 are not new mathematics. This contribution is the
strict refinement of the repository's explicit inverse envelope. No optimal
degree dependence, paid inverse algorithm, rounded implementation, complete
supplier or new kappa is claimed.

## Reproduce

Use CPython 3.12 and the standard library, from the worktree root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/hardy-inverse-constant
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/hardy-inverse-constant/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/hardy-inverse-constant --check-source-history
```

Other machines can substitute their CPython 3.12 executable. The registered
commands run both normal and optimized Python. They print
`PASS_HARDY_INVERSE_CONSTANT` in a generated JSON receipt containing exact
results and SHA256 bindings to every package file and the consumed proof.
An optional `--emit /absolute/external/new-receipt.json` creates that receipt
outside the checkout and refuses overwrites. No receipt is hand-written.

The checks cover the polynomial division and rational integral for pi<22/7,
8,385 degree pairs with 0<=m<=n<=128, 4,096 exact logarithm brackets,
fourteen named prime-power norm budgets, and seven rejection controls.
Finite checks corroborate the new rational arithmetic; they do not prove
the analytic limits or independently validate PR803. No predecessor verifier
is run. Source bindings are in [SOURCES.json](SOURCES.json); the catalogue
and selected record are historical provenance. The originating scope change
and next questions are explicit in [TASK.json](TASK.json).

## Verification limits

The analytic proof is conditional on the explicitly cited classical and
PR803 implications. Independent human and formal proof-kernel review are
unclaimed. Rounded scan errors, preparation, routing, restoration and full
supplier admission are unrun obligations. No selected frontier changes.

The verifier has no recursion, subprocesses or network access. Its numerical
loops have fixed finite domains; the largest budget uses fewer than 350,000
bits. Functions are shorter than 60 lines, and required invariants use
explicit exceptions under optimized Python. Python's managed allocation is
a documented deviation from fixed allocation: only fourteen bounded budget
rows are retained, each source file is capped at two MiB, and no steady
service loop or mutable shared state exists. The written theorem has no
finite-degree or radix ceiling; those limits apply only to calibration.

## Open next questions

- Integrate the smaller envelope into one actual PR628 or PR764 rounded
  precision recurrence. Start with its explicitly consumed inverse norm,
  retaining preparation, every error source and dirty restoration. No such
  implementation or resource improvement is supplied here.
- Improve the quadratic degree dependence. Start with a direct two-sided
  Wiener estimate that avoids separately multiplying the reflected factors.
  Neither this proof nor PR803 establishes an optimal degree multiplier.

## Credit

This refinement was produced by Nick Petalas. Credit Rafael Guevara/PR803
for the degree-controlled inverse argument; Ali Romman/PR621 for the
prime-power setting and circle certificate; Hardy, Hilbert, Blaschke,
Dolzhenko and Spijker for the classical analytic ingredients; and
Baranov-Zarouf for the normalized arc-length source retained by PR803.
Thiago Costa/PR832 supplies a distinct Sobolev estimate, William Lawyer/PR852
treats weighted power caps, and Philipp/PR1025 improves the circle gap.
Their results are cited, not rechecked or incorporated as new work here.
Apache-2.0.
