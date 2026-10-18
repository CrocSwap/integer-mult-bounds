# Make the selected invoice audit tolerate temporary-root aliases

The one-line repair in `REPAIR.patch` canonicalizes `work` before PR2158's
extraction containment checks. It fixes a real false rejection of benign
temporary-root aliases while retaining the file-only guard, resolved-member
containment, archive/member pins, and every invoice assertion. The complete
37-mutant replay still matches the original receipt: 31 mutations are rejected
by the invoice, and all six accepted mutations are rejected downstream.

This addresses [PR2158](https://github.com/CrocSwap/integer-mult-bounds/pull/2158)
at `8051d06df24704915fa7a6ec930a2c103a9f66f5`. The maintainer already diagnosed
the path alias and tried `TMPDIR=/private/tmp`; the latest c3c94c2e review records
a batch execution timeout after that workaround. **The diagnosis and workaround
are not claimed as new.** This contribution adds a portable source repair,
rejection regressions and a completed replay of that existing scientific audit.

## Exact cause and fix

Previously `prepare` compared a resolved member path against an unresolved
`src` or `fixture` root. A legitimate path such as `spelling/../work` names the
same directory as `work`, but it is not a lexical prefix of the resolved member.
The same mismatch occurs with macOS `/tmp` versus `/private/tmp`, or a Windows
directory junction. The resulting `unsafe archive member` assertion confuses a
path spelling with a containment failure.

The source fix is exactly:

```diff
 def prepare(work):
     """Extract the pinned PR1087 source and the archived selected fixture."""
+    work = work.resolve()
     src = work / 'src1087'
```

Both child roots now start in the same canonical coordinate system as every
resolved member. The existing pre-extraction validation still rejects relative
escapes, absolute escapes and non-regular members. The fixture archive retains
the same separate containment check. This is not a general hostile-filesystem
or concurrent symlink-race hardening claim; the existing trusted pinned archive
and private temporary-directory model is unchanged.

`audit.py` is the exact predecessor verifier with that single line inserted.
`verify.py` removes the unique inserted line and checks the reconstructed bytes
against the original source SHA-256 on every replay. `EXPECTED.json` is the
unchanged original receipt. All nine original external inputs are byte-pinned.
No original invoice or selected archive is edited, and no check is bypassed to
obtain the result.

## What is actually checked

The replay first demonstrates that the original function rejects a benign
dot-dot alias, then that the repaired function extracts both actual pinned
archives through the same kind of alias and returns canonical roots. Four bad
source archives exercise relative escape, absolute escape, symlink and directory
members; a separate bad fixture exercises its containment guard.

It then launches the minimally changed audit in an assertion-enabled isolated
Python process. That process executes its original positive control, all 37
mutations and all six downstream admission probes. The wrapper compares every
field and type of the emitted receipt with the unchanged predecessor receipt.
It does not replace the original scientific checks with aggregate counts.

Local validation also uses a real Windows junction for the temporary directory,
separately from the portable dot-dot regression. Execution evidence and its
limits are recorded in `VALIDATION.md`. The archive guard is intentionally not
assertion-disabled: `-O` is rejected because the retained invoice relies on
assertions.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 -I -B research/invoice-realpath-replay/verify.py
python3 scripts/research_package.py --package research/invoice-realpath-replay
```

Expected summary:

```text
PASS_INVOICE_REALPATH_REPLAY original_alias_rejected repaired_alias_passed traversal_controls=5 mutants=37 invoice_rejected=31 downstream_rejected=6
```

The repair can also be applied directly to the pinned original package using
`REPAIR.patch`; its original commands and original receipt then remain valid.
The wrapper's default replay writes only into private temporary directories.

## Scope, credit and stopping decision

The selected finite invoice findings belong to Aaron Wang / navinor and the
retained PR1087 invoice lineage, including Jeremy Kothe, Hao Yan, Rohan Arun,
the selected frontier audit and Josie Elliston's mutation-audit handoff. The
original source's attribution is retained verbatim in `audit.py`. Credit the
maintainer's efficient1200 review for the path-alias diagnosis and workaround.
This repair and regression wrapper were prepared by ywz65 with substantial
OpenAI Codex assistance. Apache-2.0; no independent human review is claimed.

The picker on base `6bd33bc0` selected the bit register model; its required
baseline passed, and current finite algebra scopes were already covered or
claimed. TASK.json records the change to this concrete review blocker and its
[canonical claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2158#issuecomment-6198945252).
The contribution stops at the source portability and exact replay obligation.
It is not a new mutation census, invoice theorem, selected-supplier cold replay,
complete multiplication audit, native runtime result or new kappa.

## Open next questions

Can the original PR incorporate the one-line repair and completed replay
evidence? Apply `REPAIR.patch` at the pinned head and rerun its unchanged commands
under a temporary-root alias. Original-author or maintainer integration remains;
no larger mathematical search is needed for this fix.
