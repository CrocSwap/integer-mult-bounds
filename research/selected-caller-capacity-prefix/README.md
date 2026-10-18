# Numerical capacity prefixes for the first-range BIT caller

This closes the **non-coefficient prefix** handoff of [PR2835](https://github.com/CrocSwap/integer-mult-bounds/pull/2835).
For unchanged PR2697 `Consumer.apply`, the credited PR2825 numerical envelope
also bounds each next allocation request, before successful completion is
assumed. With all live entry residents L and existing backing K counted,

```
C_R >= max(K_R,L_R+37672),   C_I >= max(K_I,L_I+41)
```

exclude a first numerical inventory failure under the stated source contracts.
This composes with PR2835's closed-coefficient prefix theorem; it does not
reprove those constants or establish selected catalogue membership.

Read [PROOF.md](PROOF.md) for the domain and source-site induction and
[INDEPENDENT.md](INDEPENDENT.md) for a separate AI audit. Two easily missed
residents remain explicit: setup peaks at nine indices while retaining eight;
the fallback child's zero half-width Word makes callback entry nineteen.
The numerical backing corollary now uses a caller prefix proof rather than
assuming a successful complete reference execution. Semantic validity,
termination, physical storage, recursive/outer reserve and supplier admission
remain separate obligations. No new kappa, formal-kernel or human proof.

## Evidence and reproduction

```
python3.12 -I -B verify.py
python3.12 -I -O -B test_verify.py
python3.12 -I -O -B independent.py
```

Run from this package or use the repository's registered `research_package.py`
launcher. [VALIDATION.md](VALIDATION.md) records the actual commands and limits.
All frozen inputs are authenticated by SHA256 and Git blob before execution.
The primary checker explicitly reuses PR2825's fixture/harness, adding pending
requests, real capacity guards and warm erased backing. Caller probes abstract
coefficient bodies and enormous payload movement. The complete small Boolean
primitives and the independent source audit have separately stated coverage.

## Source and credit

- Jose Manuel/jmbarrancoml PR2697 `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`:
  unchanged caller, binary arithmetic, layout, trace and stream sources.
- Nick Petalas PR2759/2770/2778/2781 and Arham Tahir PR2796: arithmetic and
  coefficient lifetime results; the latter's corrected extension interior is
  retained through PR2835.
- Ross Richardson PR2801/2810/2815/2821/2825: earlier caller-relative successful
  lifetime results; PR2831 `741e4c852b39fb05ee5343bd2b41cf3d9b8b4a6c`:
  numerical backing; PR2835 `a06f5339a1ee22017f6099cb1dfc1c93c212c424`:
  closed-coefficient capacity prefixes.
- Exact PR2825 head `b553e912bcddef550d9fae6033041ff683399ebe` is exported in
  `predecessor/` because its source loader and literal fixture are used by this
  checker. It is immutable predecessor evidence, not new work. SNAPSHOTS.json
  records every original path, head, Git blob and hash. Original notices remain.
- David Arias, ywz65, starship-s and retained source notices credit complementary
  recursive, payload and physical work; those categories are not proved here.

New work by Ross Richardson with substantial OpenAI Codex assistance, including
a separate math-storage-lifetimes AI audit. Apache-2.0; retain original notices.
Scientific base `23ef28cbeb7a3e2e985be22cab6832424bd98cf6`, priority revision5.
Task selection, overlap coverage and exact guidance pins are in TASK.json.

## Open next questions

Join the numerical backing theorem with payload, count, keys, directory,
program and serialized continuation storage at common chronological cuts, then
bind that ledger to the physical bank codec and granted reserve. Start with the
first-range caller's worst simultaneous phase; category-wise maxima alone are
insufficient. Physical movement, larger recursive grants and outer admission
remain blockers. The completed caller/coefficient prefix obligation need not
be repeated. Structured questions are in TASK.json.
