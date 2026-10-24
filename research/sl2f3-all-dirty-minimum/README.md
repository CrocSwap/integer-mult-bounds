# The SL2(F3) conjugate triple needs five calls with any dirty workspace

For every finite number of restored dirty roles, the exact formal paid-call
minimum for `diag([i],[w],[w^-1 i w],1,...,1)` remains **five**. This is a
scoped proof with finite corroboration. It answers Open next question 1 in
Wentao Li's [#4083](https://github.com/CrocSwap/integer-mult-bounds/pull/4083),
which settled one dirty role and left two or more open.

The alphabet is unchanged: `G=SL2(F3)`, paid labels `i,i^-1,w,w^-1`, and
`D_N(g)=I+([g]+[1])N` for any binary rank-one idempotent `N` on all roles.
Here `i=[[0,1],[-1,0]]`, `w=[[0,-1],[1,-1]]` over F3. Arbitrary constant
`GL_r(F2)` mixing is free; every input is arbitrary and every extra role must
return unchanged. [PROOF.md](PROOF.md) proves the result for every `r>=3`.

## New step and consequence

The first-order representation of `Q8 semidirect C3` gives a rank-two target
defect, forcing two quaternion-label calls. In the character quotient, any
one- or two-call realization of the required order-three output has all its
projectors on that output alone. Its other columns cannot acquire the
nonbinary first-order coefficient of `w^-1 i w`. Therefore three order-three
calls are necessary, independently of the number of restored dirty roles.
The predecessor's coordinate word attains `2+3=5`.

The new contribution is this all-role proof and the order-three projector
rigidity argument. Cinna Davis's original three-role result
[#2010](https://github.com/CrocSwap/integer-mult-bounds/pull/2010) and Wentao
Li's one-dirty-role result retain their credit. Their searches are not rerun.
Sagar Thakrar's [#4032](https://github.com/CrocSwap/integer-mult-bounds/pull/4032)
supplies the predecessor twisted radical-rank method and the question about
extending it to a normal 2-group with an odd-order complement.

Further dirty-role censuses cannot improve this endpoint under these
hypotheses. The decision is local to this formal alphabet. A physical native
realization, its prices, supplier admission and a new kappa remain unproved.
Clean-only inputs, partial restoration, other targets and enlarged coefficient
fields are outside the result. In particular the first-order map kills the
nonidentity central element -1; it cannot certify pure central defects.

## Reproduce

From the repository root, using CPython 3.12 and only the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/sl2f3-all-dirty-minimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/sl2f3-all-dirty-minimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/sl2f3-all-dirty-minimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/sl2f3-all-dirty-minimum --check-source-history
```

The registered commands use `{python}` for portability. The expected final
marker is `PASS_SL2F3_ALL_DIRTY_MINIMUM minimum=5 i_floor=2 w_floor=3`.
The verifier prints a generated receipt bound to all six package file hashes;
it does not write files. No receipt is hand-authored or stored as an expected
answer.

Finite coverage is separate from the all-role proof:

- All 576 group-pair cocycle identities.
- All 308 one-call and 60,880 two-call quotient words on 2, 3 and 4 roles.
  Exactly one of each length reaches the quotient target at each role count.
- 312 deterministic sampled full-group-algebra words on 3, 5 and 8 roles,
  with lengths 0 through 12. These are samples, not an exhaustive word census.
- The five-call endpoint on all 384 regular-action basis inputs across
  3, 5 and 8 roles, including two and five dirty roles.
- Eleven enumerated controls: the five single-call omissions, reversed
  conjugation, unrestored dirty output, a changed unconjugated target,
  nonbinary projectors, wrong cocycle orientation and the central kernel.

The nonbinary control exhibits two distinct F4 rank-one idempotents with
the same quotient endpoint; the binary rigidity proof cannot be reused in
that enlarged field. The dirty-output control passes data-only comparison
and fails the required full endpoint. Checks use explicit exceptions under
both normal and optimized Python.

## Verification bounds

All code is package-local; no predecessor executable is imported. Loops have
fixed finite bounds, matrices have at most eight rows, sampled words have at
most twelve factors, and the largest materialized quotient alphabet has 240
entries. Its two-call product is streamed. Functions are below 60 lines.
Warning-strict normal and optimized execution are the available diagnostics;
the checkout supplies no Python linter configuration or installed static
checker for this package.

```
Rule: 3, fixed memory before steady operation.
Location: verify.py exact finite computations.
Reason: CPython allocates integers, tuples and interpreter objects dynamically.
Scope: this bounded one-shot verifier, with no input-driven growth.
Compensating control: eight-role/twelve-factor limits and fixed fixture counts.
Verification: both registered warning-strict replays exercise all fixtures.
Follow-up: use fixed buffers if this verifier becomes a long-running service.
```

Sources, exact Git blobs and SHA256 hashes are in [SOURCES.json](SOURCES.json).
Those literature and task files are provenance, not replay dependencies.
[TASK.json](TASK.json) records the priority-7 card and the changed scope.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Is there a fully priced native address-operation realization of this alphabet
for a changed endpoint that could save paid work? This is the remaining
physical-interface question from #4083, not a reason to enlarge the closed
dirty-workspace search. Start by pinning one arbitrary-input `D_N(i)` or
`D_N(w)` program and charging address movement, source access, hosting and
restoration. The missing native implementation and complete producer/consumer
bill are the blockers. No such program is supplied here.

## Credit

This contribution was produced by Nick Petalas. Apache-2.0.

Cinna Davis #2010 retains the endpoint, four-label alphabet and five-call
direct word. Wentao Li / VictorLiwentao #4083 retains the one-dirty-role
result and the explicit remaining question. Sagar Thakrar #4032 retains the
twisted radical-rank method and its normal-2-group extension question, building
on Cinna Davis #2116, #2047 and #2248. The retained register-model lineage
includes Aaron Wang / navinor #1822, Ali Romman #468 and eumemic #288.
The first-order representation and rank subadditivity are elementary tools;
no literature-wide priority is claimed for them. The new claim is the stated
all-role endpoint theorem and its explicit proof.
