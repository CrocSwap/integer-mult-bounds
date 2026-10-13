# Validation and handoff

Verified on 2026-10-13 at 15:17–15:18 UTC with Python **3.12.14**, macOS
26.5.2 arm64. All checks below exited zero. The standalone programs need
Python 3.11 or later and no additional packages. The system Python 3.9 was
not usable: the inherited generator uses `int.bit_count`.

## Reproduction and evidence

```sh
python3 -B research/frame-completion-seed47/check.py
```

Expected JSON status: `PASS_INDEPENDENT_SEED47_LOCAL_FRAME_COMPLETIONS`.
Expected summary: 2,271 active nodes, 2,269 pointwise feasible nodes,
692 completable degenerate source spans and two obstructed nodes.
The output also records all 595 orthogonal pairs through dimension four,
the PR #920 residual counterexample and 15 rejected negative controls.
[VERIFICATION.json](VERIFICATION.json) is the full retained result.

| Completed check | Result |
|---|---|
| Independent explicit-vector certificate replay | All node records and ranks pass |
| Signed DAG output reconstruction | All 120 × 120 coefficients pass |
| Exhaustive `h=0..4` subspace enumeration | 595 orthogonal pairs; optimum searched over every nondegenerate `U` |
| Certificate and premise negative controls | All 15 rejected for the expected reason |
| PR #920 scope control | Separator accepted; alternating incident residual identified |
| Same checker under `python3 -I -O -B`, outside repository cwd | Identical JSON result |
| Producer under `python3 -I -O -B`, outside repository cwd | Byte-identical certificate |
| `python3 -B research/frame-completion-seed47/test_discover.py` | Producer agrees with independently enumerated optima on all 595 pairs; nonorthogonal premise rejected |
| `python3 -B -m unittest discover -s tests -p test_parity_side.py -v` | Four existing tests pass |
| `python3 -B scripts/verify_selected_result.py` | Selected exact kappa, source inventory and proof supplement pass |

[VALIDATION.json](VALIDATION.json) records commands, exit codes and outputs;
absolute command paths are normalized for portability. Its selected-record
check is a manifest/inventory check, not a cold replay of the selected supplier.
The complete repository-wide `make verify` and selected cold replay were not
run for this additions-only geometry package. Existing generators and the
selected construction are unchanged; global regeneration of unrelated
artifacts was avoided during the coordinated sprint. No full-suite or CI pass
is claimed.

The initial implementation, finite experiment and proof were finished by
15:15 UTC, leaving more than the reserved final quarter of the 60-minute
budget for independent review, verification, overlap refresh and packaging.
A separate Codex agent reviewed the proof, implementation scope and final
certificate/checker hash bindings and found no actionable issue. It did not
independently rerun the complete repository suite. AI assistance is disclosed
in the README; agent agreement is not treated as mathematical evidence.

## Exact bindings

- Base: `007664306fff84fbb1c9a1b4053b69f439764034`.
- DAG canonical SHA-256: `13bd7da6b47bfee17213acb2eb1120fbe7324a3ece0691f8139d358149c70040`.
- Certificate file SHA-256: `fa3db5a815f4ba00a49fdb80952a945d811b0590eb10f152e582431a4a17a0dc`.
- Certificate canonical JSON SHA-256: `bc8e5852b0b939654e4f7374b2f0328b372d0f4da1a8065a673408946392b328`.
- Checker SHA-256: `f8096f4212db4b564311b9d6131ba9cdec6dbc6e100670e90c5dd8cb84575a77`.

Canonical digests use UTF-8 `json.dumps(value, sort_keys=True,
separators=(',', ':'))`. The DAG object contains the ordered input labels,
sorted active `[node, signed arguments or null]` pairs, and sorted
`[target label, signed output node]` pairs. Thus signs and node identity are
included. Runtime source pins cover all seven imported repository modules.

## Next review step and limits

Review the short bilinear-form proof, then run the single replay command.
The two common-span witnesses are concrete impossibility certificates for
their fixed sandwiches. The 692 completions are concrete positive witnesses
for local geometry only. The unchanged full DAG remains infeasible in this
model; no recursive cost, supplier or new exponent is admitted.

The useful next question, if a separately scoped follow-up is warranted, is
whether a modified DAG can satisfy simultaneous nesting and nonalternating
incident residuals with every change fully paid. This package performs no
such search and does not suggest that a better bound necessarily exists.
