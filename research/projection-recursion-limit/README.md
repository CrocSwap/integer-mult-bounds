# Exact rational limit of the Lagrangian projection recurrence

**Scoped mathematical proof with finite corroboration; no new kappa.**
The projection recurrence of Jacob Alan Sussman [#4628](https://github.com/CrocSwap/integer-mult-bounds/pull/4628)
and Maximilian Lutz [#4643](https://github.com/CrocSwap/integer-mult-bounds/pull/4643)
has the exact asymptotic ratio

```
lim_(m->infinity) a_m(m)/a_m(1) = 439277/149175.
```

The displayed decimal is 2.9447092341209986... . The new result identifies
this limit exactly, proves convergence with an explicit error bound, and
gives the limit for every nonnegative seed profile at any fixed seed block.
It extends the predecessors' numerical tail description. It does not
re-check their hook ranks, projection geometry or engine implementation.

## The result

[PROOF.md](PROOF.md) defines the recurrence and proves that a seed profile
`a_b(0)=0`, `a_b(1)>0`, `a_b(r)>=0` has limit

```
(2^(b+1)+1) / (2(2^b-1) product_(i=1)^b(2^i+1))
* sum_(r=0)^b [b choose r]_2 2^(r(r+1)/2) a_b(r)/a_b(1).
```

Here `[b choose r]_2` is the Gaussian binomial coefficient. For the cited
block-four seed `(0,27456,48576,68320,86592)`, the distance weights are
`(1,30,280,960,1024)/2295` and the remaining factor is `11/10`.
The result is a finite rational expression, despite the infinite products
and stationary laws that appear in its proof.

The proof normalizes the integer recurrence into a Markov reduction,
uses coherent uniform-Lagrangian distance laws, and compares the deficit
with a homogeneous birth-and-death chain. A monotone coupling has expected
coalescence time at most `9/2`. A summable row-error bound proves convergence
to the coherent seed-block law. Equation (1) of PROOF.md gives the explicit
all-m error estimate. The proof invokes no numerical mixing assumption.

This theorem is unconditional for the displayed arithmetic recurrence.
Its engine-game interpretation is conditional on the predecessor's hook
profile and representation argument. In particular, the two stored-rank
certificate obligations identified in #4643 remain unresolved here.
The result does not assert monotonicity, a finite-m infimum, the optional
triangle/max strengthened recurrence, physical costs, native admission,
a new supplier, or a complete multiplication theorem. The selected
frontier is unchanged. Independent human and formal proof-kernel review
are unclaimed.

## Reproduce

From the repository root, use CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/projection-recursion-limit
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -X dev -W error -B research/projection-recursion-limit/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -X dev -W error -B research/projection-recursion-limit/verify.py
```

Another CPython 3.12 interpreter may replace the absolute local path.
Success markers are `PASS_PROJECTION_RECURSION_LIMIT` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. Both registered commands run with a
120-second timeout. Default verification is read-only and writes no receipt.
Explicit `--emit` prints newly generated hash-bound evidence to standard
output; [RESULT.json](RESULT.json) was generated through that command.

The standalone checker imports no predecessor code. It checks 3,320 new
kernel-coordinate and row-error identities, 63 coherence reductions,
80 detailed-balance/monotonicity indices, 73 seed-profile limit enclosures,
54 enclosures for six other seed blocks, and 38 independent comparisons
between probability-law propagation and the integer recurrence. Six
controls distinguish wrong normalization, a wrong exact limit, a changed
seed, a corrupt transition and a wrong coherent law. These finite checks
corroborate the written proof; they do not replace its infinite-limit
argument. The generated receipt binds the verifier, proof and cited source
README by SHA256. The registered runner also authenticates source metadata.

New code is bounded to block/index 100 and uses explicit exceptions under
normal and optimized Python. Each function is below 60 lines. Python's
managed integers and fractions allocate during execution, a deliberate
Power of Ten deviation; the finite index limits bound live collections
and integer sizes. No recursion, dynamic code execution, external solver,
network call, subprocess or background process occurs in the verifier.
Warning-strict development-mode replay supplies interpreter diagnostics;
no static type checker or formal kernel is claimed.

## Sources and overlap

Scientific base is `a5df48c55ea806d7952b65acc9c76d878ff09b13`, priority
revision 7. [SOURCES.json](SOURCES.json) pins the predecessor README,
task catalogue and selected record. Only the predecessor README is a live
input; its source bytes remain unchanged. Arbitrary code diffs and unpublished
work are outside the overlap search. The sparse local-note inventory is
incomplete and was supplemented with targeted main-tree and merged-PR searches.
The local card changes from independent ledger checking to this original
closed-form recurrence theorem; it is a complex small-block side result.

## Open next questions

1. Does this recurrence admit a finite-m closed form, or a faster convergence
   rate? The present proof gives an explicit error estimate and an exact limit.
   Begin with the coherent-law comparison rather than recomputing hook ranks.
2. Which seed profiles make the top ratios monotone, and when is their
   infimum the limit? A limit alone does not settle these questions. Start by
   examining adjacent-block differences as linear functionals of the seed.

Neither question requires another physical construction round. The separate
engine, hook-rank, native, precision, hosting and complete-cost obligations
remain with their existing investigations. Structured questions are in
[TASK.json](TASK.json).

## Credit

This result was produced by Nick Petalas. Jacob Alan Sussman #4628 supplies
the projection recurrence and block-four hook profile. Maximilian Lutz #4643
supplies its public count formulas, coherent geometry context and prior tail
analysis, including the explicit unresolved rank obligations. Eumemic #288
and Swapnil Jain retain the underlying certificate-method credit. Classical
Gaussian-binomial counting, symplectic reduction, birth-and-death chains and
coupling arguments retain their mathematical authorship. No literature-priority
claim is made for those methods. New work is Apache-2.0.
