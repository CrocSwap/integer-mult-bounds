# Exact exponential intervals with integer arithmetic

**Tooling improvement and bounded end-to-end performance result; no new κ.**

This opt-in kernel evaluates the independent PR626 owner checker's exponential
intervals with integer arithmetic. It returns exactly the same two rational
bounds as the pinned reference: the same degree-16 Taylor polynomial, geometric
remainder bound, and 200-bit outward rounding. It changes neither precision nor
the moment admission threshold.

On the actual 18 exponential argument pairs used by the archived owner check,
15 alternating pairs per interpreter on macOS arm64 measured approximately
**13× faster arithmetic**. Each kernel batch repeats those 18 pairs 50 times.

| Local interpreter | Kernel reference → integer | Ratio | Complete owner check reference → integer | Ratio |
| --- | ---: | ---: | ---: | ---: |
| CPython 3.14.4 | 0.62026 s → 0.04810 s | 12.90× | 0.38281 s → 0.37411 s | 1.023× |
| CPython 3.13.5 | 0.63399 s → 0.04867 s | 13.03× | 0.41303 s → 0.40023 s | 1.032× |

**The complete-check improvement is small (about 2–3% less wall time).** An
initial Python 3.14 run showed only 0.5% improvement. The checker also reads and
validates native programs and 35,424 owner roles. The arithmetic gain should
not be presented as a frontier-replay speedup or a substantial complete-check
acceleration.

Raw per-pair timings, environments, input/output fingerprints, implementation
hashes and receipt hashes are in [the Python 3.14 evidence](evidence/benchmark-python314.json)
and [Python 3.13 evidence](evidence/benchmark-python313.json). Earlier exploratory
runs are retained as `evidence/initial-benchmark-*.json`; they predate the addition
of implementation hashes to the reporting code. They are not discarded because
of their less favorable timings. Timings are machine-specific, include normal
OS caching, and have no pass/fail threshold. The final two interpreter runs were
sequential. Every complete-check receipt is byte-identical to the pinned baseline.

## Reproduce

From the repository root, with Python 3.11+ and the standard library only:

```sh
python3 -B -m unittest discover -s research/exact-exp-performance -p 'test_*.py' -v
```

Expected result: **11 tests pass**, including exact kernel comparisons and the
complete independent owner checker with negative controls. This does not run
supplier construction or the full selected frontier suite.

To repeat the timing experiment (use a fresh output filename):

```sh
python3 -B research/exact-exp-performance/benchmark.py --pairs 15 --out /tmp/exact-exp-benchmark.json
```

Expected marker: `PASS_EXACT_EXP_BENCHMARK`; timing ratios may differ.
Both engines receive identical input pairs. Pair order alternates. The complete
check runs in a fresh process for each engine, including source admission,
imports, JSON decoding, all existing owner checks and output writing. Entire
receipts are compared after each pair, in addition to each engine's baseline
receipt pin. Kernel timing excludes logarithm construction and input preparation;
the complete-check timing includes them.

For a single opt-in replay:

```sh
python3 -B research/exact-exp-performance/run.py --engine integer --out /tmp/exact-exp-owner.json
```

Expected marker: `PASS independent map and exact moments`. The complete report
SHA-256 is `ec82a647bc3567efef91a1588c86f012cdbb5decac0c25a9f38ba5d11762a092`.
`--engine reference` executes the unchanged reference. Existing output paths and
paths inside the repository are refused. Run from a full checkout: the archived
fixtures are already committed and no network access is needed.

## Why the bounds are identical

For a reduced `Fraction` x = p/q with q > 0, let

```
c_j = 16! / j!
N = sum(c_j * p^j * q^(16-j), j=0..16)
d = 16! * q^16.
```

Thus N/d is exactly P₁₆(x) = Σ xʲ/j!. The reference forms the same polynomial
by rational term multiplication and addition. The candidate starts N=1 and
Q=1, then for j=15,…,0 sets Q←qQ and N←pN+c_jQ. After processing j,

```
N = sum(c_k * p^(k-j) * q^(16-k), k=j..16),  Q = q^(16-j).
```

