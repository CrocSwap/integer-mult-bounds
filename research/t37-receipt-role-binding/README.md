# Preserve input roles when comparing portable T37 receipts

**Scoped audit finding and verifier tooling; no new kappa.** PR1006's
[T37 bitmap adapter](../t37-slice-bitmaps/README.md) normalizes the eight
`input_sha256` paths by checking only the length and unordered collection of
hash values. Swapping the word and native-replay hashes therefore produces
exactly the same normalized receipt. This package supplies a source-bound
counterexample and an opt-in comparison that preserves each input's role while
allowing explicit path relocation. All predecessor files remain unchanged.

This is a gap in the **receipt comparison considered on its own**. The original
adapter separately checks immutable source and input hashes, executes the
pinned wrapper, and receives a freshly computed receipt. No wrong owner result
or bypass of those checks has been demonstrated. This finding does not
invalidate PR1006's occupancy proof, measurements, or accepted T37 construction.

## Exact result

The eight hashes in the pinned PR942 receipt are distinct. The checker tests
all permutations over the same eight path labels, holding every other receipt
field fixed:

| Comparison | Accepted permutations | Rejected permutations |
| --- | ---: | ---: |
| Unchanged PR1006 `common.py:normalize` | 40,320 | 0 |
| Explicit path-to-role comparison | 1 | 40,319 |

The accepted strict case is the identity permutation. The smallest nontrivial
witness exchanges `word.json.gz` and `local-replay.json`; the original concrete
labels and both before/after hashes are in [RESULT.json](RESULT.json).
The deterministic permutation transcript hash is
`93dbd107db641be1da092947244664fd815aa3df0ad2a5c1679da9ec82b3e5f1`.
This hash records the census; it does not replace executing it.

Both complete original T37 engines are then run afresh on the same pinned
archived inputs. Their entire normalized receipts agree, with **167,832 roles,
333 calls, and 14 inherited controls each**. Both also reject the new
receipt-only word/replay exchange through the strict comparator. The common
canonical receipt hash is
`1a0e4a30fc8b18c3db52cde322fc2a7646462497186cc6276e056b58253532fd`.

Five positive layout cases cover historical paths, relocated POSIX roots,
spaces and Unicode, Windows path labels, and already-logical labels. A sixth
control confirms that normalization does not mutate its caller's receipt.
Eleven rejection cases cover wrong hashes, wrong roots with the same basename,
wholly replaced labels, missing/extra inputs, ambiguous/incomplete bindings,
changed mathematical fields, omitted controls, an unfamiliar nested field,
and Boolean-to-integer changes. The test file also checks duplicate JSON keys,
nonfinite values, source drift before import, and a corrupted stored census.
Windows paths are lexical fixtures tested on Linux, not a Windows execution
claim.

## Comparison contract

Let `L` be the fixed set of eight logical roles and let `p: L -> P` be the
injective path map taken from the producing invocation. Let `h(l)` be its
independently pinned expected digest. The strict comparator requires:

1. The receipt's path-key set is exactly `P`.
2. For every role `l`, `receipt.input_sha256[p(l)] == h(l)`.
3. After replacing those labels with `l`, the complete canonical JSON receipt
   equals the pinned expected receipt.

The path map is **not inferred from receipt hashes**. Runtime maps are built
from the actual repository and materialized-input roots; historical labels are
explicitly transcribed from the pinned layout and the wrapper's argument roles.
They are treated only as strings; historical paths are never opened.
Callers must supply trustworthy invocation bindings and expected digests.
Supplying a matching corrupted binding alongside a corrupted receipt would
fall outside that contract. This is content comparison, not authentication
that a third party ran a checker.

For distinct `h(l)`, any nonidentity permutation assigns a wrong digest to at
least one role, so condition 2 rejects it. Legacy normalization depends only
on the digest multiset and therefore accepts every permutation. Conversely,
replacing the invocation paths by any other injective map and replacing the
receipt keys accordingly preserves all three strict conditions. This proves
the stated relocation property for explicit bindings; the finite controls
corroborate it. No suffix or basename matching is used.

