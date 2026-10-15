# Strict comparison of generated replay payloads

**Scoped audit and opt-in tool; no new mathematics or kappa.** The retained
[PR1824 comparator](../selected-final-stage-portability/compare_payloads.py)
classifies 39 changes to authenticated PR1094 receipts as mere formatting or
relocation. [compare.py](compare.py) rejects all 39 while retaining valid
formatting, gzip recompression, path relocation and explicitly declared timing
changes. The frozen predecessor, selected record and source pins are unchanged.

For example, replacing `"local_profile_recounted": true` with
`"local_profile_recounted": 1` in the archived `INDEPENDENT-T16.json` returns
`json-format` in the predecessor. Python object equality equates `True` and `1`
before its type-aware `json_diff()` is reached. The strict tool reports a
`proof-relevant-candidate`, leaving mathematical significance to the reviewer.

## Exact audit domain and result

The corpus is all **105 files** under `candidate/strict/` in the immutable
PR1094 reviewed replay archive. The archive and comparator are pinned by raw
SHA256 and Git blob in [SOURCES.json](SOURCES.json). The archived review receipt,
assembly and replay receipt are also bound to their retained files. Archive
members are read in memory, without extraction or execution.

| Mutation family | Cases | Predecessor classification | Strict classification |
| --- | ---: | --- | --- |
| Boolean ↔ integer 0/1 | 25 | `json-format` | proof-relevant candidate |
| Replace an input path by its literal placeholder text | 6 | `json-relocated` | proof-relevant candidate |
| Insert a conflicting placeholder key that relocation overwrites | 6 | `json-relocated` | proof-relevant candidate |
| Add a duplicate proof-field key | 1 | `json-format` | invalid (duplicate key) |
| Change 68 to 68.000000000000000000000001 | 1 | `json-format` | proof-relevant candidate |

The 25 type cases exhaust the eligible scalar leaves of **three receipts only**:
`INDEPENDENT-T16.json`, `REPLAY.json` and `STAGES.json`. They comprise two Boolean
fields, one namespace coordinate and 22 stage exit codes. This is not an
exhaustive mutation census of the large generated word arrays. The 12 path
cases cover each of the six input keys, with both replacement and insertion.
[RESULT.json](RESULT.json) records every case, its typed path, mutated-byte
digest and both classifications.

The relocation issue is independent of type equality. The predecessor converts
paths to ordinary placeholder strings and rebuilds objects with a dictionary
comprehension. An existing literal placeholder key can therefore collide with
a relocated path; one value disappears. In the insertion witnesses the extra
key has an incorrect all-zero digest and is silently overwritten. The strict
representation retains the extra key and value.

Positive controls check all 105 unchanged files, all **22** gzip files under an
alternate compression level/mtime, and all **72** plain JSON files after
reformatting. A separately constructed complete corpus fixture changes only
six root prefixes and 22 valid timing values; its classifications are 102
byte-identical, one relocated JSON, and two declared-timing files. This fixture
is a transformation of reviewed output, not a new supplier execution.
Deleting each of the 22 declared timing fields is rejected separately.

## Comparison contract

The tool compares complete parsed JSON trees, retaining empty containers,
unknown fields, object keys and array positions. Duplicate keys and nonfinite
constants are invalid, even when both files contain identical bytes. Decimal
numbers are parsed exactly, so an arbitrarily small decimal change cannot
disappear through binary floating-point rounding. Booleans, integers and decimal
numbers have distinct tags. Decimal spellings with the same exact value, such
as `1.25` and `125e-2`, may compare equal; integer `1` versus decimal `1.0` is
conservatively reported as a type change. Integer negative zero is integer zero.

Relocation maps an explicitly declared absolute POSIX prefix to an internal
`(path, token, suffix)` tag. Literal strings have a different tag. Each side
must use distinct tokens and prefixes, and the token sets must agree across
sides. Overlapping prefixes are allowed with distinct tokens and longest-prefix
matching. There is no filesystem resolution or Windows-path interpretation.
Only prefix substitution is permitted; suffixes are retained literally.

This map is injective within either input: unequal suffixes or tokens stay
unequal, while a fixed token identifies one prefix. A literal string cannot
equal a tagged path. Object canonicalization retains all key/value pairs and
checks that their tagged keys are distinct. By structural induction, the tagged
tree then preserves every node except the explicitly declared quotients.
Identical bytes are accepted only after parsing and timing validation; when root
interpretations differ, their full relocated trees must still agree.

No timing field is ignored by default. [TIMINGS.json](TIMINGS.json) opts into
the exact 22 typed locations for these two selected receipts. Every declared
location must exist in both files and contain a finite nonnegative number,
excluding Booleans. It then receives a timing sentinel. A missing field,
an unfamiliar nested `seconds`, a key containing `/seconds`, a changed stage
name or a changed digest remains visible. In particular, **raw digest fields
are never ignored or rebound** by this tool.

For gzip files the complete decompressed content is compared. Non-JSON payloads
require byte equality; binary bytes are never decoded with replacement. Regular-file
inventories must agree and symlinks are outside the contract. Exit code 0 means
equivalence under these explicit rules, 1 means a file difference or invalid
payload, and 2 means a configuration/input-access error. This is comparison,
not mathematical verification or authentication of a claimed execution.

