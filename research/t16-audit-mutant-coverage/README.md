# Mutant coverage of the selected T16 controller/owner audit

**Scope.** This package audits one checker of the selected #1094 record: the frozen PR1087
`code/audit_allcold.py` (SHA-256 `1467a2ac…`). The selected stage
`research/complex-t16-rare-pattern-exchanges/verify.py` runs it through `verify_t16.py`, with
`--mutation-controls`. The fixture is the selected hosted template archived in
`research/community-frontier1094-audit/selected-replay.tar.gz`. The question is which of the audit's
acceptance predicates its 15 shipped mutation controls actually reach. For the predicates they miss, does a
targeted semantic mutant get rejected? This is an adversarial audit of an acceptance boundary. It makes no
κ, certificate, supplier or frontier change, and it is not a cold replay.

## Result

The pinned audit runs unchanged and in-process; the verifier only records which line rejects each mutant.
On the unmutated template it reproduces every field of the archived selected `ASYNC-AUDIT.json` except the
two mutation-run fields.

| Mutant set | Count | Rejected | Accepted | Further lines with an `assert` reached first |
|---|---:|---:|---:|---:|
| Shipped controls (exact text of the pinned control block) | 15 | 15 | 0 | 8 of 42 |
| New targeted semantic mutants | 35 | 34 | 1 | 20 |
| One-field census of the template | 111 | 92 | 19 | 6 |

- **Shipped controls are concentrated.** Four of the 15 shipped controls are rejected first by line 94 (the
  whole provider-registry equality). Three are rejected by line 152 and three by line 159. In the
  single-provider selected run, the per-provider controls exercise one equality, not separate predicates.
- **Predicates first exercised here.** Every new semantic mutant except one is rejected, by an
  `AssertionError` at the intended statement:
  - the idle window, from both sides: the owner replica changed only, so a helper runs before its child goes
    idle or after the child is swept (line 156);
  - the wrong side of the idle pair, and a width-nine helper running past the child's rank (line 156);
  - overlapping axis cells across two calls (line 163);
  - a gap in the hosted pending prefix, with the route and pooled slot moved together (line 178);
  - schedule list order and retiming (lines 114, 121, 122 and 129);
  - pooled-slot count, key and field binding (lines 169, 171, 172 and 173);
  - the retired top-level `local_programs` (line 95).
- **Accepted: 19 path mutations, in three groups.**
  - *Pooled-slot `time`.* Line 172 compares a pooled slot's roles fields but not its `time`. The audit
    itself would therefore accept a template whose pooled times differ from the frozen owners. See the
    binding below for why this does not affect the selected fixture.
  - *15 fields that `audit()` never reads.* These are `cover`, `m`, `version`, `port_restriction`,
    `provider_dispatch`, `replica_lift`, `route_semantics`, `supplier_substitution` and
    `expanded_scalar_interface`, plus `hosting.{rule, scope, idle_remainder_semantics, owner_map_sha256}`
    and `async_schedule.{scope, source_plan_sha256}`.
  - *Three partial checks.* The audit reads `loop_order` but only requires one sentence to be present,
    so appended text passes. It reads named subfields of `hosting` and `async_schedule`, so an extra key
    in either passes.

  A text search of the PR1087 archive and the maintainer frontier1094 scripts finds no reader of the 15
  unread fields in the hosted template after `emit`. The files that mention those key names are their
  producers (`emit_allcold.py`) or stages that run before `emit`, such as `restore_parent.py`,
  `build_parent.py`, `lift16.py` and `prepare_global.py`. `invoice_allcold.py` and `assemble.py` read
  none of them. This is a text search, not a proof.
- **Cross-stage binding that no selected stage checks.** The audit checks the hosted template.
  `lift16` and `independent-t16` check the frozen `data/OWNERS.json.gz` instead, and the final binding
  compares only counts and profiles. The verifier checks the link directly. The template's
  `hosting.pooled_slots` is exactly the frozen owner list: 69,120 roles, with `time` fields included.
  `hosting.owner_map_sha256` is the SHA-256 of that gzip. So for the selected fixture, the one field the
  audit ignores equals the time that `independent-t16` checks against invocation times. Each stage of the
  selected chain is deterministic. The link between them was previously implied by that determinism, not checked.