All non-input fields are preserved. Canonical JSON serialization also
distinguishes Boolean from integer values, which Python object equality alone
can conflate. Duplicate keys and nonfinite JSON constants are rejected by the
reader. No timing, proof, or unfamiliar nested field is erased. Immutable
source/container hashes remain exact; this package does not change gzip policy.

## Reproduce

From the repository root with standard-library Python 3.12:

```sh
python3 -I -B research/t37-receipt-role-binding/verify.py
python3 -I -B research/t37-receipt-role-binding/test_receipt.py
python3 -B scripts/research_package.py --package research/t37-receipt-role-binding --check-only
python3 -B scripts/research_package.py --package research/t37-receipt-role-binding
```

The first command runs the census, controls, and both complete T37 admission
engines sequentially, then compares the entire new result with RESULT.json.
Expected final marker:

```text
PASS_T37_RECEIPT_ROLE_BINDING: 40320 legacy-equal permutations; 40319 rejected by role binding; both complete T37 engines agree
```

The package hook registers that full command plus six focused test groups.
Temporary stage outputs must be outside the checkout; the default system
temporary directory is suitable unless `TMPDIR` points inside the checkout.
`--output /absolute/new/directory` retains fresh stage evidence.
`--audit-only` explicitly omits fresh T37 execution and prints an `_AUDIT_ONLY`
marker; it is not the registered acceptance command. `--write-result` explicitly
regenerates this package's result only after a complete run. Assertions must
remain enabled for the inherited T37 engine.

The reusable functions `receipt.py:runtime_paths`, `normalize`, and `compare`
provide the opt-in comparison. Import them using a normal module loader, or
follow this package's `runpy.run_path` example. No predecessor monkeypatch or
production integration is installed by this package.

## Provenance and unchecked obligations

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
Predecessor PR1006: `2b047edb2b3fedccc4f538608b1bd56dc711673d`.
PR942 wrapper/witness: `1960cfa919a0945d0ca4cb14ea96237000037903`.
[SOURCES.json](SOURCES.json) pins 21 live inputs and two historical provenance
records by Git blob and SHA256. The predecessor's own complete source and
implementation checks still execute. No pending PR is a dependency.
[TASK.json](TASK.json) records the refined `portable-replay` card and chooser.

Fresh execution covers this one historical T37 owner-admission stage. Its
native word and native replay receipt come from pinned archives and are not
freshly rebuilt. We did not run the selected PR1094 cold replay, full repository
suite, native compiler, whole-hosted emission, invoice, moments, outer assembly,
Lean, remote CI, or another operating system/interpreter. No runtime speedup,
new supplier, new kappa, full theorem, or independent human review is claimed.
All inherited compiler, realization, hosting, precision/tape, analytic and bit
interface obligations remain. General JSON canonicalization standards and
adversarially changed expected manifests are outside this contract.

## Open next questions

Should a future maintained T37 entry point use the explicit role map when
comparing receipts? It would preserve the provenance association in saved
evidence. First integrate the pure comparator at a nonfrozen successor boundary
and retain the fresh reference/bitmap controls. Maintainer adoption and the
desired historical-layout policy are the blockers; this package does not alter
frozen code. The structured question is in TASK.json.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New work is Apache-2.0. One AI agent performed this audit; no independent human
or subagent review is claimed.

Gareth Davidson (@bitplane), PR1006, supplied the bitmap adapter and original
complete differential receipt checks. Jonathan Capalbo (@jon314159), PR942,
supplied the T37 wrapper, witness, edits and retained receipt. Chafik Boukhalfa
(@chafreaky), PR890, and Hao Yan (@FanPUYen), PR858, supplied the underlying
independent owner-checking lineage. Jeremy Kothe and the retained U8/controller
contributors supplied the local supplier and archival inputs. Their
[original notice](../t37-slice-bitmaps/NOTICE.md) remains intact.

Maxime Fleury and Antoine Olivier's
[gzip reproducibility work](../gzip-container-reproducibility/README.md)
motivated the task's comparison boundary. Joshua Snider's PR695 and Rohan
Guliani's [digest-substitution diagnostic](../pr695-digest-audit/README.md)
address different assembly provenance fields and missing historical CI
payloads. PR946 and PR1298 concern codec/platform portability, not this input
role map. This package does not repeat their results.
