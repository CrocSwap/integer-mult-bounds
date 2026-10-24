# Executed validation

Environment: Linux, CPython 3.12.15; standard library only. No solver, Lean,
Docker, network fetch in the mathematical replay, or subagent was used.

The registered package replay and a separate `-I -O -B` direct replay passed.
They verify the source-bound two-stage identities and the finite corroborating
checks listed in RESULT.json. The written all-width argument is in PROOF.md.
No full source supplier, p19 controller, outer transfer or independent human
review was run. The selected frontier is unchanged.

Publication preflight and Git-free export results are recorded separately
below after execution; neither can establish the mathematical theorem.

At code commit `d86a79c0e89df105bf5564b482708c028ed8fc12`:

- `check_research_commit.py --check-source-history` passed for 13 committed
  package/input files and base `4c0a359d88f22f05189d51f48387750b801a45d4`.
  The initial history check correctly rejected this shallow checkout. After
  fetching the missing canonical history, the full check passed.
- The official exporter and Git-free export integrity check passed (13 files).
- From the unpacked export outside any Git checkout, `python3.12 -I -B`
  replay passed in 21.382 seconds, and `-I -O -B` passed in 19.987 seconds.
  Both produced `PASS_TWO_STAGE_TERMINAL_SUPPORT_NO_KAPPA` with empty stderr.

The final publication update changes this validation note only; mathematical
code, input pins and the exact receipt remain those replayed above. Hosted CI
is a separate status and was not claimed by these author checks.
