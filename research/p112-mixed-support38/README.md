# P112 mixed-rank shortening at common support 38

Three residual P112 pieces of binary support ranks at most 5,5,6, after ONE
common deletion set of size at most 38, meet the restricted root-evaluation
code in dimension at most one over every characteristic-zero field. This
improves PR3260's sufficient threshold 37. It does not prove sharpness or a
new historical profile exclusion. [PROOF.md](PROOF.md) gives the complete
argument and inherited dependencies.

The new step closes the D6 boundary. A putative equality requires a rank-six
piece supported on 20 singleton coordinates in one projective fiber. All 896
relevant live axis fibers have rank-six capacity 18. An independent ambient
annihilator/puncture check also excludes support 20. The E6 branch uses
PR3262's rechecked joint incidence argument, with allowance76 versus80.
Exact coverage and full-census digest are in [RESULT.json](RESULT.json).

## Reproduce

Python 3.12 or later, standard library only, from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/p112-mixed-support38
```

The three registered commands run sequentially with 120-second limits. Direct
Git-free export replay uses these commands, from the exported root:

```sh
python3 -W error -B research/p112-mixed-support38/verify.py
python3 -W error -B research/p112-mixed-support38/independent_check.py
python3 -W error -O -B research/p112-mixed-support38/test_verify.py
```

The export needs the package and its three declared baseline inputs at their
original relative paths. Pending PR proof/receipt bytes are retained locally
with exact commit, Git blob and SHA256 pins in [SOURCES.json](SOURCES.json).
No pending Git objects or Git subprocesses are needed for direct replay.
Authentication bounds inventory length, paths and source sizes before import.
`verify.py --output NEW_EXTERNAL_PATH` creates an external receipt and refuses
to overwrite an existing file. Set TMPDIR to an external session directory to
keep control-fixture files outside the checkout.

## Open next questions

Does support 39 admit a counterexample or a larger sufficient theorem? The D6
incidence equality used here no longer follows at 39. First bind the actual
puncture and mixed support-overlap patterns before another census. This is
unrun and not evidence that 38 is sharp. A new TWOSIDE application also needs
a named caller, current public-exclusion reconciliation and its exact retained
code dimension. [TASK.json](TASK.json) records these questions and blockers.

## Sources and verification limits

Credit Nick Petalas/PR3260/3262, DreamingOfClouds/PR3154 and the retained
root-simplex/E8/P112 lineage including joaqcoo. Worker1's concurrent uniform
rank-five support 46 theorem shares the D6 prerequisite but proves a different
predicate. This package uses no unpublished sibling theorem. All copied
predecessor bytes stay unchanged. New work and retained sources are Apache-2.0.

The global five-/six-flat capacities 12/20 and standard Weyl-chamber theorem
are inherited; their historical global censuses are not rerun. The independent
checker shares authenticated root/label reconstruction and does not independently
establish A2 capacities or characteristic-zero classification. Internal review
is not independent human or proof-kernel review. [CHECKS.json](CHECKS.json)
records executed commands, export evidence and review limits.

No full C5, decoder floor, native or physical supplier, restoration, complete
consumer, all-size multiplication theorem, new kappa or selected-frontier
update is claimed. Lean, Docker and the selected full cold replay are unrun.
