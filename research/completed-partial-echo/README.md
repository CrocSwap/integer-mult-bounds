# Completed partial echoes share source injections

This contribution was produced by Nick Petalas. Claim type: scoped algebraic
construction and exact optimality proof, with finite corroboration. No new
kappa or physical supplier is claimed.

Two successive complete external-source updates need six macro calls rather
than eight separate-echo calls, while preserving every observed output and
restoring arbitrary borrowed data. The new step answers the normalized-block
part of [PR4860's second open question](https://github.com/CrocSwap/integer-mult-bounds/pull/4860).

For s independently arbitrary linear blocks

    H_i(D,W) = (D + L_i W, W),

let the complete forward/inverse prices be c_i^+,c_i^-. The only additional
instructions are W += X and W -= X, priced a,b>0. X is immutable; X,W,D
all start arbitrary. At checkpoint j the observer must see precisely
D_initial + sum_(i<=j) L_i X. It observes D only. W may retain a source shift
between checkpoints and must return exactly to its incoming value.

For every s>=1 over a characteristic-zero field, the exact minimum is

    sum_i (c_i^+ + c_i^-) + ceil(s/2) (a+b).

Every uniform word needs at least one use of each H_i direction, and at least
ceil(s/2) injections of each sign. The same word attains all these bounds,
even with unequal positive prices. The lower bound permits arbitrary
repetitions and interleavings of every child label.

The first strict improvement is this chronological word:

```text
H_1 inverse; W += X; H_1; observe D_initial + L_1 X
H_2; W -= X; H_2 inverse; observe D_initial + (L_1+L_2) X
```

The workspace is W_initial+X at the first observation and W_initial at
return. Each output is already complete when observed. For unit prices,
the optimum is 2s+2 ceil(s/2), versus 4s for separate restored echoes. No
child call is removed. With N scalar additions per array injection, the
copying saving is 2 floor(s/2) N, before any changed routing costs.

[PROOF.md](PROOF.md) supplies the coefficient comparison, injection lower
bound, attaining word and the contrasting restored-workspace boundary.
If W must also be restored at every checkpoint, the exact price is instead
sum_i(c_i^++c_i^-)+s(a+b). Thus the saving requires an explicit observer and
workspace contract.

## Evidence and reproduction

The standard-library verifier is read-only. From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/completed-partial-echo/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/completed-partial-echo/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/completed-partial-echo
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/completed-partial-echo --check-source-history
```

Substitute another CPython 3.12 path elsewhere. The last command checks
publication bytes and declared source ancestry after committing. Expected
markers are PASS_COMPLETED_PARTIAL_ECHO, PASS_REGISTERED_RESEARCH_PACKAGE
and PASS_RESEARCH_COMMIT_BYTES.

The checks enumerate:

- 1,600 exact weighted schedule cases through 64 blocks, including unequal
  forward/inverse prices and rational injection prices. All 64 shared and
  separate-echo words check every formal checkpoint and final return.
- 448 literal matrix fixtures, 2,328 independent X/W/D input columns and
  6,294 complete output observations. These include all scalar map tuples
  over {-1,0,1} through four blocks, all pairs of binary-entry 2-by-2 maps
  interpreted in characteristic zero, and rectangular rational fixtures.
- Eight separately implemented shortest-word searches for one or two blocks
  with positive integer prices. They permit repeated labels, arbitrary
  interleavings and source shifts outside {0,1}; they do not assume the
  attaining schedule. The unit-price minima are four and six.
- Seventeen rejection controls for omitted directions, reversed injections,
  missing observations, unreturned workspace, post-observation corruption,
  dependence on repeated maps, a wrongly canonical workspace boundary, and
  invalid counts or inexact prices. Checks remain active with optimization.

Each run emits a generated receipt bound to the six package files and both
declared predecessor text inputs by SHA256. Counts are recomputed, and no
handwritten receipt is used. The all-length lower bound is the written proof;
the finite searches do not exhaust arbitrary word lengths or field elements.

## Scope, costs and provenance

Canonical base is 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8.
The selected record remains PR6030. TASK.json records the change from the
formal-interface card to this abstract boundary subproblem. The current
selected-baseline binding control passed; no selected scientific replay is
part of this result. SOURCES.json pins the catalogue, selected record and
two predecessor READMEs. The verifier authenticates the latter without
importing or replaying their implementations.

Ross Richardson's PR1287 supplies complete cyclic-equivariant batches and
ordinary dirty echoes. PR4860 supplies the canonical batch tariff and asks
for completed external-source observations. Here every H_i includes its
complete normalization, internal scratch restoration and literal inverse
cost. A block's internal cyclic frame cannot be ignored to claim this saving.
The new proof concerns the outer observation/injection schedule only.

This is a uniform-word theorem for independently arbitrary maps. Special
relations among fixed L_i can permit other words. Direct L_i X calls,
opened child bodies, scalar rescaling, output feedback, additional fields,
query records, adaptive observations or map-dependent words change the
alphabet and are outside scope. Observation execution and physical source
movement have separate costs. No actual native caller, precision/ownership
contract, tape program, compiler closure, complete signed invoice or outer
funding is supplied. The five inherited framework assumptions remain.
Independent human and formal proof-kernel review are unclaimed.

The bounded implementation accepts at most 64 blocks and 384 instructions.
Exact positive prices are at most 4096 with denominator at most 4096. Payload
fixtures use at most eight blocks and three coordinates per field. Shortest
paths use at most two labels, cost 18 and one million queue removals, with
explicit failure on exhaustion. No recursion, dynamic code, subprocess,
network access or write occurs in the verifier. Python dynamic allocations
are a Power of Ten rule-3 deviation; these enforced finite domains bound
live state. Warning-strict normal and optimized execution supplies interpreter
diagnostics. There is no fixed-memory implementation or performance claim.

## Open next questions

1. Does one actual cyclic-equivariant caller permit shifted borrowed workspace
   at a completed output observation? Pin one normalized block, its literal
   inverse and the observer's read set, then charge every injection and route.
   That missing physical boundary prevents applying the saving to a supplier.
2. What is the optimum if cyclic normalization and source injection may be
   interleaved inside the blocks? Begin with one literal child alphabet and
   full observer contract. This theorem treats H_i as indivisible and supplies
   no optimum for that changed alphabet.

## Overlap and credit

The source question is Nick Petalas's PR4860, published October 22, 2026.
Live open PRs, recent account targets, handoff claims, local reservations,
main README searches and merged formula/object searches were checked.
No recent account target cited PR4860. Sparse local notes, unpublished work
and arbitrary historical diffs remain coverage limits.

The binary partial-output-observation model of commdata2338's PR2020 and
PR5968 fixes drifting two-XOR children and hides a receiver row. This result
observes the whole completed receiver after every update and uses normalized
arbitrary signed linear blocks. Their adapter minima are not recomputed.
PR3417 serializes independent roots with unobserved outputs; its boundary
explicitly excludes intermediate observations. The Boolean multilinear
dirty-input query theorem in PR6393 has one final output and another alphabet;
it does not price these ordered completed observations.

Credit Ross Richardson / PR1287 for cyclic batching and complete dirty echoes;
Nick Petalas / PR4860 for the normalized observation question; Sagar Thakrar /
PR1227, mightyOil / PR1203, Adam Gall / PR1205, Hanson Sun / PR1488, Cinna Davis /
PR1391, and the retained restoration/echo lineage. Classical linearity and
signed cancellation are used without a global mathematical-priority claim.
Frozen predecessor files and their credit are unchanged. New work is
Apache-2.0.
