# A sharp scratch-dependent call bound for dirty echo trees

**Recursive-interface theorem and independent verification; no new κ.**
For an ordered dirty-echo tree with `n` factors and at most `s` borrowed arrays,
the complete call count satisfies `N >= 2^(s+1)n - 4^s`. An explicit family
attains equality for every `s>=2` and `3*2^(s-2) <= n <= 2^s`. Thus 50 factors
and six arbitrary dirty arrays have exact minimum **2,304 calls**, compared
with 2,752 for the pinned balanced binary schedule. This is an analytic proof
of that minimum, independent of a finite optimizer's output.

Every forward, inverse, source-restoration and dirty-restoration call is paid.
No clean array is required. The minimum concerns the stated static echo-tree
model, not arbitrary reversible programs.

The trees use androolloyd's [PR673](https://github.com/CrocSwap/integer-mult-bounds/pull/673)
echo at each node, allowing all positive contiguous partitions and mixed
fanouts while preserving factor order. Concurrent
[PR758](https://github.com/CrocSwap/integer-mult-bounds/pull/758) independently
supplies an optimizer for the same class, including unequal prices. This
package credits that work and adds the general scratch-dependent bound,
attaining family, a complete uniform-cost table and independent exact evidence.
It claims no priority for all-arity or unbalanced tree optimization.

| Factors | Dirty-array budget | PR673/PR689 reference | Independently checked minimum |
|---:|---:|---:|---:|
| 50 | 6 | 2,752, PR673 binary | 2,304 |
| 50 | 7 | 1,568, PR689 ternary | 1,472 |
| 50 | 8 | 1,568, PR689 ternary | 1,120 |

The reference column takes the minimum over every feasible fixed fanout in
PR673 and PR689's refined ternary word. All three minima also match the actual
pinned PR758 optimizer; the larger-budget rows are finite recurrence results,
not instances of the displayed closed formula. These are complete operation counts,
not runtime benchmarks. The six-array improvement is 448 calls. The seed-selected
50-factor instance is a generic ordered product, not a prime-power kernel
certificate at radix 51.

## Reproduce

From the repository root, with Python 3.11+ and its standard library:

```sh
python3 -I -O -B research/dirty-echo-space-budget/verify.py
```

Expected final line: `PASS_DIRTY_ECHO_SPACE_BUDGET: n=50, arrays=6, leaves=2752->2304`.
The verifier authenticates every vendored source, recomputes the complete
[EXPECTED.json](EXPECTED.json), and checks exact schedules, small exhaustive
tree enumeration, symbolic identities, rounded execution and negative controls.
All new checks remain active under `-O`. It needs neither Git nor network access.
`--write /absolute/new/result.json` writes the recomputed evidence to a new file.

[PROOF.md](PROOF.md) states the grammar, optimality recurrence, general lower
bound, equality construction and complete execution bill. The finite search
domain is all `1 <= n <= 64`, `0 <= s <= 8`; infeasible cells are explicit.
The written induction proves the general statements, rather than extrapolating
from this finite domain. [CLAIM.json](CLAIM.json) records the OS-random seed 50,
three candidate tasks, overlap inspection and stopping rule.

## Scope and source pins

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.

| Source | Exact head | Role |
|---|---|---|
| PR628, Chafik Boukhalfa | `0768f97d06c623b8211e651543c66135796b62bf` | Restored-input rounded leaves and inherited error assumptions |
| PR673, androolloyd | `156f259b99723468cfdd2b5d47d0ba894f09bea7` | Multiway echo identity, dirty restoration and fixed-fanout baseline |
| PR689, Dillon Amburgey | `0dedef12f05f9a06faf9d4e1c8b1462c0e3bff3a` | Refined balanced ternary baseline |
| PR758, Koroffstrogov | `a164f06263e438ead570b169e5b7103aa45bf228` | Concurrent all-arity optimizer, independently compared at unit prices |

The exact consumed files and SHA-256 digests are in [SOURCES.json](SOURCES.json).
Their original notices are retained under `vendor/`. No pending PR needs to
merge before this standalone package can run.

At the base, the selected conditional result is
`51110230636731/31250000000000000 = 0.001635527380375392`, from #626/#543.
The selected certificate and maintainer review hashes are recorded in SOURCES.json.
This package supplies no replacement bit or complex supplier, owner allocation,
common-label realization, tape layout or complete multiplication recurrence.
The selected construction's uniform, hosting, normalized-residual, precision,
tape and analytic assumptions remain. No new κ or full formal proof is claimed.

Optimality concerns **uniform leaf-call count in static ordered echo trees**.
It does not cover arbitrary reversible programs, interleaved scratch lifetimes,
factor reordering, clean checkpoints, unequal leaf costs, phase-read minima,
actual rounding error or execution time. Nonlinear rounded increments can
depend on the initial dirt even though restoration is exact.

The generic callback interface requires fixed external inputs and ordinary,
distinct mutable lists. Declare read-only arrays through `readonly=` so direct
identity aliases are rejected before execution. Overlapping views, hidden
mutable callback state and transactional rollback after a malformed leaf are
outside this interface. The rounded adapter checks the pinned leaf's own
stability, grid and precision conditions.

## Relationship to concurrent work

PR689 already proves the minimum among recursively balanced ternary placements;
Sagar Thakrar's PR730 then admits unbalanced mixed binary/ternary trees and
unequal prices. Ali Romman's PR744 independently audits a strict ternary class
over a larger finite domain. Koroffstrogov's PR758 covers all arities and includes
weighted phase costs. These arrived during this run and are credited explicitly.
The distinct theorem here is the scratch-dependent bound and attaining family;
the optimizer is an independent implementation of the shared all-arity model.
PR714's clean root checkpoint changes the initial storage contract. PR665's
spectral encoder concerns a different boundary mechanism.

The complete cost bill does not admit this array-level primitive into the
selected multiplication assembly. In particular, PR673's unfavorable bill for
its separate full-transform adapter is not invalidated by cheaper tree schedules.
The local result needs no claim that a stronger multiplication bound exists.

Prepared by **Alexander Schwartzman (@AlexS-scale)** with substantial **OpenAI
Codex assistance**, including separate mathematical and implementation checks.
No independent human peer review is claimed. See [NOTICE.md](NOTICE.md) for
predecessor attribution and license scope, and [VALIDATION.md](VALIDATION.md)
for the executed checks and their limits.
