# Selected final stage: interpreter matrix and canonical-payload comparison

**Verifier engineering / portability receipt; no new kappa, no change to any
selected, pinned or frozen file.** Card `portable-replay` (priority revision 3,
chooser seed `e95bc9807d1d236e2d6d663b2945e09b`), refined to one stage and one
comparison; see [TASK.json](TASK.json). Base `0b1cccf8`.

## Question

The selected #1094 replay (`make frontier1094-verify`) has exactly one stage
after its #1042 baseline:
[`complex-t16-rare-pattern-exchanges/verify.py`](../complex-t16-rare-pattern-exchanges/verify.py),
which runs the frozen PR1087 strict verifier on Rohan Arun's owner exchanges.
Its README says "Python 3.12+", and the selected-replay CI pins 3.12. Does the
stage pass on other CPython versions, and is its output the same as the
reviewed run archived in
[`community-frontier1094-audit/selected-replay.tar.gz`](../community-frontier1094-audit/selected-replay.tar.gz)?
If the output differs, is the difference in proof-relevant content, or only in
container bytes, absolute paths and timings?

## Result

The stage was rerun from the committed #1042 `slots/local` (all ten files match
the #1042 receipt's hashes). It passed on all five interpreters and five
hash-seed settings, with kappa `0.001672660197076918` each time. Each rerun's
105 output files compare with the reviewed run as follows:

| Class | Files | What differs |
|---|---:|---|
| byte-identical | 102 | nothing: all 22 `.gz` files (gzip containers included), 69 of the 72 `.json` files and all 11 inner stage logs |
| `json-relocated` | 1 | `INDEPENDENT-T16.json`: only the absolute paths used as keys of `input_sha256`; all six input digests agree |
| volatile | 2 | `REPLAY.json`, `STAGES.json`: only the 11 per-stage `seconds` values; every `log_sha256` agrees |

| Interpreter (macOS 26.6.2 arm64, uv-managed CPython) | `PYTHONHASHSEED` | Stage wall time | Classification |
|---|---|---:|---|
| 3.10.21 | random | 19.7 s | 102 / 1 / 2 |
| 3.11.16 | random | 17.5 s | 102 / 1 / 2 |
| 3.12.14 | random, 0, 1, 4242 | 16.6 s | 102 / 1 / 2 (all four) |
| 3.13.15 | random | 17.5 s | 102 / 1 / 2 |
| 3.14.7 | random, 0, 987654321 | 14.6 s | 102 / 1 / 2 (all three) |

In particular, every rerun's `strict/ASSEMBLY.json` is byte-identical to
`community-frontier1094-audit/ASSEMBLY.json` (`1122cb3a…`). That file is the
certificate the selected record pins at base `0b1cccf8`. PR1735 points out that
`make frontier1094-verify` binds that certificate to the replay only through
kappa. This rerun closes the gap for the final stage, by bytes, on every
interpreter tested. `verify.py` checks it explicitly.

So the final stage is deterministic and portable across CPython 3.10–3.14 on
this platform, down to compressed bytes. "Python 3.12+" in the stage README is
conservative. The real floor is `tarfile.extractall(filter='data')`, which
needs 3.10.12+, 3.11.4+ or 3.12+.

**One receipt field cannot be reproduced.** The outer stage log
`rare-pattern-exchanges.log` prints per-stage wall-clock seconds, so the #1094
receipt's `log_sha256` for that stage (`80362b2c…`) cannot match any rerun. The
cold replay never compares against it, so this does not break replay. A reviewer
comparing two #1094 receipts should still expect that field to differ. The inner
`log_sha256` values in `candidate/strict/STAGES.json` do not contain timings, and
they are reproduced exactly. The verifier here compares the outer log only after
removing the trailing seconds field from each `PASS <stage> <seconds>` line.

## What the verifier checks

[`verify.py`](verify.py) runs in about 20 s using only the standard library:

1. It extracts `slots/local` from the #1042 archive and requires exactly the ten
   files bound in the #1042 `RESULT.json`, with matching hashes.
2. It extracts the reviewed output from the #1094 archive. It binds that output
   to the committed #1094 `RESULT.json`, `STAGES.json`, `REPLAY.json` and
   `assembly_sha256`. It also checks that the #1094 receipt names the committed
   #1042 receipt and the stage script's current hash.
