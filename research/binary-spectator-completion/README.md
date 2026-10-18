# Binary-only callees with nonbinary spectators

PR2399 explicitly leaves an adapter necessary when the earlier completed
binary interchange theorem promises only binary-complete spectators. This
package supplies that conditional adapter: coalesce each of the three
spectator regions before binary padding. Spectator volume grows by **less
than eight**, independently of ancestor depth; including the two active
radix-q fields gives **less than 32**. The completed exchange restores every
inner spectator coordinate, and padding closes before the next ring operation.

This is one recursive-interface implication, not a fast callee implementation,
selected stock coefficient, new supplier or multiplication exponent.

[PROOF.md](PROOF.md) states the uniform binary-callee, scan, parking and
descriptor hypotheses and proves the all-width reduction. The descriptor
boundary matters: arbitrarily many singleton ancestor descriptors can have
unbounded length at fixed payload volume. They cannot be reparsed for free;
the adapter receives three aggregate cardinalities and parks other metadata,
or charges its input length separately. Padding each ternary ancestor field
separately likewise incurs the unbounded ratio `(4/3)^depth`.

The scientific source is commdata2338's PR2399 at
`14458fda3cac4441c27980d584582ebbbb3e9233`, specifically its assumptions 1–3,
two-field substitution and explicit nonbinary-spectator limitation. Its
README and notice are retained unchanged. The reviewed PR185 source is a
contextual completed-row/restoration contract, not proof of the new adapter.
Exact SHA256 and Git blobs are in [SOURCES.json](SOURCES.json). The base is
canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.

## Reproduction

Use standard-library Python 3.12, from the repository root:

```sh
python3.12 -I -B research/binary-spectator-completion/verify.py
python3.12 -I -O -B research/binary-spectator-completion/test_verify.py
python3.12 scripts/research_package.py --package research/binary-spectator-completion
```

The checker authenticates sources before use and requires the committed
receipt. It performs 30 distinct-token complete-rectangle checks, all 4,096
Boolean payloads of a 12-cell nonbinary-gap case, 64,000 exact spectator
volume comparisons, mixed-radix order checks and arithmetic ancestor examples
through depth 1,000. Wrong endpoints, early restriction, changed spectators,
invalid domains, source corruption and receipt drift are failure controls.
Acceptance does not use removable Python assertions.

The payload adapter reads genuine input forward and restricts forward. Its
reference binary callee is an indexed host-memory semantic fixture. No fast
callee, full supplier cold replay, finite-alphabet compiler, Lean kernel,
physical time measurement or independent human review is claimed. The finite
replay supports the written argument, not its universal quantifiers.

## Open next questions

1. Join a source-bound faster completed binary callee to this adapter. Begin
   with a nonadjacent exchange and arbitrary dirty spectators. The preceding
   callee's uniform time, cleanup and parking contracts remain prerequisites.
2. Lower the aggregate counter scans to the retained tape machine, recording
   local head/cell traces at translated parking origins. The charged scan
   model is assumed here; the reference fixture is not that implementation.

The structured scope, overlap limits and next questions are in [TASK.json](TASK.json).

## Credit

commdata2338 supplied PR2399's two-field substitution, its leaf/header binding
and the explicit binary-only spectator gap. Jose Manuel supplied PR2234's
recursive caller; Adam Gall supplied PR2087's conditional time lift. The
retained source notice credits their selected supplier, source527, normalizer,
descriptor, fallback and parking predecessors. Rohan Arun's reviewed PR185
lineage supplies the retained completed-row/restoration context. Their
constructions and bootstrap formula are not claimed as new.

Prepared by ywz65 with substantial OpenAI Codex assistance in source reading,
proof, implementation and checking. New work is Apache-2.0; unchanged source
copies retain their attribution and notice.
