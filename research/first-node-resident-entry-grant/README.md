# Complete first-range Node/Driver resident backing grant

The unchanged PR2697 caller keeps arrays outside `Consumer.apply`: the peeled
input, split families, staged packets, copied private input, cleared locals,
count tapes, programs and numerical arena free slots. PR5135 bounds the complete
Consumer body above an arbitrary `K0`; it does not construct that caller grant.

This package supplies a conservative **declared-resource** source-array grant
for the complete successful first-range Node/Driver and every actual MOVE,
COPY and idle Consumer entry. Every term comes from input geometry, named input
backing lengths, declared numerical capacities and fixed source inventories.
No measured maximum or unnamed local K0 is an input. See [PROOF.md](PROOF.md)
for the full bound, root inventory, extent proof and composition with PR5135.

The grant counts retained `Tape.cells` / `Word.cells`, including erased tails,
markers and arena templates. It is not Python heap accounting, physical tape
capacity, an improved asymptotic bound or a sharp constant. Foreign arrays,
including suspended parents, remain an explicit `K_external`. PR2753 already
proves a different recursive logical live-symbol ledger; its changed recursive
Consumer is excluded. Setup failure/rollback is separate work.

## Evidence

```
python3.12 -I -B research/first-node-resident-entry-grant/verify.py
python3.12 -I -O -B research/first-node-resident-entry-grant/verify.py
python3.12 -B scripts/research_package.py --package research/first-node-resident-entry-grant
```

The checker authenticates all50 original PR2697 files before source-only imports,
the original count cohort, and the20 runtime modules (including lazy children)
used by PR5135. Frozen sources are unchanged. It executes the actual original
Node/Driver with the original GL2 model, stopping at first MOVE and COPY entries;
the COPY fixture completes the preceding actual model residual. A separate
idle-only fixture reaches the actual idle entry. A complete exchange-only model
Node covers split, Driver exchange, merge and normal return with an independent
family-order oracle. The 15,552-bit model is not selected GL64 execution or a
complete selected global word. No historical verifier suite runs.

A weak observer takes direct distinct-array censuses at the entry boundaries.
It does not keep dead Tape objects alive. The first MOVE cut retains a cleared
82-cell gather result and cleared3-cell stock Count; source/peeled and
fibre/following alias. Counted arena backing persists beyond freed live Words.
An independent owner-graph traversal rejects a real observer mutation that omits
one such cleared resident. The written
source inventory, not this finite sample, supplies the all-domain proof.

The ledger rejects malformed/boolean/negative resource values and checks its
category sum independently. Exact JSON serialization distinguishes receipt
scalar types. Validation and cold-export evidence are recorded separately.
No independent human or formal-kernel review is claimed.

## Open next questions

Canonical successful PR2697 first-range n in[64,128), positive complete extents,
fixed selected topology, original coefficient/factory implementations and
admitted numerical semantics are required. Numerical capacity is a declared
resource, not a promise that any chosen capacity suffices. Named borrowed arrays
may have erased tails, charged explicitly at entry. Externally retained prior
outputs must be paid as foreign input on later calls.

1. Replace capacity bounds with a proved whole-Node numerical high-water increment,
   including routes and original-offset peel.
2. Establish the corresponding contract for PR2753's changed recursive interior
   and frame retirement before bounding suspended parents.
3. Supply physical bank placement, movement and blank-return; source-array lengths
   alone do not lower this caller to fixed tapes.

Credit Jose Manuel/jmbarrancoml PR2697 and original retained NOTICE; David Arias
PR2753; Nick Petalas payload/count/continuation results; Ross Richardson numerical
and packet results; ywz65 directory work; and PR5135's complete Consumer join.
New work JoyboyBrian with substantial OpenAI Codex/Astra assistance, Apache-2.0.