- **Eight lines with an `assert` are not reachable by any template-only mutation.** The other 34 of the 42 are reached. Lines 98, 157 and 182
  depend only on base inputs (DATA-PHASES and the provider artifacts) once earlier lines pass. Lines 123,
  160, 161, 164 and 167 follow from earlier assertions or from how the audit builds the values: line 123
  from 120 and 122; lines 160 and 161 from how `sigma` is built; lines 164 and 167 from lines 103, 148
  and 152.
- **Incidental exceptions.** Two census mutants are rejected by `TypeError` and `IndexError` at line 106,
  before any predicate: an appended `None` event, and an out-of-range global `source_event`. The shipped
  harness counts these exception types as rejections. Every other rejection is an `AssertionError`.

**Conclusion.** For the selected fixture, no missing implication was found in this checker. Each of
its 34 reachable assertion lines rejects some mutant first. This is line coverage: on a line with a
compound condition, such as lines 94, 152 and 156, not every conjunct has its own mutant.

What `audit()` implies for *any* template is narrower than what is checked here for the *selected* one.
The audit alone accepts changed pooled-slot times and the 15 unread fields. For the selected template,
`verify.py` checks separately that the pooled owners, including their times, equal the frozen owners
that `independent-t16` checks. The unread fields have no reader after `emit` (text search).

## Reproduce

```sh
python3 -B research/t16-audit-mutant-coverage/verify.py      # ~70 s; compares with EXPECTED.json
python3.12 scripts/research_package.py --package research/t16-audit-mutant-coverage
```

Stdlib only; needs CPython 3.10.12+ (tar `filter='data'`). Checked on CPython 3.10, 3.12 and 3.14 (macOS arm64),
with identical output. `--write` regenerates `EXPECTED.json`. Copies use a `marshal` round trip, checked once
for equality, following jackmgaller's PR1939 observation that `deepcopy` dominates this audit's time.

**Not checked:** mutations of the base inputs (DATA-PHASES, provider artifacts, parent template) and the
module-level provider checks in lines 20–80. Other stages are also not mutation-tested: `invoice_allcold.py`,
`assemble.py`, `indep16.py` and the #1042 ancestry. There is no cold rebuild, and no Linux or Windows run.

## Open next questions

1. **Same receipt for the other `audit_allcold.py` versions.** Why it matters: PR1939's handoff lists nine other
   hashes of this file in the repository, and each has its own shipped controls. First step:
   parametrize `verify.py` by archive member and script hash, and use the #1042 audit archive as the
   fixture. Blocked by: locating each version's hosted template in the retained receipts.
2. **Bind the template owner map in the replay driver.** Why it matters: today the template-to-OWNERS link
   rests on deterministic stages, not on a check. First step: add the two-line binding (see this
   package's `template_to_frozen_owners_binding`) to a successor driver; the frozen PR1087 code stays unchanged.
   Blocked by: a maintainer decision on whether to wrap the frozen `verify_t16.py`.
3. **Mutation-test the invoice.** Why it matters: `invoice_allcold.py` carries the finite inequalities
   (prefix 397 < 512, row 16,469 < 20,161) and has no mutation-control block of its own. Whether the 69 admission controls cover its inputs was not checked. First step: the same in-process
   harness on its `run()` with one-field template and receipt mutants. Blocked by: nothing; it was out of
   this session's time.

## Credit

The audited checker and its shipped controls are the PR1087 archive's `code/`, byte-identical to Jeremy
Kothe's #870 gauge44-barch-t16 code. Its docstring credits OpenAI Codex, and it includes the T16 edits from
Hao Yan's (@FanPUYen) #858. Rohan Arun's #1094
supplies the selected exchanges and archived run. The maintainer's frontier1094 audit archived the fixture.
jackmgaller's PR1939 identified the copy cost and the copy-isolation dependence of the shipped controls.
Session 26 (PR1824) established that the final stage's outputs are byte-stable across interpreters. My PR1091
is an independent owner/event-window recount, a different checker from the one audited here.

Prepared by Josie Elliston (JosieElliston) with substantial Claude Code (Claude Opus 5.5) assistance in a
donated session. Apache-2.0.
