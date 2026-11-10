# Faster literal header census by low-rank conjugation

This implementation was produced by Nick Petalas. Apache-2.0.

The complete `q=3,m=4` command of Ryanson Jonathan's
[PR4345](https://github.com/CrocSwap/integer-mult-bounds/pull/4345) takes
47.30% less local wall time with a direct low-rank request kernel.
Five alternating fresh-process pairs give median times of 9.341 seconds
and 4.923 seconds. The ranges are 9.005 to 10.028 seconds and 4.759 to
5.112 seconds. All ten commands finish the same 24,261,120-header census
with zero errors and byte-identical output. [BENCHMARK.json](BENCHMARK.json)
is the generated source-bound measurement record.

Claim type: scoped implementation-preservation proof with finite
conformance and local performance evidence. Existing counts and counting
theorems are cited context, not new results or audit deliverables.
No new kappa, supplier admission or selected-frontier change is claimed.

## What changes

The retained engine forms each request as `G R G^-1` with two dense matrix
products. The eight fixed requests have rank one or two, or are identity
minus a rank-one matrix. The new kernel forms the conjugate directly from
columns of G and rows of its already-computed inverse. It changes that
arithmetic from O(m^3) to O(m^2) per request.

The adapter authenticates the exact retained source before generating C.
It replaces the dense multiply helper with the new kernel and connects the
request index through three uniquely matched fixed substitutions. Every matrix
enumeration, inverse, guard-elimination statement, short-circuit evaluation,
counter and output statement retains its original source text.
Source changes reject rather than silently applying a stale adapter.
No predecessor file is edited.

## Preservation proof

Work over any field and let G be invertible. Write c_t=G e_t and
r_t=e_t^T G^-1. Then `G I G^-1=I` and
`G (u v^T) G^-1=(G u)(v^T G^-1)` give the entire request table:

| Request index | Original request | New conjugate |
| --- | --- | --- |
| t=0,1,2,3 when t<m | I-e_t e_t^T | I-c_t r_t |
| 4 | I-e_0(e_0+e_1)^T | I-c_0(r_0+r_1) |
| 5,6 | e_t e_t^T, t=0,1 | c_t r_t |
| 7 | e_0 e_0^T+e_1 e_1^T | c_0 r_0+c_1 r_1 |

These are identities for every entry, including odd characteristic and
extension fields. Thus every guard receives the identical matrix at every
invertible header. Its unchanged elimination and short-circuit logic return
the same Boolean result. Singular matrices are skipped by the unchanged
inverse routine on both sides. The complete enumerations and all output
counters therefore agree. No formula for a count, conjugacy quotient,
sampling reduction or cached scientific result is used for the speedup.

The identities are classical. The contribution is this specialized engine
kernel, its source-bound adapter, and the measured complete-command saving.

## Measurement and limiter

The host is macOS 27.0.1 arm64 with 18 logical CPUs and Apple clang 21.0.0.
Both binaries use `-O2 -std=c11 -Wall -Wextra -Werror -pedantic`.
The timed region includes a fresh process, the entire matrix scan, all
inversions, guards and final output. Compilation is excluded. Neither side
reuses state between processes. Other research processes were active;
alternation puts both sides under the same changing host load.

A separate three-second `/usr/bin/sample` run supplied 2,572 main-thread
samples. Exactly 1,474 landed at the dense conjugation call on retained
`headers.c:70`. Removing that work can explain the observed reduction.
The unchanged matrix scan, inverse and guard elimination limit the gain.
Profiling samples are excluded from the five timing pairs. The benchmark
covers the complete census command, not compilation or an entire research
package workflow, and is host-descriptive rather than a CI timing gate.

## Reproduction

From the repository root, use CPython 3.12 and a C11 `cc` compiler:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/low-rank-header-conjugation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/low-rank-header-conjugation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/low-rank-header-conjugation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/low-rank-header-conjugation --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/low-rank-header-conjugation/benchmark.py
```

Another CPython 3.12 installation can replace the absolute interpreter path.
Set `TMPDIR` to an external scratch directory to choose where generated C
and binaries live. Temporary builds are removed on success or failure.
The default verifier and benchmark write only to their temporary directories
and stdout. The benchmark needs at least five pairs; its timings are optional
and are not part of registered correctness acceptance.

The verifier compares all eleven complete historical commands over F2, F3,
F4 and F5, including GL5(F2), GL4(F3), GL3(F4) and GL3(F5).
A separate C harness compares every conjugated matrix entry in eight complete
smaller header domains, before any guard can hide a discrepancy. It checks
14,746,536 entries in 1,515,444 request matrices on 213,714 headers. Four actual
kernel mutations must fail: a missing odd-field sign, an incomplete one-way
dual, transposed row/column access and a missing rank-two summand. Altered
retained source bytes also reject. Checks use explicit exceptions and return
codes and remain active with optimized Python.

The direct marker is `PASS_LOW_RANK_HEADER_CONJUGATION`. Its generated
stdout receipt binds the package files by SHA256. The generic runner separately
authenticates declared source and historical metadata.

## Limits and engineering notes

The preservation proof applies to these eight requests wherever the retained
engine executes correctly. The executable scope is the eleven bounded
historical domains, not arbitrary sizes accepted by its legacy CLI. In
particular, this package does not repair its large-size counter-overflow or
input-parsing limitations. Those retained paths are unnecessary for the
measured command and finite conformance domains.

New C functions use fixed stack matrices, no recursion and bounded loops.
The comparison harness has at most 4^9 raw matrices per domain and matrices
of order at most four. The complete-command check also runs the unchanged
binary order-five and ternary order-four scans. Python subprocesses have
explicit timeouts; functions remain under 60 lines. Temporary directories
own all generated sources and binaries. Warning-strict C builds and Python
replays supply diagnostics. Managed Python allocation, the fixed source
generation adapter and the retained engine's global field tables and macro
are scoped Power of Ten deviations. Live work has fixed fixture and file-size
bounds; no general code-generation framework or shared writer is added.

No counting theorem, all-size native operation, physical compiler, selected
cold replay, Lean or Docker build was audited or run. The five inherited
framework assumptions retain their status. Independent human and formal
proof-kernel review are unclaimed.

## Open next questions

Can an actual caller supply low-rank request factors directly and use this
kernel without constructing dense requests? Start with one complete caller,
preserving its field representation, arbitrary inputs and every guard.
That caller and its benchmark remain missing. No further optimization was
attempted after this first measured improvement.

## Credit and source status

Credit Ryanson Jonathan / pinterbanget for PR4345's complete literal engine,
field implementation, request suite and original source notice. Credit Nick
Petalas's PR4259/4261/4273/4274/4275 for the cited header models and counting
laws, and retain the earlier BIT/header and normalizer lineage. None of those
mathematical results is newly audited here.

[SOURCES.json](SOURCES.json) pins canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, the current card and the exact C
input. The original claim was changed before implementation in the
[scope update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19360966).
Live open PRs, recent account work, handoffs, local reservations, merged
searches and main README terms were checked. Sparse notes, arbitrary diffs
and unpublished work remain coverage limits. Only this new package is changed.
