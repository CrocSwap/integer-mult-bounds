# Fresh verification receipts

These receipts belong to `../pr699-frame-retiming/`, whose exact frozen source
manifest is named in `RESULT.json` and `RECEIPT.json`. The cold command and
Python/zlib environment are recorded in `ENVIRONMENT.json`. Every output was
written to a new directory; native programs, phases, controls and the global
invoice were freshly rebuilt from the package's pinned PR699 input word.

`RESULT.json` records the exact conditional κ, final profile, source/native pins
and control census. `RECEIPT.json` records hashes of generated artifacts; these
can be reproduced with the README command, but most large generated programs
are not duplicated here. The full construction, audit, owner and exact pricing
receipts are retained below. This is incremental verification; neither the
ancestral PR699 construction nor the cited PR589 bit circuit is rebuilt by this
command. All inherited all-size and analytic assumptions remain conditional.

`CLAIM.json` records assignment seed 60, bounded experiments, the final scope
and handoff. `OVERLAP-CHECK.json` records the concurrent PR741 head and our
independent contribution. PR741 published the same construction first.
