# audit_local.py accepts non-centre cut gates (guard and regression fixture, no new κ)

**Finding.** The independent local auditor `research/gauge44-frames-x/independent/audit_local.py` climbs frames only in
sections A and B. In the cut it checks only gates whose source is one of the word's eight centres (the centre-path
rule). A cut gate with any other source is applied to the scalar map but never frame-checked. A word can therefore move
priced work into the unpriced cut and still pass, with an understated paid profile.

**Counterexample** (`inputs/PROBE-CUT-502.json.gz`). Start from the genuine base word of the pivot-566+554 T74 supplier
(`inputs/BASE-WORD.json.gz`, PR #1672). Make width-9 helper 502 entering (start frame of dimension 1 instead of 0), so its
width drops from 9 to 8. Cancel its initial-value leak with four cut gates `200/203/205/206 += ±½ · 502`, and re-time its
two A-section writes into B.
- The unchanged auditor run with `--main` **passes** it: compensation 7,204 gates instead of 7,208, 193 entering helpers instead of 192, local
  profile `{2: 501, 3: 415}` instead of `{2: 500, 3: 416}`. That is one rank level less, about 2.1M units per call, which
  would be worth roughly +8e-8 κ through the hosting.
- The native provider chain **rejects** it at its second step: `hpe_emit_local.py` fails with `emitted column mismatch`
  at register 153 (`evidence/NATIVE-PROBE.txt`). The base word passes all five native steps.

So the gap does not affect claims whose admission includes the native chain, which every T74 claim does. It does
affect any acceptance that relies on `audit_local.py` alone.

**Guard** (`guard.py`, standard library). Every cut gate must be an `add` whose source is a centre and whose target is a
target row (`v <= t < 2v`). This is the structure of every genuine word, and the native emitter relies on it.
- It accepts all 146 genuine words found at the base commit (every `CANONICAL-WORD`/`FULL-WORD` file with a cut) and both
  supplier words (`evidence/GUARD-GENUINE-WORDS.json`).
- It rejects exactly the probe's four gates (`evidence/GUARD-PROBE.json`).

`audit_local.py` is pinned by hash in 421 files at the base commit, so this package does not modify it. The guard is
additive: run it alongside the auditor, or fold it into a new auditor version.

## Reproduce

```sh
python3.12 scripts/research_package.py --package research/audit-local-cut-centre-guard
python3 -B research/audit-local-cut-centre-guard/guard.py WORD.json.gz
```

`verify.py` checks the input pins and runs the unchanged auditor on the base and probe words; both pass, and the
receipts equal `evidence/AUDIT-*.json`. The pins cover the three words and two repository files, which are declared in
both `VERIFY.json` and `SOURCES.json`: the auditor, and the parent `CANONICAL-WORD.json.gz` (PR622 baseline558
split-centres) that its `--main` interface check reads. The package plus those two files is enough: `verify.py` also
passes in a Git-free export that contains nothing else. It then runs the guard on all three words and two mutation controls (a
non-centre cut source, a non-target cut row). It takes a few seconds. The native rejection is recorded evidence, not
rerun.

## Scope

This audits one condition: frames of cut gates in the local auditor. It is not a new construction and gives no κ. The
counterexample is built on the pending T74 supplier's base word, which is not in main; the auditor and guard are the
same for the selected line's words.

## Open next questions

- **Version the guard into the auditor.** The first step is done. ywz65's
  [handoff](https://github.com/CrocSwap/integer-mult-bounds/pull/2478#issuecomment-6192363481) found seven registered
  packages that actually call `audit_local.py`; eleven more only hash it, and five use other checkers. Their committed
  words pass `guard.py` with the same 176-gate cut (re-run here on the six distinct words). Their admitted mutation
  families do not change the cut, so no existing claim is shown to use the gap. Adoption by those callers is blocked on a
  maintainer decision about versioning a pinned auditor.
- **Check the other unpriced sections.** The precondition, the derived compensation and the frame-free cleanup could
  admit analogous counterexamples. For each one, state the structural rule the native emitter assumes and test it with
  a constructed word, as here.

## Credit

The auditor is icekylinx's gauge44-frames-x package. The words are PR #1672's (Jeremy Kothe / LeverRank) pivot-554 kernel on
PR #1625's pivot-566 words (mdumitrean), in the PR #1319/#1297 lineage (Rohan Arun) and its retained ancestry. The native
chain is PR635's vendored scripts, run through PR #1186's toolkit. The registered-consumer screen is ywz65's (see the
open questions). See `NOTICE.md`.

Prepared by Marius-Paul Dumitrean with substantial AI assistance (Anthropic Claude, via Claude Code). Apache-2.0.
