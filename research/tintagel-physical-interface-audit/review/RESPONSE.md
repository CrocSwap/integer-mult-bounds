# Response to the Opus review of the original snapshot

The reviewed archive is preserved byte-for-byte under SHA-256
`250339fc95dc09247414978279afbaddcc9459509cb201b88c4f17afc84daf50`.
The private review report, omitted from this public copy, has SHA-256
`eae5353cc42655c25ddc5f5d4fceed37844516ff6718e931f424aca06e8ffb66`.
This v2 packet is a separate revision. The review's verdict applies to the
original snapshot; it does not assert that Opus reviewed this revision.
No theorem hypothesis, invoice, exponent or priority claim has been expanded.

| Point | Revision | Evidence and limit |
|---|---|---|
| A: controls overstated | Classify all 20 controls. Eight adapter controls now mutate actual recipes and compare them to all 512 independently recalculated exact columns. The corrupted-source control invokes the actual `binding()` verifier on temporary copied sources. | `replay.py`, `exact_checker.py:validate_adapter_recipe`. Categories: 1 schedule pipeline mutation; 8 exact recipe mutations; 1 computed route-mutation witness; 5 algebra/coverage witnesses; 4 statement-drift guards; 1 source-binding pipeline mutation. The wrong-inverse case remains accurately labelled a computed witness, not a full mutated emitted-program replay. |
| B: newly resolved | Replace with “independently re-verified.” | Endpoint proof and attribution consistently credit PR390's existing adapters. |
| C: sink provenance | Add unmodified PR390 sink-audit data and changed-walk source as read-only evidence. Check the accepted 355→206, 403→221 mapping, binary final values 1/1, both indexed frame lists, and decoded SHA-256 matching the frozen-main-source note. | `endpoint_provenance()`, `PROVENANCE.json`, endpoint proof. Only frame contents come from the binary. The changed walk and actual sink action remain unverified premises. The compiler source is inspected as text, never executed. |
| D: backward orientation | Add the multiplicative inverse-adjoint argument, crediting the endpoint candidate and PR401. Since the three operators are unitary, the same adapter is valid in the same chronological position for an inverse-adjoint live macro. | Endpoint proof. CLEAR/COPY scratch and actual emitted backward chronology still require separate complete-macro evidence. |
| E: count provenance | Count local calls from the replica/stage loop, adapter uses from rank-eight roles at each call, padding from missing-axis additions times stage count, and live families from the actual index union. Mark 59,692 as `source_declared_physical`. | `endpoint_banks()`, receipt `count_provenance`, endpoint proof and BOUNDARIES. Counts describe the reconstruction, not an emitted primitive program. |
| F: repeated evidence | State that 12,240 projector and 3,060 polynomial checks are repeated instances of a few identities, not independent obligations. | BOUNDARIES. Universal quantifiers still come from the proof. |
| G: unused expected copy | Read and compare `expected/literal-endpoint-adapters.json` with the freshly computed adapters. Rename its status to describe a derived expected copy. | Replay fails on any mismatch. It is not a separate model certificate. |
| H: portability | Recommend `python3 -I -B`; reject unlisted files, symlinks and unsafe manifest paths. Receipts belong outside the packet. Preserve the original 55-source expected count as historical context and report this packet's 35 blobs separately. | `integrity()`, README and portability tests. Hashes are integrity bindings, not authenticated remote signatures. |
| I: attribution | Explicitly credit PR401's all-512-column/global-phase method on 26 frames; PR377/PR381's B4 lineage; existing k=3 scalar checks; Sussman's generic window machinery. | NOTICE, NOVELTY and B3 proof. PR377 itself remains uninspected; its attribution is sourced to the bundled PR404 notice. No novelty/priority claim is added. |

Additional review observations addressed:

- Define sigma as the excess local paid rank mass over `2v(h-1)+Rh`.
- State non-vacuity through the pinned `XCircuit.inv`, without treating it as
  an optimized PR390 physical instance.
- Add a standalone Lean positivity lemma for idle ranks and print dependencies
  for all 15 theorems. Clarify that finite list arithmetic is not a Lean proof
  of orthonormality, spanning or full Clifford semantics.
- Bind Lean's exact compiler version, source SHA-256 and complete axiom output
  in `formal/VERIFICATION.json`; fresh optional compilation must reproduce it.

Verification procedure for the final archive is recorded in the companion
`final-v2-delivery-receipt.json`, `final-v2-replay-receipt.json` and
`final-v2-portability-tests.json` files outside this packet. It includes full
exact replay from an extracted archive in a path with spaces and an unrelated
working directory; fresh installed Lean compilation with matching axiom output;
optimized-mode rejection; modified-source rejection; planted-module/extra-file
rejection; and scope-drift rejection after deliberate manifest recomputation.
The review snapshot hashes are checked again during final packaging.

Remaining scope boundaries are unchanged: the physical local package, complete
PR390 modified walk and backward emitted chronology, nine-stage data endpoint,
all-size compressed windows, compiler/precision/bit/router bounds and exponent
are not certified. The publication copy adds the bounded read-only overlap
check in `NOVELTY.md`, including PR406–412 proof summaries and PR413–416 bodies.
Those implementations and full proof chains have not been verified here.
The original offline revision is preserved; the public copy changes only
attribution/provenance and distribution metadata, plus one attribution comment.
