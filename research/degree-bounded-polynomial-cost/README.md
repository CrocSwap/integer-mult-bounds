# Exact cost law for uniform bounded-degree polynomial targets

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped counting proof with exact finite corroboration. This answers Open next
question 1 of [PR4784](https://github.com/CrocSwap/integer-mult-bounds/pull/4784).
Its exact-degree count is a cited premise, not an audit deliverable.

Choose M uniformly among GL2(F_q[t]) matrices of maximum entry degree at most
N. Paid factors are I+u y^T with polynomial u and base-field y. GL2(F_q) maps
are free anywhere, there are two roles, and no auxiliary role is available.
Let C be the minimum paid cost, e=q^(-2N) and B(z)=q+q(q-1)z. The new law is

```text
E[z^C] = q^(-2N) [1+(q^2-1)z (B(z)^N-1)/(B(z)-1)],
E[C]   = (q-1)N/q + (1-e)/(q+1),
Var(C) = (q-1)N/q^2 + 2(q-1)Ne/[q(q+1)] - (1-e)(q-e)/(q+1)^2.
```

The quotient is the finite geometric polynomial, including its removable
value N at B=1. The formulas hold for every prime power q and N>=0. They
include the constant matrices, whose cost is zero. For N>=1, the bounded-
degree mean is below the exact-degree-N mean by exactly
`1/[q(q+1)]+q^(-2N)/(q+1)`. The individual target costs are unchanged.
[PROOF.md](PROOF.md) supplies the finite-sum derivation.

For example, q=2 and N=4 gives count weights `[1,45,102,84,24]`, divided by
the common factor |GL2(F2)|. The mean is 597/256 and variance 51399/65536.
The weights agree with the predecessor's existing binary bounded-degree
census; that census is credited prior work. The new result is the closed
law and moments for the changed sampling measure at arbitrary q and N.

## Evidence and reproduction

The verifier compares the cited joint-count mixture with an independently
formed geometric polynomial for all 495 integer pairs 2<=q<=16, 0<=N<=32.
It checks both moments by exact coefficient sums, and evaluates the PGF at
1,980 rational points, including every removable-pole case. Non-prime-power
q only test arithmetic identities, not finite fields.

A second enumeration covers 7,362 weighted digit strings in 28 small
mixtures, with q=2..5 and N=0..6. These are digit strings, not a fresh
polynomial-matrix census. Three boundary fixtures and ten rejection controls
cover invalid domains, omission of the free targets, exact-degree sampling,
an incorrect mean and an incorrect variance. No predecessor program runs.

From the repository root, using standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/degree-bounded-polynomial-cost/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/degree-bounded-polynomial-cost/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/degree-bounded-polynomial-cost
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/degree-bounded-polynomial-cost --check-source-history
```

Another CPython 3.12 executable may replace the local interpreter path.
The direct marker is `PASS_DEGREE_BOUNDED_POLYNOMIAL_COST`. The generated
stdout receipt binds all six package files and the cited proof by SHA256.
Replay writes no checkout files. Registered commands each have a 120-second
limit. [VERIFY.json](VERIFY.json) declares the sole external proof input.

The discovery base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priorities revision 8, selected
PR6030. The selected source-binding orientation passed; no selected scientific
replay ran. [TASK.json](TASK.json) changes the scalar-to-moment card to this
formal-algebra side result and records the
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370254).
Live open/account PRs, recent claims, local reservations, main formula/object
searches and merged searches were checked. The overlap cache covers 506 open
PRs and 6,507 Discussion records with complete remote pagination. Sparse
local notes, arbitrary historical diffs and unpublished work remain limits.

## Limits and implementation bounds

The universal result uses PR4784's cited degree/cost theorem. It does not
reprove its normal form. Uniform words, singular targets, other coefficient
algebras, more roles and restored auxiliary roles are outside scope. Native
preparation, conversion, routing, control, precision, restoration, stock and
complete supplier costs remain unpriced. No new kappa, selected-frontier
change, supplier admission or complete multiplication theorem is claimed.
All five selected assumptions remain. Independent human and formal proof-
kernel review are unclaimed. Lean, Docker and selected cold replay are unrun.

The code has no recursion, subprocess, network, dynamic code or callbacks.
q and N have explicit finite bounds; coefficient lists have at most 33
entries and digit tuples at most five. At most 495 parameter records are
retained. Seven source reads are capped at 256 KiB each. Functions fit within
60 lines. Guards remain enabled under optimization. Warning-strict normal
and optimized execution supplies interpreted-code diagnostics; no external
static analyzer is claimed. Managed Python allocation is a Power of Ten
rule 3 deviation: CPython integer arithmetic and JSON serialization allocate
during verification. The fixed domains and file capacities bound retained
state, and both registered runs exercise their maximum q and N. Revisit
these capacities before expanding the domain; a fixed-storage runtime port
would need its own arithmetic and receipt implementation.

## Open next questions

- Obtain a quantitative normal-approximation error for this exact bounded-
  degree measure. Start with the geometric degree deficit and the cited
  conditional binomial law. A uniform error estimate is not supplied here.
- Identify one native polynomial-coefficient producer and consumer before
  applying this formal law to a supplier. First price coefficient preparation,
  then conversion, restoration and the complete recursive bill. Those costs
  and the physical interface are missing.

## Credit

Nick Petalas's PR4784 supplies the exact-degree theorem and the explicit
bounded-degree moment question. Its retained lineage includes PR4763/4276/4243,
Wentao Li's PR4099 following PR2513, ToikY's PR4334 and the local/semilocal
comparisons. Nagao's polynomial-matrix presentation and degree method remain
classical predecessor work. [SOURCES.json](SOURCES.json) pins the unchanged
predecessor proof. The new contribution is the bounded-degree sampling law
and its closed moments, not a new classical normal-form theorem.
