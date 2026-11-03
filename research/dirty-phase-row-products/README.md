# Fewer integer products in the complete dirty-phase replay

This implementation was produced by Nick Petalas. It removes **255,310
scalar products** from the complete scientific replay of Philipp / mightyOil's
[PR1294](https://github.com/CrocSwap/integer-mult-bounds/pull/1294).
Five alternating fresh-process pairs show a **17.87% local median wall-time
reduction**, with identical complete scientific stdout and zero failures.
Claim type: scoped implementation-preservation proof, exact finite conformance
and local performance evidence. No new mathematical identity or kappa is claimed.

The opt-in adapter changes only `check_dense.multiply` in a private module.
The original symbolic checker, substitution loops, counterexamples, source
files, scientific receipts and six package tests remain intact. The
predecessor mathematics is the preserved workload, not new verification credit.

## Implementation and proof

For nonempty rectangular integer matrices A of size m by n and B of size n
by p, the original kernel evaluates every term in

    C[i,j] = sum_k A[i,k] B[k,j].

The new kernel allocates a zero m-by-p result, then visits each row i and
inner index k. If A[i,k] is nonzero, it adds A[i,k] times row k of B to
result row i. After processing inner indices less than k, the accumulator
is the corresponding partial sum. Terms with A[i,k]=0 contribute integer
zero. Induction on k proves equality of the complete matrices. Exact integer
addition permits the changed accumulation order. Both inputs remain unchanged
and each result row is fresh. The empty-output-row boundary is also preserved.

The scalar-product count changes from m*n*p to p times the number of nonzero
entries of A. This is classical row expansion. Custom scalar objects,
floating-point arithmetic and malformed matrices are outside the contract.

`adapter.py` authenticates all fourteen declared predecessor files by SHA256
and Git-blob hash before compiling any predecessor module. It executes those
authenticated source bytes directly, without predecessor bytecode-cache reads
or scientific-result caching. Changed dependencies reject before scientific
execution. Each invocation loads fresh private modules and compares both
complete generated receipts with their authenticated originals.

## Evidence

The complete dense consumer reaches **16,294** multiplication calls across
26 shapes with dimensions at most eleven. The checking adapter compares every
new result against the original kernel and checks both inputs after both
calls. The old kernel enumerates 562,574 scalar products; the new kernel
enumerates 307,264. Their difference is exactly 255,310. These counts include
all direct matrices, normal-form substitutions and four invariant-removal
counterexamples of that consumer.

Separate conformance covers all 6,561 pairs of two-by-two matrices with entries
in {-1,0,1}, 64 rectangular fixtures and the empty-output boundary, for **6,626**
cases. Sixteen source controls reject corruption of each of fourteen actual
inputs, a missing source and an unknown entry. Four arithmetic faults fail
explicit kernel fixtures; four additional well-shaped faulty kernels fail the
actual complete dense consumer. All six retained package tests run unchanged,
including relocation, source/receipt/order faults and exclusive output creation.
No assertion is needed for acceptance.

Complete scientific JSON before its trailing newline has SHA256
`7ab04e8ef093875f43f3d1240eb6bcf224c7d11f069eb7e40bfdc469e6cc9df1`.
The checking adapter also generates a digest of every reached input/output
triple and a shape histogram. Standalone verification prints a generated
receipt bound to every regular package file. No receipt is handwritten.

## Complete scientific caller timing

The timed boundary starts before launching a fresh CPython process and ends
after successful exit and captured output. Each process includes source
authentication, both module loads, the complete universal polynomial body,
the complete dense body, both expected-receipt comparisons and complete JSON
serialization. The six retained tests, new conformance tests, metadata checks,
shell startup and CI planning run separately. This does not claim a 17.87%
reduction of the whole generic registered-package job or a changed default
predecessor command.

| Pair | Original kernel, seconds | Row expansion, seconds |
| --- | ---: | ---: |
| 1 | 0.075181084 | 0.060592416 |
| 2 | 0.074843250 | 0.061917208 |
| 3 | 0.074595417 | 0.062196792 |
| 4 | 0.075584708 | 0.061222917 |
| 5 | 0.074929500 | 0.061536584 |
| Median | 0.074929500 | 0.061536584 |

The ranges are 0.074595417 to 0.075584708 seconds before and 0.060592416 to
0.062196792 seconds after. Every pair improves; the ranges are separated.
All ten outputs are byte-identical, with stdout SHA256
`292f0080f85366a0fc96108216970c365fb6c0fd52913133c962eff14902b2ea`,
including the final newline.

The machine runs macOS 27.0.1 arm64 and CPython 3.12.15, with eighteen logical
cores and entry load averages 2.10, 2.22 and 2.37. Other research processes were
present. Both sides use identical options and warm filesystem caches; module
state is fresh. An earlier five-pair pilot with the same kernel is excluded
from this final table. An untimed profile places 0.073 of 0.133 profiled seconds
in the original dense multiply. Python loops and integer arithmetic limit this
single-process caller. The measured reduction is smaller than that profiled
share; the profile itself is not a wall-time sample.

`benchmark.py` reproduces the five-pair procedure and emits every duration,
failure count, complete-output digest, source hashes, program hashes and
environment. Timing is opt-in, with no CI threshold.

## Reproduce

From the contribution checkout root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dirty-phase-row-products/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/dirty-phase-row-products/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dirty-phase-row-products
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dirty-phase-row-products --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dirty-phase-row-products/benchmark.py
```

Another CPython 3.12 path may replace the local path. Expected markers are
`PASS_DIRTY_PHASE_ROW_PRODUCTS`, `PASS_REGISTERED_RESEARCH_PACKAGE` and
`PASS_RESEARCH_COMMIT_BYTES`. Direct checks write only stdout. Retained file
fault tests use system temporary storage; set `TMPDIR` to a private external
directory when collecting evidence. Exported replay needs this package and
all fourteen declared inputs at their relative paths, but no Git or network.

## Scope, sources and credit

The base is canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8, selected conditional PR6030. The replay-runtime card is refined
to this measured integer kernel. Current main, open and recent-account PRs,
merged object/general-kernel searches, active Discussions and local reservations
were checked before the
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363383).
Sparse historical notes and unpublished work remain coverage limits.

Credit Philipp / mightyOil PR1294 for both complete scientific consumers,
identities, receipts, tests and original implementation; Charles Bethin PR1278
for the interval proof and phase formulas; Hanson Sun PR1244/1085, Chafik
Boukhalfa PR628/905, Gareth Davidson PR877 and their retained lineage. Their
source and credit lines are unchanged. The new contribution is this concrete
implementation, preservation proof, conformance and complete-caller measurement.
Distributivity and sparse multiplication are classical. New work is Apache-2.0.

Physical caller, rounded leaves, precision/tape, stock, compiler, supplier
admission and the complete multiplication theorem remain outside this result.
No selected cold replay, native suite, Lean or Docker run is needed or claimed.
The selected frontier and its five assumptions are unchanged. Independent
human and formal proof-kernel review are unclaimed.

## Open next questions

Should a maintained scientific replay adopt this integer kernel? Begin with
one named caller's profile, exact matrix contract and complete conformance.
This isolated package supplies no default adoption or selected-caller gain.
The structured first step and blocker are in `TASK.json`.

## Verifier constraints

New functions are below sixty lines. Fixed fixture domains bound every loop.
Caller dimensions are at most eleven; independent rectangular fixtures have
dimensions at most four. Fourteen source files are limited to one MiB each.
Five benchmark pairs have a thirty-second subprocess timeout. Registered
commands each have a 120-second outer bound. The unchanged retained six-test
suite invokes finite children without individual timeouts; the registered
runner's process-group deadline bounds that inherited path.

Power of Ten rule 3 deviation: CPython allocates managed integers and containers.
Fixed domains and source sizes bound live collections; no fixed-allocation
runtime is claimed. Rule 8/9 deviation: authenticated compilation, `runpy` for
the local adapter, private replacement and the fixed unittest loader use dynamic
execution/dispatch. Targets are three named predecessor modules, this adapter
and the explicitly enumerated fault kernels. No source text is rewritten.
Warning-strict ordinary/optimized checks and source compilation supply
diagnostics. No standalone Python linter is installed in this environment.
