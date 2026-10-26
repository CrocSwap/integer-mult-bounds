# Overlap receipt for the fourth100 witness-MANIFEST pin family

Scope key `757723e3fd38f20fa774` (`overlap-receipt`, consolidation track,
priority revision 3, chooser nonce `6bc45fb7886eb99e0494a94781da0e58`),
**refined** to one small named PR set: the seven entries of the fourth100
reconciliation whose contributed-package replay fails at `verify.py` line 39
with `AssertionError: larger_gain manifest pin` —
[#636](https://github.com/CrocSwap/integer-mult-bounds/pull/636),
[#638](https://github.com/CrocSwap/integer-mult-bounds/pull/638),
[#639](https://github.com/CrocSwap/integer-mult-bounds/pull/639),
[#640](https://github.com/CrocSwap/integer-mult-bounds/pull/640),
[#642](https://github.com/CrocSwap/integer-mult-bounds/pull/642),
[#644](https://github.com/CrocSwap/integer-mult-bounds/pull/644)
(vectorsss / Chi Zhao) and
[#646](https://github.com/CrocSwap/integer-mult-bounds/pull/646)
(jeremydiviney). Base main `1f7a934975e5eacaf83511c9ac870263bf095e05`.

This is a source-bound disposition receipt: a finite certificate of git-blob
identities and one diagnosed source-pin defect. It is **not** a kappa claim, a
construction, or a mathematical result, and it changes no disposition: the
seven PRs stay open, the selected frontier is unchanged, and no closure is
requested.

## What was audited

The existing receipt under audit is the fourth100 reconciliation
(`research/community-reconciliation-fourth100-audit/`,
`docs/research/community-reconciliation-fourth100-review.md`) as recorded in
`docs/research/pr-ledger.json`, which leaves all seven with the identical
unresolved question "Required contributed-package replay has not completed
successfully" and identical evidence text
`AssertionError: larger_gain manifest pin`. For each recorded head I checked
(a) the source-pin block of the package's own `verify.py` (lines 36-42: package
MANIFEST tree, each pinned source's `MANIFEST.json` pin, and each pinned file)
against the exact bytes committed at that head, and (b) the byte-retention of
every changed path against main's tree at the base commit. Method: exact
git-blob identity only (SHA256 of raw bytes for pins, blob SHAs for retention);
no heuristic matching. The fetching side is `tools/audit_witness_pins.py`, the
receipt builder is `tools/build_receipt.py`.

## Findings

**F1 — the seven failures share one cause: a drifted `larger_gain` pin.** All
seven SPECs register `larger_gain` with
`manifest_sha256 = 54d67f45ad520f4a134e069336bd0ff639aaeada28d13539298e4f2655c9692d`,
which is exactly `research/larger-gain/MANIFEST.json` at the pinned PR569
revision `897213a855b7fb8a1b8b0e552a2f5c42e6c1b326`. The same path **as staged
into main** (commit `df417acd`, "Stage frozen PR family through 588") hashes
`73c186c2807c703e43293c7cf785557a046958c245fa812e433f7fe208cdef6d`, and this
drifted copy is what every one of the seven recorded heads carries in its base
tree (checked at each head). The two manifests differ in exactly two `files`
entries: `NOTICE` and `README.md` (both 64-hex digests changed; byte length
40,559 in both). The staged package is self-consistent at its own revision:
main's `NOTICE` and `README.md` hash to the staged manifest's values, not to
PR569's. The other five pinned sources (`multicold`, `structural_gain`,
`joint_prefix`, `frame_coalescing`, `direct_delivery`) still match their pins in
the live repository packages.

**F2 — the six vectorsss packages vendor the pinned revision byte-exactly.**
For #636/#638/#639/#640/#642/#644, each source pin resolves to the package's
own `vendor/<name>/MANIFEST.json`, and every one matches its registered
`manifest_sha256` in raw bytes (zero CRLF bytes anywhere, so the repository's
text normalization is not involved). All their pinned files match too. Run
through their own `verify.sh` source overrides, these six pass the pin block
that the reconciliation recorded as failing; they evidently ran with the
sources resolved to live repository packages (as #646's defaults do), where
`larger_gain` is the first pin that fails. #646 has no vendored copy at all:
its `verify.py` defaults resolve `larger_gain` to the live
`research/larger-gain`, which reproduces its failure on any checkout of main.

**F3 — retention is partial, and dominated by re-vendored predecessor
content.** Against main's tree at the base commit (exact blob identity):

| PR | changed paths | byte-retained in main (other path) | not byte-retained |
|---|---:|---:|---:|
| #636 | 348 | 285 | 63 |
| #638 | 347 | 281 | 66 |
| #639 | 340 | 281 | 59 |
| #640 | 339 | 282 | 57 |
| #642 | 354 | 281 | 73 |
| #644 | 355 | 280 | 75 |
| #646 | 186 | 77 | 109 |

No path matches at the same path, and no path exists in main with different
content, so retention is entirely "same bytes at a different path": the
vendored copies of the six pinned source packages already live in main under
their own `research/` directories. The unretained remainder is each package's
own witness, tools, data and result files (listed path by path in
`evidence/pr{N}-audit.json`).

**F4 — the six vectorsss members share their vendored core with each other**
(250-268 shared blobs pairwise; #646 shares 31-33 with each). A reviewer can
treat the six as one content family plus six small per-PR deltas.

**F5 — predecessor credit is present.** `CONTRIBUTORS.md` credits vectorsss for
#636/#638/#639/#640/#642/#644 (line 835) and jeremydiviney for #646 (line
833). No missing attribution was found for this family; the downstream
incorporated work that credits vectorsss's owner-search methods (e.g. #654,
#671, #676, #699) is separate and unaffected.

## Reproduction

```sh
python3 -B research/pr636-family-witness-manifest-receipt/verify.py
python3 -B scripts/research_package.py --package research/pr636-family-witness-manifest-receipt
```

`verify.py` is offline and standard-library only. It recomputes the drift
identity from the two committed MANIFEST copies (and against the working tree's
`research/larger-gain/MANIFEST.json`), re-derives every pin verdict and every
retention class from the per-PR audit rows against `git ls-tree -r <base>`,
recomputes the cross-PR shared-blob counts, runs a positive fixture of the
classification rule, and runs four failure controls (tampered digest,
substituted manifest diff, omitted row, substituted class) that must each be
rejected. The evidence copies under `evidence/` are byte-exact unmodified
copies of two `MANIFEST.json` revisions, kept so the digests are checkable
without network access.

## Limitations (not checked)

- Head-side blob identities rest on the GitHub pulls/contents APIs at the
  recorded head SHAs; the seven PR trees are not fetched into the reviewer's
  git, so `verify.py` re-derives the main-tree side only.
- The `multicold` sources declare `full_tree: true`; their whole-tree manifests
  were not recomputed file by file (the recorded failure is earlier, at the
  `MANIFEST.json` pin).
- The seven packages' full contributed replays (construction, owner search,
  admission) were not executed. This receipt resolves the recorded pin failure
  and the retention/credit question only.
- That the fourth100 harness resolved sources to live packages is inferred
  from the uniform `larger_gain manifest pin` assertion plus the pin data; the
  harness's exact invocation was not recorded in the ledger.
- Retention matching is byte identity. Content rewritten equivalently would be
  reported as not retained; no such case appeared at these paths.

## Open next questions

1. **What did the fourth100 harness actually pass to `verify.py`?** It matters
   because the six vectorsss packages pass their pin block via their own
   `verify.sh` overrides, so their ledger questions may be resolvable by a
   re-run rather than a content fix. First step: re-run #636's `verify.sh` pin
   block (`--check-pins`) in a byte-preserving checkout of its recorded head
   `679621828a85bac68af869fb0e55b54508e6b14b`. Blocked by: the recorded
   traceback stops at the assertion and does not record the harness's source
   resolution.
2. **Should the `larger_gain` pin drift be reconciled in main?** The staged
   `research/larger-gain` package is self-consistent but is a later revision
   (NOTICE/README.md changed) than the pinned PR569 revision that all seven
   packages register; every live-package resolution fails until someone either
   re-pins or vendors the pinned revision. First step: confirm with the
   maintainers whether `df417acd`'s NOTICE/README.md rewrite was intentional
   (it looks like license/attribution staging) and then update the seven SPECs
   or restore the pinned revision. Blocked by: maintainer decision on pin
   policy; this receipt does not change any pin.
3. **Is any of the unretained content worth retaining for reuse?** The 57-109
   unretained paths per PR are mostly per-package witness outputs; a bounded
   follow-up could classify them into method code worth retaining versus
   generated evidence. First step: classify the `not_retained` lists in
   `evidence/pr{N}-audit.json` by extension and directory. Blocked by: nothing.

## Credit and attribution

Predecessor authors: vectorsss / Chi Zhao (#636/#638/#639/#640/#642/#644) and
jeremydiviney / Jeremy Diviney (#646); the fourth100 reconciliation authors
for the audited receipt and recorded evidence; the PR569 (`larger_gain`)
authors and the `df417acd` staging authors for the two manifest revisions
compared here. The receipt follows the source-retention receipt style of
[#1572](https://github.com/CrocSwap/integer-mult-bounds/pull/1572) (PR148),
which audited a different family.

Prepared by Aaron Wang / navinor with help from opencode. Substantial AI
assistance is disclosed; no independent human review is claimed. Apache-2.0.

## Explicit historical-only registered replay

The registered command now authenticates and replays the original package at
`20ecf2891d80b5acf18d980b2164fb44ea7faa90` against its original pinned base.
It does not validate today's ledger, contributor list, or other live input
bytes. The original SOURCES.json, VERIFY.json, verifier and evidence are read
unchanged from that commit into an isolated temporary tree. Current source
rows keep their exact original commit/blob/SHA256 pins as historical provenance.

Only these three wrapper files (README.md, SOURCES.json and VERIFY.json) may
differ from the frozen package, and the adapter checks their exact approved
transformation. All current verifier and evidence bytes must still equal the
original tree. The original positive and negative controls run without edits;
materialized and live package/input files must remain unchanged afterward.
`PASS_HISTORICAL_RECEIPT_ONLY` is a historical source/credit result, not a
current-state validation, new scientific acceptance, or closure decision.

Run the historical adapter with Python 3.12:

```sh
python3 -B scripts/replay_historical_receipt.py --package research/pr636-family-witness-manifest-receipt
```

The generic runner's default live-input contract is unchanged. To inspect the
original live contract, replay the original frozen package metadata against live
inputs: it correctly rejects later byte drift. The registered wrapper declares
the adapter and its focused tests as inputs, so changes select these two
consumers without a global shared-workflow invalidation. See
[the replay guide](../../docs/research/research-package-guide.md#historical-sourcecredit-receipt-adapters).
