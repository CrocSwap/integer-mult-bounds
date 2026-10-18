# Checked marshal copies: 1.89x faster audit sub-stage of the selected final stage

**Tooling only (verifier engineering).** No κ, certificate, supplier, frontier or
pinned-source change. Track `verifier-engineering`, card `replay-runtime`, scope
refined to one profiled sub-stage (chooser OS nonce `343b846376b457288e1b5a2336a887c0`,
priority revision 3). Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; selected-record
SHA-256 `10b9e340…85fa32`.

## What is slow

The selected record's only stage after its #1042 baseline,
`research/complex-t16-rare-pattern-exchanges/verify.py`, runs the frozen PR1087
`verify_t16.py`. Its `audit` sub-stage is the slowest: 32.6 s of 57.6 s in the
maintainer receipt (`research/community-frontier1094-audit/selected-replay.tar.gz`),
18.0 s of 32.0 s here. The pinned script is `audit_allcold.py`, SHA-256
`1467a2acb654e62552c69fb9a7c4c85f70a02120881d222313865058ab71a6cc`, the same bytes as
`research/gauge44-slots-t16/code/audit_allcold.py`, which the cold baseline1042 `t16`
stage also runs.

cProfile attributes about 80% of the profiled sub-stage to `copy.deepcopy`. Each of
the 15 mutation controls deep-copies the whole hosted T16 template
(`q=copy.deepcopy(ct)`), and each of the 16 audits deep-copies every source event.
That is 4,838 top-level calls and about 46 million recursive `deepcopy` frames.

## The change

[`fast_copy.py`](fast_copy.py) is a drop-in launcher. Use
`python3 -B fast_copy.py RUN_PORTABLE SCRIPT ARGS...` in place of
`python3 -B RUN_PORTABLE SCRIPT ARGS...`. It checks both files against a SHA-256
allow-list and runs the pinned `run_portable.py` through `runpy`, as before. It
replaces only `copy.deepcopy`. For a top-level `dict` or `list`, the copy is
`marshal.loads(marshal.dumps(x))`. That copy is used only when all of the following hold:

- marshal accepts the value: core builtin types only, so dict/list subclasses and
  custom objects raise `ValueError`;
- the copy has the same type;
- the copy compares equal (`==`; NaN, cyclic or over-deep values fall back).

Every call with a `memo` also uses the original `deepcopy`, as does every value
that fails one of these tests. marshal format 4 writes repeated objects as
back-references, so aliasing inside the copy is kept, as deepcopy keeps it. Every
container in the copy is new. No verifier source is edited, nothing is cached, and no
check or control is skipped.

## Evidence

`verify.py` does the following, all in fresh directories outside the checkout:

1. **Fixture = the selected stage itself.** It extracts the archived gauge44
   provider files from `selected-replay.tar.gz` and passes them as `--local` to the
   unchanged `complex-t16-rare-pattern-exchanges/verify.py`. That runs all 11
   `verify_t16.py` sub-stages and must print `PASS_T16_RARE_PATTERN_EXCHANGES
   0.001672660197076918`. Its `ASYNC-AUDIT.json` must equal the archived selected
   receipt byte for byte.
2. **A/B on the same inputs.** It reruns the `audit` sub-stage on fresh copies of
   that stage's `base`/`hosted` inputs with verify_t16's exact environment. Runs
   alternate between the pinned `run_portable.py` (legacy) and `fast_copy.py`. Each
   run must reproduce, byte for byte, the in-stage `ASYNC-AUDIT.json`,
   `OWNERS-AND-PROFILE.json`, `IDLE-REMAINDER-FRAMES.json`, the newly written
   `hosted/IDLE-REMAINDER-FRAMES.json.gz` and the merged stdout/stderr `audit.log`.
   All 4,838 deepcopy calls must take the marshal path (`fallback: 0`).
3. **Controls.**
   - A hosted template with `physical` reduced by one is rejected (`AssertionError`)
     by both launchers.
   - A copy of the script with one appended comment is refused by the allow-list.
   - An **identity "copy"** (no copy at all) is detected. Notably, the pinned audit
     itself still exits 0 then: every control mutates the audited template in place,
     and the written reports change (for example, provider count 143 instead of 144,
     and one idle-remainder frame missing). Only the byte comparison catches it, so
     the comparison is load-bearing.
   - In-process semantics: aliasing is kept, copies are independent, and the
     fallback runs for a dict subclass, NaN, a custom object, a cyclic list and an
     explicit memo.

Measured on macOS (Apple silicon), same host and fixture, with
`verify.py --work DIR --rounds 3` (alternating order). All rounds produced
byte-identical outputs:

