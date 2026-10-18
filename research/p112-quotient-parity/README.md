# An odd-class quotient argument excludes P112 `4,5^9`

Ten independent P112 pieces with code intersection dimension at least five
cannot have binary support-rank bounds `4,5^9`, over any characteristic-zero
field. This is the explicit TWOSIDE `(5,5)` profile left as an open next
question by [PR3169](https://github.com/CrocSwap/integer-mult-bounds/pull/3169).

The earlier support estimate gave 56 where quotient independence required
less than 53. The new proof selects a different quotient basis. Six piece
images in a four-flat would force six distinct E8 root lines into a plane,
which has at most three. Contracting a triple containing the distinguished
weight-four piece leaves seven points in classes of size at most two.
An odd number guarantees a singleton and hence the required four-piece set.
The resulting root-simplex incidence count gives `795 <= 756`, a contradiction
with margin 39. [PROOF.md](PROOF.md) states every hypothesis and implication.

[RESULT.json](RESULT.json) records the complete 3,309,747-flat census,
all 7,140 root-plane pairs, 960 reflections, all 232 seven-vertex matchings,
and the literal profile's original weight-filter binding. Fourteen behavioral
groups include an independently calculated rational six-circuit fixture,
even-parity and malformed-partner failures, strict support cutoffs, exact
endpoint counts and changed-input rejection.

This closes one finite decoder-floor configuration. Full C5, `C(P112)>=64`,
supplier admission and an improved kappa remain open. The selected conditional
kappa is unchanged at `0.001672660197076918`.

## Reproduce

Python 3.12 or later, standard library only. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-quotient-parity-replay"
mkdir -p "$RUN"
TMPDIR="$RUN" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-quotient-parity
```

An existing Python 3.12 executable can replace the `uv run` prefix. The two
registered commands run sequentially with 120-second limits. The first checks
inputs and reconstructs the mathematical receipt; the second runs the controls
with optimization enabled. `verify.py --output NEW_PATH` writes a new external
receipt and refuses to overwrite an existing file. Git-free direct replay uses
`verify.py` and `test_verify.py`, with this package and its single declared
P112 input at the same repository-relative path. [CHECKS.json](CHECKS.json)
records actual environments, commands and verification limits.

## Open next questions

Does the six-circuit restriction help another actual remaining beta profile?
Pin the live cell and check its four-piece and five-circuit support bounds
before expanding. The all-weight-five case already fails this proof's edge
cutoff, so no extension is claimed. Separately, the quotient-selection lemma
could be kernel-verified with the four-flat restriction as an abstract premise.
Structured questions and blockers are in [TASK.json](TASK.json).

## Credit and scope

Nick Petalas contributed the quotient-parity proof and this named exclusion.
DreamingOfClouds's [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154)
provides TWOSIDE, its necessary weight filters and the C5 handoff.
Nick Petalas's [PR3164](https://github.com/CrocSwap/integer-mult-bounds/pull/3164)
provides the root-simplex proof and geometry code; [PR3169](https://github.com/CrocSwap/integer-mult-bounds/pull/3169)
identifies the specific failed independence step. The retained E8/P112 and
decoder lineage includes DreamingOfClouds's packages and joaqcoo's original
model. [SOURCES.json](SOURCES.json) records exact heads, paths, Git blobs,
SHA256 hashes and code origins. Historical sources were checked locally;
fresh CI needs canonical-base provenance and the sole declared live input.
All new and reused code is Apache-2.0. Frozen predecessors remain unchanged.

Development and local checks used substantial automated assistance. Internal
read-only mathematical reviews are not independent human review. The standard
Weyl-chamber theorem is an explicit dependency; no proof-kernel verification or
complete supplier replay is claimed. [ENGINEERING.md](ENGINEERING.md) records
bounded implementation decisions and the retained decision trail.
