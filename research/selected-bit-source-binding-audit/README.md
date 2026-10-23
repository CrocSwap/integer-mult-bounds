# Selected PR589 bit supplier source binding

## Question and scope

For the selected #1094 composition, does the T16 assembler bind the cited PR589
bit supplier bytes to the source identity recorded in the assembly and retained
by the complete composition caller? This checks one source field only: the
expected Git blob ID `BIT_BLOB` for the supplier record. It does not audit the
supplier's mathematical derivation, rerun the complete composition, admit a
supplier, or change the selected result.

The scatter/export example from the task card is now covered by the live
handoff's PR #3801, so this is a complementary source-binding scope. The remote
hypothesis-tracing and semantic-supplier-fixture lanes remain separate.

## Result

**The pinned source identity is enforced.** The T16 assembler loads
`inputs/PR589-EXPECTED.json` only after `load_bit()` recomputes its Git blob ID
and matches the hardcoded 40-hex `BIT_BLOB`. The record copy is byte-identical
to the PR589 head blob at
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46:research/e8-bit-p111/tune/EXPECTED.json`
and to the merged source path
`b3eb785ac5b4b1ca2beea0f80db078a505626a90:research/e8-bit-p111-tuned/tune/EXPECTED.json`.
Both are Git blob `e293ddc557742637f9f679f083a1a282d87b1b13` (SHA-256
`b9f0e5ca038abe837b0007c8fe006f366a6f02009244ac57705a8a200e2301f4`). This
also resolves the source path rename between the PR head and merged tree by
content identity.

The positive fixture calls the production `assemble.load_bit()` on the pinned
T16 input and confirms it yields the selected `bit_lower` value
`1733427039589844234749/10^24`. The negative fixture changes only
`BIT_BLOB`'s first hexadecimal digit, preserving a valid 40-character lowercase
SHA-1 representation. The same production loader rejects the unchanged source
bytes with `AssertionError: bit supplier blob pin`. The selected assembly's
`input_sha256["package:inputs/PR589-EXPECTED.json"]` independently matches the
same T16 source bytes.

The record-to-caller chain is source-bound as follows:

- `certificates/selected-result.json` hashes the selected assembly bytes, and
  the selected record checker compares every file in the source inventory with
  its listed digest. This audit separately pins the selected manifest and its
  relevant inputs at the assigned base commit. The inventory includes the
  original supplier record, the T16 copy, and `gauge44-slots-t16/code/assemble.py`.
- The T16 assembler emits the supplier blob ID in `ASSEMBLY.json` and computes
  the bit profile only after the loader check. The existing bit supplier
  controls separately exercise 12 semantic and profile mutations; this audit
  does not repeat those fixtures.
- `make frontier1094-verify` runs the selected record check and
  `scripts/verify_frontier1094.py`; that caller requires the final assembly's
  `bit_supplier` record to equal the retained T16 baseline record and checks the
  selected exact kappa and full control counts.

This establishes a checked source identity edge for the selected bit input. It
does not replay `make frontier1094-verify`, prove the supplier's mathematical
claim, or resolve the inherited all-size/compiler, mutable-source,
whole-call-hosting, precision/tape, or analytic assumptions in the selected
scope.

## Reproduce

From the repository root, with the selected package source paths materialized:

```sh
python3 scripts/research_package.py --package research/selected-bit-source-binding-audit --check-only
python3.12 scripts/research_package.py --package research/selected-bit-source-binding-audit
```

The direct standard-library verifier is:

```sh
python3.14 -I -X pycache_prefix=/tmp/selected-bit-source-binding-pycache -B research/selected-bit-source-binding-audit/verify.py
```

`RESULT.json` records its deterministic output. The test uses the pinned
production loader in a fresh Python module instance and mutates only its
expected blob ID in memory.
The metadata check passed here and the direct verifier passed under Python
3.14.8. The registered package replay could not start because this host has no
Python 3.12 interpreter; no substitute registered replay is claimed.

## Open next questions

No new question is justified by this one closed source-identity check. Reopen
this audit if the selected bit supplier bytes, path, or composition route
changes.

## Credit

The selected assembly and verifier retain Douglas Colkitt's and credited
predecessor contributions. The T16 controller lineage credits Hao Yan. The
bit record is from DreamingOfClouds's PR #589 and its tuned word lineage from
PR #555, as described in the pinned source package. This source-binding audit
was prepared by OpenAI Codex (laptop-11), with substantial OpenAI Codex
assistance. No independent human or formal-kernel review is claimed. Apache-2.0.
