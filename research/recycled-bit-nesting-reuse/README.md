# recycled-bit-nesting-reuse

**Tooling improvement. No new bound is claimed; kappa, certificate content and predicates are unchanged.**

`make verify-recycled-bit` (`python3 research/recycled-bit-integration/verify.py --all`) is the longest job in
`verify.yml`. On main run 38506758315, job "verify (3.11, recycled-bit)", it took 657 s. Of that, 619 s was the stage
`PASS exact rational nesting (4878 new pairs; all inherited pairs checked)`. That stage builds
`frames147.Exact` from the pinned PR97 h=23 witness, then checks `inside` for all 202,190 ledger moves and
`inside` plus `nondegenerate` for the 4,878 fresh moves. This package records why the stage is slow,
refutes the first reuse idea, and documents an output-identical replacement for its main exact kernel.

## What changed

`research/recycled-bit-integration/verify.py` now defines `null_exact_ff` and `install_null_kernel`. Before
`Exact` is built, `main()` replaces `linalg.null_exact` and `check_lifted.null_exact` with an integer, fraction-free
kernel. It also replaces `frames147.prim` with an integer gcd version. These replacements happen at runtime. The
frozen files `references/partial-gauge/pr97/{linalg,check_lifted}.py` and `research/bit-reuse-147/frames147.py`
are byte-unchanged. Input that is not integral, or whose rows are ragged, falls back to the original function.
`VERIFY_NULL=reference` restores the original Fraction kernel. `VERIFY_NULL=audit` runs both kernels on every call
and asserts that their outputs are equal. The fork pool from 6fd436d0d (PR218) is kept as it was. The only other
change is the `verify.py` entry in `research/recycled-bit-integration/certificate.json` `source_sha256`. Every other
certificate byte, the move multiset, the predicates and the five PASS lines are the same. The run also prints one
extra informational line, `null_exact kernel: fast`.

**Why the output is identical, not merely equivalent.** `null_exact_ff` repeats the steps of PR97 `null_exact`:
reduce each row by the earlier pivot rows, take its first nonzero entry as the pivot, then clear that column in
the earlier rows. By induction, every stored integer row is a nonzero rational multiple of the Fraction row at the
same step, with the pivot kept positive. So the pivot columns are the same, and the free columns come in the same
increasing order. For each free column f, the integer vector has `x_f = lcm` (the lcm of the pivot values `b[pc]`
of the rows with `b[f] != 0`) and `x_pc = -b[f] * lcm / b[pc]`. This is a positive multiple of the Fraction vector (`x_f = 1`, `x_pc = -b[f]/b[pc]`).
`linalg.primitive` maps a vector to the unique primitive integer multiple with the same sign, so dividing by the
gcd returns the same list of rows. `prim` on integer rows equals `x // gcd`. The equality was also measured: see
below.

## Measurements

All runs were on one shared host (4 CPUs, Python 3.14.4, `nice -n 10`), on the pinned base input. Timings in the
same row come from the same process, or from back-to-back runs, so they compare the same input. Other sessions
were running on the host, so the absolute times are noisy.
An earlier fast run, made while the host was more heavily loaded (a profiler and this package's check were
also running), took 284 s for the stage and 304 s in total. The `null_exact` fallback path (non-integer or ragged
input) was not counted separately. A fallback call runs the reference kernel itself, so it cannot cause a
mismatch.
A repeat of the committed `bench.py` on a less loaded host, stopped before the full-key loop, gave these figures.
The init kernel time went from 15.66 s to 1.90 s (8.2x). The sample basis + null time went from 2.92 s / 2.86 s to
0.95 s / 0.88 s (3.1-3.3x), and the maps were again identical.

| Measurement | Reference (Fraction `null_exact`) | Fast (fraction-free) | Equality |
| --- | --- | --- | --- |
| `null_exact` calls inside `Exact.__init__` (4,473 calls; mostly `late_frames` intersections) | 23.43 s kernel time | 2.88 s (8.1x) | all 4,473 identical |
| Deterministic sample: 400 ledger moves (`random.Random(1)`), 709 keys, 345 annihilators. Basis + null, rep 1 / rep 2 | 4.50 s / 3.88 s | 1.25 s / 1.11 s (3.5-3.6x) | basis and null maps identical |
| Same sample, `inside` dot products | 0.024 / 0.034 s | 0.024 / 0.025 s | — |
| Full-key audit (one process, both kernels on every call): basis of all 86,789 distinct ledger-move keys, then the annihilator of all 85,017 distinct targets | `null_exact`: 145,513 calls, 381.0 s; `prim`: 1,683,853 calls, 70.6 s | 48.7 s (7.8x); 3.6 s (19.6x) | all 145,513 + 1,683,853 identical (complete, not time-stopped) |
| Full `--all` replay, `VERIFY_JOBS=3`, back-to-back runs while the audit process was also running: nesting-stage wall / whole-run wall / user CPU | 410 s / 427.7 s / 825 s | 226 s / 243.5 s / 369 s (1.81x stage wall, 2.24x CPU; a second, more loaded fast run took 284 s, 1.44x). This is one before/after pair on a loaded host; the before-run is `VERIFY_NULL=reference` on the patched `verify.py`, which installs the original PR97 kernel | both runs printed the same five PASS lines with kappa=472154791/10^12, and both matched the committed certificate |

