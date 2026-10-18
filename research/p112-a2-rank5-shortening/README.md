# Three rank-five P112 endpoints after a common support of 44

For the fixed P112 root-evaluation code over any characteristic-zero field,
delete one common set of at most 44 coordinates. Three pieces of residual
binary support rank at most five then have code-intersection dimension at
most one. The pieces may be dependent and their coefficients are arbitrary.
[PROOF.md](PROOF.md) states the exact restriction/intersection convention.

The projective-fiber argument extends the elementary sufficient common-support
threshold 41 to 44. All 1,120 A2 planes have P112 evaluation union size at least
78. In a full E8 projective A2 fiber, a binary-rank-five subset has at most ten
lines. Singleton incidence counting therefore requires
`2*(78-|S|) <= 3*12+3*10 = 66`, which fails through `|S|=44`.

The ten-line fiber capacity is sharp and has literal witnesses. The global
threshold 44 is a sufficient bound. At 45 the counting inequalities agree;
this is not a counterexample or a sharpness claim.

This is a scoped code-intersection lemma. It supplies no TWOSIDE profile
exclusion, full C5, complete decoder floor, supplier admission or new kappa.
The selected result and frozen sources are unchanged. The family decision is
to stop at this lemma and require an actual caller before further expansion.

## Reproduce

Python 3.12 or later, standard library only. From the repository root, direct
read-only checks are:

```sh
python3 -I -W error -B research/p112-a2-rank5-shortening/verify.py
python3 -I -O -W error -B research/p112-a2-rank5-shortening/test_verify.py
```

For the registered replay, keep temporary files in your own external directory:

```sh
RUN_DIR="$HOME/.cache/integer-mult-bounds-runs/p112-a2-replay"
mkdir -p "$RUN_DIR"
TMPDIR="$RUN_DIR" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-a2-rank5-shortening
```

To regenerate a receipt, pass `--output` and a new external filename to
`verify.py`. Existing paths are rejected. Default execution compares every
field with [RESULT.json](RESULT.json) and writes no receipt.

The primary replay checks all 3,309,747 P112 five-flats, the full A2 reflection
orbit, the E6 parabolic gap and all 2,667 codimension-two spaces in each of three
27-line fibers. The controls separately enumerate all 80,730 five-label subsets
per fiber to check the maximum, and test literal rank-five witnesses, every
eleventh-line extension, source drift, invalid inputs and losing count bounds.
The separate arithmetic shares the authenticated geometry constructor. It is
not a fully independent implementation of the geometry or proof.

[CHECKS.json](CHECKS.json) records commands, environments and results.
[REVIEW.json](REVIEW.json) records an internal automated peer check of the
precise proof and finite slice facts, with the five-flat census explicitly
outside that peer check. The standard Weyl-chamber theorem remains a written
dependency. No human review or proof-kernel verification is claimed.

## Sources and credit

Scientific and submission base is canonical main
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
[SOURCES.json](SOURCES.json) pins the sole live input, Nick Petalas's retained
root-simplex `geometry.py`, by Git blob and SHA256. That source provides the
root/label model, finite chamber machinery and five-flat enumeration.
DreamingOfClouds's PR3154 at
`708f0ad8928c383de8294aea3c126e9461d2066d` supplies the current shortening
handoff, but no pending executable dependency is imported here. The E8/P112
lineage, including joaqcoo's model, retains its attribution.

A [concurrent A2 investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19003040)
uses rank-six fiber capacity 16 and a named TWOSIDE profile. This package
uses rank-five capacity 10 and proves a generic common-support44 lemma.
The shared A2 singleton mechanism has no exclusive priority claim.

The new contribution is the rank-five projective-fiber capacity check and
its three-piece singleton bound. Development used substantial automated
assistance. All code and prose are Apache-2.0. [ENGINEERING.md](ENGINEERING.md)
records implementation bounds and deviations. [TASK.json](TASK.json) records
the changed card scope, overlap coverage and structured next questions.

## Open next questions

Can the sufficient threshold 44 be improved or attained at 45? First classify
the counting equality at 45. It requires 33 residual code sites, 30 singleton
sites and 36 piece incidences. Simultaneous rank-five spans remain unproved.

Does a named remaining decoder profile force three rank-five residual pieces
with a common support of at most 44 and intersection dimension at least two?
First reconcile public exclusions and bind that actual caller's quotient and
supports. This package establishes no profile application.
