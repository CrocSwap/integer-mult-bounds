# Faster cold R420 row reduction

**Tooling improvement; no new κ.** This opt-in adapter runs eumemic's unchanged
PR543 `xcheck.py` with Aman's existing PR367 primitive-integer elimination in
place of its Fraction-heavy RREF. It preserves the exact rational basis **and
pivot list**, so the original integer-nullspace construction also stays unchanged.
No geometry cache is used. Only `research/r420-rref-performance/` is added.

The selected conditional result at base
`66849e1475c930fd7732b1a0067ffee7e1e95f60` is
`51110230636731/31250000000000000 = 0.001635527380375392`, PR626 with PR543.
The selected record was followed to its assembly and maintainer review; larger
pending PR titles are not treated as accepted results.

## Reproduce

Python 3.11+, standard library only, from the repository root:

```sh
python3 -I -B research/r420-rref-performance/verify.py
python3 -I -B research/r420-rref-performance/benchmark.py --pairs 7 --out /tmp/r420-rref-new.json
```

Use a fresh benchmark output path. Expected first result:
`PASS_R420_RREF_PERFORMANCE frames=672 matrices=1090 original_controls=9+1 kernel_mutations=4`.
The benchmark prints `PASS_R420_RREF_BENCHMARK` and fresh timings. There is no
speed threshold: scheduling and interpreter differences may change performance.
`verify.py --out /absolute/fresh.json` additionally writes the exact receipt.

The same commands work in an offline minimal checkout containing this directory
and the three PR543 files listed in `SOURCES.json`. They do not download anything.
The adapter refuses changed source bytes and optimized Python, because the
original mutation harness uses assertions. Default supplier commands and frozen
source manifests are unchanged. Production adoption needs a separate integration.

## Measured result

Seven alternating fresh-process pairs, Linux x86_64 / CPython 3.14.7:

| Complete workload | Original median | Adapted median | Speedup |
|---|---:|---:|---:|
| R420 label/frame/scalar/interface check | 0.57623 s | 0.21375 s | 2.70× |
| Original mutation harness (baseline + 9 negative + 1 positive) | 5.93692 s | 1.95643 s | 3.03× |

Every pair uses the same pinned R420 word and compares the entire stdout byte
for byte against both the other engine and the verified receipt. The check
output includes every frame dimension and integer annihilator; the harness
output includes each rejection reason. Both engines perform source admission.
Timings include process startup/imports/admission; OS caches were not flushed.
Raw samples, input pins, environment and all measured Python source hashes are
in `evidence/benchmark.json`. This is not a measurement of the complete supplier
cold replay, C++ columns, hosted-parent audit or integer multiplication.

## Exactness and checked coverage

`adapter.py` replaces only the module global `rref`; every other original checker
function executes unchanged. It converts PR367's reduced primitive integer rows
to **lists of Fractions**, normalizing each row by its own pivot, and returns the
kernel's pivot columns. It does not replace label validation, HNF, determinant,
frame closure/nesting, F2 replay or the H1–H5/dirty-restoration checks.

- All 672 shipped frames: exact RREF rows, pivot columns and the original
  integer-nullspace basis agree. Separate integer dot products check that every
  annihilator kills every input row; rank plus nullity equals eight.
- 1,090 supplemental matrices: the empty matrix, all binary rectangular matrices
  with 1–3 rows and 0–3 columns (685 cases), four targeted rational/pivot cases,
  and 400 seed-94 matrices with up to 16 rows and 12 columns. Seeded cases include
  rational entries, dependent and zero rows, and 257-bit row scaling. The
  reference comparison also checks input immutability and Fraction output types.
- Four arithmetic defects are detected: omitted backward elimination, wrong
  subtraction sign, skipped first column and truncated fractional output.
  `EXPECTED.json` gives small explicit counterexample matrices.
- Five changed geometries are rejected identically: duplicate, zero or scaled
  labels, an unclosed full frame and an out-of-range line. A signed coordinate
  permutation is accepted by both complete checkers.
- The unchanged complete symbolic replay covers all 660 input columns. The
  unchanged original 9-negative/1-positive harness agrees byte for byte.
- Four source corruption controls and disabled-assertion refusal are checked.
  Missing or mismatched `EXPECTED.json` cannot silently pass verification.

These finite checks corroborate the algebraic argument in `PROOF.md`. They are
not a formal verification of the multiplication theorem. This is a deterministic
coverage run with seed 94, not a mathematical search: all listed cases were
completed; no larger domain or optimality claim is made.

## Source and review boundary

`SOURCES.json` pins byte sizes, SHA-256 and Git blob IDs. PR543's supplier source
is `2065fe4f72a914d907f1046603f5a36f17018535`; the three consumed files are pinned
at the base commit. The unmodified vendored PR367 kernel is from
`522285db971642c2d744cc8d45f2a5ade3a55e19`, original path
`research/frame-algebra-performance/exact_rows.py`.

PR367 already establishes the general integer-elimination optimization. This
contribution adds its **selected R420 pivot/nullspace integration**, exact frame
coverage, changed-geometry controls and full-check/harness timings. PR709 caches
successful geometry across words; this adapter speeds up fresh geometry without
cache state. PR707 batches Gram determinants; PR662/667/672 accelerate other
kernels. No composition with those pending adapters is asserted.

`CLAIM.md` records the three candidates, seed and overlap checks. `VALIDATION.md`
records completed and unrun checks. All-size/compiler/common-label/mutable-basis,
hosting/residual/precision/tape/analytic obligations remain inherited. The
adapter neither audits nor discharges those obligations, and makes no new
construction, bound, global optimality or independent human-review claim.

Prepared for **@MrPink604 with substantial OpenAI Codex assistance**. Apache-2.0.
Predecessor credit is retained in `NOTICE.md` and the unchanged kernel header.