**Profile of the stage (before).** The cProfile figures are inflated by profiling overhead. Of `Exact.__init__`
(about 160 s unprofiled), `Frames.dims` takes the largest share: about 52% of the profile, almost all of it
mod-p `Echelon.reduce` in `rank_mod`. `late_frames` takes about 32% (unprofiled 25.5 s), mostly the Fraction
`null_exact` in `intersect_exact`. `cobases` and `spans` take the rest. In the per-move work, a cProfile of 600
basis and 300 null calls put about 72% of the time in `linalg.null_exact`, with Fraction arithmetic dominating.
The new kernel removes most of that time. It does not touch `dims`, which this package leaves unchanged
(see Open next questions).

**Negative result for the first hypothesis (basis reuse from `late_frames`).** The planned mechanism was to seed
`Exact`'s basis memo from the `exact_basis` cache that `check_lifted.late_frames` builds and then throws away.
That cache holds 2,230 keys. The ledger moves use 86,789 distinct keys (n 64,042; v 11,374; sigma 8,181;
out 1,771; c 1,396; ret 23; '0' 1; F 1), so the cache covers 2.6% of them. Key count is not cost, so the cost bound is this: every `exact_basis` result the cache could supply was computed
inside `late_frames`, whose total is about 25.5 s per process (unprofiled). Reuse therefore saves at most about
6% of the 410 s stage, so that mechanism was dropped. This is the one pivot recorded in TASK.json.

## Reproduce

```sh
python3 -B research/recycled-bit-nesting-reuse/verify.py          # ~40 s; last line PASS_RECYCLED_BIT_NULL_KERNEL
make verify-recycled-bit                                           # full replay; five PASS lines,
                                                                   # kappa=472154791/1000000000000
python3 -B research/recycled-bit-nesting-reuse/bench.py           # ~13 min: init audit, sample timing, full-key audit
VERIFY_NULL=audit python3 research/recycled-bit-integration/verify.py --all   # optional; both kernels on every call
```

`bench.py` produced the audit and timing rows of the table above; its final `summary` line holds the numbers. The
`VERIFY_NULL=audit` full replay was not run end to end in this session. The bounded check exercises its assertion
path, and `bench.py` covers the same distinct inputs.

`verify.py` in this package is the bounded check. It runs 3,012 differential matrices: edge cases (empty input,
k = 0/1, zero rows) and a deterministic random family (rank-deficient stacks, entries from {0,1} up to 2^80). It
runs 20,000 `prim` rows and checks the fallback on Fraction and ragged input. It also runs these negative controls,
which must fail:

* a sign-flipped kernel row, and a doubled (non-primitive) row, differ from the reference;
* `VERIFY_NULL=audit` raises `null_exact kernel mismatch` when the fast kernel is replaced by a sign-flipped one;
* with the fast kernel installed, `check_moves` reports a swapped strict inclusion (non-nested move), and
  `nondegenerate` rejects a degenerate frame (the span of 1^9 0^14, where 9*9 - 9^2 = 0);
* the certificate pins the new `verify.py` bytes. An edited `verify.py` changes `sources()`, so
  `assert read(dest) == cert` fails.

## Scope, inherited assumptions, unresolved obligations

* This is an engineering change to one replay. It makes no mathematical claim beyond "same outputs". The
  certificate is still the conditional composed bit-register witness of `recycled-bit-integration`. Its retained
  analytic, fixed-tape, uniform-recursion, prime and ordinary-leaf interfaces remain assumptions, as before.
* The identity argument above is a proof sketch in this README, not a formal proof. The empirical evidence is
  finite: the full-key audit recorded above, the init audit and the differential tests.
* Coverage: the call set audited was {all 4,473 init calls} and {basis of every distinct key, null of every
  distinct target}. The 8,991 keys of the 4,878 fresh moves are a subset of the ledger keys, and the fresh moves
  are a subset of the ledger moves. Bases depend only on their keys, so these are the distinct
  `null_exact` inputs of the `--all` path. Worker processes call the same functions on the same keys.
* CI wall time was not measured. The full runs used `VERIFY_JOBS=3` on a loaded host, so no CI speedup factor is
  claimed. Sibling PR #2361 (CI selection) would run this job less often. The speedup still matters for
  `make verify`, scheduled runs and relevant PRs.
* Historical receipts record the old pins as snapshots: 52 JSON files across
  `research/community-efficient{200,...,1000}-audit/` contain both the base `verify.py` sha (`a5508f42...`) and the
  base `certificate.json` sha (`4004ea4c...`). No live verifier, test, script or workflow re-hashes them
  (`research/pr946-pin-migration` scans its own pinned base commit). They are left unchanged as historical evidence.
