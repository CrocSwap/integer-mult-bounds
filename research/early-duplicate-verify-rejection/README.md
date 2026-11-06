# Early duplicate-VERIFY rejection candidate

This opt-in package proposes a narrow parser-policy alignment: reject duplicate object members in VERIFY.json during registered metadata validation and replay planning, as the existing committed exporter already does. The patch is retained as [STRICT-VERIFY.patch](STRICT-VERIFY.patch) with bounded tests on copied exact tooling in isolated synthetic Git repositories. Shared scripts, workflows and the selected record remain untouched. Adoption is a separate maintainer decision.

The observed issue is an interpretation/exportability gap, not scientific false acceptance, a security escape or violation of a documented metadata-pass-guarantees-export promise. Export and metadata validity are already distinct predicates. A duplicate manifest is described as otherwise valid under the registered final-member predicates, rather than universally valid JSON metadata.

## Observed boundary and bounded evidence

Before the public claim, the coordinator preserved four actual calls of the unmodified canonical tooling: healthy metadata/export exits0/0, and duplicate-inputs metadata/export exits0/1. The duplicate calls used the same397-byte committed VERIFY and final inputs=[input.txt]. The earlier inputs=[missing.txt] member was ignored by the ordinary registered parser; the credited exporter rejected the exact bytes with `duplicate export JSON key: inputs`. No inert fixture command or mathematical/native workload was dispatched. The original raw observation records remain outside this package in session-02/prototype; this paragraph does not claim this metadata author reran them.

The first new-harness replay passed on CPython3.12.14 in39.68seconds: nine committed fixture cases, 144 actual source CLI outcomes (100 accepted,44 rejected),28 inert marker dispatches, and nine temporary `git apply --check`/apply pairs. Each case tests original and patched readers under normal and optimized child Python (these inner modes are distinct from a separate outer optimized-harness replay) through metadata validation, planning, export and registered inert-marker dispatch. Four object-key forms (same-value, conflicting, escaped and nested) reject before dispatch in the patched readers. Positive controls retain behavior, including TASK/SOURCES final-member parsing and numeric extensions. The repeated-input-array limitation is demonstrated explicitly. The normalized outcome-table SHA256 is `bfdbc3acb6cc9e66ee8766654a9c196d9d2c8331039663516de610a0edff7562`.

The first replay is a diagnostic, not a substitute for final registered replay, export/committed-byte checks, publication or hosted CI. Those delivery checks are recorded with the PR and handoff when observed. Every replay emits its full deterministic outcome table and package hashes; optional `--raw-context-out OUTSIDE_PACKAGE.json` also retains actual command arguments, times, streams, fixture heads and working-source phases. Source programs run only in synthetic repositories; exported fixtures use the same committed manifest bytes while the candidate runner patch is deliberately in the temporary working copy.

## Scope and provenance

[verify.py](verify.py) authenticates the three retained tooling/data files in [SOURCE-PINS.json](SOURCE-PINS.json), applies the patch to temporary copies and exercises actual CLI boundaries. The unchanged exporter is a comparison control. The complete original portable-replay card and explicit CHANGED/partial outcome are in [TASK.json](TASK.json). [SOURCES.json](SOURCES.json) pins the canonical catalogue, selected record, registered runner and exporter as provenance. Runtime vendored bytes are package-local; no external live inputs are declared.

The change is VERIFY-only object-member rejection. It does not establish complete exportability parity: a unique-key manifest with `inputs=["input.txt","input.txt"]` can still pass registered validation/planning while export rejects the repeated list declaration. That separate list policy is intentionally outside this candidate. TASK/SOURCES parsing, catalogue-card/--print-card and other provenance readers, numeric policies and unrelated schemas are unchanged. Existing aliromman[PR5728](https://github.com/CrocSwap/integer-mult-bounds/pull/5728), verified head70441d90c78bdfc48aed772d2b45e05d5a38e4fb, already implements and tests duplicate committed-VERIFY export rejection; that guard and result are credited prior work. [PR5726](https://github.com/CrocSwap/integer-mult-bounds/pull/5726), head20bed137e8807376f3124dd6d03fc076e595b016, separately rejects ambiguous coordination metadata. No predecessor scientific suite is replayed or recounted as a new result.

## Run the tooling fixtures

Requires a POSIX host, CPython3.12, its standard library and a working Git CLI on PATH. macOS was observed locally; Windows is unqualified. No install step is supplied. The standalone harness creates its own temporary repositories and does not require the original repository's Git checkout or pending foreign Git objects. This is not a Git-free or empty-PATH replay claim.

```sh
python3.12 -I -B research/early-duplicate-verify-rejection/verify.py
python3.12 -I -O -B research/early-duplicate-verify-rejection/verify.py
python3.12 -B scripts/research_package.py --package research/early-duplicate-verify-rejection
```

The two registered commands have180-second caps. Their dispatch is tooling-fixture execution, not a native or mathematical verifier replay. Registration's ready status supplies explicit opt-in commands; it does not supply scientific or adoption acceptance.

## Adoption limits

The legacy duplicate-manifest inventory, supported-platform matrix and historical regression suites are incomplete. Planner fixtures select the package through newly added package files; they test intake rejection and the matrix, not input-only invalidation causes, `--explain-plan` or `--github-output` sidecars. Positive fixture archives are compared byte-for-byte and their manifest payload/inventory inspected; full package export authentication is a separate delivery check. Child CLI process groups have bounded timeouts; the known inert marker has its own five-second registered cap and no children. This is not a general descendant-cleanup guarantee. The proposed planner rejects a duplicate-key VERIFY while reading it even when that package would otherwise be unselected, so inventory all registered manifests before shared adoption rather than checking only the current changed-package list. Changing shared replay controls can select every registered package; this package does not authorize or perform that rollout. The patch's source head must be refreshed and its policy approved before live adoption. Existing path, pin, timeout and command validation retain their authority; parser consistency does not authenticate a mathematical claim. All five selected assumptions remain, with no supplier, physical tariff, multiplier, kappa or frontier result.

## Open next questions

1. **Decide shared adoption after an inventory.** Review the patch and scan committed VERIFY manifests for duplicates without dispatching their commands. Record how existing ambiguous manifests would be handled. The blocker is the incomplete legacy inventory and maintainer policy decision.
2. **Validate an approved rollout at an exact head.** Refresh source pins, run the relevant existing onboarding/export tests and a separately budgeted platform fixture matrix. Historical/platform coverage and full shared-control CI fanout remain outside this candidate.

## Credit

Prepared for ToikY with substantial source-aware OpenAI Codex assistance. See [CREDITS.md](CREDITS.md), [NOTICE](NOTICE) and [LICENSE](LICENSE). Douglas Colkitt's runner, Tekalign's exporter and aliromman's5728/5726 strict-parser work retain attribution. AI role separation is not independent human or proof-kernel acceptance.
