# Exact local right-vector cost at residue corank one

This contribution was produced by Nick Petalas. Scoped algebraic proof,
with bounded finite corroboration. No new κ or supplier admission.

For every central field K, associative local K-algebra R with residue
division algebra D, and n-role target M of residue rank n-1,

    cost(M) = delta(M) = n - dim_K M(E) <= n,
    E = {v in K^n : Mv is in K^n},
    delta(M) = min_{T in GL_n(K)} dim_K ((MT-I)K^n).

Paid factors are I+u y^T with u in R^n and y in K^n. Arbitrary free GL_n(K)
maps are allowed anywhere. The final paid factor can be singular.
[PROOF.md](PROOF.md) gives an attaining word with no additional roles.
The residue division algebra can be noncommutative or larger than K.
Finite dimension and nilpotence of the radical are not required.

The new part is arbitrary-role singular endpoints with residue corank one.
Nick Petalas's #4276 covers two-role local targets with a unit entry;
#4787 covers arbitrary-role invertible local targets. ToikY's #4334 leaves
singular targets outside its product theorem. Those are cited predecessors,
not verification deliverables. The singular correction to the fixed-space
formula matters even for diag(1,1,0), whose cost is one, although E=K^3.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/local-corank-one-cost/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/local-corank-one-cost/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/local-corank-one-cost
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/local-corank-one-cost --check-source-history
```

Any CPython 3.12 path may replace the local path. The verifier prints a
generated JSON receipt with package SHA256 hashes, followed by
`PASS_LOCAL_CORANK_ONE_COST`. It writes nothing.

## Evidence and limits

The verifier constructs literal words over binary and ternary dual numbers,
a binary two-generator square-zero algebra, F4 over F2, and the noncommutative
algebra F4[e;Frobenius]/e^2 over F2. It checks ring laws, central scalars,
local units and the residue map before using an algebra. Samples have three
or four roles. The binary dual-number checks also include every one of the
512 lifts of diag(1,1,0). Other target sets are bounded deterministic samples.
Each word is checked as a complete matrix and on every base-field basis data
vector. A separate calibration evaluates every GL3(F2) chart on selected
targets to compare the direct definition of delta. Domain and word mutations
are rejection controls. The main checks cover 1,112 targets, 8,272 basis-data executions and 5,376
direct chart evaluations, with eight rejection controls. Two additional shared
two-role targets over F4[e]/e^2 have costs one and two, respectively. They
connect numerically to #4781 without repeating its counting deliverable.
Numerical receipts are produced by the verifier.

The universal claim rests on the written proof. Independent human and formal
proof-kernel review are unclaimed. Higher residue corank, nonlocal algebras,
physical coefficient preparation, frames, routing, restoration, precision and
stock remain outside scope. Lean, Docker and the selected operator replay
were not run. The selected frontier is unchanged.

The formal-interface card is explicitly changed to this algebraic side
question. Its historical first command, scripts/research_baseline.py, fails
with KeyError: 'bit_lower' under the selected #4470 schema. No baseline pass
or theorem acceptance follows from that orientation command. Canonical main
is pinned at 624de9dc66858af0945e5f8a0942488d62280d43, priority revision 7.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132023)
records live overlap checks and their incomplete coverage.

## Engineering notes

Build the Lever led to the literal word constructor and independent direct
chart comparison. Prove It Works led to checking actual matrix endpoints and
basis data. The code has no recursion; every collection and loop is bounded
by the fixed five algebras, at most four roles, 4,000 sample attempts and at
most 16 algebra elements. Functions stay below 60 lines. Explicit checks
remain active under optimization. Python dynamic allocation and callbacks in
rejection controls are managed-runtime deviations from Power of Ten; live
collections have these fixed bounds. No external dependencies are imported.

## Open next questions

1. Which residue-corank-two local targets attain delta? Begin with one
   three-role target over F2[x,y]/(x,y)^2 whose residue is diag(1,0,0).
   The next missing pivot can be a nonunit, so a new completion criterion is
   required. This would identify how far the singular theorem extends.
2. Can a named native caller realize one of these singular column factors
   with all preparation, frame, movement and restoration charges? Start by
   stating its dirty-input/output contract. No physical invoice is known.

Structured questions are in [TASK.json](TASK.json).

## Credit

ToikY #4334 supplies the singular-target gap. Nick Petalas #4276/#4243 and
#4787 supply predecessor criteria, lower bounds and local constructions.
Wentao Li #4099 follows the #2513 alphabet and column-bound lineage.
Basis extension, Gaussian elimination, Schur complements and local-ring unit
lifting retain classical credit. This contribution adds the scoped theorem,
its singular fixed-space formula and the self-contained bounded verifier.
Apache-2.0.