* Trusted base: in the default (fast) mode, acceptance of the exact rational nesting check now depends on the new
  `null_exact_ff`, not on the reviewed PR97 kernel. Its equivalence rests on (a) the proof sketch above and
  (b) the recorded complete audit on the pinned input. The end-to-end replay does not detect an *incomplete*
  kernel by itself: a reviewer mutant that dropped the last null vector still passed, because `inside()` only
  becomes more permissive (a perturbed entry, by contrast, fails PR97 `exact_basis`). The package check
  (`research/recycled-bit-nesting-reuse/verify.py`) is the guard, and CI runs it only when this package changes.
  Maintainers may wish to run `VERIFY_NULL=audit` periodically or add a fail-closed completeness guard (Open next
  question 4).
* `sources()` of `recycled-bit-integration` does not pin `references/partial-gauge/pr97/linalg.py` or
  `check_lifted.py` (pre-existing). This package's SOURCES.json pins them at the base bytes; widening the
  certificate pins is left out of this focused change.
* Editing the live `recycled-bit-integration` verifier and its own certificate pin follows the precedent of
  6fd436d0d (the cherry-pick of PR218), and needs maintainer acceptance. Base pins of the two modified files:
  `verify.py` `a5508f42...` -> current pin in `certificate.json`; `certificate.json` base `4004ea4c...`.
* Python: all checks ran on Python 3.14.4. The registered Python 3.12 replay in VERIFY.json was not run locally
  (no 3.12 on the host); CI 3.11/3.13 were not run locally either.
* The fast-mode wrappers materialise their input before the type check. Audit mode runs the reference
  and fast functions sequentially and requires repeatable containers; every production call site in this
  path passes lists. One-shot iterators are outside the audit wrapper contract.

## Open next questions

1. *Question:* can `Frames.dims` (mod-p `Echelon` rank, now the largest remaining part of `Exact.__init__`) be
   made faster with identical ranks? *Why:* after this change it is the largest serial cost before the pool
   starts, and the forked workers do not share it. *First step:* replace the per-row list comprehension in
   `Echelon.reduce` with a packed-integer or batched elimination mod Q31, behind the same runtime-install and
   audit pattern. *Blocked by:* nothing; it needs its own equality audit on all 112,920 `_rank` calls.
2. *Question:* should the parent build the bases of shared source keys once before forking? *Why:* the 4 workers
   rebuild overlapping source-key bases, and copy-on-write sharing would remove that duplicate work. *First step:*
   measure the overlap of source keys across the current chunks. *Blocked by:* memory. Prebuilding all 86,789
   bases in the parent may use more than the CI runner can spare. Measure RSS first.
3. *Question:* do the other replays that use PR97 `null_exact` (`research/bit-reuse-147/verify.py`,
   `research/gauge-recycling/verify.py`, `check_lifted.py` itself) benefit from the same installer? *Why:* the
   kernel is shared. *First step:* profile `make verify-bit-reuse-147` and check its share of `null_exact`.
   *Blocked by:* each verifier pins its own sources, so each would need its own pin update and review.
4. *Question:* should `null_fast` fail closed on an incomplete or wrong kernel? *Why:* the end-to-end replay
   tolerates a dropped null vector (see Scope). *First step:* assert that each output row annihilates `A` and that
   `len(out) >= k - rank_mod(A, Q31)` (rank mod p is at most rank over Q, and the outputs are independent by their
   free-column structure), then measure the overhead. *Blocked by:* nothing; it changes `verify.py` and its pin again.

## Credit

* `research/recycled-bit-integration`: Douglas Colkitt, with OpenAI Codex assistance. It composes Thomas Marchand
  (#146), William Porter (#147), Rohan Gupta / gupt1156 (#148) and DaysSky (#150), per its `SOURCE.json`.
* PR97 snapshot (Zhihao Chen / jacklightChen; imported under `references/partial-gauge/pr97`): `check_lifted.py` /
  `linalg.py` frame/lifted checking sources by Swapnil Jain.
* Fork-pool parallelization of this stage: Joel Pulikkan / GamingPuzzled (PR218, cherry-picked as 6fd436d0d).
* Related verifier speedups with an exact method: CubeJerry (PR1461, annihilator containment for the h=10/12
  audits) and RichardHoekstra (PR239, `rational_span_frames` nondegeneracy).

Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5). Apache-2.0.
Base commit `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Source pins are in [SOURCES.json](SOURCES.json), and the
replay command and inputs are in [VERIFY.json](VERIFY.json).

## Maintainer replay

Python 3.12 differential checks passed. A serial audit compared both exact kernels
on every frame-stage call and checked all 4,878 fresh and 202,190 inherited moves,
clearing only deterministic memo tables between chunks. That process hit the
1 GiB memory guard after the complete nesting stage. A second process authenticated
the first receipt, log and all input hashes, reused that completed stage, and
freshly passed the complete scalar maps, corruption controls, exact pricing,
47 assembly constraints and full certificate equality. This is two-stage
source-bound verification, not a fresh cold end-to-end replay or a measured
speedup. See [the review evidence](../community-efficient1800-audit/README.md).
