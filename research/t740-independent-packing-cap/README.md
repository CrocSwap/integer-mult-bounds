# Independent all-pattern audit of the T740 packing cap

This independently corroborates **the fixed-inventory cap**, rather than another
evaluation of the complete-profile root, in Nick Petalas's [PR3054][3054]. All
2,551 legal bin patterns are checked: 12 are identically tight and 2,539 have
strictly positive reduced cost throughout the published six-skip root bracket.
The smallest certified lower bound is greater than `0.0040828` in unnormalized
`H_r(b) = r(73/r)^b` units. The tight patterns independently yield

```text
20 * N_[9,9,9,9,9]@48 = 1341 * T.
```

Thus attaining this cap requires `20 | T`; the first eligible multiple of 74 is
740. The displayed primal basis is integral at T=20 and at T=740. This is an
integrality statement for the additive-bin relaxation; chronological feasibility
still needs its own construction and checks.

The original cap, tight patterns and divisibility result belong to Petalas's
PR3024/3030 lineage. This package supplies a separate executable audit, including
a different exact enclosure method and independently derived integer witness.
It claims no new cap, construction, kappa, supplier admission or selected result.

## Task, sources and prior coverage

Base: canonical main `18aacb215fc3717b06be8ceb9fca62aeca0d3e99`, priority revision
6. The `independent-moment` card was refined to the cap implication in the
[independent-check handoff][handoff]. The exact PR3054 head is
`4773c3ea67b471415870e38411fae313ec44a675`. [SOURCES.json](SOURCES.json) pins the
inputs and the historical catalogue/selected-record provenance; [TASK.json](TASK.json)
records scope, overlap coverage and the stop rule.

PR3054's author checker already recertifies this cap, using retained PR3024
elimination and the source logarithm/Taylor engine. Ross Richardson's
[independent report][prior] reconstructs all helper roles and the complete paid
profile, verifies the packing comparison and describes a partial native replay.
That report does not state an independent all-pattern cap or annihilator check;
its evidence is explicitly local-only. We do not count another root bracket as
new coverage. Here the root bracket is a prerequisite for checking every
reduced-cost sign at the actual cap.

The live overlap snapshot at `2026-10-17T00:40:06Z` covered all 253 open PRs and
1,858 discussion records, with complete pagination and no remote warnings.
Closed work is represented by the ledger and relevant retained notes, rather
than an exhaustive closed-PR search. Local content coverage is limited by the
sparse checkout; the archived research-directory names were also inspected.
These searches are leads, not a proof that no other audit exists. At submission,
canonical main was fetched again and remained the base above. The refreshed
`00:47:12Z` search covered 253 open PRs and 1,861 discussion records, with complete
pagination and no remote warnings; no additional all-pattern audit was identified.

## What is checked

The relaxation has capacities `(8,16,32,48)` with respectively
`(672,448,448,448)` bins per replica. Each of the nine calls supplies width
inventory `{4:26,5:2,6:16,7:52,8:99,9:213}`. The objective charges `H_idle(b)` for
every nonempty remainder, with zero cost for remainder zero. All 6,660 calls'
local children remain in the complete moment.

The verifier reads the original primal template at
`research/rank7-joint-endframes/certificates/RELAX-CAP.json`. Its historical local
profile and old root are deliberately **not** used as the six-skip inputs.
Both actual provider inventories/profiles come from PR3054's vendored PR3042
`PROVIDERS.json`; the new bracket comes from PR3054's `FINITE.json`. Their
live bytes and Git objects are pinned. No input or frozen predecessor is edited.

1. A depth-first capacity enumeration generates every nonnegative width-count
   vector, including empty bins. The 2,551 patterns are distinct.
2. Exact Fraction elimination checks that the ten primal patterns meet all four
   bin constraints and six inventory constraints. It solves `B^T y = c_B`
   symbolically in the `H_1,H_3,H_5,H_48` coordinates. Primal and dual objectives
   agree as symbolic expressions.
3. Each pattern's residual `H_idle - column^T y` is derived independently.
   Twelve expressions vanish identically. The other 2,539 receive strictly
   positive rational lower bounds over the whole root bracket. Signed terms
   use the appropriate lower or upper endpoint, including idle ranks absent
   from the complete candidate profile.
4. The primal idle histogram and both providers' local children reconstruct
   PR3054's exact full profile and rank mass `48,165,120`. The independent
   arithmetic checks `M(lower)<1<M(upper)` for the full normalized moment
   `M(b) = sum(count_r H_r(b)) / (73 * 896 * 740)`.
