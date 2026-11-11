# Lean T530 ownership replay for the two release swaps

This is a fresh, finite owner and invoice check. It regenerates all 1,946,160 literal helper-role rows without an optimizer, then independently verifies the actual source windows, physical families, chronological compact prefixes, capacities and complete histogram against the fresh canonical words. It does not rerun the canonical words' scalar/operator or native proofs, and does not establish an unconditional multiplication theorem.

From the repository root:

```sh
python3 -B research/staged-release-retiming-t530/owner-audit/run.py --out /tmp/staged-release-owner-check
```

The output directory must not exist and must be outside this package. Python 3.12 is recommended, and NumPy is required. The pinned predecessor uses `hashlib.file_digest`, so Python 3.11 is the minimum. The runner rejects optimized Python because the preserved predecessor assertions must remain enabled. `--repo /path/to/checkout` can select another checkout with exactly the same 13 source file hashes. The default derives the repository root from the runner's location; no working-directory assumption or network is required.

## Fresh checks and retained records

The new runner was executed from this public package with Python 3.12.14 and NumPy 2.5.4. The full literal reconstruction and independent owner audit passed in 19.23 seconds, and its before/after snapshot verified that no package file was written. The fresh output was outside the package. `evidence/FRESH-RUN.json` and `evidence/FRESH-RESULT.json` preserve that executed receipt, distinct from the earlier retained `RESULT.json`.

A rerun performs all of the following:

1. Authenticate the 13 existing-main dependencies and all 22 frozen PR3626 owner artifacts.
2. Execute the unchanged `upstream/portable_expand.py`, including its exact primal and deterministic integral-network checks, into a fresh output directory. This generates the full T530 literal journal and binds its decompressed payload to SHA256 `9f82e7d4abfcb52cd6d969e37e07415516856d7af85192010f3fc142dbaad246`.
3. Bind both actual retimed canonical words and read their local profile. Keep the literal ownership rows unchanged, replacing only the generated full profile by `H_new = H_old + 4770*(-2H1-2H2+2H3)`.
4. Execute `semantic_gate_controls.py`, which runs the exact preserved derived `independent_literal.py` once against the regenerated journal, changed profile and actual canonical words. Check all 1,946,160 rows, 4,770 calls and 530 replicas, then test five actual production gate statements on changed in-memory semantic inputs. Compare the positive receipt fields and verify that every package file remains unchanged. The historical five `reject()` lambdas are retained as provenance and are not counted as negative coverage.

### Correction to the inherited negative-control claim

[PR3694](https://github.com/CrocSwap/integer-mult-bounds/pull/3694) identified that the five inherited `reject()` lambdas do not invoke their corresponding production gates. A separate scratch reproduction confirmed that disabling all five named gates still leaves those historical controls reporting success. This is a test-coverage defect; the positive owner, window, family, prefix and invoice predicates remain genuine checks on the literal journal. Earlier receipts and their `controls` fields are preserved unchanged as historical records, not evidence of five genuine mutation tests.

The owned companion now extracts the exact five unconditional `need(...)` AST statements from the authenticated derived auditor and checks that they match the frozen predecessor. It first executes the complete positive auditor, including source authentication, once. It then tests duplicate helper identity, time equal to an actual nonnegative strict lower endpoint, reuse of a same-call physical family, a chronological offset hole, and one unpaid rank-1 invoice child. The family case also executes the production key-computation statements. Each changed input must raise the exact expected gate error; the original input must pass before and after. Replacing that gate predicate by `True` must make its mutation test fail.

`SEMANTIC-GATES.json` binds these five rejection results and five gate-disable sensitivity results to the preserved auditor, the new checker and the unchanged positive `RESULT.json`. These are isolated semantic gate tests on real journal data. They do not claim five complete corrupted-file replays through the artifact hash checks, or new native/controller/outer admission. The preserved auditor, upstream files, old receipts and full-admission source manifests are unchanged.

The resulting complete profile is:

```text
{1:11747920,2:3453480,3:1112042,4:486540,5:103690,8:38160,48:202828}
```

Physical stock is 475,389. The fresh independent audit derives idle counts `{1:123430,3:34022,5:8290,48:202828}`. The authenticated canonical words supply 408 helper roles and 91 zero buffers, each with width inventory `{4:26,5:2,6:18,7:52,8:97,9:213}` and local profile `{1:2437,2:724,3:226,4:102,5:20,8:8}`.

The generated `PROVIDERS.json` is unchanged predecessor materialization metadata. This owner audit obtains the retimed bill and widths from the two authenticated canonical words instead. That generated predecessor provider metadata is not a retimed full-admission input.

## Inputs, unchanged sources and provenance

`PUBLIC-INPUTS.json` lists the exact 13 repository paths and SHA256 values, pending PR3626 head `659fd5e7064d9466b668d7188cbb013b333a415a`, the source base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, and the native and semantic payload pins. Every repository dependency was already present on that base. No main source is copied again and no 11 MB generated fill is committed.

`upstream/` retains all 22 files authenticated by its unchanged `ARTIFACTS.json`. The PR3626 manifest Git blob `01694a31e732d9f0a357ce3466cb2aa9f81a5855` was checked against the exact pending head. Its original producers, source context, primal, expectations, independent auditor, proof, credits and notices retain their original bytes and hashes.

`independent_literal.py` is the already-derived auditor, copied without predicate changes. `DERIVATION.json` documents the three preceding adaptations: explicit upstream directory, actual fresh native canonical pins, and the local bill `-2H1-2H2+2H3`. The original auditor remains at `upstream/independent_literal.py`. The runner authenticates both scripts before execution. Their positive checks are not replaced by stored PASS receipts. The owned companion supplies the additional semantic mutation coverage without editing either preserved script.

Only this session's local home-directory prefix in public execution metadata is represented by `$RESEARCH_WORKSPACE`. `PUBLIC-PROVENANCE.json` records original and public SHA256 values; scientific fields and content hashes are unchanged. Frozen upstream sources are not normalized or rewritten.

The independent owner check imports neither the producer nor a solver or inherited owner checker. The separate materialization subprocess does execute the frozen deterministic constructor; the subsequent auditor checks its complete literal output independently. Canonical native frame tables are authenticated inputs; the separate complete operator and native proofs must bind those exact words.

Source credit and Apache-2.0 notices are retained in `upstream/UPSTREAM-SOURCE-CREDITS.md` and `upstream/UPSTREAM-SOURCE-NOTICE`, including PR3605's staged entering helpers, PR3626's T530 construction, PR3133/PR3148 and their named predecessors. The new release retiming, integration and package wrapper had substantial OpenAI Codex assistance. No independent human or formal-kernel review is claimed.
