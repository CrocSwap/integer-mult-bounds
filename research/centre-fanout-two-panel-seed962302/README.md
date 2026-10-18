# centre-fanout-two-panel-seed962302

**Bounded recursive-interface construction attempt; no new κ claimed.**

## Scope and evidence

Original assignment: recursive-interfaces, OS seed `96230294e168f4b58c665c3efdec8d3b`,
`centre-path-sharing`, priority revision 3, base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`.
The first selector draw returned the excluded `independent-verification` track and was discarded.
The scope refines the card to two invocations that share the same eight source-row values
and have disjoint target panels. It tests whether the selected centre trajectory can serve both
panels once while each panel retains its full target updates and all private state is restored.
The nearby #1516 work treats single-call dirty hosting; this package explores cross-call fanout
under an explicit shared-source condition.

The current selected record is `κ=836330098538459/500000000000000000` and has SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. Its review is
`docs/research/community-batch1099-review.md`; source manifest is
`research/community-frontier1094-audit/SELECTED-SOURCE.json`; certificate is
`research/community-frontier1094-audit/ASSEMBLY.json` with SHA256
`1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045`; reproduction is
`make frontier1094-verify`. The selected 480-helper emitted replay is pinned at
`research/community-frontier1094-audit/selected-replay.tar.gz`, SHA256
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`.

The exact 9-stage, 112-port planning profile changes from eight to four rank-8 children and
from centre charge 64 to 32 per call when two calls share one trajectory. The repository's
favorable relaxation gives `a_cap≈0.003213` and `κ_cap≈0.003203`; the unchanged bit side then
binds at `a=0.001733427039589844234749`, limiting any whole-bound gain to 3.4536%. This is
the binding cap for the whole supplier while the bit side stays fixed. The verifier charges
every local centre copy, clear, rank-8 move and both panels' target updates; it confirms that
the fused phase performs fewer setup/restoration operations and retains all target operations.
The unchanged non-centre paid profile is left untouched in the moment screen.

Exact source pins are in [SOURCES.json](SOURCES.json). The selected certificate, review and
record are provenance; all files listed as verifier inputs are live pinned dependencies.

## Reproduce

From the repository root:

```sh
python3 -I -B research/centre-fanout-two-panel-seed962302/verify.py
python3 scripts/research_package.py --package research/centre-fanout-two-panel-seed962302 --check-only
python3.12 scripts/research_package.py --package research/centre-fanout-two-panel-seed962302
```

The first command checks the selected source events and exact target coefficients, then compares
separate and fused schedules on all source, target-dirt and private-centre basis states over `Q`.
The selected rank-8 centre child is treated as a common linear map; the test uses a nontrivial
exact rational representative, and the algebraic identity holds for every common map, including
the inherited selected child. It checks three semantic failures, the complete local phase invoice
and the paid moment against the unchanged bit threshold. The registered command repeats the
same bounded replay through the repository hook.

## Scope and limits

The interface requires both invocations to see identical values in the eight selected source
rows while their target panels are disjoint. The finite construction establishes a local phase
rewrite under that condition. It does not show that the global supplier call schedule contains
such a pair, nor pay a new owner/precision/controller transformation needed to create one. The
unchanged bit supplier becomes binding in the optimistic screen, so no new selected κ follows.

## Open next questions

Does the selected assembly contain invocation pairs that meet the shared-source boundary without
extra owner, preparation, precision or hosting charges? The first step is to match the pinned
owner/call schedule to the eight verified centre-source functionals; this package does not claim
full supplier composition.

## Credit

Predecessor: Rohan Arun's selected PR #1094 and the retained gauge44-slots-t16 provider lineage.
This package uses the selected 480-helper replay archive, not the 492-helper ancestor in stored
evidence/local files. The local centre maps are inherited unchanged; the proposed contribution
is only the two-panel shared-source interface. Prepared by Cinna Davis with substantial OpenAI
Codex assistance in scope, cost calculation, verifier and exposition. No human or Lean
verification is claimed. New material is Apache-2.0.
