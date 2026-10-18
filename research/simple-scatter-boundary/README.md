# Simple-support scatter enforcement at both entry points

This opt-in successor rejects PR2977's paired-duplicate scatter before either
symbolic checking or record export. The unchanged selected word still produces
all three original artifacts byte for byte: 27,234 records, states and frames.
All 661 arbitrary-input F2 columns agree with the intended endpoint.

Nick Petalas's [PR2977 audit](../scatter-export-parity-audit/README.md) found the
counterexample and provided a candidate validation function. This package
answers its schema/enforcement handoff: one shared validator is now called by
two usable entry modes, which execute authenticated original scripts on private
input snapshots. The counterexample, source scripts and selected construction
are retained unchanged. No new kappa or supplier admission is claimed.

## The explicit contract

`simple-scatter-v1` adds a simple-support contract to the pinned `bitE8/1` word:

- `v` is a positive exact integer, excluding Boolean values.
- `ret` is a list; `scatter` is a list of exactly `v` rows.
- Each row is a list of distinct exact integers `k` with `0 <= k < len(ret)`.
- Empty rows and arbitrary row order are allowed. Duplicate indices, including
  odd multiplicities, are rejected; no coefficient normalization occurs.

The contract does not validate every other word field or require nine totals
in isolation. Retained-role legality, frames, dirty-state endpoints and H1-H5
remain obligations of the inherited checkers.

For abstract copied values `c_k`, symbolic scatter adds
`XOR(c_k for k in row)`, while export adds
`XOR(c_k for k in range(len(ret)) if k in row)`. Under simple support,
each coefficient is exactly the same 0 or 1. Since these operations only add
to the target roles, their order does not affect this F2 equality. This is a
sufficient schema; repeated odd multiplicities can also agree, as PR2977
already explains. The wrapper deliberately chooses the stricter contract.

The wrapper parses and validates the input before any delegate or output
directory is created, hashes the delegate's bytes against [SOURCES.json](SOURCES.json),
and copies both the word and delegate into a private temporary directory.
Changing the original input path after validation cannot change what executes.
The child runs without inherited Python optimization flags; its original
success/failure code is returned. The snapshots are removed on completion.

## Use and reproduce

From the repository root:

```sh
python3 -I -B research/simple-scatter-boundary/boundary.py check \
  research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz
python3 -I -B research/simple-scatter-boundary/boundary.py export \
  research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz /tmp/simple-scatter-records

python3.12 -B scripts/research_package.py --package research/simple-scatter-boundary
python3 -I -O -Werror -B research/simple-scatter-boundary/verify.py
python3 -I -O -Werror -B research/simple-scatter-boundary/test_boundary.py
```

`check` adds schema enforcement to the complete pinned symbolic checker.
`export` adds schema enforcement to the pinned exporter; it does **not** run the
symbolic checker or establish the semantic correctness of an arbitrary word.
Use the full symbolic/export/native sequence when evaluating a supplier.

The registered replay is standard-library-only and takes about ten seconds
locally. Its exact [receipt](RESULT.json) binds all three baseline artifacts to
their original bytes, reproduces the predecessor's paired-null symbolic
acceptance and incorrect exported endpoint, and rejects the pair through both
new entry modes before output creation. A separate F2 interpreter checks all
661 dirty-input basis columns, COPY/ERASE closure and the dirty-register-472
witness. It is a scalar projection, not an independent frame or native proof.

All 364 ordered rows of length at most five over three indices are enumerated:
16 simple supports pass, 348 repeated rows reject. Each accepted row is checked
on all eight assignments of copied bits. Nine behavioral test groups also
exercise malformed rows and types through both real CLIs, odd duplicates,
existing-output preservation, row permutation, input-path replacement,
delegate source corruption, semantic-checker failure propagation, and omitted
ADD/truncated-record controls. A disabled duplicate validator fails the same
enumeration. Explicit checks remain active under `-O`.

## Scope and remaining obligations

Base canonical main `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority
revision 6. [TASK.json](TASK.json) records the accepted draw and the changed
scope from `bit-helper-contract` to this explicit bit-interface handoff.
This is a local boundary module, with no helper search or family expansion.
The original-card first experiment was replaced by PR2977's known-working
audit, which reproduced before implementation.

The selected input/record checks and source pins are local evidence. Native
compilation, complete selected cold replay, hosting/precision, all-size transfer
and hosted CI are not claimed. Selected sources, their manifests and the
frontier are unchanged. An invalid word can still pass schema-only export;
the tests explicitly retain that distinction. Only schema rejection and source
pin failure are promised to leave output untouched; delegate failures retain
the original exporter's behavior.

## Open next questions

Should a reviewed successor supplier adopt this simple-support contract?
It would close the identified source-to-record ambiguity at both boundaries.
First review the schema, entry points and controls, then repin a successor
manifest and run the full symbolic/export/native chain. Maintainer adoption
and the inherited supplier obligations are the blockers; frozen packages
should not be repinned merely to install this opt-in module.

## Credit

Arham Tahir, with substantial OpenAI Codex assistance in investigation,
implementation, verification and writing. Apache-2.0. No independent human or
proof-assistant review is claimed.

Nick Petalas/PR2977 retains discovery, dirty-witness, prior guard and handoff
credit. The new delta is enforcing a named schema in both operational entry
points, snapshotting validated inputs, and testing that integration. Credit
eumemic for the punctured generator/checker and PR543/PR555 lineage,
DreamingOfClouds for PR589 and retained bit-supplier construction, Dylan Crow
for the exporter/native lineage, and Douglas Colkitt for selected bindings and
research guidance. Original scripts are invoked unchanged with their notices.
