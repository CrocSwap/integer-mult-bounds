# Four-column binary-to-repair interface

The actual retained CRT repair accepts one12-bit record per address. Passing a48-bit dirty-back fiber as one record fails its parser. This package physically demultiplexes all four back columns, runs the unchanged repair four times on one reusable service bank, and reinterleaves the complete196608-bit output. It keeps the numeric input/output backing identities and charges every conversion, move, dispatch and cleanup.

[PROOF.md](PROOF.md) proves the fixed successful-domain interface for arbitrary12-bit payloads and every admitted32-bit ROM. [RESULT.json](RESULT.json) contains the exact program, source, table/storage and expected full-replay receipt. The finite-symbol instruction model,13-bit record/stencil storage bound, static compiler cost separation and supplied raw-S premise remain explicit. It is not a binary lowering of the entire repair machine, a variable-geometry evaluator, or a new multiplication bound.

The program has86646 instructions and includes four complete source service copies, using the same23 private roles. Its canonical full run must execute674212875 instructions and213526309 cell operations, including all11776 bad-address key calls. The adapter cost is exactly20B+105M+3H+143 instructions and7B+134M+69 cell actions, with M=4096,B=48M and H input one-bits. Erased retained backing, all four live columns, numeric input/output, borrowed headers/ROM, fixed tables and finite registers are accounted separately.

`RAW.bin` contains numeric0/1 bytes observed from the independently completed actual12-shuttle producer. [RAW-PROVENANCE.json](RAW-PROVENANCE.json) records its origin. The verifier checks it against an independent source endpoint and feeds it to this adapter. This is supplied-byte composition, not a simultaneous physical producer/consumer execution.

## Reproduce

From the repository root, using Python3.12 and no additional dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/crt-four-column-repair-interface --check-only
python3.12 -B research/crt-four-column-repair-interface/verify.py --light
python3.12 -B scripts/research_package.py --package research/crt-four-column-repair-interface
python3.12 -O -B research/crt-four-column-repair-interface/verify.py
```

The full command is a scheduled heavy replay (600-second cap); do not run it concurrently with other heavy research suites. `--prepare-receipt` prepares independently predicted frozen data and does not certify a full run. Exact final validation is recorded in VALIDATION.md. Source pins and transitive proof/runtime dependencies are in SOURCES.json and VERIFY.json; historical catalogue/selected-result provenance does not change the selected frontier.

## Open next questions

1. Execute the actual raw producer and this adapter on the same returned object in one physical lifecycle; hash equality alone does not prove that lifecycle.
2. Lower the complete record/stencil and fixed-control alphabet to binary transitions, including every finite table and its installation; the present runtime is finite-symbol.
3. Bind variable geometry, descriptor/ROM preparation and larger key services before claiming all-size E/native/precision/outer admission.

Structured reasons and first steps are in TASK.json. Malformed-input rejection may consume a prefix; no rollback theorem is claimed.

## Credit

Retains the CRT work of Cinna Davis, Hiroki KUMAZAKI, ToikY, Jose Manuel, Ryanson Jonathan and Douglas Colkitt and the PR4637/4795/5105 chain. Source-specific NOTICE files are pinned and retained. JoyboyBrian with substantial OpenAI Codex assistance and separate agent review; Apache-2.0. Finite replay is not independent human or proof-kernel acceptance.
