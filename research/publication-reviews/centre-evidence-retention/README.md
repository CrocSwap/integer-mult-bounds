# Review evidence supplement

This supplement retains 29 existing review outputs that were absent from
the 15 original publication heads. It adds 47,576 bytes of evidence. It
does not change a frozen package, checker, proof, receipt, or claim.

The [file list](SUPPLEMENT-FILES.json) gives each exact source,
repository destination, byte count, SHA-256, and Git blob identity. It
also records all 15 original heads. The added evidence is:

- Four encoder negative-control logs, in normal and optimized Python.
- The complete 21-file original-clean replay and guard-control output.
- Four query replay receipts with distinct final bytes. Their hashes
  already occur in the published replay summary.

The [independent retention review](REVIEW.md) checked these bindings.
[REVIEW.json](REVIEW.json) records the decision. Other local cold outputs
either duplicate published bytes, contain text already embedded in the
accepted replay record, or belong to temporary inputs and earlier runs.
Those local files remain preserved.

The coordinator must copy the listed files without byte changes. The
final Git-object audit must check the supplement commit together with
the 15 original heads. The original head files must remain unchanged.
No mathematical replay or kappa calculation was run for this retention
change. The existing mathematical scope and open obligations remain.
