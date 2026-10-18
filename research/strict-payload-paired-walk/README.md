# Paired traversal for strict replay payload comparison

This opt-in successor accelerates positive comparisons in
[`strict-replay-payload-comparison`](../strict-replay-payload-comparison/README.md)
without materializing two complete tagged JSON trees. Its parser, path rules,
timing validation, directory inventory, CLI and negative diagnostics come from
the SHA256-authenticated PR2040 comparator by **commdata2338**. The predecessor
files and selected evidence remain unchanged.

`RESULT.json` records complete-result differential agreement on **1,012 calls**:
365 calls from the unchanged predecessor audit (105-file corpus, 39 adverse
witnesses and its other controls), 625 additional semantic cases, and 22
compressed JSON bodies reformatted to exercise the new traversal. The original
complete audit receipt also agrees. This is comparison evidence, not a fresh
execution of the mathematical supplier.

## What is preserved

Both inputs are completely decompressed and parsed. Duplicate object keys and
nonfinite constants are rejected; Decimal values remain exact. Integers,
Decimals and Booleans retain different tags. Every declared timing path is
validated on both inputs, including byte-identical inputs. Root tokens and
canonical POSIX prefixes retain the original injective path tagging, longest
prefix rule and literal-string distinction. Unknown fields and array order
remain significant. No digest or previously cached equality replaces reading
the actual payloads.

`paired` compares matching containers recursively. For objects with root maps,
it makes only a per-object map from normalized key to original key/value; with
empty root maps it compares the original key sets. Arrays compare their lengths
and all corresponding entries. Scalar comparison first checks the exact Python
type produced by the retained parser. Object-key order is irrelevant, as it is
in the original sorted tagged representation. Original keys are retained for
the two timing-path traversals: a normalized key is never mistaken for a path
component.

An induction on these cases shows that a successful traversal gives exactly
the same tagged-tree equality as PR2040. For the timing quotient, the two nodes
are equal as timing tags only when **both** original paths are masked; otherwise
the usual recursion applies. All masks have already passed the original shape,
type, finiteness and nonnegativity checks. Equal payload bytes under equal root
interpretations retain the predecessor's existing shortcut.

If a comparison fails, or the speculative traversal encounters an error, the
adapter invokes the original comparator on the original bytes and policies.
This preserves its entire result, including invalid-input precedence and the
first-difference diagnostic. A new traversal cannot accidentally replace an
invalid sibling by an early mismatch. Binary files always take this original
path. The adapter changes only a private, authenticated module instance; it
does not patch another importer or rewrite a frozen file.

## Measurements and limits

`BENCHMARK.json` contains three alternating-order trials on the five largest
compressed JSON bodies in the pinned corpus. The run changes only leading and
trailing JSON whitespace and measures complete `classify` calls, including
decompression and parsing. Both methods must return the full same result.
Fixture creation, source authentication and corpus extraction are outside the
timed interval. Reproduce the observation on the intended machine; the timing
is not an acceptance threshold and concurrent load can change it.

On CPython 3.12.14 / Windows 11, the sum of the five per-file median times fell
from 16.111 seconds to 6.584 seconds (**2.447x**). Individual ratios were
1.622x–2.750x. These timings include the same full-input checks and do not use a
warm result cache. The separately recorded tree-only profiling was used to
choose the optimization, not as the end-to-end speedup claim.

The saving comes from avoiding complete tagged-tree allocations on positive
cases. Parsing still constructs both JSON values, and wide objects still need
per-object key maps when relocation is enabled. Peak memory was not measured.
Different or invalid payloads can be slower because the original fallback
parses them again. Equal-byte and ordinary gzip-container cases already have a
shortcut in the predecessor. There is no claimed speedup for those cases.

The unchanged contract is JSON plus canonical POSIX root maps. PR2344's Windows
drive-root adaptation is a separate caller and is not replaced here. This does
not add UNC handling, raw digest rebinding, a supplier admission, a new circuit
cost, or a new kappa. Inputs remain trusted local files subject to the existing
parser's recursion and resource limits; arbitrary attacker-sized JSON is not a
new supported service interface.

## Reproduce

Python 3.12 or later, standard library only:

```sh
python3 -I -B research/strict-payload-paired-walk/verify.py
python3 -I -O -B research/strict-payload-paired-walk/test_compare.py
python3 scripts/research_package.py --package research/strict-payload-paired-walk
python3 -I -B research/strict-payload-paired-walk/benchmark.py --rounds 3 --out /tmp/paired-benchmark.json
```

The test file runs all nine retained predecessor test groups against the new
adapter, including its CLI, plus six adapter controls. These check source-change
invalidation before execution, original diagnostic equality, original-key
masking, rejection of invalid identical timing data, detection of a Python
equality mutant, and that positive traversals do not build tagged trees.
`SOURCES.json` authenticates all 12 inherited inputs by SHA256 and Git blob ID;
the replay works without a Git checkout or network. `RESULT.json` is compared
as canonical JSON bytes, so Boolean/integer substitutions cannot satisfy it.

The CLI is the same as the predecessor, with this script path:

```sh
python3 research/strict-payload-paired-walk/compare.py REF_DIR RUN_DIR \
  --ref-root W=/old/root --run-root W=/new/root --out comparison.json
```

Use an explicit timing policy only when that caller authorizes those exact
typed paths. This package introduces no default ignored fields.

## Open next questions

Can an actual replay wrapper obtain a useful end-to-end saving after its own
source authentication and unchanged-output shortcuts? First run its complete
output comparison through both implementations with identical policy and
retained negative fixtures; adoption is blocked on caller-specific review.

Can the negative path reuse already parsed values while preserving the
predecessor's exact error ordering? First profile a representative changed
large payload. This is left open because positive-path allocation is the
measured bottleneck addressed here, and moving diagnostic logic would enlarge
the verification boundary.

Prepared by **ywz65**, with substantial OpenAI Codex assistance in implementation,
proof review, testing and writing. Apache-2.0. Credit to commdata2338 for the
strict comparator and controls, Josie Elliston for the historical portability
comparator, Rohan Arun and the retained supplier authors for the frozen corpus.
