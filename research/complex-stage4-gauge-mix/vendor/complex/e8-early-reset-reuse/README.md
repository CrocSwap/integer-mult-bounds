# Earlier clean resets on PR433

Conditional kappa = 0.001128250848293019, approximately 0.659% above PR433. Eleven helpers removed, R758 to R747. The exact bit saving is 0.001129525236098815991751; the unchanged complex saving is 0.001183986549206329.

Run `python -B research/e8-early-reset-reuse/verify.py /absolute/new/output` with Python 3.11 or 3.14. Standard library only. The wrapper freshly verifies the pinned parent with all phases before reconstructing and checking the changed bit program.

At draft submission the changed emitted bit, independent bank audit, two rational moments and exact finite assembly passed locally against the previously fully replayed parent. The new uninterrupted wrapper and GitHub CI are pending. Local receipts distinguish that scope.

The initial full Python3.14 wrapper passed. Python3.11 exposed the parent compressed-file metadata mismatch; the package now imports PR433's upstream decoded-witness hash fix at 6d9244518175caf9e0089f92486959bc2c317273. Fresh both-version replays are pending. The original failure and pass receipts are preserved.

Both fresh portable full replays now passed locally on Python 3.11 and 3.14 against e48f24fd2393500c804a0cbab542e20de8ddee6e. See VALIDATION.json and local-evidence/FULL-PORTABLE-PYTHON*.json.
