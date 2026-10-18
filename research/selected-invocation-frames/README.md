# Local invocation frames for a nested selected child

This supplies the local caller boundary needed to place a completed selected
child inside another caller. At pinned PR2534 the inherited wrapper checks the
root parking floor and all registered working tapes, so it rejects both an
already parked parent packet and a live foreign parent tape. Those checks are
correct for its documented flat scope. The new wrapper scopes parking and
cleanup to one invocation and proves a conditional composition rule for every
finite sequential call tree.

The concrete new invoice is exact: for active extent W and total parked extent
S, one wrapper adds `12(W+S)` charged moves and `2W+3S` reads, writes and erases,
excluding its callee. These costs add over the call tree. See [PROOF.md](PROOF.md)
for ownership, ancestor noninterference and all completed-return premises.

The actual selected PR2534 f=2 Compact child is executed inside three nested
callers, forward and inverse, on all 4,096 records. All eight selected wrappers
pass the exact tariff; each nested return preserves parent parking and a live
foreign tape at a nonzero head. An independent retained Gaussian oracle checks
the endpoint; final cleanup clears all work. Eight controls cover wrong
ownership/return/parking behavior and explicitly expose the raw-Python access
boundary. `RESULT.json` records the full deterministic receipt.

```sh
python3.12 -I -O -B research/selected-invocation-frames/verify.py
python3.12 -I -O -B research/selected-invocation-frames/test_integrity.py
python3.12 -I -B scripts/research_package.py --package research/selected-invocation-frames
```

Source baseline is canonical main
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4. Retained
PR2534 head is `f961dcb12061c3959058aed883f48b55f365eb80`; `VENDOR.json` pins
its code/proofs and earlier PR2250/2287/2483 lineage. `SOURCES.json` binds the
selected archive and native exact kernel. Dependency imports compile the
authenticated bytes, avoiding adjacent timestamp bytecode. No frozen source
or selected result changes. Initial author replay used native CPython 3.12.7
on Windows x64 with `-I -O -B`; validation metadata records the final checks.

The selected leaf, its native factor, Compact adapter and exact arithmetic
are credited predecessor work. This adds local invocation frames, their
conditional all-depth restoration proof, exact additive wrapper tariff and
nested source-bound witness. It does not provide a nonleaf recursive C callee,
a fixed-tape allocator/controller, whole-supplier hosting, a complete 73-axis
payload, an all-size numerical precision theorem or a new kappa. Runtime
checks are not a sandbox against raw Python mutation; successful completed
returns assume the stated access discipline. No rollback on failure is claimed.

## Open next questions

1. Bind an actual nonleaf numerical callee to this interface. Start with its
   exact input/output/grid contract and prove the intermediate argument and
   parking discipline. The remaining blocker is the recursive supplier,
   not the local caller cleanup condition.
2. Compile the frame descriptors and observational tape registry into a fixed
   sequential tape arrangement and price its controller. The additive payload
   tariff isolates the cost already known; allocation and directory control
   remain unproved.
3. Supply a whole-call-tree space/precision invariant for that numerical
   recursion. The present induction preserves completed return contracts but
   neither bounds recursion depth nor manufactures a numerical callee.

Substantial OpenAI Codex assistance was used for implementation, proof,
experiments and separate-agent review. No independent human review or formal
verification of the full multiplication theorem is claimed.