## Reproduce

Python 3.12 standard library, from the repository root:

```sh
python3 -I -B research/strict-replay-payload-comparison/verify.py
python3 -I -O -B research/strict-replay-payload-comparison/test_compare.py
python3 scripts/research_package.py --package research/strict-replay-payload-comparison --check-only
python3 scripts/research_package.py --package research/strict-replay-payload-comparison
```

Expected audit marker:

```text
PASS_STRICT_REPLAY_PAYLOAD_COMPARISON files=105 false_equivalences=39 type_cases=25 path_cases=12 timing_rejections=22 no_new_kappa
```

The default audit writes nothing in the checkout and uses no Git or network.
`--write-result` is a first-generation option that refuses to overwrite its
receipt. The registered package checker additionally checks historical Git
provenance. Nine focused test groups cover scalar types and exact decimals,
duplicate/nonfinite JSON, injective roots and stale paths, precise timing paths,
gzip corruption, full containers, CLI failures, and immutable-source rejection.
The archive control changes only gzip MTIME, confirms an unchanged decompressed
tar, and still requires raw-source-pin rejection.

For other generated trees, use the standalone tool with no exemptions, or add
explicit root pairs and a reviewed timing policy:

```sh
python3 research/strict-replay-payload-comparison/compare.py REF_DIR RUN_DIR
python3 research/strict-replay-payload-comparison/compare.py REF_DIR RUN_DIR \
  --ref-root 'WORK=/absolute/reference/work' --run-root 'WORK=/absolute/run/work' \
  --timings research/strict-replay-payload-comparison/TIMINGS.json --out comparison.json
```

The example root mapping is illustrative. The selected receipt requires both
its `WORK` and `LOCAL` roots, using the paths actually recorded by each run.
Never apply generated-payload equivalence to immutable source archives.

## Independent Linux observation and limits

A separate invocation of the unmodified PR1824 `verify.py` on Linux x86_64,
CPython 3.12.3, completed the selected final stage with the retained kappa, but
its expected comparison-count assertion failed. The output had 99 byte-equal
files, one JSON formatting difference, one relocated JSON, two timing differences
and two proof-relevant candidates. The formatting difference was
`global/audit/PREFIX-AND-INVOICE.json`; the two candidates were its raw
`input_sha256/fresh_invoice` references in `ADMISSION-CONTROLS.json` and
`ASSEMBLY.json`. The invoice's complete typed payload agreed. This is additional
local execution evidence, not a registered cross-platform equivalence claim;
the archived byte-exact ASSEMBLY condition did not pass. Neither comparator is
changed to suppress those references. The reproduction is the predecessor's
documented `python3 -B research/selected-final-stage-portability/verify.py`.

This audit does not establish that the production supplier verifier accepts a
bad construction, invalidate the predecessor's reported macOS runs, rebuild the
earlier cold stages, or discharge inherited all-size, physical, precision,
hosting or analytic obligations. No Windows execution, resource-exhaustion
hardening, formal proof of this Python implementation, new supplier, or exponent
improvement is claimed. The standalone comparator is opt-in; no frozen caller
is rewired.

## Scope, overlap and credit

Base: `c676548106012571fefa1dce0ec16f1bcfe11dce`. Card `portable-replay`, priority
revision 3; full refined task card and exact predecessor heads are in
[TASK.json](TASK.json). The claim is in discussion
[#1472](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472).

Josie Elliston's PR1824 supplied the comparator, replay and portability results
being audited; its exact head is `ad5b1248f25a71983b20617e2f3a80be22f03990`.
Adam Gall's [generated-identity audit](../selected-generated-identity-audit/README.md)
checks a different seven-artifact projection and explicitly leaves other
normalizers open. This account's PR1372 and Gareth Davidson's T37 code concern
digest-to-role permutations, not these type/relocation equivalences. PR1559
repairs different gzip comparison sites. These contributions are credited,
not repeated. No pending code dependency is imported.

Credit Maxime Fleury's gzip convention and Antoine Olivier's independent replay;
Rohan Arun's PR1094, Jeremy Kothe's strict verifier, Hao Yan and the retained
supplier/compiler lineage; and Douglas Colkitt's reviewed archive and replay
records. Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Assistance covered design, code, experiments, tests and writing; self-reviewed
only. New work is Apache-2.0; predecessor bytes and notices remain intact.

## Open next questions

1. **Adopt the strict comparator in a future wrapper?** This could remove the
   demonstrated ambiguity. First review each caller's intended number/path/time
   contract, then test that caller with explicit timing paths. The blocker is
   caller-specific compatibility and source-pin review; adoption is not part of
   this package.
2. **Bind portable invoice references without ignoring them?** The Linux
   observation shows why formatting-independent payload equality alone is not
   enough for receipts containing raw hashes. First authenticate both complete
   invoice payloads and design an explicit reference-rebinding rule. The blocker
   is preserving that binding across the complete receipt graph; a global
   `log_sha256` or `input_sha256` exemption would not do so.

Structured versions of both questions are in [TASK.json](TASK.json).
