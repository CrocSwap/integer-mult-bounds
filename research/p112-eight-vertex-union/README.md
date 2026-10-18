# P112 `4,5^2,6^8` excluded by an eight-vertex support union

Eleven independent P112 pieces with code-intersection dimension at least seven
cannot have weight bounds `4,5,5,6^8`, over any characteristic-zero field.
This excludes one of the 154 original TWOSIDE `(7,4)` profiles in
DreamingOfClouds's [PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154).

The new proof follows PR3176's adjacent twelve-piece result. The eight-vertex
mixed-edge census requires at least 162 endpoint incidences against allowance
160. One all-root A7 branch defeats the arbitrary-cut relaxation, which gives
only 158. Keeping the actual binary four-/five-/five-flat support union repairs
that gap: every one of 2,025 frame choices again requires at least 162.
[PROOF.md](PROOF.md) gives the characteristic-zero argument and full coverage.

[RESULT.json](RESULT.json) records 9,737 mixed six-cliques, both root-star branches,
all frame orbits, 6,619,494 binary four-/five-flats, filtered support unions and
positive witnesses. Fourteen behavioral groups include separate Gram/rank/clique
and set-union calculations, source and receipt mutants, a planted failing union,
and a substantive one-extra-cut control.

This is a scoped mathematical exclusion. Full C5, `C(P112)>=64`, physical
suppliers and a new kappa remain open. The selected frontier is unchanged.

## Reproduce

Python 3.12 or later, standard library only. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-eight-vertex-replay"
mkdir -p "$RUN"
TMPDIR="$RUN" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-eight-vertex-union
```

An existing Python 3.12 executable can replace the `uv run` prefix. The two
registered commands run sequentially with 180-second limits. The second uses
optimization to verify that guards remain active. `verify.py --output NEW_PATH`
creates an external receipt and refuses to overwrite it. Direct Git-free replay
needs this package and its sole declared P112 input at the same relative path.
[CHECKS.json](CHECKS.json) records executed checks and limits.

## Open next questions

Does another actual remaining TWOSIDE profile meet a useful support-union
version of this lemma? First pin that profile and derive its quotient dimension,
edge cutoff and complete support budget. Larger supports may admit additional
D7 directions or E6 faces. Replaying this census with a different seed adds no
coverage. Structured relevance and blockers are in [TASK.json](TASK.json).

## Credit

Nick Petalas contributed the eight-vertex extension, complete frame-orbit and
weighted support-union checks, and this profile exclusion. DreamingOfClouds's
PR3154 supplies the original TWOSIDE filters and open-conjecture handoff.
Nick Petalas's [PR3176](https://github.com/CrocSwap/integer-mult-bounds/pull/3176)
supplies the retained support-72 alphabet and mixed-edge normalization, following
PR3164/3175's root-simplex and support-spectrum arguments. The retained E8/P112
decoder lineage includes DreamingOfClouds and joaqcoo's model. Exact heads,
Git blobs, hashes and copied-code origins are in [SOURCES.json](SOURCES.json).
Frozen predecessors are unchanged. New and copied code is Apache-2.0.

A [concurrent claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19000159)
on the same profile appeared after the initial overlap snapshot. It proposes
retaining two five-flat supports while relaxing the rank-four support to eight
arbitrary coordinates. This package supplies a separate actual four-/five-/five-flat
union proof and replay. No exclusive priority is claimed.

The standard Weyl-chamber theorem is an explicit dependency. Finite checks and
internal read-only reviews are not independent human or proof-kernel review.
Full supplier replay is outside this scope. Development and local checks used
substantial automated assistance. [ENGINEERING.md](ENGINEERING.md) records
implementation limits and decisions.
