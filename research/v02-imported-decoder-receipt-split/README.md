# v02-imported-decoder-receipt-split

**No new κ.** The selected record stays `363005817/100000000000`
(`0.00363005817`). This package does not edit `certificates/selected-result.json`,
does not authenticate a protected origin, and does not join a parent prebirth
to the child.

## Scope and evidence

Original card: `portable-replay`. Scope status: **refined**. Discussion
[#1166 comment 19530677](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19530677)
asks for a reconciliation of the conflicting imported-decoder receipts on one
child digest before any parent-origin join. That is one canonical comparison
with an omitted mutation field. It is not a gzip-container repair.

Audited head: PR [#7137](https://github.com/CrocSwap/integer-mult-bounds/pull/7137)
`b5587eef1dd66d477a2e4d7b6f83616e07a01386`. Package base:
`e54523517d0f03e58352e647c403a5af3e525a57`. The PR head is not an ancestor of
that base, and this checkout does not contain the commit object. `inputs/`
holds unchanged byte copies. The verifier hashes them. When that commit is
present in the local Git database, it also compares the four files with
`git cat-file`.

| File | SHA-256 | Bytes |
|---|---|---:|
| `selected_child_preseal_v1.py.txt` | `7001e2ba395ebb7e943816301be7830e6a9bb699acc182e2bbeb786148459048` | 120929 |
| `INTERMEDIATE-7001e2ba.json` | `1ae26dddbdd917481e5972b4b98eca21a48733eefd04f1585741b7583b42f807` | 481 |
| `INGRESS-INDEPENDENT.json` | `bd74779a39172a77185bf118faccf4a6804ae97fd7c6e0de2ce27ce33d47f4bb` | 2103 |
| `REVIEW-final.json` | `6db9bd22e5e34eef213d0f4e29553713a58de16680618566dabdf6a01b29e35c` | 3363 |

`REVIEW-final.json` records the ingress digest and length above. Both receipts
name the child digest. The archive README says the preserved intermediate
source bytes equal the final source bytes, and that the archive does not
select a finding.

## Result

On these child bytes, replacing the identity of a snapshotted `json.loads`
binding during the first fd0 read cannot call that replacement three times and
then assign `phase = 'SEALED'`.

`_receive_v02_preseal` snapshots its function globals and the module
dictionaries reachable from those globals before it creates the fd0 `io`
record and before `_READ`. The nested `source_recheck` compares each
snapshotted global with `namespace0[key] is not value` and each snapshotted
import entry with `namespace[key] is not value`. On a miss it raises
`RuntimeError` through the local name `error0`, which was bound to
`RuntimeError` before the nested function. The comparison does not call the
new object. Neither comparison is gated by `include_import_functions`.

The read loop calls `_READ(0, 1)` and then `source_recheck()` with no
arguments. The default of that flag is `False`. The first `_document` call in
the function is after that loop, and a `source_recheck(True)` sits between the
loop and that call. The only `json.loads` call in the module is inside
`_document`. The receive handler is `except BaseException`, assigns
`phase = 'STOP'`, and re-raises. `install_before_capture` calls
`_receive_v02_preseal`, then `_construct_v02_issued_input`, then
`_register_v02_live`, and only a later statement of the same `try` assigns
`phase = 'SEALED'`. Its handler likewise assigns `STOP` and re-raises.

An identity change visible to those `is not` checks therefore raises inside
the read loop, before `_document`. The exception leaves the install `try`
before `SEALED`. The final ingress case `imported_decoder_alias_after_read`
records that refusal text and `fd0_model_reads: 1`. The helper-global case
`decoder_alias_after_read` records `V02 preseal retained helper alias changed`
and the same one-read count. Both match a check that runs after the first
one-byte read.

The intermediate receipt names the same child digest, the mutation
`json.loads alias replaced during first fd0 read`, `foreign_callbacks: 3`, and
`final_phase: SEALED`. That pair of outcomes is not an execution of this
identity replacement on these bytes. `REVIEW-final.md` says the intermediate
repair left the imported alias exposed and that the final source checks the
imported namespaces before post-I/O decode. The final prose agrees with the
source. The intermediate JSON's attachment of `SEALED` and three callbacks to
this digest does not.

The success path that does get past `source_recheck(True)` calls `_document`
twice in `_receive_v02_preseal` and once in `_construct_v02_issued_input`.
`_register_v02_live` does not call it. Three is the number of `json.loads`
calls on that later success path. It is the count a mutation can report only
after it has already survived the identity checks.

Imported function descriptors are a different check. `source_recheck` builds
`records` as `functions0 + import_functions0` only when
`include_import_functions` is true; otherwise `records` is `functions0`.
Helper code objects are therefore checked on the per-byte call, and imported
code objects are checked on `source_recheck(True)` after the frame has been
assembled. The ingress rows match that split: `decoder_code_after_read` has
one modeled read, and `imported_decoder_code_after_read` has 1111. This
package records 1111 from the receipt. It does not derive 1111 as a frame
length. A `__code__` change of the snapshotted `json.loads` function is in
the deferred set, so it is also refused before the first `_document` when the
`True` recheck runs. The same-object code case is not a way through to
`SEALED` on these bytes.

`verify.py` checks these facts and five mutants: deleting the import-alias
raise, deleting the post-read `source_recheck()`, assigning `SEALED` in the
install handler, always including import descriptors, and setting the
intermediate callback count to 0. Each identity mutant removes the
obstruction. The descriptor mutant keeps the identity obstruction and loses
the deferred-import fact. The callback mutant no longer states the conflicting
outcome. The child is parsed, not imported or executed.

Orientation only: `python3 -B scripts/research_selected_baseline.py` printed
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` with selected κ
`363005817/100000000000`. That command is not a frontier replay. The
priorities prose still names an earlier figure; this package does not edit
that prose or the selected record.

## What remains unresolved

The certificate covers an identity replacement in the snapshotted function
globals or in the snapshotted module dictionary. It does not cover a
replacement of the module `__dict__` object, a concurrent mutation after the
pre-decode `source_recheck(True)`, or an arbitrary interpreter or stdlib
mutation. `REVIEW-final.md` already limits the direct-import check in those
terms.

`REVIEW-final.json` names `test_ingress_independent.py` at SHA-256
`52d6b54ee6c465a00d6bc4d0a5ccf4271376651a061246cf293d7a5dce0a429b` (4450
bytes). On 2026-11-11 the contents listing of this commit's
`snapshots/trusted-preseal-ingress/review/` directory did not include that
file. The verifier records the digest and does not re-query GitHub. Without
the harness, the object that was replaced and the driver that wrote
`final_phase` stay unidentified.

The final review's own status is
`ACCEPT_PROSPECTIVE_CONDITIONAL_SOURCE_ONLY`, with
`protected_origin_authenticated`, `operational_channel_accepted`, and
`real_live_profile_tested` false, and `original_omission_cases` 0. Those
fields are unchanged by this reconciliation.

## Reproduce

From the repository root, CPython 3.12 standard library:

```sh
python3 -B research/v02-imported-decoder-receipt-split/verify.py
python3 -O -B research/v02-imported-decoder-receipt-split/verify.py
python3 scripts/research_package.py --package research/v02-imported-decoder-receipt-split --check-only
```

`make frontier7000-verify` was not run. The child module was not executed.
The missing ingress harness was not replayed.

## Open next questions

1. Which source bytes and harness produced `foreign_callbacks: 3` and
   `final_phase: SEALED`? Publish that harness, the object it replaced, and
   the child digest it actually ran. If those bytes differ from
   `7001e2ba395ebb7e943816301be7830e6a9bb699acc182e2bbeb786148459048`, the
   intermediate JSON's `source_sha256` needs a different digest. A same-object
   change that survives both the identity check and the descriptor check would
   also have to be shown explicitly. The named ingress harness is absent from
   the published review directory.

2. What caller contract joins parent prebirth (`RootProxy._run` /
   `_prebirth_v02`) to `prepare_selected_child`, `install_before_capture`, and
   `_receive_v02_preseal`? The receipt split does not authenticate the writer
   on fd0. `TRANSPORT-POINT.md` in the same archive records a character-device
   fd0 with immediate EOF on the observed Tool route, and the private
   observation records were not exported. A design that lists prerequisites is
   not that join. Original omission acceptance remains 0/8.

## Credit

The child source and the two receipts are Clear1nsight / Chris R, PR #7137,
building on PRs #6867, #6873, #6885 and #6910. The archive's own reviews used
OpenAI assistance, as its NOTICE states. This reconciliation was prepared by
unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
