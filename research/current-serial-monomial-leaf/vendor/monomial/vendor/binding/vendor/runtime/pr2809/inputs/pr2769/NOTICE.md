# Attribution

Jose Manuel (`jmbarrancoml`) wrote the numerical-bank codec, its composition
proof, exact sequential invoice and tests with substantial OpenAI Codex
assistance. Apache-2.0. We claim no independent human or formal-kernel review.

We retain these source files without byte changes:

- `vendor/words.py`: Jose Manuel's PR2697, commit
  `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, originally
  `research/selected-bit-node/vendor/words.py`. The retained selected
  coefficient/stream lineage includes PR2332/2364/2405/2449/2501/2569,
  the PR2234 recursive specification, and the source527/PR589 construction.
- `vendor/parking_machine.py`: ywz65's PR2635, commit
  `1662dda699d9ea57b3fb13a23873b087d765149f`, originally
  `research/finite-parking-frames/machine.py`. ywz65 supplied the two-tape
  finite table, matched-frame proof and exact table invoice with OpenAI
  Codex assistance. Its PR2574/2534/2483/2250/2287 lineage retains credit.
- `vendor/pr2753_recursive_call.py`: David Arias's PR2753, commit
  `7dba5452a4071a856a0b11cebdcd2d3b6bcd7659`, originally
  `research/selected-bit-recursive-caller/recursive_call.py`. We retain it
  as reference text only. David Arias supplied the concurrent all-size
  logical caller, iterative scheduler and joined logical reserve with
  substantial OpenAI Codex assistance.

The source creators retain their original credit. This contribution does
not claim a new generic stack construction or first logical recursive caller.
The new boundary is the literal bank/slot/word serialization into the existing
parking table, same-slot restoration, fixed physical inventory and complete
sequential-operation invoice.
