# Faster exact relative-tariff replay

This contribution is produced by Nick Petalas. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.

An exact integer Horner kernel reduces the complete frozen PR6378 primary
relative-tariff replay's median wall time by **29.42%**, from **49.18 ms to
34.71 ms**, on the recorded CPython 3.12.15/macOS arm64 host. The median uses
nine alternating fresh-process pairs. Original times range from 48.44 to
52.46 ms; integer times range from 34.04 to 36.01 ms. Every process succeeds.
[BENCHMARK.json](BENCHMARK.json) is the generated source-bound timing receipt.
This is a scoped exact-arithmetic preservation proof and measured verifier
improvement, with no new kappa.

## Result and evidence

[ToikY's PR6378](https://github.com/CrocSwap/integer-mult-bounds/pull/6378)
supplies the complete primary relative-tariff verifier, its theorem, frozen
profiles, independent oracle and rejection checks. This package changes its
private positive-exponential binding in an isolated opt-in replay. The
predecessor theorem is a cited premise, not an audit deliverable.

For x=a/b, the replacement evaluates the same degree-n Taylor polynomial
using integer updates `D=b*k*D; A=D+a*A`, in descending k. It constructs the
same geometric tail by one rational expression. [PROOF.md](PROOF.md) proves
both endpoints equal the original rational endpoints for every rational
0<=x<=1/4 and n>=1. No precision or series term is removed.

The complete caller reaches 72 exponential evaluations at degree 24. The
1728 per-term Fraction divisions, multiplications and additions become integer
arithmetic. All later outward rounding and the original CLI's full checks
remain. The complete 5805-byte result has unchanged SHA256
`abae56ad096f0361e9b3698ac37b12021bd0432ac52968e60e3b40551aeddb24`.

The deterministic verifier checks 1449 exact direct-power/factorial cases,
every reached exponential argument, complete result equality, both original
CLIs, fourteen negative controls and the benchmark's source binding. Its
finite evidence corroborates the written identity. The three inherited
controls still reject missing carrier fees, missing productive debits and
reversed endpoint signs.

## Measurement contract

Both timed arms use the same adapter, source authentication, interpreter
flags and fresh-process setup. The baseline arm retains the original kernel;
the integer arm binds the new kernel. The whole command, including its
original retained-result comparison, executes inside the timed region. No
persistent cache, network access or warm interpreter is used. Two checked
warmups precede the eighteen measured processes.

The separate cProfile run identifies the exponential kernel as the limiter:
its 72 calls consume 25.4 ms of a 43.6 ms instrumented complete source run.
These profiling times are excluded from the benchmark. Fraction gcd work
dominates that kernel. [PROFILE.json](PROFILE.json) retains the generated
profile summary and source hash. The measured end-to-end gain is smaller
than the kernel's removable share.

This is the predecessor's exact published arithmetic configuration, including
its existing logarithm cache, degree and work grids. Both arms use identical
settings. The host has eighteen logical CPUs and other work was present;
the recorded load averages are in the receipt. Alternation exposes both arms
to that load. The measured ranges do not overlap. The gain is for this command
and host, not a universal runtime guarantee or an aggregate speedup of every
PR6378 verification command.

## Reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/relative-tariff-integer-exp/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/relative-tariff-integer-exp/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/relative-tariff-integer-exp
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/relative-tariff-integer-exp --check-source-history
```

Expected markers are `PASS_RELATIVE_TARIFF_INTEGER_EXP`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Another CPython 3.12 path can replace the displayed local interpreter.
Normal verification writes nothing and needs no Git or predecessor checkout.

Run the measured complete command with `replay.py --arm original` or
`replay.py --arm integer`, under the same interpreter flags. To generate a
fresh timing receipt, use an unoccupied output path outside the checkout:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/relative-tariff-integer-exp/benchmark.py --pairs 9 --output /tmp/relative-tariff-timings.json
```

CI checks exact conformance and the committed timing receipt's bindings.
It does not certify the local speed percentage on a different host.

## Scope, provenance and constraints

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8. [TASK.json](TASK.json) retains the refined replay-runtime card
and [SOURCES.json](SOURCES.json) its historical provenance. The selected
source-binding positive control passes; no selected scientific replay ran.
[ORIGINS.json](ORIGINS.json) binds the retained pending predecessor's public
commit, paths, Git blob IDs and byte hashes. The local source subset is
338450 bytes. The sixteen files include the original NOTICE unchanged.
There is no runtime reliance on that pending commit's presence in Git history.

The new kernel accepts Fraction components of at most 4096 bits and degrees
1..64; the actual caller uses degree 24 and denominators of at most 171 bits.
No arbitrary public Python-number compatibility is claimed. Source changes
fail closed. The adapter modifies only its private namespace and restores
its temporary argument list even on failure. No original source, selected
frontier, shared tool or public verifier API changes.

The new functions are below sixty physical lines. The kernel has at most
64 iterations, the finite polynomial fixture has 41 denominator choices and
six degrees, and source-call traces are capped at eighty. Benchmarks accept
five to fifteen pairs and give each process thirty seconds. Source reads
are bounded and authenticated. Warning-strict normal/optimized replay and
syntax parsing supply the available Python diagnostics.

Power of Ten rule 3 deviation: Python and Fraction allocate managed objects.
The bounded kernel's raw and transient fraction arithmetic has a conservative 534000-bit bound; each
replay loads sixteen fixed retained files, whose total is 338450 bytes.
There is no new cache or queue; the fixed source logarithm cache has six rank keys. Rule 8/9 deviation: fixed local source
loading and one explicit function binding are necessary to run an unchanged
predecessor CLI. The adapter authenticates the source bytes before execution;
the callable targets are the original kernel and the new integer kernel.
Conformance covers both targets, while source mutation controls reject drift.
A shared or fixed-allocation integration needs its own resource contract.

No complete scientific audit, independent human/kernel acceptance, native
phase/endpoint, caller ownership/restoration, compiler, precision/tape,
analytic recovery or supplier admission follows. The five selected framework
assumptions remain. Lean, Docker, selected cold replay, predecessor profile
producer/oracle replays and physical integration are unrun and unclaimed.

## Open next questions

- Can the same exact integer kernel improve a different actual caller?
  Profile its complete command and bind its exact interval contract first.
  No additional caller or timing evidence is supplied here.
- Should a future primary relative-tariff verifier adopt this backend?
  Start with that exact new source head and preserve its full receipt and
  rejection checks. Shared adoption and changed-head applicability remain
  separate decisions.

Structured relevance, first steps and blockers are in [TASK.json](TASK.json).

## Credit and coordination

ToikY retains PR6378's scientific proof, complete verifier and independent
oracle. DreamingOfClouds retains PR6375's shared-carrier construction;
Ali Romman retains the PR6372/6353/6349/6348 P104/query lineage. Cinna Davis,
Jacob Alan Sussman, zxv, Cao Yifan and all authors in the retained NOTICE
keep their native, caller, interval and construction credit. Horner evaluation,
Taylor polynomials and rational arithmetic are classical. The new result is
this interval-preserving backend and its measured complete-command gain.

[Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19361553).
Live open/account PRs, handoff claims, local reservations, active Discussions,
merged object/formula searches and main README searches were checked. The
cached replay-runtime search has incomplete sparse local coverage; absence
of a match is not a novelty certificate. Unpublished work remains outside
that coverage. The first verified improvement is the stopping point.
