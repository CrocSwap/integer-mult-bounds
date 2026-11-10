# Exact action tables reduce complete partial-Pauli replay time

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped implementation-equivalence proof with exact finite
conformance and local performance evidence. No new mathematical rank bound,
kappa or supplier admission is claimed.

An optional adapter reduces the median wall time of Ali Romman's complete
[PR5342 replay](https://github.com/CrocSwap/integer-mult-bounds/pull/5342)
by **5.20%**, from 0.254097 to 0.240896 seconds on the measured local host.
Six alternating fresh-process pairs have identical complete stdout and zero
failures. Both sides include Python startup, source authentication, compilation
and the entire original `main`. No persistent table or cached successful check
is used. The original verifier and its proof remain unchanged.

The complete command retains 10,113 completion fibers, 386 signed lifts,
848 literal Gaussian-rational matrix-column checks and all five original
controls. The adapter replaces only binary `act` evaluation. Its 307,191
calls use 3,466 tables with 32,551 entries, built within that invocation.
Action-value accumulation uses 29,085 XORs instead of 468,473, saving 439,388.
These counts exclude index arithmetic and dictionary work; the complete wall
measurement includes that overhead. Discovery stopped at this first improvement.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/partial-pauli-action-tables/replay.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/partial-pauli-action-tables/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/partial-pauli-action-tables/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/partial-pauli-action-tables
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/partial-pauli-action-tables --check-source-history
```

Replace the interpreter path on other hosts. `replay.py --original` runs the
unchanged algorithm through the same source-authentication wrapper. Both
replay modes print `PASS_PARTIAL_PAULI_GAUSSIAN_MINIMUM` and the complete
original counts. The registered normal and optimized conformance commands
print `PASS_PARTIAL_PAULI_ACTION_TABLES`, with a generated file-hash-bound
receipt on stdout. No receipt is hand-written or committed.

The verifier compares the complete ordered action transcripts and stdout,
then directly checks all 1,082,401 actions on every tuple of zero through four
four-bit columns. That domain includes zero and dependent columns. Twelve
named controls cover fresh-cache invalid requests, invocation isolation,
mutable-list keys and source corruption before execution. Assertions are
not used for admission. [PROOF.md](PROOF.md) gives the induction and scope.

To repeat timing, supply a new absolute output path outside the checkout:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/partial-pauli-action-tables/benchmark.py --output /absolute/scratch/measurement.json
```

Timing is not a CI passing threshold. The complete output SHA256 is
`32ba2068f05bf13e509776284f64834442447bd12dd8d2bed93e10e585c388bb`.

## Measurement record

CPython 3.12.15, macOS 27.0.1 arm64, 18 logical CPUs. Load averages before
were 2.421/2.742/2.257 and after 2.467/2.746/2.261. Other research processes
shared the machine; the measurements were serial and interleaved.
One warmup of each side preceded the twelve timed complete commands.

| Pair | Original seconds | Table seconds |
| --- | ---: | ---: |
| 1 | 0.255615333 | 0.240823125 |
| 2 | 0.275469167 | 0.243438208 |
| 3 | 0.253116833 | 0.244139875 |
| 4 | 0.255076584 | 0.240015208 |
| 5 | 0.249899458 | 0.240258291 |
| 6 | 0.250187750 | 0.240967959 |

The original range is 0.249899458..0.275469167 seconds; the table range is
0.240015208..0.244139875. Medians are 0.2540967085 and 0.2408955420 seconds.
This is a local matched-wrapper observation, not a host-independent guarantee.
An untimed original profile places 0.049 of 0.673 instrumented seconds in
`act`; literal rational word checks dominate at 0.464 seconds. Thus the
measured small end-to-end gain is consistent with the targeted work's share.
Profiler times are not the benchmark samples.

The measured implementation SHA256 is
`43aa41ca77f3339249844f700b133319c974e10ddf8a7db3d9e71375b2a7f2c0`.
The benchmark SHA256 is
`41913d342a171c3a22ec7e970363da722d9c11374b00d99d0c3ad1d37629d1ff`.
The source manifest SHA256 is
`a818b2f68ded7caa6fe2b188dcfa973f767cabc771a823188858b4c863bdf0e9`.

## Scope and credit

Ali Romman / PR5342 supplies the complete original replay, rank theorem,
fixture choices and five controls. JoyboyBrian / PR5051 supplies the signed
partial-map conventions and lift lineage; David Ganz / Dugongue / PR4841
supplies the native compiler context. Nick Petalas's partial-transvection
work remains a different tariff result. Classical XOR subset evaluation
retains its credit. The new contribution is this bounded adapter and its
complete-process implementation improvement, not an audit of those results.

The refined `replay-runtime` card, source bytes and selected-record provenance
are pinned at main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority 8.
The selected source-binding orientation passed. Cached overlap covered 572
open PRs and 6,639 Discussion records, but only 135 of 8,917 local notes.
Direct main and merged-PR searches supplemented that incomplete local view.
Arbitrary historical diffs and unpublished work remain unknown.
[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375443).

No new completion construction, physical contact, literal phase theorem,
rounded implementation, stock/tape bound, compiler closure or full multiplier
is supplied. All five selected framework assumptions remain. Independent
human and formal proof-kernel review are unclaimed. The selected cold replay,
Lean and Docker were outside scope and unrun.

## Open next questions

Does a named larger consumer benefit from the same table policy? First pin
that consumer and profile its complete action-call distribution. This matters
because the measured gain is limited to this complete fixture. Larger source
contracts, memory bounds and a complete physical bill are absent here.
The structured question is in [TASK.json](TASK.json).
