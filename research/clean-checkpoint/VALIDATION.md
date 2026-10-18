# Validation record

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Platform: macOS arm64. Focused package requires Python 3.9+ and only the
standard library. Local interpreters are CPython 3.9.6 and 3.12.14.

## Contribution checks

The following commands pass and compare the complete deterministic receipt:

```sh
python3 -B research/clean-checkpoint/verify.py
python3 -I -O -B research/clean-checkpoint/verify.py
python3 -I -O -B research/clean-checkpoint/test_package.py
```

The exact package replay passes on both listed interpreters. Coverage:
32,640 root splits; 498 noncommutative symbolic cases; 216 rounded executions
with independent dense rational comparisons and nonzero rounding error in every
case; 14 algebraic/interface rejection controls and two rounded controls.

`test_package.py` copies the package into a path with spaces, without repository
or Git dependencies, and verifies it under isolated optimized Python. It then
requires failures for four corruptions: a changed pinned source, a changed
expected call count, removal of the clean-checkpoint guard, and removal of the
phase-array alias guard. These check actual subprocess exit status and diagnostic
markers. The temporary copies are restored or deleted; source files stay intact.

The first implementation review caught and fixed two checker defects before
packaging: Python assertions in the rounded harness would disappear under `-O`,
and a same-order sign-negation control at seven factors happened to invert the
ideal odd-degree product. Explicit checks now remain active under optimization;
the inverse-order control uses two factors where the mutation is nontrivial.
These were checker-development findings, not counterexamples to the clean-root
identity. A separate Codex reviewer subsequently passed the optimized package.

Concurrent PR673 arrived during the final overlap check. Its phase-alias defect
motivated a guard before any mutable operation. Five phase aliases are rejected,
and removing the guard makes the package control fail. Its original patch and
head are pinned; no broader PR673 replay or review is claimed.

## Repository checks and limits

`make selected-record-check` passes at the base, checking the selected κ,
original source inventory and proof supplements. Only the new research package
is changed; selected sources and `upstream/` are preserved. Staged whitespace,
vendored Git-blob/SHA-256 bindings and clean-patch applicability are checked in
the final handoff.

The repository-wide `make verify` was launched in a separate detached checkout
at the exact base, to avoid regenerating unrelated artifacts in the contribution.
The initial system-Python 3.9 attempt passed the two opening arithmetic audits
but failed in the historical copied-centers producer at `int.bit_count`; the root
suite requires Python 3.11+. It was retried with the available Python 3.12.14.
The supported-interpreter run passed `verify-community`, `verify-producers`,
`verify-partial-gauge`, `verify-three-stage-cover`, `verify-paired-cube`,
`verify-recycled-bit` and `verify-entrance-banks`, including their exact words,
assembly checks and controls. It then stopped in `gen4-bank-verify` at
`research/five-stage-gen4-banks/verify.py:52` with
`ModuleNotFoundError: No module named 'sympy'` (make exit 2). No root-wide pass
is claimed. Later root targets, including `frontier626-verify`, were not reached.
No third-party dependency was installed merely to broaden this additive
standard-library package's scope.

The complete expected receipt has SHA-256
`9c7b5aa11a2592547f2432f0d2a6c434b8ab160126c71c07c23a586f54d8bdbd`.
All eight vendored/source-license files were independently compared to the
exact Git objects in SOURCE.json, in addition to the offline checker bindings.

The initial overlap review covered recent open PRs through #675. The
user-authorized publication continuation refreshed metadata through #709 and
repeated the targeted `clean checkpoint` search (no matches). PR689 by Dillon
Amburgey optimizes balanced ternary placement in PR673's all-dirty echo; our
result instead changes the root storage contract and retains balanced binary
dirty children. No PR689 code is consumed. PR673 remains explicitly credited
and distinguished in README.md. No pinned sprint coordination issue was
available at the initial claim. Main still resolves to the exact base.

The initial deliverable was a local patch and standalone package because the
connected account lacked upstream push permission and the checked in-app
browser was signed out. The user then authorized publication using Chrome,
where the FanPUYen session is signed in. Final publication status belongs to
the external handoff record, separate from the local verification evidence.

No selected-supplier cold replay, remote CI, Linux replay, Lean proof or complete
multiplication theorem is claimed for this additive interface package. The
uniform rounded-leaf estimates and preparation/tape/hosting obligations retain
the explicit limits stated in PROOF.md.
