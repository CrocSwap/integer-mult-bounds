# P112 `2,4,5^9` excluded by D7 support saturation

Eleven independent P112 pieces with code-intersection dimension at least five
cannot have weight bounds `2,4,5^9`, over any characteristic-zero field.
This is one additional actual TWOSIDE `(5,6)` profile from DreamingOfClouds's
[PR3154](https://github.com/CrocSwap/integer-mult-bounds/pull/3154).

The new proof extends PR3174's quotient selection to a support-34 starting
union. Any surviving configuration must contain a non-root D7 edge with
support exactly 70. Equality forces disjoint supports of sizes `2,8,12^5`.
The sharp D7 packing maximum is three disjoint saturated twelve-point
five-flat supports, while this configuration requires five.
[PROOF.md](PROOF.md) gives the characteristic-zero argument and finite coverage.

[RESULT.json](RESULT.json) records the complete 3,309,747-flat census,
240-frame stabilizer orbit, 756-vertex packing graph, sharp three-set witness
and original profile binding. Fourteen behavioral groups include a separate
enumeration of every disjoint packing, a planted four-set failure control,
the losing strict-cost profile, source changes and receipt changes.

This is a scoped mathematical exclusion and a finite packing theorem.
Full C5, `C(P112)>=64`, supplier admission and an improved kappa remain open.
The selected conditional kappa stays `0.001672660197076918`.

## Reproduce

Python 3.12 or later, standard library only. From the repository root:

```sh
RUN="$HOME/.cache/integer-mult-bounds-runs/p112-d7-replay"
mkdir -p "$RUN"
TMPDIR="$RUN" uv run --python 3.12 --no-project python -W error -B \
  scripts/research_package.py --package research/p112-d7-saturation
```

An existing Python 3.12 executable can replace the `uv run` prefix.
The two registered commands run sequentially, with 120-second limits.
The second runs under optimization to check that mathematical guards stay
active. `verify.py --output NEW_PATH` creates a fresh external receipt and
refuses to overwrite it. Direct Git-free replay needs this package and its
sole declared P112 input at the same repository-relative path.
[CHECKS.json](CHECKS.json) records executed checks and limits.

## Open next questions

Can an actual remaining profile force four saturated twelve-point supports
inside a D7 support? Name the original profile and first derive its complete
quotient and support budget. A support-71 edge need not be a root or D7
direction under the present classification gate. Avoid extending this
finite packing census before establishing the new profile's hypotheses.
Structured relevance and blockers are in [TASK.json](TASK.json).

## Credit and limits

Nick Petalas contributed the new D7 saturation implication, frame-orbit
reduction, sharp packing bound and `2,4,5^9` exclusion. DreamingOfClouds's
PR3154 supplies TWOSIDE, its original filters and the C5 handoff. Nick
Petalas's PR3164 and [PR3174](https://github.com/CrocSwap/integer-mult-bounds/pull/3174)
supply the root-simplex and quotient-selection predecessors.
[PR3175](https://github.com/CrocSwap/integer-mult-bounds/pull/3175)
retains the unchanged `vendor/geometry.py`, following PR3164/3162/3161.
The E8/P112 decoder lineage includes DreamingOfClouds and joaqcoo's model.
Exact heads, Git blobs, hashes and copied-code origins are in
[SOURCES.json](SOURCES.json). Frozen predecessors are unchanged.
All new and copied code is Apache-2.0.

The standard Weyl-chamber theorem is an explicit dependency. The finite
checks and internal read-only reviews are not independent human review or
proof-kernel verification. Full supplier replay is outside this scope.
Development and local checks used substantial automated assistance.
[ENGINEERING.md](ENGINEERING.md) records implementation limits and decisions.
