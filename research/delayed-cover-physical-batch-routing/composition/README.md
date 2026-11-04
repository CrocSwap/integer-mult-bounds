# Physical high-address router + codec + continuation boundary

This module executes the root router's actual split/merge microtables through a
stateless 3-bit facade and the unchanged retained continuation stack/output relay.
It passes a genuine V/L child input, preserves the complete parked parent, saves
the child output before pop, reinstalls it in an occupied parent bank and reuses
the same physical storage for two sequential sibling calls. For fixed L, there are K+7 fixed
tapes, K=max(16,L+8). A/R/depth arrive on physical tapes; no runtime code reads host head/cell
coordinates, action counts or a host recursive-frame list.

Scope: any compiled fixed L>=2 by the one-edge argument, physical child-shape
grants, bit-complement leaf. Actual new finite controls use L2/L3/L4/L9. No production descriptor evaluator, arbitrary-depth selected grammar,
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

The core router/machine/counters are unchanged copies. The composition differs
from its original29-case version only by the compiled K/return-slot ABI; the
router and physical continuation algorithms are unchanged. Existing stack and
return routines are exact main7c49fe32 Git blobs. All byte counts/SHA256 and
published source Git blobs are in SOURCES.json. The core router is now pinned to the exact PR6719 published source commit; the
retained root-router/SOURCES.json is an inert copy of its earlier local-draft
metadata. The new source inventory distinguishes these two provenance roles.

Credit: root physical router by thu-nmrc with substantial OpenAI Codex assistance;
David Arias' finite machine/counter lineage; Ali Romman's continuation and output
return; Mason Hale's selected-owned-dispatch codec/composition, with their retained
predecessors. New one-edge composition and exact controls: thu-nmrc with
substantial OpenAI Codex assistance, Apache-2.0. All checks are author-side AI
evidence, not external scientific acceptance.

## High-coordinate edge

The physical grant relation is A_parent=L*H*A_child and R_child=H*R_parent,
with actual #5829 R_parent=H^(j+1)*R_body and D>=j+2 when a child split is
invoked. The new cases choose D2/j0, so R_parent=H*R_body and
R_child=H^2*R_body. The exact root address identity is

    a_parent=(a_child*L+l_child)*H+h_child,
    a_parent*R_parent+r_parent
      =(a_child*L+l_child)*R_child+h_child*R_parent+r_parent.

The source's H coordinate is retained and returned to the same address.
All original29 H1 receipts are preserved exactly; four added nonconstant cases
are (L,H)=(2,2),(3,3),(4,3),(9,1). The final case actually uses24 tapes and
return slot16. Same-volume incorrect child indexing is explicitly distinguished.
The runtime reads only the physical child grants; it does not compute a
production shape/weight descriptor. Normal/O receipts and file hashes are in
VALIDATION.json and FILES.json.
