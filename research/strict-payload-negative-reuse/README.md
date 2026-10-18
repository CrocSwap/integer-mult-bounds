# Reuse parsed payloads for strict mismatch diagnostics

This opt-in successor takes the negative-path handoff in ywz65's
[PR2693 paired comparator](../strict-payload-paired-walk/README.md).
After a proof-relevant JSON mismatch, PR2693 calls commdata2338's original
PR2040 classifier on the input bytes. Both compressed inputs are decompressed
and parsed again. [compare.py](compare.py) passes the already parsed values
into the original tree-comparison phase instead.

The compressed mismatch control observes four decompressions and four parses
before this change, and two of each afterward. Both implementations return the
same literal diagnostic, including its typed path, scalar types and values.
There is no persistent result cache or dependency-invalidation shortcut.

## Contract and evidence

The positive path, parser, root mapping, timing validation and tagged trees
come from the authenticated predecessors. Parsing and timing validation retain
their original order. The diagnostic phase constructs the reference relocated
tree, the run relocated tree, then each required timing-masked tree, in the
original order. It uses the original `first_difference` function. If speculative
comparison raises one of the original handled errors, the original classifier
still decides the diagnostic from the original bytes. Binary inputs retain the
original classifier.

Consequently, a completed parse is reused only within that call. No files,
fields or subtrees are omitted. Duplicate keys, nonfinite numbers, exact scalar
types, unfamiliar fields, array order, relocated keys and both original timing
paths remain significant under the predecessor's existing policy.

[RESULT.json](RESULT.json) retains the complete PR2693 result, including all
**1,012 full-result differential comparisons** against PR2040. That comprises
the 105-file frozen corpus audit, 39 adverse witnesses, 625 additional semantic
cases and 22 compressed JSON reformats. Its entire canonical result must agree,
including invalid reasons and first-difference details. This is comparison
evidence using archived supplier outputs.

[test_compare.py](test_compare.py) runs all fifteen predecessor control groups
against the successor and adds three groups for parent-source invalidation,
literal mismatch diagnostics and parse/decompression counts, and sorted-path
and invalid-sibling precedence. An independent internal review found a retained
test-module alias error. The alias was corrected to `c`, and all eighteen groups
were rerun against the successor. No independent human review is claimed.

## Measurement

[BENCHMARK.json](BENCHMARK.json) records three trials with rotating method order
on the same five largest compressed JSON bodies in the frozen corpus. Each run
adds exactly one unknown root field, `_negative_reuse_probe`, while preserving
every original body byte before the closing brace. All complete results must
equal the original classifier's result. Full-call timing includes decompression,
parsing, comparison and diagnostics. Setup and fixture construction are outside
the interval. The original PR2040 classifier is measured alongside PR2693 and
the successor for context.
Three of the five files are byte-identical inherited copies of one template.

On macOS 27.0.1 arm64 with CPython 3.12.15, the sum of the five per-file median times
fell from **7.403 seconds to 6.073 seconds**, a **1.219x** speedup over PR2693.
Per-file ratios range from 1.156x to 1.267x. The original PR2040 classifier took
6.149 seconds on the same basis; no improvement over that direct classifier is
claimed. This addresses PR2693's repeated-parse regression while retaining its
positive traversal.

These are observations, not acceptance thresholds or a full-replay speedup.
Other mismatch positions, invalid inputs, root/timing policies and caller
workloads may have different costs. Invalid inputs still take the original fallback. Peak memory was not
measured.

## Reproduce

Python 3.12 or later, standard library only:

```sh
python3.12 -W error -B scripts/research_package.py --package research/strict-payload-negative-reuse
python3.14 -I -O -B research/strict-payload-negative-reuse/test_compare.py
python3.12 -I -B research/strict-payload-negative-reuse/benchmark.py --rounds 3 --out /tmp/negative-reuse-benchmark.json
```

The benchmark refuses an existing output path. The registered replay checks the
canonical retained result and all eighteen control groups. [SOURCES.json](SOURCES.json)
pins all seventeen external inputs by SHA256 and Git blob identity. All inputs
are authenticated before predecessor verifier source executes. The standalone
comparator authenticates its parent comparator and source manifest, whose loader
then authenticates the original classifier.
Changed source is rejected before execution. Full verifier replay and standalone
comparison have different source inventories, as in the predecessor.

The CLI retains PR2040's interface, with this script path:

```sh
python3.12 research/strict-payload-negative-reuse/compare.py REF_DIR RUN_DIR --out comparison.json
```

Declare root maps and exact timing paths only when the caller's policy allows
them. No default ignored field is introduced.

## Implementation and limits

Build the Lever led to the rerunnable full-call benchmark and parse-count
control. Prove It Works led to the complete predecessor-result check and actual
CLI tests. New functions stay below sixty physical lines. The benchmark is
bounded to five fixtures and one through nine trials; source authentication is
bounded to seventeen files. State is private to the adapter module.

Power of Ten deviations remain confined to the inherited comparator contract.
Rules 1 and 3 use the predecessor's recursive JSON/tree routines and managed
allocation on trusted local artifacts. This change adds no recursive traversal
or input-size promise and avoids two extra parsed trees on ordinary mismatches.
The registered commands have 600/120-second caps. Untrusted-input depth, byte
and memory limits would require a separately reviewed boundary; arbitrary-input
hardening is not claimed. Rules 8 and 9 retain authenticated source compilation
and private-module adaptation so frozen predecessors and bytecode caches cannot
replace the declared source. All execution targets are pinned local modules.
Rule 10 uses warning-as-error replay, syntax inspection and the registered tests;
the repository declares no shared Python linter for these scripts. The follow-up
for those deviations is a caller-owned bounded-input contract before service
adoption, rather than changing historical comparator behavior here.

The successor inherits PR2040's inventory and integer-conversion boundaries.
PR2921's fail-closed inventory, PR2803's large-integer parser and PR2344's Windows
roots are separate adapters and are not composed here. Inputs must remain stable
while the inherited directory comparator reads them. No frozen caller is changed.
No new supplier, selected exponent, full cold replay or multiplication theorem
is claimed. See [TASK.json](TASK.json) for scope, source baseline, overlap and
the bounded stop rule.

## Open next questions

Can an actual replay wrapper benefit from this mismatch optimization under its
authorized root and timing policy? Profile that wrapper's complete changed-output
corpus with both comparators, preserve full diagnostics and include authentication
costs. Caller-specific adoption and review remain the blocker.

## Credit

Credit ywz65, PR2693, for paired traversal and its explicit negative-path
handoff; commdata2338, PR2040, for the strict comparator and full controls;
Josie Elliston, PR1824, for the historical portability comparator; Rohan
Arun, Douglas Colkitt, and the retained supplier/archive authors for the
frozen corpus and receipts. The gzip convention follows Maxime Fleury and
Antoine Olivier. Their files and attribution remain unchanged.

Nick Petalas. Substantial AI assistance was used for implementation,
testing, internal review and writing. Apache-2.0.
