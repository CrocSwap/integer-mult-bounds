# Exact frame containment without rebuilding unions

**Verification tooling; No new κ.** This opt-in adapter accelerates one operation
in the historical rational-frame checker: deciding whether every source row lies
in a target frame. It checks exact integer equations instead of reducing their
combined row basis. The complete h=10 and h=12 mixed-point audits keep the same
mathematical payload and selected-frame hashes. No original checker, supplier,
selected record, frozen artifact or `upstream/` file is edited.

Base: `cd91ac8e2652bfee6bf09da3b8724253bcf78f5f`. At that base the selected
conditional κ is **0.001672660197076918**, PR1094 on PR1087/k8/T16, with
PR589 on PR555 for the bit side. We followed the selected source manifest,
assembly, construction README, review and cold-replay wrapper. That supplier
is context, not this benchmark's workload.

## Reproduce

From a full repository checkout on POSIX, using Python 3.12 and only its standard library
(tested on Linux; the inherited benchmark imports `resource`):

```sh
python3.12 scripts/research_package.py --package research/exact-frame-containment
```

Expected: both five-group kernel suites pass, followed by
`PASS_EXACT_FRAME_CONTAINMENT audits=6 decisions=42860 compiler_controls=4 kernel_mutations=5`
and `PASS_REGISTERED_RESEARCH_PACKAGE research/exact-frame-containment outcome=completed`.
The registered command checks exact Git/SHA256 provenance and all six live
execution-input pins. The selected record and task catalogue are pinned as
historical provenance; a later selected result does not invalidate this package.

The direct offline replay is `python3 -I -B research/exact-frame-containment/verify.py`.
It needs this directory and the six source files in [SOURCES.json](SOURCES.json).
It verifies their SHA256 hashes without requiring Git history. Temporary work
uses a path containing spaces and is removed; success receipts are not written
unless `--out FRESH_PATH` is supplied. Whole-audit `-O` is deliberately refused
because inherited circuit assertions are proof-relevant. The independent kernel
suite runs both normally and under `-O`.

Fresh timing, including process startup, adapter imports and source admission:

```sh
python3 -I -B research/exact-frame-containment/benchmark.py --pairs 9 --cpu 0 --out /tmp/new-containment-benchmark.json
```

Use an available CPU number, or omit `--cpu`; output must not exist. There is no
timing pass/fail threshold. Every sample must match the complete expected payload.

## Exact predicate and cache contract

The predecessor predicate is `basis(sorted(set(U + V))) == V`. It requires a
**canonical representation of V**, not merely equality of abstract row spaces.
For rectangular integer rows, its canonical basis has increasing pivot columns,
positive pivots, primitive rows (gcd one), and zero entries in all other rows'
pivot columns. These properties uniquely describe the primitive scaling of
rational reduced row echelon form. `_prepare` checks every property. A target
which fails any property cannot equal the predecessor's canonical union and
returns false, including scaled, sign-flipped, duplicate, zero and reordered rows.

For canonical rows v_i with pivot p_i and positive pivot value d_i, the unique
possible coefficients expressing u in their span are u[p_i]/d_i. At pivot
coordinates their combination already equals u. Let D=lcm(d_i). For every
nonpivot coordinate j, membership is therefore exactly

```
D * u[j] == sum_i u[p_i] * (D // d_i) * v_i[j].
```

The adapter checks all these equations for every source row, using unbounded
Python integers. Zero coefficients may be omitted from the sums. This proves
equivalence on the declared domain; no floating point, modular rank assumption,
probabilistic acceptance or integral-lattice membership is substituted. An empty
target contains exactly zero rows; a full-dimensional canonical target has no
free-coordinate equations. Source rows may be dependent, zero or nonprimitive.
After validating V, an empty source or the identical immutable source object is
an immediate true case of the same predicate.

Each adapter instance has two caches, each bounded at 4,096 entries. Prepared
equations use the complete immutable target contents. The separate shape/type
validation cache uses `(id(rows), rows)` and retains the matrix object itself:
its ID cannot be recycled while cached. Only exact tuples of exact tuples of
built-in integers pass validation, so their contents cannot change. The ID
distinguishes numerically equal but differently typed matrices such as `(1,)`
and `(True,)`; validation happens before the content-equation cache. Eviction
causes revalidation, not acceptance. No complete audit verdict is cached.
Malformed types and inconsistent widths explicitly fail outside the integer
matrix contract; the predecessor is not claimed to be a general input parser.

## Coverage and failure controls

- **7,339 matrix pairs** agree with independent Fraction Gauss-Jordan rank and
  canonicalization: all 5,828 pairs of binary presentations with at most two
  rows and at most three columns, plus 800 seed-90 generated cases up to 16
  columns and 711 noncanonical-target variants. These include true rational
  membership, dependence, zero/full spaces and multiplication by 2^257+1. The stopping
  rule is completion of this fixed domain, not a mathematical search.
