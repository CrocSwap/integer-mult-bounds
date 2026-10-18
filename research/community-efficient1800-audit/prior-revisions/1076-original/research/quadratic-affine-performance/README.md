# Batched exact row engine for the quadratic-affine rank witness

Verification engineering (track 85–94), assignment seed 89. Base commit
`2921874911956718fcaaaf9396fe8267b3cfa9f0`. No new kappa; this is a tooling
improvement to one costly check. Prepared with help from opencode.

## What changed

`scripts/audit_quadratic_affine.py`, part of `make verify-certificates`,
re-derives twelve exact rank witnesses for real and Gaussian quadratic-phase
label families. Measured at the base commit it takes **89.1 s**, and the
timing survey recorded in `research/agent-07-verifeng-seed88` lists it as the
most expensive `make verify` check after the isolated test runner that work
sped up. Profiling attributed nearly all of it to `rank_witness` in
`scripts/experiments/quadratic_affine.py`, which built each witness row with
one `inner` call per (row, column) pair — 160,135,378 calls for the heavy
fixture alone (12,623 rows × 12,687 columns, diagonal short-circuited) — and
assembled each row as `sum(1<<j ...)`.

`rank_witness` now builds every row with a bit-sliced batched engine
(`_character_masks`, `_lane_flags`, `_gather_lanes`, `_orthogonality_rows`).
`inner` is unchanged and remains the reference the tests compare against.
Every mathematical output of the check — all twelve case records, row digests,
binary ranks, span controls, and the certificate — is unchanged; the only
byte difference in the regenerated
`certificates/quadratic-affine-vectors.json` is the recorded hash of the
edited source file itself (one line; see "Reproduce").

## Measured result (same host, same input, CPython 3.13.15, Windows)

| Run | Wall time |
|---|---:|
| `scripts/audit_quadratic_affine.py`, base commit, end to end | 89.1 s |
| `scripts/audit_quadratic_affine.py`, this change, end to end | 10.6 s (8.4×) |
| Row construction, all 12 fixtures, reference engine (`inner` per pair) | 67.0 s |
| Row construction, all 12 fixtures, batched engine | 3.56 s (18.8×) |
| Heavy `rank_witness`, this change (rows 3.5 s + unchanged GF(2) elimination) | 10.7 s |

The GF(2) elimination and digest inside `rank_witness` are unchanged code and
now dominate the check; they are the runtime floor of this method. Timings are
measurements, not acceptance thresholds.

## Method and exactness argument

`inner(u,v)` is a sum of independent per-position products: at each position
the packed value is `i^(lo+2*hi)`, and the product is `u_p * conj(v_p)`
(confirmed by `tests/test_quadratic_affine.py::test_packed_phase_inner_product_against_integer_components`).
So for a fixed row `i` the pair condition `inner(v_i,v_j)==(0,0)` is two
integer equations over positions, and each equation is a sum of per-position
coefficients in `{-1,0,1}` read off the four character classes
`i^0,i^1,i^2,i^3` of column `j` at position `p`. The engine:

1. Precomputes, for each position `p` and character `k`, one lane-packed
   column mask (`_character_masks`): lane `j` sits at bit `8j` and holds `2`
   iff column `j` has `i^k` at `p`.
2. Accumulates each row's positive and negative real and imaginary counts by
   adding the matching masks once per position — one big-integer add per
   position per accumulator instead of 12,687 `inner` calls per row.
3. Tests `pos == neg` lane-wise with an exact SWAR zero test
   (`_lane_flags`): `(x-ones) & ~x & 0x80...` flags bit `8k+7` iff lane `k`
   is zero. This is exact per lane because lanes hold even values in
   `[0,126]` (pre-doubled counts): an even lane `>= 2` never underflows on a
   borrow-in, so borrows propagate only through zero lanes, and zero lanes
   always wrap to a flagged value. Odd lanes would break this — the
   negative control `test_odd_lanes_break_the_swar_test` demonstrates the
   false positive.
4. Gathers the stride-8 flags into a dense column mask (`_gather_lanes`):
   after shifting the flags to bit `8k`, bit `k` travels down `7`, then down
   `7*2^i` at stage `i` whenever bit `i` of `k` is set, for total
   displacement `7*(k+1)`. Stage `i` selects bits by bit `i+3` of their
   current position, which equals bit `i` of their index (no carry: the
   already-moved part sits below position `i`). Distinct indices never
   collide: within one `2^i` block of indices the position difference equals
   the index difference, and across blocks `8*(k-k')` dominates the
   `7*(k mod 2^i)` term. The forced diagonal bit replaces `i==j or ...`
   exactly as before.

Every step is exact integer arithmetic; no sampling, no floating point, no
early exit.

## Verification and negative controls

From the repository root:

```sh
python3 -B research/quadratic-affine-performance/benchmark.py --out /tmp/qa-benchmark.json
```

Expected final line (timings vary):

```text
PASS identical rows (14662 rows, 0 mismatches); certificate equals committed; controls: odd-lane false positive demonstrated, dropped gather stage detected
```

