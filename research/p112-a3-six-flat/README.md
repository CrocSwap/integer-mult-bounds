# One ten-piece P112 profile excluded by binary endpoint closure

The actual TWOSIDE `(b,t)=(6,4)` profile `2^2,6^5,7^3` is impossible
over every characteristic-zero field. Deleting three pieces leaves three
code dimensions and an A3 configuration. Keeping one six-dimensional label
space improves the support-only bound 76 to equality 80. In every equality
case, the original rank-six endpoint constraint forces total support at
most 64, which is a contradiction.

[PROOF.md](PROOF.md) gives the theorem and its exact caller. The new finite
step checks every binary six-space and orthogonal root frame. Exactly 60
flat/frame pairs reach the critical union cost 48. Each endpoint then has
sixteen mandatory singleton labels of binary rank six, with only those
sixteen live labels in its closure. This excludes the profile without
searching endpoint coefficients or all four extra common coordinates.

## Reproduce

Python 3.12 and its standard library suffice. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-a3-six-flat-replay"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-a3-six-flat
```

The registered commands run `verify.py`, `independent.py`, sixteen
behavioral groups under optimization and `cold_source_check.py`, sequentially.
The first three commands need only this package and work in a Git-free export.
The cold-source regression and registered launcher also need Git history for
reachable source-history provenance. The regression makes non-ancestor source
commits unavailable while using the real metadata validator for every allowed
source. Each verifier's optional `--output NEW_EXTERNAL_PATH` creates a new receipt and refuses to overwrite
existing files. Default replay compares the committed receipts.

The primary checker enumerates 788,035 annihilator kernels. The separate
checker independently reconstructs the lattice and labels and enumerates
777,240 affine five-flats plus 10,795 even-only six-spaces. Both check all
2,025 orthogonal frames, every maximizing flat, all 60 equality pairs and
all 240 singleton closures. The tests compare complete maximizing sets and
equality witnesses, and reject changed source, labels, singleton cost and
coverage receipts. Source pins, environments, commands and limitations
are in SOURCES.json, VERIFY.json, CHECKS.json and ENGINEERING.md.

## Cold-checkout source provenance

The original metadata required two blobs at pending PR3154 head
`708f0ad8928c383de8294aea3c126e9461d2066d`. Canonical CI did not fetch that
foreign commit, so registered replay failed in provenance validation before
running any mathematical checker. A populated local object store hid the gap.

Both exact predecessor files are now archived in this package: `original-bk1b.py`
and the existing `caller-data.json`. Their original paths, head, SHA256 and Git
blob IDs remain in `SOURCES.json.archived_sources`. Replay authenticates both
hashes for both copies, and rejects changed bytes, blob IDs and origin pins.
The filter is retained as source evidence, not executed or rewritten.

The generic launcher retains all five Git-source provenance checks. The two
foreign-head rows now resolve identical blobs in this PR's own reachable history:
filter archive commit `443ea34f1fcb09bba084b416ced1731621e444fc` and original PR
head `2a79c8314ae10b677bc7c1dd593d0c3d06b7cd15` for the existing caller data.
The original foreign pins remain recorded separately; capture equality was
checked against PR3154. No source hash, scientific receipt, mathematical assertion
or workflow check is removed. No peer repair head or accidentally cached Git
object is required. The scoped repair evidence is in `CI-REPAIR.json`.

## Open next questions

Can another still-open historical profile use this literal six-flat plus
four-coordinate cover? First pin its current source and earlier exclusions,
then prove its retained code dimension, common cover and endpoint ranks.
TASK.json records this question and its missing caller. No further census
or construction expansion is justified merely by this local result.

## Credit and limits

Nick Petalas contributes the weighted A3 six-flat/frame equality lemma and
this ten-piece application. DreamingOfClouds/PR3154 supplies TWOSIDE and
the original filters. PR3211 supplies piece deletion and simplex
normalization; PR3217 supplies the preceding arbitrary-support versus
binary-rank distinction. The retained E8/P112 lineage includes joaqcoo's
decoder model. Exact sources and heads are in SOURCES.json.

The nearby nine-piece `2,6^5,7^3` investigation was already claimed by
another session when this work started. Its separate support 22 contract
is credited as concurrent work. This package claims only the ten-piece
profile and the stated six-flat lemma.

This is author-checked finite evidence and a written proof, with internal
automated review. The standard Weyl-chamber theorem and original TWOSIDE
reduction remain explicit dependencies. Human review, formal verification
and hosted CI are separate. Full C5, `C(P112)>=64`, physical suppliers and
kappa remain open or unchanged. Frozen sources and the selected frontier
are untouched. New work is Apache-2.0. Development used substantial
automated assistance.
