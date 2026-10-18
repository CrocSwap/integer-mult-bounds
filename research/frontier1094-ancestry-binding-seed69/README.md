# Ancestry binding of the selected #1094 reuse replay

**Adversarial audit and supplemental certificate; no new kappa.** Seed 69
(adversarial mathematical audit), card `supplier-boundary-audit`, refined scope
recorded in [TASK.json](TASK.json). Base `dadfea6e`. No selected record, pinned
verifier, review document or `upstream/` file is changed.

## Finding

The selected record's `reproduce` command is the cold `make frontier1094-verify`.
`scripts/verify_frontier1094.py` also has a reuse mode, `--baseline1042`. The
[batch1099 review](../../docs/research/community-batch1099-review.md) says its
local execution used that mode. Reuse mode checks the published #1042 receipt,
its stage logs and all 457 artifacts. It then runs these three statements:

```python
ancestor = Path(receipt['baseline']).resolve()
check_selected(ancestor, ancestor/'ancestor')
require(sha(baseline/'BASELINE-BINDING.json') == receipt['baseline_binding_sha256'], 'Ancestor binding')
```

The return value of `check_selected` is discarded. `BASELINE-BINDING.json` is
compared only with the receipt's hash, and both come from the same #1042
package. Nothing ties the rechecked PR799/PR741 ancestry to the binding that
#1042 recorded. Reuse mode therefore accepts any ancestry at the receipt's
machine-local path (`/private/tmp/batch952-baseline799`) that passes
`check_selected`, even when its binding differs from the bound one.

`verify_frontier1042.py` writes that file as exactly
`json.dumps(check_selected(baseline, baseline/'ancestor'), indent=2)+'\n'`, so
the missing comparison is a direct one. The #890 and #942 reuse modes also
discard an initial pre-check, but they then bind their ancestry through their
`final_binding` comparisons
([complex-t21-owners/verify.py](../complex-t21-owners/verify.py),
[complex-t37-owners/final_binding.py](../complex-t37-owners/final_binding.py)).
Among the current `--baseline*` reuse modes, #1094's is the only one without
that binding.

**Severity: low.**

- **κ:** no κ changes.
- **Cold path:** the cold default rebuilds the ancestry and writes the binding
  from that same directory, so it has no such gap.
- **Reuse inputs:** in reuse mode, the #1094 candidate stage consumes
  `slots/local`, and the verifier's retained-bit-supplier check reads
  `t16/ASSEMBLY.json`. Both come from the hashed #1042 artifacts, not the PR799
  ancestry.
- **Review wording:** the review's description, "rechecks the complete retained
  bit/PR741/PR799 ancestry", is accurate about the check performed. The check
  does not show that the rechecked ancestry is the one #1042 bound.

## Certificate from committed evidence

The verifier extracts two committed archives into the `check_selected` layout:

- [integrated799-replay.tar.gz](../community-frontier799-audit/integrated799-replay.tar.gz)
  (the PR799 replay);
- [composed-replay-evidence.tar.gz](../community-frontier741-audit/composed-replay-evidence.tar.gz)
  (its PR741 ancestor).

The unchanged `check_selected` returns a binding whose canonical serialization
has SHA256 `22575ff2…`. That is byte-identical to
[BASELINE-BINDING.json](../community-frontier1042-audit/BASELINE-BINDING.json).
The same hash appears in three places:

- as `baseline_binding_sha256` in the #1042 receipt (`bf12c6ed…`);
- in the archived #1042 replay `selected-replay.tar.gz`;
- by chain from the #1094 receipt, which names that #1042 receipt in its
  `baseline_receipt_sha256` field.

So the ancestry binding behind the selected record can be reproduced from
in-repo evidence alone. It does not depend on what was present at the recorded
`/private/tmp` path during review.

## Controls

Each variant is a copy of the rebuilt ancestry. Where a variant changes PR741 or
bit evidence, `ANCESTRY.json` and the PR799 `RESULT.json` are rebound to the
ancestry check, as a consistent rerun would record them.

| Variant | Mutation | `check_selected` | Binding field that differs | Pinned reuse mode | With suggested line |
| --- | --- | --- | --- | --- | --- |
| identity | none | PASS | none | PASS, κ = 0.001672660197076918 | PASS |
| timing | PR741 stage-one `seconds` +1, `STAGES.json` and receipt rehashed | PASS | `complex_receipt_sha256` | PASS | reject |
| bit_result | PR589 `RESULT9.json` `next_grid_point_rejected` replaced | PASS | `bit_result_sha256` | PASS | reject |
| bit_supplier | PR799 `global/ASSEMBLY.json` `bit_supplier` commit and blob zeroed | PASS | `assembly_sha256` | PASS | reject |
| kappa | PR799 `RESULT.json` κ raised by 10⁻¹⁸ | reject | none | reject | reject |

What the variants show:

- **timing** is benign. A genuine re-execution has different wall-clock times,
  and reuse mode cannot tell which execution #1042 bound.
- **bit_supplier** is the semantically invalid fixture the card asks for. The
  PR799 assembly names a nonexistent supplier commit and blob. `check_selected`
  does not pin those provenance fields, and the assembly hash in its return
  value is the value reuse mode discards.
- **kappa** shows that `check_selected` itself is not vacuous.

Each row is evaluated at three layers:

