# Literal complete-row parking caller

A fixed eight-port, four-symbol wrapper replaces host slicing at the retained
W=2 parking boundary. It splits complete runtime-width rows, calls each actual
parking boundary, then rejoins and erases the owned roles. Both children receive
exactly V/2 bits. The wrapper costs at most 60V+107 steps, including descriptor
resets and cleanup; child costs and semantic/locality premises remain separate.

See [PROOF.md](PROOF.md) for the successful-call ABI, complete invoice and
K0-relative retained-backing theorem. This is one conditional caller theorem,
not a complete recursive tape scheduler or multiplication supplier.

Run `python3 -B research/literal-complete-row-parking-caller/verify.py`.
The independent finite oracle uses different children, 218 cases, 10 controls,
complete snapshots and visited intervals. No Lean/kernel verification was run.

Exact source hashes/blobs and predecessor credit are in SOURCES.json. The code
reuses commdata2338's recursive-parking controller, JoyboyBrian's R8 row Builder,
and original credited transfer Lean tables without editing those sources.
New work: JoyboyBrian with substantial OpenAI Codex assistance, Apache-2.0.

## Open next questions

Supply a paid external descriptor conversion, global fixed-tape recursive
outer-port reuse, and children satisfying the stated frame and uniform resource
contracts. The first next step is an ownership schedule before claiming recursion.
