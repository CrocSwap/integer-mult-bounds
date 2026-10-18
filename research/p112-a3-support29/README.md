# Sharp P112 A3 shortening with 29 common coordinates

The general rank-six A3 shortening allowance increases from PR3221's 22
common coordinates to the sharp uniform value **29**. With four
binary-rank-six endpoints and collectively independent pieces, their span
meets the P112 root-evaluation code in dimension at most two. An actual
independent-piece witness at **30** has intersection dimension three.
[PROOF.md](PROOF.md) states the characteristic-zero theorem and its limits.

The new argument charges missing singleton coordinates, including nonmodal
shifts. Every eleven-element subset of a mandatory sixteen-label set
already spans six dimensions. This pins most endpoints to support sixteen
and contradicts the complete defect budget for all orthogonal punctures.
No special common six-flat cover is needed.

## Reproduce

Python 3.12 and its standard library suffice. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-a3-support29-replay"
mkdir -p "$RUN/tmp"
TMPDIR="$RUN/tmp" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-a3-support29
```

The registered replay first checks source-history closure, then runs the
primary checker, separate checker and fourteen behavioral groups sequentially. It checks all 788,035 six-flats,
2,025 punctures, 17,472 eleven-label subsets and the literal boundary
witness. Primary witness ranks are exact rational ranks; separate literal
code identities and two modular rank checks corroborate them. Ten-label
rank-five controls and mutations of witness/source are rejected.
RESULT.json and INDEPENDENT.json preserve the exact receipts.

For a Git-free export, retain this entire package, including `vendor/`, and
the pinned `research/p112-ten-piece-simplex/geometry.py`. Run
`source_closure.py --export-only`, then `verify.py`, `independent.py` and
`test_verify.py` directly. The registered launcher also needs this PR's Git
history for provenance. `verify.py --output NEW_EXTERNAL_PATH` creates a
new receipt and refuses to overwrite existing files.

### CI source closure repair

The original hosted replay stopped before mathematics because four provenance
files were pinned at unrelated, unmerged PR heads. Those Git objects could
exist in a contributor's shared local repository but be absent in CI, even
with full-history checkout. Planning passed because it did not resolve the
source blobs.

`vendor/` now retains the exact four original files, with identical Git blob
IDs and SHA256 hashes. SOURCES.json binds them to archive commit
`f02c7f4e575b0ef9351899e8c88b8c626d60e9d5`, an ancestor of this repair, and
retains every original pin and contributor head. No peer repair head or
foreign object is needed. The original mathematical code, proof and receipts
are unchanged.

`source_closure.py` rejects any pin outside this PR's ancestry even when its
objects happen to exist locally. It also verifies the exact archived/input
bytes and exercises unavailable-head and changed-archive failure controls.
The export-only mode checks archive/input bytes without Git; it does not
claim to validate Git provenance. This guards the cold-source failure rather
than weakening the existing metadata checks.

## Open next questions

Bind one actual still-open TWOSIDE profile to the stronger theorem. First
reconcile the exact historical survivor list with public exclusions, then
prove its retained code dimension, common support and endpoint ranks.
TASK.json records the question and missing caller. No new historical
profile, full C5 or decoder-floor conclusion follows merely from this
improvement. The support30 witness leaves stronger structured common-cover
contracts open.

## Credit and limits

Nick Petalas contributes the robust defect theorem and boundary witness.
PR3221 supplies support22 shortening; PR3227 supplies the neighboring
six-flat contract; DreamingOfClouds/PR3154 supplies the original reduction.
The retained E8/P112 lineage includes joaqcoo's decoder model. Exact heads,
blob hashes and input hashes are in SOURCES.json.

The standard Weyl-chamber theorem and original decoder reduction remain
written dependencies. This is author-checked finite evidence and a written
proof, with internal automated review. Human/proof-kernel review and hosted
CI are separate. No supplier or new kappa is claimed. Frozen inputs and
the selected frontier are unchanged. New work is Apache-2.0. Development
used substantial automated assistance.