| Interpreter | Legacy audit, 3 rounds (s) | `fast_copy.py` audit, 3 rounds (s) | Median speedup |
|---|---|---|---:|
| CPython 3.12.13 (registered replay interpreter) | 22.37, 22.27, 22.50 | 9.05, 9.06, 9.21 | **2.47x** |
| CPython 3.14.7 | 17.85, 18.31, 17.79 | 9.43, 9.46, 9.47 | **1.89x** |

On 3.12, the selected final stage spends about 13 s less in this sub-stage. The
maintainer's Linux receipt has a 32.6 s audit inside a 57.6 s stage, so the absolute
saving there may be larger, but that host was not measured. Timing has no pass
threshold.

## Reproduce

```sh
python3 scripts/research_package.py --package research/audit-allcold-fast-copy --check-only
python3.12 scripts/research_package.py --package research/audit-allcold-fast-copy
# Optional: more timing rounds and a kept RESULT.json
python3 -B research/audit-allcold-fast-copy/verify.py --work /fresh/dir/outside/repo --rounds 3
```

The registered replay takes about 1–2 minutes: one selected-stage run plus one A/B
round and the controls.

## Limitations

- **Not wired into `make frontier1094-verify`.** The frozen `verify_t16.py` calls
  `run_portable.py` directly. Using the launcher needs an opt-in driver or a
  maintainer-approved hook (open question 1).
- **One script hash.** The allow-list has the single audited `audit_allcold.py`.
  The other nine `audit_allcold.py` variants in `research/` are not checked here.
- **Fixture source.** The fixture's `--local` files come from the maintainer's
  archived selected replay, not a fresh cold baseline1042 run. The archived
  `ASYNC-AUDIT.json` check binds them to the selected receipt. A cold
  `make frontier1094-verify` was not rerun.
- **Indirect inputs.** `verify_t16.py`'s upstream pins (`data/UPSTREAM-PINS.json`)
  are checked by the stage itself, but they are not listed as this package's CI
  inputs.
- **Same interpreter.** The `marshal` format is used only in-process, so both
  sides of every copy run under the same interpreter.

## Open next questions

The structured list is in [TASK.json](TASK.json).

1. **Opt-in wiring.** Should a new driver offer a source-bound, opt-in path that
   runs the audit sub-stage (and the cold baseline1042 `t16` stage) through this
   launcher? That is what turns the measured saving into faster reviews. First
   step: an opt-in flag in a new driver, not in the frozen `verify_t16.py`, that
   substitutes the launcher only for allow-listed hashes. It is blocked on a
   maintainer decision about wrapping the frozen stage runner.
2. **Other scripts.** Which other pinned verifiers spend most of their time
   deep-copying JSON trees for mutation controls? There are ten distinct
   `audit_allcold.py` hashes, plus other `reject()` helpers. First step: profile
   each on its own committed fixture and add a hash only when it has byte-identical
   receipts. Blocker: many need a long cold upstream replay first. The concurrent
   mutant-coverage audit [PR1959](https://github.com/CrocSwap/integer-mult-bounds/pull/1959)
   lists the same nine hashes as its open question 1, for coverage rather than
   speed. One per-hash fixture could serve both questions.
3. **The remaining 9 s.** These are spent mainly in `audit()` itself: 16 passes
   over 69,120 helper roles. Reducing that would need an adapter that changes
   audit code, with its own equivalence argument.

## Credit

The audited code is from the retained gauge44 / PR1087 lineage:

- the `audit_allcold.py` controller audit and its mutation controls (OpenAI Codex
  in the original packages);
- Hao Yan's (@FanPUYen) PR858 T16 controller;
- the `run_portable.py` wrapper from `complex-k492-owner-repair`;
- PR1094 (Rohan Arun) on Jeremy Kothe's k8/T16 construction;
- the maintainer's frontier1094 audit receipt (Douglas Colkitt).

Earlier opt-in, byte-identical replay adapters set the pattern followed here:
PR1880 (joint-dual scans), PR1874 (PR589 hashing), PR1646 (phase recipes) and
`frontier1042-lec-parallel`.

Related, concurrent: Josie Elliston's
[PR1959](https://github.com/CrocSwap/integer-mult-bounds/pull/1959) runs the same
pinned audit in-process on the same archived template. It records which assertion
rejects each shipped control and new semantic mutants, and its harness uses the
checked `marshal` copy from this package. The two are complementary. This package
shows that the shipped controls depend on real copies for isolation (the
identity-copier control). PR1959 maps which of the audit's assertions those controls
reach.

Prepared by jackmgaller with substantial Claude Code (Claude Opus 5.5) assistance.
New files are Apache-2.0.
