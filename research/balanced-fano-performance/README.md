# Faster exact balanced-Fano replay

This tooling change accelerates the existing exhaustive check of the historical
10-role, 14-gate balanced-Fano model. It preserves the negative result and its
complete ordered enumeration. It does not extend the search domain or claim a
new κ. The selected conditional result remains #626 with #543, exactly
`51110230636731/31250000000000000`, at the base commit below.

The production change is confined to
[`balanced_fano.py`](../../scripts/experiments/balanced_fano.py). Each local
binary operation now acts on a packed column representation, avoiding a fresh
10-by-10 transpose at every leaf. The matching table retains each first prefix
word; its matrix is reconstructed only when recovering a witness.

## Reproduce

From the repository root, using Python 3.11 or later and no third-party packages:

```sh
python3 -B research/balanced-fano-performance/benchmark.py --rounds 5
```

Expected: `PASS_IDENTICAL_COMPLETE_RESULTS`, with **279,936 prefixes**,
**258,156 distinct prefix keys**, **279,936 inverse suffixes**, no witness,
and these unchanged stream hashes:

```text
prefix b34379c5feeb67216fb7531294f13da5f67ce4a22f92b94ff8ea2b26f3aa21ec
suffix a19c1f14c463451e7bdd0900a2aeae701d98bcee790e9145d70e05c316555c38
```

Each sample runs in a fresh process. The two implementations run sequentially
in alternating order, fixed by assignment seed 91, on identical inputs. Every
sample must match **every result field** in the original certificate, including
counts, both hashes, witness and scope. The benchmark fails on a changed source
pin, unequal result, or subprocess failure. It has no noisy timing threshold.
The benchmark's RSS measurement supports macOS and Linux; the checker itself
uses portable Python integers. Use `--output /path/to/new-result.json` to retain
a new measurement without overwriting the shipped receipt.

[`RESULT.json`](RESULT.json) records all local samples, medians, environment and
exact implementation hashes. The measurement is for this fixed search, not the
complete research suite, selected supplier replay, or multiplication runtime.
OS caches were not flushed and no CPU affinity was imposed.

The contributor name was corrected after measurement. `RESULT.json` records
both the measured and updated hashes for the benchmark's attribution-only
module-docstring edit. Its executable AST was checked unchanged after removing
that docstring; all timing samples and mathematical results are retained.

On CPython 3.13.2 / macOS arm64, five sequential pairs give median search time
**5.969 → 2.051 seconds (2.91×)** and median peak process RSS
**162,381,824 → 113,180,672 bytes (30.3% lower)**. These are measured local
results, not guaranteed performance on other environments.

Additional checks:

```sh
python3 -B -m unittest discover -s tests -p 'test_balanced_fano_performance.py' -v
python3 -B -m unittest discover -s tests -p 'test_stronger_screens.py' -v
python3 -B -S scripts/audit_stronger_screens.py
make selected-record-check
```

The audit regenerates only `certificates/stronger-rank-screens.json`. Its sole
change is the SHA256 binding for the optimized source. A test restores that one
old binding and requires the entire serialized certificate to match its
original SHA256, so other certificate differences cannot pass unnoticed.

Local validation also passed `PYTHONDONTWRITEBYTECODE=1 make verify-tests`:
555 tests in 85 isolated modules and the existing patch-application checks.
The six added tests also pass under `python3 -B -O`. See
[`VALIDATION.json`](VALIDATION.json) for the precise coverage. Full `make verify`
and the selected supplier cold replay were not rerun for this historical-checker
change; unrelated artifacts were not regenerated. Remote CI is separate from
this local evidence.

## Why the enumeration is identical

For a binary matrix `M` with `W` rows, encode its columns as

```text
S = sum(M[i,j] * 2**(W*j+i) for i,j in range(W)).
U = sum(2**(W*j) for j in range(W)).
```

The masks `(S >> a) & U` and `(S >> b) & U` extract rows `a` and `b`
into the same column-start positions. XOR therefore adds those two rows over
F2 simultaneously in every column. Clearing only `U << a` and `U << b` and
placing the two selected linear combinations in those positions gives exactly
the old local row operation. The positions are disjoint because `a != b` and
both are in `[0,W)`. Python integers have arbitrary precision; this uses no
fixed-width truncation or approximate arithmetic.

The identity uses bits `i*(W+1)`. Induction on the unchanged depth-first GL2
choice order shows that each leaf has the same word and matrix as before.
Reading each W-bit block yields the old `columns(rows)` tuple. Thus prescribed
columns, sorted free columns, packed keys, first-prefix selection, stream
order and both hashes remain identical. There is no pruning, orbit reduction,
sampling, memoized result reuse, or changed stopping rule.

When keys match, replaying the retained first prefix word reconstructs its
original columns exactly. The suffix inversion and full recovered-permutation
checks are unchanged. Half-enumeration budgets and invalid-terminal/port
rejections run before enumeration as before.

The existing meet-in-the-middle argument still covers all `6**14 = 78,364,164,096`
complete local assignments via the two `6**7` streams. The absence of a match
excludes only this fixed balanced topology, with its three prescribed
terminals and free permutation of the other seven roles. It does not exclude
other Fano completions, larger gates, or different terminal obligations.

## Evidence and provenance

- Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
- The reference is the byte-for-byte original `balanced_fano.py`, last changed
  by `d55bcd62ceb8f322bcf311a5a66e94c3ac7724f0`; its SHA256 and shared dependencies
  are pinned in [`SOURCE.json`](SOURCE.json). No pending PR code is required.
- Tests compare every `(columns, word)` pair in both full historical streams,
  not only their final hashes. Independent dense matrix controls cover widths
  2, 3, 5, 9, 16, 33 and 65, including integer limb and byte boundaries.
- Seeded small-model comparisons cover complete result dictionaries, positive
  witnesses, first matching suffixes, empty words, repeated/reversed ports,
  fixed/free terminals and negative cases. Existing tests independently exhaust
  9,294 complete dense assignments.
- A missing-leaf mutation still reports no completion, but changes both counts
  and hashes and is rejected by the receipt comparison. Invalid inputs and an
  exhausted half budget retain the original exceptions; budget exhaustion is
  never reported as a negative mathematical result.

[`CLAIM.json`](CLAIM.json) records assignment seed 91, candidate selection and
overlap review. No pinned sprint coordination issue existed. Nearby PRs #367,
#452, #662, #667, #672, #707, #709 and #721 address other algebra, producer,
geometry, arithmetic or archive checks. This contribution replays the already
closed Fano model more efficiently; it is not a renewed search.

No selected construction, `upstream/`, theorem claim or inherited compiler,
hosting, precision, tape, or analytic assumption changes. These are exact
finite checks and an implementation equivalence argument, not a formal proof
of the full multiplication theorem. Attribution and AI disclosure are in
[`NOTICE.md`](NOTICE.md).
