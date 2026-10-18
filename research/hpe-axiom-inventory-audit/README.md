# HPE axiom-probe inventory audit

The retained standalone HPE verifier can print `PASS` after its axiom checks
silently lose coverage. Removing all queries makes it report **0 results**.
Indenting all 42 queries has the same effect, although Lean 4.21 accepts the
indentation and emits the reports. This package reproduces that driver behavior
and supplies a proposed [repair](repair.patch). It establishes no false HPE
theorem and no new multiplication bound.

The original driver, Lean files, selected record and frozen evidence are
unchanged. Apply the patch only in a separately reviewed successor. Its explicit
42-name inventory must be deliberately maintained when the intended theorem
inventory changes.

## Evidence and repair

The audited driver is `research/hyperplane-end-lean/verify.py`, SHA256
`2b94b629b2c5d091b1a3ff06ce0fbee1cf178521ccb6ac97843c5c456dfd5eb8`, at base
`ebedc0895eb4c06725af020bc1af165722b0a3ce`. It derives `wanted` from lines that
start at column zero with `#print axioms`, then checks only that list. It has no
separate required inventory. Its report dictionary also overwrites duplicates.

[verify.py](verify.py) runs the original and patched `main()` in temporary copies
of their pinned source inputs. **The build and probe subprocess results are
substituted test transcripts.** These are controlled driver tests, not historical
HPE logs or fresh HPE builds. [RESULT.json](RESULT.json) records all 100 cases.

| Case | Original driver | Proposed repair |
|---|---|---|
| Complete 42-probe inventory | Accepts, reports 42 | Accepts, reports 42 |
| Import-only query file | Accepts, reports 0 | Rejects before building |
| Each single query omitted, with its report omitted | Accepts, reports 41, in all 42 cases | Rejects all 42 before building |
| All queries indented, healthy reports supplied | Accepts, reports 0 | Accepts, reports 42 |
| Indented queries, one forbidden dependency supplied | Accepts, reports 0 | Rejects |
| Duplicate or unexpected report | Accepts | Rejects |
| One report missing while its query remains | Rejects in all 42 cases | Preserves all 42 rejections |

The repair checks the exact required query inventory before either expensive
subprocess. It then requires one report per required name and retains the
`propext`, `Classical.choice`, `Quot.sound` allowlist. Complete axiom-free,
reordered, indented and multiline-report controls pass. The tests reject four
weakened repairs: removing the query inventory guard, permitting duplicate
report overwrites, ignoring extra reports, or disabling the axiom allowlist.

A separate **real Lean 4.21.0** run produced [fixtures/lean421.txt](fixtures/lean421.txt)
from three tiny [syntax fixtures](fixtures/ProbeSyntax.lean). It confirms the
message syntax, valid indentation, a permitted `propext` dependency and a
forbidden dependency. The fixture deliberately declares an extra axiom solely
as a negative control; it is not imported by any HPE theorem. Compiler/version,
source and output hashes are in [fixtures/LEAN.json](fixtures/LEAN.json).

The six adversarial test groups also check source and receipt corruption,
transcript corruption, overwrite refusal, and a read-only relocated replay
under optimized Python. The registered replay passed on CPython 3.12.13;
standalone replay was also checked on CPython 3.14.6 with `-I -B -O`.

## Reproduce

From the repository root, with Git and Python 3.12; no Python dependencies:

```sh
python3.12 -I -B scripts/research_package.py --package research/hpe-axiom-inventory-audit
```

Expected final line:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/hpe-axiom-inventory-audit outcome=completed
```

To independently regenerate the small compiler transcript, using an actual
Lean 4.21.0 binary, rather than an elan shim:

```sh
python3.12 -I -B research/hpe-axiom-inventory-audit/check_lean.py --lean /path/to/lean-4.21.0/bin/lean
```

Default verification is read-only. The optional `--write-receipt` and `--record`
modes refuse to overwrite evidence. [SOURCES.json](SOURCES.json) binds all 21
consumed external files; the package runner additionally verifies Git provenance.

## Limits

The unmodified pinned probe file already contains all 42 expected names. These
experiments do not refute its previously recorded axiom results. A separate
immutable-source check would also detect a changed probe file; this result
concerns the standalone driver's coverage contract.

No HPE/Mathlib build, Lean kernel replay of the HPE theorems, selected-construction
cold replay, supplier admission, or new kappa is claimed. The repaired driver
still trusts the invoked compiler and its output. Its source scanner and probe
parser are not a general Lean parser or a defense against fabricated output.
The full repaired HPE build remains an adoption check.

## Open next questions

Can the proposed repair be adopted while preserving the full pinned HPE build
and the 42 actual reports? This matters because the controlled tests establish
driver behavior, not full-build compatibility. The first step is to apply
`repair.patch` in an isolated successor and run the original combined HPE
verification with Lean/Mathlib 4.21.0. That requires the complete dependency
setup and an explicit decision about successor source pins; frozen receipts
must not be rewritten. The structured question is in [TASK.json](TASK.json).

## Credit and scope

Jeremy Kothe (`jeremykothe2`, PR593) supplied the audited HPE driver and formal
package; DreamingOfClouds supplied PR599 and the Lemma A/G lineage. Their
[source notice](../hyperplane-end-lean/NOTICE.md) retains the construction,
realization and Clifford credits. No predecessor implementation is vendored;
the proposed patch retains its notice.

`commdata2338`'s [PR1415](https://github.com/CrocSwap/integer-mult-bounds/pull/1415)
already audits the three HPE pairs' operator semantics. WeberChen8128's
[PR893](https://github.com/CrocSwap/integer-mult-bounds/pull/893) already uses
exact command/report coverage for the separate PR236 historical corpus. The
general coverage principle is prior work; this contribution adds the specific
HPE failure reproductions, repair and executable controls. No code is imported
from either audit.

The assigned `formal-interface-lemma` scope changed to this verification-coverage
prerequisite after overlap review. It is a tooling side result, not a new formal
lemma. [Discussion1593](https://github.com/CrocSwap/integer-mult-bounds/discussions/1593)
and [TASK.json](TASK.json) record the scope and overlap limits.

Prepared for Hanson Sun (`bbMisk`) with substantial OpenAI Codex assistance in
investigation, implementation, verification and writing. No subagents or
independent human review. New material is Apache-2.0. Emulate was unavailable;
prose was checked against sources and executed evidence under the donor's
instruction to disclose that limitation.
