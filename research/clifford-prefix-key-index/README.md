# Bounded linear-work Clifford prefix keys

This contribution was produced by Nick Petalas. Apache-2.0.

A bounded iterative index replaces whole-prefix recursion in Ali Romman's
[PR6479](https://github.com/CrocSwap/integer-mult-bounds/pull/6479) exact
Clifford state evaluator. Cold key preparation uses O(LG) work, where L is
the circuit length and G is the cost of one frozen gate. The retained cold
recursive method traverses L(L+1)/2 gate occurrences in complete-prefix keys
and copies L(L-1)/2 gate references into slices. The new method constructs
L+1 compact prefix nodes. [PROOF.md](PROOF.md) proves exact state preservation,
mutation invalidation and safe reuse after node eviction.

This is a scoped algorithmic proof with exact finite corroboration and a
negative runtime experiment. Neither tested variant demonstrates a speedup
of the complete current native component. There is no new kappa or supplier
admission. The selected frontier and five framework assumptions are unchanged.

## Construction and result

Each prefix has a fresh scalar ID interned by `(parent_ID, gate)`. A bounded
prepared-path cache avoids rebuilding paths on warm calls. State keys contain
only `(prefix_ID, basis_index)`. IDs never recycle while dependent paths or
states survive. The index bounds are 8,192 node entries, 512 prepared paths
and 512 cached states. Gates, sparse Gaussian arithmetic and normalization
retain their exact meanings; the explicit compiler fork changes its evaluator
import only. The construction supports one through nine address bits and
at most 512 gates per request.

The verifier preserves all 2,941 native recipes, 208 main adapters, 1,124
helper normalizers, signed Pauli checks, absolute phases and the existing
wrong-phase rejection. The complete recipe hash remains
`4649372e3e86cee6f427df503fc64c32a7e3ae5ebb2b6e7302cb86521656dba9`.
Those scientific objects and their inherited claims remain predecessor work.

New exact conformance checks compare 1,580 complete states with the retained
dense compiler. Controls exercise returned-list mutation, changed phases,
8,194 eviction-phase requests, 8,193 ancestor-eviction keys, coordinated ID
rollover, five invalid-boundary cases and source corruption. AST checks retain
every compiler body and sparse gate branch. The separate cold-key check
executes 257 requests at lengths zero through 256: 33,153 actual recursive
cache misses and compact node constructions, 2,829,056 complete-key gate
occurrences and 2,796,160 copied slice references. The last two counts use
the verified cold prefix lengths and the literal source key/slice structure.
At an explicit recursion limit of 256, a 512-gate cold request raises
RecursionError in the retained recursion and returns the exact identity state
with the iterative index. This controlled resource example does not describe
the default interpreter recursion limit.

## Complete-component timing outcome

Both experiments use five alternating baseline/candidate fresh-process pairs
on the identical complete native component. Every process succeeds, emits the
same full receipt and retains the wrong-phase rejection. Startup, source
binding, input decoding and receipt comparison are included in wall time.
The inner component duration is recorded separately.

| Variant | Baseline median and range, seconds | Candidate median and range, seconds |
| --- | --- | --- |
| Rebuild each path | 7.251, 7.047–7.286 | 7.337, 7.112–7.771 |
| Cache prepared paths | 7.153, 7.003–7.748 | 7.592, 7.284–8.062 |

The ranges overlap. These samples demonstrate no runtime improvement and do
not prove a universal slowdown. [BENCHMARK.json](BENCHMARK.json) retains every
second-experiment measurement and executed Python-source hash.
[The first experiment](history/NO-PATH-CACHE.json) and its
[exact candidate source](history/no_path_cache.py.txt) remain available.
No unfavorable sample was removed. Optimization stopped after these two
variants. The second variant is retained for its key-work and stack bounds,
not proposed as a faster current-native replacement.

The separate [diagnostic profile](PROFILE.json) identifies state evaluation,
scalar Clifford algebra, independent tableau work and gate-table construction.
Profiling overhead prevents treating its durations as unprofiled cost shares.
The host had 18 cores, load averages 4.25/2.76/2.55, and other applications and
contribution processes running. Alternation limits drift but cannot eliminate
that noise. Standard prefix interning, LRU caches and complexity arguments are
classical; no literature-priority claim is made.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/clifford-prefix-key-index
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/clifford-prefix-key-index/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/clifford-prefix-key-index/check_depth.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/clifford-prefix-key-index --check-source-history
```

Substitute another CPython 3.12 path elsewhere. Registered replay runs both
checkers in normal and optimized modes. Expected markers are
`PASS_CLIFFORD_PREFIX_KEY_INDEX`, `PASS_COMPACT_PREFIX_DEPTH`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
Checks are read-only in the checkout and use temporary external bytecode
namespaces. Set `IMB_SCRATCH_ROOT` to an existing external directory to place
their temporary files there. Direct verification prints generated receipts
bound to the new source and proof hashes; it does not rewrite receipts.

To reproduce the measurement rather than replace its historical evidence:

```sh
python3.12 -I -W error -B research/clifford-prefix-key-index/benchmark.py /absolute/new-output.json
```

The output must be new and outside the package. Timings vary by host and are
not a CI pass criterion. This times the complete native component, not the
complete caller, compiler, multiplier or other historical native suites.

## Sources, credit and limits

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363376)
predicted a possible runtime improvement. The
[scope update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19363578)
records the narrower delivered result:
a bounded linear key-work construction and a negative complete-runtime test.
Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision
8, selected PR6030. Selected source-binding orientation passed; it was not a
scientific replay. Full entry overlap covered 431 open PRs and 6,406 Discussion
records with complete pagination, plus 8,917 main note records. Unsearched
historical diffs and unpublished work remain limits.

[ORIGINS.json](ORIGINS.json) records the nine exact runtime/source files
retained from PR6479 head `ca129c9e0b12e2315765aab4c39c42220f68016d`, acquired
through the GitHub contents API. Replay authenticates these local bytes and
needs no pending Git object or network. Their source credit is unchanged.
The package's Git history pins cover catalogue/selected-record provenance;
they do not independently establish the external PR head's ancestry or
scientific acceptance. These are functional replay inputs, not a provenance-only
copy of the predecessor package.

Credit Ali Romman for sparse prefix-state reuse and independent Gray-order
native tables; Charles Bethin for the retained exact compiler and gate tables;
Wentao Li for their production use; Cinna Davis, David Arias, Gareth Davidson,
Erwan L., Rohan Arun and the native/P104 lineage retained in the unchanged
[vendor notice](vendor/NOTICE). The new step is compact iterative key
preparation with bounded path retention, its proof, controls and recorded
negative measurement. No predecessor theorem is audited or claimed anew.

The code assumes valid retained gate constructors and serial calls. Extra
index/path memory is real; no lower total-memory or runtime claim is made.
Python-managed allocation, source loading and dispatch constraints are stated
in PROOF.md. Native physical realization, full compiler/caller, ownership,
precision/tape, stock and analytic recovery remain unrun. Selected cold replay,
Lean, Docker, independent human review and formal proof-kernel review are
unclaimed. This does not close any selected framework assumption.

## Open next questions

- Identify a measured prefix-length and miss-rate regime where compact keys
  improve the complete component after preparation and extra storage are
  charged. Another index variation is not justified by the current timings.
- Profile a larger unchanged native cost and propose a different algorithm
  that retains the full receipt. No further optimization or target is reserved
  by this package.
