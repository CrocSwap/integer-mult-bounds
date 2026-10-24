# Whole first-node setup rejection ownership

The retained PR2697 Consumer constructs directories, odometers, geometry and
layout before entering its cleanup block. A valid width64/rank1/depth2/mod3
caller with insufficient fixed register inventory can therefore reject while
leaving newly owned numerical slots live. The new source adapter surrounds the
whole preparation interval and restores shared ownership on admitted ValueErrors,
then removes its hooks at the exact original packet-engine handoff.

The complete argument and domain are in PROOF.md. This is reachable source-array
ownership, not physical erasure of deallocated Python memory. It excludes host
allocation failure, concurrency, malicious mutation and post-handoff recovery.
The weak registry has bounded simultaneous entries and never retains all previous
allocations. Cleanup reads/writes/moves are metered; retained numerical backing
remains charged. No borrowed payload snapshots occur in the implementation.

Run `python3 -I -B research/first-node-setup-rejection-ownership/verify.py` and
repeat with `-O`. The verifier authenticates original sources before importing the
credited PR2825 fixture. It exercises full-width actual preparation and rejects
an omitted-rollback mutant. No complete selected GL64 payload is executed.

Attribution: Jose Manuel/jmbarrancoml's PR2697 source and PR2825 fixture/runtime,
PR2749 count-root inventory, and PR5135 complete successful source reserve remain
unchanged and pinned. New adapter, proof and checker: JoyboyBrian with substantial
OpenAI assistance, Apache-2.0. Original notices remain in their source packages.

## Open next questions

Physical bank reclamation, post-handoff failure ownership, and entry-parametric
preparation/rejection time are open; see the precise boundaries in PROOF.md.
