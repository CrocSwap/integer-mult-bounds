# Linear-transition canonical switch queries

One fixed 3,237-location, fourteen-tape program returns the exact canonical
padded-rotation switch bit with at most `1024(h+4)` literal transitions.
It preserves all five borrowed descriptors, returns one owned bit, clears
eight private bodies and their guards, and restores all heads. Historical
backing increases by at most `16(h+4)` cells. This is a physical query
construction and scoped proof. **No new kappa** follows.

The program implements PR7734's closed descent on the unchanged PR7593 ABI.
Canonical shrinking counters and one two-carry scan avoid repeated full-width
child operations. The bound includes height expansion, format/domain checks,
arithmetic, output, clearing and head returns. The standalone linear order
is sharp by the predecessor's input-bit lower bound.

Read [PROOF.md](PROOF.md), [program.py](program.py), [RESULT.json](RESULT.json),
[SOURCE-PINS.json](SOURCE-PINS.json) and [CREDITS.md](CREDITS.md).

## Reproduce

Use Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/linear-tape-rotation-switch
```

Normal and optimized commands print:

```text
PASS_LINEAR_TAPE_ROTATION_SWITCH 14 tapes; 1024*(h+4) transitions
```

Two instruction interpreters agree on all 1,566 entries of 49 complete small
networks, the 544-query historical row, and 42 wider queries through height
4096. They check every returned cell, head, visited span and transition count.
Thirteen malformed domains, three wrong-semantic graphs, one failed private
retirement and owner aliasing provide controls. The finite checks support
the all-height proof; they do not replace it.

For the same 544 supplied fixtures, a fresh retained-graph run uses 1,473,152
transitions; the new graph uses 1,341,888, with maximum 2,545 per query.
Both counts include service setup and cleanup. Host fixture serialization,
current-state offsets, transport, output use and retirement are excluded.
These are exact service counts, not wall-clock timings or a complete caller.

## Scope

The five input descriptors and blank, disjoint working windows are supplied.
The physical ABI and framing boundaries are stated in the proof. The graph
has no runtime host-integer, arbitrary move, array lookup or callback operand.
The builder and primary hardware are retained dependencies; the sparse
interpreter is a separate implementation on the same emitted graph and ABI.
No independent human or formal-kernel acceptance is claimed.

Current CRT source/offset production, descriptor conversion, payload updates,
transport, output retirement and a complete repeated-query bill remain open.
All five selected framework assumptions remain. Historical full suites,
selected cold replay, Lean and Docker were not run. The selected frontier
is unchanged.

## Open next questions

- Compose this exact service with one current-state CRT offset producer and
  payload consumer. Start with the historical `(h,s,j)=(5,17,6)` boundary.
  Preserve owner leases and charge descriptor conversion and output retirement.
  The present fixtures supply serialized inputs, so they do not close this gap.
- Compare a complete query stream with retained ROM reuse on the same inputs.
  Include construction, transport, access and disposal on both sides. The
  service counts alone do not establish that workload comparison.

`TASK.json` records the scope and these questions. The canonical base is
`e54523517d0f03e58352e647c403a5af3e525a57`, priority revision 8. Selected
bindings pass; the catalogue's assessment is older than the selection.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Credit Jerry
Chen for the physical ABI, builder and primary hardware, Nick Petalas for
endpoint/child formulas, Ali Romman for the closed descent, and Cinna Davis
for the canonical compiler. The eleven retained files and their notices
remain unchanged. Apache-2.0.
