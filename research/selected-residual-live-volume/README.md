# Sharp payload storage for the selected BIT residual engine

PR2697 leaves residual and primitive temporaries as an asymptotic term in its
first-node storage ledger. For its unchanged completed-leaf implementation,
**the sharp live payload bound, including the borrowed input, is `3v + 3R`**.
Here `R` is one complete prefix fibre and `v = P R` is the packet containing
`P >= 1` fibres. This closes one storage component, not the total caller reserve.

The source is Jose Manuel/jmbarrancoml's [PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697)
at `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`.
[SNAPSHOTS.json](SNAPSHOTS.json) authenticates the 22 unchanged source exports.
The [Discussion2319 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18955184)
takes the residual-lifetime handoff after Nick Petalas's
[PR2708 route bound](https://github.com/CrocSwap/integer-mult-bounds/pull/2708).
ywz65's [PR2688 directory bound](https://github.com/CrocSwap/integer-mult-bounds/pull/2688)
is another complementary component. Neither result is reproduced or claimed anew.

## Contract and metric

Count nonblank Boolean payload cells on distinct tapes. Reading a cell does not
erase it. Keep borrowed input cells in the count until the routine returns.
Exclude LEFT markers, prefix directories and fields, numerical/controller/count
tapes, and allocated Python backing capacity. Thus this is not a count of all
physical tape cells or host memory.

Assume `q` is a fixed odd prime, `M = q^w`, `w >= 1`, `P >= 1`, and `R > 0`.
The input is a complete packet of equally sized fibres. Each fibre includes all
positive before/gap/suffix multiplicities and the full body domain supplied by
[Layout](vendor/layout.py). The trace is valid and completes successfully using
the pinned ADD, atom-swap and sign primitives and below-cutoff completed leaves.
Coefficient and observation callbacks allocate no payload tapes. Larger
recursive calls and arbitrary exception-path cleanup are outside this contract.

## Lifetime proof

### Primitive interiors

The primitives preserve their borrowed source of `R` cells and return a new
`R`-cell output. Their bucket reads do not erase bucket content.

* [ADD](vendor/vendor/stream.py) partitions the source into two buckets whose
  combined size is `R`. Both buckets survive until the full output is written.
  Its exact peak, including source, is `3R`.
* A single digit swap or complement has the same `3R` peak. In a
  [multi-digit atom swap](vendor/vendor/bitstream.py), a later digit pass also
  retains the original source while its current intermediate, buckets and next
  output coexist. Its exact peak is `4R`. A one-digit atom swap needs `3R`.
* A sign first complements every digit, then calls `translate_one` before
  clearing the complemented intermediate. During translation, the original
  source, complemented current, translation buckets and complete output all
  coexist. Its exact peak is `4R`, including when `w = 1`.

All these counts are independent of the payload values. Empty bucket partitions
can change which bucket owns a cell, but not the combined bucket length.

### Packet accumulation

In [packet_engine.run](vendor/packet_engine.py), the first primitive uses the
borrowed input itself as `current`. After a primitive completes, `current` is a
new full packet. The original borrowed packet remains unchanged. The previous
owned `current` is cleared only after the next complete packet has been written.

During the last fibre of a later primitive, the retained objects have sizes:

| Object | Payload cells |
| --- | ---: |
| Original borrowed source | `v` |
| Distinct current packet | `v` |
| Previously completed fibres in the next output | `(P - 1)R` |
| Local source, intermediate, buckets and primitive output | at most `4R` |

Their sum is `3v + 3R`. Earlier fibres have a smaller accumulated output.
After the primitive returns, copying its result to the packet output retains
only the local source and result, so that phase needs at most `3v + 2R`.
Cleanup and packet replacement cannot increase either bound.

More precisely, numbering payload primitives from zero, their exact peaks are:

| Primitive | First primitive | Any later primitive |
| --- | ---: | ---: |
| ADD or one-digit atom swap | `2v + 2R` | `3v + 2R` |
| Sign or multi-digit atom swap | `2v + 3R` | `3v + 3R` |

An empty trace returns the source alias and has peak `v`. Entry/return records
allocate no payload. Every nonempty [completed leaf](vendor/vendor/trace.py)
contains a sign after earlier primitives. Consequently any trace containing
such a leaf attains `3v + 3R`; the result is not just an upper bound.

This is a source-level lifetime proof for the stated contract. The finite checks
below corroborate the proof and instrument coverage; they do not replace it.

## Retained-role corollary

Let `K` distinct staged packets of size `v` remain live during a local call,
including any existing private packet. Count aliases by tape identity.
In [Driver.local](vendor/driver.py):

* MOVE passes one of those packets as the engine's borrowed input. The staged
  packets plus residual therefore need at most `(K + 2)v + 3R`.
* COPY first makes a distinct clone while all `K` staged packets remain live.
  That clone is the engine's borrowed input. The bound is `(K + 3)v + 3R`.
  The clone is cleared after return; the returned private packet remains until
  its matching ERASE.

For the source's 661 ordinary roles and at most one private role, both cases
are bounded by `664v + 3R`. This counts staged roles and the active residual
only. It does not include protected input, whole-family storage, directories,
routes, scatter output, peel/merge work, control tapes or markers. The corollary
is derived from source ownership and chronology; this checker does not execute
the full `Driver.local` schedule or certify its total reserve.

## Reproduction and evidence

From the repository root, with standard-library Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/selected-residual-live-volume --check-only
python3.12 scripts/research_package.py --package research/selected-residual-live-volume
python3.12 -B -O research/selected-residual-live-volume/verify.py
```

[verify.py](verify.py) authenticates sources before imports, instruments the
unchanged allocation/read/write paths, and checks a direct tape census against
the running meter. Instrumentation is restored in `finally`; it changes no
transform, cleanup order or allocation policy. Origin tags track every input
cell through actual copy operations. Expected address permutations use separate
ordinary modular arithmetic, and actual Boolean values are checked too.
Allocation-site classification is bound to the frozen source lines, not a
promise of compatibility with future versions.

[RESULT.json](RESULT.json) records 17 fixtures and 231 primitive events. The
fixtures include an empty alias case, ADD/swap/sign over moduli 3 and 9 with
one and two prefixes, nontrivial spectators and gaps, an embedded layout, and
complete good/fallback traces with 1 and 19 child returns. The final fixture
rejects a missing child return. Positive fixtures cover 10,701 input cells with
individual origin tracking; these are complete small declared domains, not
selected GL64 execution or a complete high-header census.

A sharp fixture has `P = 2`, `R = 972`, `v = 1944` and measured peak **8748**.
At that cut the census identifies both full packets, the partial next output,
local source, primitive intermediate, buckets and primitive output. Budgets
that omit the borrowed source or prematurely discard `current` give 6804;
omitting bucket/output overlap gives 7776. All are rejected by the actual census.
Source-byte mutation, incomplete manifests and borrowed-input mutation are also
rejected. Default replay compares the exact typed receipt and does not rewrite
it; `--write-result` refuses an existing result file.

The registered replay and the standalone checker serve different provenance
roles. The runner validates historical catalogue provenance at the pinned Git
base. Standalone replay authenticates the frozen manifest and scientific source
exports. The historical selected record is provenance only: the calculation
uses none of its fields, so an unrelated publication update does not invalidate
this frozen payload-lifetime certificate. Its original Git/hash pins remain in
SOURCES.json. Full Git
history is needed for the runner's historical provenance check, not for the
standalone scientific replay.

## Open next questions

Can the complete first-node caller fit a numerical reserve? Join this residual
component with the route and directory components at their actual overlapping
lifetimes, then include protected/family copies, count/controller tapes, markers
and disposal. A source-matched event ledger is the feasible first step, not
another independent maximum added blindly to all others. Larger recursive
returns remain a separate blocker. [TASK.json](TASK.json) records this handoff.

Stop this contribution at the component result. It does not justify a larger
construction campaign by itself. No new supplier, kappa, selected-frontier
change, full selected cold replay, full GL64 execution, formal-kernel proof or
independent human review is claimed. The finite coefficient fixtures use small
explicit projectors rather than selected 64-dimensional callbacks. Numerical
storage, markers and arbitrary error-path cleanup remain unverified.

## Credit

Jose Manuel/jmbarrancoml supplies the unchanged PR2697 engine and first-node
caller. [vendor/NOTICE.md](vendor/NOTICE.md) retains its full stream, selected-word,
normal-form, controller, hosting and audit lineage. Nick Petalas supplies the
complementary route result and explicit residual-lifetime handoff; ywz65 supplies
the directory and earlier primitive/setup audits.

New proof, checker and evidence prepared by starship-s with substantial Hermes
(`gpt-6-astra-900k`) and Codex (`gpt-6-astra`, max effort) assistance. Apache-2.0.

Maintainer integration retains the original scientific receipt and source pins.
Only the unused selected-record dependency, authenticated input count and
checker/manifest self-hashes change; the combined replay is checked with the
live selected record absent.
