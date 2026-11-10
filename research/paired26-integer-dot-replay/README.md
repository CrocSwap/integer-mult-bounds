# Faster complete paired26 replay with integer dot products

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped implementation-equivalence proof, exact finite conformance
and local performance evidence. The complete primary command from
[Andrey Mas / an664's PR1624](https://github.com/CrocSwap/integer-mult-bounds/pull/1624)
takes **33.77% less median wall time locally**, from 0.628150 s to 0.415995 s.
Nine fresh-process pairs alternate their execution order. All eighteen commands
succeed with identical complete stdout and zero failures. Discovery stopped at
the first verified improvement. This is new implementation work. The predecessor's
decoder minimum and classification are cited results, not audit deliverables.

## Exact change and proof

The frozen source and certificate remain unchanged. `replay.py` authenticates
both SHA256 pins before executing the exact source bytes, then replaces only
its eight-coordinate rational `dot`. It runs the original default entry point,
including every mathematical check and rejection control. The accelerated
command accepts no arguments and cannot select the certificate-writing option.
It imports no predecessor bytecode.

For an integer/Fraction row v, let q(v) be the positive least common multiple
of its reduced denominators, and put
n(v)[i] = numerator(v[i]) q(v) / denominator(v[i]). Then

```text
sum_i v[i] w[i] = sum_i n(v)[i] n(w)[i] / (q(v) q(w)).
```

Python integer arithmetic is exact. One final Fraction reduction replaces the
repeated rational products and additions. Integer-only inputs return an integer,
matching the original type. Other widths/types use the original function,
including its shape-error behavior.

Row conversion is reused only for the identical container with all eight scalar
objects identical to its saved snapshot. Built-in integers and Fractions are
immutable. Mutating a row therefore causes conversion again, including a change
from an integer to an equal Fraction. Cached entries retain their owners, so
object IDs cannot be recycled while cached. At most 1,024 rows are cached;
capacity clearing changes only conversion work. No dot-product result is cached.
Every call still computes all eight products and their sum.

## Conformance evidence

The new verifier compares all **189,904 reached dot values and exact types**
with the original throughout the complete primary computation. Both complete
computed certificates agree and pass the original strict comparison against the
saved certificate. Its canonical computed-certificate SHA256 is
`f975a374d2d0ce6346ae4eaf053dfd049185fdf2dfe731f1b175de77e99e5fc1`.
The new route performs 12,369 conversions, 367,439 row-cache hits and twelve
capacity clears, with zero reached fallbacks. Both routes retain the fourteen
original rejection controls and two additional complex controls.

Additional conformance covers 65,536 rational vector pairs, ten fallback widths,
three fallback types, five in-place mutations and 2,049 capacity inputs. Eight
rejecting controls cover two bad shapes, both source pins, a wrong denominator,
wrong integer numerators, an oversized source and the writer option. Explicit
exceptions remain active under `-O`.
The unchanged default workload still includes all 511 functional records,
1,716 subsets, four decoder examples, full all-pairs identities, actual support
ranks and complete saved-certificate comparison. The separate predecessor
`audit.py` is unchanged and outside this optimization.

## Local timing evidence

CPython 3.12.15, macOS 27.0.1 arm64, eighteen logical CPUs. The load average
near the run was 1.76, 2.16, 2.11. Other applications remained active. Runs were
serial and alternating. Both commands use `-I -W error -B`, identical source and
certificate bytes and the same interpreter. Every timed region includes fresh
process startup and the complete default replay/certificate comparison. The new
route also includes authentication and cache initialization.

| Pair | Original seconds | Integer seconds |
|---:|---:|---:|
| 1 | 0.620465667 | 0.415328333 |
| 2 | 0.634360125 | 0.568668250 |
| 3 | 0.621159000 | 0.418008917 |
| 4 | 0.627842541 | 0.415584500 |
| 5 | 0.630763416 | 0.418947291 |
| 6 | 0.624511541 | 0.412711708 |
| 7 | 0.634765208 | 0.415995042 |
| 8 | 0.631476833 | 0.416269375 |
| 9 | 0.628149917 | 0.415403291 |

The ranges are 0.620465667 to 0.634765208 s and 0.412711708 to 0.568668250 s.
Every pair improves, including the slower second candidate run. Complete stdout
SHA256 is
`81d9b07342fe4de43ffa4acc83a5a33afedefd11939410d2d3d7be07edd8f10b`.
These are local observations, not a portable speed guarantee or CI timing claim.

An untimed discovery profile places 2.015 of 2.474 profiled seconds in `dot`,
with Fraction multiplication/addition dominating. The saving is below that
81.45% share. An untimed candidate profile leaves 0.817 of 1.357 profiled seconds
in the replacement dot, including 0.487 s in row conversion/snapshot checking.
Profiles are excluded from wall-time reporting. Final Fraction construction and
all unchanged certificate work remain. There is no cached certificate or early
acceptance.

## Reproduction

From the repository root, standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/paired26-integer-dot-replay/replay.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/paired26-integer-dot-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/paired26-integer-dot-replay/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/paired26-integer-dot-replay
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/paired26-integer-dot-replay --check-source-history
```

Any CPython 3.12 executable can replace the displayed path. Expected markers
are the unchanged `PASS_FIXED_PAIRED26_MINIMUM_62`, `PASS_PAIRED26_INTEGER_DOT`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
For timings, run `benchmark.py --pairs 9 --output /absolute/fresh/outside.json`
with that interpreter and flags. `verify.py --receipt /absolute/fresh/outside.json`
generates a hash-bound receipt. Default replay writes no artifacts.

## Sources, scope and limitations

Base main is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.
[TASK.json](TASK.json) refines replay-runtime to one complete default command.
[SOURCES.json](SOURCES.json) pins exact inputs and provenance. Both input files
are declared in [VERIFY.json](VERIFY.json) for CI invalidation; any byte change
fails the adapter's hash boundary before source execution.

Credit Andrey Mas / an664 / PR1624 for the original proof, program and
certificate; woklerx / PR1020 and PR1077 for the puncture, first pair and prior
decoder; Hanson Sun / bbMisk / PR1521 for the completion question;
themilkman216 / PR968 and DreamingOfClouds / PR717 for the geometry/billing model;
and the retained E8 lineage. Josie Elliston's PR1663 is a separate mathematical
audit, cited as prior work rather than replayed here. Common-denominator
arithmetic and caching are standard. The new result is the source-bound adapter,
equivalence contract and measured complete-command saving.

Earlier exact-arithmetic implementations include Ali Romman's
[PR5002](https://github.com/CrocSwap/integer-mult-bounds/pull/5002) and Nick
Petalas's [PR6272](https://github.com/CrocSwap/integer-mult-bounds/pull/6272)
and [PR6281](https://github.com/CrocSwap/integer-mult-bounds/pull/6281).
They already use denominator clearing on other complete commands. This adapter's
specific contract reuses scalar-row normalization across calls while detecting
in-place mutations, and preserves the complete scalar value and return type.
Those earlier product implementations are not imported or extended here.

No new decoder optimum, physical supplier, kappa, selected-frontier change,
complete multiplication theorem, independent human review or formal proof-kernel
acceptance is claimed. All five inherited framework assumptions remain.
No Lean, Docker, selected cold replay or separate predecessor audit was run.

Local registered normal and optimized conformance commands passed in 1.870 s
and 1.953 s respectively, below their sixty-second timeouts. The package
metadata/registered replay passed. Publication-byte/source-history and exported
standalone checks are recorded in the PR body after the publication commit.
Hosted CI is pending at initial publication.

Power of Ten inspection bounds numerical loops by eight coordinates, 1,024
cached rows, the fixed test corpus, at most fifteen timing pairs and a 30-second
subprocess timeout. Functions stay below sixty lines. Source reads are capped
at 1 MiB. Source pins, arithmetic equality, capacity and full fixture coverage
are checked with exceptions. Python integer/Fraction allocation is a managed
runtime deviation from fixed allocation. Live cached collections are bounded;
allocator internals and arbitrary external scalar bit lengths are not measured.
Executing authenticated source and replacing its `dot` callable are explicit
deviations from static dispatch/metaprogramming restrictions, constrained to
one SHA256-pinned module and one function. The inherited verifier stays frozen.
A native fixed-allocation implementation and separate static analyzer are not
supplied. Warning-strict normal/optimized execution and AST inspection are used.

## Open next questions

Can the same representation improve another named complete rational replay?
Profile that command first, then authenticate its sources and check all reached
widths, scalar types, mutation behavior and output. Different denominators and
mutation patterns require new evidence. Neither the percentage nor this
conformance certificate transfers automatically. This follow-on is unclaimed.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371170).
