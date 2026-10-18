# Concrete target-write row certificates

Lean 4.30.0 accepts a concrete row-generating certificate for arbitrary finite
register sets and chronological legal XOR words. If the full raw word restores
every register and has `m > 0` target-destination gates, the package constructs
exact Boolean coefficients expressing every row of `I XOR projected` using the
last `m - 1` actual donor occurrences. The proof permits dirty inputs and target
feedback. It formalizes the execution and coefficient certificate, not a numeric
rank API or the three-cycle minimum theorem.

This is a formalization follow-up to [Discussion 1548](https://github.com/CrocSwap/integer-mult-bounds/discussions/1548)
and the written target-write lemma in [PR 1546](https://github.com/CrocSwap/integer-mult-bounds/pull/1546),
section 2 of `research/projected-three-cycle-minimum/proof.md` at
`0980a7c266532b42ccda3d77bf61b5cf18be9054`. It claims no novelty for that prose lemma.

## Exact statement and coverage

`Row n := Fin n -> Bool` and `Matrix n := Fin n -> Row n`. A `Gate` contains
destination, source, and their inequality. Both executions start at the full
identity, including the target input column. Lists execute head first.
`projected` omits precisely target-destination gates, while `donors` records the
full raw source row immediately before each omitted gate. Equal donor values
remain separate occurrences.

The main declaration is `TargetWriteCertificate.restored_row_certificate`.
For any `y : Fin n` and `w : List (Gate n)`, its hypotheses are
`raw w = identity n` and `0 < targetCount y w`. Its deterministic outputs are
`G := retainedDonors y w = (donors y w).tail` and
`C r := reducedCoefficients y w r`. It proves:

```lean
(exists first, donors y w = first :: G) ∧
G.length = targetCount y w - 1 ∧
forall r, (C r).length = G.length ∧
  combination G (C r) = rowXor ((identity n) r) (projected y w r)
```

`combination` uses Boolean AND for selection and XOR for addition. Although the
definition truncates mismatched lists, every certificate row proves matching
lengths. `ScanState` holds data only; the separate invariant is proved from the
actual initial state and update operation. No execution history or generation
property is an assumed field.

| Interface | Checked content |
|---|---|
| `projected_eq_filter` | Skip semantics agree with chronological replay of retained gates. |
| `donors_target_snoc` | Appending a target gate records its raw pre-gate donor. |
| `row_generation`, `prefix_row_generation` | Computed masks generate every defect row for every actual prefix. |
| `restored_donor_sum_zero` | Raw restoration gives the actual donor XOR-sum relation. |
| `restored_row_certificate`, `restored_at_most_certificate` | Explicit donor-tail certificate and its existential bound. |
| `zero_target_projected_eq_raw` | Zero target writes make projected and raw executions equal, without a restoration premise. |

The Lean fixtures cover changing donors with target feedback, repeated donor
values, raw versus projected helper entries, chronological versus reversed
projection, wrong later/projected donor sampling, and zero target writes.
Immediately after a donor's own distinct-register gate it is unchanged, as
proved by `applyGate_donor_unchanged`; that timing is not a failure control.

## Reproduction and observed evidence

Use an **already installed** Lean 4.30.0 binary at commit
`d024af099ca4bf2c86f649261ebf59565dc8c622` and Python 3.12. The proof imports only
`Std`; there is no Mathlib dependency. From the repository root:

```sh
LEAN=/path/to/installed/lean python3.12 -I -B research/target-write-row-certificate/replay.py > /tmp/target-write-replay.json
```

`LEAN` may be omitted if the installed binary is on `PATH`. The wrapper checks
the exact release and full commit, verifies the two delivered source hashes,
compiles the proof in a temporary directory, and compiles a reporting-only copy
that requests all 78 theorem axiom reports (65 public, 13 private). It rejects
missing, duplicate, unknown, incorrectly bound private, or disallowed axiom
reports. Only `propext`, `Classical.choice`, and `Quot.sound` are permitted.
Inherited `LEAN_*` settings are excluded. The wrapper does not install packages
or invoke a package manager; compiler outputs are temporary, and the JSON receipt
goes to standard output. Use a direct installed binary rather than an installer
or toolchain-manager shim.

`REPLAY.json` records the successful local run on `arm64-apple-darwin24.6.0`,
Python 3.12.14. Both source and reporting copy compiled; all 78 reports were
present, with exactly the permitted axiom union and no `sorryAx` or custom axiom.
The only diagnostic was an unnecessary-`simpa` linter warning. No mathematical
repair was made locally. The external Python fixtures also passed, including
1,170 small donor-list/mask elimination cases; these are separate finite checks.

The producer delivered source only and did not run Lean. Subsequent local
kernel execution supplies the acceptance evidence. Packaging changed only the
leading Lean comment to report that distinction and normalize attribution;
all bytes after that comment match the original delivery. `SOURCES.json` pins
both versions and the original archive; `REPLAY.json` records the body hash.
The Python fixture source is unchanged.

The generic package hook runs **only** external Python fixtures and eight
report-parser controls. A green generic hook is not a Lean kernel result:

```sh
python3.12 scripts/research_package.py --package research/target-write-row-certificate
```

## Open next questions

The numeric statement `rank(I - P) <= m - 1` still needs a formal bridge from
this concrete coefficient certificate to a conventional finite-field rank API.
Choose and pin that algebra environment, then prove the bridge using the actual
gate and donor semantics here. The core/Std artifact has no field/dimension API.
See the structured question in `TASK.json`.

No three-cycle application, helper reduction, BFS, 13-gate minimum, physical
supplier, all-size compiler, geometry, or multiplication theorem is formalized
by this package. It does not change the selected frontier.

## Attribution and source pins

Andrey Mas, with substantial **GPT-6 Pro** formalization and fixture-checker
assistance through ChatGPT, as identified in the browser UI. Codex prepared
source briefs, coordinated, audited execution, replayed, and mechanically
packaged the artifact. A producer self-reported model variant was not
independently verified and is not used as attribution evidence.

The written lemma and research lineage are credited to PR 1546 / Discussion
1503. The precursor raw/projected model and write-count lineage are due to
**Gareth Davidson / @bitplane**, [PR 1420](https://github.com/CrocSwap/integer-mult-bounds/pull/1420),
head `d19a944897714f2ecae72720b7dafc3e256f2f8d`, mathematical commit
`dc6ba012c92470ea830e3b0ff2dab28fbd8126d8`, following **@woklerx**,
[PR 1105](https://github.com/CrocSwap/integer-mult-bounds/pull/1105).
No predecessor Lean implementation was copied. Apache-2.0; see `LICENSE`.

Package provenance is pinned to main
`ddb4371c16a5a5de9e363afa8c0d6d7c27429e3c`. `TASK.json` explains the change from
the original complex masked-decoder card to this scoped independent
formalization. Exact selected-record, catalogue, proof-source, and delivered
file pins are in `SOURCES.json`.

Publication branch starts at current main `adc34159e0d6dc3dd2af2bdba3f5ca7376ef957e`.
The revision-3 checkpoint preserves this completed independent-verification
result; that track is unchanged. The original revision-2 task and source pins
remain historical provenance, not a current masked-decoder assignment.
