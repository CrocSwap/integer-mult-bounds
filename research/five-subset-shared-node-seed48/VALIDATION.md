# Validation receipt

Base ce7ad1b6ab09452c3478723a2e96ed5ff212dc08; seed48; macOS arm64,
Python 3.9.6, standard library only. Completed on October 13, 2026.

```sh
python3 -I -B research/five-subset-shared-node-seed48/verify.py
python3 -I -B research/five-subset-shared-node-seed48/independent.py
python3 -I -O -B research/five-subset-shared-node-seed48/verify.py
python3 -I -O -B research/five-subset-shared-node-seed48/independent.py
make selected-record-check
git diff --cached --check
```

All passed. Primary output: threshold=9, 453600 labeled h9 rectangles,
59520 canonical frame candidates, four residual bases. Independent output:
h8=0, h9=453600, residual dimensions=3,3,4,4. The selected-record guard
retains conditional kappa=836330098538459/500000000000000000.

The primary has six semantic controls: an alternating incoming residual,
a corrupted residual vector, a cross-incompatible endpoint, a signed-rank-two
rectangle despite cross orthogonality and two degenerate pairs, a nonzero
common-span intersection, and a degenerate proposed source frame. It also
checks all 65536 vector pairs for the h8 complement map's linear isometry,
and all 3136 five-subset kernel pairs for its common negative sign.

Additional checks copied the package to a temporary directory and ran both
programs with isolated optimized Python successfully. Changing the recorded
h9 total by one then caused both programs to exit nonzero. Independently
changing the first incoming residual vector from 52 to 53 caused both to
exit nonzero. Deleting one incoming residual basis causes the independent
checker to reject the endpoint/basis count. These controls changed disposable
copies only. Both default commands compare the committed certificate without
rewriting it. Regeneration is explicit and package-local.

A separate read-only review confirmed the written h8 isometry lower bound,
all h9 witness residuals, quotient-plane completeness and the characteristic
test. That review identified the missing-basis `zip` failure mode; an explicit
two-bases-per-side check was added and its rejection verified. This is AI
assisted algorithmic review, not independent human peer review.

Every repository source hash in SOURCES.json was checked against the exact
base. Pending PR1139 was refreshed at unchanged head
82da1e827c51d94691134c6aec346357d89622bc. The open PR queue was refreshed
through PR1171; no matching weight-five shared-node package was found.
The contribution adds a distinct label class and threshold, crediting PR920
and PR1139 rather than presenting their fixtures or classification as new.

No root generator, selected source, upstream file, Makefile or workflow is
modified. The expensive repository-wide `make verify` and selected cold
supplier replay were not repeated for this isolated historical-geometry
research package. No hosted CI success or full multiplication theorem
certification is claimed.
