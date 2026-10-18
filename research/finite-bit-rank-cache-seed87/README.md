# Exact finite-bit transition caching

Verification tooling. No new kappa or construction is claimed.

The retained finite-bit checker already caches exact elimination results, but
still subtracts and hashes a rational matrix for every physical edge. The
opt-in [adapter](adapter.py) interns normalized frames once per call and uses
an integer pair to reuse an identical transition. Its nine-line replacement
leaves all input, scalar, endpoint and deficit checks in place. Every physical
edge still contributes its own charge, in its original position.

Base commit: `680967accfd4311f3241dc154e1f434869747b43`.
Final upstream refresh: `ddb4371c16a5a5de9e363afa8c0d6d7c27429e3c`;
all 57 live inputs remain byte-identical to the research base.
The selected record at that commit is PR1094's conditional
`kappa = 836330098538459/500000000000000000`.
[SOURCES.json](SOURCES.json) pins 57 live inputs and two provenance files by
Git blob and SHA256. The original checker, frozen certificates and `upstream/`
are unchanged. Loading fails if the checker's pinned source bytes differ.

## Why the cache preserves the check

Validation first converts every frame to an immutable tuple of exact
`Fraction` entries. Python dictionary equality compares the complete tuple,
including entries, so equal IDs imply equal matrices. A hash collision does
not equate unequal keys. The key for an edge is its ordered source/sink ID
pair. On the first occurrence, the unchanged expression computes
`rank(sink - source)`. Every repeated pair has exactly the same difference
matrix, hence the same rational rank. Appending that rank for every original
edge preserves the complete edge-rank list, its sum and every returned field.

Both dictionaries are local to one `inspect_candidate` call. A caller can
change a frame between calls and must receive a newly checked result. The
adapter caches no circuit validity or completed audit verdict. It uses the
original arithmetic, including the existing bounded elimination cache.

There are at most F frame keys and E transition keys for F frames and E edges.
This adds O(F + E) references in the worst case. Workloads with few repeated
frames need not benefit. The measurements are finite runtime evidence, not
an asymptotic improvement or a formal proof of the multiplication theorem.

## Reproduce

From the repository root, with Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/finite-bit-rank-cache-seed87
```

Expected result: `PASS_FINITE_BIT_TRANSITION_CACHE`. The command validates
source pins, compares complete reference/cached receipts, and runs 53 existing
tests under each engine. It does not write generated certificates.
The registered replay also passes with `PYTHONOPTIMIZE=2` inherited by its
driver. Child processes explicitly enable assertions, and directly launching a
worker with `-O` fails. This retains assertions used by historical dependencies.

For the benchmark, run:

```sh
python3.12 -B research/finite-bit-rank-cache-seed87/verify.py --pairs 9
```

Each engine runs in a fresh subprocess. Pair order alternates, and each
fixture group starts with the inherited rank cache cleared. Timing includes
normalization, scalar validation, all endpoints, the complete physical edge
list and scoring. Fixture construction and process startup are excluded from
the reported group times. The complete Fano audit is also timed separately.
No wall-clock threshold controls acceptance.

The fixed domain is all 15 Fano completion fixtures, all five existing
rank-product controls, both existing 64-dimensional block-core controls, and
12 rational-frame fixtures. The latter use seed 87, dimensions 2, 3, 4 and 8,
and banks of 1, 3 and 17 frames, with signed numerators -3 through 3 and
denominators 1 through 5. This is differential coverage, not a search for a
stronger bound. The stopping rule is at most nine benchmark pairs.

Eleven controls reject bad endpoints, a wrong permutation, an omitted scalar
update, a float, a wrong dimension, repeated ports, a missing terminal, a zero
denominator, equality submitted as a strict deficit, and two source-byte
changes. A valid frame mutation changes the edge charges; restoring it recovers
the original receipt. Reference and cached engines must agree on the full
error class and message as well as accepted receipts.

[BENCHMARK.json](BENCHMARK.json) records individual measurements, exact receipt
digest, rank-call counts and environment. Every complete receipt is compared
before it is reduced to a digest in that report. The existing test modules are
listed explicitly in `verify.py`; no test is selected by a performance result.

Nine alternating fresh-process pairs on macOS arm64, CPython 3.12.15:

| Workload | Reference median | Cached median | Speedup |
| --- | ---: | ---: | ---: |
| Both 64-dimensional block-core controls | 4.6681 s | 3.8311 s | 1.2185x |
| Five rank-product controls | 0.2614 s | 0.1885 s | 1.3864x |
| Fifteen Fano frame checks | 0.0396 s | 0.0201 s | 1.9678x |
| Complete Fano audit | 0.0724 s | 0.0536 s | 1.3503x |
| Twelve varied rational-frame controls | 0.0181 s | 0.0184 s | 0.9809x |

The last workload is about 2% slower, so this is not a universal speedup.
For the Fano checks, rank-function calls fall from 5,532 to 30 while exact
elimination misses remain two. Block-core calls fall from 764 to 360 with
63 elimination misses in both engines. The benefit comes from avoiding repeated
matrix construction and hashing, not from omitting a distinct elimination.
Every pair produces the canonical full-receipt digest
`93acaade285fe35afc2a3ad87283c04c86d0a766d03e432dec738a60a8e52ca3`.
[PORTABILITY.json](PORTABILITY.json) records the same receipt and 53 tests per
engine on CPython 3.14.8. Python 3.10 syntax parsing passes; execution on 3.10
and Linux was not tested. The benchmark was not CPU-pinned or isolated from
other host activity; individual samples remain in the report.

## Credit and scope

Douglas R. Colkitt authored the retained finite-bit contract, historical Fano,
rank-product and block-core work used here. Their original sources and notices
are preserved. This work is Sagar Thakrar's contribution, with substantial
OpenAI Codex assistance in profiling, implementation, checking and writing.
New work is Apache-2.0, the repository's license. No independent human review
is claimed.

Nearest parallel work: [4RchYMing's PR808](https://github.com/CrocSwap/integer-mult-bounds/pull/808)
optimizes cyclic routing-state search;
[Richard Hoekstra's PR1234](https://github.com/CrocSwap/integer-mult-bounds/pull/1234)
optimizes rational span normalization and complements; CubeJerry's
[PR1459](https://github.com/CrocSwap/integer-mult-bounds/pull/1459) and
[PR1461](https://github.com/CrocSwap/integer-mult-bounds/pull/1461) optimize
rational containment. Their methods and targets are separate from this per-call
transition cache. Their source heads were inspected in the overlap check;
none is a dependency of this adapter.

This does not replay the selected supplier, its native compiler, hosting,
precision, tape or analytic interface. All inherited conditional obligations
remain. The added argument proves why identical transitions can reuse a rank;
the finite replay checks implementation agreement on the declared fixtures.

## Open next questions

Should the retained checker adopt this cache? Review the replacement and repeat
the same workload benchmark on Linux first. Adoption would require maintainer
review and explicit migration of the six historical certificates that pin the
original checker. There is no justification here to change the selected
frontier or to optimize unrelated frame algorithms. [TASK.json](TASK.json)
records the same bounded follow-up.
