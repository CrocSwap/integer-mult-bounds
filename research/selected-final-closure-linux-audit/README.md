# Complete PR2101 final-stage replay on Linux/WSL2

Independent execution of Adam Gall's pending [PR2101](https://github.com/CrocSwap/integer-mult-bounds/pull/2101), exact head `a247ef876e50bf3a7d890c7c1f9b409576674d7d`, passed on CPython 3.12.15, Linux x86_64 under WSL2. Both runs completed the fresh selected final stage, all **105 output comparisons**, the coupled 13-line outer log, five positive controls and **287 rejection controls**. No caller, comparator, frozen input or selected record was changed.

The [dated review](../community-efficient1100-audit/README.md#remaining-review) had completed the supplier stage but exhausted its batch budget before finishing the composed comparison and controls. This audit supplies that missing execution evidence on another platform. It does not change the review's disposition or admit the portable caller as a supplier.

## Evidence

The work started from canonical main `a7482490b4ca256db67d767a33fa6f7553060807`, priority revision 5. The exact pending package was exported into that isolated checkout. Its metadata check authenticated all 42 live scientific inputs against the unchanged predecessor pins. [SOURCES.json](SOURCES.json) records those pins and all eleven caller files, including both vendored predicates, by Git blob and SHA256. The historical scientific pin expressions retain their original meaning and base.

| Check | Observed outcome |
| --- | --- |
| Direct run, isolated optimized parent and fresh cache | Exit 0, 430.221 seconds |
| Registered replay, including source-pin validation | Exit 0, 421.852 seconds |
| Complete deterministic result | Byte-identical to PR2101's `RESULT.json` |
| Raw generated outputs against reviewed archive | 99 identical, six different |
| Complete comparison after the declared policy | 103 `bytes`, two `json-diff:declared-timing` |
| Same-side raw references authenticated | 30 per side |
| Fresh timing fields permitted to vary | 22; all 12 copied historical times retained |

Times are observations on this host, not benchmark or performance claims. The supplier child ran without optimization, with its assertions enabled. The registered parent used the predecessor's explicit `-I -O -B` command and the current runner's private bytecode namespace.

The six raw differences were:

- `global/audit/PREFIX-AND-INVOICE.json`, with equal complete canonical invoice content;
- `ADMISSION-CONTROLS.json` and `ASSEMBLY.json`, whose two raw invoice references changed consistently;
- `INDEPENDENT-T16.json`, whose six authenticated input keys used the new work/local roots;
- `REPLAY.json` and `STAGES.json`, with the permitted fresh times.

The reviewed invoice SHA256 is `212cf4ee3b16081bf66f300fa18b4070d25c17210c21c78c2967892c91870d12`; the first Linux run produced `4c4c57eee80328d4c1ad91857240dda46d31949d83736091a97ea47073a8d1e1`. Thus this was an actual execution of the invoice-reference case previously reported by commdata2338, not just a constructed formatting fixture. The exact generated assembly bytes differ from the selected certificate. Equivalence here is under PR2101's explicit authenticated-reference policy, not raw certificate equality.

`bytes` in the composed report describes the inputs *after* the named invoice/role transformations. It must not be read as 103 raw-byte matches. All eleven inner logs matched the reviewed run byte for byte.

### Retained artifacts

- [EXECUTION.json](EXECUTION.json) records exact commands, return codes, environment, durations, evidence hashes and output contexts.
- [REPLAY-RESULT.json](REPLAY-RESULT.json) retains the complete deterministic receipt, including every predecessor control label. The controls were executed unchanged, not independently reimplemented.
- [COMPARISON.json](COMPARISON.json) retains every per-file comparison result.
- [OUTPUTS.json](OUTPUTS.json) records the size and raw hash of every actual output, alongside its reviewed hash.
- [OUTPUT-DELTA.tar.gz](OUTPUT-DELTA.tar.gz) retains the six actual changed files. Overlay it on the 105 `candidate/strict/` files in the pinned reviewed PR1094 archive to reconstruct the entire first output tree. The other 99 files match that archive exactly. The compressed delta is 26,115 bytes instead of copying the 18 MB output tree.
- The `*-stdout.txt` files retain the metadata check, both complete caller outputs and the first run's outer stage log.

The delta's raw container and decompressed tar hashes are recorded separately. Its committed bytes are immutable evidence; regenerating another gzip stream is not required. A separate round-trip check reconstructed all 105 files and matched their raw hashes, complete comparison report and coupled outer log. Only the first run's outputs are retained. The registered repeat cleaned its temporary directory normally.

All 144 `test_research_*.py` workflow tests passed on CPython 3.12.15. The selected baseline binding check also passed. No full historical test suite was run for this evidence-only change.

## Boundary inspection

The unchanged `prepare` function first requires the exact 105-file set. It checks both ordered stage receipts, their success codes and all 22 raw log links, then checks the six exact input roles against actual same-side input bytes. The three-node invoice predicate validates both raw invoice links before canonicalizing the complete invoice and its complete consumers. The complete comparator then checks every output, with only the 22 declared fresh times masked. `outer_log` separately binds its eleven printed times to the same-side receipt and checks both final lines.

This audit inspected those source boundaries and their pins. It did not prove the Python implementations correct for every input. The executed controls include all 105 file omissions and a semantic change in each output. Changed log/invoice contents still reject after their corresponding raw links are repaired. Stale roles, invalid or missing times, altered historical times, duplicate keys, Boolean/integer substitution and an immutable archive-header mutation also reject. Re-running the predecessor's controls supplies independent execution evidence, not code-disjoint verification of the predicates.

The measured complete runs exceed 300 seconds and fit the declared 600-second registered-command budget on this host. This explains why a shorter triage budget is not an adequate completion test here; it does not guarantee a 600-second bound on every host.

## Reproduce the fresh execution

From a checkout containing both the audit and fetched PR2101 commit, create a separate checkout at the audited main base. Export only the exact pending package into it:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git pull/2101/head
test "$(git rev-parse FETCH_HEAD)" = a247ef876e50bf3a7d890c7c1f9b409576674d7d
replay_tree=$(mktemp -d)
git worktree add --detach "$replay_tree/tree" a7482490b4ca256db67d767a33fa6f7553060807
git archive a247ef876e50bf3a7d890c7c1f9b409576674d7d \
  research/selected-final-replay-closure | tar -x -C "$replay_tree/tree"
cd "$replay_tree/tree"
python3.12 -B scripts/research_package.py \
  --package research/selected-final-replay-closure --check-only
python3.12 -B scripts/research_package.py \
  --package research/selected-final-replay-closure
```

Expected final marker:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/selected-final-replay-closure outcome=completed
```

The direct retained-output command is also recorded verbatim in `EXECUTION.json`. Use new external paths for its `--work`, cache and `--write-result` arguments. Its result file must match both PR2101's `RESULT.json` and this audit's `REPLAY-RESULT.json` byte for byte. Raw output hashes and times need not repeat because work roots, object serialization and timing can differ.

This is an evidence-only package. There is no new verifier or registered hook that could be mistaken for a fresh supplier execution. The reproduction deliberately runs the exact predecessor. No source copies were added merely for provenance.

## Limits and credit

This is **not** `make frontier1094-verify`. The ten local inputs and earlier scalar/native/phase evidence came from authenticated reviewed archives; ancestors were not rebuilt. No new supplier, paid profile, kappa, hosted-CI result, complete multiplication theorem or discharge of all-size/compiler, physical hosting, precision/tape or analytic assumptions is claimed. This session exercised Linux/WSL2 only. Concurrent-writer snapshots, unreadable-directory hardening and arbitrary unclassified digest rebinding were not tested. Normalization was not broadened to make the run pass.

Credit Adam Gall for PR2101's complete caller and PR2059's invoice binding, commdata2338 for PR2040's strict comparator and Linux invoice observation, Josie Elliston for PR1824's replay, and Maxime Fleury and Antoine Olivier for the payload/container convention. Rohan Arun, Jeremy Kothe, Hao Yan, Douglas Colkitt and the retained supplier/compiler lineage keep their original attribution. The dated batch review identified the unfinished execution obligation.

Independent execution and evidence packaging by Nick Petalas. Apache-2.0. Canonical coordination is [Discussion1472](https://github.com/CrocSwap/integer-mult-bounds/discussions/1472#discussioncomment-18972126). Exact task, overlap and refresh details are in [TASK.json](TASK.json).

## Open next questions

Should maintainers admit PR2101 as an opt-in portable caller after completing their source/policy review? This audit removes the dated missing-execution evidence, but does not make that decision. First inspect the exact head, the six-file actual-output delta and its authenticate-before-rebind boundary. The blocker is maintainer review, not a missing complete Linux control run. Earlier-stage portable comparison and full cold ancestry remain separate tasks; this audit does not assign or reserve them.
