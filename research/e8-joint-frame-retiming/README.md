# Joint B-phase frame retiming on the R740 shared-donor word

Conditional kappa = 0.001137722673868541. This composes #440's kernel and 57 A-phase moves with 28 jointly moved groups affecting 70 B-phase gates. All primitive ADD operands and their order remain unchanged. The kernel has 112 pivots, entrance rank 136 and 100 donor slots. There are 723 complete banks per stage, 14,187 live and 14,196 physical families.

Run `python -B research/e8-joint-frame-retiming/verify.py /absolute/new/output --replay-phases`. Python standard library only. The complete verifier rebuilds the pinned R740 producer and kernel, reconstructs all 127 frame changes, replays every upstream complex phase, emits and independently audits both global orientations and residual routes, and recomputes the finite invoice and exact outer assembly.

The changed scalar/source-span, global banks, residual route mutation tests, two moment engines and finite assembly passed before publication. Full uninterrupted Python 3.11/3.14 runs are pending. Inherited #440 validation files are historical under local-evidence/upstream440. No unconditional multiplication theorem or new Lean proof is claimed; all inherited all-size interfaces remain assumptions.
