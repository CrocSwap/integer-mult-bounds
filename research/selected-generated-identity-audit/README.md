# Selected-lineage generated-identity field audit

**Exact bounded audit; no defect found, no repair and no new kappa.** The
seven-artifact projection in
[`gauge44-slots-t16/code/generated_identity.py`](../gauge44-slots-t16/code/generated_identity.py)
retains all proof-relevant fields of the reviewed `slots/local` input. Its sole
field exclusion is the root `CLIFFORD-REVIEW.json#/seconds`; four raw file
references are checked before being replaced by content identities. This
package changes no predecessor, immutable archive, source pin or selected record.

## Concrete result

The input is the seven `slots/local/` members of
`community-frontier1042-audit/selected-replay.tar.gz`, authenticated by the
archive's exact SHA-256 and the corresponding `RESULT.json` member hashes.
This is the actual R480 selected local input inherited by PR1094, **not** the
historical R492 `gauge44-slots-t16/evidence/local/` directory. The earlier
[selected1042 lineage resolution](../selected1042-lineage-resolution98/README.md)
established this distinction. The audited implementation's hash is also checked
against PR1094's retained selected-source manifest.

| Artifact | Retained tree nodes | Identity domain |
| --- | ---: | --- |
| `CANONICAL-WORD.json.gz` | 152,706 | All 492,283 decompressed bytes |
| `LOCAL-PROGRAMS.json.gz` | 572,575 | All 2,084,018 decompressed bytes |
| `LOCAL-CHECKS.json` | 31 | Complete canonical JSON |
| `INDEPENDENT-LOCAL-REPLAY.json` | 63 | Complete reference-rebound canonical JSON |
| `CLIFFORD-RECIPES.json` | 211,459 | Complete canonical JSON |
| `CLIFFORD-REVIEW.json` | 16 | Complete reference-rebound JSON except root time |
| `RESIDUAL-ADAPTERS.json` | 2,753 | Complete canonical JSON |
| **Total** | **939,603** | |

The original trees contain 939,604 nodes. Exactly one node, root phase time,
is removed. Nodes include every object, array and scalar; the census records
object keys and list positions, not merely leaf counts. `RESULT.json` retains
per-artifact type counts, typed-path transcript hashes and artifact identities.

There are **155 receipt mutation cases**: omit and replace each nonroot node
of both receipts (124 native and 31 phase), except the deliberately permissible
replacement of valid root phase time. This includes all four raw-reference
slots, both orientation profiles, arbitrary-dirty column counts, charged bits,
private-work restoration, every negative-control entry, phase ranks, adapters,
status and scope. All 155 reject. The package does not describe this as 939,603
separately executed mutations: full-tree identity coverage and the receipt
mutation census are distinct evidence.

There are **181 negative controls in total**, including stale references after
recompression/reformatting, Boolean-to-integer changes, unfamiliar nested
`seconds` fields, invalid timing, one omitted root field in each artifact with
references correctly rebound, decompressed serialization drift, and truncated
gzip streams. **Nine positive controls** accept the complete independent
identity oracle, three valid root timings, four alternate gzip containers and
reformatted plain JSON with an updated raw recipe reference.

## Independent oracle and exact boundary

The oracle does not call the audited canonicalizer or `json.dumps` to construct
an expected identity. It recursively encodes all dictionaries, lists, strings,
integers, Booleans and nulls, with its own JSON string escaping and sorted object
keys. Its supported domain is the actual retained data: the only input float is
the excluded root timing. Unexpected retained floats fail rather than silently
borrowing the primary serializer. This is not a general-purpose JSON library.

For each of the five plain JSON artifacts, the independently encoded **entire
expected tree** hashes to the actual primary identity. For each gzip artifact,
the entire decompressed byte string hashes to its primary identity; parsing is
used only for the additional tree census, not to relax byte equality. For both
receipt projections, an independent typed-path traversal also compares the
expected and actual projected trees. It distinguishes `true` from `1`, retains
empty containers, and includes every key and index. A focused oracle-fault test
removes the global-phase field from the returned phase projection and requires
this independent tree check to reject it.

The exact transformation is:

1. Keep each plain JSON value, including unfamiliar fields, in full.
2. In phase review only, require a finite nonnegative `int` or `float` time
   (not `bool`), then remove its root `seconds` field.
3. In native replay, require the literal canonical-word and local-program hashes
   to match the current files, then replace them by full decompressed hashes.
4. In phase review, require its canonical-word and recipe hashes to match the
   current files, then replace them by the decompressed-word and canonical-recipe
   hashes respectively.
5. Hash the resulting complete canonical JSON trees.

The reference fields are **rebound, not erased**. Under the ordinary SHA-256
collision-resistance assumption, the two payload identities bind all their
bytes. Recursive canonical encoding binds the complete retained JSON trees;
only key order/whitespace and the declared timing/reference representation
changes are quotiented out. This is a statement about these authenticated inputs
and this pinned implementation, not universal injectivity of SHA-256 or every
possible JSON parser. The audit's fixture reader rejects duplicate keys and
nonfinite constants; it does not claim the inherited reader generally does so.

