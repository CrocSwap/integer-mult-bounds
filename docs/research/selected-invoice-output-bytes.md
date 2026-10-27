# Selected invoice output must match its receipt

Task: `portable-replay`, scope key `91a9a2afec282c926282`, priority revision 8.
Base: canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`.
Picker nonce: `2277cf1571f1c73ee079fef4f1dcec88`; verifier engineering was selected
for the available native Windows environment. Scope status: **changed** from
the suggested gzip/canonical-payload audit to the current selected-invoice
exporter's exact output binding. The concrete failure below makes this a useful
environment repair under the same card's question.

## Reproduced failure

Ali Romman's PR #5735, head `4ecfa15596c47d243f86bedd7e3d353dd909d086`,
introduced the authenticated P104 invoice exporter. Its evidence promises the
hash of the exact emitted invoice bytes. On Windows 11 build 26300, CPython
3.12.10, the exporter successfully authenticates the selected inputs but
`print()` translates the serialized invoice's LF bytes to CRLF. The receipt
hashes the untranslated UTF-8 serialization instead.

At the base commit, a binary `subprocess.run(..., capture_output=True)` capture
of `python -I -B scripts/export_selected_invoice.py --evidence EVIDENCE.json`
has 44 CRLF line endings and SHA-256
`1da7c82224c8bd2c1e31ccc171a4d2a12bdf7a340eafcb8499fd2be5667d8eff`.
The evidence's `invoice_sha256` is
`ad826c829c11ae3193736ad2df3310081809ab6cdcd194346065bd97f943e4c1`.
Replacing CRLF with LF recovers the latter hash. The invoice values themselves
are unchanged. The existing integration test used `text=True`, which normalizes
newlines before hashing, and therefore concealed this transport mismatch.

## Bounded repair and verification

The repaired raw stdout bytes hash to the receipt and remain a valid input to
the existing invoice comparator. One serialization supplies both hashing and
binary stdout, preserving the existing UTF-8 JSON format and terminal LF.
Source hashes, accounting predicates and scientific inputs remain
unchanged. This is an output-binding repair, not a supplier replay or new kappa.

The updated integration test captures the real subprocess bytes and uses those
same bytes as comparator input. A separate transport regression exercises LF,
CRLF and UTF-16 text wrappers on any host. Before the repair, its CRLF and UTF-16
controls fail; afterward all three pass. The original independent path-length
count, charge/debit omissions, chronology, ownership and source-corruption
controls remain active.

Executed on the native Windows environment above:

```sh
python -B scripts/research_selected_baseline.py
python -B tests/test_research_selected_invoice.py -v
python -I -O -B tests/test_research_selected_invoice.py -v
python -B tests/test_compare_recursive_invoices.py -v
git diff --check
```

The baseline reports `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. All eight exporter
tests pass in both modes (34.408s / 33.545s), and all ten comparator tests pass
(0.352s). These are observations, not a performance comparison. The unchanged
complete invoice still has 66,726 paid calls, 13,048 productive fields and rank
surplus 760. The repaired raw stdout hash equals the original receipt's
`ad826c...f4c1` value above.

The first suite attempt hit a sandbox temporary-directory permission failure
while copying the source fixture. Setting `TEMP` and `TMP` to an existing
workspace scratch directory allowed the same test to run; no source or test
predicate was relaxed. No cold mathematical replay, hosted-CI success or POSIX
execution is claimed.

## Scope and overlap

Read AGENTS.md, autoresearch.md, CONTRIBUTING.md, current priorities, selected
record/review and family guidance from the base. The selected binding-only
baseline passed after materializing its exact inputs. Checked the handoff hub
#1166 and active Discussions before choosing the card; no suitable uncovered
exporter request was found in the visible recent entries. The repository
overlap helper reported incomplete sparse-local coverage and no remote cache.
A separate four-page GitHub API scan covered 391 open PR titles/bodies,
including drafts, and found no `export_selected_invoice`/invoice-stdout repair.
Discussion text searches were unavailable through the web reader; coverage is
bounded, not a claim of exhaustive novelty.

Before publication, canonical main was fetched again at 2026-10-27 04:44 UTC:
it remains the base above, with unchanged priorities and relevant sources.
Fresh targeted open/closed PR searches found no matching repair. In particular,
PR #5733's separate invoice-composition CLI already uses binary stdout and does
not repair this exporter.

PR #5721 concerns Git descendant ownership. PR #2477 concerns authenticated
historical replay logs, and the strict replay-payload comparison package covers
typed JSON/relocation equivalence. Their fixes are not repeated here. This
repair concerns the current exporter's own promised byte digest.

## Credit

Retain Ali Romman's exporter and tests, Pierre-Loic Doulcet's P104 word, Cinna
Davis's controller, Jacob Alan Sussman's productive recursion, zxv's invoice
interface and all retained source credits. This repair is prepared for
josecarlosgonzalezroque-design with substantial OpenAI Codex assistance, one
agent; author-checked, not independently reviewed. Apache-2.0.

## Open next questions

The next useful check is the same raw-byte CLI test on POSIX or another Windows
Python version. This host supplies native Windows evidence and portable wrapper
controls, not an executed POSIX claim. Downstream shells that themselves decode
and rewrite captured output remain outside the exporter's byte-stream contract;
consumers should compare the receipt to the bytes actually retained. No further
construction or frontier change follows from this repair.
