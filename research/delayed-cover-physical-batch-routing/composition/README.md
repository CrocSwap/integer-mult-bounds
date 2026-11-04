# Physical router + codec + continuation boundary

This module executes the root router's actual split/merge microtables through a
stateless 3-bit facade and the unchanged retained continuation stack/output relay.
It passes a genuine V/L child input, preserves the complete parked parent, saves
the child output before pop, reinstalls it in an occupied parent bank and reuses
the same physical storage for two sequential sibling calls. There are23 fixed
tapes. A/R/depth arrive on physical tapes; no runtime code reads host head/cell
coordinates, action counts or a host recursive-frame list.

Scope: L2/L3, one unequal child edge, physical child-shape grants, bit-complement
leaf. No production descriptor evaluator, arbitrary-depth selected grammar,
Gaussian child, physical supplier, assumption discharge or kappa is claimed.
See PROOF.md for the exact contract and limits.

Run with Python3.12 and the standard library:

    python3.12 -I -B verify.py
    python3.12 -I -O -B verify.py

The default authenticates sources before import and compares RESULT.json without
writing. --write is explicit receipt authoring only.

## Portable layout

Keep composition.py, verify.py, SOURCES.json and RESULT.json together. The only
imported scientific source files are:

- inputs/root-router/router.py
- inputs/root-router/machine.py
- inputs/root-router/counters.py
- inputs/research/delimited-continuation-stack/stack.py
- inputs/research/continuation-output-return/return_output.py

SOURCES also authenticates four inert provenance references already included:
root-router/SOURCES.json and the selected-owned-dispatch prototype/README/SOURCES
under inputs/. Consequently include every listed SOURCES copy when relocating
the default checker. No runtime path outside this module is read, and no Git,
network, installed package or workspace-specific path is required.

The source router/machine/counters are unchanged copies. Existing stack and
return routines are exact main7c49fe32 Git blobs. All byte counts/SHA256 and
published source Git blobs are in SOURCES.json. The root router itself was an
unpublished local draft when copied and is honestly identified as such; its
bytes can be matched to the parent package's core before publication.

Credit: root physical router by thu-nmrc with substantial OpenAI Codex assistance;
David Arias' finite machine/counter lineage; Ali Romman's continuation and output
return; Mason Hale's selected-owned-dispatch codec/composition, with their retained
predecessors. New one-edge composition and exact controls: thu-nmrc with
substantial OpenAI Codex assistance, Apache-2.0. All checks are author-side AI
evidence, not external scientific acceptance.
