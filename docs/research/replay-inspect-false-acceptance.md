# Registered replay and inherited interactive inspection

The registered replay launcher removes `PYTHONINSPECT` from its copied child
environment. An ambient interactive setting must not turn a verifier exception
into a successful interactive-shell exit. This is a tooling result, not a
mathematical certificate, supplier admission or selected-frontier change.

## Actual failure and scoped repair

At canonical base `20a1e31bc6009b9b3f4d084bbaadc6350e34fcba`, a generated,
source-pinned package whose verifier raises `ValueError` is rejected normally.
With inherited `PYTHONINSPECT=1` and terminal stdin, the same verifier enters
Python's interactive prompt after the exception. Ordinary terminal EOF
(Ctrl-D), without executing a replacement success command, exits successfully.
The shared runner then prints `PASS_REGISTERED_RESEARCH_PACKAGE`. Thus a real
verifier failure becomes a false registered acceptance.

The regression drives the actual `run_package` validation and launch path,
using a disposable Git repository, the existing package generator and a
pseudo-terminal. Its outer test driver starts with `-I` so only the child's
ambient inspection is under test. Before the fix, six test methods report ten
failures including subtests; the actual registered test observes a PASS after
the failing verifier. After the fix the child raises and exits nonzero, no
interactive prompt appears, and the registered runner does not print PASS.

The production change is one environment removal in `run_command`, alongside
its existing handling of ambient optimization and import-path settings. It
copies the environment first, so the running parent's environment is unchanged.
It does not redirect or close stdin, replace interpreter options, wrap the
verifier, or parse traceback text.

## Complete launch-path boundary

- `run_package` calls `run_python_replay`, which creates the private bytecode
  namespace and calls `run_command`. File, `-m` and `-c` entry points share this
  boundary, including explicit `-O` execution.
- POSIX launches the command with that copied environment. Windows passes the
  same copied environment to its existing Job Object ownership gate and then
  the requested command. The gate's own `-I -S` isolation remains unchanged.
- Optional dependency installation also calls `run_command`, so its Python/pip
  process receives the same ambient-inspection policy. Its argv, environment
  apart from the existing removals plus `PYTHONINSPECT`, and stdin are preserved.
- Ordinary descendant processes inherit the sanitized environment. A verifier
  can deliberately restore `PYTHONINSPECT` or choose interactive options; this
  repair does not constrain trusted verifier code or implement a sandbox.
- `run_isolated_tests.py` separately uses private unittest completion receipts
  and the lower-level Windows ownership helper. That helper preserves its
  explicitly supplied environment; no new global policy is imposed on it.
  There is no `scripts/run_isolated_verifier.py` in this tree.

Explicit manifest `-i` remains explicit and can still enter a REPL, including
its normal exit semantics. The already-running outer Python launcher may itself
have been started in inspection mode; this child-launch repair cannot change
that interpreter's startup flags. Use an appropriately isolated outer launcher
when its own exit semantics are part of an acceptance boundary. User-site
startup, intentionally interactive/hostile verifiers and arbitrary environment
isolation are outside this change.

## Validation and reproducibility

Run the small controls with Python 3.12:

```sh
python3.12 -B -m unittest discover -s tests -p test_research_replay_inspect.py
python3.12 -O -B -m unittest discover -s tests -p test_research_replay_inspect.py
```

The six methods cover actual registered rejection, file/module/command failures
under normal and optimized flags, a clean-environment control, shared direct
launch, preserved stdin input, successful completion, descendant inheritance,
unchanged parent state, intentional `-i`, and copied Windows-dispatch arguments.
The pseudo-terminal controls are POSIX-only. The portable Windows dispatch
control examines the environment passed to the gate; it is not native Windows
execution. Native Windows remains unrun.

On macOS 27.0 arm64 with CPython 3.12.7 and Git 2.44.0, all six new
methods pass in both modes. The existing onboarding PackageTests, bytecode
isolation, POSIX signal cleanup and Windows Job Object test module contribute
40 compatibility methods in each mode: 32 pass and eight native Windows cases
skip (20.194 seconds normal, 22.060 seconds optimized). The final handoff records commands, counts,
source hashes, committed-byte export and cold results. Shared-tooling changes
have no package VERIFY.json, so the scoped cold closure is the committed runner,
package generator, new test and this document. Its source directory can be
read-only and Git-free; disposable registered fixtures still require Git.

Frozen package pins remain unchanged. A shared-runner edit may be rejected by
historical packages that pin an earlier runner as a live input; passing targeted
unit tests does not imply those historical scientific replays pass. No full
archive or scientific replay is part of this repair.

## Open next questions

Run an equivalent native Windows terminal control when that platform is
available. Audit any broader interpreter-startup trust policy separately with
its declared dependency requirements; do not replace this narrow repair with
unmeasured blanket environment isolation.

## Credit

Prepared by JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Retains Douglas Colkitt's shared package runner and generator, and the existing
contributors' environment, private-cache and process-ownership work. This change
adds the real interactive false-acceptance control and scoped ambient policy.