The plain-JSON reformatting allowance belongs to the identity function. Caller
checks may impose additional byte pins, so these controls do not claim that the
complete production binder accepts every reformatted artifact.

**Generated versus immutable:** alternate containers are created only in a
private temporary directory. The original archive and implementation remain
exact raw-hash inputs. A separate test changes only the immutable archive's gzip
MTIME byte and requires source-pin rejection. Recompression permission is never
applied to an immutable source archive. Invalid/truncated streams are not
silently treated as payload equality.

## Reproduce

Python 3.12 standard library; run from the repository root with assertions enabled:

```sh
python3.12 -I -B research/selected-generated-identity-audit/verify.py
python3.12 -I -B research/selected-generated-identity-audit/test_audit.py
python3.12 -B scripts/research_package.py --package research/selected-generated-identity-audit --check-only
python3.12 -B scripts/research_package.py --package research/selected-generated-identity-audit
```

With a uv-managed interpreter, prefix commands with
`uv run --python 3.12 --no-project` and use `python` in place of `python3.12`.
The direct marker is:

```text
PASS_SELECTED_GENERATED_IDENTITY_AUDIT nodes=939603 receipt_mutations=155 positives=9 negatives=181
```

The initial exact experiment used CPython 3.12.12 on macOS arm64 and completed
in 5.85 seconds including the launcher. The default command writes nothing in
the checkout. `--write-result` is an explicit first-generation option that refuses
to overwrite an existing result. `VERIFY.json` registers the direct replay and
five focused test groups. There are no third-party or native dependencies.

## Overlap, attribution and limits

Base: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. Source hashes and Git blobs are
in `SOURCES.json`; the chosen card, recorded scope and exact overlap heads are
in `TASK.json`. The local task card was written before the substantive experiment.
Parent coordination is [discussion 1884](https://github.com/CrocSwap/integer-mult-bounds/discussions/1884).

Final focused verification used the direct command, `--check-only`, and the
registered package command above in one phase on the same interpreter. All
passed in 16.05 seconds combined in the publication recheck. The registered
command replayed the exact result and ran all five focused tests (`Ran 5 tests in 3.892s`, `OK`), ending
with `PASS_REGISTERED_RESEARCH_PACKAGE research/selected-generated-identity-audit outcome=completed`.

The publication overlap recheck used the shared cached snapshot offline: 543
open PRs (including drafts, complete pages, 2026-10-14 13:23Z) and 529 discussion
records (complete pages, 13:25Z). It may miss subsequent changes. Targeted live
queries confirmed PR1559 and PR1824 remained open at the heads below.
The full nearby PR bodies and relevant local notes were read:

- [PR1559](https://github.com/CrocSwap/integer-mult-bounds/pull/1559), head
  `c4f8af1dcf9fc2317c893b6b250007ded5ef879f`, fixes two PR589 gzip `cmp` sites.
- [PR1824](https://github.com/CrocSwap/integer-mult-bounds/pull/1824), head
  `ad5b1248f25a71983b20617e2f3a80be22f03990`, replays the selected final stage
  across interpreters and compares its outputs.
- [T37 receipt-role binding](../t37-receipt-role-binding/README.md) finds actual
  collisions in a different eight-input path normalizer.
- [Joint-prefix validation](../complex-joint-prefix-validation/README.md)
  previously compared complete runtime identities across platforms; it does not
  supply this independent all-node oracle and exhaustive receipt mutation census.

No-match is not novelty: these searches exclude code diffs and most closed-PR
bodies. The result is deliberately a separate audit, not another gzip repair.

This audit does **not** rebuild a supplier, authenticate historical execution,
replay the selected cold construction, prove full caller acceptance, test other
operating systems, discharge inherited theorem assumptions, or improve kappa.
In particular, the producer's raw archive receipt and the generated portable
identity are different evidence domains. No independent human review is claimed.

Credit Jeremy Kothe, Rohan Arun, Hao Yan and the retained native/compiler/supplier
lineage, and Douglas Colkitt's maintainer replay and identity convention. Credit
Maxime Fleury's gzip reproducibility audit following Antoine Olivier's independent
replay, and the authors of the selected1042 lineage-resolution package for the
correct archived input location. Prepared for Adam Gall (@adamgall) with
substantial OpenAI Codex assistance in audit design, implementation, experiments,
testing and writing. New work is Apache-2.0; predecessor files and notices remain
unchanged.

## Open next questions

Do other current normalizers preserve roles and all proof-relevant fields?
This matters because neither this result nor prior gzip portability fixes certify
other projections or caller acceptance logic. A feasible next step is to choose
one distinct overlap-checked comparator, pin its actual input and repeat an
independent all-field oracle plus a bounded omission census. There is no technical
blocker, but it requires a separately scoped audit; this package makes no claim
about those other comparators. The structured question is in `TASK.json`.
