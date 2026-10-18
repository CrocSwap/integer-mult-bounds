# Complete portable comparison of the selected final replay

**Verification engineering; no new supplier, paid profile or kappa.** This is an
opt-in caller for the selected PR1094 final stage, not a change to the selected
reproduction command. It closes the *caller-composition* handoff in
[PR2040](https://github.com/CrocSwap/integer-mult-bounds/pull/2040) and
[PR2059](https://github.com/CrocSwap/integer-mult-bounds/pull/2059): execute the
unchanged supplier stage, then compare its **complete 105-file strict output**
with the authenticated reviewed output, without requiring environment-specific
classification counts or erasing unclassified fields.

The older PR1824 caller requires exactly 102 byte matches, one relocation and
two timing differences, then requires raw assembly equality. PR2040 reports a
Linux run where the final supplier passes but invoice object order changes two
consumer hashes and breaks that comparison. PR2059 repairs only the three-node
invoice predicate and explicitly leaves its complete caller open. This package
uses both new predicates **unchanged**, pinned and attributed in `vendor/`, and
adds the full execution, source binding, inventory and cross-receipt boundary.
The Linux observation belongs to PR2040; it is not a Linux run performed here.

## Exact scope and comparison policy

[POLICY.json](POLICY.json) names every output and permitted transformation.
The complete boundary consists of 94 JSON or gzip-JSON artifacts, 11 inner logs,
and the outer 13-line execution log. The complete 105-file inventory is required
on **each** side, even when both sides are identical. Missing and extra files
are errors. Directory loading rejects symlinks.

Before comparing payloads, each side independently checks:

1. **Two invoice edges.** Both consumers' literal `input_sha256/fresh_invoice`
   values must hash that side's actual invoice bytes. PR2059 then replaces only
   these two values with the complete canonical invoice digest. The entire
   invoice and both entire consumers remain in the comparison.
2. **Twenty-two log edges.** The eleven ordered, successful stages must occur
   in both `STAGES.json` and `REPLAY.json`. Their complete stage arrays must be
   typed-equal *within that run*, including elapsed times, and every recorded
   log hash must match that run's actual inner log bytes. Those eleven logs are
   also compared byte for byte across runs. Repaired references cannot hide
   altered log contents.
3. **Six input roles.** `INDEPENDENT-T16.json` must name exactly its three
   work-tree inputs, two local inputs and source owner input, and all six
   digests must match the corresponding bytes. Only these six exact path keys
   are replaced with fixed role keys. Receipt paths are never followed to read
   files. No general prefix rewrite applies to other keys or string values.
4. **Twenty-two execution times.** Only the eleven per-stage times in each of
   the two receipts may differ across runs. They must be present, finite,
   nonnegative numbers, not Booleans or strings. The **12 copied historical
   timing fields** elsewhere remain exact.
5. **The complete outer log.** Its eleven ordered `PASS name time` lines must
   agree with the same-side stage times, and its two final result lines must
   match exactly. No arbitrary line, trailing token or generic `seconds` key
   is stripped.

After those checks, PR2040's strict comparison consumes every file's entire
payload. It rejects duplicate JSON keys and nonfinite numbers, retains numeric
types and every unfamiliar field, and compares exact Decimal values rather
than rounded binary64. The invoice and independent-input receipts use the
narrower integer/string/Boolean/null schema. Gzip streams are decompressed;
container headers alone do not establish a proof-relevant difference. The
comparison does **not** require a fixed count of formatting/container classes.

### Why this composition preserves evidence

Write the comparison as `V(A) and V(B) and N(A) = N(B)`. `V` is the per-side
inventory and raw-reference check above. `N` preserves every payload except the
explicit representation coordinates. Authenticating both invoice links is
necessary but insufficient: the complete canonical invoice is compared too,
so changing the invoice and repairing both links still rejects. Full consumer
comparison retains every other hash and proof field. Exact role-key sets make
path substitution injective on the six declared inputs. Typed equality retains
Boolean/integer distinctions and object/list boundaries. Stage timing removal
cannot detach a stage from its log or alter its order, status or exit code.

This argument is about the declared comparison relation under the usual
SHA-256 collision-resistance assumption. It does not prove the Python programs
formally, authenticate historical execution, or establish that arbitrary
matching receipts describe true mathematics.

### Deliberately closed graph boundary

An exploratory census found 173 hash-valued leaves whose values happen to
match output bytes. Some are semantic digests or have several byte-identical
candidate targets. **Value coincidence is not a role contract**, so this caller
does not infer graph edges from that census and does not rewrite those hashes.
Only the two invoice edges are rebound; the six input and 22 log edges are
checked without digest rebinding. Every other digest field stays exact in the
full payload comparison. This is not an arbitrary reserialized-DAG validator,
and does not promise acceptance when other artifacts' changed raw hashes
propagate into other receipts. It completes the explicit invoice-format,
root-relocation and fresh-timing caller boundary, not universal portability.

## Source and execution boundary

The scientific base is `564148b82ae9df72163f22106f15e73efca8aff2`, priority
revision **4**, selected kappa `836330098538459/500000000000000000`.
[SELECTION.json](SELECTION.json) preserves the one-shot independent chooser
nonce `a1c9b8df7348849ae3ec156120abe878`; [TASK.json](TASK.json) records the
`portable-replay` refinement before the substantive archive experiment.

[SOURCES.json](SOURCES.json) pins 42 live repository inputs by Git blob and raw
SHA-256, including the final package manifest and every member it names, the
strict driver's upstream pins, the entire copied frozen base, both reviewed
archives and the used review receipts. Both small vendored comparators retain
exact upstream bytes, immutable commit URLs, blob IDs and SHA-256 hashes.
Sources are authenticated before execution. `VERIFY.json` declares all 42
inputs for replay invalidation. No network or unpinned dependency is required.

The local input is all ten `slots/local` files from the authenticated PR1042
archive, checked against its complete receipt. The output reference is the
PR1094 archive, additionally bound to the committed assembly and execution
receipts. The supplier runs in fresh external storage with assertions enabled;
source archives, selected pointers and frozen packages are never modified.

The reviewed archive omits the extracted `source/` directory. Its owner-input
reference is therefore checked against the separately pinned selected package's
`data/OWNERS.json.gz`, not an invented archive member. The fresh run's owner
reference is checked against its actual extracted/overlaid input.

At the submission checkpoint, canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` changed guidance only; the catalogue,
selected record and scientific inputs remained unchanged. The new guidance was
read while the original scientific base was retained. The shared complete
snapshot contained 353 open PRs (including drafts, 19:00:33Z) and 738 discussion
records (19:02:09Z). Targeted searches and live PR2040/2059 heads were checked at
19:04Z; both heads were unchanged. These searches are not a novelty certificate.

## Reproduce

From a full-history checkout, with standard-library CPython 3.12:

```sh
uv run --python 3.12 --no-project python -I -B research/selected-final-replay-closure/verify.py
uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/selected-final-replay-closure --check-only
uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/selected-final-replay-closure
```

Each scientific command actually executes the unchanged final supplier stage.
The default uses a temporary directory and writes nothing into the checkout.
`--work NEW_EXTERNAL_DIRECTORY` preserves diagnostics; `--write-result NEW_FILE`
is an explicit first-generation option that refuses overwriting. Normal replay
compares the complete deterministic result with [RESULT.json](RESULT.json).
Per-run classification counts are diagnostic, not the acceptance criterion.

## Observed evidence

The final direct scientific smoke freshly executed the unchanged supplier and
passed the complete comparison: **103 byte-equivalent normalized outputs and
two declared timing differences**. This classification is an observation, not
an exact-count acceptance rule. The direct command including controls completed
in 268.58 seconds on CPython **3.12.12**, macOS **27.0.1 arm64**, standard library.

The metadata/source-pin check passed. The registered replay then passed in
261.47 seconds, freshly executing the supplier again and reproducing the
complete deterministic receipt. Its parent verifier uses `-I -O -B`; the
supplier subprocess deliberately runs without optimization and with inherited
`PYTHONOPTIMIZE` removed, so its assertions remain enabled. Observed markers:

```text
PASS_FRESH_SELECTED_FINAL_STAGE {"bytes": 103, "json-diff:declared-timing": 2}
PASS_SELECTED_FINAL_REPLAY_CLOSURE files=105 edges=30 positives=5 negatives=287 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-final-replay-closure outcome=completed
```

The deterministic receipt records **five constructed positive controls and 287
negative controls**, separately from that fresh supplier execution:

- all 105 single-file omissions and one extra output reject;
- one semantic mutation in each of all 105 outputs rejects, including all
  eleven altered logs with both corresponding receipt hashes repaired and the
  altered invoice with both consumer hashes repaired;
- valid invoice formatting, its composition with all six root-role changes and
  all 22 fresh timing changes, a coupled outer log and a generated gzip-header/
  compression change accept;
- stale invoice links (including identical malformed sides), stale coupled log
  references, six input digest faults and six role aliases reject;
- all 22 timing omissions, invalid coupled times, all 12 changed historical
  timing fields, duplicate keys, invalid replay shapes/numbers, Boolean/integer
  substitution, truncated gzip and outer-log faults reject;
- an immutable archive header change preserves decompressed tar content but
  fails the committed raw SHA-256 equality.

The semantic census is bounded: it is one mutation per output, not an
exhaustive mutation of every tree node or a formal verification of the caller.


## Limits and next questions

This is not `make frontier1094-verify`: the PR1042/#799 ancestors are not rebuilt,
and local scalar/native/phase evidence is reused from authenticated archives.
The unchanged final stage does execute its restore, bind, lift, emit, audit,
invoice, assembly, admission, bit-control and independent-T16 checks. This does
not discharge the inherited all-size/compiler, common-label, hosting,
precision/tape, exact-recovery or analytic assumptions. No stronger exponent,
formal-kernel run, hosted CI result or independent human review is claimed.

## Open next questions

Can one earlier PR1042 stage receive an equally complete portable comparison?
This matters because the final stage alone does not establish portable cold
ancestry. A feasible first step is to choose one earlier source-bound stage,
read its actual producer, and derive its complete output/reference policy.
That requires a separate overlap review and its native dependencies; it is
outside this package. Structured scope and blockers are in `TASK.json`.

## Attribution

Josie Elliston (PR1824) supplied the source-bound final-stage replay, fixture
locations and original comparison. commdata2338 (PR2040) supplied the strict
typed/path/timing comparator, its counterexamples and the Linux invoice-format
observation. Adam Gall (PR2059) supplied the authenticated three-node invoice
predicate. Both comparator source files are preserved byte-for-byte, not
presented as new algorithms here. Credit Maxime Fleury and Antoine Olivier for
the payload-versus-container convention; Rohan Arun, Jeremy Kothe, Hao Yan,
Douglas Colkitt and the retained selected supplier/compiler lineage for the
construction and review archives. All original notices remain intact.

New caller, controls and documentation prepared for Adam Gall (@adamgall) with
substantial OpenAI Codex assistance in design, implementation, experiments,
testing and writing. Apache-2.0.