- **42,860 actual containment decisions** in the complete h=10/h=12 audits
  agree individually with the original predicate. All are true in these valid
  fixtures; negative decisions are exercised separately. The original,
  substituted and per-decision crosscheck engines run both complete audits.
- Full output is identical, including 1,798/3,687 physical roles, 16/320 singular
  source spans, 48/969 forced-dual nodes, both nesting directions and both frame
  digests. The canonical payload SHA256 is
  `faa0f9c0159a6e70d4e2cfcdb4012ea62ef350bd26b81312d11da4a770f8b218`.
- Five actual kernel mutations are detected: dropped all/last free coordinates,
  wrong coefficient sign, missing pivot denominator, and acceptance of
  noncanonical targets. Their explicit witnesses are in `test_kernel.py`.
- Four corrupt compiler-frame inputs reject identically under both engines:
  missing, scaled and reordered frames (`Decreasing forward side edge`), and
  full ambient frames at forbidden injections (`Wrong forward injection frame`).
- Six changed source files and two incomplete/duplicate input inventories reject.
  Four changed receipts reject, including a bool-to-int change that naive Python
  equality would miss, a rehashed changed frame digest, an omitted reverse check,
  and an unexpected field. Only the two explicit timing/memory fields are excluded.
- Immutable input and bounded-cache/eviction controls pass. Equal-valued bool,
  float and Fraction matrices are rejected even after warming integer cache keys.

This is an algorithmic equivalence argument plus finite executable evidence,
not a formal proof of the multiplication theorem or a new supplier construction.

## Measurements

Nine alternating pairs on Linux x86_64, CPython 3.12.14, CPU 0:

| Complete h=10/h=12 workload | Reference | Exact containment |
| --- | ---: | ---: |
| Median process wall time | 3.158709 s | 2.726833 s |
| Median peak RSS | 88,852 KiB | 70,512 KiB |

Median wall time is **13.67% lower** (reference/candidate ratio **1.15838**).
Median peak RSS is **20.64% lower**. The candidate is faster in all nine pairs;
these are local measurements, not a cross-platform guarantee. All 18 sample
payloads match. The separate 40-test historical regression set also passes with
both engines; no speed claim is made for that broader suite.

Final paired measurements and exact environment are recorded in
[evidence/benchmark.json](evidence/benchmark.json). The input fixture and all
Python implementation hashes are included. Samples alternate reference-first
and equations-first, starting with reference because seed 90 is even. Each arm
uses the same pinned wrapper and runs the unchanged complete benchmark in a
fresh interpreter. OS caches are not flushed; system contention is uncontrolled.
The comparison is for these historical audits, not the selected cold replay or
integer multiplication. The validation receipt is
[evidence/validation.json](evidence/validation.json). The registered Python 3.12
replay, selected-record integrity check, and a standalone replay from a relocated
export containing only this package and the six read-only input files also pass.

## Open next questions

Would this opt-in predicate still improve the complete audit when combined with
Richard Hoekstra's pending PR1234 normalization/complement changes? A first
step is a four-arm source-pinned benchmark and the same full-payload and failure
controls. The blocker is a separate review and explicit integration of that
pending source; this package neither depends on it nor claims combined speedup.
The structured question is in [TASK.json](TASK.json).

## Credit and limits

Prepared for **@CubeJerry** with substantial **OpenAI Codex** assistance. No
independent human review or subagent review is claimed. New work is Apache-2.0.
Credit Douglas Colkitt and the historical mixed-point/circuit authors, and
Richard Hoekstra's integrated PR239 (commit
`7c2a27ff6b8442522c1e1fdcc0913fd0c54a2d61`) for the dual-Gram checker, independent
Fraction tests and complete benchmark reused here. Pending PR1234 by Richard
Hoekstra optimizes primitive normalization and orthogonal complements in the
same module (head `8812ca21c43f5cea16276c7fa539fa8d1559b0f1` at the final
overlap check); this package changes only containment, via an opt-in substitution.
Aman/PR367 and the integrated R420 row-reduction, Gram-prefix and owner-bitset
tools are neighboring methods, not execution dependencies.

The seed-90 local task card records the three candidates, selected scope and
bounded overlap inspection. GitHub API/posting access was unavailable under the
donor's publication workflow. Public PR bodies, issues, discussions and local
notes were inspected; public-page pagination limits are retained. No exhaustive
novelty or exclusivity claim is made. Full selected-supplier cold replay, the
repository-wide historical suite, native/Lean builds and hosted CI are outside
this contribution; inherited compiler, realization, hosting, precision and
analytic obligations remain untouched.