This invariant follows directly by multiplication by p and adding the k=j
term. At j=0 it gives the numerator and denominator above without intermediate
fraction normalization.

The reference's upper remainder is

```
R(x) = x^17 / (17! * (1 - x/18)).
```

For 0≤x<1, all Taylor terms are nonnegative and the ratios after the first
omitted term are at most x/18, so the geometric bound covers the entire tail.
With the same N,d and t = 17(18q-p)>0,

```
P₁₆(x) + R(x) = (N*t + 18*p^17) / (d*t).
```

The candidate therefore returns floor(2²⁰⁰P₁₆(a))/2²⁰⁰ and
ceil(2²⁰⁰(P₁₆(b)+R(b)))/2²⁰⁰ by integer division. These are exactly the
reference's `down` and `up`, including grid boundaries and zero. Python integers
are unbounded; there is no floating-point arithmetic or input-dependent cache.

Supported inputs are `Fraction` endpoints satisfying 0≤a≤b<1, exactly the
actual owner-checker calls. Other types are rejected explicitly. This does not
promise compatibility with accidental behavior on floats or other numeric types.
Invalid intervals raise `ValueError`; checks remain active under optimized Python.

## Validation scope

The kernel tests compare all **276 boundary pairs** and **480 seed-91 rational
pairs**, with denominator sizes through 1024 bits, to the source-pinned reference.
A separate direct-power/factorial implementation checks the arithmetic, and a
degree-64 enclosure supplies exact witnesses for rounding and tail controls.
Five negative mechanisms are detected: an omitted polynomial term, an omitted
tail, an incorrect tail ratio, and inward rounding at either endpoint. These
finite checks corroborate the algebraic argument; they are not a formal proof
of the multiplication theorem.

The replay test executes **32 subprocess controls** covering both engines:
normal and optimized-Python positives, existing-output protection, repository
output refusal, changed and missing pinned sources, and a wrong receipt digest.
Mathematical mutations exercise both moment thresholds, owner width/family/call/
footprint checks, call chronology, native hashes and orientation counts. For
these mutations only, the test bypasses adapter source admission and recomputes
the relevant input pins in a temporary copy, so rejection comes from the actual
checker obligation. It requires the specific expected error, not just any crash.
These controls pass on local Python 3.14.4 and Python 3.13.5 (the latter suite
also under `-O`); each suite runs the checker with and without optimization.
The dedicated Linux workflow is separate from these recorded local results.

`SOURCE.json` pins the exact base, reference helper, full checker, six package
inputs and four archived native artifacts. `run.py` executes the unchanged
checker via `runpy` and narrowly intercepts its import of `exact_intervals.py`:
the original module is loaded first, then only `exp` is replaced. The original
logarithm, source checks, geometry, both program orientations, owner capacities,
disjointness, compaction, rank mass, exact moments and outer conversion all run.
The import hook is restored afterward and must apply exactly once.

The archived native words are reused from the maintainer's PR622 replay; the
owner map is PR626. **No fresh supplier construction, controller replay,
47-inequality assembly, Lean build or full `make verify` is claimed.** All-size
compilation, common-label/mutable-basis realization, pooled hosting,
precision/tape/recovery and analytic assumptions remain inherited. Frozen
packages, `upstream/`, default commands and the selected result are unchanged.

## Provenance and overlap

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. OS-random assignment seed: **91**.
The local claim and three considered tasks are recorded in `CLAIM.json`. No
pinned sprint coordination issue existed at the initial check.

Chafik Boukhalfa's PR626 supplies the independent checker; Jeremy Kothe's
PR622/623 supplies the native construction and inherited dispatch. The archive
comes from the maintainer's review. See [NOTICE.md](NOTICE.md) and the retained
[construction notice](../complex-k492-owner-repair/NOTICE.md) for the cumulative
contributor and AI-assistance record.

Pending PR667 optimizes logarithms in a different moment engine; it is related
work, not a dependency or a source of this implementation. PR662 addresses
Clifford states; PR367 and PR452 address frame algebra and native replay.
This submission changes only exponential interval evaluation and preserves its
negative end-to-end performance result. It makes no priority claim for integer
Horner evaluation.