The benchmark compares **every row of every fixture** (14,662 rows, including
all 12,623 rows of the heavy fixture) against the verbatim base-commit
reference in `reference.py`, recomputes the full certificate and requires it
to equal the committed `certificates/quadratic-affine-vectors.json`, requires
the base-commit certificate snapshot
(`evidence/base-certificate.json`) to differ from it only in
`scripts/experiments/quadratic_affine.py`, and runs two negative controls: an
odd-lane SWAR false positive must appear on a borrow chain, and a dropped
gather stage must be caught by the same row comparison. The recorded run is
`evidence/benchmark.json` (14,662 rows, 0 mismatches; row phase 67.0 s vs
3.5 s).

```sh
python3 -B -m unittest discover -s research/quadratic-affine-performance -p 'test_engine.py' -v
```

Expected: **11 tests pass**. They cover the gather against brute force on
random and adversarial flag patterns, the SWAR zero test against brute force
with long zero-run borrow chains, full row equality for fixtures 0–10,
subsampled row equality for the heavy fixture, randomized small-family
samples, full `rank_witness` dict equality for fixtures 0–10, one-bit row
corruption changing the digest, a dropped gather stage being detected, and
the unchanged rejection paths (duplicate labels, invalid indices, claimed
linear dependence) failing identically in both engines.

The repository test `tests/test_quadratic_affine.py` passes unchanged, and
`python3 -B scripts/verify_selected_result.py` still reports
`PASS selected record, exact kappa, ... 1661960547713947/1000000000000000000`.

## Reproduce the one-line certificate diff

```sh
python3 -B scripts/audit_quadratic_affine.py
git diff 2921874911956718fcaaaf9396fe8267b3cfa9f0 -- certificates/quadratic-affine-vectors.json
```

Expected: `PASS: twelve exact quadratic-affine core rejections, including
Gaussian rank-two labels.`, then a one-line diff replacing
`8f9252bd092eb14779997c6767e090377e91f4d57e6526e9840ae0dd7dcc8f9c` with the
new hash of `scripts/experiments/quadratic_affine.py`. Every other byte of the
certificate is identical to the base commit.

## Scope and inherited obligations

- Only `scripts/experiments/quadratic_affine.py` and the regenerated
  certificate change in the verification surface; no certificate content,
  patch, generator, proof supplement, pinned source or `upstream/` file
  changes. `inner`, `family`, `vector`, `block_projector` and the fixtures
  file are untouched, and `certificates/quadratic-affine-vectors.json` is not
  listed in `certificates/selected-result.json`.
- This speeds up a finite check; it changes no mathematical claim, bound, or
  kappa value, and it is not a formal proof of any theorem. The certificate's
  own scope statement (full orthogonality central matrices on exactly the
  declared families) is unchanged.
- The elimination step of `rank_witness` (unchanged) is now the runtime
  floor; further speedups would need a different rank algorithm and are out
  of scope here.
- The base-commit certificate snapshot in `evidence/base-certificate.json` is
  a copy of the file at the base commit, kept so the benchmark can check the
  "everything but one line" claim without invoking git.

## Overlap and distinction (final review 2026-10-13)

PR #752 ("Tooling: accelerate exact quadratic-affine witness replay",
Curtis Dransfield, seed 92, opened 2026-10-13T05:07Z) reached this hotspot
first, with a carry-safe packed-lane adapter in
`research/quadratic-affine-packed/` (73.4 s → 10.96 s on macOS arm64,
CPython 3.14). This submission was developed independently and adds three
things that #752 deliberately does not: (1) the speedup is wired into the
shipped check, so the default `make verify-certificates` run gets faster
instead of only an optional adapter; (2) a machine-checked guarantee that the
regenerated certificate differs from the base commit in exactly one line
(the edited source's recorded hash), anchored on a committed base-commit
certificate snapshot; (3) a second, independent implementation of the
packed-lane mechanism — pre-doubled even lanes, SWAR zero-lane detection,
collision-free staged stride-8 gather — corroborating #752's conclusion on
every row from a different angle, with red-green verified negative controls
(odd-lane borrow-chain false positive, dropped gather stage, one-bit row
corruption). Credit Curtis Dransfield for first publishing this acceleration.

## Attribution

Written with help from opencode. The witness families, fixtures, `inner`
formula and certificate are repository predecessors (see
`docs/research/quadratic-affine-vectors.md` and the audit's own source
notices); this package changes only how witness rows are computed and adds
evidence. Related concurrent verification-engineering work — PR #752
(packed-lane adapter for the same audit), the `audit_joint_frames` modular
rank screen (PR #976), T37 occupancy bitmaps (PR #1006), the
isolated-test-runner concurrency change
(`research/agent-07-verifeng-seed88`), and
`research/owner-footprint-bitsets` — targets different checks, different
functions, or (for #752) the same check through a separate adapter; this
result neither imports from nor depends on any of them. `inner` here is
the pair function of `scripts/experiments/quadratic_affine.py`, not a
contribution by any external author.
