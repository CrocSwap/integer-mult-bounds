# Native warp events must carry their declared frames

This package reproduces the event-to-frame gap reported by jwr404 in
[issue #4571](https://github.com/CrocSwap/integer-mult-bounds/issues/4571)
and supplies an independent prerequisite checker. It checks **2,880 actual warp
events** in twelve oriented programs. It establishes no new κ and does not
change the frozen evaluators or automatically guard their callers.

## Result and scope

The frozen buffer replay accepts the reported two-label mutation in both
orientations of the selected PR4470 word: two inverse warps on `L273` are
relabelled from `0 → 0 → 0` to `0 → 1 → 0`, where frame 1 has dimension nine.
The formal operator words still cancel, all endpoint rows pass, and the paid
profile stays `{1:2237, 2:388, 3:494, 4:147, 5:36, 8:8}`. This is a reproduced
acceptance gap, not a counterexample to the selected multiplication claim.
The mutant is rejected by the additional check at event 3 in both directions.

`warp_frames.py` reads the actual event's signed operator, old frame and new
frame. It checks exact equality of binary subspaces, rather than only their
dimensions. It also rejects singular maps, duplicate operator IDs, dependent
frame bases, missing frames and unknown/zero operators. Equivalent bases for
the same subspace are accepted. `RESULT.json` records the fixtures, the legacy
counterexample and thirteen rejection controls, including a non-involutive
order-three map that distinguishes positive and negative operators.

All six pinned fixtures pass, each with 72 operators and 240 warp events per
orientation:

| Fixture | Source and status |
| --- | --- |
| THREE-base, THREE-extra, FOUR-base, FOUR-extra | Retained converted native words and their canonical tables |
| PR4470 | Current selected constructor at the pinned main commit |
| PR4610 | Actual word retained by PR4616; frame transport acceptance only |

The last fixture shows that the checker accepts a changed, valid operator
table. It does not require the maps to equal the selected table. It does not
admit PR4610's operator substitutions, phases, endpoint identity or κ claim.
Only the buffer evaluator's legacy acceptance is rerun; the corresponding
`native_extensions.py` finding remains attributed to the original issue.

## Exact implication

Let `U_f` be the span over F₂ of frame `f`, and let `G_k` be the binary map
whose columns are the canonical table's `G_columns` for positive operator `k`.
The native frame declaration for an event `['warp', role, op, old, new]` is

```
op > 0:  G_op(U_old) = U_new
op < 0:  G_|op|^(-1)(U_old) = U_new.
```

The checker enumerates the 512 images of each nine-bit map and requires all
images to be distinct. The map is therefore invertible. For negative `op`,
applying `G_|op|` to both sides makes the second condition equivalent to
`G_|op|(U_new) = U_old`. Both checks are finite exact set equalities. Checking
each event separately is needed even when the canonical table's own
`from_frame` and `to_frame` declarations are valid: those declarations do not
constrain the frame labels supplied by a different emitted word.

This proves the stated binary frame-transport condition for each accepted
event, with the supplied canonical maps. It does not establish Clifford
absolute phases, frame chronology between events, scalar actions, dirty-state
restoration, paid tariffs, all-column validity, or a multiplication theorem.
The ordinary literal and physical checks remain separate obligations.

## Reproduce and reuse

From the repository root, using Python 3.12 and no third-party packages:

```sh
python3 -B scripts/research_package.py --package research/native-warp-event-binding --check-only
python3 -B scripts/research_package.py --package research/native-warp-event-binding
```

The registered run authenticates all declared live inputs, constructs the
selected word in an isolated interpreter with a private empty bytecode cache,
checks the fixtures and controls, and compares the deterministic receipt.
`verify.py --write` regenerates `RESULT.json` using the same checks.

For a word with separate canonical and program JSON files, including `.gz`:

```sh
python3 -B research/native-warp-event-binding/warp_frames.py canonical.json.gz native-word.json.gz
```

Alternatively, import `audit(canonical, programs)` from `warp_frames.py` before
the existing literal replay. `programs` maps orientation names to event lists.
An invalid transport raises `ValueError` with the orientation, event index,
role, operator and frame IDs. The CLI checks supplied data; it does not
authenticate those files against repository provenance. The registered audit
does authenticate its declared inputs. A pass is only the frame prerequisite.

## Provenance and overlap

Scientific baseline: main `b91956876e5b4122fd89179f1b57557ff8378f15`, priority
revision 7, selected κ `60403/20000000`. Exact blobs and SHA256 pins are in
`SOURCES.json`. The catalogue and selected record are historical provenance;
the explicit inputs are authenticated live dependencies.

The overlap refresh on 2026-10-23 at 05:05 UTC covered 319 open PRs and 4,077
discussion records with complete remote pagination. The sparse local search
did not cover all 6,636 tracked notes. The directly relevant existing
`pr4610-warp-substitution-check` and `complex-cover-lift-audit/native_warps.py`
were inspected: they check canonical maps/classes, while this package checks
every emitted event's labels. This is bounded overlap evidence, not a novelty
certificate. The original task card is changed from historical four-provider
admission to this prerequisite in the current native caller; see `TASK.json`.

## Open next questions

1. Install this prerequisite in a new caller that admits caller-supplied native
   words, preserving the frozen predecessor files. First identify its exact
   mutable-word entrance and invoke the audit before any profile acceptance.
   The integration needs that caller's complete endpoint and physical checks.
2. Independently check phase-corrected physical lowering for changed valid
   warp tables. Start with a single substituted map from PR4610 and retain
   spectator and absolute-phase obligations. Binary transport alone is
   insufficient. These questions are also structured in `TASK.json`.

## Credit

jwr404 (James Reed) reported the gap, supplied the two-label counterexample and
proposed the span-image check in issue #4571. Ryanson Jonathan's PR4616 checks
PR4610's canonical map substitutions; intqwq supplied that candidate word.
The retained native/caller lineage includes Cinna Davis's PR4470, the credited
fresh-helper-boundary and missing-join-frame predecessors, and the authors
retained in their frozen source files. This package adds event-level checking
and executable controls; it does not claim the original discovery.

Prepared by 1337isnot1337 with substantial OpenAI Codex assistance. Apache-2.0.
