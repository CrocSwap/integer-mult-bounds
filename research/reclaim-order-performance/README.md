# Filter eligible slots before ranked reclamation

**Verification engineering; no new kappa or physical word.**

The joint compiler sorts every retired slot before it checks whether the slot
can enter the current frame.
The change first selects the eligible slots, then sorts them with the original
key: descending current frame rank, followed by slot ID.

The production change is two lines in
`scripts/experiments/joint_dual_reclaim_compiler.py`. No new mode, cache,
data structure, dependency, or test-only interface is added. The original
compiler is retained byte for byte in `reference.py` for comparison.

## Exact equivalence

At the start of an `acquire` call, let `R` be the retired set, `P(s)` its frame
containment predicate, and `K(s)=(-rank(frame(s)),s)` its sort key. Filtering
`sort_K(R)` by `P` gives the same ordered list as `sort_K({s in R:P(s)})`.
Slot IDs make the sort keys unique.

Frame containment and key evaluation read the current frames; neither changes
them. The old loop skips each ineligible slot before it calls `ins`. During
the eligible scan, `ins` changes only its local elimination basis. The first
dependent row, its clearing expression, all emitted XORs, and all frame raises
are therefore identical. Once clearing starts, both implementations return
without another eligibility decision. If no row is usable, both allocate the
same new slot. Induction over `acquire` calls proves the complete compiler word
is unchanged, not only its endpoint matrix or rank histogram.

If `m` slots are retired and `e` are eligible, sorting changes from
`O(m log m)` to `O(e log e)`, with one scan of the retired set. The new code
can evaluate more containment predicates when the old loop found a reusable
slot early. No universal speedup is claimed. The benchmark measures the two
actual historical PR55 inputs at `h=23` and `h=25`.

## Reproduce the benchmark

Use Python 3.10+ and the standard library:

```sh
python3 -B research/reclaim-order-performance/benchmark.py --pairs 3 --out /tmp/reclaim-order-benchmark.json
```

Use a new output path. Expected final line:

```text
PASS_IDENTICAL_RECLAIM_WORDS_AND_RECEIPTS
```

Each pair uses fresh processes on identical source-pinned inputs. Pair order
alternates. Setup copies are outside the timing interval. Each timed command
does the complete scalar compilation, including all input and dirty columns
in both orientations. It also verifies the unchanged PR55 scalar graph.

After every timed command, the harness compares the decompressed serialized
word with the accepted historical word. It compares the complete compiler
receipt too. After each pair, it compares both outputs directly. Compression
bytes are not used as mathematical equality. Timing includes process startup,
source admission and output serialization; it excludes the independent CRT
profiler and the complete repository suite.

`BENCHMARK.json` records the final local measurements. `VALIDATION.json` records
the separate required checks and source hashes. There is no timing threshold
in the checks. The benchmark rejects disabled assertions, a nonpositive pair
count, changed pinned sources, and an output path that already exists. These
four rejection controls were tested. OS caches are not flushed, and the
development machine is not an isolated benchmarking host. These are verifier compilation timings, not
integer-multiplication runtimes or latest-frontier replay timings.

Three fresh alternating-order pairs on macOS arm64 / Python 3.14.7 gave:

| Axis | Reference median | Filtered median | Speedup |
|---|---:|---:|---:|
| h=23 | 72.876 s | 30.901 s | 2.36x |
| h=25 | 135.037 s | 50.220 s | 2.69x |

All 12 timed runs produced identical physical words and compiler receipts.
An earlier single-pair screen also passed; it is kept in the local sprint
archive and is not mixed into these medians.
After timing, receipt comparison was tightened to preserve JSON types.
All 12 timed receipt hashes match the retained receipt bytes, which also
match the accepted typed JSON. Timed commands and compiler sources are unchanged.

## Required mathematical checks

The existing `make joint-dual-verify` target rebuilds both words and compares
their literal payloads. It independently checks every dirty basis column,
frame transition, actual CRT profile, exact recurrence, 47 strict inequalities
and seven margins. The existing mutation tests cover missing XORs, illegal
frames, omitted transitions, uncharged scatter, aliasing and disabled
assertions. They remain unchanged.

All 18 groups required by `make verify` passed across the initial run and a
resumption. The initial run passed the first 14 groups, then stopped because
the historical positive-skip compiler did not find the installed Boost
headers. A retry refused its existing output directory. That generated
directory was preserved, and the four remaining groups passed with a fresh
output and `CPLUS_INCLUDE_PATH=/opt/homebrew/include`. The joint target
included all 16 existing controls. The failed attempts and successful
resumption are recorded in `VALIDATION.json`; no uninterrupted full-run pass
is claimed. No repository code was changed for the setup correction.

Only the compiler source pin and the derived historical certificate bindings
need regeneration. All numerical fields, selected words and profiles remain
the same. This package does not change the accepted #626/#543 frontier or
`upstream/`. It does not discharge the inherited compiler, tape, precision or
analytic assumptions.

## Sources and attribution

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
The accepted conditional kappa at that base remains
`51110230636731/31250000000000000`.

The measured compiler is the historical PR55/PR57/PR58 ranked-reclamation
lineage. The PR55 graph is pinned at
`03e991aa79f9df1a935726213bb6a8631cd0d823`; the repository retains its exact
dependency manifests. `SOURCES.json` binds those manifests, both input words,
the wrapper, and the before/after compiler sources.

Credit gupt1156 for the PR55 producer, eumemic for the PR57 compiler, and
Chafik Boukhalfa for ranked reclamation.
[PR154](https://github.com/CrocSwap/integer-mult-bounds/pull/154)
at `f571bcbd6e06618aeae0b8279da48060032dc74b` identified this sorting bottleneck
and explicitly left it unchanged. That report guided the scope; its code is
not a dependency. PR367/452/662/667/672 accelerate other exact checks.

OS-random seed 85 selected the verification-engineering track. `CLAIM.json`
records the three candidate tasks and local scope. No pinned sprint issue was
available. This change adds measured evidence for the previously identified
bottleneck and does not duplicate the existing frame or arithmetic kernels.

The final review covered 614 open PRs through PR795. It found
[PR779](https://github.com/CrocSwap/integer-mult-bounds/pull/779), Peter
Carpenter, at `daa9b0e773b53f36d5b4c3f1c7524600e5714deb`. Its separate adapter
maintains exact eligibility indexes and reports larger speedups. It also
credits Chafik Boukhalfa's earlier
[PR175](https://github.com/CrocSwap/integer-mult-bounds/pull/175), at
`f1081fabbfadaaaaf7292a40d428dbbb865ce920`, which maintains sorted rank
buckets. The review ledger records PR175's incorporation in a historical
source archive; the default compiler at this base still uses the full sort.

This change is a smaller option for that default compiler. It adds no
maintained index, update hook or adapter. Its contribution is the two-line
change, exact-output benchmark and integration checks. It is not a claim of
priority or best performance. PR175 and PR779 were not benchmarked on this
machine; no direct timing comparison with them is claimed. Their source
archives and adapters are unchanged.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Original source credits are retained. No independent human review is claimed.

## Follow-up review

The [2026-10-14 follow-up](FOLLOWUP-REVIEW.md) records the response to the
maintainer triage, the fresh checks and the remaining proof boundaries.
