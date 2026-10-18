# PR946 frozen-source migration: exact inventory and restoration replay

**Research consolidation; no new kappa.** PR946's locale/newline patch changes
bytes that historical packages deliberately authenticate. Its frozen-file
detector does not visit package-local `research/` manifests. The maintainer's
[batch952 review](../../docs/research/community-batch952-review.md) already
identified eight conflicting PR950 inputs and deferred integration. This
package makes that boundary executable and extends the provenance inventory.

The new evidence is:

- All **165** proposed paths are checked against the retained batch952 inventory
  and, in the recorded source check, the actual PR946 Git diff and blobs.
- A scan of **10,707** tracked JSON files at the exact base finds **561** literal
  references to old bytes, spanning **148** proposed paths and **99** JSON files.
  There are no parse failures. This is a bounded syntactic inventory, **not 561
  demonstrated verifier failures**.
- The unchanged PR950 verifier independently rejects **each of its eight**
  changed inputs. Restoring only the seven scripts still fails on the changed
  certificate. Restoring all eight reproduces the complete historical audit,
  including **6,760,000** coefficients, and its byte-identical original receipt.
  Neither the verifier nor its source manifest is re-pinned.

Only this new research directory is added. PR946's changes are not applied to
the production tree. The selected record at the base is Jonathan Capalbo's
PR942 T37 composition with conditional kappa **0.001661960547713947**; the
historical central-factor audit does not change it.

## One-command reproduction

Use Python 3.11+ and Git, from a clone containing the base commit and this
contribution. No Python dependencies or network calls are needed:

```sh
python -I -B research/pr946-pin-migration/check.py
```

Expected final line:

```text
PASS_PR946_PIN_MIGRATION json_files=10707 proposal_files=165 old_references=561 single_file_rejections=8 full_audits=2 coefficients_per_audit=6760000 kappa=unchanged
```

The command runs six adversarial inventory tests normally and with `-O`,
recomputes and compares every field of [EXPECTED.json](EXPECTED.json), then
runs the isolated historical replay. Full replay itself rejects optimized
Python because inherited audit assertions are required. Disposable source
closures use the current directory; `--scratch-parent PATH` chooses another
existing writable parent. No producer writes to the real `upstream/` tree.

The scanner reads immutable Git blobs at the named base, so newer working-tree
JSON cannot silently change the historical inventory. The replay instead checks
the 43 original input hashes and both adapter hashes in the checkout before
copying them. If those historical sources have changed, it fails closed; it does
not silently substitute new inputs or claim to migrate a future checkout.

To corroborate the maintainer's retained inventory directly against the proposal
commit, fetch the public PR once, then use the optional extra check:

```sh
git fetch origin refs/pull/946/head
python -I -B research/pr946-pin-migration/check.py --check-proposal
```

This option always verifies the **pinned** proposal below, even if the live PR
later changes. The default command does not require that PR object: proposed
hashes are already retained in the base, and the eight replay inputs are
included byte-for-byte under [inputs/pr946/](inputs/pr946/).

## Exact source identities

| Object | Pin |
|---|---|
| This investigation's base | `407d52ff15b2217b6e22bce44728b4c3907b6515` |
| PR946 proposal head | `b6e22dbf548d72f18b722ccb6c2ea8e3d9df6ac1` |
| Proposal parent / original submission base | `91a2094f2e022930069e8cfdc810a3ea1b81cd09` |
| PR950 historical source base | `47481c89fd30a43f8f882eb4b391e89c29273fd0` |
| PR950 original source manifest SHA256 | `cc1165946c6469f8873ad4fcf8be6698b210411c300314dde8a0319f9b1ad7df` |
| Original/restored complete receipt SHA256 | `ffae0f0a22863718e3134a924592dcf4b05e919223323ba536c587c592bfe6a1` |

The PR946 metadata in the later batch952 review uses its then-current base
`47481c89...`; that is distinct from the proposal's actual parent `91a2094...`.
The complete diff check uses the latter. EXPECTED records the exact base tree,
Git blob IDs, original/proposed SHA256 values and JSON pointers for every
reported reference. [REPLAY.json](REPLAY.json) preserves the actual execution
receipt, environment, unchanged adapter hashes and all rejection diagnostics.

## What the inventory establishes

All tracked regular `.json` files are parsed, without a filename/size filter.
The closed grammar recognizes a repository-relative proposed path as a map key
whose value is either a lowercase 64-character digest or a `sha256` record;
it also recognizes explicit `path/sha256`, `repository_path/sha256`,
`source_path/source_sha256`, and `file/sha256` records. JSON pointers preserve
the exact location. Numeric tokens are left uninterpreted, so very large
integers neither stop scanning nor become false string digests. Duplicate keys
would be reported as a parse failure rather than silently overwritten.