1. **`check_selected` directly**, on the variant ancestry.
2. **The three pinned statements.** They are parsed from the pinned Git blob of
   `verify_frontier1094.py`, executed with the real `check_selected`, then
   executed again with the second statement replaced by the suggested binding.
3. **The whole pinned `verify_frontier1094.py` reuse mode**, run in a scratch
   copy of the required sources against the archived #1042 replay. Two stages
   are stubbed: the historical-source stage, and the candidate stage, whose stub
   copies the published #1094 `REPLAY.json`/`ASSEMBLY.json`. All #1042 receipt,
   stage-source, log and artifact checks, and every later #1094 assertion, run
   unchanged. Only the receipt's `baseline` field is redirected to each variant;
   this models placing the variant at the recorded path.

Outcomes are frozen in [EXPECTED.json](EXPECTED.json).

## Suggested maintainer fix (not applied)

```python
require(check_selected(ancestor, ancestor/'ancestor') == read(baseline/'BASELINE-BINDING.json'),
        'Ancestry recheck differs from bound #1042 binding')
```

In cold mode, `BASELINE-BINDING.json` is written from `check_selected` on the
same directory, so it still matches. A future receipt could also record
`ancestry_binding_sha256`. This package does not edit the pinned verifier,
because that would change the selected record's reproduction source.

The package reads both audited verifiers from their pinned Git blobs whenever
the live files differ. Its result therefore remains checkable after such a fix.

## Reproduce

```sh
python3 scripts/research_package.py --package research/frontier1094-ancestry-binding-seed69 --check-only
python3.12 scripts/research_package.py --package research/frontier1094-ancestry-binding-seed69
```

- Expected output: `PASS_FRONTIER1094_ANCESTRY_BINDING_AUDIT 22575ff2…`.
- Inputs: before importing any checker, `verify.py` requires every live input
  declared in `SOURCES.json` to match its pin. `check_selected` also requires
  all of `research/gauge44-frames-x` to equal that package's `MANIFEST.json`.
  The manifest and the six files read directly are declared, and the manifest
  stands in for the rest of the directory.
- Run time and environment: about 3 seconds, standard library only, with
  assertions required. All scratch files go in temporary directories outside
  the checkout.
- Tested on Python 3.12.15 and 3.14.8 (macOS).

## Scope and remaining obligations

This package is not:

- a cold replay of #1042 or #1094 (the cold path was not rerun here);
- authentication of the archived logs' execution;
- a proof of the multiplication theorem.

It shows that the bound ancestry binding is reproducible from committed
evidence, and that the reuse path does not itself enforce that binding.
Inherited assumptions remain conditional: all-size/compiler,
common-label/mutable-source, whole-call hosting, precision/tape, analytic, and
bit H1–H5.

## Open next questions

The structured entries are in [TASK.json](TASK.json).

1. **Should PR799's bit-supplier provenance fields be bound to their cited
   source?**
   - *The question:* should `check_selected` (or `verify_frontier799_bindings`)
     bind the PR799 assembly's `bit_supplier` commit, blob and path to the cited
     PR589 source?
   - *Why it matters:* the zeroed fixture above passes, because only a
     downstream hash differs.
   - *First step:* in a separate checker, require
     `git rev-parse <merged_as>:<path>` to equal `git_blob_sha1`. At the PR589
     head `commit`, the same blob sits at the pre-rename path
     `research/e8-bit-p111/tune/EXPECTED.json`, so a check against `commit`
     must handle the rename.
   - *Blocker:* those scripts are pinned selected supplements, so changing them
     needs a maintainer rehash cycle.
2. **Should receipts record a portable ancestry identity instead of a
   machine-local path?**
   - *The question:* receipts could record archive and binding hashes rather
     than only a `baseline` path under `/private/tmp`.
   - *Why it matters:* the receipt records a path but no content identity, so
     reviewers have no portable record of which ancestry was rechecked.
   - *First step:* add `ancestry_binding_sha256` in the next selected-record
     integration, and derive the reuse ancestor from committed archives as this
     package does.
   - *Blocker:* the receipt schema of the selected record is frozen.

## Credit

Prepared by Sagar Thakrar with substantial Anthropic Claude assistance. That
assistance included a five-explorer sweep with impact, rigor and novelty judges,
and separate code and impact skeptics who tried to refute the finding.

Predecessor and maintainer credit:

- Douglas Colkitt: the #1042/#1094 composition verifiers, archived replays,
  binding receipts and batch1099 review.
- Rohan Arun's #1094 and Jeremy Kothe's #1042 constructions, with Hao Yan's T16
  controller.
- nightangelflowerwin-ops (#865): `check_selected` and the versioned PR741
  coverage contract it enforces.
- Lucas Steinmetz (@ljste, #838): the PR741 receipt-coverage finding that the
  contract addresses
  ([frontier741-receipt-coverage-audit](../frontier741-receipt-coverage-audit/README.md)).
- Adem Vessell (@AdemVessell, #851): the bridge-identity check used to rebind
  the variant ancestries.
- Chafik Boukhalfa / chafreaky (#890) and Jonathan Capalbo / jon314159 (#942):
  the replays whose ancestry-binding pattern this note compares against.
- The bit and complex supplier lineage credited in the selected review.

New work is Apache-2.0.
