# Reconcile PR279's later target-prefix source

**Research consolidation; no new selected bound.** At main
`66849e1475c930fd7732b1a0067ffee7e1e95f60`, the central ledger identifies twelve
uncovered files in [PR279](https://github.com/CrocSwap/integer-mult-bounds/pull/279)'s
later head. They are a specific target-prefix update,
not a failure of the earlier reviewed construction. This companion preserves
the exact missing bytes and reconstructs the later package in a separate
directory. The historical package and its original receipts stay intact.

| Source state | Exact commit | Conditional historical kappa |
|---|---|---|
| Reviewed and retained on main | `4d8c31eec7ae618645cb058101cb4e72a97268d3` | `90446448750933/125000000000000000` |
| Later PR279 head reconstructed here | `913ccc48a0bc1173709ea92280b96252256b7754` | `724098741932703/1000000000000000000` |

The selected result at this contribution's original research base was #626 with #543,
`51110230636731/31250000000000000`. Neither historical value above replaces it.
During this run, main advanced to `7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`
and selected #741 with #589, `1661202643272239/1000000000000000000`.
This contribution is rebased on that final integration base. Every consumed
historical package, workflow and immutable context byte is identical across
the two bases, so the completed mathematical replay remains applicable.
Both bases are recorded in the source and evidence inventories; the original
`base_commit` fields identify the research base, not the final PR parent.
The [original integration receipt](../../docs/research/community-pr279-integration.json)
explicitly pins the first head and labels the second as later and unreviewed.
The [original source comparison](../pr-reconciliation-20261012/content-comparison.json)
records 104 matching paths and 12 unresolved paths among 116 PR paths.

## Exact source coverage

[SOURCE.json](SOURCE.json) binds every reconstructed file to both its SHA-256
and its Git blob ID. The historical package contains 113 files. The later
package contains 115: 103 unchanged files, ten modified files, and two additions.
The unchanged workflow is the 116th path in the PR inventory. The complete
historical inventory, workflow, original review receipt, and old comparison
are checked before reconstruction.

[source-update.tar.gz](source-update.tar.gz) holds the twelve updated files
byte for byte. It is an input archive, not a patch applied to the selected
or historical source trees. Extracting the archive alone yields the twelve
changed files; `--extract` below reconstructs the complete candidate package.
The upstream package's own manifest must then cover every reconstructed file.
No network or Git checkout is required for that reconstruction.
The [pinned later source tree](https://github.com/CrocSwap/integer-mult-bounds/tree/913ccc48a0bc1173709ea92280b96252256b7754/research/five-stage-gen4-banks)
also permits direct review of the original files.

| Updated files | Substantive change |
|---|---|
| `target-selection.json`, `target_transform.py` | Add the 220-square selection and literal target-prefix transform. |
| `portable_bit.py` | Execute the transform after the reviewed descent step and rebind its raw ledger. |
| `scalar_check.py` | Bind the changed event hash, 626,580 additions and coefficient counts. The scalar checker logic is unchanged. |
| `bank_check.py` | Recount 479,580 banked calls per replica, previously 480,680; rank mass is unchanged. |
| `finite_check.py` | Charge 626,580 weighted and 630,100 unit additions, previously 626,360 and 629,880. |
| `verify.py` | Require the later exact historical kappa after the same nine mandatory stages. |
| `README.md`, `PROOF.md`, `PR-STATEMENT.md`, `NOTICE.md` | Describe and credit the added stage. |
| `MANIFEST.json` | Bind the complete updated package. |

All changes between the two pinned repository commits fall in this table.
The package's retained scalar decoder, bank templates, complex supplier,
prime checker, exact moment engines and assembly logic are unchanged.
The new transform's checks supplement the existing pipeline.

## Mechanism and complete local cost

Each disjoint square contains four targets. In the selected interval, the
prefix delivered to one dependent target is the F2 sum of the prefixes
delivered to the other three. Writing their arbitrary initial contents as
`d0, r1, r2, r3` and delivered prefixes as `P0, P1, P2, P3`, the setup changes
the dependent target to `d0 + r1 + r2 + r3`. Omitting its old prefix and adding
back the three completed retained targets gives
`d0 + P1 + P2 + P3 = d0 + P0`. Thus setup and restore both matter even when
the target initially contains arbitrary data.

This argument needs the literal dependencies and the no-active-target-read
guard; a selection's announced counts alone do not establish it. The candidate
transform recomputes the prefix responses from the actual input word, checks
the guard, rebuilds every movement, and checks nesting, common frames,
nondegeneracy, endpoints and copied-center lifetimes. It replays all formal
columns in both directions and requires an omitted-setup mutation to fail.

The 220 squares touch 880 targets. They remove 1,100 old prefix additions and
insert 660 setup plus 660 restore additions, a net **220 extra additions**.
The local paid profile changes by `{1: -220, 20: -220, 21: +220}`. That removes
220 recursive calls per invocation while preserving rank mass, because
`-220 - 20*220 + 21*220 = 0`. The five-stage bill drops from 483,146 to 482,046
calls, and the banked bill from 480,680 to 479,580 per replica. Source accesses,
copies, helper restoration, banks and the inherited complex supplier remain
in the unchanged full finite replay. The quick command below only checks the
submitted schedule's accounting; it does not independently prove these
literal identities.

## Reproduce and inspect

Python 3.11 or later suffices for the source/evidence checks and corruption
controls. The full candidate replay also requires the inherited pinned
dependency `sympy==1.14.0`.

```sh
python -X utf8 -B research/pr279-target-prefix-reconciliation/verify.py
python -X utf8 -B research/pr279-target-prefix-reconciliation/test_verify.py
```

The first command checks exact source coverage, the finite selection census
and the retained replay evidence. Its first line is:

```text
PASS_PR279_SOURCE_RECONCILIATION old=113 current=115 modified=10 added=2
```

For a fresh complete replay, choose a **new directory outside the repository**:

```sh
python -X utf8 -B research/pr279-target-prefix-reconciliation/verify.py --replay --work ../pr279-replay-new
```

The wrapper reconstructs all 115 input files under `source/`, runs the
unmodified candidate `verify.py` with assertions enabled, and writes raw
output to `replay.log` and per-stage results to `replay/`. A successful run ends
with:

```text
PASS_PR279_FRESH_REPLAY stages=9 kappa=724098741932703/1000000000000000000
```

Use `--extract --work ../pr279-inspect-new` to reconstruct the source for
review without executing the mathematical verifier. Both actions reject an
existing destination. Checks remain enabled under `-I -O`; the full replay
always launches a normal assertion-enabled interpreter.

## Evidence and review boundary

The [result](RESULTS.json) and [replay evidence inventory](EVIDENCE.json) record
the exact source identity, environment, command and retained output hashes.
The complete fresh replay passed on Windows 11, CPython 3.12.0 and SymPy 1.14.0
in 1,096.765 seconds. It checked all 19,930 formal columns, 27,349 distinct exact
basis determinants, 4,923,000 bank assignments and 370 charts, both moment
engines, and the finite assembly. The actual target-prefix omission control,
11 scalar controls, six prime controls and all nine mandatory-stage omission
controls passed. All 115 source files retained their input bytes.

The companion's 13 tests pass both normally and under `-I -O`. They include
rejection of the actual historical replay as evidence for the later head,
missing/changed source, missing stages, unpaid restoration and archive
ambiguities. The literal-word fingerprint canonicalizes all six integer
fields of each instruction; a changed frame changes the fingerprint while a
changed gzip timestamp does not. Fresh replays compare this complete word
fingerprint rather than the regenerated gzip container.

Checking the retained archive is a check of stored
evidence; `--replay` performs fresh mathematical execution. A complete nine-stage
finite replay is distinct from regenerating the unchanged gen4 discovery
outputs, rerunning the selected construction, running Lean, or observing
remote Linux CI. No such additional local execution is inferred.

[SOURCE-CI.json](SOURCE-CI.json) separately records GitHub's completed successful
[run 38025932115](https://github.com/CrocSwap/integer-mult-bounds/actions/runs/38025932115),
whose `head_sha` is the later `913ccc48...` head. Its dedicated immutable-replay
jobs report success on Python 3.11 and 3.13. This is historical run metadata,
not newly executed CI for this consolidation. It is also distinct from the
earlier head's run recorded in the original maintainer receipt.

The inherited all-size compiler, weighted/common-ancestor charts, restored-row,
selector, routing, prime-supply, precision/recovery, complex symbolic and
analytic-transfer interfaces remain assumptions. This is not a formal proof
of the full multiplication theorem, a runtime benchmark, or a global optimum.
The consolidation makes the later head's source and scoped replay reviewable;
maintainer acceptance and PR disposition remain separate decisions.

## Attribution and sprint scope

Rohan Arun authored PR279's descent selection and integration with Anthropic
Claude assistance. The target-prefix transform is credited in his source to
eumemic's PR268; DreamingOfClouds supplied the gen4 word and package. Henry
Grant and Jacob Sussman's five-stage architecture, Evan McKinney's banks,
Chafik Boukhalfa's physical checkers, Avi Eisenberg's complex supplier and the
full source lineage retain their original notices in the reconstructed package.
Douglas Colkitt's reviewed checkpoint and reconciliation receipts supply the
historical context. See [NOTICE.md](NOTICE.md).

This consolidation was prepared for **mihir-s-05** with substantial **OpenAI
Codex assistance** in source comparison, implementation, review, execution and
writing. It does not claim independent human peer review. Apache-2.0 applies.

[CLAIM.md](CLAIM.md) records OS-random seed 95, the three candidate tasks, the
selection rule, the exact main base and overlap checks. No search for a stronger
bound was performed; the experiment is bounded by the single pinned 12-file
update and its complete finite verifier.

[VALIDATION.md](VALIDATION.md) records the final integration checks, and
[OVERLAP.json](OVERLAP.json) records the pre-submission overlap refresh.