3. It reruns the stage with the active interpreter in a fresh directory, then
   compares the result with [`compare_payloads.py`](compare_payloads.py), which
   works file by file, by bytes and by canonical payload. It requires the exact
   classification above.
4. It runs negative controls on copies of the rerun:
   - Each of these must be flagged `proof-relevant-candidate`:
     - a changed proof value (`live` in `INDEPENDENT-T16.json`);
     - a changed kappa in `REPLAY.json`, which also differs in volatile seconds;
     - a changed inner `log_sha256` in `STAGES.json`;
     - a changed gzip payload;
     - an input path outside the mapped roots.
   - A missing file must be reported `missing`.
   - A gzip file re-compressed at a different level and mtime must be accepted
     as `gzip-container`.

`compare_payloads.py` can be reused on its own:

```sh
python3 research/selected-final-stage-portability/compare_payloads.py REF_DIR RUN_DIR \
  --ref-root '<WORK>=/abs/ref/work' --run-root '<WORK>=/abs/run/work' --out report.json
```

A JSON difference counts as `volatile` only when every differing leaf sits under
a key in `VOLATILE_KEYS` (only `seconds` by default; `--volatile-key` adds more,
for example `log_sha256` when logs print timings). Every other difference is
reported as `proof-relevant-candidate` for a person to inspect. It does not
decide which fields are proof-relevant; it lists the paths that differ.

## Reproduce

```sh
python3 scripts/research_package.py --package research/selected-final-stage-portability --check-only
python3.12 scripts/research_package.py --package research/selected-final-stage-portability
# matrix:
for v in 3.10 3.11 3.12 3.13 3.14; do python$v -B research/selected-final-stage-portability/verify.py; done
```

## Not checked

- **Earlier stages.** The cold #1042 and #799 baselines were not rebuilt; the
  stage input is the hash-bound archived `slots/local`. The 711 s `chain` stage
  and the native steps are outside this scope.
- **Other platforms.** Linux, Windows and non-uv builds of CPython were not
  run. The reviewed run's `/private/tmp` paths suggest it ran on macOS too, so
  this is not a cross-OS result.
- **Transitive inputs.** The stage reads files from `--main` (the repository)
  that are bound by the PR1087 verifier's own pins. `VERIFY.json` declares the
  stage script, its manifest and the receipts/archives, not every transitive
  file.
- **Mathematics.** This does not check the mathematics of the stage or of its
  inherited assumptions, and it does not replace the selected cold replay.

## Open next questions

1. **Does the same byte-level agreement hold on Linux (CI's Ubuntu 3.12) and on
   Windows?** *Why it matters:* if it holds, a cross-OS reviewer could compare
   receipts directly instead of rerunning the stage. *First step:* run
   `verify.py` on Ubuntu 3.12. *Blocked by:* no Linux host in this session.
2. **Can the #1094 receipt drop or annotate its non-reproducible outer
   `log_sha256`?** *Why it matters:* it would make two runs' receipts directly
   comparable. *First step:* a maintainer decision. This package changes no
   selected script. *Blocked by:* any edit to `scripts/verify_frontier1094.py`
   touches the selected reproduction path.
3. **Do the same classes hold for the #1042 stages?** *Why it matters:* the
   #1042 receipt binds 457 artifact hashes, so byte determinism there would let
   reuse mode be checked across machines. *First step:* run
   `compare_payloads.py` on a cold `verify_frontier1042.py` run against
   `community-frontier1042-audit/selected-replay.tar.gz`. *Blocked by:* a cold
   run takes about 20 minutes plus the #799 baseline.

## Credit

The stage under test is Rohan Arun's #1094 (`complex-t16-rare-pattern-exchanges`)
on Jeremy Kothe's PR1087 strict verifier and the credited PR1018/1005/869/799/741
lineage. Douglas Colkitt wrote the selected replay driver and the receipts that
the reviewed archives come from. The gzip-container convention follows Maxime
Fleury's [reproducibility audit](../gzip-container-reproducibility/README.md),
which built on Antoine Olivier's replay findings. Related audits, which this
package does not repeat: [ancestry binding, seed 69](../frontier1094-ancestry-binding-seed69/README.md)
and PR1735 (certificate-to-replay binding).

Prepared by JosieElliston's donated Claude Code session 26, with substantial AI
assistance (Claude Opus 5.5), self-reviewed only. Apache-2.0.
