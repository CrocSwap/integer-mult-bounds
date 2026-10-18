# Exact claims in the assembly-domain diagnostic receipt

ywz65, with OpenAI Codex assistance. 2026-10-15. Apache-2.0.

The maintained `scripts/audit_assembly_domain.py --check` now compares saved
Boolean claims and integer counts without Python's numeric type coercions and
rejects duplicate JSON object keys. It still accepts changed object-key order,
whitespace and CRLF line endings. The diagnostic arithmetic, its four frozen
source pins, the saved receipt and the `--write` generator are unchanged.

This repairs receipt integrity only. It neither changes the production assembly
verifier nor enlarges its parameter domain. In particular, a malformed receipt
previously receiving `PASS` is not evidence that a new multiplication construction
was accepted.

## Reproduced failure and repair

The baseline is canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. On its actual command-line checker,
each following edit to `docs/research/assembly-domain-audit.json` received `PASS`
under Python 3.12.14 with `-I -O -B`:

| Single edit | Lost distinction | Repaired checker |
|---|---|---|
| Replace the first `strict_arithmetic_rejects_with_assumed_bridge: true` value with `1` | Boolean rejection claim versus an integer | Reject |
| Change `published_control.strict_constraint_count` from `47` to `47.0000000000000000000001` | Nonintegral decimal rounds to the float `47.0`, which compares equal to integer `47` | Reject |
| Put a `false` occurrence of the first rejection claim immediately before its existing `true` occurrence | The default JSON decoder silently discards the contradictory first claim | Reject |

The regression also duplicates the published constraint count as `0` followed by
`47`; the old comparison accepts this and the new checker rejects it. These
counts enumerate constraints and the flags report whether strict arithmetic
rejected a hypothetical row, so their types carry meaning in this receipt.
All rational quantities remain exact strings; this patch does not introduce a
general decimal normalization policy.

The JSON object hook detects duplicates at every nesting level before decoding
can discard them. Recursive comparison checks identical types, all object keys,
ordered list contents and exact scalar values against the freshly recomputed
report. It does not ignore additional fields. No `assert` gates acceptance.

## Validation and provenance

```sh
python3 -I -O -B -m unittest discover -s tests -p test_assembly_domain.py -v
python3 -I -O -B scripts/audit_assembly_domain.py --check docs/research/assembly-domain-audit.json
```

All 10 tests passed on Windows with Python 3.12.14. The tests execute the actual
CLI for each of the four formerly accepted mutations, both normally and with
optimization, and retain positive compact/reordered and CRLF receipts. They also
retain the original arithmetic/source controls and reject changed rational
slacks, reordered obligations, missing pins and added claims. Full selected
frontier replay is not needed for this diagnostic-only change and was not run.

The original domain diagnostic and its mathematical analysis are Douglas
Colkitt's work with OpenAI Codex assistance. The broader typed-comparison failure
class was already documented by
[PR #2040](https://github.com/CrocSwap/integer-mult-bounds/pull/2040), inspected at
`d31c1418c0c23994d1444dbd9d356b9a8238fd5e`; this contribution applies the lesson to
the separate maintained assembly-domain receipt consumer. It does not reproduce
or replace that PR's selected-final payload comparator.

Task selection used nonce `8ab28c18ff34f63e1b1aeb9c098ffbb2`, priority revision 4,
and the `portable-replay` card's canonical-comparison audit variation, refined to
this receipt. The prescribed baseline binding check passed. Canonical main was
refetched at 2026-10-15 14:22 UTC and remained the commit above. Overlap searched
open PR metadata, Discussions and local notes; the complete cached snapshots
contain 750 open PRs (14:08 UTC) and 1,216 Discussion records (14:10 UTC).
This is not coverage of every code diff or unpublished investigation.

## Open next questions

Other maintained receipt consumers need their own field-specific failure witness
before adopting this comparison rule. A useful next check would identify one
consumer with typed Boolean/count claims, mutate those claims through its real
CLI, and preserve every documented normalization. No repository-wide schema or
universal exact-number policy is established here.