| Observed category | Count | Meaning |
|---|---:|---|
| Proposed paths absent at this base | 10 | New files, not old-byte migrations |
| Proposed paths with different base bytes | 155 | Actual byte differences |
| References equal to base bytes | 561 | Candidate retention/migration obligations |
| References equal to proposed bytes | 330 | Proposed-byte records, including review inventories |
| References equal to neither | 42 | Other digests; not automatically stale or erroneous |

Of the 561 old-byte references, 82 are in `certificates/`, 8 are in explicitly
named submitted/vendor archive directories, and 471 are in research/other
locations. These are **path-location categories only**, not freshness or
execution classifications. A preservation snapshot, archived certificate,
canonical-payload digest and actively consumed raw-byte pin require different
treatment. This scanner does not infer those semantics.

Three concrete manifest intersections help prioritize review:

| Manifest | Matching changed inputs | Evidence level here |
|---|---:|---|
| `research/central-factor-packed/SOURCES.json` (PR950) | 8 | Isolated source-admission failures and full restoration replay |
| `research/bit-compression-provenance/SOURCES.json` (PR970) | 5 | Exact manifest entries; no new PR970 runtime replay |
| `research/coordinated-frames-and-entrance-banks/SOURCE.json` | 136 | Exact entries; `verify_inner.py::pins` consumes the map, but unrelated historical drift may already block the package |

In particular, the PR970 intersection was not present in PR946's original
submission base. Its five paths are `audit_bit_compression.py`, `certify.py`,
`prepare_layers.py`, `search_network.py`, and `shared_point_network.py`, all
under `scripts/`. This demonstrates why the integration base matters even when
the proposed patch head is unchanged.

The grammar deliberately excludes Python/Markdown literals, dynamically built
paths, relative aliases, SHA1/Git pins, compressed JSON, and other digest-field
schemas. No absence in this inventory is a certificate of safe modification.
It does not reconstruct a complete runtime/transitive dependency graph.

## Executable source-preserving repair boundary

`replay.py` first authenticates the original 43 inputs plus two adapter files
and manifest, creating a **46-file** temporary closure. It then:

1. Runs original source admission and the complete packed historical audit.
2. Overlays each proposed input separately and demands its exact pin failure.
3. Overlays all eight; both source admission and a full-audit invocation must
   reject before executing proposed source. This is a provenance rejection,
   not a mathematical counterexample to the proposed generators.
4. Restores all seven scripts but leaves the proposed certificate; rejection
   must persist. Generator-only retention is insufficient.
5. Restores all eight original byte sequences and repeats admission and the
   complete audit. The original receipt digest and every closure file must
   match exactly. The three package authentication files never change.

For PR950 this gives a concrete migration option: retain the **whole historical
source namespace**, including the certificate, when later production encoders
change. Editing expected digests alone would authenticate different evidence;
it is not the repair demonstrated here. A future integration may instead
revalidate a new closure, but that requires its own complete replay and receipt.

For the other inventory entries, inspect the consuming code and distinguish
historical preservation from active validation before choosing retention or
revalidation. Applying the 165-file patch, migrating all consumers, rerunning
the broad verification suite, and fixing PR946's detector remain outside this
contribution. The package is not approval to merge PR946.

## Scope, validation and credit

The assignment seed was **95**, drawn from OS randomness as recorded in
[CLAIM.json](CLAIM.json). The bounded experiment covers exactly the named
proposal and base; it performs no mathematical search. There is no impossibility
claim or finite-replay-as-formal-proof claim. All-size/compiler, realization,
hosting, precision/tape and analytic assumptions of the selected result remain.

Validation passed on Windows with Python 3.14.5: the complete command including
direct proposal-blob comparison, six tests under both assertion modes, and
`python -I -B scripts/verify_selected_result.py`. The existing interpreter emits
a nonfatal location diagnostic, retained in the raw replay receipt. No Linux CI
pass, whole-repository `make verify`, or fresh selected-construction cold replay
is claimed. Those expensive checks were not repeated for this additive evidence
package.

See [NOTICE.md](NOTICE.md) for predecessor attribution and substantial AI
assistance disclosure. The known eight-input finding belongs to the maintainer
review; the extension here is the exact wider inventory and reproducible
per-input failure/restoration evidence, not a priority claim for that finding.
