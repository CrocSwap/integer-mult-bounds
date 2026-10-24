# Structured-centre physical transfer

The original and scaled coherent implementations are complete as local
physical words. Both normal and optimized runs pass. Each implementation
contains six variants for each of the two source providers. The scaled
implementation is the cheaper one:

```text
balanced backward:    91208 scalar, mass5073
diagonal backward:    91592 scalar, mass5073
normalized backward: 96012 scalar, mass5073
balanced forward:    91830 scalar, mass5073
```

Every complete word checks all 640 input columns and all 91 private zero
buffers. It restores 408 arbitrary helpers and leaves all eight owned
fields zero. The 64-port scalar factor and its literal inverse cost
2,048 each, including 32 field exchanges. The selected set has 24 ports.

Read `STRUCTURED-TRANSFER.md` for the exact interface and the first
implementation. Read `SCALED-TRANSFER.md` for the coherent scale change.
Use `original-normal/` and `scaled-normal/` for the final payloads.
Their optimized-run copies are byte-identical. The earlier `run-*` and
`final-normal/` directories are preserved preliminary evidence. They
are not the final receipt paths.

The source native records are unchanged. The two actual canonical words
also equal the words pinned by `new-native-recipes-20261017/FREEZE.json`.
The forward and literal-dual backward phase recipes from that packet
remain the native dependency. The new physical transfer has been sent
to that lane for independent reverse replay. Record its later review
as a separate artifact; do not rewrite this frozen producer evidence.

The following obligations remain outside this result: routed-stage code
transport, caller exterior phase, storage hosting, recursive precision,
and the complete supplier bill. Do not claim a full supplier or a kappa
improvement from these local words.

The controller lane has a new signed-response S8 candidate. It is a
separate response, not a smaller restriction of this emitted S24 word.
Before a transfer, obtain its frozen actual response, native payload,
ordinary inverse, data inverse, and selected set. Recheck the 64-port
block before reusing its scalar factor.

The publication hold remains in force. Do not create a PR, commit, or
push. Before any future PR description, read
`/Users/aliromman/Projects/IntegerMultiplicationBounds/PR-DESCRIPTION-STANDARD.md`.
