# Post-emit read-set of the 15 audit-unread hosted-template fields

**Scope.** This package machine-checks one hosting transfer claim of the selected #1094 chain.
The frozen PR1087 `code/audit_allcold.py` acceptance audit does not read 15 fields of the hosted
template it checks (`cover`, `m`, `version`, `port_restriction`, `provider_dispatch`,
`replica_lift`, `route_semantics`, `supplier_substitution`, `expanded_scalar_interface`,
`hosting.rule`, `hosting.scope`, `hosting.idle_remainder_semantics`, `hosting.owner_map_sha256`,
`async_schedule.scope`, `async_schedule.source_plan_sha256`). Josie Elliston's
[`research/t16-audit-mutant-coverage`](../t16-audit-mutant-coverage/README.md)
([PR #1959](https://github.com/CrocSwap/integer-mult-bounds/pull/1959)) asserts "a text search of
the PR1087 archive and the maintainer frontier1094 scripts finds no reader of the 15 unread fields
in the hosted template after `emit`", and labels it "a text search, not a proof". This package
replaces the text search with a pinned AST inventory of the whole consumer universe and maps the
whole-object channels through which those fields could still reach a post-emit acceptance
decision. It makes no kappa, certificate, supplier or frontier change, and it is not a cold
replay or a mutation audit.

## Result

Universe: all 57 `*.py` members of the pinned
`research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz` (SHA-256
`d4acf04daef85d4514f80ec5fcd2492d0c60e5d6c49fa71b3e6523f8db2dea86`) plus five main-tree files
(`scripts/verify_frontier1094.py`, `research/community-batch1099-audit/check_frontier1094.py`,
the selected stage driver `research/complex-t16-rare-pattern-exchanges/verify.py`, and the
in-process import closure of `check_frontier1094.py`:
`research/t16-owner-audit-seed67/verify.py` and
`research/pending-claims-independent-pricing/sweep.py`). Every file is SHA-256 pinned in
`EXPECTED.json`; the post-emit consumer closure is `code/audit_allcold.py`,
`code/invoice_allcold.py`, `code/assemble.py`, `code/assembly_controls.py`,
`code/bit_supplier_controls.py` and the audit's in-process helpers `code/witness.py`,
`code/generated_identity.py`.

**S1 — no post-emit name-directed read.** Of the 58 name-directed occurrences of the 15 field
names in the universe, exactly five are in the post-emit closure, and all five are output-receipt
construction keys (`scope=` in the `dict(...)` builders at `assemble.py:234`,
`assembly_controls.py:246`, `audit_allcold.py:231`, `audit_allcold.py:253`,
`invoice_allcold.py:310`). A dict()/dict-literal key writes another dict; it cannot read the
template. Zero post-emit occurrences are reads, writes, presence tests or opaque calls of any of
the 15 names. This is the machine-checked replacement for PR1959's text search.

**S2 — complete occurrence inventory.** All 58 occurrences are pinned with file, line, syntactic
context and access class in `EXPECTED.json`, so source drift invalidates the receipt. The only
semantic reads of any of the 15 names in the entire universe are three pre-emit read-modify-writes
of `route_semantics` (each overwrites its `helper` subfield during construction:
`restore_parent.py:62`, `t16/build_parent.py:117`, `code/emit_allcold.py:102`) and two reads of
*other* objects that happen to share a field name (`t16/build_parent.py:63` reads the source
SPEC's dimension `source['m']`; `verify_t16.py:120` and `scripts/verify_frontier1094.py:101` read
an assembly receipt's `scope`). Nothing in the pinned universe reads the hosted template's 15
fields.

**S3 — dynamic and whole-object channels.** The 54 dynamic-access sites of the template variables
(`ct`, `t`, `q` in the audit; `template` in the invoice) are pinned with excerpts. There is no
unbounded top-level dynamic read: the single top-level dynamic subscript is
`audit_allcold.py:97`, `for key in ('exact_data_phase_recipe_sha256','adapter_policy'): assert
t[key]==parent[key]`, whose key set is finite and disjoint from the 15 fields. The two top-level
presence tests (`audit_allcold.py:95`, `invoice_allcold.py:178`) probe retired field names
(`local_programs`, `exact_local_clifford_recipe_sha256`, `residual_adapter_sha256`), not the 15.
No post-emit code iterates, serializes, hashes or compares the template object itself in-process;
the one `copy.deepcopy(ct)` (`audit_allcold.py:190`) is the audit's own mutation harness.

**Channel map — how the 15 fields can still reach acceptance.** Through whole-object byte
equality only, against receipts produced by the same emit run:

| Channel | Pinned statement | Effect on a changed field |
| --- | --- | --- |
| audit stage | `audit_allcold.py:185` recomputes `sha256` of the template file bytes and requires `== summary['template_sha256']` (`HOSTED.json`, written by `emit_allcold.py`) | detected unless `HOSTED.json` is re-emitted consistently |
| invoice stage | `invoice_allcold.py` `run()`: `template_hash=contenthash(template_path)` must equal `control['complex_template_sha256']` (ASYNC-AUDIT.json), `owners['template_sha256']` (OWNERS-AND-PROFILE.json) and `summary['template_sha256']` (HOSTED.json) — the four-way binding | detected unless all four values are consistent with the changed bytes |
| maintainer check | `check_frontier1094.py:18` binds `a.TEMPLATE` (the **ROUND20 parent** template, a pre-emit artifact) by file hash to `research/t16-owner-audit-seed67/SOURCES.json`, and `geometry()` reads only `execution_schedule` and `recipe` from it | does not touch the hosted emit output |

Consequence (what would change downstream): with the emit-produced receipts kept consistent, no
post-emit acceptance predicate in the pinned universe distinguishes any values of the 15 fields.
Their presence in the hosted template is provenance/documentation; the chain's protection of them
is the emit-stage byte-hash provenance binding, not semantic validation. PR1959's prose ("the
audit alone accepts changed pooled-slot times and the 15 unread fields") therefore extends from
`audit()` alone to the whole pinned post-emit chain, modulo the file-hash bindings above.

**S4 — detector self-test (corruption control).** `verify.py` parses ten synthetic probe forms
(subscript read, attribute read, dict() keyword, dict-literal key, `get()` argument, subscript
write, membership test, unbounded dynamic subscript, bounded dynamic subscript, top-level
iteration, top-level hash) and fails unless every one is classified as intended. A single
injected `ct['cover']` in any pinned file would trip S1 and the EXPECTED inventory comparison.

## What this does not establish

- This is static analysis of pinned bytes. Receiver binding for the dynamic sites uses the
  declared template variables (`TEMPLATE_VARS` in `verify.py`); renamed receivers would need a
  re-derivation, though any byte drift already fails the pins.
- It certifies the pinned universe, not arbitrary future code, and it is not a proof of semantic
  non-interference. The `engines/moment.py`, `engines/base_two_moment.py` and `engines/outer.py`
  modules that `assemble.py` loads from its own package directory are outside the frozen archive
  and were not scanned; `assemble.py` passes them profile dictionaries, not the template (visible
  in the pinned site inventory).
- It does not replay the selected chain, does not mutation-test any stage, and does not discharge
  the all-size/compiler, precision, hosting or restoration obligations themselves. The template
  owner-map binding left open by PR1959's open question 2 is untouched.

## Reproduce

```sh
python3 -B research/hosted-template-postemit-fields/verify.py
python3.12 scripts/research_package.py --package research/hosted-template-postemit-fields
```

Stdlib only, CPython 3.10+. `verify.py --write` regenerates `EXPECTED.json` after a deliberate
source change. Checked on CPython 3.13 and 3.12 on Windows, identical output.

## Open next questions

1. **Read-set receipt for the other `audit_allcold.py` versions.** PR1959's open question 1 lists
   nine other hashes of that file in the repository. First step: parametrize `verify.py` by
   archive member and re-run the inventory on the #1042 audit archive. Blocked by: locating each
   version's hosted template in the retained receipts (PR1959's own blocker).
2. **Consumers of the emitted `scope` receipts.** Five post-emit receipts carry a `scope=` string;
   which downstream readers (human or script) consume them? First step: a name-directed scan of
   `report['scope']` consumers in the replay drivers and ledger tooling. Blocked by: nothing.
3. **Bind the parent/hosted template distinction.** `check_frontier1094.py` pins the parent
   template bytes; no stage pins the hosted template bytes against a pre-emit value. First step:
   a two-line pin of the hosted template in the frontier1094 driver, as PR1959's open question 2
   proposes for the owner map. Blocked by: a maintainer decision on wrapping the frozen driver.

## Credit

The audited claim and the 15-field census are Josie Elliston's (PR #1959,
`research/t16-audit-mutant-coverage`), prepared with Claude Code assistance. The frozen chain code
is Jeremy Kothe's PR1087/#870 lineage with T16 edits from Hao Yan (@FanPUYen) #858; the selected
run is Rohan Arun's PR1094; the frontier1094 composition is Douglas Colkitt's; the owner audit is
Josie Elliston's `research/t16-owner-audit-seed67`; the pricing sweep is Sagar Thakrar's
`research/pending-claims-independent-pricing`. Adjacent concurrent work:
[PR #2158](https://github.com/CrocSwap/integer-mult-bounds/pull/2158) (Aaron Wang, agent-43)
mutation-tests `invoice_allcold.py`'s predicates — a dynamic method on one stage; this package's
static, universe-complete inventory complements it and neither supersedes the other.

Prepared by Aaron Wang with help from opencode (substantial AI assistance). Apache-2.0.