5. Fraction elimination finds the one-dimensional annihilator of every tight
   column except `(48,[9,9,9,9,9])`. Primitive integer normalization produces
   `(-3,-6,-12,0,0,0,1,2,3,4)`, in capacity-then-width coordinate order.
   Its dot product with that column is 20, with every other tight column zero,
   and with the per-replica constraint vector 1341. Coprimality proves `20 | T`.

Weak duality now gives optimality: every feasible nonnegative pattern mixture
has objective at least the dual objective, and the displayed primal attains
it. At the unique root inside the checked interval, every other feasible
packing's complete moment is at least one. Since each charged child has rank
below 73, its moment increases with `b`; the same fixed-inventory model cannot
support a larger endpoint. An optimal integer packing must use only the tight
patterns, so the residue identity applies to it.

## Independent enclosure method

The checker imports only Python's standard library. It executes no predecessor
Python and uses no floating-point operations for acceptance.

For `0 <= x <= 8`, put `N=2^128`. Elementary logarithm inequalities give

```text
(1+x/N)^N <= exp(x) <= (1-x/N)^(-N).
```

Round the two bases outward to denominator `2^320`, then square 128 times,
rounding outward after each integer multiplication. Nonnegative squaring
preserves containment. This supplies rigorous bounds without a Taylor series
or an assumed truncation tolerance. Inverting those bounds with 112 rational
bisections on `[0,8]` encloses each required `log(73/r)`; `exp(8)>73` establishes
the initial bracket. Unresolved comparisons fail closed. Multiplication by the
nonnegative root endpoints and another Euler enclosure bound every `H_r`.

The tests use a separately implemented rational Taylor enclosure as an oracle
for representative exponential and inverse-log bounds. It runs only in tests.

## Reproduce

Python 3.12 and the standard library suffice. A direct replay takes about one
second on the development host; the registered command runs both the checker
and its 20 tests. It writes no scientific input. [VALIDATION.json](VALIDATION.json)
records the actual commands and Python 3.12/3.14 executions, including optimized
mode; both versions reproduce the exact result.

```sh
python3.12 -B scripts/research_package.py --package research/t740-independent-packing-cap
python3 -O -B research/t740-independent-packing-cap/test_verify.py
```

[RESULT.json](RESULT.json) contains the exact bounds, all tight count vectors
(in width order 4,5,6,7,8,9), and the derived integer witness. Controls reject
infeasible/duplicate/negative primal entries, missing patterns, stale roots,
provider/inventory mismatches, omitted idle charges, mass-preserving profile
corruption and changed source bytes. A corrupted rank-44 cost specifically
passes the candidate-root calculation but fails a reduced-cost inequality:
this checks coverage beyond the candidate histogram itself.

## Scope

This checks a fixed chronology-free inventory, its additive-bin objective,
optimality at the six-skip cap and the tight-pattern integrality condition.
Actual word action, owner windows, literal fill, physical stock/prefixes,
native execution, full admission and outer transfer are outside this audit.
The selected-result cold replay and formal proof kernels were not run.

## Open next questions

**Open next question:** finish the source-bound full native/admission replay
requested in [the handoff][handoff]. It matters because an optimal relaxation
does not establish an executed supplier. Start with PR3054's pinned exports
and full recipe and compare the actual outputs through the final strict audit.
The prior independent run timed out there; adequate runtime, disk and the
inherited physical/all-size/compiler/caller/analytic obligations remain blockers.
No further search within this attained packing cap is motivated by this audit.

## Credit

Arham Tahir, with substantial OpenAI Codex assistance in implementation,
mathematical exposition, tests and publication. Apache-2.0. No independent
human or proof-kernel review is claimed.

Credit Nick Petalas for PR3024/3030's primal/dual cap, divisibility argument and
PR3054 composition; dcharb78 for PR3042's six skips; Jeremy Kothe for PR3015's
edit tooling/R1; Marius-Paul Dumitrean for PR2979's joint words and original
allocation; Ross Richardson for the prior independent report that identified
already-covered work and the outstanding admission gate. Retain the credited
Mason Hale, Jeremy Diviney, Yiyang Lu, Tekalign, Dugongue, icekylinx,
themilkman216 and native/geometry/owner lineage. Inputs stay in their original
credited packages; no predecessor implementation is copied here.

[3054]: https://github.com/CrocSwap/integer-mult-bounds/pull/3054
[handoff]: https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18982879
[prior]: https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18983422
