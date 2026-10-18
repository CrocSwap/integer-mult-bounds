# Validation and handoff scope

Base commit: `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`.
Local environment: Linux, CPython 3.14.7. New material is confined to
`research/hadamard-readout-census/`. No generator, selected frontier,
existing research package or `upstream/` source is edited.

Relevant commands:

```sh
python3 -I -O -B research/hadamard-readout-census/test_package.py
python3 -B scripts/verify_selected_result.py
python3 -B -m unittest discover -s tests -p 'test_selected*.py'
git diff --cached --check
```

The package command passes with byte-exact deterministic regeneration,
read-only relocated replay under optimized Python, and four real subprocess
controls. The independent verifier passes on all 40,320 signed source orders,
114 profile frequencies, 22 Pareto profiles and all their attaining words.
It checks 16 individual signed child contracts, 624 dense basis/dirty cases,
literal inverses, 1,296 exact rational price fixtures, the three profile
families, full restoration/control invoices and ten mathematical controls.
No mathematical condition depends on Python assertions.

The selected-record source inventory, exact κ and proof binding pass.
All 25 selected-result/inventory/proof tests pass. All seven retained source
files match their exact Git bytes at the recorded predecessor/base commits;
all additional context hashes match the recorded base Git bytes. The final
submitted package is additionally replayed from files exported from the Git
index, with exact command output stored in VALIDATION.json.

The full source-order census completes its stated domain. Arbitrary repeated
readouts are covered by the written four-difference/eight-readout upper bound.
No failure to find a candidate is presented as an impossibility theorem.
The independent calculation enumerates signed-event permutations and shortest
sums of state differences; it imports neither census.py nor predecessor code.

The two recursive implementations are compared on exactly PR997's same factor
lengths and dirty interface through the same new primitive backend. The
emitted primitive-word digests and a common exact integer prefix bound, with
sufficient signed width for the stated finite norm domain, are in the command
receipt. The bound includes scalar intermediates and the appended inverses.

Full repository `make verify`, selected supplier cold replay, hosting/tape
execution, remote CI and human peer review are not claimed. This standalone
research package does not modify a selected construction or regenerate
unrelated artifacts. Relevant package checks and selected-record checks are
the completed validation scope; the result is an exact interface operation
count and scoped finite optimum, not a measured multiplication speedup or
formal proof of the complete theorem.

The handoff metadata refresh at 19:12 UTC on October 13 found 767 open PRs
through #1152; main and the PR997 source pin were unchanged. PR1088's weighted
3x3 repair, PR1103's rectangular output borrowing and PR997's sampled 4x4
construction have different scopes. This package extends PR997 with complete
coverage and a new price envelope. No pinned coordination issue existed;
CLAIM.json contains the local claim. Handoff and later publication details
are recorded there once after publication.

Contributor, predecessor and substantial AI-assistance credit are retained
in NOTICE.md and the frozen source notices. New material is Apache-2.0.
