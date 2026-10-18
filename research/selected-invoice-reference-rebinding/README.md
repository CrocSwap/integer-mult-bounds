# Authenticate invoice references before portable comparison

**Verifier engineering; an opt-in three-node comparison, not mathematical
admission. No new supplier, physical claim, paid profile or κ.** This closes the
explicit invoice-reference handoff in [PR2040](https://github.com/CrocSwap/integer-mult-bounds/pull/2040)
without editing a frozen caller or any selected source.

## Result and concrete scope

The reviewed PR1094 strict-output corpus has **105 files**. Its generated
`global/audit/PREFIX-AND-INVOICE.json` has exactly **two direct raw SHA-256
references** in that corpus:

- `ADMISSION-CONTROLS.json#/input_sha256/fresh_invoice`;
- `ASSEMBLY.json#/input_sha256/fresh_invoice`.

The census inspects every plain/gzip JSON payload and every decompressed file's
literal digest occurrences, including logs. Both the count and the precise
locations are checked, not inferred from filenames. The actual input is the
raw-hash-pinned `community-frontier1094-audit/selected-replay.tar.gz`; its archived
assembly is also byte-equal to the selected committed certificate and bound by
the archived and committed `RESULT.json`.

PR2040 reports that Linux reordered invoice object keys: the invoice raw digest
changed from `212cf4ee…0d12` to `e3fc03bf…6ca2`, and both references changed with
it. Its strict comparator intentionally flags those references and leaves their
source-bound normalization open. **That Linux observation is predecessor
attribution, not a platform run performed here.** Our experiment constructs a
format-only variant of the authenticated invoice, updates both literal raw
references, and independently establishes complete typed payload equality. On
this fixture the retained PR1824 comparator calls the invoice `json-format` but
flags each consumer `proof-relevant-candidate`, with exactly one differing field.
The new predicate accepts this valid graph without ignoring either reference.

| Authenticated artifact | Bytes | Tree nodes | Contents retained |
| --- | ---: | ---: | --- |
| Invoice | 78,165 | 2,649 | Every field, list position, scalar and empty container |
| Admission controls | 4,184 | 96 | Every field; the one validated invoice edge is rebound |
| Assembly | 85,147 | 296 | Every field; the one validated invoice edge is rebound |
| **Total** | **167,496** | **3,041** | No timing/path/digest-name exemptions |

`compare_invoice.py` is deliberately limited to these three named artifacts.
It is **not** a replacement for a full-output comparator, a new production
acceptance rule, a supplier replay, or a validator of all other digest edges.
The unchanged external references remain exact strings in the comparison. Its
CLI reads these three paths below each `strict` directory; other files are out
of scope. The Python API requires an exact three-file mapping.

## Exact predicate and why no field disappears

Let `I` be the invoice bytes, `R₁,R₂` the two consumer bytes, `H` SHA-256, and
`C` the complete canonical encoding of parsed JSON. The accepted domain is the
reviewed JSON tree grammar: objects with unique string keys, arrays, strings,
integers, Booleans and null. Decimal/exponent number tokens, nonfinite values,
and duplicate keys **reject**, rather than falling back to binary64 or treating
`true` as `1`. All three actual artifacts lie within this domain. Numbers in
rational/decimal **strings** remain exact strings.
Integers compare by exact parsed value (thus `-0` and `0` denote the same
integer), not by the spelling of their source token.

For **each side separately**, before performing any equality shortcut:

1. Parse all three files and require object roots.
2. Require **both** `Rᵢ.input_sha256.fresh_invoice = H(I)` as literal strings.
3. Form `C(I)` with sorted object keys, fixed separators and escaped strings.
4. In each freshly parsed consumer, replace exactly that authenticated edge
   value with `H(C(I))`; retain every other key and value.
5. Compare `C(I)` and both complete rebound consumer encodings **by bytes**
   against the corresponding reference encodings. Digests in the report are
   receipts; they do not replace those three byte comparisons.

**Critical proof step.** On this grammar, canonical JSON is injective modulo
object-key order, insignificant whitespace and equivalent JSON string escapes:
the JSON grammar distinguishes each scalar type, preserves every object key and
array index, and the serializer retains every value. Thus invoice equality
implies equality of the entire invoice tree, not only its status, κ or hash.
Only after the literal raw links have authenticated on both sides is their
representation changed. If the invoice payload changes, its byte comparison
fails even when both raw links are consistently updated. If either link is
stale, normalization is never reached. For equal invoices, the two substitutions
are equal; complete consumer comparison then checks every remaining field.
SHA-256 collision resistance is the inherited assumption for authenticating raw
links and immutable inputs, not a claim of universal mathematical injectivity.

The independent oracle does **not** use this serializer or the canonical digest
as its expected identity. It recursively tags every value by type, includes all
keys/positions/empty containers, and represents each authenticated edge as the
explicit tuple `("edge", invoice_path)`. The primary projection must agree with
the full original oracle tree after these two role substitutions. A focused
oracle-fault control deletes `provider_phase_semantic_sha256` and detects the
loss. This is a written argument plus executable evidence, not a formal kernel
proof of Python or JSON.

## Evidence and semantic controls

[`RESULT.json`](RESULT.json) is deterministic and contains the complete source
census, raw/canonical hashes, type counts, positive-witness hashes, before
classifications, per-artifact negative counts and a reproducible mutation
transcript SHA-256. The transcript covers the declared full enumeration, not a
random sample:

- **6,076 field mutations:** omit and replace each of the 3,038 nonroot tree
  nodes once. This includes all nested objects, array positions, receipt fields,
  known and unknown digests, proof values, and empty containers.
- **5,296 of those mutations change the invoice** and then correctly update
  **both** consumer raw links. Every one still rejects. This is the crucial
  difference from unvalidated whole-file hash substitution.
- **57 further negatives:** stale links, just one repaired link, links misbound
  to `owner_audit`, identical stale graphs, duplicate keys, nonfinite or decimal
  tokens, missing files, unfamiliar fields, and all **27 Boolean-to-integer**
  substitutions in these artifacts. **6,133 negatives total.**
- **Seven positive controls:** identical valid input; sorted/compact invoice;
  recursively reversed object order; an equivalent string escape; each consumer
  reformatted independently; and all three reformatted together. Every invoice
  format change carries freshly authenticated links. List order is never free.

Eight focused tests additionally cover CLI exit status (0 equivalent, 1 different,
2 invalid/missing), both-side edge validation, the independent oracle, precise
number/type handling, and immutable-source handling. The source-header control
changes only the pinned archive's gzip MTIME byte, proves its decompressed tar
unchanged, then requires **raw source-pin rejection**. Generated JSON formatting
permission is never applied to immutable source archives.

## Reproduce

CPython 3.12 standard library, from the repository root:

```sh
uv run --python 3.12 --no-project python -I -B research/selected-invoice-reference-rebinding/verify.py
uv run --python 3.12 --no-project python -I -O -B research/selected-invoice-reference-rebinding/test_compare.py
uv run --python 3.12 --no-project python -B scripts/research_package.py --package research/selected-invoice-reference-rebinding
```

Expected direct marker:

```text
PASS_SELECTED_INVOICE_REFERENCE_REBINDING files=105 nodes=3041 edges=2 positives=7 field_mutations=6076 synchronized_invoice_mutations=5296 negatives=6133 no_new_kappa
```

The first-generation experiment (`verify.py --write-result`) completed in
17.14 seconds including the uv launcher on macOS arm64, CPython 3.12. It refuses
to overwrite a result. Ordinary replay writes only temporary before-comparison
fixtures and compares the **complete** generated receipt against `RESULT.json`.
No archive is regenerated; no network, native compiler or third-party package is
used. This is not a replay-runtime/speedup claim.

Final focused verification on **CPython 3.12.12** ran the direct audit, all eight
tests under `-I -O -B`, the metadata/pin check, then the registered replay in one
serial batch (**31.45 seconds** including launchers). Every command passed;
the registered replay repeated the audit and eight tests, ending with
`PASS_REGISTERED_RESEARCH_PACKAGE research/selected-invoice-reference-rebinding outcome=completed`.
The focused test runs took 0.298 and 0.299 seconds. No remote CI was run or claimed.

To compare two already-produced strict directories:

```sh
python3.12 -I -B research/selected-invoice-reference-rebinding/compare_invoice.py REF_STRICT RUN_STRICT
```

The CLI establishes equivalence/integrity of these three nodes only. Its caller
must trust its reference independently. The registered verifier supplies that
trust through the immutable archive pins; it does not infer mathematical truth
from self-consistent hashes. The chosen card's first working example,
`research_baseline.py`, returned `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` at the
unchanged selected κ `0.001672660197076918` before the experiment.

## Provenance, overlap and limits

Base: `e112d71c8d7bb32435debcc54df932593dd8223a`. The chooser was run exactly
once without overrides; complete seed/cards are in [`SELECTION.json`](SELECTION.json),
seed `a2e5a793b5e1a2555a2466367171c2ea`. The refined scope and full optimistic
engineering acceptance budget were written in [`TASK.json`](TASK.json) before
substantial computation. [`SOURCES.json`](SOURCES.json) pins exact Git blobs and
raw SHA-256; [`VERIFY.json`](VERIFY.json) registers all live external inputs.
Claim: [discussion2049](https://github.com/CrocSwap/integer-mult-bounds/discussions/2049#discussioncomment-18931179).

Nearest work and distinctions:

- PR2040, head `d31c1418c0c23994d1444dbd9d356b9a8238fd5e`, establishes typed/path
  false equivalences and explicitly hands off invoice reference rebinding. This
  contribution consumes no unmerged PR2040 code or unverifiable Linux payload.
- PR1824, head `ad5b1248f25a71983b20617e2f3a80be22f03990`, supplies the retained
  before comparator. We do not weaken its frozen expectations in place.
- [Selected generated identity audit](../selected-generated-identity-audit/README.md)
  covers seven **different local artifacts**, not these invoice consumers. Its
  underlying `generated_identity.py` is precedent for authenticate-then-rebind;
  that source remains unchanged and its attribution pin is retained.
- [PR695 digest audit](../pr695-digest-audit/README.md) warns that propagating a
  hash alone can hide semantic change. Here all invoice fields are present and
  compared, including 5,296 synchronized-mutation rejections. We make no claim
  about its unavailable historical CI payloads or different template graph.

The shared overlap snapshot covered 329 open PRs including drafts (18:11:09Z)
and 692 discussions with comments/replies (18:12:32Z), complete pagination on
2026-10-14. Exact `rebinding` search, local/merged predecessors and PR2040's live
body/head were inspected. The final targeted check confirmed PR2040 still open
at the pinned head and PR1824 merged at its pinned head (2026-10-14 16:34:44Z).
The repeated cached query added only this package's README/TASK to its prior
matches. Cached coverage can miss later changes; no-match is not novelty.
No older contribution has been resubmitted.

Not established: all-output equivalence, a Linux/Windows run, a full cold
supplier replay, production adoption, mathematical admission, improved κ, any
all-size/compiler/hosting/precision/analytic discharge, or GitHub CI success.
This package does not modify the selected record, source archives, shared indices
or predecessor code. Decimal JSON tokens outside the actual grammar fail closed;
a future format requiring them needs a separately reviewed exact extension.

## Open next questions

Should a future selected-final-stage wrapper adopt this predicate? This matters
because it supplies the missing source-bound handling of the two raw invoice
references. The feasible first step is to compose it with a separately reviewed
full-output comparator and explicit per-field time/path policy, then replay that
whole caller. **Blocked by maintainer adoption and caller/source-pin review, not
by an assertion that the remaining graph is already certified.** The structured
question is in `TASK.json`.

## Credit and license

Credit Josie Elliston (@JosieElliston, PR1824), commdata2338 (PR2040 and its named
handoff), Maxime Fleury and Antoine Olivier (gzip reproducibility convention),
Rohan Guliani and Joshua Snider (PR695 diagnostic/warning), Adam Gall's earlier
local generated-identity audit, and the retained selected supplier/compiler
lineage including Rohan Arun, Jeremy Kothe, Hao Yan and Douglas Colkitt. Exact
selected source head: PR1094 `0fc329d0bec93ca7cd288eaea1295172e8789810`.

Prepared for Adam Gall (@adamgall) with **substantial OpenAI Codex (GPT-6 Astra)
assistance** in design, implementation, experiments, tests and writing. No
independent human review claimed. New work is Apache-2.0; all predecessor files
and notices are unchanged.
